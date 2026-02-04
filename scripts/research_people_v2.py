#!/usr/bin/env python3
"""
Enhanced research gathering for designers and developers.
Target: 15+ quality sources per person.
"""

import os
import re
import json
import time
import hashlib
from pathlib import Path
from urllib.parse import quote_plus, quote

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

RESEARCH_DIR = Path("research/people")
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')
KAGI_API_KEY = os.environ.get('KAGI_API_KEY', '')


def slug_from_name(name: str) -> str:
    """Generate URL-safe slug from name."""
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug)
    return re.sub(r'-+', '-', slug).strip('-')


def extract_text_from_html(html: str) -> str:
    """Extract clean text from HTML using BeautifulSoup."""
    if not HAS_BS4:
        # Fallback: strip HTML tags with regex
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    soup = BeautifulSoup(html, 'html.parser')

    # Remove script/style elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'noscript']):
        element.decompose()

    # Get text
    text = soup.get_text(separator='\n')

    # Clean up whitespace
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and len(line) > 2:
            lines.append(line)

    return '\n'.join(lines)


def fetch_via_scraper(url: str, render: bool = False) -> tuple[str, int]:
    """Fetch URL via ScraperAPI."""
    if not SCRAPER_API_KEY:
        return "", 0

    params = f"api_key={SCRAPER_API_KEY}&url={quote_plus(url)}"
    if render:
        params += "&render=true"

    try:
        resp = httpx.get(f"http://api.scraperapi.com?{params}", timeout=60)
        return resp.text, resp.status_code
    except Exception as e:
        print(f"    Error: {e}")
        return "", 0


