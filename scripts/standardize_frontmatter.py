#!/usr/bin/env python3
"""
Standardize Frontmatter for SEO & Metadata Enhancement

This script:
1. Audits existing frontmatter for consistency issues
2. Normalizes field values (lineage, genre, platforms)
3. Adds missing fields (description, tags, series, composer, designer)
4. Extracts metadata from page content when missing
5. Generates SEO descriptions from Overview sections

Usage:
    python3 standardize_frontmatter.py                     # Dry run audit
    python3 standardize_frontmatter.py --fix               # Apply fixes
    python3 standardize_frontmatter.py --file "path.md"    # Single file
    python3 standardize_frontmatter.py --series "King's Quest"  # By series
"""

import argparse
import re
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from collections import defaultdict
import textwrap

VAULT_PATH = Path(__file__).parent.parent / 'vault'

# ============================================================================
# NORMALIZATION MAPPINGS
# ============================================================================

# Lineage normalization: map old values to standard values
LINEAGE_MAPPING = {
    'Dynamix': 'Sierra Label (Dynamix)',
    'Impressions': 'Sierra Label (Impressions)',
    'Coktel Vision': 'Sierra Label (Coktel)',
    'Papyrus': 'Sierra Label (Papyrus)',
    'Headgate': 'Sierra Label (Headgate)',
    'Valve': 'Sierra Label (Valve)',
    'Bright Star': 'Sierra Label (Bright Star)',
    'Sierra Attractions': 'Sierra Label (Sierra Attractions)',
    'Sierra Discovery Series': 'Sierra Label (Discovery)',
    'Acquired Studio': 'Acquired Studio',
    'Acquired Studio (Papyrus)': 'Sierra Label (Papyrus)',
    'Subsidiary (Papyrus)': 'Sierra Label (Papyrus)',
    'Third-Party Published': 'Third-Party Published',
    'Distributed by Sierra': 'Third-Party Published',
    'Synergistic': 'Sierra Label (Synergistic)',
    'Post-Sierra': 'Post-Sierra',
    'Spiritual Successor': 'Spiritual Successor',
}

