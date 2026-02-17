#!/usr/bin/env python3
"""
preprocess_research.py — SierraVault Research Pre-Processing Pipeline

Sends research JSON files to Ollama (Mac Studio) for extraction of key facts,
quotable passages, unique info, and relevance scoring.

Usage:
    python3 preprocess_research.py --slug red-baron-2013-remake
    python3 preprocess_research.py --all --limit 10
    python3 preprocess_research.py --slug space-quest-iv --model deepseek-r1:70b
"""

import argparse
import json
import os
import sys
import time
import glob
import urllib.request
import urllib.error

RESEARCH_BASE = os.path.expanduser(
    "~/Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault/research/games"
)

OLLAMA_HOSTS = [
    "http://100.90.195.80:11434",
    "http://192.168.10.228:11434",
    "http://localhost:11434",
]

DEFAULT_MODEL = "llama3.3:70b"

EXTRACTION_PROMPT = """You are a research assistant for SierraVault, a Sierra On-Line encyclopedia.

Analyze the following research source about a Sierra game and extract structured information.

SOURCE FILE: {filename}
SOURCE URL: {url}
PAGE TITLE: {title}

CONTENT:
{content}

Return ONLY valid JSON (no markdown fencing, no explanation) with this exact structure:
{{
  "relevance": <1-10 integer, how useful for a SierraVault encyclopedia article>,
  "key_facts": ["<specific dates, names, version numbers, sales figures, events>"],
  "quotable": ["<notable quotes from reviews, developers, or articles worth citing>"],
  "unique_info": ["<information unlikely to appear in other sources>"],
  "suggested_sections": ["<which article sections this source supports, e.g. Development, Reception, Legacy, Technical, Versions>"]
}}

Rules:
- relevance 1-3: barely related or generic. 4-6: useful background. 7-8: solid primary source. 9-10: essential/unique.
- If content is empty or irrelevant, return relevance 1 with empty arrays.
- key_facts should be SPECIFIC (dates, names, numbers), not vague.
- quotable should be EXACT quotes worth citing, not paraphrases.
- Keep each array to 10 items max.
"""


