#!/usr/bin/env python3
"""
URL Discovery System for Sierra Games Archive

Discovers URLs for a game from multiple sources:
1. Wikipedia - Extract all external references
2. Grokipedia - Extract references
3. Kagi web search - 10 query variants for diverse results
4. Known source templates - MobyGames, GOG, Steam, etc.
5. Fandom wiki subpage discovery
6. Direct database URLs for known gaming sites

Output: research/{game-slug}/_urls.json
"""

import argparse
import asyncio
import json
import re
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote_plus
import httpx
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

# API Keys
KAGI_API_KEY = os.environ.get('KAGI_API_KEY', '')
BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY', '')

# Paths
SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"
DOMAINS_FILE = INTERNAL_DIR / "data" / "domains.json"

# Load domain intelligence
def load_domains():
    if DOMAINS_FILE.exists():
        with open(DOMAINS_FILE) as f:
            return json.load(f)
    return {"domains": {}}

DOMAIN_DB = load_domains()

# Smart domain limits - allow more URLs from content-rich sites
MAX_PER_DOMAIN = {
    # Deep content sites - many unique pages
    'fandom.com': 15,
    'spacequest.net': 10,
    'archive.org': 10,
    'mobygames.com': 5,
    'sierrachest.com': 5,
    'sierrahelp.com': 5,
    'wiki.sierrahelp.com': 5,
    'gamefaqs.gamespot.com': 5,
    'wiki.scummvm.org': 4,
    'tcrf.net': 3,
    'pcgamingwiki.com': 3,
    # Single-page sources
    'wikipedia.org': 2,
    'gog.com': 2,
    'steampowered.com': 2,
    'igdb.com': 2,
    'rawg.io': 2,
    # Reviews
    'adventuregamers.com': 3,
    'ign.com': 2,
    'gamespot.com': 3,
    'hardcoregaming101.net': 3,
    # Default
    'default': 3,
}

# Kagi search query templates for diverse results
KAGI_SEARCH_QUERIES = [
    '"{game_title}" Sierra game review',
    '"{game_title}" video game retrospective',
    '"{game_title}" Sierra OR Dynamix development',
    '"{game_title}" game walkthrough OR guide',
    '"{game_title}" DOS game manual',
    '"{game_title}" game soundtrack OR music',
    '"{game_title}" speedrun video game',
    '"{game_title}" Sierra patch OR fix',
    '"{game_title}" video game easter egg',
    '"{game_title}" MobyGames OR GOG',
]

# Fandom subpages to discover
FANDOM_SUBPAGES = [
    '',  # Main page
    '/Characters',
    '/Locations',
    '/Easter_eggs',
    '/Easter_Eggs',
    '/Development',
    '/Behind_the_scenes',
    '/Walkthrough',
    '/Items',
    '/Music',
    '/Soundtrack',
    '/Cut_content',
    '/Unused_content',
    '/Gallery',
    '/Trivia',
    '/Glitches',
    '/Bugs',
    '/Cast',
    '/Voice_cast',
    '/Voice_Cast',
]


def get_domain_limit(domain: str) -> int:
    """Get max URLs allowed for a domain."""
    if domain in MAX_PER_DOMAIN:
        return MAX_PER_DOMAIN[domain]
    for pattern, limit in MAX_PER_DOMAIN.items():
        if pattern in domain:
            return limit
    return MAX_PER_DOMAIN['default']


