#!/usr/bin/env python3
"""
Fix duplicate references in game pages.

Consolidates duplicate URLs to use a single reference number and
optionally renumbers all references to be sequential.
"""

import os
import re
from collections import defaultdict
from pathlib import Path
import argparse

# Paths
SCRIPT_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPT_DIR.parent
VAULT_DIR = INTERNAL_DIR.parent
GAMES_DIR = VAULT_DIR / "Games"


def normalize_url(url: str) -> str:
    """Normalize URL for comparison."""
    url = url.lower().strip()
    url = url.rstrip('/')
    url = re.sub(r'^https?://(www\.)?', '', url)
    return url


def find_duplicates_in_file(content: str) -> dict:
    """Find duplicate URLs in content."""
    lines = content.split('\n')

    # Pattern to match reference definitions
    ref_pattern = re.compile(r'^\[\^ref-(\d+)\]:\s*\[([^\]]+)\]\(([^)]+)\)')

    refs = {}  # ref_num -> (title, url, line_num)
    url_to_refs = defaultdict(list)  # normalized_url -> [(ref_num, title, url)]

    for line_num, line in enumerate(lines):
        match = ref_pattern.match(line.strip())
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

    return duplicates, refs


def count_ref_usages(content: str, ref_num: int) -> int:
    """Count how many times a reference is used in the document."""
    pattern = re.compile(rf'\[\^ref-{ref_num}\]')
    return len(pattern.findall(content))


def fix_duplicates_in_content(content: str, duplicates: dict) -> tuple[str, int]:
    """
    Fix duplicate references in content.

    Returns tuple of (fixed_content, num_fixes).
    """
    if not duplicates:
        return content, 0

    num_fixes = 0

    for norm_url, ref_list in duplicates.items():
        # Determine which ref to keep (most usages, or lowest number if tied)
        refs_with_counts = []
        for ref_num, title, url in ref_list:
            count = count_ref_usages(content, ref_num)
            refs_with_counts.append((ref_num, title, url, count))

        # Sort by usage count (descending), then by ref number (ascending)
        refs_with_counts.sort(key=lambda x: (-x[3], x[0]))
        keep_ref = refs_with_counts[0]
        remove_refs = refs_with_counts[1:]

        # Replace usages of duplicate refs with the kept ref
        for ref_num, title, url, count in remove_refs:
            # IMPORTANT: Remove the definition line FIRST before replacing inline citations
            # Otherwise the inline replacement will also change the definition line
            def_pattern = rf'^\[\^ref-{ref_num}\]:.*$\n?'
            content = re.sub(def_pattern, '', content, flags=re.MULTILINE)

            if count > 0:
                # Replace inline citations (use negative lookahead to skip definitions)
                pattern = rf'\[\^ref-{ref_num}\](?!:)'
                replacement = f'[^ref-{keep_ref[0]}]'
                content = re.sub(pattern, replacement, content)
                num_fixes += 1

    return content, num_fixes


def renumber_refs(content: str) -> str:
    """Renumber all references to be sequential starting from 1."""
    # Find all ref definitions
    ref_pattern = re.compile(r'\[\^ref-(\d+)\]')
    def_pattern = re.compile(r'^\[\^ref-(\d+)\]:', re.MULTILINE)

    # Get all unique ref numbers used
    all_refs = set()
    for match in ref_pattern.finditer(content):
        all_refs.add(int(match.group(1)))

    # Create mapping from old to new numbers
    sorted_refs = sorted(all_refs)
    ref_map = {old: new for new, old in enumerate(sorted_refs, 1)}

    if not ref_map:
        return content

    # Replace references in reverse order (highest first) to avoid conflicts
    for old_num in sorted(ref_map.keys(), reverse=True):
        new_num = ref_map[old_num]
        if old_num != new_num:
            # Use a temporary placeholder to avoid conflicts
            content = re.sub(
                rf'\[\^ref-{old_num}\]',
                f'[^ref-TEMP{new_num}]',
                content
            )

    # Replace all temp placeholders with final numbers
    content = re.sub(r'\[\^ref-TEMP(\d+)\]', r'[^ref-\1]', content)

    return content


def process_file(filepath: Path, dry_run: bool = True, renumber: bool = False) -> tuple[bool, int]:
    """
    Process a single file to fix duplicate references.

    Returns tuple of (was_modified, num_fixes).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    duplicates, refs = find_duplicates_in_file(original_content)

    if not duplicates:
        return False, 0

    fixed_content, num_fixes = fix_duplicates_in_content(original_content, duplicates)

    if renumber:
        fixed_content = renumber_refs(fixed_content)

    if fixed_content == original_content:
        return False, 0

    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

    return True, num_fixes


def scan_and_fix_all(dry_run: bool = True, renumber: bool = False):
    """Scan and fix all game markdown files."""
    results = []
    total_fixes = 0
    total_files_modified = 0

    for root, dirs, files in os.walk(GAMES_DIR):
        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = Path(root) / filename
            was_modified, num_fixes = process_file(filepath, dry_run, renumber)

            if was_modified:
                rel_path = filepath.relative_to(GAMES_DIR)
                results.append((str(rel_path), num_fixes))
                total_fixes += num_fixes
                total_files_modified += 1

    return results, total_fixes, total_files_modified


def main():
    parser = argparse.ArgumentParser(
        description='Fix duplicate references in game pages'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Show what would be changed without modifying files (default)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Actually apply the fixes'
    )
    parser.add_argument(
        '--renumber',
        action='store_true',
        help='Also renumber refs to be sequential (1, 2, 3, ...)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Fix a specific file instead of all files'
    )

    args = parser.parse_args()

    dry_run = not args.apply

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            filepath = GAMES_DIR / args.file
        if not filepath.exists():
            print(f"File not found: {args.file}")
            return

        print(f"Processing: {filepath}")
        was_modified, num_fixes = process_file(filepath, dry_run, args.renumber)
        if was_modified:
            action = "Would fix" if dry_run else "Fixed"
            print(f"{action} {num_fixes} duplicate reference(s)")
        else:
            print("No duplicates found")
    else:
        mode = "DRY RUN" if dry_run else "APPLYING FIXES"
        print(f"\n{'='*60}")
        print(f"FIXING DUPLICATE REFERENCES ({mode})")
        print(f"{'='*60}\n")

        results, total_fixes, total_files = scan_and_fix_all(dry_run, args.renumber)

        for filepath, num_fixes in sorted(results):
            action = "Would fix" if dry_run else "Fixed"
            print(f"{action} {num_fixes} duplicate(s) in: {filepath}")

        print(f"\n{'='*60}")
        action = "Would fix" if dry_run else "Fixed"
        print(f"{action} {total_fixes} duplicate references in {total_files} files")
        print(f"{'='*60}")

        if dry_run and total_fixes > 0:
            print("\nRun with --apply to actually fix the files")


if __name__ == "__main__":
    main()
