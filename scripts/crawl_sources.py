#!/usr/bin/env python3
"""
Parallel Source Crawler for Sierra Games Archive

Crawls discovered URLs in parallel using domain-aware strategies.
Uses httpx for simple sites, Playwright for JS-heavy sites.

Input: research/{game-slug}/_urls.json
Output: research/{game-slug}/{source_id}.json per source
"""

import argparse
import asyncio
import hashlib
import json
import re
import os
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote_plus
import httpx

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("Warning: Playwright not installed. Some sites may not work.")

# ScraperAPI for Cloudflare bypass
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')

# Paths
SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"
DOMAINS_FILE = INTERNAL_DIR / "data" / "domains.json"

# Configuration
MAX_WORKERS = 16  # Max parallel crawls
MAX_CONTENT_SIZE = 50000  # Max chars to store
MIN_CONTENT_SIZE = 500  # Min chars to be valid
TIMEOUT = 30000  # 30 seconds

# Load domain intelligence
def load_domains():
    if DOMAINS_FILE.exists():
        with open(DOMAINS_FILE) as f:
            return json.load(f)
    return {"domains": {}}

DOMAIN_DB = load_domains()

def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""

def get_domain_method(domain: str) -> str:
    """Get crawl method for domain."""
    domain_info = DOMAIN_DB.get("domains", {}).get(domain, {})
    return domain_info.get("method", "scraperapi")

def url_to_source_id(url: str) -> str:
    """Convert URL to a source ID for filenames."""
    domain = get_domain(url)
    # Clean domain for filename
    clean_domain = domain.replace("www.", "").replace(".", "_")

    # Create short hash for uniqueness
    url_hash = hashlib.md5(url.encode()).hexdigest()[:6]

    return f"{clean_domain}_{url_hash}"