def search_kagi(query: str) -> list[dict]:
    """Search Kagi FastGPT."""
    if not KAGI_API_KEY:
        return []

    try:
        resp = httpx.post(
            "https://kagi.com/api/v0/fastgpt",
            headers={"Authorization": f"Bot {KAGI_API_KEY}"},
            json={"query": query},
            timeout=60
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for ref in data.get("data", {}).get("references", []):
                if ref.get("url"):
                    results.append({
                        "url": ref["url"],
                        "title": ref.get("title", ""),
                        "snippet": ref.get("snippet", "")
                    })
            return results
    except Exception as e:
        print(f"    Kagi error: {e}")
    return []


def save_source(output_dir: Path, source_id: str, url: str, content: str, url_hash: str = None) -> bool:
    """Save a source file if content is valid. Extracts text from HTML."""
    if not content or len(content) < 500:
        return False

    # Extract text from HTML
    text = extract_text_from_html(content)

    # Check if we have meaningful content after extraction
    if not text or len(text) < 200:
        return False

    # Check for error pages
    error_indicators = ['page not found', 'error 404', 'access denied', 'page you requested could not be found']
    if any(err in text.lower()[:500] for err in error_indicators):
        return False

    if url_hash:
        filename = f"{source_id}_{url_hash}.json"
    else:
        filename = f"{source_id}.json"

    filepath = output_dir / filename
    if filepath.exists():
        return False

    with open(filepath, 'w') as f:
        json.dump({
            "source_id": source_id,
            "url": url,
            "fetch_date": time.strftime("%Y-%m-%d"),
            "fetch_status": "success",
            "full_text": text[:50000]
        }, f, indent=2)
    return True


def research_designer(name: str, output_dir: Path) -> int:
    """Comprehensive research for a game designer."""
    output_dir.mkdir(parents=True, exist_ok=True)
    query = quote_plus(name)
    wiki_name = name.replace(' ', '_')
    files_created = 0

    print(f"  Researching designer: {name}")

    # 1. Multiple Kagi searches with different queries
    kagi_queries = [
        f"{name} Sierra game designer",
        f"{name} video game designer interview",
        f"{name} game developer biography",
        f'"{name}" adventure games history',
    ]

    all_kagi_urls = set()
    for q in kagi_queries:
        results = search_kagi(q)
        for ref in results:
            all_kagi_urls.add(ref["url"])
        time.sleep(0.5)

    # Save Kagi results
    if all_kagi_urls:
        kagi_file = output_dir / "kagi_fastgpt.json"
        if not kagi_file.exists():
            with open(kagi_file, 'w') as f:
                json.dump({
                    "source": "kagi_fastgpt",
                    "queries": kagi_queries,
                    "urls": list(all_kagi_urls),
                    "fetch_date": time.strftime("%Y-%m-%d")
                }, f, indent=2)
            files_created += 1
        print(f"    Kagi: {len(all_kagi_urls)} unique URLs")

    # 2. Core sources - always fetch
    core_sources = [
        ("wikipedia", f"https://en.wikipedia.org/wiki/{wiki_name}", False),
        ("mobygames", f"https://www.mobygames.com/person/{query.lower().replace('+', '-')}/", True),
        ("sierragamers", f"https://www.sierragamers.com/{name.lower().replace(' ', '-')}/", True),
        ("giantbomb", f"https://www.giantbomb.com/search/?q={query}&filter=person", True),
        ("imdb", f"https://www.imdb.com/find/?q={query}&s=nm", True),
    ]

    for source_id, url, render in core_sources:
        if list(output_dir.glob(f"{source_id}*.json")):
            continue
        print(f"    Fetching {source_id}...")
        content, status = fetch_via_scraper(url, render=render)
        if save_source(output_dir, source_id, url, content):
            files_created += 1
        time.sleep(1)

    # 3. Interview/article sources
    interview_sources = [
        ("adventuregamers", f"https://adventuregamers.com/search?query={query}", True),
        ("gamedeveloper", f"https://www.gamedeveloper.com/search?q={query}", True),
        ("polygon", f"https://www.polygon.com/search?q={query}", True),
        ("kotaku", f"https://kotaku.com/search?q={query}", True),
        ("ign", f"https://www.ign.com/search?q={query}", True),
        ("gamespot", f"https://www.gamespot.com/search/?q={query}", True),
    ]

    for source_id, url, render in interview_sources:
        if list(output_dir.glob(f"{source_id}*.json")):
            continue
        print(f"    Fetching {source_id}...")
        content, status = fetch_via_scraper(url, render=render)
        if save_source(output_dir, source_id, url, content):
            files_created += 1
        time.sleep(1)

    # 4. Archive/history sources
    archive_sources = [
        ("filfre", f"https://www.filfre.net/?s={query}", True),
        ("hardcoregaming101", f"https://www.hardcoregaming101.net/?s={query}", True),
        ("archive_org", f"https://archive.org/search?query={query}", False),
    ]

    for source_id, url, render in archive_sources:
        if list(output_dir.glob(f"{source_id}*.json")):
            continue
        print(f"    Fetching {source_id}...")
        content, status = fetch_via_scraper(url, render=render)
        if save_source(output_dir, source_id, url, content):
            files_created += 1
        time.sleep(1)

    # 5. Fetch all unique Kagi URLs (up to 10)
    fetched_domains = set()
    for url in list(all_kagi_urls)[:15]:
        # Skip already-fetched sources
        if any(s in url for s in ['mobygames', 'wikipedia', 'sierragamers', 'giantbomb', 'imdb']):
            continue

        domain_match = re.search(r'https?://([^/]+)', url)
        if not domain_match:
            continue
        domain = domain_match.group(1)

        # Skip if we already have this domain
        if domain in fetched_domains:
            continue
        fetched_domains.add(domain)

        domain_slug = domain.replace('.', '_').replace('www_', '')
        if list(output_dir.glob(f"{domain_slug}*.json")):
            continue

        print(f"    Fetching {domain_slug}...")
        content, status = fetch_via_scraper(url, render=True)
        if status == 200 and len(content) > 500:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
            if save_source(output_dir, domain_slug, url, content, url_hash):
                files_created += 1
        time.sleep(1)

    return files_created


def research_developer(name: str, output_dir: Path) -> int:
    """Comprehensive research for a game development company."""
    output_dir.mkdir(parents=True, exist_ok=True)
    query = quote_plus(name)
    wiki_name = name.replace(' ', '_')
    files_created = 0

    print(f"  Researching developer: {name}")

    # 1. Multiple Kagi searches
    kagi_queries = [
        f"{name} game developer company",
        f"{name} video game studio history",
        f'"{name}" Sierra entertainment',
        f"{name} games developed",
    ]

    all_kagi_urls = set()
    for q in kagi_queries:
        results = search_kagi(q)
        for ref in results:
            all_kagi_urls.add(ref["url"])
        time.sleep(0.5)

    if all_kagi_urls:
        kagi_file = output_dir / "kagi_fastgpt.json"
        if not kagi_file.exists():
            with open(kagi_file, 'w') as f:
                json.dump({
                    "source": "kagi_fastgpt",
                    "queries": kagi_queries,
                    "urls": list(all_kagi_urls),
                    "fetch_date": time.strftime("%Y-%m-%d")
                }, f, indent=2)
            files_created += 1
        print(f"    Kagi: {len(all_kagi_urls)} unique URLs")

    # 2. Core sources
    core_sources = [
        ("wikipedia", f"https://en.wikipedia.org/wiki/{wiki_name}", False),
        ("mobygames", f"https://www.mobygames.com/company/{query.lower().replace('+', '-')}/", True),
        ("giantbomb", f"https://www.giantbomb.com/search/?q={query}&filter=company", True),
        ("igdb", f"https://www.igdb.com/search?q={query}&type=company", True),
    ]

    for source_id, url, render in core_sources:
        if list(output_dir.glob(f"{source_id}*.json")):
            continue
        print(f"    Fetching {source_id}...")
        content, status = fetch_via_scraper(url, render=render)
        if save_source(output_dir, source_id, url, content):
            files_created += 1
        time.sleep(1)

    # 3. History/archive sources
    history_sources = [
        ("filfre", f"https://www.filfre.net/?s={query}", True),
        ("hardcoregaming101", f"https://www.hardcoregaming101.net/?s={query}", True),
        ("archive_org", f"https://archive.org/search?query={query}", False),
        ("gamehistory", f"https://gamehistory.org/search?q={query}", True),
    ]

    for source_id, url, render in history_sources:
        if list(output_dir.glob(f"{source_id}*.json")):
            continue
        print(f"    Fetching {source_id}...")
        content, status = fetch_via_scraper(url, render=render)
        if save_source(output_dir, source_id, url, content):
            files_created += 1
        time.sleep(1)

    # 4. Fetch unique Kagi URLs
    fetched_domains = set()
    for url in list(all_kagi_urls)[:15]:
        if any(s in url for s in ['mobygames', 'wikipedia', 'giantbomb', 'igdb']):
            continue

        domain_match = re.search(r'https?://([^/]+)', url)
        if not domain_match:
            continue
        domain = domain_match.group(1)

        if domain in fetched_domains:
            continue
        fetched_domains.add(domain)

        domain_slug = domain.replace('.', '_').replace('www_', '')
        if list(output_dir.glob(f"{domain_slug}*.json")):
            continue

        print(f"    Fetching {domain_slug}...")
        content, status = fetch_via_scraper(url, render=True)
        if status == 200 and len(content) > 500:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
            if save_source(output_dir, domain_slug, url, content, url_hash):
                files_created += 1
        time.sleep(1)

    return files_created


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enhanced research for designers/developers (15+ sources)")
    parser.add_argument('--designer', help='Single designer name')
    parser.add_argument('--developer', help='Single developer name')
    parser.add_argument('--all-designers', action='store_true', help='Research all designers')
    parser.add_argument('--all-developers', action='store_true', help='Research all developers')
    parser.add_argument('--force', action='store_true', help='Re-fetch even if files exist')
    args = parser.parse_args()

    if not HAS_HTTPX:
        print("ERROR: httpx required. Run: pip install httpx")
        return

    if not HAS_BS4:
        print("WARNING: BeautifulSoup not found. Install with: pip install beautifulsoup4")
        print("Using regex fallback for HTML parsing (less accurate)")

    if not SCRAPER_API_KEY:
        print("ERROR: SCRAPER_API_KEY not set")
        return

    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    designers = [
        "Roberta Williams", "Al Lowe", "Mark Crowe", "Jeff Tunnell",
        "Damon Slye", "Ken Williams", "Scott Murphy", "Jane Jensen",
        "Corey Cole", "Lori Ann Cole", "Jim Walls", "Josh Mandel",
        "Lorelei Shannon", "Chris Beatrice", "Warren Schwader"
    ]

    developers = [
        "Sierra On-Line", "Dynamix", "Impressions Games", "Coktel Vision",
        "Berkeley Systems", "Papyrus Design Group", "Bright Star Technology",
        "Knowledge Adventure", "Headgate Studios", "Game Arts", "AGD Interactive"
    ]

    total_files = 0

    if args.designer:
        slug = slug_from_name(args.designer)
        output_dir = RESEARCH_DIR / "designers" / slug
        if args.force:
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)
        files = research_designer(args.designer, output_dir)
        total_files += files
        print(f"  Created {files} files for {args.designer}")

        # Show file count
        file_count = len(list(output_dir.glob("*.json")))
        status = "PASS" if file_count >= 15 else "NEEDS MORE"
        print(f"  Total files: {file_count} [{status}]")

    elif args.developer:
        slug = slug_from_name(args.developer)
        output_dir = RESEARCH_DIR / "developers" / slug
        if args.force:
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)
        files = research_developer(args.developer, output_dir)
        total_files += files
        print(f"  Created {files} files for {args.developer}")

        file_count = len(list(output_dir.glob("*.json")))
        status = "PASS" if file_count >= 15 else "NEEDS MORE"
        print(f"  Total files: {file_count} [{status}]")

    elif args.all_designers:
        for name in designers:
            slug = slug_from_name(name)
            output_dir = RESEARCH_DIR / "designers" / slug
            files = research_designer(name, output_dir)
            total_files += files

            file_count = len(list(output_dir.glob("*.json")))
            status = "PASS" if file_count >= 15 else "NEEDS MORE"
            print(f"  {name}: {file_count} files [{status}]")
            print()

    elif args.all_developers:
        for name in developers:
            slug = slug_from_name(name)
            output_dir = RESEARCH_DIR / "developers" / slug
            files = research_developer(name, output_dir)
            total_files += files

            file_count = len(list(output_dir.glob("*.json")))
            status = "PASS" if file_count >= 15 else "NEEDS MORE"
            print(f"  {name}: {file_count} files [{status}]")
            print()

    else:
        parser.print_help()
        return

    print(f"\nTotal new files created: {total_files}")


if __name__ == '__main__':
    main()
