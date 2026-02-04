#!/usr/bin/env python3
"""
MobyGames API-based research for games, developers, designers, and publishers.
Uses the official MobyGames API for structured data.
"""

import os
import re
import json
import time
from pathlib import Path
from urllib.parse import quote_plus

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# API Configuration
MOBYGAMES_API_KEY = os.environ.get('MOBYGAMES_API_KEY', '')
API_BASE = "https://api.mobygames.com/v1"
RATE_LIMIT_DELAY = 1.5  # MobyGames recommends 1 req/sec

RESEARCH_DIR = Path("research")


def slugify(title: str) -> str:
    """Convert title to folder slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return re.sub(r'-+', '-', slug).strip('-')


def api_request(endpoint: str, params: dict = None) -> dict:
    """Make a MobyGames API request."""
    if not MOBYGAMES_API_KEY:
        print("ERROR: MOBYGAMES_API_KEY not set")
        return {}

    url = f"{API_BASE}/{endpoint}"
    headers = {"Accept": "application/json"}
    params = params or {}
    params["api_key"] = MOBYGAMES_API_KEY

    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            print("  Rate limited, waiting 10s...")
            time.sleep(10)
            return api_request(endpoint, params)
        else:
            print(f"  API error: {resp.status_code}")
            return {}
    except Exception as e:
        print(f"  Request error: {e}")
        return {}


def search_game(title: str) -> dict:
    """Search for a game by title."""
    print(f"  Searching MobyGames for: {title}")
    data = api_request("games", {"title": title})
    time.sleep(RATE_LIMIT_DELAY)
    return data


def get_game_details(game_id: int) -> dict:
    """Get full game details by ID."""
    print(f"  Getting game details: {game_id}")
    data = api_request(f"games/{game_id}")
    time.sleep(RATE_LIMIT_DELAY)
    return data


def get_game_platforms(game_id: int) -> dict:
    """Get all platforms for a game."""
    data = api_request(f"games/{game_id}/platforms")
    time.sleep(RATE_LIMIT_DELAY)
    return data


def get_game_screenshots(game_id: int, platform_id: int = None) -> dict:
    """Get screenshots for a game."""
    endpoint = f"games/{game_id}/platforms/{platform_id}/screenshots" if platform_id else f"games/{game_id}/screenshots"
    data = api_request(endpoint)
    time.sleep(RATE_LIMIT_DELAY)
    return data


def get_game_covers(game_id: int, platform_id: int = None) -> dict:
    """Get cover art for a game."""
    endpoint = f"games/{game_id}/platforms/{platform_id}/covers" if platform_id else f"games/{game_id}/covers"
    data = api_request(endpoint)
    time.sleep(RATE_LIMIT_DELAY)
    return data


def search_company(name: str) -> dict:
    """Search for a company (developer/publisher)."""
    print(f"  Searching companies for: {name}")
    # MobyGames API doesn't have direct company search, use games search
    # and extract company info from results
    data = api_request("games", {"title": name})
    time.sleep(RATE_LIMIT_DELAY)
    return data


def research_game(title: str, output_dir: Path) -> int:
    """Research a single game via MobyGames API."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if already have MobyGames API data
    existing = list(output_dir.glob("mobygames_api*.json"))
    if existing:
        print(f"  Already have MobyGames API data for {title}")
        return 0

    # Search for game
    search_results = search_game(title)
    if not search_results or "games" not in search_results:
        print(f"  No MobyGames results for: {title}")
        return 0

    games = search_results.get("games", [])
    if not games:
        print(f"  No games found for: {title}")
        return 0

    # Find best match
    best_match = None
    title_lower = title.lower()
    for game in games:
        game_title = game.get("title", "").lower()
        if title_lower in game_title or game_title in title_lower:
            best_match = game
            break

    if not best_match:
        best_match = games[0]  # Use first result

    game_id = best_match.get("game_id")
    if not game_id:
        return 0

    print(f"  Found: {best_match.get('title')} (ID: {game_id})")

    # Get full details
    details = get_game_details(game_id)

    # Get platforms
    platforms = get_game_platforms(game_id)

    # Compile all data
    full_data = {
        "source_id": "mobygames_api",
        "game_id": game_id,
        "fetch_date": time.strftime("%Y-%m-%d"),
        "search_results": search_results,
        "game_details": details,
        "platforms": platforms,
        "url": f"https://www.mobygames.com/game/{game_id}/"
    }

    # Save
    out_file = output_dir / "mobygames_api.json"
    with open(out_file, 'w') as f:
        json.dump(full_data, f, indent=2)

    print(f"  Saved MobyGames API data for {title}")
    return 1