def slugify(title: str) -> str:
    """Convert game title to folder slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


# Games directory for metadata lookup
GAMES_DIR = INTERNAL_DIR.parent / "Games"


def get_game_metadata(game_title: str) -> dict:
    """
    Look up game metadata (developer, publisher, series) from existing game files
    or MobyGames research data.
    Returns dict with: developer, publisher, series, release_year
    """
    metadata = {
        "developer": None,
        "publisher": None,
        "series": None,
        "release_year": None,
    }

    # First, try to load from MobyGames research data
    slug = slugify(game_title)
    moby_file = GAMES_RESEARCH_DIR / slug / "mobygames.json"
    if moby_file.exists():
        try:
            with open(moby_file) as f:
                moby_data = json.load(f)
            # Extract developer/publisher from MobyGames data
            if moby_data.get('developers'):
                devs = moby_data['developers']
                if isinstance(devs, list) and devs:
                    metadata['developer'] = devs[0].get('name') if isinstance(devs[0], dict) else devs[0]
                elif isinstance(devs, str):
                    metadata['developer'] = devs
            if moby_data.get('publishers'):
                pubs = moby_data['publishers']
                if isinstance(pubs, list) and pubs:
                    metadata['publisher'] = pubs[0].get('name') if isinstance(pubs[0], dict) else pubs[0]
                elif isinstance(pubs, str):
                    metadata['publisher'] = pubs
            if moby_data.get('series'):
                metadata['series'] = moby_data['series']
            if moby_data.get('release_date'):
                try:
                    metadata['release_year'] = int(str(moby_data['release_date'])[:4])
                except:
                    pass
            # If we got good data, return early
            if metadata['developer'] or metadata['publisher']:
                return metadata
        except Exception:
            pass

    # Fall back to game file YAML frontmatter
    metadata = {
        "developer": None,
        "publisher": None,
        "series": None,
        "release_year": None,
    }

    # Search for game file by title
    slug = slugify(game_title)

    # Try to find the game file
    for game_file in GAMES_DIR.rglob("*.md"):
        file_slug = slugify(game_file.stem.split(" - ", 1)[-1] if " - " in game_file.stem else game_file.stem)
        if file_slug == slug or game_title.lower() in game_file.stem.lower():
            try:
                content = game_file.read_text()
                # Extract YAML frontmatter
                if content.startswith("---"):
                    end = content.find("---", 3)
                    if end > 0:
                        frontmatter = content[3:end].strip()
                        data = yaml.safe_load(frontmatter)
                        if data:
                            metadata["developer"] = data.get("developer")
                            metadata["publisher"] = data.get("publisher")
                            metadata["series"] = data.get("series")
                            metadata["release_year"] = data.get("release_year")
                            return metadata
            except Exception:
                pass

    return metadata


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""

def should_skip_domain(domain: str) -> bool:
    """Check if domain should be skipped based on intelligence."""
    domain_info = DOMAIN_DB.get("domains", {}).get(domain, {})
    return domain_info.get("method") == "skip"

async def fetch_wikipedia_refs(game_title: str) -> list[dict]:
    """Extract external references from Wikipedia article."""
    urls = []
    search_title = game_title.replace(" ", "_")

    # Try direct URL first
    wiki_urls = [
        f"https://en.wikipedia.org/wiki/{quote_plus(search_title)}",
        f"https://en.wikipedia.org/wiki/{quote_plus(game_title)}_(video_game)",
    ]

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        for wiki_url in wiki_urls:
            try:
                resp = await client.get(wiki_url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, 'html.parser')

                # Check if it's actually about a video game
                categories = soup.find_all('a', href=re.compile(r'/wiki/Category:'))
                is_game = any('video_game' in c.get('href', '').lower() or 'game' in c.get_text().lower()
                             for c in categories)

                if not is_game:
                    continue

                # Extract external links from references
                refs = soup.find_all('cite', class_='citation')
                for cite in refs:
                    links = cite.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        if href.startswith('http') and 'wikipedia' not in href.lower():
                            domain = get_domain(href)
                            if not should_skip_domain(domain):
                                urls.append({
                                    "url": href,
                                    "source": "wikipedia_refs",
                                    "domain": domain
                                })

                # Also get external links section
                ext_links = soup.find('span', id='External_links')
                if ext_links:
                    parent = ext_links.find_parent(['h2', 'h3'])
                    if parent:
                        for sibling in parent.find_next_siblings():
                            if sibling.name in ['h2', 'h3']:
                                break
                            for link in sibling.find_all('a', href=True):
                                href = link.get('href', '')
                                if href.startswith('http') and 'wikipedia' not in href.lower():
                                    domain = get_domain(href)
                                    if not should_skip_domain(domain):
                                        urls.append({
                                            "url": href,
                                            "source": "wikipedia_external",
                                            "domain": domain
                                        })

                # Found valid article
                urls.append({
                    "url": wiki_url,
                    "source": "wikipedia",
                    "domain": "en.wikipedia.org"
                })
                break

            except Exception as e:
                continue

    return urls


async def fetch_grokipedia_refs(game_title: str) -> list[dict]:
    """Extract references and links from Grokipedia article."""
    urls = []
    search_title = game_title.replace(" ", "_")
    grok_url = f"https://grokipedia.com/page/{quote_plus(search_title)}"

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            resp = await client.get(grok_url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                # Try alternate formats
                alternates = [
                    f"https://grokipedia.com/page/{quote_plus(game_title)}",
                    f"https://grokipedia.com/page/{game_title.replace(' ', '_')}_(video_game)",
                ]
                for alt in alternates:
                    try:
                        resp = await client.get(alt, headers={"User-Agent": "Mozilla/5.0"})
                        if resp.status_code == 200:
                            grok_url = alt
                            break
                    except:
                        continue
                else:
                    return urls

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Add Grokipedia page itself
            urls.append({
                "url": grok_url,
                "source": "grokipedia",
                "domain": "grokipedia.com"
            })

            # Extract all external links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('http') and 'grokipedia' not in href.lower():
                    domain = get_domain(href)
                    if domain and not should_skip_domain(domain):
                        urls.append({
                            "url": href,
                            "source": "grokipedia_refs",
                            "domain": domain
                        })

        except Exception as e:
            pass

    return urls

async def search_web(game_title: str, domains: list[str], metadata: dict = None) -> list[dict]:
    """
    Search web for game on specific domains using contextual queries.
    Uses developer/publisher context for games with generic titles.
    """
    urls = []
    metadata = metadata or {}

    # Build contextual query variants
    queries = [f'"{game_title}"']

    # Add developer context for better results
    if metadata.get("developer"):
        dev = metadata["developer"]
        queries.append(f'"{game_title}" "{dev}"')
        queries.append(f'"{game_title}" {dev} game')

    # Add publisher context
    if metadata.get("publisher"):
        pub = metadata["publisher"]
        queries.append(f'"{game_title}" "{pub}"')

    # Add "game" or "video game" for disambiguation
    queries.append(f'"{game_title}" video game')
    queries.append(f'"{game_title}" PC game review')

    # Use DuckDuckGo HTML search (no API needed)
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        seen_urls = set()

        for domain in domains[:15]:  # Limit to avoid rate limiting
            if should_skip_domain(domain):
                continue

            # Try each query variant
            for query in queries[:3]:  # Use top 3 query variants
                search_query = f'{query} site:{domain}'
                search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(search_query)}"

                try:
                    resp = await client.get(search_url, headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                    })

                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        results = soup.find_all('a', class_='result__a')

                        for result in results[:3]:  # Top 3 results per query
                            href = result.get('href', '')
                            if href and domain in href and href not in seen_urls:
                                seen_urls.add(href)
                                urls.append({
                                    "url": href,
                                    "source": "web_search",
                                    "domain": domain
                                })

                    await asyncio.sleep(0.3)  # Rate limit

                except Exception as e:
                    continue

    return urls


async def search_general(game_title: str, metadata: dict = None) -> list[dict]:
    """
    Perform general web searches with contextual queries (not domain-specific).
    Returns URLs from any gaming-related domain.
    """
    urls = []
    metadata = metadata or {}

    # Build search queries with context
    queries = []

    # Basic query
    queries.append(f'"{game_title}" video game')

    # With developer
    if metadata.get("developer"):
        dev = metadata["developer"]
        queries.append(f'"{game_title}" "{dev}"')

    # With publisher
    if metadata.get("publisher"):
        pub = metadata["publisher"]
        queries.append(f'"{game_title}" "{pub}" game')

    # Add review/retrospective queries
    queries.append(f'"{game_title}" game review')
    queries.append(f'"{game_title}" retrospective')

    trusted_domains = {
        "mobygames.com", "pcgamingwiki.com", "gog.com", "igdb.com",
        "hardcoregaming101.net", "filfre.net", "adventuregamers.com",
        "sierrahelp.com", "sierrachest.com", "scummvm.org",
        "myabandonware.com", "abandonwaredos.com", "archive.org"
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        seen_urls = set()

        for query in queries[:5]:
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

            try:
                resp = await client.get(search_url, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                })

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    results = soup.find_all('a', class_='result__a')

                    for result in results[:5]:
                        href = result.get('href', '')
                        if href and href not in seen_urls:
                            domain = get_domain(href)
                            # Only keep results from trusted gaming domains
                            if any(td in domain for td in trusted_domains):
                                seen_urls.add(href)
                                urls.append({
                                    "url": href,
                                    "source": "web_search_general",
                                    "domain": domain
                                })

                await asyncio.sleep(0.5)

            except Exception:
                continue

    return urls


async def kagi_search(query: str, limit: int = 10) -> list[dict]:
    """Search using Kagi API for higher quality results."""
    if not KAGI_API_KEY:
        print("    Warning: KAGI_API_KEY not set, falling back to DuckDuckGo")
        return []

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://kagi.com/api/v0/search",
                headers={"Authorization": f"Bot {KAGI_API_KEY}"},
                params={"q": query, "limit": limit}
            )

            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get('data', []):
                    if item.get('url'):
                        domain = get_domain(item['url'])
                        results.append({
                            'url': item['url'],
                            'title': item.get('title', ''),
                            'source': 'kagi_search',
                            'domain': domain,
                            'query': query,
                        })
                return results
            else:
                print(f"    Kagi error: {response.status_code}")
                return []
    except Exception as e:
        print(f"    Kagi exception: {e}")
        return []


async def kagi_search_diverse(game_title: str, metadata: dict = None) -> list[dict]:
    """Run multiple Kagi searches with diverse query variants."""
    urls = []
    metadata = metadata or {}
    designer = ''
    if metadata.get('designer'):
        if isinstance(metadata['designer'], list):
            designer = metadata['designer'][0] if metadata['designer'] else ''
        else:
            designer = metadata['designer']

    seen_urls = set()

    for i, query_template in enumerate(KAGI_SEARCH_QUERIES):
        query = query_template.format(game_title=game_title, designer=designer)
        results = await kagi_search(query, limit=10)

        new_count = 0
        for r in results:
            if r['url'] not in seen_urls:
                seen_urls.add(r['url'])
                urls.append(r)
                new_count += 1

        print(f"        Query {i+1}/{len(KAGI_SEARCH_QUERIES)}: +{new_count} new URLs")
        await asyncio.sleep(0.3)  # Rate limit

    return urls


async def brave_search(query: str, count: int = 10) -> list[dict]:
    """Search using Brave Search API with all Pro Data features."""
    if not BRAVE_API_KEY:
        return []

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": BRAVE_API_KEY
                },
                params={
                    "q": query,
                    "count": count,
                    "result_filter": "web,news,videos,discussions,faq,infobox,locations",
                    "extra_snippets": True,
                }
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                # Web results - capture ALL Pro Data fields
                for item in data.get('web', {}).get('results', []):
                    if item.get('url'):
                        domain = get_domain(item['url'])
                        result = {
                            'url': item['url'],
                            'title': item.get('title', ''),
                            'source': 'brave_web',
                            'domain': domain,
                            'query': query,
                            # Pro Data fields
                            'description': item.get('description', ''),
                            'page_age': item.get('page_age'),
                            'age': item.get('age'),
                            'subtype': item.get('subtype'),  # e.g., "review"
                            'language': item.get('language'),
                            'extra_snippets': item.get('extra_snippets', []),
                        }
                        # Profile info
                        if item.get('profile'):
                            result['source_name'] = item['profile'].get('name')
                            result['source_long_name'] = item['profile'].get('long_name')
                        # Thumbnail
                        if item.get('thumbnail'):
                            result['thumbnail'] = item['thumbnail'].get('src')
                        results.append(result)

                # News results
                for item in data.get('news', {}).get('results', []):
                    if item.get('url'):
                        domain = get_domain(item['url'])
                        results.append({
                            'url': item['url'],
                            'title': item.get('title', ''),
                            'source': 'brave_news',
                            'domain': domain,
                            'query': query,
                            'description': item.get('description', ''),
                            'page_age': item.get('page_age'),
                            'age': item.get('age'),
                        })

                # Video results - capture video metadata
                for item in data.get('videos', {}).get('results', []):
                    if item.get('url'):
                        domain = get_domain(item['url'])
                        result = {
                            'url': item['url'],
                            'title': item.get('title', ''),
                            'source': 'brave_video',
                            'domain': domain,
                            'query': query,
                            'description': item.get('description', ''),
                            'page_age': item.get('page_age'),
                            'age': item.get('age'),
                        }
                        # Video-specific metadata
                        if item.get('video'):
                            result['video_duration'] = item['video'].get('duration')
                            result['video_views'] = item['video'].get('views')
                            result['video_creator'] = item['video'].get('creator')
                            result['video_publisher'] = item['video'].get('publisher')
                        results.append(result)

                # Discussion/forum results
                for item in data.get('discussions', {}).get('results', []):
                    if item.get('url'):
                        domain = get_domain(item['url'])
                        results.append({
                            'url': item['url'],
                            'title': item.get('title', ''),
                            'source': 'brave_discussion',
                            'domain': domain,
                            'query': query,
                            'description': item.get('description', ''),
                            'page_age': item.get('page_age'),
                        })

                # Infobox - capture rich data
                infobox = data.get('infobox', {})
                for item in infobox.get('results', []):
                    if item.get('url'):
                        result = {
                            'url': item['url'],
                            'title': item.get('title', ''),
                            'source': 'brave_infobox',
                            'domain': get_domain(item['url']),
                            'query': query,
                            'description': item.get('description', ''),
                        }
                        # Infobox Q&A data
                        if item.get('data'):
                            result['infobox_question'] = item['data'].get('question')
                            if item['data'].get('answer'):
                                result['infobox_answer'] = item['data']['answer'].get('text', '')[:500]
                        results.append(result)

                # FAQ results
                for item in data.get('faq', {}).get('results', []):
                    if item.get('url'):
                        domain = get_domain(item['url'])
                        results.append({
                            'url': item['url'],
                            'title': item.get('title', item.get('question', '')),
                            'source': 'brave_faq',
                            'domain': domain,
                            'query': query,
                            'question': item.get('question'),
                            'answer': item.get('answer', '')[:500] if item.get('answer') else None,
                        })

                # Location results (game stores, museums, etc.)
                for item in data.get('locations', {}).get('results', []):
                    if item.get('url'):
                        domain = get_domain(item['url'])
                        results.append({
                            'url': item['url'],
                            'title': item.get('title', ''),
                            'source': 'brave_location',
                            'domain': domain,
                            'query': query,
                            'address': item.get('address'),
                        })

                return results
            else:
                print(f"    Brave error: {response.status_code}")
                return []
    except Exception as e:
        print(f"    Brave exception: {e}")
        return []


async def brave_search_diverse(game_title: str, metadata: dict = None) -> list[dict]:
    """Run multiple Brave searches with diverse query variants."""
    urls = []
    metadata = metadata or {}

    # Extract developer for better query context
    developer = ''
    if metadata.get('developer'):
        dev = metadata['developer']
        if isinstance(dev, list):
            developer = dev[0] if dev else ''
        else:
            developer = dev

    # For generic titles, add developer context to improve relevance
    generic_words = {'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'and', 'or'}
    title_words = [w for w in game_title.lower().split() if w not in generic_words]
    is_generic_title = len(title_words) <= 2  # Short titles are more likely to be generic

    # Build context string for generic titles
    context = ''
    if is_generic_title and developer:
        context = f' {developer}'

    seen_urls = set()

    for i, query_template in enumerate(KAGI_SEARCH_QUERIES):
        query = query_template.format(game_title=game_title, designer=developer)
        # Add developer context for generic titles
        if context and 'Sierra' not in query:
            query = query + context
        results = await brave_search(query, count=10)

        new_count = 0
        for r in results:
            if r['url'] not in seen_urls:
                seen_urls.add(r['url'])
                urls.append(r)
                new_count += 1

        print(f"        Query {i+1}/{len(KAGI_SEARCH_QUERIES)}: +{new_count} new URLs")
        await asyncio.sleep(0.02)  # Brave Pro allows 50 qps

    return urls


async def check_url_exists(url: str) -> bool:
    """Quick HEAD check if URL exists."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.head(
                url,
                headers={'User-Agent': 'Mozilla/5.0'},
                follow_redirects=True
            )
            return response.status_code == 200
    except:
        return False