# Genre normalization: map inconsistent genres to standard values
GENRE_MAPPING = {
    # Adventure variants
    'Point-and-click Adventure': 'Adventure',
    'Point-and-Click Adventure': 'Adventure',
    'Adventure/RPG': 'Adventure RPG',
    'Adventure, Role-playing': 'Adventure RPG',
    'Action role-playing': 'Action RPG',
    'Action RPG / Hack & Slash': 'Action RPG',
    'Role-Playing Game': 'RPG',
    'Role-playing Game': 'RPG',
    
    # Simulation variants
    'Flight Simulator': 'Flight Simulation',
    'Combat Flight Simulation': 'Flight Simulation',
    'Flight Simulation / Shoot \'em up': 'Flight Simulation',
    'Tank Simulation': 'Vehicle Simulation',
    'Tank Simulation / Shooter': 'Vehicle Simulation',
    'Tank Simulation / First-Person Shooter': 'Vehicle Simulation',
    'Mech Simulation': 'Vehicle Simulation',
    'Vehicle Simulation / Mech Combat': 'Vehicle Simulation',
    'Submarine Simulation': 'Vehicle Simulation',
    'Racing Simulation': 'Racing',
    'Racing / Combat': 'Racing',
    'Sports Simulation': 'Sports',
    'Sports Management': 'Sports Management',
    'Sports Management Simulation': 'Sports Management',
    'Golf Simulation': 'Sports',
    'Business Simulation': 'Business Simulation',
    'City Building': 'City-Building',
    'City Building Strategy': 'City-Building',
    'City-building simulation': 'City-Building',
    'City-building, Strategy': 'City-Building',
    'Casino Simulation': 'Casino',
    'Gambling/Casino': 'Casino',
    'Gambling/Casino Simulation': 'Casino',
    'Gambling': 'Casino',
    'Casino/Gambling': 'Casino',
    'Casino / Gambling Simulation': 'Casino',
    'Card Game / Casino': 'Casino',
    
    # Strategy variants  
    'Real-time Strategy': 'Real-Time Strategy',
    'Real-time strategy': 'Real-Time Strategy',
    'Real-time tactics': 'Real-Time Tactics',
    'Real-Time Tactics': 'Real-Time Tactics',
    'Turn-based Strategy': 'Turn-Based Strategy',
    'Turn-Based Strategy Wargame': 'Turn-Based Strategy',
    'Strategy/Tactics': 'Turn-Based Strategy',
    'Strategy / Tactics': 'Turn-Based Strategy',
    'Strategy / War Simulation': 'Turn-Based Strategy',
    'Strategy/Business Simulation': 'Business Simulation',
    'Strategy / Business Simulation': 'Business Simulation',
    'Fantasy Strategy': 'Strategy',
    '4X, Turn-based Strategy, City-building': 'Strategy',
    
    # FPS variants
    'First-Person Shooter': 'FPS',
    'First-person shooter': 'FPS',
    'Tactical First-Person Shooter': 'Tactical Shooter',
    'Tactical Shooter': 'Tactical Shooter',
    'First-Person Shooter/Stealth': 'FPS',
    
    # Action variants
    'Action/Platform': 'Action Platformer',
    'Action Platformer': 'Action Platformer',
    'Platform': 'Platformer',
    'Platform/Action': 'Action Platformer',
    'Action, Arcade': 'Arcade',
    'Action, Shooter': 'Shooter',
    'Action/Arcade': 'Arcade',
    'Arcade, Shooter': 'Shooter',
    'Fixed Shooter': 'Shooter',
    'Vertical Scrolling Shooter': 'Shooter',
    'Run and Gun / Shooter': 'Shooter',
    'Space Combat Simulator': 'Space Combat',
    'Space Combat Simulation': 'Space Combat',
    'Survival Horror': 'Horror',
    'Adventure, Horror': 'Horror Adventure',
    
    # Puzzle variants
    'Puzzle Adventure': 'Puzzle',
    'Adventure, Puzzle': 'Puzzle',
    'Adventure/Puzzle': 'Puzzle',
    'Educational Puzzle': 'Educational',
    'Educational Adventure': 'Educational',
    'Adventure, Educational': 'Educational',
    'Educational, Puzzle, Adventure': 'Educational',
    'Educational, Puzzle, Action': 'Educational',
    'Educational / Puzzle': 'Educational',
    'Educational / Puzzle / Racing': 'Educational',
    'Educational Simulation': 'Educational',
    'Educational Action-Adventure': 'Educational',
    'Edutainment': 'Educational',
    'Edutainment/Interactive Book': 'Educational',
    
    # Card/Board games
    'Card Games': 'Card Game',
    'Card/Tile': 'Card Game',
    'Card/Strategy': 'Card Game',
    'Card & Board': 'Card Game',
    'Card Game / Board Game': 'Board Game',
    'Board Games': 'Board Game',
    'Board Game Compilation': 'Board Game',
    'Board Games/Compilation': 'Board Game',
    'Board and Card Games': 'Board Game',
    'Board/Card Game': 'Board Game',
    'Board games, Puzzles': 'Board Game',
    'Strategy/Board Game': 'Board Game',
    'Casino & Card Games': 'Casino',
    'Board game, Card/Tile game': 'Board Game',
    'Chess': 'Board Game',
    'Chess / Strategy / Educational': 'Board Game',
    
    # Pinball
    'Pinball': 'Pinball',
    'Pinball Simulation': 'Pinball',
    'Pinball Compilation': 'Pinball',
    
    # Other
    'Life Simulation': 'Simulation',
    'Action Simulation': 'Simulation',
    'Action, Simulation': 'Simulation',
    'Action/Simulation': 'Simulation',
    'Simulation / Mech Combat': 'Vehicle Simulation',
    'Text Adventure': 'Adventure',
    'Interactive Storybook, Creativity': 'Educational',
    'Creativity / Interactive Storybook': 'Educational',
    'MMORPG': 'MMORPG',
    'RPG': 'RPG',
    'Fighting': 'Fighting',
    'Trivia / Quiz': 'Trivia',
    'Screensaver/Puzzle Collection': 'Puzzle',
    'Puzzle/Card Game': 'Card Game',
    'Puzzle / Card Game': 'Card Game',
    'Puzzle/Mini-Games Collection': 'Puzzle',
    'Puzzle, Board Games': 'Board Game',
    'Puzzle/Board Game Compilation': 'Board Game',
    'Compilation, Puzzle, Strategy': 'Puzzle',
    'Strategy/Puzzle': 'Puzzle',
    'Strategy / Board Games': 'Board Game',
    'Puzzle adventure': 'Puzzle',
    'Card Game/Casino Simulation': 'Casino',
    'Cards / Gambling': 'Casino',
    'Card Game Simulation': 'Card Game',
    'Strategy/Simulation': 'Strategy',
    'Gambling Simulation': 'Casino',
    'City-Building Strategy': 'City-Building',
    'Vehicle simulation': 'Vehicle Simulation',
    'Adventure/Educational': 'Educational',
    'Adventure / RPG Hybrid': 'Adventure RPG',
    'Tactical Simulation': 'Tactical Shooter',
    'Tactical Action': 'Tactical Shooter',
    'Educational / Driving Simulation': 'Educational',
    'Survival Horror / Parody': 'Horror',
    'Action/Shooter': 'Shooter',
    'Sports simulation': 'Sports',
    'Sports/Simulation': 'Sports',
    'Sports Simulation / Educational': 'Sports',
    'Billiards/Sports': 'Sports',
    'Sports/Pool': 'Sports',
    'Sports, Minigolf': 'Sports',
    'Maze/Arcade': 'Arcade',
    'Action, Multiplayer, Deathmatch': 'FPS',
    'Action, Simulation, Strategy': 'Strategy',
    'Strategy/RPG': 'Strategy RPG',
    'Strategy/RPG/Action': 'Strategy RPG',
    'Naval Strategy/Trading Simulation': 'Strategy',
    'Strategy/City-Building Simulation': 'City-Building',
    'Adventure/Action': 'Action Adventure',
    'Action-Adventure / Space Combat Simulation': 'Action Adventure',
    'Arcade Flight Combat Simulator': 'Flight Simulation',
}

