#!/usr/bin/env python3
"""Generate release information tables from MobyGames research data."""

import json
import re
import sys
from pathlib import Path
from datetime import datetime


def find_mobygames_data(game_folder):
    """Find and load the best MobyGames data file for a game."""
    # Prefer mobygames.json (has full platform data with dates)
    # over mobygames_api.json (may just have platform names)
    for filename in ['mobygames.json', 'mobygames_api.json']:
        file_path = game_folder / filename
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
                # Verify it has useful platform data (dicts with dates)
                platforms = data.get('platforms', [])
                if platforms and len(platforms) > 0 and isinstance(platforms[0], dict):
                    return data
            except (json.JSONDecodeError, IndexError, KeyError):
                continue
    
    # Fall back to any mobygames*.json file
    for file_path in game_folder.glob('mobygames*.json'):
        try:
            data = json.loads(file_path.read_text())
            if data.get('platforms'):
                return data
        except json.JSONDecodeError:
            continue
    
    return None


def format_date(date_str):
    """Format a date string for display."""
    if not date_str:
        return 'Unknown'
    
    try:
        if len(date_str) == 4:
            return date_str
        elif len(date_str) == 7:
            dt = datetime.strptime(date_str, '%Y-%m')
            return dt.strftime('%B %Y')
        elif len(date_str) == 10:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%B %d, %Y')
        else:
            return date_str
    except ValueError:
        return date_str


def extract_platform_releases(data):
    """Extract platform release information from MobyGames data."""
    platforms = data.get('platforms', [])
    credits = data.get('credits', [])
    
    platform_map = {}
    
    for p in platforms:
        # Handle both dict and string format
        if isinstance(p, str):
            name = p
            release_date = ''
        else:
            name = p.get('name', p.get('platform_name', 'Unknown'))
            release_date = p.get('release_date', p.get('first_release_date', ''))
        
        if name not in platform_map:
            platform_map[name] = {
                'platform': name,
                'release_date': release_date,
                'publishers': [],
                'countries': set(),
                'notes': []
            }
        elif release_date and (not platform_map[name]['release_date'] or 
                               release_date < platform_map[name]['release_date']):
            platform_map[name]['release_date'] = release_date
    
    for credit in credits:
        platform = credit.get('platform', '')
        role = credit.get('role', '')
        company = credit.get('company', '')
        countries = credit.get('countries', [])
        
        if platform in platform_map:
            if 'Published by' in role and company:
                if company not in platform_map[platform]['publishers']:
                    platform_map[platform]['publishers'].append(company)
            
            for country in countries:
                platform_map[platform]['countries'].add(country)
    
    releases = list(platform_map.values())
    releases.sort(key=lambda x: x['release_date'] or 'zzzz')
    
    return releases


def generate_release_table(releases, game_title=""):
    """Generate a markdown release table."""
    if not releases:
        return ""
    
    lines = [
        "## Release Information",
        "",
        "| Platform | Release Date | Publisher | Region/Notes |",
        "|----------|--------------|-----------|--------------|"
    ]
    
    for release in releases:
        platform = release['platform']
        date = format_date(release['release_date'])
        
        publishers = release.get('publishers', [])
        publisher = publishers[0] if publishers else ''
        
        countries = release.get('countries', set())
        notes_parts = []
        
        if countries:
            if 'Japan' in countries and len(countries) == 1:
                notes_parts.append('Japan only')
            elif 'Japan' in countries:
                notes_parts.append('Includes Japan')
        
        notes = '; '.join(notes_parts) if notes_parts else ''
        
        lines.append(f"| {platform} | {date} | {publisher} | {notes} |")
    
    return '\n'.join(lines)


def process_game(research_folder, dry_run=True):
    """Process a single game's release information."""
    data = find_mobygames_data(research_folder)
    if not data:
        return False, f"No MobyGames data found in {research_folder.name}"
    
    releases = extract_platform_releases(data)
    if not releases:
        return False, f"No platform data in {research_folder.name}"
    
    game_title = data.get('title', research_folder.name)
    table = generate_release_table(releases, game_title)
    
    if dry_run:
        print(f"\n=== {game_title} ===")
        print(f"Research: {research_folder.name}")
        print(f"Platforms: {len(releases)}")
        print(table)
        return True, table
    
    return True, table


def list_flagships(research_dir):
    """Get flagship game research folders (KQ, SQ, QFG, LSL, PQ, GK)."""
    flagships = []
    patterns = [
        'kings-quest-*', 'king-s-quest-*',
        'space-quest-*', 
        'quest-for-glory-*', 'hero-s-quest-*',
        'leisure-suit-larry-*',
        'police-quest-*',
        'gabriel-knight-*'
    ]
    
    for pattern in patterns:
        flagships.extend(research_dir.glob(pattern))
    
    filtered = []
    skip_terms = ['remake', 'redux', 'vga-remake', 'collection', 'compilation', 
                  'fan', 'agdi', 'infamous', 'retold', 'cancelled', '2015']
    
    for folder in flagships:
        name = folder.name.lower()
        if not any(term in name for term in skip_terms):
            filtered.append(folder)
    
    return sorted(set(filtered))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate release information tables')
    parser.add_argument('--game', type=str, help='Process a specific game research folder')
    parser.add_argument('--flagships', action='store_true', help='Process flagship games only')
    parser.add_argument('--all', action='store_true', help='Process all games')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Preview without writing')
    parser.add_argument('--write', action='store_true', help='Actually write to files')
    
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent.parent
    research_dir = base_dir / 'internal' / 'research' / 'games'
    games_dir = base_dir / 'Games'
    
    if args.write:
        args.dry_run = False
    
    folders_to_process = []
    
    if args.game:
        folder = research_dir / args.game
        if folder.exists():
            folders_to_process = [folder]
        else:
            print(f"Research folder not found: {args.game}")
            return
    elif args.flagships:
        folders_to_process = list_flagships(research_dir)
        print(f"Found {len(folders_to_process)} flagship games")
    elif args.all:
        folders_to_process = [f for f in research_dir.iterdir() if f.is_dir()]
        print(f"Found {len(folders_to_process)} games total")
    else:
        folders_to_process = list_flagships(research_dir)[:5]
        print(f"Showing first 5 flagships (use --flagships for all):")
    
    results = {'success': 0, 'failed': 0, 'skipped': 0}
    
    for folder in folders_to_process:
        success, message = process_game(folder, args.dry_run)
        if success:
            results['success'] += 1
        else:
            results['failed'] += 1
            print(f"  SKIP: {message}")
    
    print(f"\n=== Summary ===")
    print(f"Processed: {results['success']}")
    print(f"Skipped: {results['failed']}")


if __name__ == '__main__':
    main()
