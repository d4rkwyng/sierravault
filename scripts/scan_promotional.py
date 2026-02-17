#!/usr/bin/env python3
"""
Scan SierraVault game pages for promotional/non-encyclopedic language using Ollama LLM.

Uses llama3.3:70b to detect:
- Superlatives not attributed to reviews
- Marketing-speak
- Non-neutral tone
- Unsupported claims

Usage:
    python3 scripts/scan_promotional.py
    python3 scripts/scan_promotional.py --batch 20
    python3 scripts/scan_promotional.py --series "Space Quest"
    python3 scripts/scan_promotional.py --fix
    python3 scripts/scan_promotional.py --model deepseek-r1:70b
"""

import argparse
import json
import os
import random
import re
import shutil
import sys
import time
from pathlib import Path
from datetime import datetime

import urllib.request
import urllib.error

VAULT_GAMES = Path("/Users/woodd/Projects/sierravault/vault/Games")
OLLAMA_HOSTS = [
    os.environ.get("OLLAMA_STUDIO_TAILSCALE", "http://localhost:11434"),
    os.environ.get("OLLAMA_STUDIO_LOCAL", "http://localhost:11434"),
    "http://localhost:11434",
]
DEFAULT_MODEL = "llama3.3:70b"
BATCH_SIZE = 3  # pages per LLM call