def validate_content(content: str, game_title: str, url: str, metadata: dict = None) -> tuple[bool, str]:
    """
    Validate that content is relevant and not an error page.
    Returns (is_valid, reason).

    Args:
        content: The page content
        game_title: The game title
        url: The source URL
        metadata: Optional dict with developer, publisher for context validation
    """
    if not content:
        return False, "empty"

    if len(content) < MIN_CONTENT_SIZE:
        return False, f"too_short ({len(content)} chars)"

    content_lower = content.lower()
    metadata = metadata or {}

    # Check for common error patterns
    error_patterns = [
        "access denied",
        "403 forbidden",
        "404 not found",
        "page not found",
        "this page doesn't exist",
        "we couldn't find",
        "error 404",
        "captcha",
        "please verify you are human",
        "enable javascript",
        "browser not supported",
        # Anti-bot protection pages
        "making sure you're not a bot",
        "proof-of-work",
        "anubis",
        "protect the server against",
        "aggressively scraping",
        "you must enable javascript to get past this",
        "checking your browser",
        "just a moment",
        "ray id",
        "cloudflare",
        "ddos protection",
        "security check",
    ]

    for pattern in error_patterns:
        if pattern in content_lower[:1000]:
            return False, f"error_page ({pattern})"

    # Check for developer/publisher context (helps with generic titles)
    has_dev_context = False
    if metadata.get("developer"):
        devs = metadata["developer"]
        if isinstance(devs, str):
            devs = [devs]
        for dev in devs:
            if dev and dev.lower() in content_lower:
                has_dev_context = True
                break
    if metadata.get("publisher"):
        pubs = metadata["publisher"]
        if isinstance(pubs, str):
            pubs = [pubs]
        for pub in pubs:
            if pub and pub.lower() in content_lower:
                has_dev_context = True
                break

    # Trusted gaming domains - still verify game title appears
    domain = get_domain(url)
    trusted_domains = {
        "en.wikipedia.org", "www.mobygames.com", "mobygames.com",
        "wiki.scummvm.org", "sciwiki.sierrahelp.com", "wiki.sierrahelp.com",
        "sierrahelp.com", "www.sierrachest.com", "sierrachest.com",
        "sierra.fandom.com", "www.gog.com", "gog.com",
        "www.pcgamingwiki.com", "pcgamingwiki.com", "tcrf.net",
        "www.adventuregamers.com", "adventuregamers.com",
        "tvtropes.org", "www.filfre.net", "grokipedia.com",
        "store.steampowered.com", "www.hardcoregaming101.net",
        "archive.org", "web.archive.org", "www.imdb.com",
        "www.behindthevoiceactors.com", "www.igdb.com", "rawg.io",
        "howlongtobeat.com", "www.speedrun.com", "classicreload.com",
        "www.myabandonware.com", "www.abandonwaredos.com",
        "gamesnostalgia.com", "www.old-games.com",
    }

    # For trusted domains, still verify game appears in content (but don't require gaming context)
    if domain in trusted_domains:
        # Common words to ignore
        common_words = {"the", "a", "an", "of", "at", "in", "to", "and", "or", "for", "by", "on"}
        game_words = [w.lower() for w in game_title.split() if w.lower() not in common_words]

        if game_words:
            # At least one significant word should appear
            matches = sum(1 for word in game_words if word in content_lower)
            if matches > 0:
                return True, "valid"
            # For trusted domains, also check if game title appears in page title
            page_title_lower = content_lower[:500]  # Title is usually at start
            if any(word in page_title_lower for word in game_words):
                return True, "valid"
            return False, "content_mismatch_trusted"
        return True, "valid"

    # Gaming context words - if content has these, it's likely about games
    gaming_context = [
        "video game", "computer game", "pc game", "dos game",
        "sierra", "sierra on-line", "sierra entertainment",
        "developer", "publisher", "gameplay", "walkthrough",
        "puzzle", "adventure game", "rpg", "role-playing",
        "impressions games", "dynamix", "release date", "platforms",
        "dos", "windows 95", "amiga", "atari st",
        "mobygames", "gog.com", "steam", "scummvm",
        "city-building", "simulation", "strategy game",
    ]
    has_gaming_context = any(ctx in content_lower for ctx in gaming_context)

    # Developer/publisher context is as good as gaming context
    if has_dev_context:
        has_gaming_context = True

    # Common words to ignore in title matching
    common_words = {"the", "a", "an", "of", "at", "in", "to", "and", "or", "for", "by", "on"}

    # Get significant words from game title
    game_words = [w.lower() for w in game_title.split() if w.lower() not in common_words]

    if not game_words:
        # Title is all common words (unlikely) - just check gaming context
        return has_gaming_context, "valid" if has_gaming_context else "no_gaming_context"

    # For single-word generic titles (like "Pharaoh"), require gaming context
    if len(game_words) == 1:
        word = game_words[0]
        if word in content_lower:
            # Word found - but is it about the game or something else?
            if has_gaming_context:
                return True, "valid"
            else:
                return False, "content_mismatch_no_game_context"
        # Word not found but developer/publisher mentioned - still valid
        if has_dev_context:
            return True, "valid_via_developer"
        return False, "content_mismatch"

    # For multi-word titles, at least one significant word should appear
    matches = sum(1 for word in game_words if word in content_lower)
    if matches == 0:
        # No title match but developer mentioned - allow it
        if has_dev_context:
            return True, "valid_via_developer"
        return False, "content_mismatch"

    # If we have matches but no gaming context, be more cautious
    if matches < len(game_words) / 2 and not has_gaming_context:
        return False, "content_mismatch_weak"

    return True, "valid"

async def crawl_with_httpx(url: str, timeout: int = TIMEOUT) -> tuple[str, str]:
    """Crawl URL using httpx (for simple sites)."""
    try:
        async with httpx.AsyncClient(timeout=timeout/1000, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })

            if resp.status_code != 200:
                return "", f"http_{resp.status_code}"

            # Parse HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Remove script/style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()

            # Get text content
            text = soup.get_text(separator='\n', strip=True)

            # Get title
            title = soup.title.string if soup.title else ""

            return text[:MAX_CONTENT_SIZE], f"success|{title}"

    except httpx.TimeoutException:
        return "", "timeout"
    except Exception as e:
        return "", f"error: {str(e)[:50]}"

async def crawl_with_playwright(browser, url: str, semaphore,
                                timeout: int = TIMEOUT) -> tuple[str, str]:
    """Crawl URL using Playwright (for JS-heavy sites)."""
    async with semaphore:
        try:
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            page = await context.new_page()

            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            await asyncio.sleep(1.5)  # Let JS render

            title = await page.title()
            content = await page.evaluate("() => document.body.innerText")

            await context.close()

            return content[:MAX_CONTENT_SIZE], f"success|{title}"

        except Exception as e:
            try:
                await context.close()
            except:
                pass
            return "", f"error: {str(e)[:50]}"