# Standard genre values (after normalization)
STANDARD_GENRES = [
    'Adventure', 'Action', 'Action Adventure', 'Action Platformer', 'Action RPG',
    'Adventure RPG', 'Arcade', 'Board Game', 'Business Simulation', 'Card Game',
    'Casino', 'City-Building', 'Educational', 'Fighting', 'Flight Simulation',
    'FPS', 'Horror', 'Horror Adventure', 'MMORPG', 'Pinball', 'Platformer',
    'Puzzle', 'Racing', 'Real-Time Strategy', 'Real-Time Tactics', 'RPG',
    'Shooter', 'Simulation', 'Space Combat', 'Sports', 'Sports Management',
    'Strategy', 'Strategy RPG', 'Tactical Shooter', 'Trivia', 'Turn-Based Strategy',
    'Vehicle Simulation',
]

# Platform normalization
PLATFORM_MAPPING = {
    'MS-DOS': 'DOS',
    'DOS': 'DOS',
    'Windows': 'Windows',
    'Macintosh': 'Mac',
    'Mac': 'Mac',
    'Apple II': 'Apple II',
    'Apple IIgs': 'Apple IIgs',
    'Amiga': 'Amiga',
    'Atari ST': 'Atari ST',
    'Commodore 64': 'C64',
    'C64': 'C64',
    'NES': 'NES',
    'Sega CD': 'Sega CD',
    'PlayStation': 'PlayStation',
    'PlayStation 2': 'PS2',
    'Xbox': 'Xbox',
    'Xbox 360': 'Xbox 360',
    'FM Towns': 'FM Towns',
    'NEC PC-9801': 'PC-98',
    'PC-98': 'PC-98',
    'Linux': 'Linux',
    'Android': 'Android',
    'iOS': 'iOS',
    '3DO': '3DO',
    'Sega Genesis': 'Genesis',
}

# ============================================================================
# EXTRACTION FUNCTIONS
# ============================================================================

def extract_frontmatter(content: str) -> Tuple[Optional[Dict], str, str]:
    """Extract YAML frontmatter from markdown content.
    
    Returns: (frontmatter_dict, yaml_raw, body)
    """
    if not content.startswith('---'):
        return None, '', content
    
    # Find end of frontmatter
    match = re.search(r'\n---\n', content[3:])
    if not match:
        return None, '', content
    
    yaml_raw = content[4:match.start() + 3]
    body = content[match.end() + 4:]
    
    try:
        data = yaml.safe_load(yaml_raw)
        return data, yaml_raw, body
    except yaml.YAMLError:
        return None, yaml_raw, body


