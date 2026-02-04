#!/usr/bin/env python3
"""
Sierra Games Archive - Pipeline Orchestrator v2

Runs the complete workflow:
  1. DISCOVER - Find URLs with discover_urls.py
  2. CRAWL - Fetch content with crawl_sources.py (parallel)
  3. ENRICH - Extract facts with enrich_research.py
  4. GENERATE - Create page (manual or generate_page_from_research.py)
  5. SCORE - Validate with score_page.py and score_page_llm.py
  6. PUBLISH - Copy to Games/ folder

Usage:
  python pipeline.py "Space Quest III"              # Full pipeline (stops at generate)
  python pipeline.py "Space Quest III" --discover   # Discovery only
  python pipeline.py "Space Quest III" --crawl      # Discover + Crawl
  python pipeline.py "Space Quest III" --enrich     # Through enrichment (default)
  python pipeline.py "Space Quest III" --generate   # Full pipeline including generation
  python pipeline.py --status                       # Show all game status
  python pipeline.py --next 5                       # Show next 5 games to work on
  python pipeline.py --batch games.txt              # Process multiple games
"""

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"
GAMES_DIR = INTERNAL_DIR.parent / "Games"

def slugify(title: str) -> str:
    """Convert game title to folder slug."""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def run_script(script: str, args: list, description: str) -> tuple[bool, str]:
    """Run a Python script and return success status."""
    print(f"\n{'='*60}")
    print(f"STAGE: {description}")
    print(f"{'='*60}\n")

    cmd = [sys.executable, script] + args

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(SCRIPTS_DIR),
            timeout=1800  # 30 minute timeout
        )

        print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")

        return result.returncode == 0, result.stdout

    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def check_research_quality(game_slug: str) -> dict:
    """Check research quality for a game."""
    folder = GAMES_RESEARCH_DIR / game_slug

    if not folder.exists():
        return {"status": "no_folder", "sources": 0, "enriched": 0}

    # Count sources
    json_files = [f for f in folder.glob("*.json")
                  if f.name not in ['_urls.json', '_manifest.json']]

    # Count enriched
    enriched = 0
    good_sources = 0
    for f in json_files:
        try:
            with open(f) as fp:
                data = json.load(fp)
            if data.get("extracted_facts"):
                enriched += 1
            if len(data.get("full_text", "")) > 2000:
                good_sources += 1
        except:
            pass

    return {
        "status": "ok" if good_sources >= 30 else "needs_more",
        "sources": len(json_files),
        "good_sources": good_sources,
        "enriched": enriched,
        "enrichment_pct": round(enriched / len(json_files) * 100) if json_files else 0
    }

def step_discover(game_title: str, game_slug: str, series: str = None) -> bool:
    """Step 1: Discover URLs."""
    args = [game_title]
    if series:
        args.extend(["--series", series])

    success, _ = run_script("discover_urls.py", args, "URL Discovery")
    return success

def step_crawl(game_title: str, game_slug: str, workers: int = 16) -> bool:
    """Step 2: Crawl discovered URLs."""
    args = [game_title, "--workers", str(workers)]
    success, _ = run_script("crawl_sources.py", args, "Parallel Crawl")

    if success:
        # Check quality
        quality = check_research_quality(game_slug)
        print(f"\nResearch Quality Check:")
        print(f"  Total sources: {quality['sources']}")
        print(f"  Good sources (>2KB): {quality['good_sources']}")

        if quality['good_sources'] < 30:
            print(f"\n⚠️  Need {30 - quality['good_sources']} more good sources")
            print("Consider manual source addition or re-running discovery")

    return success

def step_enrich(game_title: str, game_slug: str) -> bool:
    """Step 3: Enrich with LLM."""
    args = [game_slug]
    success, _ = run_script("enrich_research.py", args, "LLM Enrichment")

    if success:
        quality = check_research_quality(game_slug)
        print(f"\nEnrichment Status:")
        print(f"  Enriched: {quality['enriched']}/{quality['sources']}")
        print(f"  Percentage: {quality['enrichment_pct']}%")

        if quality['enrichment_pct'] < 80:
            print(f"\n⚠️  Low enrichment rate. Check for failed extractions.")

    return success

