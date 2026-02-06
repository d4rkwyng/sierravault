#!/usr/bin/env python3
"""
Validate external links in SierraVault pages with content verification.
Uses ScraperAPI to fetch pages and verifies game names match.

Usage:
    python3 validate_external_links.py                    # Check all
    python3 validate_external_links.py --dreamlist        # Only GOG Dreamlist
    python3 validate_external_links.py --gog              # All GOG links
    python3 validate_external_links.py --steam            # Steam links
    python3 validate_external_links.py --file "path.md"   # Single file
    python3 validate_external_links.py --dry-run          # Show URLs without checking

Requires: SCRAPERAPI_KEY environment variable
"""

import argparse
import os
import re
import sys
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
import urllib.request
import urllib.error
import urllib.parse
from html.parser import HTMLParser

VAULT_PATH = Path(__file__).parent.parent / 'vault'
SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY')
SCRAPERAPI_URL = 'http://api.scraperapi.com'

# URL patterns to check
PATTERNS = {
    'gog_dreamlist': r'https://www\.gog\.com/dreamlist/game/[^\s\)\]]+',
    'gog_store': r'https://www\.gog\.com/(?:en/)?game/[^\s\)\]]+',
    'steam': r'https://store\.steampowered\.com/app/[^\s\)\]]+',
}

# Normalization patterns for game name comparison
NORMALIZE_PATTERNS = [
    (r'\s*[-:]\s*(VGA|EGA|SCI)\s*Remake.*', ''),  # Remove VGA/EGA Remake suffixes
    (r'\s*\([^)]+\)\s*$', ''),  # Remove trailing parentheticals
    (r'\s*[-–—]\s*Enhanced Edition.*', ''),
    (r'[^\w\s]', ''),  # Remove punctuation
    (r'\s+', ' '),  # Normalize whitespace
]


class TitleExtractor(HTMLParser):
    """Extract title and h1 from HTML."""
    
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_h1 = False
        self.title = None
        self.h1 = None
        self.og_title = None
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'title':
            self.in_title = True
        elif tag == 'h1':
            self.in_h1 = True
        elif tag == 'meta':
            if attrs_dict.get('property') == 'og:title':
                self.og_title = attrs_dict.get('content')
                
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'h1':
            self.in_h1 = False
            
    def handle_data(self, data):
        if self.in_title and not self.title:
            self.title = data.strip()
        elif self.in_h1 and not self.h1:
            self.h1 = data.strip()


def normalize_name(name: str) -> str:
    """Normalize game name for comparison."""
    name = name.lower()
    for pattern, replacement in NORMALIZE_PATTERNS:
        name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
    return name.strip()