def extract_overview_first_paragraph(content: str) -> Optional[str]:
    """Extract the first paragraph from the Overview section."""
    # Find Overview section
    match = re.search(r'^## Overview\s*\n+(.*?)(?=\n##|\n\[|\Z)', content, re.MULTILINE | re.DOTALL)
    if not match:
        return None
    
    overview = match.group(1).strip()
    
    # Get first paragraph (before double newline)
    paragraphs = re.split(r'\n\n+', overview)
    if not paragraphs:
        return None
    
    first_para = paragraphs[0].strip()
    
    # Clean up: remove citations, links, etc.
    first_para = re.sub(r'\[\^ref-\d+\]', '', first_para)
    first_para = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', first_para)  # [[link|text]] -> text
    first_para = re.sub(r'\[\[([^\]]+)\]\]', r'\1', first_para)  # [[link]] -> link
    first_para = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', first_para)  # [text](url) -> text
    first_para = re.sub(r'\s+', ' ', first_para).strip()
    
    return first_para


def generate_description(data: Dict, content: str) -> str:
    """Generate an SEO-friendly description from page data and overview."""
    title = data.get('title', 'Unknown')
    year = data.get('release_year', '')
    developer = data.get('developer', 'Sierra')
    genre = data.get('genre', 'game')
    
    # Clean developer if it has wiki links
    if isinstance(developer, str):
        developer = re.sub(r'\[\[([^\]|]+)\|?([^\]]*)\]\]', lambda m: m.group(2) or m.group(1), developer)
    
    # Try to get first sentence from overview
    overview = extract_overview_first_paragraph(content)
    if overview:
        # Truncate to ~160 chars for SEO
        if len(overview) > 160:
            # Find a good break point
            truncated = overview[:157]
            last_space = truncated.rfind(' ')
            if last_space > 100:
                truncated = truncated[:last_space]
            return truncated + '...'
        return overview
    
    # Fallback: generate from metadata
    if year and developer:
        return f"{title} is a {year} {genre.lower() if isinstance(genre, str) else 'game'} developed by {developer}."
    elif year:
        return f"{title} is a {year} {genre.lower() if isinstance(genre, str) else 'game'}."
    else:
        return f"{title} is a {genre.lower() if isinstance(genre, str) else 'game'}."