def step_generate(game_title: str, game_slug: str, output_path: Path = None) -> bool:
    """Step 4: Generate page."""
    if output_path is None:
        output_path = Path(f"/tmp/{game_slug}.md")

    args = [game_slug, "-o", str(output_path)]
    success, _ = run_script("generate_page_from_research.py", args, "Page Generation")

    if success and output_path.exists():
        print(f"\n✓ Page generated: {output_path}")

    return success and output_path.exists()

def step_score(game_title: str, game_slug: str, page_path: Path) -> tuple[bool, dict]:
    """Step 5: Score the page."""
    scores = {}

    # Automated scoring
    success1, output1 = run_script("score_page.py", [str(page_path)], "Automated Scoring")
    if success1:
        import re
        match = re.search(r'Score:\s*(\d+)', output1)
        if match:
            scores['automated'] = int(match.group(1))

    # LLM scoring
    success2, output2 = run_script("score_page_llm.py",
                                   [str(page_path), "--model", "claude"],
                                   "LLM Scoring")
    if success2:
        import re
        match = re.search(r'Score:\s*(\d+)', output2)
        if match:
            scores['claude'] = int(match.group(1))

    # Check pass threshold
    auto_pass = scores.get('automated', 0) >= 90
    llm_pass = scores.get('claude', 0) >= 90

    print(f"\nScoring Results:")
    print(f"  Automated: {scores.get('automated', 'N/A')}/100 {'✓' if auto_pass else '✗'}")
    print(f"  Claude: {scores.get('claude', 'N/A')}/100 {'✓' if llm_pass else '✗'}")

    return auto_pass and llm_pass, scores

def step_publish(game_title: str, game_slug: str, page_path: Path, series: str = None) -> bool:
    """Step 6: Publish to Games/ folder."""
    # Determine destination
    if series:
        dest_folder = GAMES_DIR / series
    else:
        # Auto-detect series from title
        series_map = {
            "King's Quest": "Kings Quest",
            "Space Quest": "Space Quest",
            "Quest for Glory": "Quest For Glory",
            "Leisure Suit Larry": "Leisure Suit Larry",
            "Police Quest": "Police Quest",
            "Gabriel Knight": "Gabriel Knight",
        }
        dest_folder = GAMES_DIR / "Other"
        for prefix, folder in series_map.items():
            if prefix.lower() in game_title.lower():
                dest_folder = GAMES_DIR / folder
                break

    dest_folder.mkdir(parents=True, exist_ok=True)

    # Get year from page frontmatter
    year = "1990"  # Default
    try:
        with open(page_path) as f:
            content = f.read()
        import re
        match = re.search(r'release_year:\s*(\d+)', content)
        if match:
            year = match.group(1)
    except:
        pass

    dest_path = dest_folder / f"{year} - {game_title}.md"

    import shutil
    shutil.copy2(page_path, dest_path)

    print(f"\n✓ Published to: {dest_path}")
    return True

