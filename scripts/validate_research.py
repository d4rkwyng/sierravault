#!/usr/bin/env python3
"""
Research Quality Validator for Sierra Games Archive

Validates that a game's research folder has sufficient quality data
before page generation. Checks:
1. Minimum number of source files
2. Required source types (MobyGames, Wikipedia, etc.)
3. Content quality (word count, no error pages)
4. Data consistency across sources

Usage:
    python3 validate_research.py <game-slug>
    python3 validate_research.py --all
"""

import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

INTERNAL_DIR = Path(__file__).parent
RESEARCH_DIR = INTERNAL_DIR / "research"

# Validation thresholds
MIN_SOURCE_FILES = 15  # Minimum unique source files
MIN_TOTAL_WORDS = 3000  # Minimum total words across all sources
MIN_UNIQUE_DOMAINS = 5  # Minimum unique domains

# Required source types (at least one from each category)
REQUIRED_SOURCES = {
    "database": ["mobygames.json", "mobygames_api.json"],  # MobyGames API data
    "encyclopedia": ["en_wikipedia", "wikipedia"],  # Wikipedia
    "llm": ["llm_claude.json", "llm_openai.json", "kagi_fastgpt.json"],  # LLM research
}

# High-value domains that indicate good research
HIGH_VALUE_DOMAINS = [
    "mobygames.com",
    "wikipedia.org",
    "adventuregamers.com",
    "pcgamingwiki.com",
    "sierrahelp.com",
    "sierrachest.com",
    "archive.org",
    "filfre.net",
    "hardcoregaming101.net",
]

# Bad content patterns - indicates search pages, error pages, etc.
BAD_CONTENT_PATTERNS = [
    "search results for",
    "no results found",
    "0 results",
    "did not match any",
    "page not found",
    "404 error",
    "access denied",
    "please enable javascript",
    "checking your browser",
    "just a moment",
    "cloudflare",
]

# Search page URL patterns
SEARCH_URL_PATTERNS = [
    "/search?",
    "/search/?",
    "?q=",
    "?query=",
    "?search=",
    "/find?",
]


def count_words(text: str) -> int:
    """Count words in text."""
    if not text:
        return 0
    return len(text.split())


def is_bad_content(content: str, url: str = "") -> tuple[bool, str]:
    """
    Check if content is bad (search page, error page, etc.)
    Returns (is_bad, reason).
    """
    if not content:
        return True, "empty"

    content_lower = content.lower()

    # Check for bad content patterns
    for pattern in BAD_CONTENT_PATTERNS:
        if pattern in content_lower[:2000]:  # Check first 2000 chars
            return True, f"bad_pattern: {pattern}"

    # Check URL for search patterns
    if url:
        for pattern in SEARCH_URL_PATTERNS:
            if pattern in url:
                return True, f"search_url: {pattern}"

    # Check word count - very short content is suspicious
    word_count = count_words(content)
    if word_count < 100:
        return True, f"too_short: {word_count} words"

    return False, ""


def get_quality_sources(folder: Path, game_title: str = "") -> tuple[list, list]:
    """
    Analyze sources and return (good_sources, bad_sources).
    Each entry is (filename, reason).
    """
    good_sources = []
    bad_sources = []

    json_files = list(folder.glob("*.json"))
    source_files = [f for f in json_files if f.name not in ["_urls.json"]]

    for json_file in source_files:
        try:
            with open(json_file) as f:
                data = json.load(f)

            # Get content and URL
            content = ""
            url = data.get("url", "")

            if "full_text" in data:
                content = data["full_text"]
            elif "game_details" in data:  # MobyGames API format
                content = json.dumps(data.get("game_details", {}))
            elif "data" in data and isinstance(data["data"], dict):
                content = json.dumps(data["data"])
            elif "queries" in data:  # Kagi FastGPT format
                for q in data.get("queries", []):
                    if "response" in q and "data" in q["response"]:
                        content += q["response"]["data"].get("output", "")
            elif "search_results" in data:  # MobyGames API alt format
                content = json.dumps(data.get("search_results", {}))

            # Check if content is bad
            is_bad, reason = is_bad_content(content, url)

            if is_bad:
                bad_sources.append((json_file.name, reason))
            else:
                good_sources.append((json_file.name, count_words(content)))

        except Exception as e:
            bad_sources.append((json_file.name, f"error: {e}"))

    return good_sources, bad_sources