def generate_tags(data: Dict) -> List[str]:
    """Generate SEO-friendly tags from page metadata."""
    tags = set()
    
    # Add sierra tag
    tags.add('sierra')
    
    # Genre-based tags
    genre = data.get('genre', '')
    if isinstance(genre, str):
        genre_lower = genre.lower()
        if 'adventure' in genre_lower:
            tags.add('adventure')
        if 'rpg' in genre_lower or 'role-playing' in genre_lower:
            tags.add('rpg')
        if 'puzzle' in genre_lower:
            tags.add('puzzle')
        if 'simulation' in genre_lower:
            tags.add('simulation')
        if 'strategy' in genre_lower:
            tags.add('strategy')
        if 'educational' in genre_lower:
            tags.add('educational')
        if 'racing' in genre_lower:
            tags.add('racing')
        if 'shooter' in genre_lower or 'fps' in genre_lower:
            tags.add('shooter')
    
    # Decade tag
    year = data.get('release_year')
    if isinstance(year, int):
        decade = (year // 10) * 10
        tags.add(f'{decade}s')
    
    # Engine tag
    engine = data.get('engine', '')
    if engine:
        engine_lower = str(engine).lower()
        if 'agi' in engine_lower:
            tags.add('agi')
        elif 'sci' in engine_lower:
            tags.add('sci')
        elif 'dgds' in engine_lower:
            tags.add('dgds')
    
    # Series tag
    series = data.get('series', '')
    if series:
        series_slug = re.sub(r'[^a-z0-9]+', '-', series.lower()).strip('-')
        if series_slug:
            tags.add(series_slug)
    
    # Designer tags (major designers)
    designers = data.get('designer', [])
    if isinstance(designers, list):
        for designer in designers:
            if isinstance(designer, str):
                # Clean wiki links
                name = re.sub(r'\[\[([^\]|]+)\|?([^\]]*)\]\]', lambda m: m.group(2) or m.group(1), designer)
                # Known major designers
                name_lower = name.lower()
                if 'roberta williams' in name_lower:
                    tags.add('roberta-williams')
                elif 'al lowe' in name_lower:
                    tags.add('al-lowe')
                elif 'jane jensen' in name_lower:
                    tags.add('jane-jensen')
                elif 'corey cole' in name_lower or 'lori cole' in name_lower:
                    tags.add('coles')
                elif 'mark crowe' in name_lower or 'scott murphy' in name_lower:
                    tags.add('two-guys')
    
    # Lineage tags
    lineage = data.get('sierra_lineage', '')
    if isinstance(lineage, str):
        lineage_lower = lineage.lower()
        if 'dynamix' in lineage_lower:
            tags.add('dynamix')
        elif 'impressions' in lineage_lower:
            tags.add('impressions')
        elif 'coktel' in lineage_lower:
            tags.add('coktel')
        elif 'valve' in lineage_lower:
            tags.add('valve')
        elif 'papyrus' in lineage_lower:
            tags.add('papyrus')
    
    return sorted(tags)


def extract_series_from_path(filepath: Path) -> Optional[str]:
    """Extract series name from file path."""
    # Games/King's Quest/file.md -> King's Quest
    parts = filepath.parts
    if 'Games' in parts:
        games_idx = parts.index('Games')
        if games_idx + 1 < len(parts) - 1:
            return parts[games_idx + 1]
    return None


def extract_composer_from_content(content: str) -> Optional[List[str]]:
    """Extract composer names from page content."""
    composers = []
    
    # Look for Music/Composer in Game Info callout
    match = re.search(r'\*\*(?:Music|Composer)[:\s]*\*\*\s*(.+?)(?:\n|\[\^)', content)
    if match:
        composer_text = match.group(1).strip()
        # Extract names from wiki links
        links = re.findall(r'\[\[([^\]|]+)\|?([^\]]*)\]\]', composer_text)
        for link, display in links:
            composers.append(display if display else link)
        if not composers:
            composers.append(composer_text)
    
    return composers if composers else None


def normalize_lineage(lineage: str) -> str:
    """Normalize sierra_lineage value."""
    if not lineage:
        return lineage
    return LINEAGE_MAPPING.get(lineage, lineage)


def normalize_genre(genre: str) -> str:
    """Normalize genre value."""
    if not genre:
        return genre
    return GENRE_MAPPING.get(genre, genre)


def normalize_platforms(platforms: List[str]) -> List[str]:
    """Normalize platform names."""
    if not platforms:
        return platforms
    return [PLATFORM_MAPPING.get(p, p) for p in platforms]


def remove_wiki_links_from_yaml(value: Any) -> Any:
    """Remove wiki links from YAML values, preserving display text."""
    if isinstance(value, str):
        # [[Link|Display]] -> Display, [[Link]] -> Link
        return re.sub(r'\[\[([^\]|]+)\|?([^\]]*)\]\]', lambda m: m.group(2) or m.group(1), value)
    elif isinstance(value, list):
        return [remove_wiki_links_from_yaml(item) for item in value]
    return value


# ============================================================================
# MAIN PROCESSING
# ============================================================================

def standardize_frontmatter(filepath: Path, apply_fix: bool = False) -> Dict[str, Any]:
    """Analyze and optionally fix frontmatter for a single file.
    
    Returns a dict with:
        - issues: list of issues found
        - changes: list of changes made/proposed
        - new_frontmatter: the corrected frontmatter (if any changes)
    """
    result = {
        'issues': [],
        'changes': [],
        'new_frontmatter': None,
    }
    
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        result['issues'].append(f"Error reading file: {e}")
        return result
    
    data, yaml_raw, body = extract_frontmatter(content)
    if data is None:
        result['issues'].append("No valid YAML frontmatter")
        return result
    
    original_data = dict(data)
    modified = False
    
    # 1. Normalize sierra_lineage
    if 'sierra_lineage' in data:
        old_lineage = data['sierra_lineage']
        new_lineage = normalize_lineage(old_lineage)
        if new_lineage != old_lineage:
            data['sierra_lineage'] = new_lineage
            result['changes'].append(f"Lineage: '{old_lineage}' → '{new_lineage}'")
            modified = True
    
    # 2. Normalize genre
    if 'genre' in data:
        old_genre = data['genre']
        new_genre = normalize_genre(old_genre)
        if new_genre != old_genre:
            data['genre'] = new_genre
            result['changes'].append(f"Genre: '{old_genre}' → '{new_genre}'")
            modified = True
        
        # Check if genre is now standard
        if new_genre not in STANDARD_GENRES:
            result['issues'].append(f"Non-standard genre remains: '{new_genre}'")
    
    # 3. Normalize platforms
    if 'platforms' in data and isinstance(data['platforms'], list):
        old_platforms = data['platforms']
        new_platforms = normalize_platforms(old_platforms)
        if new_platforms != old_platforms:
            data['platforms'] = new_platforms
            result['changes'].append(f"Platforms normalized")
            modified = True
    
    # 4. Remove wiki links from YAML values
    for key in ['developer', 'publisher', 'designer', 'composer']:
        if key in data:
            old_val = data[key]
            new_val = remove_wiki_links_from_yaml(old_val)
            if new_val != old_val:
                data[key] = new_val
                result['changes'].append(f"Removed wiki links from '{key}'")
                modified = True
    
    # 5. Add missing series from path
    if 'series' not in data or not data['series']:
        series = extract_series_from_path(filepath)
        if series and series not in ['Standalone', 'Cancelled', 'Fan Games', 'Spiritual Successors']:
            data['series'] = series
            result['changes'].append(f"Added series: '{series}'")
            modified = True
    
    # 6. Add composer if found in content
    if ('composer' not in data or not data['composer']) and 'Games' in str(filepath):
        composer = extract_composer_from_content(content)
        if composer:
            data['composer'] = composer
            result['changes'].append(f"Added composer: {composer}")
            modified = True
    
    # 7. Add description
    if 'description' not in data or not data['description']:
        description = generate_description(data, content)
        if description:
            data['description'] = description
            result['changes'].append(f"Added description")
            modified = True
    
    # 8. Add tags
    if 'tags' not in data or not data['tags']:
        tags = generate_tags(data)
        if tags:
            data['tags'] = tags
            result['changes'].append(f"Added tags: {tags}")
            modified = True
    
    if modified:
        result['new_frontmatter'] = data
        
        if apply_fix:
            # Rebuild the file
            new_yaml = yaml.dump(data, allow_unicode=True, default_flow_style=None, sort_keys=False)
            new_content = f"---\n{new_yaml}---\n{body}"
            filepath.write_text(new_content, encoding='utf-8')
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Standardize frontmatter for SEO')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (otherwise dry run)')
    parser.add_argument('--file', '-f', type=str, help='Process single file')
    parser.add_argument('--series', '-s', type=str, help='Process specific series folder')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all details')
    parser.add_argument('--summary', action='store_true', help='Only show summary stats')
    args = parser.parse_args()
    
    print("=" * 80)
    print("FRONTMATTER STANDARDIZATION" + (" (DRY RUN)" if not args.fix else " (APPLYING FIXES)"))
    print("=" * 80)
    print()
    
    files_to_process = []
    
    if args.file:
        files_to_process = [Path(args.file)]
    elif args.series:
        series_path = VAULT_PATH / 'Games' / args.series
        if series_path.exists():
            files_to_process = list(series_path.glob('*.md'))
        else:
            print(f"Series folder not found: {series_path}")
            return 1
    else:
        files_to_process = list((VAULT_PATH / 'Games').rglob('*.md'))
    
    stats = defaultdict(int)
    all_changes = defaultdict(list)
    all_issues = defaultdict(list)
    
    for filepath in sorted(files_to_process):
        result = standardize_frontmatter(filepath, apply_fix=args.fix)
        
        try:
            rel_path = str(filepath.relative_to(VAULT_PATH))
        except ValueError:
            rel_path = str(filepath)
        stats['total'] += 1
        
        if result['changes']:
            stats['modified'] += 1
            all_changes[rel_path] = result['changes']
        
        if result['issues']:
            stats['with_issues'] += 1
            all_issues[rel_path] = result['issues']
    
    # Report
    if not args.summary:
        if all_changes:
            print(f"\n{'CHANGES PROPOSED' if not args.fix else 'CHANGES APPLIED'} ({len(all_changes)} files):\n")
            for path, changes in sorted(all_changes.items()):
                print(f"  {path}:")
                for change in changes:
                    print(f"    ✓ {change}")
        
        if all_issues:
            print(f"\nREMAINING ISSUES ({len(all_issues)} files):\n")
            for path, issues in sorted(all_issues.items()):
                print(f"  {path}:")
                for issue in issues:
                    print(f"    ⚠ {issue}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Total files processed: {stats['total']}")
    print(f"  Files {'modified' if args.fix else 'to modify'}: {stats['modified']}")
    print(f"  Files with remaining issues: {stats['with_issues']}")
    
    if not args.fix and stats['modified'] > 0:
        print(f"\n  Run with --fix to apply changes")
    
    print()
    return 0


if __name__ == '__main__':
    exit(main())
