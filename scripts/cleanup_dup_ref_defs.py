#!/usr/bin/env python3
"""
Cleanup duplicate reference definitions (same ref number defined multiple times).

This fixes files where the same [^ref-N] is defined multiple times with
different titles/descriptions.
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


def find_dup_ref_definitions(content: str) -> dict:
    """Find ref numbers that are defined multiple times."""
    lines = content.split('\n')
    ref_pattern = re.compile(r'^\[\^ref-(\d+)\]:\s*\[([^\]]+)\]\(([^)]+)\)')

    # ref_num -> [(line_num, full_line, title, url)]
    ref_defs = defaultdict(list)

    for line_num, line in enumerate(lines):
        match = ref_pattern.match(line.strip())
        if match:
            ref_num = int(match.group(1))
            title = match.group(2)
            url = match.group(3)
            ref_defs[ref_num].append((line_num, line, title, url))

    # Find refs defined multiple times
    duplicates = {k: v for k, v in ref_defs.items() if len(v) > 1}
    return duplicates


def cleanup_dup_definitions(content: str) -> tuple[str, int]:
    """
    Remove duplicate reference definitions, keeping only the first one.

    Returns (cleaned_content, num_removed).
    """
    duplicates = find_dup_ref_definitions(content)

    if not duplicates:
        return content, 0

    lines = content.split('\n')
    lines_to_remove = set()
    num_removed = 0

    for ref_num, defs in duplicates.items():
        # Keep the first definition, remove the rest
        for line_num, full_line, title, url in defs[1:]:
            lines_to_remove.add(line_num)
            num_removed += 1

    # Remove the duplicate lines
    new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
    return '\n'.join(new_lines), num_removed


def process_file(filepath: Path, dry_run: bool = True) -> tuple[bool, int]:
    """Process a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    duplicates = find_dup_ref_definitions(content)

    if not duplicates:
        return False, 0

    cleaned_content, num_removed = cleanup_dup_definitions(content)

    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

    return True, num_removed


def scan_and_cleanup(dry_run: bool = True):
    """Scan and cleanup all game markdown files."""
    results = []
    total_removed = 0

    for root, dirs, files in os.walk(GAMES_DIR):
        for filename in files:
            if not filename.endswith('.md'):
                continue

            filepath = Path(root) / filename
            was_modified, num_removed = process_file(filepath, dry_run)

            if was_modified:
                rel_path = filepath.relative_to(GAMES_DIR)
                results.append((str(rel_path), num_removed))
                total_removed += num_removed

    return results, total_removed


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Cleanup duplicate reference definitions'
    )
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Show what would be changed (default)')
    parser.add_argument('--apply', action='store_true',
                        help='Actually apply the fixes')
    parser.add_argument('--file', type=str, help='Process a specific file')

    args = parser.parse_args()
    dry_run = not args.apply

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            filepath = GAMES_DIR / args.file
        if not filepath.exists():
            print(f"File not found: {args.file}")
            return

        duplicates = find_dup_ref_definitions(open(filepath).read())
        if duplicates:
            print(f"Found duplicate definitions in {filepath}:")
            for ref_num, defs in duplicates.items():
                print(f"\n  [^ref-{ref_num}] defined {len(defs)} times:")
                for line_num, line, title, url in defs:
                    print(f"    Line {line_num+1}: {title[:50]}...")

            if not dry_run:
                was_modified, num_removed = process_file(filepath, dry_run=False)
                print(f"\nRemoved {num_removed} duplicate definition(s)")
        else:
            print("No duplicate definitions found")
    else:
        mode = "DRY RUN" if dry_run else "APPLYING FIXES"
        print(f"\n{'='*60}")
        print(f"CLEANING UP DUPLICATE DEFINITIONS ({mode})")
        print(f"{'='*60}\n")

        results, total_removed = scan_and_cleanup(dry_run)

        for filepath, num_removed in sorted(results):
            action = "Would remove" if dry_run else "Removed"
            print(f"{action} {num_removed} dup def(s) in: {filepath}")

        print(f"\n{'='*60}")
        action = "Would remove" if dry_run else "Removed"
        print(f"{action} {total_removed} duplicate definitions in {len(results)} files")
        print(f"{'='*60}")

        if dry_run and total_removed > 0:
            print("\nRun with --apply to fix")


if __name__ == "__main__":
    main()
