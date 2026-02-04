#!/usr/bin/env python3
"""
Find duplicate references in game pages.

Scans all markdown files for reference definitions and identifies pages
where the same URL appears multiple times with different reference numbers.
"""

import os
import re
from collections import defaultdict
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPT_DIR.parent
VAULT_DIR = INTERNAL_DIR.parent
GAMES_DIR = VAULT_DIR / "Games"

# Regex patterns
REF_PATTERN = re.compile(r'^\[\^ref-(\d+)\]:\s*\[([^\]]+)\]\(([^)]+)\)')
INLINE_REF_PATTERN = re.compile(r'\[\^ref-(\d+)\]')


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (remove trailing slashes, www, etc.)."""
    url = url.lower().strip()
    url = url.rstrip('/')
    url = re.sub(r'^https?://(www\.)?', '', url)
    return url


def find_duplicates_in_file(filepath: Path) -> dict:
    """Find duplicate URLs in a single markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # Extract all reference definitions
    refs = {}  # ref_num -> (title, url, line_num)
    url_to_refs = defaultdict(list)  # normalized_url -> [(ref_num, title, url)]

    for line_num, line in enumerate(lines, 1):
        match = REF_PATTERN.match(line.strip())
        if match:
            ref_num = int(match.group(1))
            title = match.group(2)
            url = match.group(3)
            refs[ref_num] = (title, url, line_num)
            normalized = normalize_url(url)
            url_to_refs[normalized].append((ref_num, title, url))

    # Find URLs that appear multiple times
    duplicates = {}
    for norm_url, ref_list in url_to_refs.items():
        if len(ref_list) > 1:
            duplicates[norm_url] = ref_list

    return duplicates, refs, content


def count_ref_usages(content: str, ref_num: int) -> int:
    """Count how many times a reference is used in the document."""
    pattern = re.compile(rf'\[\^ref-{ref_num}\]')
    return len(pattern.findall(content))


def scan_all_games():
    """Scan all game markdown files for duplicate references."""
    results = []

    for root, dirs, files in os.walk(GAMES_DIR):
        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = Path(root) / filename
            duplicates, refs, content = find_duplicates_in_file(filepath)

            if duplicates:
                # Get relative path from Games dir
                rel_path = filepath.relative_to(GAMES_DIR)

                dup_info = []
                for norm_url, ref_list in duplicates.items():
                    refs_detail = []
                    for ref_num, title, url in ref_list:
                        usages = count_ref_usages(content, ref_num)
                        refs_detail.append({
                            'ref_num': ref_num,
                            'title': title,
                            'url': url,
                            'usages': usages
                        })
                    dup_info.append({
                        'url': ref_list[0][2],  # Original URL from first ref
                        'refs': refs_detail
                    })

                results.append({
                    'file': str(rel_path),
                    'filepath': str(filepath),
                    'duplicates': dup_info,
                    'total_refs': len(refs)
                })

    return results


def print_report(results):
    """Print a formatted report of duplicate references."""
    if not results:
        print("No duplicate references found!")
        return

    print(f"\n{'='*80}")
    print(f"DUPLICATE REFERENCES REPORT")
    print(f"{'='*80}")
    print(f"\nFound {len(results)} files with duplicate references:\n")

    total_duplicates = 0

    for item in sorted(results, key=lambda x: len(x['duplicates']), reverse=True):
        print(f"\n{'-'*80}")
        print(f"FILE: {item['file']}")
        print(f"Total refs: {item['total_refs']}, Duplicate URLs: {len(item['duplicates'])}")

        for dup in item['duplicates']:
            total_duplicates += len(dup['refs']) - 1  # -1 because one is the "original"
            print(f"\n  URL: {dup['url'][:70]}...")
            print(f"  Used in refs:")
            for ref in dup['refs']:
                print(f"    [^ref-{ref['ref_num']}] \"{ref['title']}\" - used {ref['usages']} times")

    print(f"\n{'='*80}")
    print(f"SUMMARY: {len(results)} files, {total_duplicates} duplicate refs to consolidate")
    print(f"{'='*80}")


def generate_fix_suggestions(results):
    """Generate suggestions for fixing duplicate references."""
    print(f"\n{'='*80}")
    print(f"FIX SUGGESTIONS")
    print(f"{'='*80}")

    for item in results:
        print(f"\n{item['file']}:")
        for dup in item['duplicates']:
            # Suggest keeping the ref with most usages
            refs_sorted = sorted(dup['refs'], key=lambda x: x['usages'], reverse=True)
            keep_ref = refs_sorted[0]
            remove_refs = refs_sorted[1:]

            print(f"\n  Keep [^ref-{keep_ref['ref_num']}] ({keep_ref['usages']} usages)")
            for ref in remove_refs:
                print(f"  Replace [^ref-{ref['ref_num']}] -> [^ref-{keep_ref['ref_num']}] ({ref['usages']} usages)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Find duplicate references in game pages')
    parser.add_argument('--fix', action='store_true', help='Show fix suggestions')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    print("Scanning game pages for duplicate references...")
    results = scan_all_games()

    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print_report(results)
        if args.fix and results:
            generate_fix_suggestions(results)
