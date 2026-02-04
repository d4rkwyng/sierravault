#!/usr/bin/env python3
"""
Expand Research - Find and crawl additional sources using Kagi + ScraperAPI.

For games with few research files, this script:
1. Searches Kagi for additional sources
2. Filters out already-crawled URLs
3. Uses ScraperAPI to fetch new pages
4. Saves them as research JSON files

Usage:
  python expand_research.py "3-d-ultra-pinball"           # Single game
  python expand_research.py --under 20                    # All games with <20 files
  python expand_research.py --list                        # List games needing expansion
"""

import json
import os
import re
import sys
import argparse
import hashlib
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"

# Load API keys
def load_env():
    env_path = INTERNAL_DIR / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

load_env()
KAGI_API_KEY = os.environ.get('KAGI_API_KEY')
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY')

# Domains to skip (already well-covered or problematic)
SKIP_DOMAINS = {
    'youtube.com', 'youtu.be',  # Video content
    'facebook.com', 'twitter.com', 'x.com', 'instagram.com',  # Social media
    'reddit.com',  # Often blocked
    'pinterest.com',
    'ebay.com', 'amazon.com',  # Shopping
    'archive.org',  # Often slow/complex
}

# Prioritize these domains
PRIORITY_DOMAINS = [
    'mobygames.com',
    'giantbomb.com',
    'igdb.com',
    'pcgamingwiki.com',
    'gamefaqs.gamespot.com',
    'allgame.com',
    'gamespot.com',
    'ign.com',
    'hardcoregaming101.net',
    'adventuregamers.com',
    'sierrachest.com',
    'sierrahelp.com',
]


def get_game_title(folder_name: str) -> str:
    """Convert folder name to search-friendly title."""
    # Load from manifest if available
    manifest_path = GAMES_RESEARCH_DIR / folder_name / "_manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        if manifest.get("game_title"):
            return manifest["game_title"]

    # Convert folder name
    title = folder_name.replace("-", " ").title()
    # Fix common patterns
    title = re.sub(r'\b3 D\b', '3D', title)
    title = re.sub(r'\bV(\d+)\b', r'v\1', title)
    return title


def get_existing_urls(folder_path: Path) -> set:
    """Get URLs already crawled for this game."""
    urls = set()
    for json_file in folder_path.glob("*.json"):
        if json_file.name in ("_manifest.json", "_facts.json"):
            continue
        try:
            with open(json_file) as f:
                data = json.load(f)
            if data.get("url"):
                urls.add(data["url"].lower().rstrip('/'))
        except:
            pass
    return urls


