#!/usr/bin/env python3
"""
Targeted Research - Re-research games with poor quality sources using focused searches.

Uses Brave Search API with targeted queries (game name + year + "review"/"Sierra")
and Kagi FastGPT for quick fact lookups.

Usage:
  python targeted_research.py kings-quest-vii          # Single game
  python targeted_research.py --worst 20               # 20 worst quality games
  python targeted_research.py --list                   # List games needing help
"""

import json
import os
import re
import hashlib
import time
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

RESEARCH_DIR = Path(__file__).parent / "research"

# Load API keys
def load_env():
    env_path = Path(__file__).parent / ".env"
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
BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY')
KAGI_API_KEY = os.environ.get('KAGI_API_KEY')
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY')

# Skip these domains (already covered or problematic)
SKIP_DOMAINS = {
    'youtube.com', 'youtu.be', 'facebook.com', 'twitter.com', 'x.com',
    'instagram.com', 'reddit.com', 'pinterest.com', 'ebay.com', 'amazon.com',
}

# Prioritize these for game info
PRIORITY_DOMAINS = [
    'mobygames.com', 'giantbomb.com', 'igdb.com', 'pcgamingwiki.com',
    'adventuregamers.com', 'hardcoregaming101.net', 'sierrachest.com',
    'gamespot.com', 'ign.com', 'gamefaqs.gamespot.com',
]


def get_game_info(folder_name: str) -> dict:
    """Get game title and year from manifest or folder name."""
    manifest_path = RESEARCH_DIR / folder_name / "_manifest.json"
    info = {"title": folder_name.replace("-", " ").title(), "year": None}

    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        info["title"] = manifest.get("game_title", info["title"])
        info["year"] = manifest.get("release_year")

    # Try to extract year from title or folder
    if not info["year"]:
        year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', info["title"])
        if year_match:
            info["year"] = year_match.group(1)

    return info


def get_existing_urls(folder_path: Path) -> set:
    """Get URLs already crawled for this game."""
    urls = set()
    for json_file in folder_path.glob("*.json"):
        if json_file.name.startswith("_"):
            continue
        try:
            with open(json_file) as f:
                data = json.load(f)
            if data.get("url"):
                urls.add(data["url"].lower().rstrip('/'))
        except:
            pass
    return urls


def search_brave(query: str, count: int = 10) -> list:
    """Search using Brave Search API."""
    if not BRAVE_API_KEY:
        print("  Warning: BRAVE_API_KEY not set")
        return []

    try:
        resp = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": BRAVE_API_KEY},
            params={"q": query, "count": count},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            url = item.get("url", "")
            title = item.get("title", "")
            desc = item.get("description", "")
            if url:
                results.append({"url": url, "title": title, "snippet": desc})
        return results
    except Exception as e:
        print(f"  Brave search error: {e}")
        return []