def run_pipeline(game_title: str, series: str = None,
                stop_at: str = "enrich", workers: int = 16,
                force: bool = False, auto_publish: bool = False):
    """Run pipeline for a game."""
    game_slug = slugify(game_title)

    print(f"\n{'#'*60}")
    print(f"# PIPELINE: {game_title}")
    print(f"# Slug: {game_slug}")
    print(f"# Stop at: {stop_at}")
    print(f"{'#'*60}")

    # Step 1: Discover
    if not step_discover(game_title, game_slug, series):
        print("\n[FAILED] Discovery failed")
        return False

    if stop_at == "discover":
        print("\n[DONE] Stopped at discovery")
        return True

    # Step 2: Crawl
    if not step_crawl(game_title, game_slug, workers):
        print("\n[FAILED] Crawl failed")
        return False

    # Check quality gate
    quality = check_research_quality(game_slug)
    if quality['good_sources'] < 30:
        print(f"\n[BLOCKED] Only {quality['good_sources']}/30 good sources")
        print("Add more sources manually or improve discovery")
        return False

    if stop_at == "crawl":
        print("\n[DONE] Stopped at crawl")
        return True

    # Step 3: Enrich
    if not step_enrich(game_title, game_slug):
        print("\n[FAILED] Enrichment failed")
        return False

    if stop_at == "enrich":
        print("\n[DONE] Research complete - ready for page generation")
        print(f"\nNext steps:")
        print(f"  1. Review research in: research/{game_slug}/")
        print(f"  2. Request page generation when ready")
        return True

    # Step 4: Generate
    output_path = Path(f"/tmp/{game_slug}.md")
    if not step_generate(game_title, game_slug, output_path):
        print("\n[FAILED] Generation failed")
        return False

    if stop_at == "generate":
        print(f"\n[DONE] Page generated: {output_path}")
        return True

    # Step 5: Score
    passed, scores = step_score(game_title, game_slug, output_path)
    if not passed:
        print("\n[NEEDS REVIEW] Scoring did not pass")
        print(f"Review and fix: {output_path}")
        return False

    if stop_at == "score":
        print(f"\n[DONE] Scoring passed: {scores}")
        return True

    # Step 6: Publish
    if auto_publish:
        if step_publish(game_title, game_slug, output_path, series):
            print("\n[COMPLETE] Pipeline finished successfully!")
            return True
    else:
        print(f"\n[READY] Page ready for review: {output_path}")
        print("Run with --auto-publish to publish automatically")
        return True

    return False

def show_status():
    """Show pipeline status for all games."""
    # Run completion tracker
    run_script("completion_tracker.py", ["--refresh"], "Completion Status")

def show_next(count: int):
    """Show next games to work on."""
    run_script("completion_tracker.py", ["--next", str(count)], "Next Games")

def main():
    parser = argparse.ArgumentParser(description="Sierra Games Pipeline v2")
    parser.add_argument("game", nargs="?", help="Game title")
    parser.add_argument("--series", help="Series name")
    parser.add_argument("--workers", "-w", type=int, default=16,
                       help="Parallel crawl workers (default: 16)")

    # Stop points
    parser.add_argument("--discover", action="store_true",
                       help="Stop after URL discovery")
    parser.add_argument("--crawl", action="store_true",
                       help="Stop after crawling")
    parser.add_argument("--enrich", action="store_true",
                       help="Stop after enrichment (default)")
    parser.add_argument("--generate", action="store_true",
                       help="Include page generation")
    parser.add_argument("--score", action="store_true",
                       help="Include scoring")
    parser.add_argument("--auto-publish", action="store_true",
                       help="Auto-publish if scores pass")

    parser.add_argument("--force", "-f", action="store_true",
                       help="Force re-run of completed steps")
    parser.add_argument("--batch", type=Path,
                       help="File with list of game titles")
    parser.add_argument("--status", action="store_true",
                       help="Show completion status")
    parser.add_argument("--next", type=int, default=0,
                       help="Show next N games to work on")

    args = parser.parse_args()

    # Handle status/next commands
    if args.status:
        show_status()
        return

    if args.next:
        show_next(args.next)
        return

    # Determine stop point
    if args.discover:
        stop_at = "discover"
    elif args.crawl:
        stop_at = "crawl"
    elif args.generate:
        stop_at = "generate"
    elif args.score:
        stop_at = "score"
    elif args.auto_publish:
        stop_at = "publish"
    else:
        stop_at = "enrich"  # Default: stop before generation

    # Batch mode
    if args.batch:
        if not args.batch.exists():
            print(f"Error: Batch file not found: {args.batch}")
            return

        with open(args.batch) as f:
            games = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        print(f"Processing {len(games)} games...")
        for i, game_title in enumerate(games):
            print(f"\n\n{'#'*60}")
            print(f"# BATCH [{i+1}/{len(games)}]: {game_title}")
            print(f"{'#'*60}")
            run_pipeline(game_title, args.series, stop_at, args.workers,
                        args.force, args.auto_publish)
        return

    # Single game
    if not args.game:
        parser.print_help()
        return

    run_pipeline(args.game, args.series, stop_at, args.workers,
                args.force, args.auto_publish)

if __name__ == "__main__":
    main()
