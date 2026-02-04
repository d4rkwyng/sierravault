#!/usr/bin/env python3
"""
Validate that references in game pages actually pertain to the game.
Checks if reference URLs/titles mention key words from the game title.
"""

import re
import sys
from pathlib import Path


def extract_title_keywords(title: str) -> set[str]:
    """Extract meaningful keywords from game title."""
    # Remove common words that don't help identify the game
    stopwords = {
        'the', 'a', 'an', 'of', 'in', 'to', 'and', 'or', 'for', 'on', 'at',
        'by', 'with', 'from', 'as', 'is', 'it', 'its', 'be', 'was', 'were',
        'game', 'games', 'sierra', 'online', 'entertainment', 'part', 'chapter',
        'episode', 'vol', 'volume', 'edition', 'deluxe', 'gold', 'platinum',
        'collection', 'anthology', 'pack', 'bundle', 'remake', 'remaster',
        'enhanced', 'definitive', 'complete', 'original', 'classic', 'ultra',
        '3d', 'vga', 'ega', 'cd', 'rom', 'dos', 'windows', 'mac', 'amiga',
    }

    # Clean and split title
    clean = re.sub(r'[^\w\s]', ' ', title.lower())
    words = clean.split()

    # Filter out stopwords and short words
    keywords = {w for w in words if w not in stopwords and len(w) > 2}

    # Also add Roman numerals as Arabic numbers
    roman_map = {'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5',
                 'vi': '6', 'vii': '7', 'viii': '8', 'ix': '9', 'x': '10'}
    for w in list(keywords):
        if w in roman_map:
            keywords.add(roman_map[w])

    return keywords


def extract_references(content: str) -> list[dict]:
    """Extract all references from markdown content."""
    refs = []
    # Match [^ref-N]: [Title](URL) – description
    pattern = r'\[\^ref-(\d+)\]:\s*\[([^\]]*)\]\(([^)]+)\)(?:\s*[–-]\s*(.*))?'

    for match in re.finditer(pattern, content):
        refs.append({
            'num': match.group(1),
            'title': match.group(2),
            'url': match.group(3),
            'desc': match.group(4) or '',
            'full': match.group(0)
        })

    return refs


def check_reference_relevance(ref: dict, keywords: set[str]) -> tuple[bool, str]:
    """Check if a reference seems relevant to the game."""
    # Combine all reference text for checking
    ref_text = f"{ref['title']} {ref['url']} {ref['desc']}".lower()

    # Check if any keyword appears in the reference
    matches = [kw for kw in keywords if kw in ref_text]

    if matches:
        return True, f"matches: {', '.join(matches)}"

    # Check for common game-related sites that are usually relevant
    generic_relevant = [
        'mobygames.com', 'gog.com', 'steam', 'wikipedia.org', 'archive.org',
        'sierrachest.com', 'adventuregamers.com', 'pcgamingwiki.com',
        'igdb.com', 'metacritic.com', 'gamefaqs', 'myabandonware.com',
        'old-games.com', 'filfre.net', 'sierrahelp.com'
    ]

    for site in generic_relevant:
        if site in ref['url'].lower():
            return True, f"trusted game site: {site}"

    return False, "no keyword matches found"


def validate_page(filepath: Path, verbose: bool = False) -> dict:
    """Validate references in a single page."""
    content = filepath.read_text()

    # Extract title from YAML or first heading
    title_match = re.search(r'^title:\s*["\']?([^"\'\n]+)', content, re.MULTILINE)
    if not title_match:
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)

    if not title_match:
        return {'file': str(filepath), 'error': 'Could not extract title'}

    title = title_match.group(1).strip()
    keywords = extract_title_keywords(title)

    if verbose:
        print(f"\nTitle: {title}")
        print(f"Keywords: {keywords}")

    refs = extract_references(content)

    if not refs:
        return {'file': str(filepath), 'title': title, 'error': 'No references found'}

    relevant = []
    irrelevant = []

    for ref in refs:
        is_relevant, reason = check_reference_relevance(ref, keywords)
        if is_relevant:
            relevant.append({'ref': ref, 'reason': reason})
        else:
            irrelevant.append({'ref': ref, 'reason': reason})

    total = len(refs)
    relevance_pct = (len(relevant) / total * 100) if total > 0 else 0

    return {
        'file': str(filepath),
        'title': title,
        'keywords': list(keywords),
        'total_refs': total,
        'relevant': len(relevant),
        'irrelevant': len(irrelevant),
        'relevance_pct': relevance_pct,
        'irrelevant_refs': irrelevant if irrelevant else None
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Validate reference relevance in game pages')
    parser.add_argument('path', nargs='?', help='File or directory to validate')
    parser.add_argument('--threshold', type=float, default=50.0,
                       help='Minimum relevance percentage (default: 50)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show details')
    parser.add_argument('--show-irrelevant', action='store_true',
                       help='Show irrelevant references')
    args = parser.parse_args()

    # Default to Games/ directory
    if args.path:
        target = Path(args.path)
    else:
        target = Path(__file__).parent.parent / 'vault' / 'Games'

    if target.is_file():
        files = [target]
    else:
        files = sorted(target.rglob('*.md'))

    results = []
    problematic = []

    for f in files:
        if f.name.startswith('.') or 'template' in f.name.lower():
            continue

        result = validate_page(f, verbose=args.verbose)
        results.append(result)

        if 'error' not in result and result['relevance_pct'] < args.threshold:
            problematic.append(result)

    # Summary
    print(f"\n{'='*60}")
    print(f"Validated {len(results)} pages")
    print(f"Pages below {args.threshold}% relevance threshold: {len(problematic)}")

    if problematic:
        print(f"\n{'='*60}")
        print("PROBLEMATIC PAGES (low reference relevance):")
        print(f"{'='*60}\n")

        for r in sorted(problematic, key=lambda x: x['relevance_pct']):
            print(f"\n{r['title']}")
            print(f"  File: {r['file']}")
            print(f"  Relevance: {r['relevance_pct']:.1f}% ({r['relevant']}/{r['total_refs']} refs)")
            print(f"  Keywords searched: {', '.join(r['keywords'][:10])}")

            if args.show_irrelevant and r.get('irrelevant_refs'):
                print("  Irrelevant references:")
                for ir in r['irrelevant_refs'][:5]:
                    url = ir['ref']['url'][:60] + '...' if len(ir['ref']['url']) > 60 else ir['ref']['url']
                    print(f"    - [^ref-{ir['ref']['num']}]: {url}")

    return len(problematic)


if __name__ == '__main__':
    sys.exit(main())