def search_kagi(query: str, limit: int = 20) -> list:
    """Search Kagi for URLs about a game."""
    if not KAGI_API_KEY:
        print("Warning: KAGI_API_KEY not set, skipping Kagi search")
        return []

    try:
        resp = httpx.get(
            "https://kagi.com/api/v0/search",
            headers={"Authorization": f"Bot {KAGI_API_KEY}"},
            params={"q": query, "limit": limit},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("data", []):
            url = item.get("url", "")
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            if url:
                results.append({"url": url, "title": title, "snippet": snippet})

        return results
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print(f"  Kagi API unauthorized - using fallback search")
        else:
            print(f"  Kagi search error: {e}")
        return []
    except Exception as e:
        print(f"  Kagi search error: {e}")
        return []


def search_google_via_scraper(query: str, limit: int = 20) -> list:
    """Search Google using ScraperAPI's Google Search endpoint."""
    if not SCRAPER_API_KEY:
        print("Error: SCRAPER_API_KEY not set")
        return []

    try:
        # ScraperAPI has a Google Search endpoint
        resp = httpx.get(
            "https://api.scraperapi.com/structured/google/search",
            params={
                "api_key": SCRAPER_API_KEY,
                "query": query,
                "num": min(limit, 100)
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("organic_results", []):
            url = item.get("link", "")
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            if url:
                results.append({"url": url, "title": title, "snippet": snippet})

        return results
    except Exception as e:
        print(f"  Google search error: {e}")
        return []


def fetch_with_scraperapi(url: str) -> tuple:
    """Fetch a URL using ScraperAPI."""
    if not SCRAPER_API_KEY:
        return None, "SCRAPER_API_KEY not set"

    try:
        api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
        resp = httpx.get(api_url, timeout=60, follow_redirects=True)

        if resp.status_code == 200:
            return resp.text, "success"
        else:
            return None, f"HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)


def extract_text(html: str) -> str:
    """Extract text content from HTML."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Get text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        # Truncate if too long
        if len(text) > 50000:
            text = text[:50000] + "\n\n[... content truncated ...]"

        return text
    except:
        return ""


def url_to_source_id(url: str) -> str:
    """Convert URL to a source ID filename."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '').replace('.', '_')
    path_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{domain}_{path_hash}"


def save_research_file(folder_path: Path, url: str, content: str, title: str = "") -> Path:
    """Save fetched content as a research JSON file."""
    source_id = url_to_source_id(url)

    data = {
        "source_id": source_id,
        "url": url,
        "fetch_date": datetime.now().isoformat(),
        "fetch_status": "success",
        "page_title": title,
        "full_text": content
    }

    output_path = folder_path / f"{source_id}.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output_path


def expand_game(folder_name: str, target_files: int = 30, workers: int = 5) -> dict:
    """Expand research for a single game."""
    folder_path = GAMES_RESEARCH_DIR / folder_name

    if not folder_path.exists():
        return {"status": "error", "reason": "Folder not found"}

    game_title = get_game_title(folder_name)
    existing_urls = get_existing_urls(folder_path)
    current_count = len(list(folder_path.glob("*.json"))) - 2  # Exclude manifest and facts

    if current_count >= target_files:
        return {"status": "skipped", "reason": f"Already has {current_count} files"}

    needed = target_files - current_count

    print(f"\n{'='*60}")
    print(f"Expanding: {game_title}")
    print(f"Current files: {current_count}, Target: {target_files}, Need: {needed}")
    print(f"{'='*60}")

    # Search for sources - try Kagi first, fall back to Google via ScraperAPI
    queries = [
        f'"{game_title}" game review',
        f'"{game_title}" Sierra game',
        f'{game_title} video game',
    ]

    all_results = []
    use_google = False

    for query in queries:
        print(f"  Searching: {query}")

        # Try Kagi first
        if not use_google:
            results = search_kagi(query, limit=15)
            if not results:
                use_google = True  # Fall back to Google for remaining queries

        # Use Google via ScraperAPI if Kagi failed
        if use_google:
            results = search_google_via_scraper(query, limit=15)

        all_results.extend(results)
        time.sleep(1.0)  # Rate limit

    # Filter and deduplicate URLs
    seen_urls = set()
    new_urls = []

    for result in all_results:
        url = result["url"].lower().rstrip('/')
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')

        # Skip if already crawled or in skip list
        if url in existing_urls or url in seen_urls:
            continue
        if any(skip in domain for skip in SKIP_DOMAINS):
            continue

        seen_urls.add(url)

        # Prioritize certain domains
        priority = 100
        for i, pdom in enumerate(PRIORITY_DOMAINS):
            if pdom in domain:
                priority = i
                break

        new_urls.append((priority, result))

    # Sort by priority and take what we need
    new_urls.sort(key=lambda x: x[0])
    urls_to_fetch = [r for _, r in new_urls[:needed + 5]]  # Fetch a few extra in case some fail

    print(f"  Found {len(new_urls)} new URLs, fetching up to {len(urls_to_fetch)}")

    # Fetch URLs in parallel
    results = {"fetched": 0, "failed": 0, "files": []}

    def fetch_and_save(result):
        url = result["url"]
        title = result.get("title", "")

        html, status = fetch_with_scraperapi(url)
        if status != "success":
            return {"url": url, "status": "failed", "reason": status}

        text = extract_text(html)
        if len(text) < 200:
            return {"url": url, "status": "failed", "reason": "Too little content"}

        output = save_research_file(folder_path, url, text, title)
        return {"url": url, "status": "success", "file": output.name}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_and_save, r): r for r in urls_to_fetch}

        for future in as_completed(futures):
            try:
                result = future.result()
                if result["status"] == "success":
                    results["fetched"] += 1
                    results["files"].append(result["file"])
                    print(f"    ✓ {result['file']}")
                else:
                    results["failed"] += 1
                    print(f"    ✗ {result['url'][:50]}... ({result['reason']})")

                # Stop if we have enough
                if results["fetched"] >= needed:
                    break
            except Exception as e:
                results["failed"] += 1

    print(f"\n  Results: {results['fetched']} fetched, {results['failed']} failed")
    return results


def list_games_needing_expansion(threshold: int = 20):
    """List games with fewer than threshold research files."""
    games = []

    for folder in sorted(GAMES_RESEARCH_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith('_'):
            continue
        json_files = [f for f in folder.glob("*.json") if f.name not in ("_manifest.json", "_facts.json")]
        count = len(json_files)
        if count < threshold:
            title = get_game_title(folder.name)
            games.append((folder.name, title, count))

    games.sort(key=lambda x: x[2])

    print(f"Games with <{threshold} research files: {len(games)}\n")
    print(f"{'Folder':<50} {'Title':<40} {'Files':>5}")
    print("-" * 97)
    for folder, title, count in games:
        print(f"{folder:<50} {title:<40} {count:>5}")

    return games


def main():
    parser = argparse.ArgumentParser(description="Expand research using Kagi + ScraperAPI")
    parser.add_argument("folder", nargs="?", help="Research folder name")
    parser.add_argument("--under", type=int, help="Expand all games with fewer than N files")
    parser.add_argument("--target", type=int, default=30, help="Target number of files (default: 30)")
    parser.add_argument("--list", action="store_true", help="List games needing expansion")
    parser.add_argument("--workers", type=int, default=5, help="Parallel workers (default: 5)")

    args = parser.parse_args()

    if args.list:
        list_games_needing_expansion(args.target)
    elif args.under:
        games = list_games_needing_expansion(args.under)
        print(f"\nExpanding {len(games)} games...")
        for folder, title, count in games:
            expand_game(folder, args.target, args.workers)
    elif args.folder:
        expand_game(args.folder, args.target, args.workers)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
