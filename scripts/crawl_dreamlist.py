#!/usr/bin/env python3
"""
Crawl GOG Dreamlist API to find Sierra games and build slug mapping.

The API at gamesdb.gog.com/wishlist/wishlisted_games returns ~104K games.
This script paginates through all pages and collects Sierra-published games.
"""

import json
import time
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

API_URL = "https://gamesdb.gog.com/wishlist/wishlisted_games"
OUTPUT_FILE = Path(__file__).parent.parent / "dreamlist_sierra_games.json"
FULL_OUTPUT = Path(__file__).parent.parent / "dreamlist_all_slugs.json"

# Publishers to look for (case-insensitive)
SIERRA_PUBLISHERS = [
    "sierra",
    "sierra entertainment",
    "sierra on-line",
    "sierra online",
    "vivendi",
    "cuc software",
    "dynamix",
    "papyrus",
    "impressions",
    "radical entertainment",  # Some Sierra-published games
]


def fetch_page(page: int, limit: int = 50) -> dict:
    """Fetch a single page from the API."""
    url = f"{API_URL}?limit={limit}&page={page}"
    req = Request(url, headers={"User-Agent": "SierraVault/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except (URLError, HTTPError) as e:
        print(f"  Error on page {page}: {e}")
        return {"items": [], "pagination": {"pages": 0}}


def is_sierra_game(item: dict) -> bool:
    """Check if game is published by Sierra or related companies."""
    publishers = [p.get("name", "").lower() for p in item.get("publishers", [])]
    developers = [d.get("name", "").lower() for d in item.get("developers", [])]
    all_companies = publishers + developers
    
    for company in all_companies:
        for sierra_name in SIERRA_PUBLISHERS:
            if sierra_name in company:
                return True
    return False


def extract_slug(item: dict) -> str:
    """Extract slug from product_page URL."""
    url = item.get("product_page", {}).get("url", "")
    if "/game/" in url:
        return url.split("/game/")[-1]
    return ""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Crawl GOG Dreamlist for Sierra games")
    parser.add_argument("--full", action="store_true", help="Collect ALL games, not just Sierra")
    parser.add_argument("--start", type=int, default=1, help="Start page (for resuming)")
    parser.add_argument("--limit", type=int, default=50, help="Items per page")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests (seconds)")
    args = parser.parse_args()

    # First request to get total pages
    print("Fetching first page to get total count...")
    first = fetch_page(1, args.limit)
    total_pages = first.get("pagination", {}).get("pages", 0)
    print(f"Total pages: {total_pages}")
    
    if total_pages == 0:
        print("Failed to get page count")
        sys.exit(1)

    sierra_games = []
    all_slugs = {}  # slug -> title mapping
    
    for page in range(args.start, total_pages + 1):
        if page % 50 == 0 or page == args.start:
            print(f"Page {page}/{total_pages} - Sierra games found: {len(sierra_games)}")
        
        data = fetch_page(page, args.limit)
        items = data.get("items", [])
        
        for item in items:
            slug = extract_slug(item)
            title = item.get("title", "")
            
            if slug and title:
                all_slugs[slug] = title
                
                if is_sierra_game(item):
                    sierra_games.append({
                        "title": title,
                        "slug": slug,
                        "url": item.get("product_page", {}).get("url", ""),
                        "publishers": [p.get("name") for p in item.get("publishers", [])],
                        "developers": [d.get("name") for d in item.get("developers", [])],
                    })
        
        # Rate limiting
        time.sleep(args.delay)
        
        # Save progress every 100 pages
        if page % 100 == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(sierra_games, f, indent=2)
            print(f"  Saved progress: {len(sierra_games)} Sierra games")
    
    # Final save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(sierra_games, f, indent=2)
    print(f"\n✓ Saved {len(sierra_games)} Sierra games to {OUTPUT_FILE}")
    
    if args.full:
        with open(FULL_OUTPUT, "w") as f:
            json.dump(all_slugs, f)
        print(f"✓ Saved {len(all_slugs)} total slugs to {FULL_OUTPUT}")


if __name__ == "__main__":
    main()