async def discover_fandom_pages(game_title: str, series: str = None) -> list[dict]:
    """Discover Fandom wiki pages by checking subpages."""
    urls = []
    wiki_title = game_title.replace(" ", "_")

    # Determine which Fandom wikis to check
    wikis_to_check = ['sierra.fandom.com']

    if series:
        series_lower = series.lower()
        if 'king' in series_lower and 'quest' in series_lower:
            wikis_to_check.append('kingsquest.fandom.com')
        elif 'space' in series_lower and 'quest' in series_lower:
            wikis_to_check.append('spacequest.fandom.com')
        elif 'quest for glory' in series_lower or 'hero' in series_lower:
            wikis_to_check.append('questforglory.fandom.com')
        elif 'leisure' in series_lower or 'larry' in series_lower:
            wikis_to_check.append('leisuresuitlarry.fandom.com')
        elif 'police' in series_lower and 'quest' in series_lower:
            wikis_to_check.append('policequestseries.fandom.com')
        elif 'gabriel' in series_lower:
            wikis_to_check.append('gabrielknight.fandom.com')

    print(f"        Checking {len(wikis_to_check)} Fandom wikis...")

    for wiki in wikis_to_check:
        found_pages = 0
        for subpage in FANDOM_SUBPAGES:
            url = f"https://{wiki}/wiki/{wiki_title}{subpage}"
            if await check_url_exists(url):
                urls.append({
                    'url': url,
                    'title': f"{wiki} - {game_title}{subpage}",
                    'source': 'fandom_discovery',
                    'domain': wiki,
                })
                found_pages += 1
            await asyncio.sleep(0.1)  # Rate limit

        if found_pages > 0:
            print(f"        {wiki}: {found_pages} pages")

    return urls