def find_ollama():
    """Find a working Ollama host."""
    for host in OLLAMA_HOSTS:
        try:
            req = urllib.request.Request(f"{host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    print(f"✓ Connected to Ollama at {host}", file=sys.stderr)
                    return host
        except (urllib.error.URLError, OSError, TimeoutError):
            continue
    print("✗ No Ollama host available", file=sys.stderr)
    sys.exit(1)


def ollama_generate(host: str, model: str, prompt: str) -> str:
    """Call Ollama generate API with streaming to avoid timeout."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": 0.1, "num_predict": 4096, "num_ctx": 8192},
    }).encode()
    req = urllib.request.Request(
        f"{host}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    response_parts = []
    with urllib.request.urlopen(req, timeout=300) as resp:
        for line in resp:
            line = line.strip()
            if not line:
                continue
            try:
                chunk = json.loads(line)
                response_parts.append(chunk.get("response", ""))
                if chunk.get("done"):
                    break
            except json.JSONDecodeError:
                continue
    return "".join(response_parts)


def collect_pages(series: str = None) -> list[Path]:
    """Collect all .md game pages, optionally filtered by series."""
    pages = []
    for md in VAULT_GAMES.rglob("*.md"):
        if md.name.startswith("."):
            continue
        if series:
            # Match series folder name
            rel = md.relative_to(VAULT_GAMES)
            if rel.parts[0].lower() != series.lower():
                # Also check frontmatter series field
                try:
                    text = md.read_text(errors="replace")[:500]
                    if f'series: {series}' not in text and series.lower() not in rel.parts[0].lower():
                        continue
                except Exception:
                    continue
        pages.append(md)
    return sorted(pages)


def extract_content_lines(path: Path) -> list[tuple[int, str]]:
    """Read file and return (line_number, line) pairs, skipping frontmatter."""
    lines = path.read_text(errors="replace").splitlines()
    in_frontmatter = False
    result = []
    for i, line in enumerate(lines, 1):
        if i == 1 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            continue
        # Skip reference lines and empty lines for analysis
        if line.strip().startswith("[^ref-") or line.strip().startswith("[^"):
            continue
        result.append((i, line))
    return result


def build_prompt(pages_data: list[dict]) -> str:
    """Build the LLM prompt for a batch of pages."""
    prompt = """You are an encyclopedic tone reviewer for a game encyclopedia (like Wikipedia). 
Analyze the following game page excerpts for promotional or non-encyclopedic language.

Detect:
1. **Unattributed superlatives** - "the greatest", "the best", "legendary" without citing a review
2. **Marketing-speak** - "must-play", "unforgettable experience", "groundbreaking"  
3. **Non-neutral tone** - "amazingly", "incredibly innovative", "brilliant design"
4. **Unsupported claims** - "universally beloved", "widely regarded as the best" without citation
5. **Peacock words** - "iconic", "revolutionary", "genre-defining" used as fact not attributed opinion

IMPORTANT: Quoted text (in quotes or attributed to a reviewer/source with a citation like [^ref-N]) is OK.
Text describing documented critical reception with citations is OK.
Only flag language that presents opinion as encyclopedic fact.

For each issue found, respond with a JSON array. Each item:
{
  "page": "filename",
  "line_num": 42,
  "original": "the exact problematic text",
  "issue": "brief description of the problem",
  "suggestion": "neutral alternative text"
}

If a page has no issues, omit it. Return ONLY a JSON array (no markdown fencing).
If no issues at all, return [].

"""
    for pd in pages_data:
        prompt += f"\n=== PAGE: {pd['filename']} ===\n"
        for lnum, line in pd['lines']:
            if line.strip():
                prompt += f"L{lnum}: {line}\n"
        prompt += "\n"

    return prompt


def parse_llm_response(response: str) -> list[dict]:
    """Extract JSON array from LLM response."""
    # Try to find JSON array in response
    response = response.strip()
    # Remove markdown code fences if present
    response = re.sub(r'^```(?:json)?\s*', '', response)
    response = re.sub(r'\s*```$', '', response)
    response = response.strip()

    # Find the array
    match = re.search(r'\[.*\]', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Try parsing the whole thing
    try:
        result = json.loads(response)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    return []


def apply_fix(path: Path, findings: list[dict]) -> int:
    """Apply fixes to a file, creating a backup first. Returns count of fixes applied."""
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    fixed = 0

    # Create backup
    backup = path.with_suffix(".md.bak")
    shutil.copy2(path, backup)

    for finding in sorted(findings, key=lambda f: f.get("line_num", 0), reverse=True):
        lnum = finding.get("line_num", 0)
        original = finding.get("original", "")
        suggestion = finding.get("suggestion", "")
        if not original or not suggestion or lnum < 1 or lnum > len(lines):
            continue
        if original in lines[lnum - 1]:
            lines[lnum - 1] = lines[lnum - 1].replace(original, suggestion)
            fixed += 1

    if fixed > 0:
        path.write_text("\n".join(lines) + "\n")
    else:
        # Remove backup if nothing changed
        backup.unlink(missing_ok=True)

    return fixed


def main():
    parser = argparse.ArgumentParser(description="Scan SierraVault pages for promotional language")
    parser.add_argument("--batch", type=int, default=10, help="Number of pages to process (default: 10)")
    parser.add_argument("--series", type=str, help="Limit to one series folder")
    parser.add_argument("--fix", action="store_true", help="Auto-apply suggested replacements (with backup)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--random", action="store_true", help="Randomize page selection")
    parser.add_argument("--output", type=str, help="Output JSON report to file")
    args = parser.parse_args()

    host = find_ollama()
    pages = collect_pages(args.series)

    if not pages:
        print(f"No pages found{f' for series {args.series}' if args.series else ''}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(pages)} pages{f' in {args.series}' if args.series else ''}", file=sys.stderr)

    if args.random:
        random.shuffle(pages)

    pages = pages[:args.batch]
    print(f"Processing {len(pages)} pages with {args.model}...", file=sys.stderr)

    all_findings = []
    total_fixes = 0

    # Process in batches of BATCH_SIZE
    for i in range(0, len(pages), BATCH_SIZE):
        batch = pages[i:i + BATCH_SIZE]
        batch_names = [p.name for p in batch]
        print(f"\nBatch {i // BATCH_SIZE + 1}: {', '.join(batch_names)}", file=sys.stderr)

        pages_data = []
        for p in batch:
            content_lines = extract_content_lines(p)
            # Send first ~60 content lines to keep prompt manageable
            pages_data.append({
                "filename": p.name,
                "path": str(p),
                "lines": content_lines[:60],
            })

        prompt = build_prompt(pages_data)
        t0 = time.time()
        response = ollama_generate(host, args.model, prompt)
        elapsed = time.time() - t0
        print(f"  LLM response in {elapsed:.1f}s", file=sys.stderr)

        findings = parse_llm_response(response)

        # Attach full paths to findings
        path_map = {pd["filename"]: pd["path"] for pd in pages_data}
        for f in findings:
            f["file_path"] = path_map.get(f.get("page", ""), "")

        if findings:
            print(f"  Found {len(findings)} issues", file=sys.stderr)
            for f in findings:
                print(f"    L{f.get('line_num', '?')}: {f.get('issue', '')}", file=sys.stderr)
        else:
            print(f"  No issues found", file=sys.stderr)

        all_findings.extend(findings)

        # Apply fixes if requested
        if args.fix and findings:
            # Group by file
            by_file = {}
            for f in findings:
                fp = f.get("file_path", "")
                if fp:
                    by_file.setdefault(fp, []).append(f)
            for fp, file_findings in by_file.items():
                n = apply_fix(Path(fp), file_findings)
                total_fixes += n
                if n:
                    print(f"  Fixed {n} issues in {Path(fp).name}", file=sys.stderr)

    # Build report
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": args.model,
        "pages_scanned": len(pages),
        "total_issues": len(all_findings),
        "fixes_applied": total_fixes if args.fix else None,
        "findings": all_findings,
    }

    output = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(output)
        print(f"\nReport saved to {args.output}", file=sys.stderr)
    else:
        print(output)

    print(f"\nSummary: {len(all_findings)} issues in {len(pages)} pages", file=sys.stderr)


if __name__ == "__main__":
    main()