def find_ollama():
    """Try each Ollama host and return the first responding one."""
    for host in OLLAMA_HOSTS:
        try:
            req = urllib.request.Request(f"{host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return host
        except (urllib.error.URLError, OSError, TimeoutError):
            continue
    return None


def ollama_generate(host: str, model: str, prompt: str, timeout: int = 300) -> str:
    """Call Ollama generate API and return the response text."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048}
    }).encode()

    req = urllib.request.Request(
        f"{host}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
        return data.get("response", "")


def load_research_file(filepath: str) -> dict | None:
    """Load a research JSON file, handling malformed data."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        print(f"  ⚠ Skipping {os.path.basename(filepath)}: {e}")
        return None


def extract_content(data: dict) -> str:
    """Extract readable content from a research JSON file."""
    parts = []
    for key in ("full_text", "content", "text", "body"):
        val = data.get(key, "")
        if val and isinstance(val, str):
            parts.append(val)
    # Also grab pre-enriched data if present
    for key in ("extracted_facts", "key_quotes", "source_significance"):
        val = data.get(key)
        if val:
            if isinstance(val, list):
                parts.append("\n".join(str(v) for v in val))
            elif isinstance(val, str):
                parts.append(val)
    return "\n\n".join(parts).strip()


def parse_llm_json(text: str) -> dict | None:
    """Parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    # Find JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return None


def process_game(slug: str, host: str, model: str, limit: int | None = None) -> dict:
    """Process all research files for a single game slug."""
    game_dir = os.path.join(RESEARCH_BASE, slug)
    if not os.path.isdir(game_dir):
        print(f"✗ Directory not found: {game_dir}")
        return {"processed": 0, "skipped": 0, "errors": 0}

    summaries_path = os.path.join(game_dir, "_summaries.json")

    # Load existing summaries for skip logic
    existing = {}
    if os.path.exists(summaries_path):
        try:
            with open(summaries_path, "r") as f:
                for entry in json.load(f):
                    existing[entry.get("source_file", "")] = entry
        except (json.JSONDecodeError, OSError):
            pass

    # Get research files (skip underscore-prefixed)
    json_files = sorted(
        f for f in glob.glob(os.path.join(game_dir, "*.json"))
        if not os.path.basename(f).startswith("_")
    )

    if not json_files:
        print(f"  No research files found for {slug}")
        return {"processed": 0, "skipped": 0, "errors": 0}

    if limit:
        json_files = json_files[:limit]

    total = len(json_files)
    processed = 0
    skipped = 0
    errors = 0
    results = list(existing.values())  # keep existing entries
    seen_files = {e.get("source_file") for e in results}

    print(f"\n{'='*60}")
    print(f"📂 {slug} — {total} files to process")
    print(f"{'='*60}")

    start_time = time.time()

    for i, filepath in enumerate(json_files):
        fname = os.path.basename(filepath)

        # Skip already processed
        if fname in seen_files:
            skipped += 1
            print(f"  [{i+1}/{total}] ⏭ {fname} (already processed)")
            continue

        data = load_research_file(filepath)
        if data is None:
            errors += 1
            continue

        content = extract_content(data)
        if not content or len(content) < 50:
            print(f"  [{i+1}/{total}] ⏭ {fname} (no usable content)")
            skipped += 1
            continue

        # Truncate very long content
        if len(content) > 12000:
            content = content[:12000] + "\n\n[TRUNCATED]"

        url = data.get("url", "")
        title = data.get("page_title", "")

        prompt = EXTRACTION_PROMPT.format(
            filename=fname, url=url, title=title, content=content
        )

        elapsed = time.time() - start_time
        remaining_count = total - i - 1 - skipped
        if processed > 0:
            avg = elapsed / processed
            eta = avg * remaining_count
            eta_str = f" | ETA: {eta:.0f}s"
        else:
            eta_str = ""

        print(f"  [{i+1}/{total}] 🔄 {fname[:50]}{eta_str}")

        try:
            response = ollama_generate(host, model, prompt)
            parsed = parse_llm_json(response)

            if parsed is None:
                print(f"    ⚠ Failed to parse LLM response")
                errors += 1
                continue

            summary = {
                "source_file": fname,
                "source_url": url,
                "relevance": int(parsed.get("relevance", 1)),
                "key_facts": parsed.get("key_facts", [])[:10],
                "quotable": parsed.get("quotable", [])[:10],
                "unique_info": parsed.get("unique_info", [])[:10],
                "suggested_sections": parsed.get("suggested_sections", []),
            }
            results.append(summary)
            seen_files.add(fname)
            processed += 1
            print(f"    ✓ relevance={summary['relevance']} facts={len(summary['key_facts'])} quotes={len(summary['quotable'])}")

        except (urllib.error.URLError, OSError, TimeoutError) as e:
            print(f"    ✗ Ollama error: {e}")
            errors += 1
        except Exception as e:
            print(f"    ✗ Unexpected error: {e}")
            errors += 1

    # Sort by relevance descending
    results.sort(key=lambda x: x.get("relevance", 0), reverse=True)

    # Save
    with open(summaries_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"\n✅ {slug}: {processed} processed, {skipped} skipped, {errors} errors ({elapsed:.1f}s)")
    print(f"   Saved to {summaries_path}")

    return {"processed": processed, "skipped": skipped, "errors": errors}


def get_all_slugs() -> list[str]:
    """Get all game slugs that have research directories."""
    if not os.path.isdir(RESEARCH_BASE):
        return []
    return sorted(
        d for d in os.listdir(RESEARCH_BASE)
        if os.path.isdir(os.path.join(RESEARCH_BASE, d))
    )


def main():
    parser = argparse.ArgumentParser(description="SierraVault Research Pre-Processor")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--slug", help="Process a single game slug")
    group.add_argument("--all", action="store_true", help="Process all games")
    parser.add_argument("--limit", type=int, help="Max sources per game")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--dry-run", action="store_true", help="List files without processing")
    args = parser.parse_args()

    # Find Ollama
    print("🔍 Finding Ollama server...")
    host = find_ollama()
    if host is None:
        print("✗ No Ollama server reachable. Tried:", OLLAMA_HOSTS)
        sys.exit(1)
    print(f"✓ Connected to {host}")
    print(f"  Model: {args.model}")

    if args.slug:
        slugs = [args.slug]
    else:
        slugs = get_all_slugs()
        print(f"  Found {len(slugs)} game directories")

    if args.dry_run:
        for slug in slugs:
            game_dir = os.path.join(RESEARCH_BASE, slug)
            files = [f for f in glob.glob(os.path.join(game_dir, "*.json"))
                     if not os.path.basename(f).startswith("_")]
            if files:
                print(f"  {slug}: {len(files)} files")
        return

    total_stats = {"processed": 0, "skipped": 0, "errors": 0}
    for slug in slugs:
        stats = process_game(slug, host, args.model, args.limit)
        for k in total_stats:
            total_stats[k] += stats[k]

    print(f"\n{'='*60}")
    print(f"📊 TOTAL: {total_stats['processed']} processed, {total_stats['skipped']} skipped, {total_stats['errors']} errors")


if __name__ == "__main__":
    main()
