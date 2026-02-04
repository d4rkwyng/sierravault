#!/usr/bin/env python3
"""
Completion Tracker for Sierra Games Archive

Tracks which games have been:
1. Researched (has research folder with sources)
2. Enriched (sources have extracted_facts)
3. Generated (page exists in Games/)
4. Scored (page has been validated)

Output: completion_status.json
"""

import argparse
import json
import re
import yaml
from pathlib import Path
from datetime import datetime

# Paths
INTERNAL_DIR = Path(__file__).parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_DIR = INTERNAL_DIR.parent / "Games"
STATUS_FILE = INTERNAL_DIR / "completion_status.json"
SCORES_FILE = INTERNAL_DIR / "page_scores.json"

def slugify(title: str) -> str:
    """Convert game title to folder slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def extract_yaml_frontmatter(file_path: Path) -> dict:
    """Extract YAML frontmatter from markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            end = content.find('---', 3)
            if end != -1:
                yaml_str = content[3:end].strip()
                return yaml.safe_load(yaml_str) or {}
    except Exception as e:
        pass
    return {}

def scan_published_pages() -> dict:
    """Scan Games/ folder for all published pages."""
    pages = {}

    for md_file in GAMES_DIR.rglob("*.md"):
        # Skip index/readme files
        if md_file.name.lower() in ['readme.md', 'index.md', '_index.md']:
            continue

        rel_path = md_file.relative_to(GAMES_DIR)
        series = rel_path.parent.name if rel_path.parent != Path('.') else None

        # Extract metadata
        frontmatter = extract_yaml_frontmatter(md_file)
        title = frontmatter.get('title', md_file.stem)

        # Count references and assess quality
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        ref_count = len(re.findall(r'\[\^ref-\d+\]:', content))
        word_count = len(content.split())

        # Check for required sections
        has_overview = '## Overview' in content
        has_reception = '## Reception' in content
        has_development = '## Development' in content
        has_legacy = '## Legacy' in content
        has_downloads = '## Downloads' in content

        section_count = sum([has_overview, has_reception, has_development,
                           has_legacy, has_downloads])

        # Quality assessment
        if ref_count >= 20 and word_count >= 1500 and section_count >= 4:
            quality = "good"
        elif ref_count >= 10 and word_count >= 800:
            quality = "okay"
        elif ref_count > 0:
            quality = "poor"
        else:
            quality = "stub"

        slug = slugify(title)

        pages[slug] = {
            "title": title,
            "file": str(rel_path),
            "series": series,
            "release_year": frontmatter.get('release_year'),
            "references": ref_count,
            "word_count": word_count,
            "sections": section_count,
            "quality": quality,
            "last_updated": frontmatter.get('last_updated'),
        }

    return pages

def scan_research_folders() -> dict:
    """Scan research/ folder for all research data."""
    research = {}

    for folder in RESEARCH_DIR.iterdir():
        if not folder.is_dir():
            continue

        slug = folder.name

        # Count source files
        json_files = list(folder.glob("*.json"))
        source_files = [f for f in json_files if f.name not in ['_urls.json', '_manifest.json']]

        # Check for URLs file
        urls_file = folder / "_urls.json"
        urls_data = {}
        if urls_file.exists():
            with open(urls_file) as f:
                urls_data = json.load(f)

        # Check enrichment status
        enriched_count = 0
        for source_file in source_files:
            try:
                with open(source_file) as f:
                    data = json.load(f)
                if data.get("extracted_facts"):
                    enriched_count += 1
            except:
                pass

        # Check manifest
        manifest_file = folder / "_manifest.json"
        manifest = {}
        if manifest_file.exists():
            with open(manifest_file) as f:
                manifest = json.load(f)

        research[slug] = {
            "game_title": urls_data.get("game_title") or manifest.get("game_title") or slug,
            "source_count": len(source_files),
            "urls_discovered": urls_data.get("total_discovered", 0),
            "urls_crawled": len(urls_data.get("crawled", {})),
            "urls_pending": len(urls_data.get("pending", [])),
            "enriched_count": enriched_count,
            "enrichment_pct": round(enriched_count / len(source_files) * 100) if source_files else 0,
            "pipeline_status": manifest.get("pipeline_status", {}),
        }

    return research