def query_kagi_fastgpt(query: str) -> dict:
    """Query Kagi FastGPT for quick facts with sources."""
    if not KAGI_API_KEY:
        return {}

    try:
        resp = httpx.post(
            "https://kagi.com/api/v0/fastgpt",
            headers={"Authorization": f"Bot {KAGI_API_KEY}"},
            json={"query": query},
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {
            "output": data.get("output", ""),
            "references": data.get("references", [])
        }
    except Exception as e:
        print(f"  Kagi FastGPT error: {e}")
        return {}


def fetch_with_scraper(url: str) -> tuple:
    """Fetch URL using ScraperAPI."""
    if not SCRAPER_API_KEY:
        return None, "SCRAPER_API_KEY not set"

    try:
        api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
        resp = httpx.get(api_url, timeout=60, follow_redirects=True)
        if resp.status_code == 200:
            return resp.text, "success"
        return None, f"HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)


def extract_text(html: str) -> str:
    """Extract text from HTML."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        text = soup.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        if len(text) > 50000:
            text = text[:50000] + "\n\n[... truncated ...]"
        return text
    except:
        return ""


def url_to_source_id(url: str) -> str:
    """Convert URL to source ID."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '').replace('.', '_')
    path_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{domain}_{path_hash}"


def save_research(folder_path: Path, url: str, content: str, title: str = "") -> Path:
    """Save research file."""
    source_id = url_to_source_id(url)
    data = {
        "source_id": source_id,
        "url": url,
        "fetch_date": datetime.now().isoformat(),
        "fetch_status": "success",
        "page_title": title,
        "full_text": content
    }
    output = folder_path / f"{source_id}.json"
    with open(output, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output


def save_kagi_response(folder_path: Path, query: str, response: dict) -> Path:
    """Save Kagi FastGPT response with references."""
    query_hash = hashlib.md5(query.encode()).hexdigest()[:8]

    # Format references for full_text
    output_text = response.get("output", "")
    refs = response.get("references", [])

    if refs:
        output_text += "\n\n## Sources:\n"
        for i, ref in enumerate(refs, 1):
            output_text += f"[{i}] {ref.get('title', 'Unknown')}\n"
            output_text += f"    URL: {ref.get('url', '')}\n"
            if ref.get('snippet'):
                output_text += f"    {ref.get('snippet', '')[:200]}\n"
            output_text += "\n"

    data = {
        "source_id": f"kagi_fastgpt_{query_hash}",
        "url": f"kagi:fastgpt:{query}",
        "fetch_date": datetime.now().isoformat(),
        "fetch_status": "success",
        "query": query,
        "full_text": output_text,
        "kagi_references": refs  # Store structured references too
    }
    output = folder_path / f"kagi_fastgpt_{query_hash}.json"
    with open(output, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output


def research_game(folder_name: str, max_new_sources: int = 10) -> dict:
    """Research a single game with targeted searches."""
    folder_path = RESEARCH_DIR / folder_name
    if not folder_path.exists():
        return {"status": "error", "reason": "Folder not found"}

    game_info = get_game_info(folder_name)
    title = game_info["title"]
    year = game_info["year"]
    existing_urls = get_existing_urls(folder_path)

    print(f"\n{'='*60}")
    print(f"Targeted Research: {title}" + (f" ({year})" if year else ""))
    print(f"Existing sources: {len(existing_urls)}")
    print(f"{'='*60}")

    # Clean up title for better search
    clean_title = title.replace(" Xl", " XL").replace(" Ii", " II").replace(" Iii", " III")
    clean_title = clean_title.replace(" Iv", " IV").replace(" Vi", " VI")

    # Build focused search queries - try with and without quotes
    queries = [
        f'{clean_title} video game review',
        f'{clean_title} Sierra game',
        f'"{clean_title}" game',
    ]
    if year:
        queries.append(f'{clean_title} {year} game review')
        queries.append(f'{clean_title} {year}')

    # Add genre-specific searches based on title keywords
    if any(kw in title.lower() for kw in ['quest', 'adventure']):
        queries.append(f'"{title}" adventure game walkthrough')
    if any(kw in title.lower() for kw in ['racing', 'nascar', 'driver']):
        queries.append(f'"{title}" racing game review')

    # Search and collect URLs
    all_results = []
    for query in queries[:4]:  # Limit queries
        print(f"  Searching: {query}")
        results = search_brave(query, count=10)
        all_results.extend(results)
        time.sleep(0.5)

    # Filter and dedupe
    seen = set()
    new_urls = []
    for r in all_results:
        url = r["url"].lower().rstrip('/')
        if url in existing_urls or url in seen:
            continue
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        if any(skip in domain for skip in SKIP_DOMAINS):
            continue
        seen.add(url)

        # Priority scoring
        priority = 100
        for i, pdom in enumerate(PRIORITY_DOMAINS):
            if pdom in domain:
                priority = i
                break
        new_urls.append((priority, r))

    new_urls.sort(key=lambda x: x[0])
    urls_to_fetch = [r for _, r in new_urls[:max_new_sources]]

    print(f"  Found {len(new_urls)} new URLs, fetching {len(urls_to_fetch)}")

    # Fetch URLs
    results = {"fetched": 0, "failed": 0, "files": []}

    for r in urls_to_fetch:
        url = r["url"]
        html, status = fetch_with_scraper(url)
        if status != "success":
            results["failed"] += 1
            print(f"    ✗ {url[:50]}... ({status})")
            continue

        text = extract_text(html)
        if len(text) < 200:
            results["failed"] += 1
            print(f"    ✗ {url[:50]}... (too short)")
            continue

        output = save_research(folder_path, url, text, r.get("title", ""))
        results["fetched"] += 1
        results["files"].append(output.name)
        print(f"    ✓ {output.name}")
        time.sleep(0.5)

    # Also query Kagi FastGPT for quick facts with sources
    print(f"  Querying Kagi FastGPT...")
    kagi_queries = [
        f"What year was {title} video game released and who developed it?",
        f"What were the review scores for {title} video game?",
    ]

    kagi_ref_urls = []  # Collect reference URLs to crawl
    for kq in kagi_queries:
        response = query_kagi_fastgpt(kq)
        if response and response.get("output") and len(response.get("output", "")) > 50:
            output = save_kagi_response(folder_path, kq, response)
            results["files"].append(output.name)
            refs = response.get("references", [])
            ref_count = len(refs)
            print(f"    ✓ {output.name} ({ref_count} sources)")
            # Collect reference URLs for crawling
            for ref in refs:
                url = ref.get("url", "")
                if url and url.lower().rstrip('/') not in existing_urls:
                    kagi_ref_urls.append({"url": url, "title": ref.get("title", "")})
        time.sleep(1)

    # Crawl Kagi reference URLs with ScraperAPI
    if kagi_ref_urls:
        # Dedupe and filter
        seen = set()
        unique_refs = []
        for r in kagi_ref_urls:
            url = r["url"].lower().rstrip('/')
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            if url not in seen and not any(skip in domain for skip in SKIP_DOMAINS):
                seen.add(url)
                unique_refs.append(r)

        to_crawl = unique_refs[:5]  # Limit to 5 Kagi refs
        if to_crawl:
            print(f"  Crawling {len(to_crawl)} Kagi reference URLs...")
            for r in to_crawl:
                url = r["url"]
                html, status = fetch_with_scraper(url)
                if status == "success":
                    text = extract_text(html)
                    if len(text) >= 200:
                        out = save_research(folder_path, url, text, r.get("title", ""))
                        results["fetched"] += 1
                        results["files"].append(out.name)
                        print(f"    ✓ {out.name} (from Kagi ref)")
                    else:
                        print(f"    ✗ {url[:50]}... (too short)")
                else:
                    print(f"    ✗ {url[:50]}... ({status})")
                time.sleep(0.5)

    print(f"\n  Results: {results['fetched']} fetched, {results['failed']} failed")
    return results


def get_worst_games(limit: int = 20) -> list:
    """Get games with worst research quality."""
    skip_patterns = ["_manifest", "_facts", "_urls", "kagi_", "llm_"]
    game_quality = []

    for folder in sorted(RESEARCH_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith('_'):
            continue

        good = 0
        empty = 0
        total = 0

        for f in folder.glob("*.json"):
            if any(p in f.name for p in skip_patterns):
                continue
            total += 1
            try:
                with open(f) as fp:
                    data = json.load(fp)
                ef = data.get("extracted_facts", {})
                if ef and len(ef) > 0:
                    has_content = any(
                        v and not (isinstance(v, (list, dict)) and len(v) == 0)
                        for v in ef.values()
                    )
                    if has_content:
                        good += 1
                    else:
                        empty += 1
            except:
                pass

        if total > 0 and empty >= 3:
            good_pct = 100 * good / total
            game_quality.append((folder.name, total, good, empty, good_pct))

    game_quality.sort(key=lambda x: x[4])
    return game_quality[:limit]


def main():
    parser = argparse.ArgumentParser(description="Targeted research for low-quality games")
    parser.add_argument("folder", nargs="?", help="Research folder name")
    parser.add_argument("--worst", type=int, help="Research N worst quality games")
    parser.add_argument("--list", action="store_true", help="List games needing help")
    parser.add_argument("--max-sources", type=int, default=10, help="Max new sources per game")

    args = parser.parse_args()

    if args.list:
        games = get_worst_games(30)
        print(f"{'Game':<50} {'Total':>6} {'Good':>6} {'Empty':>6} {'%Good':>6}")
        print("-" * 80)
        for name, total, good, empty, pct in games:
            print(f"{name:<50} {total:>6} {good:>6} {empty:>6} {pct:>5.1f}%")

    elif args.worst:
        games = get_worst_games(args.worst)
        print(f"Researching {len(games)} worst quality games...")
        for name, total, good, empty, pct in games:
            research_game(name, args.max_sources)

    elif args.folder:
        research_game(args.folder, args.max_sources)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
