#!/usr/bin/env python3
"""
Generate Series Index Pages

Automatically generates series overview pages for game series folders.
Creates pages in the Series/ directory with timeline, overview, and links.

Usage:
    python3 generate_series_index.py "King's Quest"  # Generate for one series
    python3 generate_series_index.py --all  # Generate for all series
    python3 generate_series_index.py --missing  # Only generate missing ones
"""

import argparse
import os
import re
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path(__file__).parent.parent / 'vault'
GAMES_PATH = VAULT_PATH / 'Games'
SERIES_PATH = VAULT_PATH / 'Series'

# Minimum games to auto-generate a series page
MIN_GAMES_FOR_SERIES = 4

# Series that should be excluded (already have custom pages or shouldn't have one)
EXCLUDED_SERIES = [
    'Standalone', 'Arcade', 'Education', 'Cancelled', 'Fan Games',
    'Spiritual Successors', 'Strategy', 'Coktel', 'Impressions',
    'Dynamix', 'Valve',  # Developer-based folders, not series
]


def extract_game_info(filepath: Path) -> dict:
    """Extract info from a game page."""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        info = {
            'filename': filepath.stem,
            'path': filepath,
        }
        
        # Extract YAML fields
        yaml_patterns = {
            'title': r'^title:\s*["\']?([^"\'\n]+)',
            'release_year': r'^release_year:\s*(\d{4})',
            'developer': r'^developer:\s*["\']?([^"\'\n]+)',
            'genre': r'^genre:\s*["\']?([^"\'\n]+)',
            'engine': r'^engine:\s*["\']?([^"\'\n]+)',
        }
        
        for key, pattern in yaml_patterns.items():
            match = re.search(pattern, content[:2000], re.MULTILINE)
            if match:
                info[key] = match.group(1).strip().strip('"\'')
        
        # Get year from filename if not in YAML
        if 'release_year' not in info:
            year_match = re.match(r'^(\d{4})', filepath.stem)
            if year_match:
                info['release_year'] = year_match.group(1)
        
        return info
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def get_series_games(series_folder: Path) -> list:
    """Get all games in a series folder."""
    games = []
    
    for md_file in series_folder.glob('*.md'):
        info = extract_game_info(md_file)
        if info:
            games.append(info)
    
    # Sort by year
    games.sort(key=lambda x: x.get('release_year', '9999'))
    
    return games


def generate_series_page(series_name: str, games: list) -> str:
    """Generate markdown content for a series overview page."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Calculate stats
    years = [int(g.get('release_year', 0)) for g in games if g.get('release_year')]
    first_year = min(years) if years else 'Unknown'
    last_year = max(years) if years else 'Unknown'
    
    developers = set(g.get('developer', 'Unknown') for g in games)
    genres = set(g.get('genre', 'Unknown') for g in games)
    engines = set(g.get('engine', 'Unknown') for g in games if g.get('engine'))
    
    content = f'''---
title: "{series_name} Series"
first_game: {first_year}
latest_game: {last_year}
total_games: {len(games)}
developers: {list(developers)}
genres: {list(genres)}
last_updated: "{today}"
---

# {series_name} Series

<small style="color: gray">Last updated: {datetime.now().strftime('%B %d, %Y')}</small>

## Overview

The {series_name} series spans {len(games)} games from {first_year} to {last_year}.

<!-- TODO: Add series description here -->

## Timeline

| Year | Title | Developer |
|------|-------|-----------|
'''
    
    # Add games to timeline
    for game in games:
        year = game.get('release_year', '?')
        title = game.get('title', game['filename'])
        filename = game['filename']
        developer = game.get('developer', 'Unknown')
        
        # Escape pipes in wiki links
        wiki_link = f'[[{filename}\\|{title}]]'
        content += f'| {year} | {wiki_link} | {developer} |\n'
    
    # Add engines section if we have engine info
    if engines and 'Unknown' not in engines:
        content += f'''
## Technology

The series has used the following game engines:

'''
        for engine in sorted(engines):
            engine_games = [g for g in games if g.get('engine') == engine]
            years = [g.get('release_year', '?') for g in engine_games]
            content += f'- **{engine}** ({", ".join(sorted(years))})\n'
    
    content += '''
## Related Pages

<!-- TODO: Add links to related designers, developers, guides -->

## References

<!-- TODO: Add references -->

[^ref-1]: [Source](URL) - Description
'''
    
    return content


def main():
    parser = argparse.ArgumentParser(description='Generate series index pages')
    parser.add_argument('series', nargs='?', help='Series name to generate')
    parser.add_argument('--all', action='store_true', help='Generate for all series')
    parser.add_argument('--missing', action='store_true', help='Only generate missing pages')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')
    parser.add_argument('--min-games', type=int, default=MIN_GAMES_FOR_SERIES,
                        help=f'Minimum games for auto-generation (default: {MIN_GAMES_FOR_SERIES})')
    args = parser.parse_args()
    
    print("=" * 80)
    print("SERIES INDEX GENERATOR")
    print("=" * 80)
    print()
    
    # Ensure Series directory exists
    SERIES_PATH.mkdir(exist_ok=True)
    
    # Collect series to process
    series_to_process = []
    
    if args.series:
        # Single series
        series_folder = GAMES_PATH / args.series
        if series_folder.exists():
            series_to_process.append(args.series)
        else:
            print(f"Error: Series folder not found: {args.series}")
            return 1
    
    elif args.all or args.missing:
        # All series folders
        for folder in sorted(GAMES_PATH.iterdir()):
            if not folder.is_dir():
                continue
            
            folder_name = folder.name
            
            # Skip excluded folders
            if folder_name in EXCLUDED_SERIES:
                continue
            
            # Check minimum game count
            games = list(folder.glob('*.md'))
            if len(games) < args.min_games:
                continue
            
            # Check if page already exists (for --missing)
            if args.missing:
                output_path = SERIES_PATH / f"{folder_name} Series.md"
                if output_path.exists():
                    continue
            
            series_to_process.append(folder_name)
    
    else:
        parser.print_help()
        return 1
    
    if not series_to_process:
        print("No series to process.")
        return 0
    
    print(f"Processing {len(series_to_process)} series:\n")
    
    created = 0
    for series_name in series_to_process:
        series_folder = GAMES_PATH / series_name
        games = get_series_games(series_folder)
        
        if len(games) < 2:
            print(f"  ⏭️  {series_name}: Only {len(games)} game(s), skipping")
            continue
        
        content = generate_series_page(series_name, games)
        output_path = SERIES_PATH / f"{series_name} Series.md"
        
        if args.dry_run:
            print(f"  📝 Would create: {output_path.name} ({len(games)} games)")
        else:
            output_path.write_text(content, encoding='utf-8')
            print(f"  ✅ Created: {output_path.name} ({len(games)} games)")
            created += 1
    
    print()
    print("=" * 80)
    if args.dry_run:
        print("(Dry run - no files written)")
    else:
        print(f"Created {created} series index page(s)")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    exit(main())