def extract_expected_name(filepath: Path) -> str:
    """Extract expected game name from file path or frontmatter."""
    # Try frontmatter title first
    try:
        content = filepath.read_text(encoding='utf-8')
        title_match = re.search(r'^title:\s*["\']?([^"\'\n]+)["\']?\s*$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
    except:
        pass
    
    # Fall back to filename (remove year prefix like "1990 - ")
    name = filepath.stem
    name = re.sub(r'^\d{4}\s*[-–—]\s*', '', name)
    return name


def similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def extract_urls(content: str, pattern: str) -> list:
    """Extract URLs matching pattern from content."""
    return list(set(re.findall(pattern, content)))


def fetch_with_scraperapi(url: str, timeout: int = 30) -> tuple:
    """
    Fetch URL via ScraperAPI.
    Returns (success, content_or_error, final_url)
    """
    if not SCRAPERAPI_KEY:
        return (False, "SCRAPERAPI_KEY not set", None)
    
    params = urllib.parse.urlencode({
        'api_key': SCRAPERAPI_KEY,
        'url': url,
        'render': 'false',  # Don't need JS rendering for GOG/Steam
    })
    
    api_url = f"{SCRAPERAPI_URL}?{params}"
    
    try:
        req = urllib.request.Request(
            api_url,
            headers={'Accept': 'text/html'}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read().decode('utf-8', errors='replace')
            final_url = response.geturl()
            return (True, content, final_url)
            
    except urllib.error.HTTPError as e:
        return (False, f'HTTP {e.code}', None)
    except urllib.error.URLError as e:
        return (False, f'URL Error: {e.reason}', None)
    except Exception as e:
        return (False, str(e), None)


def extract_page_title(html: str, url: str) -> str:
    """Extract the most relevant title from HTML."""
    parser = TitleExtractor()
    try:
        parser.feed(html)
    except:
        pass
    
    # For GOG Dreamlist, prefer og:title or h1
    if 'dreamlist' in url:
        if parser.og_title:
            # GOG Dreamlist og:title is usually "Game Name"
            return parser.og_title
        if parser.h1:
            return parser.h1
    
    # For GOG store pages
    if 'gog.com/game' in url or 'gog.com/en/game' in url:
        if parser.og_title:
            return parser.og_title
            
    # For Steam
    if 'steampowered.com' in url:
        if parser.og_title:
            return parser.og_title
    
    # Fall back to title tag
    if parser.title:
        # Clean up common suffixes
        title = parser.title
        title = re.sub(r'\s*[-|]\s*GOG\.com.*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*on Steam$', '', title, flags=re.IGNORECASE)
        return title
    
    return None


def check_url_with_content(url: str, expected_name: str, timeout: int = 30) -> dict:
    """
    Check URL validity and content match.
    Returns dict with status, found_title, similarity, etc.
    """
    result = {
        'url': url,
        'expected': expected_name,
        'valid': False,
        'content_match': False,
        'found_title': None,
        'similarity': 0.0,
        'error': None,
    }
    
    success, content_or_error, final_url = fetch_with_scraperapi(url, timeout)
    
    if not success:
        result['error'] = content_or_error
        return result
    
    # Check for GOG Dreamlist redirect to main page
    if 'dreamlist/game/' in url:
        if 'class="dreamlist__empty"' in content_or_error or \
           '<title>GOG.com Dreamlist</title>' in content_or_error:
            result['error'] = 'Game not found on Dreamlist (empty/redirect)'
            return result
    
    # Extract page title
    found_title = extract_page_title(content_or_error, url)
    result['found_title'] = found_title
    
    if found_title:
        result['valid'] = True
        sim = similarity(expected_name, found_title)
        result['similarity'] = sim
        result['content_match'] = sim >= 0.6  # 60% threshold for fuzzy match
        
        if not result['content_match']:
            result['error'] = f'Content mismatch (similarity: {sim:.0%})'
    else:
        result['valid'] = True  # Page loaded but couldn't extract title
        result['error'] = 'Could not extract page title'
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Validate external links with content verification')
    parser.add_argument('--dreamlist', action='store_true', help='Only check GOG Dreamlist links')
    parser.add_argument('--gog', action='store_true', help='Check all GOG links')
    parser.add_argument('--steam', action='store_true', help='Check Steam links')
    parser.add_argument('--file', type=str, help='Check single file')
    parser.add_argument('--threads', type=int, default=3, help='Number of threads (default: 3)')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--threshold', type=float, default=0.6, help='Similarity threshold (default: 0.6)')
    parser.add_argument('--dry-run', action='store_true', help='List URLs without checking')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    args = parser.parse_args()

    if not SCRAPERAPI_KEY and not args.dry_run:
        print("Error: SCRAPERAPI_KEY environment variable not set", file=sys.stderr)
        print("Get your key at https://www.scraperapi.com/", file=sys.stderr)
        sys.exit(1)

    # Determine which patterns to check
    if args.dreamlist:
        patterns = {'gog_dreamlist': PATTERNS['gog_dreamlist']}
    elif args.gog:
        patterns = {k: v for k, v in PATTERNS.items() if 'gog' in k}
    elif args.steam:
        patterns = {'steam': PATTERNS['steam']}
    else:
        patterns = PATTERNS

    # Collect all URLs with their expected names and source files
    url_data = {}  # url -> {'expected': name, 'files': []}
    
    if args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = Path.cwd() / filepath
        files = [filepath.resolve()]
    else:
        files = list(VAULT_PATH.rglob('*.md'))
    
    print(f"Scanning {len(files)} files...", file=sys.stderr)
    
    for filepath in files:
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            continue
        
        expected_name = extract_expected_name(filepath)
        
        for pattern_name, pattern in patterns.items():
            urls = extract_urls(content, pattern)
            for url in urls:
                if url not in url_data:
                    url_data[url] = {'expected': expected_name, 'files': []}
                try:
                    rel_path = str(filepath.relative_to(VAULT_PATH))
                except ValueError:
                    rel_path = str(filepath)
                url_data[url]['files'].append(rel_path)
    
    print(f"Found {len(url_data)} unique URLs to check", file=sys.stderr)
    
    if args.dry_run:
        print("\nDRY RUN - URLs that would be checked:\n")
        for url, data in sorted(url_data.items()):
            print(f"{url}")
            print(f"  Expected: {data['expected']}")
            print(f"  Files: {', '.join(data['files'][:3])}")
            print()
        return 0
    
    print(f"Using {args.threads} threads, {args.timeout}s timeout", file=sys.stderr)
    print(f"Similarity threshold: {args.threshold:.0%}\n", file=sys.stderr)
    
    # Check URLs
    results = []
    broken = []
    mismatched = []
    valid_count = 0
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(
                check_url_with_content, 
                url, 
                data['expected'], 
                args.timeout
            ): (url, data) 
            for url, data in url_data.items()
        }
        
        for i, future in enumerate(as_completed(futures), 1):
            url, data = futures[future]
            result = future.result()
            result['files'] = data['files']
            results.append(result)
            
            if not result['valid']:
                broken.append(result)
                status = f"✗ BROKEN: {result['error']}"
            elif not result['content_match']:
                mismatched.append(result)
                status = f"⚠ MISMATCH: '{result['found_title']}' ({result['similarity']:.0%})"
            else:
                valid_count += 1
                status = f"✓ OK ({result['similarity']:.0%})"
            
            print(f"[{i}/{len(url_data)}] {status}", file=sys.stderr)
            print(f"    {url[:70]}...", file=sys.stderr)
            
            # Rate limiting for ScraperAPI
            time.sleep(0.5)
    
    # Output
    if args.json:
        print(json.dumps({
            'summary': {
                'total': len(url_data),
                'valid': valid_count,
                'broken': len(broken),
                'mismatched': len(mismatched),
            },
            'broken': broken,
            'mismatched': mismatched,
            'all_results': results,
        }, indent=2))
    else:
        # Summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total URLs checked: {len(url_data)}")
        print(f"Valid & matching:   {valid_count}")
        print(f"Broken links:       {len(broken)}")
        print(f"Content mismatches: {len(mismatched)}")
        
        if broken:
            print("\n" + "=" * 70)
            print("BROKEN LINKS")
            print("=" * 70)
            for r in broken:
                print(f"\n❌ {r['url']}")
                print(f"   Expected: {r['expected']}")
                print(f"   Error: {r['error']}")
                print(f"   Files: {', '.join(r['files'][:3])}")
        
        if mismatched:
            print("\n" + "=" * 70)
            print("CONTENT MISMATCHES")
            print("=" * 70)
            for r in mismatched:
                print(f"\n⚠️  {r['url']}")
                print(f"   Expected: {r['expected']}")
                print(f"   Found:    {r['found_title']}")
                print(f"   Similarity: {r['similarity']:.0%}")
                print(f"   Files: {', '.join(r['files'][:3])}")
    
    return 1 if (broken or mismatched) else 0


if __name__ == '__main__':
    sys.exit(main())
