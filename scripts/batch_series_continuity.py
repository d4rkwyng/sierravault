#!/usr/bin/env python3
"""Batch Series Continuity Generator for SierraVault.

Scans game pages, identifies those missing series continuity prose in their
See Also section, and uses Ollama to generate proposed continuity paragraphs
that get inserted at the top of See Also (before navigation links).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

GAMES_DIR = Path("/Users/woodd/Projects/sierravault/vault/Games")
OLLAMA_HOSTS = [
    os.environ.get("OLLAMA_STUDIO_TAILSCALE", "http://localhost:11434"),
    os.environ.get("OLLAMA_STUDIO_LOCAL", "http://localhost:11434"),
    "http://localhost:11434",
]
DEFAULT_MODEL = "llama3.3:70b"


def find_ollama():
    """Find a reachable Ollama host."""
    for host in OLLAMA_HOSTS:
        try:
            req = Request(f"{host}/api/tags", method="GET")
            with urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    print(f"✓ Connected to Ollama at {host}")
                    return host
        except (URLError, OSError):
            continue
    return None


def ollama_generate(host: str, model: str, prompt: str) -> str:
    """Generate text via Ollama API."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 1024},
    }).encode()
    req = Request(f"{host}/api/generate", data=payload, method="POST",
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())["response"].strip()


def get_series_games(series_dir: Path) -> list[dict]:
    """Get sorted list of game files in a series directory."""
    games = []
    for f in sorted(series_dir.glob("*.md")):
        name = f.stem
        # Extract year from filename pattern "YYYY - Title"
        m = re.match(r"(\d{4})\s*-\s*(.*)", name)
        if m:
            games.append({"year": int(m.group(1)), "title": m.group(2), "path": f, "filename": name})
    return games


def has_series_continuity(content: str) -> bool:
    """Check if page already has continuity prose in See Also section."""
    # Check for legacy separate section
    if "## Series Continuity" in content or "### Series Continuity" in content:
        return True
    # Check for prose paragraph in See Also (not just navigation links)
    see_also = re.search(r"^## See Also\n\n(.+?)(?=\n- |\n\[|\Z)", content, re.MULTILINE | re.DOTALL)
    if see_also and len(see_also.group(1).strip()) > 50:
        return True
    return False


def get_series_context(games: list[dict], idx: int) -> dict:
    """Get previous/next game info for context."""
    ctx = {"current": games[idx]["title"], "series": games[idx]["path"].parent.name}
    if idx > 0:
        ctx["previous"] = games[idx - 1]["title"]
    if idx < len(games) - 1:
        ctx["next"] = games[idx + 1]["title"]
    return ctx


def build_prompt(page_content: str, series_ctx: dict) -> str:
    """Build the Ollama prompt for generating series continuity prose for the See Also section."""
    parts = [
        "You are writing series continuity prose for a Sierra game wiki page's See Also section.",
        "Write 2-3 paragraphs (each 2-3 sentences) describing how this game connects "
        "to the previous and next entries in the series, both narratively and mechanically.",
        "Use specific plot points, character names, and gameplay evolution details from the page content.",
        "Reference the previous and next games by name where applicable.",
        "Do NOT include any heading—just the prose paragraphs.",
        "Do NOT use wiki links or markdown formatting beyond basic prose.",
        "",
        f"Series: {series_ctx['series']}",
        f"Current game: {series_ctx['current']}",
    ]
    if "previous" in series_ctx:
        parts.append(f"Previous entry: {series_ctx['previous']}")
    if "next" in series_ctx:
        parts.append(f"Next entry: {series_ctx['next']}")
    parts.append("")
    parts.append("=== PAGE CONTENT (first 6000 chars) ===")
    parts.append(page_content[:6000])
    return "\n".join(parts)


