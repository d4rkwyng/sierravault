#!/usr/bin/env python3
"""
Validate internal links in Obsidian vault.
Checks for broken wiki-style [[...]] links across ALL content directories.

Usage:
    python3 validate_links.py           # Check all directories
    python3 validate_links.py --quick   # Check only Guides and Designers
    python3 validate_links.py --dir Games  # Check specific directory
"""

import argparse
import os
import re
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path(__file__).parent.parent / 'vault'

# All content directories to check
CONTENT_DIRS = ['Games', 'Designers', 'Developers', 'Publishers', 'Guides', 'Series', 'Technology']

# Quick mode only checks these (for backward compatibility)
QUICK_DIRS = ['Guides', 'Designers']


def extract_links(content):
    """Extract all wiki-style links from markdown content."""
    # Pattern matches [[path/to/file|Display Text]] or [[path/to/file]]
    pattern = r'\[\[(.*?)\]\]'
    matches = re.findall(pattern, content)

    links = []
    for match in matches:
        # Handle both escaped (\|) and unescaped (|) pipe separators
        # In table cells, pipes are escaped as \| but still act as separator
        if '\\|' in match:
            # Escaped pipe - split on \|
            path = match.split('\\|')[0].strip()
        elif '|' in match:
            # Unescaped pipe - split on |
            path = match.split('|')[0].strip()
        else:
            path = match.strip()
        links.append(path)

    return links


def check_link_exists(base_path, link_path, file_index=None):
    """Check if a link resolves to an existing file."""
    # Try as-is first (relative path with .md extension)
    if link_path.endswith('.md'):
        full_path = base_path / link_path
        if full_path.exists():
            return True, str(full_path)

    # Try adding .md extension
    full_path_md = base_path / f"{link_path}.md"
    if full_path_md.exists():
        return True, str(full_path_md)

    # Try searching from root (for paths like "Games/...")
    if link_path.startswith('Games/') or link_path.startswith('Designers/') or link_path.startswith('Developers/'):
        full_path = base_path / link_path
        if full_path.exists():
            return True, str(full_path)

        full_path_md = base_path / f"{link_path}.md"
        if full_path_md.exists():
            return True, str(full_path_md)

    # Try basename only (Obsidian can link by filename alone)
    basename = os.path.basename(link_path)
    if not basename.endswith('.md'):
        basename_md = f"{basename}.md"
    else:
        basename_md = basename

    # Use index if available (faster)
    if file_index and basename_md in file_index:
        return True, file_index[basename_md]

    # Search for file with this basename anywhere in the vault
    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if basename_md in files:
            return True, str(Path(root) / basename_md)

    return False, None


def extract_headings(content):
    """Extract all headings from markdown content for anchor validation."""
    pattern = r'^#{1,6}\s+(.+)$'
    headings = []
    for line in content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            heading = match.group(1).strip()
            headings.append(heading)
    return headings


def build_file_index(vault_path):
    """Build an index of all markdown files for faster lookup."""
    index = {}
    for root, dirs, files in os.walk(vault_path):
        # Skip hidden directories and internal
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'internal']
        for f in files:
            if f.endswith('.md'):
                index[f] = str(Path(root) / f)
    return index


def validate_file_links(file_path, vault_path, file_index=None):
    """Validate all links in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [], [f"Error reading file: {e}"], []

    links = extract_links(content)
    headings = extract_headings(content)
    broken_links = []

    for link in links:
        # Handle anchor links (links to headings in same file)
        if link.startswith('#'):
            anchor_target = link[1:]
            heading_matches = [h for h in headings if h.lower() == anchor_target.lower()]
            if not heading_matches:
                broken_links.append(link)
        else:
            exists, resolved_path = check_link_exists(vault_path, link, file_index)
            if not exists:
                broken_links.append(link)

    # Check for curly quotes
    curly_issues = check_curly_quotes(content)

    return links, broken_links, curly_issues


def check_curly_quotes(content):
    """Check for curly quotes in links that won't match filenames."""
    issues = []
    link_pattern = r'\[\[([^\]]+)\]\]'
    matches = re.findall(link_pattern, content)
    for match in matches:
        if ''' in match or ''' in match or '"' in match or '"' in match:
            issues.append(f"Curly quote in: [[{match[:40]}...]]")
    return issues


def main():
    parser = argparse.ArgumentParser(description='Validate wiki links')
    parser.add_argument('--quick', action='store_true', help='Only check Guides and Designers')
    parser.add_argument('--dir', help='Check specific directory only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all files checked')
    args = parser.parse_args()

    print("=" * 80)
    print("LINK VALIDATION REPORT")
    print("=" * 80)
    print()

    # Build file index for faster lookup
    print("Building file index...")
    file_index = build_file_index(VAULT_PATH)
    print(f"Indexed {len(file_index)} markdown files\n")

    # Determine which directories to check
    if args.dir:
        dirs_to_check = [args.dir]
    elif args.quick:
        dirs_to_check = QUICK_DIRS
    else:
        dirs_to_check = CONTENT_DIRS

    all_broken = defaultdict(list)
    curly_issues = defaultdict(list)
    total_links = 0
    total_broken = 0
    files_checked = 0

    for dir_name in dirs_to_check:
        dir_path = VAULT_PATH / dir_name
        if not dir_path.exists():
            print(f"Directory not found: {dir_name}")
            continue

        print(f"Checking {dir_name}/...")

        for md_file in sorted(dir_path.rglob('*.md')):
            files_checked += 1
            rel_path = md_file.relative_to(VAULT_PATH)

            links, broken, curly = validate_file_links(md_file, VAULT_PATH, file_index)

            total_links += len(links)
            total_broken += len(broken)

            if broken:
                all_broken[str(rel_path)] = broken

            if curly:
                curly_issues[str(rel_path)] = curly

            if args.verbose and links:
                status = "✅" if not broken else f"❌ {len(broken)} broken"
                print(f"  {rel_path}: {len(links)} links {status}")

    # Also check root-level files
    print("Checking root files...")
    for md_file in sorted(VAULT_PATH.glob('*.md')):
        if md_file.name in ['README.md', 'CLAUDE.md', 'CONTRIBUTING.md']:
            continue
        files_checked += 1
        links, broken, curly = validate_file_links(md_file, VAULT_PATH, file_index)
        total_links += len(links)
        total_broken += len(broken)
        if broken:
            all_broken[md_file.name] = broken
        if curly:
            curly_issues[md_file.name] = curly

    # Print results
    print()
    print("=" * 80)
    print(f"Checked {files_checked} files, {total_links} total links")
    print()

    if all_broken:
        print(f"❌ Found {total_broken} broken links in {len(all_broken)} files:\n")

        for file_path, broken_links in sorted(all_broken.items()):
            print(f"\n{file_path}:")
            for link in broken_links:
                print(f"  ❌ [[{link}]]")
    else:
        print(f"✅ All {total_links} links validated successfully!")
        print("No broken links found.")

    # Print curly quote warnings
    if curly_issues:
        print("\n⚠️  CURLY QUOTE WARNINGS (may cause link issues):")
        for filepath, issues in sorted(curly_issues.items()):
            print(f"\n{filepath}:")
            for issue in issues:
                print(f"  ⚠️  {issue}")

    print("\n" + "=" * 80)

    return len(all_broken) + len(curly_issues)


if __name__ == '__main__':
    exit(main())
