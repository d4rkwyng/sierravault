#!/usr/bin/env python3
"""Crawl sources with render=true for protected sites like ScummVM wiki."""
import asyncio
import hashlib
import httpx
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup

SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')
MAX_CONTENT_SIZE = 50000
TIMEOUT = 90

# Domains that need render=true (JS-heavy or bot protection)
RENDER_DOMAINS = [
    "wiki.scummvm.org",
    "sciwiki.sierrahelp.com",
    "agiwiki.sierrahelp.com",
]

def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except:
        return ""

def url_to_source_id(url: str) -> str:
    domain = get_domain(url)
    clean_domain = domain.replace("www.", "").replace(".", "_")
    url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    return f"{clean_domain}_{url_hash}"

def needs_render(url: str) -> bool:
    """Check if URL needs render=true for JavaScript execution."""
    domain = get_domain(url)
    return any(d in domain for d in RENDER_DOMAINS)

async def crawl_url(url: str) -> dict:
    """Crawl a single URL with ScraperAPI."""
    result = {
        "source_id": url_to_source_id(url),
        "url": url,
        "domain": get_domain(url),
        "fetch_date": datetime.now().isoformat(),
    }

    if not SCRAPER_API_KEY:
        result["fetch_status"] = "error: no api key"
        result["full_text"] = ""
        return result

    try:
        encoded_url = quote_plus(url)
        api_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_url}"

        # Use render=true for protected sites
        if needs_render(url):
            api_url += "&render=true"
            result["fetch_method"] = "scraperapi_render"
            print(f"    Using render=true for {get_domain(url)}")
        else:
            result["fetch_method"] = "scraperapi"

        async with httpx.AsyncClient(timeout=TIMEOUT + 60) as client:
            resp = await client.get(api_url)

            if resp.status_code != 200:
                result["fetch_status"] = f"http_{resp.status_code}"
                result["full_text"] = ""
                return result

            # Check for bot protection pages
            if "Making sure you're not a bot" in resp.text:
                result["fetch_status"] = "blocked_anubis"
                result["full_text"] = ""
                return result

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Remove scripts/styles
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()

            text = soup.get_text(separator='\n', strip=True)
            title = soup.title.string if soup.title else ""

            # Validate content
            if len(text) < 200:
                result["fetch_status"] = "minimal_content"
                result["full_text"] = text
                return result

            result["fetch_status"] = "success"
            result["full_text"] = text[:MAX_CONTENT_SIZE]
            result["page_title"] = title

    except httpx.TimeoutException:
        result["fetch_status"] = "timeout"
        result["full_text"] = ""
    except Exception as e:
        result["fetch_status"] = f"error: {str(e)[:50]}"
        result["full_text"] = ""

    return result

async def crawl_game(game_slug: str, max_workers: int = 8):
    """Crawl pending URLs for a game."""
    folder = GAMES_RESEARCH_DIR / game_slug
    urls_file = folder / "_urls.json"

    if not urls_file.exists():
        print(f"No URLs file for {game_slug}")
        return

    data = json.loads(urls_file.read_text())
    pending = data.get("pending", [])

    if not pending:
        print(f"No pending URLs for {game_slug}")
        return

    print(f"\nCrawling {len(pending)} URLs for {game_slug}")

    semaphore = asyncio.Semaphore(max_workers)
    crawled = data.get("crawled", {})
    stats = {"success": 0, "failed": 0, "render_used": 0}

    async def crawl_with_semaphore(url):
        async with semaphore:
            return await crawl_url(url)

    tasks = [crawl_with_semaphore(url) for url in pending]

    for i, coro in enumerate(asyncio.as_completed(tasks)):
        result = await coro

        if result.get("fetch_method") == "scraperapi_render":
            stats["render_used"] += 1

        if result["fetch_status"] == "success":
            stats["success"] += 1
            # Save file
            source_file = folder / f"{result['source_id']}.json"
            with open(source_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"  ✓ [{i+1}/{len(pending)}] {result['domain']}")
        else:
            stats["failed"] += 1
            print(f"  ✗ [{i+1}/{len(pending)}] {result['domain']}: {result['fetch_status']}")

        crawled[result["url"]] = result["fetch_status"]

    # Update URLs file
    data["crawled"] = crawled
    data["pending"] = []
    data["last_crawl"] = datetime.now().isoformat()

    with open(urls_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Done: {stats['success']} success, {stats['failed']} failed, {stats['render_used']} used render")
    return stats

async def main():
    if len(sys.argv) > 1:
        await crawl_game(sys.argv[1])
    else:
        # Crawl all games with pending URLs
        for folder in sorted(GAMES_RESEARCH_DIR.iterdir()):
            if not folder.is_dir():
                continue
            urls_file = folder / "_urls.json"
            if not urls_file.exists():
                continue
            data = json.loads(urls_file.read_text())
            if data.get("pending"):
                await crawl_game(folder.name)

if __name__ == "__main__":
    asyncio.run(main())
