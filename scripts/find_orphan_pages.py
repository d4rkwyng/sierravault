#!/usr/bin/env python3
"""
Find Orphan Pages

Identifies pages that have no inbound links from other pages in the vault.
These pages may be hard to discover and should be linked from relevant pages.

Usage:
    python3 find_orphan_pages.py
    python3 find_orphan_pages.py --category Games
    python3 find_orphan_pages.py --json  # Output as JSON
"""

import argparse
import json
import os
import re
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path(__file__).parent.parent / 'vault'

# Directories to scan
CONTENT_DIRS = ['Games', 'Designers', 'Developers', 'Publishers', 'Guides', 'Series', 'Technology']

# Files that don't need inbound links
EXCLUDED_FILES = [
    'Site Index.md',
    'welcome.md',
    'README.md',
    'CLAUDE.md',
    'CONTRIBUTING.md',
]


def extract_wiki_links(content: str) -> set:
    """Extract all wiki link targets from content."""
    # Match [[path/to/file|Display Text]] or [[path/to/file]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    matches = re.findall(pattern, content)
    
    links = set()
    for match in matches:
        # Normalize: remove any path prefix, just keep basename
        basename = os.path.basename(match.strip())
        # Remove .md extension if present
        if basename.endswith('.md'):
            basename = basename[:-3]
        links.add(basename)
    
    return links


def get_all_pages(vault_path: Path) -> dict:
    """Get all markdown pages in the vault."""
    pages = {}
    
    for content_dir in CONTENT_DIRS:
        dir_path = vault_path / content_dir
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.rglob('*.md'):
            # Use basename without .md as key
            key = md_file.stem
            pages[key] = {
                'path': md_file,
                'category': content_dir,
                'inbound_links': 0,
                'linked_from': [],
            }
    
    # Also check root level files
    for md_file in vault_path.glob('*.md'):
        if md_file.name not in EXCLUDED_FILES:
            key = md_file.stem
            pages[key] = {
                'path': md_file,
                'category': 'Root',
                'inbound_links': 0,
                'linked_from': [],
            }
    
    return pages


def analyze_links(vault_path: Path, pages: dict) -> dict:
    """Analyze all links and count inbound links for each page."""
    # Scan all markdown files
    for content_dir in CONTENT_DIRS + ['']:  # Include root
        dir_path = vault_path / content_dir if content_dir else vault_path
        if not dir_path.exists():
            continue
        
        pattern = '*.md' if not content_dir else '**/*.md'
        for md_file in dir_path.glob(pattern):
            if not content_dir and md_file.name in EXCLUDED_FILES:
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                links = extract_wiki_links(content)
                
                source_name = md_file.stem
                
                for link_target in links:
                    if link_target in pages:
                        pages[link_target]['inbound_links'] += 1
                        pages[link_target]['linked_from'].append(source_name)
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
    
    return pages


def find_orphans(pages: dict, category_filter: str = None) -> list:
    """Find pages with no inbound links."""
    orphans = []
    
    for name, info in pages.items():
        # Apply category filter if specified
        if category_filter and info['category'] != category_filter:
            continue
        
        if info['inbound_links'] == 0:
            orphans.append({
                'name': name,
                'path': str(info['path'].relative_to(VAULT_PATH)),
                'category': info['category'],
            })
    
    return sorted(orphans, key=lambda x: (x['category'], x['name']))


def main():
    parser = argparse.ArgumentParser(description='Find orphan pages')
    parser.add_argument('--category', '-c', help='Filter by category (Games, Designers, etc.)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--threshold', '-t', type=int, default=0, 
                        help='Include pages with <= N inbound links')
    args = parser.parse_args()
    
    # Get all pages
    pages = get_all_pages(VAULT_PATH)
    
    # Analyze links
    pages = analyze_links(VAULT_PATH, pages)
    
    # Find orphans (or pages below threshold)
    orphans = []
    for name, info in pages.items():
        if args.category and info['category'] != args.category:
            continue
        
        if info['inbound_links'] <= args.threshold:
            orphans.append({
                'name': name,
                'path': str(info['path'].relative_to(VAULT_PATH)),
                'category': info['category'],
                'inbound_links': info['inbound_links'],
            })
    
    orphans = sorted(orphans, key=lambda x: (x['category'], x['name']))
    
    if args.json:
        print(json.dumps(orphans, indent=2))
        return
    
    # Pretty print
    print("=" * 80)
    print(f"ORPHAN PAGES REPORT (threshold: {args.threshold} inbound links)")
    print("=" * 80)
    print()
    
    if not orphans:
        print("✅ No orphan pages found!")
        print()
        print("=" * 80)
        return 0
    
    # Group by category
    by_category = defaultdict(list)
    for orphan in orphans:
        by_category[orphan['category']].append(orphan)
    
    for category in sorted(by_category.keys()):
        pages_in_cat = by_category[category]
        print(f"\n{category}/ ({len(pages_in_cat)} orphan{'s' if len(pages_in_cat) != 1 else ''}):")
        print("-" * 40)
        for page in pages_in_cat:
            links_note = f" ({page['inbound_links']} links)" if page['inbound_links'] > 0 else ""
            print(f"  📄 {page['name']}{links_note}")
    
    print()
    print("=" * 80)
    print(f"Total: {len(orphans)} orphan pages")
    print()
    print("Suggestions:")
    print("  - Add links to these pages from Site Index or relevant guides")
    print("  - Add Series Continuity links between related games")
    print("  - Link designers/developers from their games' Development sections")
    print("=" * 80)
    
    return len(orphans)


if __name__ == '__main__':
    exit(main())