def validate_research(game_slug: str) -> dict:
    """
    Validate research quality for a game.

    Returns dict with:
        - valid: bool
        - score: int (0-100)
        - issues: list of issues found
        - stats: dict of statistics
        - bad_sources: list of (filename, reason) tuples
    """
    folder = RESEARCH_DIR / game_slug
    if not folder.exists():
        return {
            "valid": False,
            "score": 0,
            "issues": [f"Research folder not found: {game_slug}"],
            "stats": {},
            "bad_sources": []
        }

    issues = []
    stats = defaultdict(int)

    # Get quality analysis of sources
    good_sources, bad_sources = get_quality_sources(folder)
    stats["good_sources"] = len(good_sources)
    stats["bad_sources"] = len(bad_sources)

    # Get all JSON files for total count
    json_files = list(folder.glob("*.json"))
    stats["total_files"] = len(json_files)
    source_files = [f for f in json_files if f.name not in ["_urls.json"]]
    stats["source_files"] = len(source_files)

    # Check minimum GOOD files (not just any files)
    if len(good_sources) < MIN_SOURCE_FILES:
        issues.append(f"Insufficient good sources: {len(good_sources)}/{MIN_SOURCE_FILES} files")

    # Report bad sources
    if bad_sources:
        issues.append(f"Bad sources found: {len(bad_sources)} files")

    # Analyze good sources only
    domains = set()
    total_words = 0
    has_required = {cat: False for cat in REQUIRED_SOURCES}
    high_value_count = 0

    for json_file in source_files:
        try:
            with open(json_file) as f:
                data = json.load(f)

            # Check for required source types
            for category, patterns in REQUIRED_SOURCES.items():
                for pattern in patterns:
                    if pattern in json_file.name:
                        has_required[category] = True
                        break

            # Extract domain
            domain = None
            if "domain" in data:
                domain = data["domain"]
            elif "url" in data:
                from urllib.parse import urlparse
                domain = urlparse(data["url"]).netloc

            if domain:
                domains.add(domain)
                # Check high-value domains
                for hv in HIGH_VALUE_DOMAINS:
                    if hv in domain:
                        high_value_count += 1
                        break

            # Count words in content (only from good sources)
            content = ""
            if "full_text" in data:
                content = data["full_text"]
            elif "game_details" in data:  # MobyGames API format
                content = json.dumps(data.get("game_details", {}))
            elif "data" in data and isinstance(data["data"], dict):
                content = json.dumps(data["data"])
            elif "queries" in data:  # Kagi FastGPT format
                for q in data.get("queries", []):
                    if "response" in q and "data" in q["response"]:
                        content += q["response"]["data"].get("output", "")
            elif "search_results" in data:  # MobyGames API alt format
                content = json.dumps(data.get("search_results", {}))

            # Only count words if this is a good source
            is_bad, _ = is_bad_content(content, data.get("url", ""))
            if not is_bad:
                total_words += count_words(content)

        except Exception as e:
            issues.append(f"Error reading {json_file.name}: {e}")

    stats["unique_domains"] = len(domains)
    stats["total_words"] = total_words
    stats["high_value_sources"] = high_value_count

    # Check required sources
    missing_required = []
    for category, found in has_required.items():
        if not found:
            missing_required.append(category)

    if missing_required:
        issues.append(f"Missing required source types: {', '.join(missing_required)}")

    # Check domain diversity
    if len(domains) < MIN_UNIQUE_DOMAINS:
        issues.append(f"Low domain diversity: {len(domains)}/{MIN_UNIQUE_DOMAINS} domains")

    # Check content volume
    if total_words < MIN_TOTAL_WORDS:
        issues.append(f"Insufficient content: {total_words}/{MIN_TOTAL_WORDS} words")

    # Calculate score
    score = 0

    # Files (30 points) - based on GOOD sources, not total
    file_score = min(30, (len(good_sources) / MIN_SOURCE_FILES) * 30)
    score += file_score

    # Penalty for bad sources (up to -10 points)
    bad_penalty = min(10, len(bad_sources) * 2)
    score -= bad_penalty

    # Required sources (30 points)
    required_score = (len(has_required) - len(missing_required)) / len(has_required) * 30
    score += required_score

    # Domain diversity (20 points)
    domain_score = min(20, (len(domains) / MIN_UNIQUE_DOMAINS) * 20)
    score += domain_score

    # Content volume (20 points)
    content_score = min(20, (total_words / MIN_TOTAL_WORDS) * 20)
    score += content_score

    return {
        "valid": len(issues) == 0,
        "score": max(0, round(score)),  # Don't go below 0
        "issues": issues,
        "stats": dict(stats),
        "domains": list(domains),
        "bad_sources": bad_sources
    }


def print_validation(game_slug: str, result: dict, verbose: bool = False):
    """Print validation results."""
    status = "PASS" if result["valid"] else "FAIL"
    color = "\033[92m" if result["valid"] else "\033[91m"
    reset = "\033[0m"
    yellow = "\033[93m"

    print(f"{color}{status}{reset} {game_slug}: {result['score']}/100")

    if result["stats"]:
        stats = result["stats"]
        good = stats.get('good_sources', 0)
        bad = stats.get('bad_sources', 0)
        print(f"  Good: {good} | Bad: {bad} | "
              f"Domains: {stats.get('unique_domains', 0)} | "
              f"Words: {stats.get('total_words', 0)} | "
              f"High-value: {stats.get('high_value_sources', 0)}")

    if result["issues"]:
        for issue in result["issues"]:
            print(f"  - {issue}")

    # Show bad sources if verbose or if there are many
    bad_sources = result.get("bad_sources", [])
    if bad_sources and (verbose or len(bad_sources) <= 5):
        print(f"  {yellow}Bad sources:{reset}")
        for filename, reason in bad_sources[:10]:
            print(f"    - {filename}: {reason}")
        if len(bad_sources) > 10:
            print(f"    ... and {len(bad_sources) - 10} more")


def main():
    parser = argparse.ArgumentParser(description="Validate research quality")
    parser.add_argument("game_slug", nargs="?", help="Game slug to validate")
    parser.add_argument("--all", action="store_true", help="Validate all games")
    parser.add_argument("--min-score", type=int, default=70, help="Minimum passing score")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show bad sources")
    args = parser.parse_args()

    if args.all:
        # Validate all games
        results = {}
        for folder in sorted(RESEARCH_DIR.iterdir()):
            if folder.is_dir() and not folder.name.startswith("_"):
                result = validate_research(folder.name)
                results[folder.name] = result
                if not args.json:
                    print_validation(folder.name, result, args.verbose)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Summary
            passing = sum(1 for r in results.values() if r["valid"])
            print(f"\n{passing}/{len(results)} games pass validation")

    elif args.game_slug:
        result = validate_research(args.game_slug)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_validation(args.game_slug, result, verbose=True)  # Always verbose for single game

        sys.exit(0 if result["valid"] else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
