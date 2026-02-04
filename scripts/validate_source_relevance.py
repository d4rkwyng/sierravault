#!/usr/bin/env python3
"""
Validate research source relevance for a specific game.
Ensures crawled content is about the correct game, not similarly-named titles.

Usage:
    python3 validate_source_relevance.py <game-slug> [--config CONFIG_FILE]
    python3 validate_source_relevance.py kings-quest-1-vga-remake-agdi
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

RESEARCH_DIR = Path("research")

# Default validation config - can be overridden per game
DEFAULT_CONFIG = {
    "game_title": "Unknown Game",
    "required_keywords": [],      # Must have at least one
    "positive_keywords": [],      # Boost score
    "negative_keywords": [],      # Reduce score (wrong game indicators)
    "year_range": (1980, 2030),   # Valid release year range
    "min_content_length": 500,   # Minimum chars
    "min_relevance_score": 5,    # 0-10, reject below this
}

# Game-specific configs
GAME_CONFIGS = {
    "kings-quest-1-vga-remake-agdi": {
        "game_title": "King's Quest I VGA Remake (AGD Interactive)",
        "required_keywords": [
            "agd interactive", "agdi", "tierra entertainment", "tierra",
            "vga remake", "fan remake", "fan-made", "freeware remake"
        ],
        "positive_keywords": [
            "2001", "2002", "2009", "2010", "2024",  # Release years
            "adventure game studio", "ags",
            "britney brimhall", "christopher warren", "chris warren",
            "point-and-click", "point and click",
            "version 4.0", "version 4.1", "version 4.2",
            "himalaya studios", "himalaya soft",
            "fan license", "vivendi",
            "king's quest i", "king's quest 1", "quest for the crown"
        ],
        "negative_keywords": [
            "1984 sierra", "1990 sierra", "roberta williams original",
            "sci remake", "agi version", "pcjr", "tandy",
            "mask of eternity", "king's quest viii", "king's quest 8",
            "2015 reboot", "the odd gentlemen", "chapter 1"
        ],
        "year_range": (2001, 2026),
        "min_content_length": 300,
        "min_relevance_score": 4,
    },
    # Add more game configs as needed
}


def load_config(game_slug: str) -> dict:
    """Load validation config for a game."""
    if game_slug in GAME_CONFIGS:
        config = DEFAULT_CONFIG.copy()
        config.update(GAME_CONFIGS[game_slug])
        return config
    return DEFAULT_CONFIG.copy()


def extract_text(data: dict) -> str:
    """Extract text content from research JSON."""
    # Try different field names used in our research files
    text = data.get('full_text', '')
    if not text:
        text = data.get('content', '')
    if not text:
        text = data.get('text', '')
    if not text:
        # Kagi FastGPT format
        queries = data.get('queries', [])
        for q in queries:
            resp = q.get('response', {})
            output = resp.get('data', {}).get('output', '')
            if output:
                text += output + "\n"
    return text


def score_relevance(text: str, config: dict) -> tuple[int, list[str]]:
    """
    Score source relevance 0-10.
    Returns (score, list of reasons).
    """
    text_lower = text.lower()
    score = 5  # Start neutral
    reasons = []

    # Check required keywords (must have at least one)
    has_required = False
    for kw in config['required_keywords']:
        if kw.lower() in text_lower:
            has_required = True
            break

    if not has_required and config['required_keywords']:
        score -= 4
        reasons.append("Missing required keywords (AGDI/Tierra/fan remake)")
    else:
        reasons.append("Has required keyword")

    # Count positive keywords
    positive_count = 0
    for kw in config['positive_keywords']:
        if kw.lower() in text_lower:
            positive_count += 1

    if positive_count >= 5:
        score += 3
        reasons.append(f"Strong positive keywords ({positive_count})")
    elif positive_count >= 2:
        score += 2
        reasons.append(f"Good positive keywords ({positive_count})")
    elif positive_count >= 1:
        score += 1
        reasons.append(f"Some positive keywords ({positive_count})")

    # Check negative keywords (wrong game indicators)
    negative_count = 0
    negative_found = []
    for kw in config['negative_keywords']:
        if kw.lower() in text_lower:
            negative_count += 1
            negative_found.append(kw)

    if negative_count >= 3:
        score -= 3
        reasons.append(f"Many wrong-game indicators: {negative_found[:3]}")
    elif negative_count >= 1:
        score -= 1
        reasons.append(f"Some wrong-game indicators: {negative_found[:2]}")

    # Check content length
    if len(text) < config['min_content_length']:
        score -= 2
        reasons.append(f"Too short ({len(text)} chars)")
    elif len(text) > 2000:
        score += 1
        reasons.append(f"Good length ({len(text)} chars)")

    # Clamp score to 0-10
    score = max(0, min(10, score))

    return score, reasons


def validate_source(filepath: Path, config: dict) -> dict:
    """Validate a single research source file."""
    try:
        with open(filepath) as f:
            data = json.load(f)
    except Exception as e:
        return {
            "file": filepath.name,
            "status": "error",
            "error": str(e),
            "score": 0,
            "reasons": ["Failed to parse JSON"]
        }

    url = data.get('url', 'N/A')
    title = data.get('page_title', data.get('title', 'N/A'))
    text = extract_text(data)

    if not text:
        return {
            "file": filepath.name,
            "url": url,
            "title": title,
            "status": "empty",
            "score": 0,
            "reasons": ["No text content"],
            "content_length": 0
        }

    score, reasons = score_relevance(text, config)

    status = "valid" if score >= config['min_relevance_score'] else "rejected"

    return {
        "file": filepath.name,
        "url": url[:80] + "..." if len(url) > 80 else url,
        "title": title[:60] + "..." if len(str(title)) > 60 else title,
        "status": status,
        "score": score,
        "reasons": reasons,
        "content_length": len(text)
    }


def validate_game_research(game_slug: str, move_rejected: bool = False) -> dict:
    """Validate all research for a game."""
    folder = RESEARCH_DIR / game_slug
    if not folder.exists():
        print(f"ERROR: Research folder not found: {folder}")
        return {"error": "folder_not_found"}

    config = load_config(game_slug)
    print(f"\n{'='*60}")
    print(f"Validating: {config['game_title']}")
    print(f"Folder: {folder}")
    print(f"Min relevance score: {config['min_relevance_score']}/10")
    print(f"{'='*60}\n")

    results = {
        "game_slug": game_slug,
        "game_title": config['game_title'],
        "validation_date": datetime.now().isoformat(),
        "config": config,
        "sources": [],
        "summary": {
            "total": 0,
            "valid": 0,
            "rejected": 0,
            "empty": 0,
            "error": 0
        }
    }

    # Find all JSON files except _urls.json
    json_files = sorted(folder.glob("*.json"))
    json_files = [f for f in json_files if f.name != "_urls.json"]

    for filepath in json_files:
        result = validate_source(filepath, config)
        results["sources"].append(result)
        results["summary"]["total"] += 1
        results["summary"][result["status"]] += 1

        # Print result
        status_icon = {
            "valid": "\033[92m✓\033[0m",      # Green check
            "rejected": "\033[91m✗\033[0m",   # Red X
            "empty": "\033[93m○\033[0m",      # Yellow circle
            "error": "\033[91m!\033[0m"       # Red exclamation
        }.get(result["status"], "?")

        print(f"{status_icon} [{result['score']:2d}/10] {result['file'][:40]}")
        if result.get("title"):
            print(f"         Title: {result['title']}")
        for reason in result.get("reasons", []):
            print(f"         - {reason}")
        print()

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Total sources: {results['summary']['total']}")
    print(f"  \033[92mValid:\033[0m {results['summary']['valid']}")
    print(f"  \033[91mRejected:\033[0m {results['summary']['rejected']}")
    print(f"  \033[93mEmpty:\033[0m {results['summary']['empty']}")
    print(f"  Errors: {results['summary']['error']}")

    valid_pct = (results['summary']['valid'] / results['summary']['total'] * 100) if results['summary']['total'] > 0 else 0
    print(f"\n  Validity rate: {valid_pct:.1f}%")

    if valid_pct < 60:
        print(f"\n  \033[91mWARNING: Low validity rate. Need more targeted research.\033[0m")
    elif valid_pct < 80:
        print(f"\n  \033[93mCAUTION: Some sources may be about wrong game.\033[0m")
    else:
        print(f"\n  \033[92mGOOD: Most sources are relevant.\033[0m")

    # Save results
    output_file = folder / "_validation_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Report saved to: {output_file}")

    # Optionally move rejected files
    if move_rejected and results['summary']['rejected'] > 0:
        rejected_dir = folder / "_rejected"
        rejected_dir.mkdir(exist_ok=True)
        for source in results['sources']:
            if source['status'] == 'rejected':
                src = folder / source['file']
                dst = rejected_dir / source['file']
                if src.exists():
                    src.rename(dst)
                    print(f"  Moved rejected: {source['file']}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate research source relevance")
    parser.add_argument("game_slug", help="Game folder slug in research/")
    parser.add_argument("--move-rejected", action="store_true",
                       help="Move rejected sources to _rejected/ subfolder")
    parser.add_argument("--list-configs", action="store_true",
                       help="List available game configs")

    args = parser.parse_args()

    if args.list_configs:
        print("Available game configs:")
        for slug, config in GAME_CONFIGS.items():
            print(f"  - {slug}: {config['game_title']}")
        return

    results = validate_game_research(args.game_slug, args.move_rejected)

    # Exit with error if too few valid sources
    if results.get("summary", {}).get("valid", 0) < 10:
        print(f"\n\033[91mERROR: Need at least 10 valid sources. Have {results['summary']['valid']}.\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
