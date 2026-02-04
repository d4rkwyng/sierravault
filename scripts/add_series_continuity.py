#!/usr/bin/env python3
"""
Add Series Continuity sections to game pages that need them.

Analyzes games in series folders and adds Previous/Next navigation links.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Folders that should have series continuity
SERIES_FOLDERS = {
    'Aces', 'Caesar', 'Civil War Generals', 'Dr. Brain', 'EcoQuest',
    'Empire Earth', 'Gabriel Knight', 'Gobliiins', 'Gold Rush', 'Ground Control',
    'Homeworld', 'Inca', 'Incredible Machine', 'IndyCar', 'INN',
    'Jawbreaker', 'King\'s Quest', 'Krondor', 'Laura Bow', 'Leisure Suit Larry',
    'Lords of Magic', 'Lords of the Realm', 'Manhunter', 'Metaltech', 
    'Mixed Up', 'NASCAR', 'Outpost', 'PGA Championship Golf', 'Phantasmagoria',
    'Pharaoh', 'Playtoons', 'Police Quest', 'Quest for Glory', 'Red Baron',
    'Shivers', 'Sierra Pro Pilot', 'Space Quest', 'Stellar 7', 'SWAT',
    'Thexder', 'Trophy Bass', 'Ultima', 'Ultimate Soccer Manager', 'Zeus',
}


def extract_year(filename):
    """Extract year from filename like '1992 - Game Name.md'."""
    match = re.search(r'^(\d{4})\s*-', filename)
    if match:
        return int(match.group(1))
    return 9999  # Sort to end if no year


def get_display_name(filename):
    """Get display name from filename."""
    # Remove .md extension
    name = filename.replace('.md', '')
    # Remove year prefix
    name = re.sub(r'^\d{4}\s*-\s*', '', name)
    # Remove CXL/TBD prefixes for display
    name = re.sub(r'^(CXL|TBD|TBA)\s*-?\s*', '', name)
    return name.strip()


def has_series_continuity(content):
    """Check if page already has Series Continuity section."""
    return '## Series Continuity' in content or '### Series Continuity' in content


def find_downloads_section(content):
    """Find the position of ## Downloads section."""
    match = re.search(r'^## Downloads', content, re.MULTILINE)
    if match:
        return match.start()
    return -1


def add_series_continuity(filepath, series_folder, all_games, dry_run=False):
    """Add Series Continuity section to a page."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    if has_series_continuity(content):
        return False, "Already has Series Continuity"
    
    # Find current game's position in series
    filename = Path(filepath).name
    current_year = extract_year(filename)
    
    # Sort games by year
    sorted_games = sorted(all_games, key=lambda x: extract_year(x))
    current_idx = None
    for i, game in enumerate(sorted_games):
        if game == filename:
            current_idx = i
            break
    
    if current_idx is None:
        return False, "Could not find game in series"
    
    # Build continuity section
    prev_game = sorted_games[current_idx - 1] if current_idx > 0 else None
    next_game = sorted_games[current_idx + 1] if current_idx < len(sorted_games) - 1 else None
    
    series_name = series_folder.replace("'", "'")  # Normalize apostrophes
    
    lines = [f"\n## Series Continuity\n"]
    lines.append(f"|  | **{series_name} Series** |  |")
    lines.append("|:---:|:---:|:---:|")
    
    # Build Previous/Next row
    if prev_game:
        prev_display = get_display_name(prev_game)
        prev_link = prev_game.replace('.md', '')
        prev_cell = f"**←** [[{prev_link}\\|{prev_display}]]"
    else:
        prev_cell = "**←** First game in series"
    
    if next_game:
        next_display = get_display_name(next_game)
        next_link = next_game.replace('.md', '')
        next_cell = f"[[{next_link}\\|{next_display}]] **→**"
    else:
        next_cell = "Final game in series **→**"
    
    lines.append(f"| {prev_cell} | {next_cell} |  |")
    lines.append("")
    
    continuity_section = '\n'.join(lines)
    
    # Find where to insert (before ## Downloads)
    downloads_pos = find_downloads_section(content)
    if downloads_pos == -1:
        # No Downloads section, add before ## References
        references_match = re.search(r'^## References', content, re.MULTILINE)
        if references_match:
            downloads_pos = references_match.start()
        else:
            return False, "Could not find insertion point"
    
    # Insert the section
    new_content = content[:downloads_pos] + continuity_section + content[downloads_pos:]
    
    if dry_run:
        print(f"Would add to {filepath}")
        return True, "Would add (dry run)"
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    # Update timestamp
    today = datetime.now().strftime('%Y-%m-%d')
    today_display = datetime.now().strftime('%B %d, %Y')
    
    # Read again and update timestamps
    with open(filepath, 'r') as f:
        new_content = f.read()
    
    new_content = re.sub(
        r'last_updated:\s*"?\d{4}-\d{2}-\d{2}"?',
        f'last_updated: "{today}"',
        new_content
    )
    new_content = re.sub(
        r'Last updated:\s*\w+\s+\d+,\s+\d{4}',
        f'Last updated: {today_display}',
        new_content
    )
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    return True, "Added Series Continuity"


def process_series_folder(folder_path, dry_run=False):
    """Process all games in a series folder."""
    folder = Path(folder_path)
    if not folder.exists():
        return
    
    # Get all .md files
    games = [f.name for f in folder.glob('*.md')]
    if len(games) < 2:
        print(f"Skipping {folder.name} (only {len(games)} game)")
        return
    
    series_name = folder.name
    added = 0
    
    for game in games:
        filepath = folder / game
        success, msg = add_series_continuity(filepath, series_name, games, dry_run)
        if success:
            added += 1
            print(f"✓ {game}: {msg}")
    
    if added > 0:
        print(f"Added continuity to {added} games in {series_name}")


def main():
    parser = argparse.ArgumentParser(description="Add Series Continuity sections to game pages")
    parser.add_argument('--folder', help="Process specific folder")
    parser.add_argument('--all', action='store_true', help="Process all series folders")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be done without making changes")
    args = parser.parse_args()
    
    games_dir = Path(__file__).parent.parent.parent / 'Games'
    
    if args.folder:
        folder_path = games_dir / args.folder
        if folder_path.exists():
            process_series_folder(folder_path, args.dry_run)
        else:
            print(f"Folder not found: {folder_path}")
            sys.exit(1)
    elif args.all:
        for series in sorted(SERIES_FOLDERS):
            folder_path = games_dir / series
            if folder_path.exists():
                process_series_folder(folder_path, args.dry_run)
    else:
        print("Usage: add_series_continuity.py [--folder NAME | --all] [--dry-run]")
        sys.exit(1)


if __name__ == '__main__':
    main()
