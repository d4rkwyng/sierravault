#!/usr/bin/env python3
"""
Bulk Rename Script

Safely batch rename files using git mv to preserve history.
Updates wiki links in other files after renaming.

Usage:
    python3 bulk_rename.py --dry-run  # Preview changes
    python3 bulk_rename.py --pattern "1983 - " --replace "1984 - " --folder "Games/Arcade"
    python3 bulk_rename.py --csv renames.csv  # Load renames from CSV
"""

import argparse
import csv
import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

VAULT_PATH = Path(__file__).parent.parent / 'vault'


def find_wiki_links_to_file(vault_path: Path, old_name: str) -> List[Path]:
    """Find all files that contain wiki links to the given file."""
    files_with_links = []
    old_stem = Path(old_name).stem  # Without .md
    
    # Pattern to match wiki links (with or without display text)
    pattern = re.compile(rf'\[\[{re.escape(old_stem)}(?:\|[^\]]+)?\]\]')
    
    for md_file in vault_path.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            if pattern.search(content):
                files_with_links.append(md_file)
        except Exception:
            pass
    
    return files_with_links


def update_wiki_links(filepath: Path, old_name: str, new_name: str, dry_run: bool = False) -> bool:
    """Update wiki links from old name to new name."""
    old_stem = Path(old_name).stem
    new_stem = Path(new_name).stem
    
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        
        # Update [[OldName]] -> [[NewName]]
        content = re.sub(
            rf'\[\[{re.escape(old_stem)}\]\]',
            f'[[{new_stem}]]',
            content
        )
        
        # Update [[OldName|Display Text]] -> [[NewName|Display Text]]
        content = re.sub(
            rf'\[\[{re.escape(old_stem)}\|([^\]]+)\]\]',
            rf'[[{new_stem}|\1]]',
            content
        )
        
        if content != original_content:
            if not dry_run:
                filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False


def git_mv(old_path: Path, new_path: Path, dry_run: bool = False) -> bool:
    """Rename file using git mv."""
    if dry_run:
        print(f"  Would rename: {old_path.name} -> {new_path.name}")
        return True
    
    try:
        result = subprocess.run(
            ['git', 'mv', str(old_path), str(new_path)],
            cwd=VAULT_PATH,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"  Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def process_renames(renames: List[Tuple[Path, Path]], dry_run: bool = False) -> Tuple[int, int]:
    """Process a list of renames."""
    success = 0
    failed = 0
    
    for old_path, new_path in renames:
        print(f"\nRenaming: {old_path.name}")
        print(f"      To: {new_path.name}")
        
        # Find files that link to this page
        files_with_links = find_wiki_links_to_file(VAULT_PATH, old_path.name)
        
        if files_with_links:
            print(f"  Found {len(files_with_links)} file(s) with links to update")
        
        # Perform rename
        if git_mv(old_path, new_path, dry_run):
            # Update links in other files
            links_updated = 0
            for linked_file in files_with_links:
                if update_wiki_links(linked_file, old_path.name, new_path.name, dry_run):
                    links_updated += 1
            
            if links_updated > 0:
                print(f"  Updated {links_updated} wiki link(s)")
            
            success += 1
        else:
            failed += 1
    
    return success, failed


def collect_pattern_renames(folder: Path, pattern: str, replace: str) -> List[Tuple[Path, Path]]:
    """Collect renames based on pattern matching."""
    renames = []
    
    for md_file in folder.rglob('*.md'):
        filename = md_file.name
        if pattern in filename:
            new_filename = filename.replace(pattern, replace)
            new_path = md_file.parent / new_filename
            renames.append((md_file, new_path))
    
    return renames


def load_csv_renames(csv_path: Path) -> List[Tuple[Path, Path]]:
    """Load renames from a CSV file with columns: old_path, new_path"""
    renames = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            old_path = VAULT_PATH / row['old_path']
            new_path = VAULT_PATH / row['new_path']
            
            if old_path.exists():
                renames.append((old_path, new_path))
            else:
                print(f"Warning: File not found: {row['old_path']}")
    
    return renames


def main():
    parser = argparse.ArgumentParser(description='Bulk rename with git mv')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without making them')
    parser.add_argument('--pattern', help='Pattern to find in filenames')
    parser.add_argument('--replace', help='Replacement string')
    parser.add_argument('--folder', help='Folder to search (relative to vault root)')
    parser.add_argument('--csv', help='CSV file with old_path,new_path columns')
    parser.add_argument('--old', help='Single file to rename (old name)')
    parser.add_argument('--new', help='Single file to rename (new name)')
    args = parser.parse_args()
    
    print("=" * 80)
    print("BULK RENAME" + (" (DRY RUN)" if args.dry_run else ""))
    print("=" * 80)
    
    renames = []
    
    # Single file rename
    if args.old and args.new:
        old_path = VAULT_PATH / args.old
        new_path = VAULT_PATH / args.new
        if old_path.exists():
            renames.append((old_path, new_path))
        else:
            print(f"Error: File not found: {args.old}")
            return 1
    
    # Pattern-based rename
    elif args.pattern and args.replace:
        folder = VAULT_PATH / args.folder if args.folder else VAULT_PATH / 'Games'
        renames = collect_pattern_renames(folder, args.pattern, args.replace)
    
    # CSV-based rename
    elif args.csv:
        renames = load_csv_renames(Path(args.csv))
    
    else:
        parser.print_help()
        return 1
    
    if not renames:
        print("\nNo files to rename.")
        return 0
    
    print(f"\nFound {len(renames)} file(s) to rename")
    
    success, failed = process_renames(renames, args.dry_run)
    
    print()
    print("=" * 80)
    print(f"Summary: {success} succeeded, {failed} failed")
    
    if args.dry_run:
        print("\n(This was a dry run. Use without --dry-run to apply changes.)")
    else:
        print("\nRemember to commit changes:")
        print("  git add -A && git commit -m 'Bulk rename: description'")
    
    print("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())