def generate_template_urls(game_title: str, series: str = None) -> list[dict]:
    """Generate URLs from known templates."""
    urls = []
    slug = slugify(game_title)
    encoded = quote_plus(game_title)
    wiki_title = game_title.replace(" ", "_")

    # Core database templates
    templates = [
        ("https://www.mobygames.com/search/?q=" + encoded, "www.mobygames.com"),
        ("https://store.steampowered.com/search/?term=" + encoded, "store.steampowered.com"),
        ("https://www.gog.com/en/games?query=" + encoded, "www.gog.com"),
        ("https://www.pcgamingwiki.com/wiki/" + wiki_title, "www.pcgamingwiki.com"),
        ("https://gamefaqs.gamespot.com/search?game=" + encoded, "gamefaqs.gamespot.com"),
        ("https://rawg.io/search?query=" + encoded, "rawg.io"),
        ("https://www.imdb.com/find/?q=" + encoded + "&s=tt", "www.imdb.com"),
        ("https://howlongtobeat.com/?q=" + encoded, "howlongtobeat.com"),
        ("https://www.speedrun.com/" + slug, "www.speedrun.com"),
        ("https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/" + game_title.replace(" ", ""), "tvtropes.org"),
        ("https://www.behindthevoiceactors.com/video-games/" + slug + "/", "www.behindthevoiceactors.com"),
        ("https://tcrf.net/" + wiki_title, "tcrf.net"),
    ]

    # Sierra-specific templates (note: sierrahelp without www)
    sierra_templates = [
        ("https://www.sierrachest.com/index.php?a=search&q=" + encoded, "www.sierrachest.com"),
        ("https://sierrahelp.com/Games/" + wiki_title, "sierrahelp.com"),
        ("https://wiki.sierrahelp.com/index.php?search=" + encoded, "wiki.sierrahelp.com"),
        ("https://sierra.fandom.com/wiki/" + wiki_title, "sierra.fandom.com"),
        ("https://sciwiki.sierrahelp.com/index.php?search=" + encoded, "sciwiki.sierrahelp.com"),
        ("https://wiki.scummvm.org/index.php/" + wiki_title, "wiki.scummvm.org"),
        ("https://dynamix.fandom.com/wiki/" + wiki_title, "dynamix.fandom.com"),
    ]

    # Abandonware/retro gaming sites
    retro_templates = [
        ("https://www.myabandonware.com/search/q/" + encoded, "www.myabandonware.com"),
        ("https://www.abandonwaredos.com/search.php?search=" + encoded, "www.abandonwaredos.com"),
        ("https://gamesnostalgia.com/search?query=" + encoded, "gamesnostalgia.com"),
        ("https://classicreload.com/" + slug + ".html", "classicreload.com"),
        ("https://www.lemonamiga.com/games/search.php?search=" + encoded, "www.lemonamiga.com"),
        ("https://amiga.fandom.com/wiki/" + wiki_title, "amiga.fandom.com"),
    ]

    # Historical/retrospective sites
    history_templates = [
        ("https://www.filfre.net/?s=" + encoded, "www.filfre.net"),
        ("https://www.hardcoregaming101.net/?s=" + encoded, "www.hardcoregaming101.net"),
        ("https://retro365.blog/?s=" + encoded, "retro365.blog"),
        ("https://adventuregamers.com/search/?q=" + encoded, "adventuregamers.com"),
    ]

    # Archive/historical sources
    archive_templates = [
        ("https://archive.org/search?query=" + encoded + "+sierra", "archive.org"),
        ("https://www.mocagh.org/search.php?search=" + encoded, "www.mocagh.org"),
    ]

    # Series-specific wikis
    series_wikis = {
        "King's Quest": [
            ("https://kingsquest.fandom.com/wiki/" + wiki_title, "kingsquest.fandom.com"),
        ],
        "Space Quest": [
            ("https://spacequest.fandom.com/wiki/" + wiki_title, "spacequest.fandom.com"),
            ("https://spacequest.net/sq" + slug[-1] if slug[-1].isdigit() else "", "spacequest.net"),
        ],
        "Quest for Glory": [
            ("https://questforglory.fandom.com/wiki/" + wiki_title, "questforglory.fandom.com"),
        ],
        "Leisure Suit Larry": [
            ("https://larrylaffer.net/games/", "larrylaffer.net"),
        ],
        "Gabriel Knight": [
            ("https://gabrielknight.fandom.com/wiki/" + wiki_title, "gabrielknight.fandom.com"),
        ],
        "Police Quest": [
            ("https://policequest.fandom.com/wiki/" + wiki_title, "policequest.fandom.com"),
        ],
    }

    all_templates = templates + sierra_templates + retro_templates + history_templates + archive_templates

    for url, domain in all_templates:
        if not should_skip_domain(domain):
            urls.append({
                "url": url,
                "source": "template",
                "domain": domain
            })

    # Add series-specific URLs
    if series and series in series_wikis:
        for url, domain in series_wikis[series]:
            if url and not should_skip_domain(domain):
                urls.append({
                    "url": url,
                    "source": "series_template",
                    "domain": domain
                })

    return urls