def insert_continuity(content: str, continuity_text: str) -> str:
    """Insert continuity prose inside ## See Also section (before navigation links)."""
    see_also_match = re.search(r"^## See Also\n", content, re.MULTILINE)
    if see_also_match:
        insert_pos = see_also_match.end()
        return (content[:insert_pos] +
                "\n" + continuity_text + "\n\n" +
                content[insert_pos:])
    # If no See Also exists, create one before ## References
    ref_match = re.search(r"^## References", content, re.MULTILINE)
    if ref_match:
        insert_pos = ref_match.start()
        return (content[:insert_pos] +
                "## See Also\n\n" + continuity_text + "\n\n" +
                content[insert_pos:])
    # Last resort: append
    return content.rstrip() + "\n\n## See Also\n\n" + continuity_text + "\n"


def main():
    parser = argparse.ArgumentParser(description="Batch generator for series continuity prose in See Also sections")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Report what needs fixing (default)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually generate and insert continuity sections")
    parser.add_argument("--series", type=str, default=None,
                        help="Limit to one series folder name (e.g. \"King's Quest\")")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                        help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--output", type=str, default=None,
                        help="JSON output file for proposed changes")
    args = parser.parse_args()

    if args.apply:
        args.dry_run = False

    # Discover series directories
    if args.series:
        series_dirs = [GAMES_DIR / args.series]
        if not series_dirs[0].is_dir():
            print(f"✗ Series directory not found: {series_dirs[0]}")
            sys.exit(1)
    else:
        series_dirs = sorted([d for d in GAMES_DIR.iterdir() if d.is_dir()])

    # Find pages missing continuity
    missing = []
    total_pages = 0
    has_continuity = 0

    for series_dir in series_dirs:
        games = get_series_games(series_dir)
        if len(games) < 2:
            # Single-game "series" don't need continuity
            total_pages += len(games)
            continue

        for idx, game in enumerate(games):
            total_pages += 1
            content = game["path"].read_text(encoding="utf-8")
            if has_series_continuity(content):
                has_continuity += 1
                continue
            ctx = get_series_context(games, idx)
            missing.append({
                "path": str(game["path"]),
                "series": series_dir.name,
                "title": game["title"],
                "year": game["year"],
                "context": ctx,
            })

    print(f"\nScan Results:")
    print(f"  Total game pages: {total_pages}")
    print(f"  Already have continuity: {has_continuity}")
    print(f"  Missing continuity: {len(missing)}")
    print()

    if not missing:
        print("Nothing to do!")
        return

    # Group by series for display
    by_series = {}
    for m in missing:
        by_series.setdefault(m["series"], []).append(m)
    for series, pages in sorted(by_series.items()):
        print(f"  {series}: {len(pages)} pages need continuity")
        for p in pages:
            print(f"    - {p['title']} ({p['year']})")

    if args.dry_run:
        print(f"\n[DRY RUN] Use --apply to generate and insert continuity sections.")
        if args.output:
            with open(args.output, "w") as f:
                json.dump(missing, f, indent=2)
            print(f"Missing pages list written to {args.output}")
        return

    # --- Apply mode: generate continuity ---
    host = find_ollama()
    if not host:
        print("✗ No Ollama host reachable!")
        sys.exit(1)

    results = []
    for i, entry in enumerate(missing, 1):
        path = Path(entry["path"])
        print(f"\n[{i}/{len(missing)}] Generating for: {entry['title']}...")
        content = path.read_text(encoding="utf-8")
        prompt = build_prompt(content, entry["context"])

        try:
            continuity = ollama_generate(host, args.model, prompt)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({**entry, "status": "error", "error": str(e)})
            continue

        new_content = insert_continuity(content, continuity)
        path.write_text(new_content, encoding="utf-8")
        print(f"  ✓ Inserted series continuity prose in See Also")
        results.append({**entry, "status": "applied", "generated": continuity})

    output_path = args.output or "series_continuity_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {output_path}")
    print(f"Review changes before committing!")


if __name__ == "__main__":
    main()
