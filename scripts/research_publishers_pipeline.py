#!/usr/bin/env python3
"""
Publisher Research Pipeline

Gathers verified research from multiple sources for game publishers:
1. MobyGames company page (scraped via ScraperAPI)
2. Wikipedia
3. Brave Search for articles/history
4. Kagi FastGPT for sourced facts
5. Additional crawling of discovered URLs

Usage:
  python research_publishers_pipeline.py --publisher "Activision"
  python research_publishers_pipeline.py --all
  python research_publishers_pipeline.py --list publishers.txt
"""

import os
import re
import json
import time
import hashlib
from pathlib import Path
from urllib.parse import quote_plus, quote, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

try:
    import httpx
except ImportError:
    print("ERROR: httpx required. Run: pip install httpx")
    exit(1)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("WARNING: beautifulsoup4 not found, using regex HTML parsing")

# Load environment
def load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.replace('export ', '').strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value

load_env()

# API Keys
BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY', '')
KAGI_API_KEY = os.environ.get('KAGI_API_KEY', '')
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')
MOBYGAMES_API_KEY = os.environ.get('MOBYGAMES_API_KEY', '')

# Paths
RESEARCH_DIR = Path(__file__).parent / "research" / "publishers"
VAULT_DIR = Path(__file__).parent.parent
GAMES_DIR = VAULT_DIR / "Games"

# Rate limiting
BRAVE_DELAY = 0.5
KAGI_DELAY = 1.0
SCRAPER_DELAY = 0.3
MOBYGAMES_API_DELAY = 1.5

# Publishers with 2+ games to research (non-Sierra)
ALL_PUBLISHERS = [
    # Major external publishers
    "Encore Software",
    "Activision",
    "Electronic Arts",
    "Virgin Games",
    "Brøderbund Software",
    "Disney",
    # Sierra sublabels/partners
    "Tomahawk",
    # Fan/indie publishers
    "AGD Interactive",
    "Infamous Quests",
    "Infamous Adventures",
    "Himalaya Studios",
    "Transolar Games",
    "Schnibble Productions",
    "Replay Games",
    "Gearbox Publishing",
]