async def crawl_with_scraperapi(url: str, timeout: int = TIMEOUT, render: bool = False) -> tuple[str, str]:
    """
    Crawl URL using ScraperAPI (for Cloudflare-protected sites).

    ScraperAPI bypasses Cloudflare and other bot protection.
    Costs: 1 credit per request, 25 credits with render=true
    """
    if not SCRAPER_API_KEY:
        return "", "error: SCRAPER_API_KEY not set"

    try:
        # Build ScraperAPI URL
        encoded_url = quote_plus(url)
        api_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_url}"

        # Add render=true for JS-heavy sites (uses more credits but handles Cloudflare)
        if render:
            api_url += "&render=true"

        async with httpx.AsyncClient(timeout=timeout/1000 + 60) as client:  # Extra timeout for ScraperAPI
            resp = await client.get(api_url)

            if resp.status_code != 200:
                return "", f"scraperapi_http_{resp.status_code}"

            # Parse HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Remove script/style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()

            # Get text content
            text = soup.get_text(separator='\n', strip=True)

            # Get title
            title = soup.title.string if soup.title else ""

            return text[:MAX_CONTENT_SIZE], f"success|{title}"

    except httpx.TimeoutException:
        return "", "scraperapi_timeout"
    except Exception as e:
        return "", f"scraperapi_error: {str(e)[:50]}"

async def crawl_url(url: str, game_title: str, browser, semaphore, metadata: dict = None) -> dict:
    """
    Crawl a single URL and return result.

    Args:
        url: URL to crawl
        game_title: Game title for validation
        browser: Playwright browser instance
        semaphore: Concurrency semaphore
        metadata: Optional dict with developer, publisher for validation
    """
    domain = get_domain(url)
    method = get_domain_method(domain)
    source_id = url_to_source_id(url)

    result = {
        "source_id": source_id,
        "url": url,
        "domain": domain,
        "fetch_date": datetime.now().isoformat(),
        "fetch_method": "scraperapi",  # Always ScraperAPI
    }

    if method == "skip":
        result["fetch_status"] = "skipped"
        result["full_text"] = ""
        return result

    # ALWAYS use ScraperAPI for best success rate (ignore domain config)
    content, status = await crawl_with_scraperapi(url)

    # Parse status
    if status.startswith("success|"):
        result["page_title"] = status.split("|", 1)[1]
        result["full_text"] = content

        # Validate content (with developer/publisher context)
        is_valid, reason = validate_content(content, game_title, url, metadata)
        if is_valid:
            result["fetch_status"] = "success"
        else:
            result["fetch_status"] = f"invalid: {reason}"
    else:
        result["fetch_status"] = status
        result["full_text"] = ""
        result["page_title"] = ""

    return result

def load_game_metadata(game_title: str) -> dict:
    """Load developer/publisher metadata from game file."""
    import yaml
    GAMES_DIR = INTERNAL_DIR.parent / "Games"

    metadata = {"developer": None, "publisher": None}

    # Slugify for matching
    slug = game_title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)

    for game_file in GAMES_DIR.rglob("*.md"):
        if game_title.lower() in game_file.stem.lower():
            try:
                content = game_file.read_text()
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end > 0:
                        data = yaml.safe_load(content[3:end])
                        if data:
                            metadata["developer"] = data.get("developer")
                            metadata["publisher"] = data.get("publisher")
                            return metadata
            except:
                pass
    return metadata