def load_scores() -> dict:
    """Load page scores."""
    if SCORES_FILE.exists():
        with open(SCORES_FILE) as f:
            return json.load(f)
    return {}

def build_completion_status() -> dict:
    """Build complete status for all games."""
    print("Scanning published pages...")
    pages = scan_published_pages()
    print(f"  Found {len(pages)} published pages")

    print("Scanning research folders...")
    research = scan_research_folders()
    print(f"  Found {len(research)} research folders")

    print("Loading scores...")
    scores = load_scores()

    # Merge data
    all_games = set(pages.keys()) | set(research.keys())

    status = {
        "_meta": {
            "generated": datetime.now().isoformat(),
            "total_games": len(all_games),
            "published": len(pages),
            "researched": len(research),
        },
        "games": {}
    }

    for slug in sorted(all_games):
        page_info = pages.get(slug, {})
        research_info = research.get(slug, {})
        score_info = scores.get(slug, {})

        game_status = {
            "title": page_info.get("title") or research_info.get("game_title") or slug,
            "slug": slug,
            "stages": {
                "discovered": research_info.get("urls_discovered", 0) > 0,
                "crawled": research_info.get("source_count", 0) >= 10,
                "enriched": research_info.get("enrichment_pct", 0) >= 80,
                "generated": slug in pages,
                "scored": slug in scores or page_info.get("references", 0) >= 15,
            }
        }

        # Add details
        if page_info:
            game_status["page"] = page_info
        if research_info:
            game_status["research"] = research_info
        if score_info:
            game_status["scores"] = score_info

        # Calculate completion level (factor in page quality)
        stages = game_status["stages"]
        page_quality = page_info.get("quality", "none")

        if page_quality == "good" and stages["scored"]:
            game_status["status"] = "complete"
        elif page_quality == "good":
            game_status["status"] = "needs_scoring"
        elif page_quality in ["okay", "poor"]:
            game_status["status"] = "needs_improvement"
        elif page_quality == "stub":
            game_status["status"] = "stub"
        elif stages["enriched"]:
            game_status["status"] = "needs_generation"
        elif stages["crawled"]:
            game_status["status"] = "needs_enrichment"
        elif stages["discovered"]:
            game_status["status"] = "needs_crawling"
        else:
            game_status["status"] = "needs_research"

        status["games"][slug] = game_status

    # Add summary stats
    statuses = [g["status"] for g in status["games"].values()]
    qualities = [g.get("page", {}).get("quality", "none") for g in status["games"].values()]

    status["_meta"]["by_status"] = {
        "complete": statuses.count("complete"),
        "needs_scoring": statuses.count("needs_scoring"),
        "needs_improvement": statuses.count("needs_improvement"),
        "stub": statuses.count("stub"),
        "needs_generation": statuses.count("needs_generation"),
        "needs_enrichment": statuses.count("needs_enrichment"),
        "needs_crawling": statuses.count("needs_crawling"),
        "needs_research": statuses.count("needs_research"),
    }

    status["_meta"]["by_quality"] = {
        "good": qualities.count("good"),
        "okay": qualities.count("okay"),
        "poor": qualities.count("poor"),
        "stub": qualities.count("stub"),
        "none": qualities.count("none"),
    }

    return status

def save_status(status: dict):
    """Save status to file."""
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)
    print(f"\nSaved to: {STATUS_FILE}")