def slugify(name: str) -> str:
    """Convert name to URL-safe slug."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return re.sub(r'-+', '-', slug).strip('-')


def extract_text_from_html(html: str) -> str:
    """Extract clean text from HTML."""
    if HAS_BS4:
        soup = BeautifulSoup(html, 'html.parser')
        for elem in soup(['script', 'style', 'nav', 'header', 'footer', 'noscript']):
            elem.decompose()
        text = soup.get_text(separator='\n')
    else:
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)

    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2]
    return '\n'.join(lines)


def scraper_fetch(url: str, render: bool = False, timeout: int = 60) -> tuple[str, int]:
    """Fetch URL via ScraperAPI."""
    if not SCRAPER_API_KEY:
        return "", 0

    params = f"api_key={SCRAPER_API_KEY}&url={quote_plus(url)}"
    if render:
        params += "&render=true"

    try:
        resp = httpx.get(f"http://api.scraperapi.com?{params}", timeout=timeout)
        return resp.text, resp.status_code
    except Exception as e:
        print(f"    ScraperAPI error: {e}")
        return "", 0


def brave_search(query: str, count: int = 10) -> list[dict]:
    """Search via Brave Search API."""
    if not BRAVE_API_KEY:
        return []

    try:
        resp = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": BRAVE_API_KEY},
            params={"q": query, "count": count},
            timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "description": item.get("description", "")
                })
            return results
        elif resp.status_code == 402:
            print("    Brave API quota exceeded")
    except Exception as e:
        print(f"    Brave error: {e}")
    return []


def kagi_fastgpt(query: str) -> dict:
    """Query Kagi FastGPT for sourced answers."""
    if not KAGI_API_KEY:
        return {}

    try:
        resp = httpx.post(
            "https://kagi.com/api/v0/fastgpt",
            headers={"Authorization": f"Bot {KAGI_API_KEY}"},
            json={"query": query},
            timeout=60
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"    Kagi error: {e}")
    return {}


def save_source(output_dir: Path, source_id: str, url: str, content: str,
                extra_data: dict = None) -> bool:
    """Save a source file if content is valid."""
    if not content or len(content) < 300:
        return False

    text = extract_text_from_html(content) if '<' in content else content

    if not text or len(text) < 200:
        return False

    # Check for error pages
    error_indicators = ['page not found', 'error 404', 'access denied',
                       'could not be found', 'no results', 'search results']
    if any(err in text.lower()[:500] for err in error_indicators):
        return False

    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    filename = f"{source_id}_{url_hash}.json"
    filepath = output_dir / filename

    if filepath.exists():
        return False

    data = {
        "source_id": source_id,
        "url": url,
        "fetch_date": datetime.now().strftime("%Y-%m-%d"),
        "fetch_status": "success",
        "full_text": text[:50000]
    }

    if extra_data:
        data.update(extra_data)

    filepath.write_text(json.dumps(data, indent=2))
    return True


def get_vault_games_for_publisher(name: str) -> list[dict]:
    """Find all games in vault published by this company."""
    games = []
    name_lower = name.lower()

    # Also check for variations
    variations = [name_lower]
    if name_lower.endswith(', inc.'):
        variations.append(name_lower.replace(', inc.', ''))
    if not name_lower.endswith(', inc.'):
        variations.append(name_lower + ', inc.')
    # Handle common variations
    if 'broderbund' in name_lower:
        variations.extend(['broderbund', 'brøderbund', 'broderbund software'])

    for md_file in GAMES_DIR.rglob("*.md"):
        try:
            content = md_file.read_text()
            # Check publisher field in YAML
            pub_match = re.search(r'^publisher:\s*["\']?([^"\'\n]+)', content, re.MULTILINE)
            if pub_match:
                pub = pub_match.group(1).lower().strip()
                if any(v in pub for v in variations):
                    filename = md_file.stem
                    year = filename[:4] if filename[:4].isdigit() else "Unknown"
                    title = filename[7:] if filename[:4].isdigit() else filename
                    games.append({
                        "title": title.replace(' - ', ': '),
                        "year": year,
                        "path": str(md_file.relative_to(VAULT_DIR)),
                        "filename": md_file.name
                    })
        except:
            pass

    return sorted(games, key=lambda x: (x.get("year", "0000"), x.get("title", "")))


def research_mobygames(name: str, output_dir: Path) -> int:
    """Scrape MobyGames company page."""
    files_created = 0

    # Use Brave search to find the correct MobyGames company URL
    print(f"    Finding MobyGames URL via Brave...")
    results = brave_search(f'"{name}" site:mobygames.com/company', count=5)

    mobygames_url = None
    for r in results:
        url = r.get("url", "")
        if "/company/" in url:
            mobygames_url = url
            if not mobygames_url.endswith('/'):
                mobygames_url += '/'
            break

    time.sleep(BRAVE_DELAY)

    if mobygames_url:
        print(f"    Fetching MobyGames: {mobygames_url}")
        content, status = scraper_fetch(mobygames_url, render=True)

        if status == 200 and len(content) > 1000:
            if save_source(output_dir, "mobygames_company", mobygames_url, content):
                files_created += 1
        time.sleep(SCRAPER_DELAY)
    else:
        print(f"    No MobyGames company URL found for {name}")

    return files_created


def research_wikipedia(name: str, output_dir: Path) -> int:
    """Fetch Wikipedia page if exists."""
    wiki_names = [
        name.replace(' ', '_'),
        name.replace(' ', '_') + '_(company)',
        name.replace(' ', '_') + '_(video_game_company)',
        name.replace(' ', '_') + '_(video_game_publisher)',
    ]

    files_created = 0
    for wiki_name in wiki_names:
        url = f"https://en.wikipedia.org/wiki/{wiki_name}"
        print(f"    Trying Wikipedia: {url}")
        content, status = scraper_fetch(url, render=False)

        if status == 200 and len(content) > 1000 and 'does not have an article' not in content.lower():
            if save_source(output_dir, "wikipedia", url, content):
                files_created += 1
                break
        time.sleep(SCRAPER_DELAY)

    return files_created


def research_brave_search(name: str, output_dir: Path) -> tuple[int, list[str]]:
    """Run comprehensive Brave searches for publisher info."""
    files_created = 0
    discovered_urls = []

    # Publisher-specific queries
    queries = [
        f'"{name}" video game publisher history',
        f'"{name}" game publisher founded',
        f'"{name}" Sierra games published',
        f'"{name}" game company acquisition',
        f'"{name}" video game publisher catalog',
        f'"{name}" publisher interview',
        f'"{name}" retrospective gaming',
        f'"{name}" game publisher closure OR shutdown',
        f'"{name}" notable games published',
        f'"{name}" game publisher founders',
    ]

    for query in queries:
        print(f"    Brave search: {query[:60]}...")
        results = brave_search(query, count=10)

        for result in results:
            url = result.get("url", "")
            if url and url not in discovered_urls:
                discovered_urls.append(url)

        time.sleep(BRAVE_DELAY)

    # Save search results
    if discovered_urls:
        search_file = output_dir / "brave_search_results.json"
        if not search_file.exists():
            search_file.write_text(json.dumps({
                "source": "brave_search",
                "queries": queries,
                "urls": discovered_urls,
                "fetch_date": datetime.now().strftime("%Y-%m-%d")
            }, indent=2))
            files_created += 1

    return files_created, discovered_urls


def research_kagi(name: str, output_dir: Path) -> tuple[int, list[str]]:
    """Query Kagi FastGPT for sourced publisher facts."""
    files_created = 0
    discovered_urls = []

    queries = [
        f"What video games did {name} publish? List each game with year.",
        f"Tell me the history of {name} as a game publisher.",
        f"When was {name} founded and by whom?",
        f"What happened to {name}? Are they still operating?",
        f"What is {name} best known for in gaming?",
        f"Was {name} acquired or did they acquire other companies?",
        f"What developers did {name} work with?",
    ]

    all_responses = []
    all_references = []

    for query in queries:
        print(f"    Kagi query: {query[:60]}...")
        result = kagi_fastgpt(query)

        if result:
            data = result.get("data", {})
            output = data.get("output", "")
            refs = data.get("references", [])

            if output:
                all_responses.append({"query": query, "response": output})

            for ref in refs:
                url = ref.get("url", "")
                if url and url not in discovered_urls:
                    discovered_urls.append(url)
                    all_references.append(ref)

        time.sleep(KAGI_DELAY)

    # Save Kagi results
    if all_responses or all_references:
        kagi_file = output_dir / "kagi_fastgpt.json"
        if not kagi_file.exists():
            kagi_file.write_text(json.dumps({
                "source": "kagi_fastgpt",
                "queries": queries,
                "responses": all_responses,
                "references": all_references,
                "fetch_date": datetime.now().strftime("%Y-%m-%d")
            }, indent=2))
            files_created += 1

    return files_created, discovered_urls


def crawl_discovered_urls(urls: list[str], output_dir: Path, max_urls: int = 30) -> int:
    """Crawl discovered URLs via ScraperAPI."""
    files_created = 0
    seen_domains = {}

    # Priority domains for gaming company info
    priority_domains = [
        'gamedeveloper.com', 'filfre.net', 'hardcoregaming101.net',
        'rockpapershotgun.com', 'polygon.com', 'kotaku.com', 'ign.com',
        'gamespot.com', 'giantbomb.com', 'pcgamer.com', 'eurogamer.net',
        'sierragamers.com', 'sierrahelp.com', 'adventuregamers.com',
        'venturebeat.com', 'gamesindustry.biz', 'gamasutra.com'
    ]

    def url_priority(url):
        domain = urlparse(url).netloc.replace('www.', '')
        if domain in priority_domains:
            return priority_domains.index(domain)
        return 100

    sorted_urls = sorted(urls, key=url_priority)

    for url in sorted_urls[:max_urls]:
        if any(s in url for s in ['mobygames.com', 'wikipedia.org', 'kagi.com']):
            continue

        domain = urlparse(url).netloc.replace('www.', '')
        domain_key = domain.split('.')[-2] if '.' in domain else domain
        if seen_domains.get(domain_key, 0) >= 2:
            continue
        seen_domains[domain_key] = seen_domains.get(domain_key, 0) + 1

        domain_slug = domain.replace('.', '_')

        print(f"    Crawling: {domain}")
        content, status = scraper_fetch(url, render=True)

        if status == 200 and save_source(output_dir, domain_slug, url, content):
            files_created += 1

        time.sleep(SCRAPER_DELAY)

    return files_created


def research_additional_sources(name: str, output_dir: Path) -> int:
    """Fetch additional publisher sources."""
    files_created = 0
    query = quote_plus(name)

    additional_sources = [
        ("giantbomb", f"https://www.giantbomb.com/search/?q={query}&filter=company", True),
        ("igdb", f"https://www.igdb.com/search?q={query}&type=company", True),
        ("sierragamers", f"https://www.sierragamers.com/?s={query}", True),
        ("gamesindustry", f"https://www.gamesindustry.biz/search?q={query}", True),
        ("filfre", f"https://www.filfre.net/?s={query}", True),
    ]

    for source_id, url, render in additional_sources:
        if list(output_dir.glob(f"{source_id}*.json")):
            continue

        print(f"    Fetching {source_id}...")
        content, status = scraper_fetch(url, render=render)

        if status == 200 and save_source(output_dir, source_id, url, content):
            files_created += 1

        time.sleep(SCRAPER_DELAY)

    return files_created


def research_publisher(name: str, force: bool = False) -> dict:
    """Run complete research pipeline for a single publisher."""
    slug = slugify(name)
    output_dir = RESEARCH_DIR / slug

    if force and output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Researching Publisher: {name}")
    print(f"Output: {output_dir}")
    print('='*60)

    total_files = 0
    discovered_urls = []

    # 1. Get vault games for this publisher
    vault_games = get_vault_games_for_publisher(name)
    print(f"  Found {len(vault_games)} vault games")

    # Save vault games list
    games_file = output_dir / "_vault_games.json"
    games_file.write_text(json.dumps(vault_games, indent=2))

    # 2. MobyGames (scrape)
    print("  Phase 1: MobyGames...")
    total_files += research_mobygames(name, output_dir)

    # 3. Wikipedia
    print("  Phase 2: Wikipedia...")
    total_files += research_wikipedia(name, output_dir)

    # 4. Brave Search
    print("  Phase 3: Brave Search...")
    files, urls = research_brave_search(name, output_dir)
    total_files += files
    discovered_urls.extend(urls)

    # 5. Kagi FastGPT
    print("  Phase 4: Kagi FastGPT...")
    files, urls = research_kagi(name, output_dir)
    total_files += files
    discovered_urls.extend(urls)

    # 6. Crawl discovered URLs
    print("  Phase 5: Crawling discovered URLs...")
    total_files += crawl_discovered_urls(discovered_urls, output_dir)

    # 7. Additional sources
    print("  Phase 6: Additional sources...")
    total_files += research_additional_sources(name, output_dir)

    # Count total files
    all_files = list(output_dir.glob("*.json"))
    source_files = [f for f in all_files if not f.name.startswith("_")]

    status = "PASS" if len(source_files) >= 10 else "NEEDS MORE"
    print(f"\n  Total source files: {len(source_files)} [{status}]")
    print(f"  Vault games: {len(vault_games)}")

    return {
        "name": name,
        "slug": slug,
        "source_files": len(source_files),
        "vault_games": len(vault_games),
        "status": status
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Publisher Research Pipeline")
    parser.add_argument('--publisher', help='Research a single publisher')
    parser.add_argument('--all', action='store_true', help='Research all publishers')
    parser.add_argument('--list', help='File with publisher names (one per line)')
    parser.add_argument('--force', action='store_true', help='Re-research even if exists')
    parser.add_argument('--parallel', type=int, default=1,
                        help='Number of parallel workers (default: 1, max: 4)')
    args = parser.parse_args()

    # Verify API keys
    missing_keys = []
    if not BRAVE_API_KEY: missing_keys.append("BRAVE_API_KEY")
    if not KAGI_API_KEY: missing_keys.append("KAGI_API_KEY")
    if not SCRAPER_API_KEY: missing_keys.append("SCRAPER_API_KEY")

    if missing_keys:
        print(f"ERROR: Missing API keys: {', '.join(missing_keys)}")
        print("Run: source .env")
        return

    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

    # Limit parallel workers to avoid API rate limits
    num_workers = min(max(1, args.parallel), 4)

    if args.publisher:
        research_publisher(args.publisher, args.force)
    elif args.all:
        results = []

        if num_workers > 1:
            print(f"\nRunning with {num_workers} parallel workers...")
            print("Note: Some APIs have rate limits, parallel may cause throttling.\n")

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = {
                    executor.submit(research_publisher, name, args.force): name
                    for name in ALL_PUBLISHERS
                }

                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        print(f"  ERROR researching {name}: {e}")
                        results.append({
                            "name": name,
                            "slug": slugify(name),
                            "source_files": 0,
                            "vault_games": 0,
                            "status": "ERROR"
                        })
        else:
            for name in ALL_PUBLISHERS:
                result = research_publisher(name, args.force)
                results.append(result)

        # Summary
        print("\n" + "="*60)
        print("RESEARCH SUMMARY")
        print("="*60)

        for r in sorted(results, key=lambda x: x.get("name", "")):
            status = r.get("status", "UNKNOWN")
            files = r.get("source_files", 0)
            games = r.get("vault_games", 0)
            marker = "✓" if status == "PASS" else "✗" if status == "ERROR" else "○"
            print(f"  {marker} {r['name']}: {files} sources, {games} vault games [{status}]")

        passed = len([r for r in results if r.get("status") == "PASS"])
        errors = len([r for r in results if r.get("status") == "ERROR"])
        print(f"\nTotal: {passed}/{len(results)} passed (10+ sources)")
        if errors:
            print(f"Errors: {errors}")

    elif args.list:
        names = Path(args.list).read_text().strip().split('\n')
        for name in names:
            if name.strip():
                research_publisher(name.strip(), args.force)
    else:
        parser.print_help()
        print("\nAvailable publishers:")
        for name in ALL_PUBLISHERS:
            print(f"  - {name}")


if __name__ == '__main__':
    main()