def deduplicate_urls(urls: list[dict]) -> list[dict]:
    """Remove duplicate URLs, keeping first occurrence."""
    seen = set()
    unique = []
    for item in urls:
        url = item["url"].rstrip("/").lower()
        if url not in seen:
            seen.add(url)
            unique.append(item)
    return unique

async def discover_urls(game_title: str, series: str = None,
                       skip_search: bool = False) -> dict:
    """
    Discover all URLs for a game from multiple sources.

    Returns dict with:
    - discovered: list of URL dicts
    - crawled: dict of url -> status
    - pending: list of URLs to crawl
    """
    print(f"\nDiscovering URLs for: {game_title}")
    print("=" * 60)

    all_urls = []

    # 0. Look up game metadata for contextual searches
    print("  [0/5] Looking up game metadata...")
    metadata = get_game_metadata(game_title)
    if metadata.get("developer"):
        print(f"        Developer: {metadata['developer']}")
    if metadata.get("publisher"):
        print(f"        Publisher: {metadata['publisher']}")
    if metadata.get("series"):
        series = series or metadata.get("series")  # Use metadata if not provided
        print(f"        Series: {series}")

    # 1. Wikipedia references
    print("  [1/5] Extracting Wikipedia references...")
    wiki_urls = await fetch_wikipedia_refs(game_title)
    print(f"        Found {len(wiki_urls)} URLs from Wikipedia")
    all_urls.extend(wiki_urls)

    # 2. Grokipedia references
    print("  [2/5] Extracting Grokipedia references...")
    grok_urls = await fetch_grokipedia_refs(game_title)
    print(f"        Found {len(grok_urls)} URLs from Grokipedia")
    all_urls.extend(grok_urls)

    # 3. Template URLs (expanded list)
    print("  [3/5] Generating template URLs...")
    template_urls = generate_template_urls(game_title, series)
    print(f"        Generated {len(template_urls)} template URLs")
    all_urls.extend(template_urls)

    # 4. Web search (Brave preferred, Kagi fallback, DuckDuckGo last resort)
    if not skip_search:
        if BRAVE_API_KEY:
            print("  [4/6] Running Brave diverse searches...")
            brave_urls = await brave_search_diverse(game_title, metadata)
            print(f"        Total from Brave: {len(brave_urls)} URLs")
            all_urls.extend(brave_urls)
        elif KAGI_API_KEY:
            print("  [4/6] Running Kagi diverse searches...")
            kagi_urls = await kagi_search_diverse(game_title, metadata)
            print(f"        Total from Kagi: {len(kagi_urls)} URLs")
            all_urls.extend(kagi_urls)
        else:
            # Fallback to DuckDuckGo
            print("  [4/6] Running DuckDuckGo searches...")
            search_domains = [
                d for d, info in DOMAIN_DB.get("domains", {}).items()
                if info.get("priority", 5) <= 3 and info.get("method") != "skip"
            ]
            search_urls = await search_web(game_title, search_domains, metadata)
            print(f"        Found {len(search_urls)} URLs from domain search")
            all_urls.extend(search_urls)
            general_urls = await search_general(game_title, metadata)
            print(f"        Found {len(general_urls)} URLs from general search")
            all_urls.extend(general_urls)

        # 5. Fandom wiki subpage discovery
        print("  [5/6] Discovering Fandom wiki pages...")
        fandom_urls = await discover_fandom_pages(game_title, series)
        print(f"        Found {len(fandom_urls)} Fandom pages")
        all_urls.extend(fandom_urls)
    else:
        print("  [4/6] Skipping web search")
        print("  [5/6] Skipping Fandom discovery")

    # 6. Apply domain limits for diversity
    print("  [6/6] Applying domain diversity limits...")

    # Deduplicate first
    deduped_urls = deduplicate_urls(all_urls)
    print(f"        After dedup: {len(deduped_urls)} URLs")

    # Apply domain limits
    domain_counts = {}
    unique_urls = []
    skipped_by_limit = 0

    for url_info in deduped_urls:
        domain = url_info.get("domain", get_domain(url_info.get("url", "")))
        limit = get_domain_limit(domain)

        if domain_counts.get(domain, 0) < limit:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            unique_urls.append(url_info)
        else:
            skipped_by_limit += 1

    print(f"        After domain limits: {len(unique_urls)} URLs (skipped {skipped_by_limit})")
    print(f"\n  Total unique URLs: {len(unique_urls)}")

    # Sort by domain priority
    def get_priority(url_dict):
        domain = url_dict.get("domain", "")
        return DOMAIN_DB.get("domains", {}).get(domain, {}).get("priority", 5)

    unique_urls.sort(key=get_priority)

    # Show domain breakdown
    domain_counts = {}
    for u in unique_urls:
        d = u.get("domain", "unknown")
        domain_counts[d] = domain_counts.get(d, 0) + 1

    print(f"\n  Top domains:")
    for d, count in sorted(domain_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {d}: {count}")

    return {
        "game_title": game_title,
        "series": series,
        "discovered": unique_urls,
        "crawled": {},
        "pending": [u["url"] for u in unique_urls],
        "discovery_date": datetime.now().isoformat(),
        "total_discovered": len(unique_urls)
    }

def save_urls(game_slug: str, urls_data: dict):
    """Save URLs to research folder."""
    folder = GAMES_RESEARCH_DIR / game_slug
    folder.mkdir(parents=True, exist_ok=True)

    urls_file = folder / "_urls.json"
    with open(urls_file, 'w') as f:
        json.dump(urls_data, f, indent=2)

    print(f"\n  Saved to: {urls_file}")

def load_urls(game_slug: str) -> dict:
    """Load existing URLs for a game."""
    urls_file = GAMES_RESEARCH_DIR / game_slug / "_urls.json"
    if urls_file.exists():
        with open(urls_file) as f:
            return json.load(f)
    return None

async def main():
    parser = argparse.ArgumentParser(description="Discover URLs for a game")
    parser.add_argument("game", help="Game title")
    parser.add_argument("--series", help="Series name (e.g., 'King's Quest')")
    parser.add_argument("--skip-search", action="store_true",
                       help="Skip web search (faster)")
    parser.add_argument("--refresh", action="store_true",
                       help="Re-discover even if URLs exist")
    parser.add_argument("--list", action="store_true",
                       help="List existing discovered URLs")

    args = parser.parse_args()
    game_slug = slugify(args.game)

    # List mode
    if args.list:
        existing = load_urls(game_slug)
        if existing:
            print(f"\nDiscovered URLs for: {existing.get('game_title', args.game)}")
            print(f"Total: {existing.get('total_discovered', 0)}")
            print(f"Pending: {len(existing.get('pending', []))}")
            print(f"Crawled: {len(existing.get('crawled', {}))}")
            print("\nBy domain:")
            domains = {}
            for u in existing.get("discovered", []):
                d = u.get("domain", "unknown")
                domains[d] = domains.get(d, 0) + 1
            for d, count in sorted(domains.items(), key=lambda x: -x[1]):
                print(f"  {d}: {count}")
        else:
            print(f"No URLs discovered yet for: {args.game}")
        return

    # Check for existing
    if not args.refresh:
        existing = load_urls(game_slug)
        if existing and existing.get("total_discovered", 0) > 0:
            print(f"URLs already discovered for {args.game}")
            print(f"  Total: {existing.get('total_discovered', 0)}")
            print(f"  Use --refresh to re-discover")
            return

    # Discover URLs
    urls_data = await discover_urls(args.game, args.series, args.skip_search)
    save_urls(game_slug, urls_data)

    print(f"\nDone! Discovered {urls_data['total_discovered']} URLs")
    print(f"Next: Run 'python3 crawl_sources.py {args.game}' to fetch content")

if __name__ == "__main__":
    asyncio.run(main())