def print_summary(status: dict):
    """Print status summary."""
    meta = status["_meta"]
    by_status = meta["by_status"]
    by_quality = meta.get("by_quality", {})

    print("\n" + "=" * 60)
    print("COMPLETION STATUS")
    print("=" * 60)
    print(f"Total games tracked: {meta['total_games']}")
    print(f"Published pages: {meta['published']}")
    print(f"Research folders: {meta['researched']}")

    print("\nPage Quality:")
    print(f"  ✓ Good (20+ refs, 1500+ words):  {by_quality.get('good', 0):3}")
    print(f"  ~ Okay (10+ refs, 800+ words):   {by_quality.get('okay', 0):3}")
    print(f"  ✗ Poor (has refs, needs work):   {by_quality.get('poor', 0):3}")
    print(f"  ○ Stub (no refs):                {by_quality.get('stub', 0):3}")
    print(f"  - No page:                       {by_quality.get('none', 0):3}")

    print("\nBy Status:")
    print(f"  ✓ Complete:           {by_status.get('complete', 0):3}")
    print(f"  ⟳ Needs scoring:      {by_status.get('needs_scoring', 0):3}")
    print(f"  ⟳ Needs improvement:  {by_status.get('needs_improvement', 0):3}")
    print(f"  ○ Stub pages:         {by_status.get('stub', 0):3}")
    print(f"  ⟳ Needs generation:   {by_status.get('needs_generation', 0):3}")
    print(f"  ⟳ Needs enrichment:   {by_status.get('needs_enrichment', 0):3}")
    print(f"  ⟳ Needs crawling:     {by_status.get('needs_crawling', 0):3}")
    print(f"  ○ Needs research:     {by_status.get('needs_research', 0):3}")

def print_games_by_status(status: dict, filter_status: str = None):
    """Print games filtered by status."""
    games = status["games"]

    if filter_status:
        filtered = {k: v for k, v in games.items() if v["status"] == filter_status}
        print(f"\nGames with status: {filter_status}")
        print("-" * 40)
        for slug, info in sorted(filtered.items(), key=lambda x: x[1]["title"]):
            print(f"  {info['title']}")
        print(f"\nTotal: {len(filtered)}")
    else:
        # Group by status
        by_status = {}
        for slug, info in games.items():
            s = info["status"]
            by_status.setdefault(s, []).append(info)

        for s in ["complete", "needs_scoring", "needs_improvement", "stub",
                  "needs_generation", "needs_enrichment", "needs_crawling", "needs_research"]:
            if s in by_status:
                print(f"\n{s.upper()} ({len(by_status[s])})")
                print("-" * 40)
                for info in sorted(by_status[s], key=lambda x: x["title"])[:10]:
                    refs = info.get("page", {}).get("references", 0)
                    words = info.get("page", {}).get("word_count", 0)
                    print(f"  {info['title'][:40]:40} {refs:3} refs, {words:4} words")
                if len(by_status[s]) > 10:
                    print(f"  ... and {len(by_status[s]) - 10} more")

def main():
    parser = argparse.ArgumentParser(description="Track completion status")
    parser.add_argument("--refresh", action="store_true",
                       help="Refresh status (scan all files)")
    parser.add_argument("--status", type=str,
                       choices=["complete", "needs_scoring", "needs_generation",
                               "needs_enrichment", "needs_crawling", "needs_discovery"],
                       help="Filter by status")
    parser.add_argument("--list", action="store_true",
                       help="List all games by status")
    parser.add_argument("--next", type=int, default=0,
                       help="Show next N games to work on")

    args = parser.parse_args()

    # Load or build status
    if args.refresh or not STATUS_FILE.exists():
        status = build_completion_status()
        save_status(status)
    else:
        with open(STATUS_FILE) as f:
            status = json.load(f)

    # Output
    if args.list:
        print_games_by_status(status, args.status)
    elif args.next:
        # Find next games to work on
        priority_order = ["needs_scoring", "needs_generation", "needs_enrichment",
                         "needs_crawling", "needs_discovery"]
        games = []
        for s in priority_order:
            for slug, info in status["games"].items():
                if info["status"] == s and len(games) < args.next:
                    games.append((s, info))

        print(f"\nNext {len(games)} games to work on:")
        print("-" * 50)
        for s, info in games:
            print(f"  [{s:20}] {info['title']}")
    else:
        print_summary(status)

if __name__ == "__main__":
    main()