def research_person(name: str, person_type: str, output_dir: Path) -> int:
    """Research a person (designer/developer) via MobyGames API."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if already have data
    existing = list(output_dir.glob("mobygames_api*.json"))
    if existing:
        print(f"  Already have MobyGames data for {name}")
        return 0

    # Search games by this person to find their MobyGames profile
    # The API doesn't have direct person search, so we search games
    print(f"  Searching for person: {name}")

    # Try to find games credited to this person
    search_results = api_request("games", {"title": name})
    time.sleep(RATE_LIMIT_DELAY)

    # For now, save the search results
    data = {
        "source_id": "mobygames_api",
        "person_name": name,
        "person_type": person_type,
        "fetch_date": time.strftime("%Y-%m-%d"),
        "search_results": search_results,
        "note": "MobyGames API doesn't have direct person search - web scraping needed for full profile"
    }

    out_file = output_dir / "mobygames_api.json"
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)

    return 1


def research_company(name: str, output_dir: Path) -> int:
    """Research a company (developer/publisher) via MobyGames API."""
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = list(output_dir.glob("mobygames_api*.json"))
    if existing:
        print(f"  Already have MobyGames data for {name}")
        return 0

    # Search for games by this company
    print(f"  Searching for company: {name}")
    search_results = api_request("games", {"title": name})
    time.sleep(RATE_LIMIT_DELAY)

    data = {
        "source_id": "mobygames_api",
        "company_name": name,
        "fetch_date": time.strftime("%Y-%m-%d"),
        "search_results": search_results,
        "note": "MobyGames API doesn't have direct company endpoint - games published/developed by this company"
    }

    out_file = output_dir / "mobygames_api.json"
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)

    return 1


def main():
    import argparse
    parser = argparse.ArgumentParser(description='MobyGames API research')
    parser.add_argument('--games', nargs='+', help='Game titles to research')
    parser.add_argument('--designers', nargs='+', help='Designer names')
    parser.add_argument('--developers', nargs='+', help='Developer company names')
    parser.add_argument('--all-missing', action='store_true',
                       help='Research all games missing MobyGames API data')
    parser.add_argument('--limit', type=int, default=20)
    args = parser.parse_args()

    if not HAS_HTTPX:
        print("ERROR: httpx required")
        return

    if not MOBYGAMES_API_KEY:
        print("ERROR: MOBYGAMES_API_KEY not set in environment")
        print("Run: source .env")
        return

    total_files = 0

    # Research games
    if args.games:
        for title in args.games[:args.limit]:
            slug = slugify(title)
            output_dir = RESEARCH_DIR / slug
            files = research_game(title, output_dir)
            total_files += files

    # Research all missing
    if args.all_missing:
        count = 0
        for game_dir in sorted(RESEARCH_DIR.iterdir()):
            if not game_dir.is_dir() or game_dir.name.startswith('_'):
                continue
            if game_dir.name == 'people':
                continue

            # Check if has mobygames_api.json
            if list(game_dir.glob("mobygames_api.json")):
                continue

            # Get game title from existing files
            title = game_dir.name.replace('-', ' ').title()

            print(f"\nResearching: {title}")
            files = research_game(title, game_dir)
            total_files += files
            count += 1

            if count >= args.limit:
                break

    # Research designers
    if args.designers:
        for name in args.designers[:args.limit]:
            slug = slugify(name)
            output_dir = RESEARCH_DIR / "people" / "designers" / slug
            files = research_person(name, "designer", output_dir)
            total_files += files

    # Research developers
    if args.developers:
        for name in args.developers[:args.limit]:
            slug = slugify(name)
            output_dir = RESEARCH_DIR / "people" / "developers" / slug
            files = research_company(name, output_dir)
            total_files += files

    print(f"\nTotal files created: {total_files}")


if __name__ == '__main__':
    main()