async def crawl_game(game_slug: str, game_title: str = None,
                    max_workers: int = MAX_WORKERS,
                    force: bool = False) -> dict:
    """
    Crawl all pending URLs for a game.
    """
    # Load URLs
    urls_file = GAMES_RESEARCH_DIR / game_slug / "_urls.json"
    if not urls_file.exists():
        print(f"Error: No URLs discovered for {game_slug}")
        print(f"Run: python3 discover_urls.py \"{game_title or game_slug}\"")
        return {"error": "no_urls"}

    with open(urls_file) as f:
        urls_data = json.load(f)

    game_title = game_title or urls_data.get("game_title", game_slug)

    # Load developer/publisher metadata for validation
    metadata = load_game_metadata(game_title)
    if metadata.get("developer"):
        print(f"  Using developer context: {metadata['developer']}")

    pending_raw = urls_data.get("pending", [])
    crawled = urls_data.get("crawled", {})

    # Normalize pending URLs (could be strings or dicts with 'url' key)
    pending = []
    for item in pending_raw:
        if isinstance(item, dict):
            url = item.get("url", "")
        else:
            url = str(item)
        if url and (force or url not in crawled):
            pending.append(url)

    if not pending:
        print(f"No pending URLs to crawl for {game_title}")
        return {"crawled": 0, "success": 0, "failed": 0}

    print(f"\nCrawling {len(pending)} URLs for: {game_title}")
    print(f"Workers: {max_workers}")
    print("=" * 50)

    # Setup
    folder = GAMES_RESEARCH_DIR / game_slug
    semaphore = asyncio.Semaphore(max_workers)
    results = {"crawled": 0, "success": 0, "failed": 0, "skipped": 0}

    # All URLs go through ScraperAPI for best success rate
    scraperapi_urls = []
    for url in pending:
        domain = get_domain(url)
        method = get_domain_method(domain)
        if method == "skip":
            crawled[url] = "skipped"
            results["skipped"] += 1
        else:
            scraperapi_urls.append(url)

    print(f"  ScraperAPI: {len(scraperapi_urls)}")
    print(f"  Skipped: {results['skipped']}")
    print()

    # Crawl all URLs with ScraperAPI
    if scraperapi_urls and SCRAPER_API_KEY:
        print(f"Crawling with ScraperAPI ({max_workers} concurrent)...")
        scraper_semaphore = asyncio.Semaphore(max_workers)

        async def crawl_scraperapi_url(url):
            async with scraper_semaphore:
                return await crawl_url(url, game_title, None, semaphore, metadata)

        scraper_tasks = [crawl_scraperapi_url(url) for url in scraperapi_urls]

        for i, coro in enumerate(asyncio.as_completed(scraper_tasks)):
            result = await coro
            results["crawled"] += 1

            status = result["fetch_status"]
            url = result["url"]

            if status == "success":
                results["success"] += 1
                # Save content
                source_file = folder / f"{result['source_id']}.json"
                with open(source_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"  ✓ [{results['crawled']}/{len(pending)}] {result['domain']}")
            else:
                results["failed"] += 1
                print(f"  ✗ [{results['crawled']}/{len(pending)}] {result['domain']}: {status}")

            crawled[url] = status

    # Update URLs file with crawl status
    urls_data["crawled"] = crawled
    urls_data["pending"] = [u for u in urls_data.get("pending", []) if u not in crawled]
    urls_data["last_crawl"] = datetime.now().isoformat()

    with open(urls_file, 'w') as f:
        json.dump(urls_data, f, indent=2)

    # Print summary
    print("\n" + "=" * 50)
    print(f"CRAWL COMPLETE: {game_title}")
    print(f"  Success: {results['success']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Total files: {len(list(folder.glob('*.json'))) - 1}")  # -1 for _urls.json

    return results

async def crawl_batch(game_slugs: list[str], max_workers: int = MAX_WORKERS):
    """Crawl multiple games."""
    for slug in game_slugs:
        await crawl_game(slug, max_workers=max_workers)
        print()

def main():
    parser = argparse.ArgumentParser(description="Crawl discovered URLs")
    parser.add_argument("game", nargs="?", help="Game title or slug")
    parser.add_argument("--workers", "-w", type=int, default=MAX_WORKERS,
                       help=f"Max parallel workers (default: {MAX_WORKERS})")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Re-crawl already crawled URLs")
    parser.add_argument("--batch", type=Path,
                       help="File with list of game slugs")
    parser.add_argument("--status", action="store_true",
                       help="Show crawl status for all games")

    args = parser.parse_args()

    if args.status:
        # Show status for all games
        print("Crawl Status")
        print("=" * 60)
        for folder in sorted(RESEARCH_DIR.iterdir()):
            if not folder.is_dir():
                continue
            urls_file = folder / "_urls.json"
            if urls_file.exists():
                with open(urls_file) as f:
                    data = json.load(f)
                discovered = data.get("total_discovered", 0)
                crawled = len(data.get("crawled", {}))
                pending = len(data.get("pending", []))
                success = sum(1 for s in data.get("crawled", {}).values()
                             if s == "success")
                files = len(list(folder.glob("*.json"))) - 1

                print(f"{folder.name:35} D:{discovered:3} C:{crawled:3} "
                      f"S:{success:3} P:{pending:3} F:{files:3}")
        return

    if args.batch:
        # Batch mode
        if not args.batch.exists():
            print(f"Error: Batch file not found: {args.batch}")
            return
        with open(args.batch) as f:
            slugs = [line.strip() for line in f if line.strip()]
        asyncio.run(crawl_batch(slugs, args.workers))
        return

    if not args.game:
        parser.print_help()
        return

    # Single game
    from discover_urls import slugify
    game_slug = slugify(args.game)

    asyncio.run(crawl_game(game_slug, args.game, args.workers, args.force))

if __name__ == "__main__":
    main()
