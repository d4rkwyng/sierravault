#!/usr/bin/env python3
"""
Add last_updated timestamps to game files based on git commit history.
Adds a 'last_updated' field to YAML frontmatter and a visible timestamp after the title.
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

def get_git_last_modified(file_path, repo_root):
    """Get the last git commit date for a file."""
    # Try both the actual path and lowercase variant (macOS case-insensitivity)
    relative_path = file_path.relative_to(repo_root)
    paths_to_try = [
        str(relative_path),
        str(relative_path).replace('Games/', 'games/'),  # Handle case mismatch
    ]

    for path_variant in paths_to_try:
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%aI', '--', path_variant],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                # Parse ISO format and return YYYY-MM-DD
                iso_date = result.stdout.strip()
                # Extract just the date portion (YYYY-MM-DD)
                return iso_date[:10]
        except Exception as e:
            continue

    return None

def format_date_readable(iso_date):
    """Convert YYYY-MM-DD to 'Month Day, Year' format."""
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    return dt.strftime("%B %d, %Y").replace(" 0", " ")  # Remove leading zero from day

def update_file_with_timestamp(file_path, timestamp):
    """Add or update last_updated in YAML and visible timestamp after title."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file has YAML frontmatter
    if not content.startswith('---'):
        return False, "No YAML frontmatter"

    # Find the end of YAML frontmatter
    yaml_end = content.find('\n---', 3)
    if yaml_end == -1:
        return False, "Malformed YAML frontmatter"

    yaml_block = content[4:yaml_end]  # Skip initial '---\n'
    rest_of_file = content[yaml_end + 4:]  # Skip '\n---'

    # Update YAML
    if 'last_updated:' in yaml_block:
        yaml_block = re.sub(
            r'last_updated:\s*"?[\d-]+"?',
            f'last_updated: "{timestamp}"',
            yaml_block
        )
        action = "updated"
    else:
        if 'sierra_lineage:' in yaml_block:
            yaml_block = re.sub(
                r'(sierra_lineage:\s*"[^"]*")',
                f'\\1\nlast_updated: "{timestamp}"',
                yaml_block
            )
        else:
            yaml_block = yaml_block.rstrip() + f'\nlast_updated: "{timestamp}"'
        action = "added"

    # Format readable date for visible timestamp
    readable_date = format_date_readable(timestamp)
    visible_timestamp = f'<small style="color: gray">Last updated: {readable_date}</small>'

    # Update or add visible timestamp after title
    # Pattern: # Title\n followed by optional existing timestamp, then ## Overview or blank line
    timestamp_pattern = r'(# [^\n]+\n)(\s*<small style="color: gray">Last updated: [^<]+</small>\n)?'

    if re.search(timestamp_pattern, rest_of_file):
        rest_of_file = re.sub(
            timestamp_pattern,
            f'\\1\n{visible_timestamp}\n',
            rest_of_file,
            count=1
        )

    # Reconstruct file
    new_content = '---\n' + yaml_block + '\n---' + rest_of_file

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, action

def main():
    vault_path = Path(__file__).parent.parent / 'vault'
    games_path = vault_path / 'Games'

    print("=" * 80)
    print("ADDING GIT TIMESTAMPS TO GAME FILES")
    print("=" * 80)
    print()

    updated_count = 0
    skipped_count = 0
    error_count = 0

    # Find all .md files in Games directory
    for md_file in sorted(games_path.rglob('*.md')):
        relative_path = md_file.relative_to(vault_path)

        # Get git timestamp
        timestamp = get_git_last_modified(md_file, vault_path)

        if not timestamp:
            print(f"  SKIP: {relative_path} (no git history)")
            skipped_count += 1
            continue

        # Update the file
        success, action = update_file_with_timestamp(md_file, timestamp)

        if success:
            print(f"  {action.upper()}: {relative_path} -> {timestamp}")
            updated_count += 1
        else:
            print(f"  ERROR: {relative_path} ({action})")
            error_count += 1

    print()
    print("=" * 80)
    print(f"Summary: {updated_count} updated, {skipped_count} skipped, {error_count} errors")
    print("=" * 80)

if __name__ == '__main__':
    main()
