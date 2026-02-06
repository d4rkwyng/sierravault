#!/usr/bin/env python3
"""
MobyGames Web Crawler for Sierra Games Archive

Scrapes MobyGames pages for all games in research folder.
Uses ScraperAPI for reliable scraping.

Pages scraped per game:
- Main game page (description, specs, releases)
- Credits page (full development credits)
- Reviews page (critic and player reviews)
- Screenshots page (screenshot listings)

Usage:
    python crawl_mobygames.py                    # Crawl all games missing MobyGames data
    python crawl_mobygames.py --game "kings-quest-iv"  # Single game
    python crawl_mobygames.py --pages credits    # Only crawl credits pages
    python crawl_mobygames.py --force            # Re-crawl even if data exists
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus, urlparse

from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError

# Configuration
SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY', '')
SCRAPERAPI_URL = "http://api.scraperapi.com"
RATE_LIMIT_DELAY = 1.0  # Seconds between requests

# Paths
SCRIPTS_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPTS_DIR.parent
INTERNAL_DIR = PROJECT_DIR.parent / "sierravault-internal"
RESEARCH_DIR = INTERNAL_DIR / "research" / "games"

# MobyGames URL patterns
MOBY_BASE = "https://www.mobygames.com"
MOBY_PAGES = ["", "/credits", "/reviews", "/screenshots"]


def get_source_id(url: str) -> str:
    """Generate unique source ID from URL."""
    h = hashlib.md5(url.encode()).hexdigest()[:6]
    domain = urlparse(url).netloc.replace("www.", "").replace(".", "_")
    return f"{domain}_{h}"


def scrape_url(url: str) -> dict:
    """Scrape a URL via ScraperAPI."""
    if not SCRAPERAPI_KEY:
        print("ERROR: SCRAPERAPI_KEY not set in environment")
        return {}
    
    params = urlencode({
        "api_key": SCRAPERAPI_KEY,
        "url": url,
        "render": "false",  # MobyGames works without JS
    })
    api_url = f"{SCRAPERAPI_URL}?{params}"
    
    try:
        req = Request(api_url, headers={"User-Agent": "SierraVault/1.0"})
        with urlopen(req, timeout=60) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            return {
                "url": url,
                "fetch_date": datetime.now().isoformat(),
                "fetch_method": "scraperapi",
                "fetch_status": "success",
                "html": html[:100000],  # Limit size
            }
    except HTTPError as e:
        return {
            "url": url,
            "fetch_date": datetime.now().isoformat(),
            "fetch_status": f"error_{e.code}",
        }
    except Exception as e:
        return {
            "url": url,
            "fetch_date": datetime.now().isoformat(),
            "fetch_status": f"error_{str(e)[:100]}",
        }


def extract_moby_id(research_dir: Path) -> int | None:
    """Extract MobyGames game ID from existing research data."""
    # Try API data first (both naming conventions)
    for api_name in ["mobygames.json", "mobygames_api.json"]:
        api_file = research_dir / api_name
        if api_file.exists():
            try:
                data = json.loads(api_file.read_text())
                if data.get("game_id"):
                    return data["game_id"]
            except:
                pass
    
    # Try scraped pages
    for f in research_dir.glob("mobygames_com_*.json"):
        try:
            data = json.loads(f.read_text())
            url = data.get("url", "")
            # Extract ID from URL like /game/1234/title/
            match = re.search(r"/game/(\d+)/", url)
            if match:
                return int(match.group(1))
        except:
            continue
    
    return None


def get_game_title(research_dir: Path) -> str:
    """Get game title from research data."""
    # Try API data
    api_file = research_dir / "mobygames.json"
    if api_file.exists():
        try:
            data = json.loads(api_file.read_text())
            if data.get("title"):
                return data["title"]
        except:
            pass
    
    # Try Wikipedia
    for f in research_dir.glob("en_wikipedia_*.json"):
        try:
            data = json.loads(f.read_text())
            if data.get("page_title"):
                return data["page_title"].split(" - ")[0].strip()
        except:
            continue
    
    # Fall back to slug
    return research_dir.name.replace("-", " ").title()


def crawl_game(game_slug: str, pages: list[str], force: bool = False) -> dict:
    """Crawl MobyGames pages for a single game."""
    research_dir = RESEARCH_DIR / game_slug
    if not research_dir.exists():
        return {"error": f"Research dir not found: {game_slug}"}
    
    moby_id = extract_moby_id(research_dir)
    if not moby_id:
        title = get_game_title(research_dir)
        return {"error": f"No MobyGames ID found for {game_slug} ({title})"}
    
    results = {"game": game_slug, "moby_id": moby_id, "pages": {}}
    
    for page_suffix in pages:
        page_name = page_suffix.strip("/") or "main"
        url = f"{MOBY_BASE}/game/{moby_id}/{game_slug}{page_suffix}/"
        
        # Check if already exists
        source_id = get_source_id(url)
        output_file = research_dir / f"mobygames_com_{source_id}.json"
        
        if output_file.exists() and not force:
            results["pages"][page_name] = "skipped (exists)"
            continue
        
        print(f"  Scraping {page_name}: {url}")
        data = scrape_url(url)
        
        if data.get("fetch_status") == "success":
            # Parse and extract useful content
            html = data.pop("html", "")
            data["source_id"] = source_id
            data["domain"] = "www.mobygames.com"
            
            # Extract text content (basic extraction)
            # Remove script/style tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', text)
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            data["full_text"] = text[:50000]  # Limit size
            data["page_title"] = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
            if data["page_title"]:
                data["page_title"] = data["page_title"].group(1).strip()
            
            output_file.write_text(json.dumps(data, indent=2))
            results["pages"][page_name] = "success"
        else:
            results["pages"][page_name] = data.get("fetch_status", "error")
        
        time.sleep(RATE_LIMIT_DELAY)
    
    return results


def find_games_needing_crawl(pages: list[str]) -> list[str]:
    """Find games that need MobyGames data."""
    games_to_crawl = []
    
    for game_dir in sorted(RESEARCH_DIR.iterdir()):
        if not game_dir.is_dir():
            continue
        
        moby_id = extract_moby_id(game_dir)
        if not moby_id:
            continue  # Skip games without MobyGames ID
        
        # Check if any requested pages are missing
        needs_crawl = False
        for page_suffix in pages:
            # We can't know exact URL without crawling, so check for any mobygames files
            moby_files = list(game_dir.glob("mobygames_com_*.json"))
            if len(moby_files) < len(MOBY_PAGES):
                needs_crawl = True
                break
        
        if needs_crawl:
            games_to_crawl.append(game_dir.name)
    
    return games_to_crawl


def main():
    parser = argparse.ArgumentParser(description="Crawl MobyGames for Sierra games")
    parser.add_argument("--game", help="Single game slug to crawl")
    parser.add_argument("--pages", default="all", 
                       help="Pages to crawl: all, main, credits, reviews, screenshots")
    parser.add_argument("--force", action="store_true", help="Re-crawl even if exists")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of games")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be crawled")
    args = parser.parse_args()
    
    # Parse pages
    if args.pages == "all":
        pages = MOBY_PAGES
    else:
        pages = [f"/{p}" if p != "main" else "" for p in args.pages.split(",")]
    
    print(f"MobyGames Crawler")
    print(f"Pages: {[p or 'main' for p in pages]}")
    print(f"Research dir: {RESEARCH_DIR}")
    print()
    
    if args.game:
        games = [args.game]
    else:
        games = find_games_needing_crawl(pages)
        print(f"Found {len(games)} games needing MobyGames data")
    
    if args.limit:
        games = games[:args.limit]
    
    if args.dry_run:
        print("\nWould crawl:")
        for g in games[:20]:
            print(f"  {g}")
        if len(games) > 20:
            print(f"  ... and {len(games) - 20} more")
        return
    
    print()
    success = 0
    errors = 0
    
    for i, game in enumerate(games, 1):
        print(f"[{i}/{len(games)}] {game}")
        result = crawl_game(game, pages, args.force)
        
        if "error" in result:
            print(f"  Error: {result['error']}")
            errors += 1
        else:
            success += 1
            for page, status in result.get("pages", {}).items():
                print(f"    {page}: {status}")
    
    print(f"\nDone: {success} games crawled, {errors} errors")


if __name__ == "__main__":
    main()
