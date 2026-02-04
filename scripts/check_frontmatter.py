#!/usr/bin/env python3
"""
Check Frontmatter Consistency

Validates YAML frontmatter across all game pages:
- Required fields present
- Correct data types
- Valid values for enums (lineage, genre, etc.)
- No wiki links in YAML
- Consistent formatting

Usage:
    python3 check_frontmatter.py
    python3 check_frontmatter.py --fix  # Apply safe fixes
    python3 check_frontmatter.py --category Games
"""

import argparse
import re
import yaml
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path(__file__).parent.parent / 'vault'

# Required fields for game pages
GAME_REQUIRED_FIELDS = [
    'title',
    'release_year',
    'developer',
    'publisher',
    'genre',
    'platforms',
    'sierra_lineage',
]

# Required fields for designer pages (using actual field names from project)
DESIGNER_REQUIRED_FIELDS = [
    'title',  # Used instead of 'name' in this project
]

# Required fields for developer pages (using actual field names from project)
DEVELOPER_REQUIRED_FIELDS = [
    'title',  # Used instead of 'name' in this project
]

# Valid sierra_lineage values
VALID_LINEAGE = [
    'Core Sierra',
    'Sierra Label (Dynamix)',
    'Sierra Label (Impressions)',
    'Sierra Label (Coktel)',
    'Sierra Label (Papyrus)',
    'Sierra Label (Headgate)',
    'Sierra Label (Valve)',
    'Sierra Label (Bright Star)',
    'Sierra Label (Sierra Attractions)',
    'Sierra Label (Discovery)',
    'Sierra Label (Synergistic)',
    'Acquired Studio',
    'Acquired Franchise',
    'Fan Project',
    'Alumni Project',
    'Sierra Published',
    'Third-Party Published',
    'Post-Sierra',
    'Spiritual Successor',
    # Allow some variations
    'Sierra Label',
    'Third Party',
]

# Valid genres (aligned with standardize_frontmatter.py)
VALID_GENRES = [
    'Adventure', 'Action', 'Action Adventure', 'Action-Adventure', 'Action Platformer',
    'Action RPG', 'Adventure RPG', 'Arcade', 'Board Game', 'Business Simulation',
    'Card Game', 'Casino', 'City-Building', 'City Builder', 'Educational',
    'Fighting', 'Flight Simulation', 'FPS', 'Golf', 'Horror', 'Horror Adventure',
    'MMORPG', 'Pinball', 'Platformer', 'Puzzle', 'Racing', 'Real-Time Strategy',
    'Real-Time Tactics', 'Role-Playing', 'RPG', 'Shooter', 'Simulation',
    'Space Combat', 'Sports', 'Sports Management', 'Strategy', 'Strategy RPG',
    'Tactical Shooter', 'Trivia', 'Turn-Based Strategy', 'Vehicle Simulation',
    'Visual Novel',
]


def extract_frontmatter(content: str) -> tuple:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return None, "No YAML frontmatter"
    
    # Find end of frontmatter
    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return None, "Malformed YAML (no closing ---)"
    
    yaml_content = content[4:end_match.start() + 3]
    
    try:
        data = yaml.safe_load(yaml_content)
        return data, None
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"


def check_game_frontmatter(filepath: Path, data: dict) -> list:
    """Check game page frontmatter."""
    issues = []
    
    # Check required fields
    for field in GAME_REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            issues.append(f"Missing required field: {field}")
    
    # Check data types
    if 'release_year' in data:
        year = data['release_year']
        if not isinstance(year, int):
            issues.append(f"release_year should be integer, got {type(year).__name__}")
        elif year < 1979 or year > 2030:
            issues.append(f"release_year out of range: {year}")
    
    if 'platforms' in data:
        platforms = data['platforms']
        if not isinstance(platforms, list):
            issues.append(f"platforms should be list, got {type(platforms).__name__}")
    
    if 'designer' in data and data['designer'] is not None:
        designer = data['designer']
        if not isinstance(designer, list):
            issues.append(f"designer should be list, got {type(designer).__name__}")
    
    # Check for wiki links in values
    for key, value in data.items():
        if isinstance(value, str):
            if '[[' in value or ']]' in value:
                issues.append(f"Wiki link in YAML field '{key}'")
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and ('[[' in item or ']]' in item):
                    issues.append(f"Wiki link in YAML field '{key}'")
    
    # Check sierra_lineage
    if 'sierra_lineage' in data:
        lineage = data['sierra_lineage']
        if lineage and lineage not in VALID_LINEAGE:
            # Check for close matches
            close_matches = [v for v in VALID_LINEAGE if lineage.lower() in v.lower() or v.lower() in lineage.lower()]
            if close_matches:
                issues.append(f"Non-standard lineage '{lineage}' (did you mean '{close_matches[0]}'?)")
            else:
                issues.append(f"Unknown sierra_lineage: '{lineage}'")
    
    # Check genre
    if 'genre' in data:
        genre = data['genre']
        if genre and genre not in VALID_GENRES:
            issues.append(f"Non-standard genre: '{genre}'")
    
    # Check last_updated format
    if 'last_updated' in data:
        date = str(data['last_updated'])
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            issues.append(f"last_updated should be YYYY-MM-DD format, got '{date}'")
    
    return issues


def check_designer_frontmatter(filepath: Path, data: dict) -> list:
    """Check designer page frontmatter."""
    issues = []
    
    for field in DESIGNER_REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            issues.append(f"Missing required field: {field}")
    
    # Check for wiki links
    for key, value in data.items():
        if isinstance(value, str) and ('[[' in value or ']]' in value):
            issues.append(f"Wiki link in YAML field '{key}'")
    
    return issues


def check_developer_frontmatter(filepath: Path, data: dict) -> list:
    """Check developer page frontmatter."""
    issues = []
    
    for field in DEVELOPER_REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            issues.append(f"Missing required field: {field}")
    
    # Check founded year
    if 'founded' in data:
        founded = data['founded']
        if not isinstance(founded, int):
            issues.append(f"founded should be integer, got {type(founded).__name__}")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description='Check frontmatter consistency')
    parser.add_argument('--category', '-c', help='Check only this category')
    parser.add_argument('--fix', action='store_true', help='Apply safe fixes (not implemented)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all files checked')
    args = parser.parse_args()
    
    print("=" * 80)
    print("FRONTMATTER CONSISTENCY CHECK")
    print("=" * 80)
    print()
    
    all_issues = defaultdict(list)
    files_checked = 0
    
    # Check Games
    if not args.category or args.category == 'Games':
        print("Checking Games...")
        for game_file in (VAULT_PATH / 'Games').rglob('*.md'):
            files_checked += 1
            try:
                content = game_file.read_text(encoding='utf-8')
                data, error = extract_frontmatter(content)
                
                if error:
                    all_issues[str(game_file.relative_to(VAULT_PATH))].append(error)
                elif data:
                    issues = check_game_frontmatter(game_file, data)
                    if issues:
                        all_issues[str(game_file.relative_to(VAULT_PATH))].extend(issues)
            except Exception as e:
                all_issues[str(game_file.relative_to(VAULT_PATH))].append(f"Error reading file: {e}")
    
    # Check Designers
    if not args.category or args.category == 'Designers':
        print("Checking Designers...")
        for designer_file in (VAULT_PATH / 'Designers').glob('*.md'):
            files_checked += 1
            try:
                content = designer_file.read_text(encoding='utf-8')
                data, error = extract_frontmatter(content)
                
                if error:
                    all_issues[str(designer_file.relative_to(VAULT_PATH))].append(error)
                elif data:
                    issues = check_designer_frontmatter(designer_file, data)
                    if issues:
                        all_issues[str(designer_file.relative_to(VAULT_PATH))].extend(issues)
            except Exception as e:
                all_issues[str(designer_file.relative_to(VAULT_PATH))].append(f"Error reading file: {e}")
    
    # Check Developers
    if not args.category or args.category == 'Developers':
        print("Checking Developers...")
        for dev_file in (VAULT_PATH / 'Developers').glob('*.md'):
            files_checked += 1
            try:
                content = dev_file.read_text(encoding='utf-8')
                data, error = extract_frontmatter(content)
                
                if error:
                    all_issues[str(dev_file.relative_to(VAULT_PATH))].append(error)
                elif data:
                    issues = check_developer_frontmatter(dev_file, data)
                    if issues:
                        all_issues[str(dev_file.relative_to(VAULT_PATH))].extend(issues)
            except Exception as e:
                all_issues[str(dev_file.relative_to(VAULT_PATH))].append(f"Error reading file: {e}")
    
    # Report
    print()
    print("=" * 80)
    print(f"Checked {files_checked} files")
    print()
    
    if all_issues:
        print(f"Found issues in {len(all_issues)} files:\n")
        for filepath, issues in sorted(all_issues.items()):
            print(f"\n{filepath}:")
            for issue in issues:
                print(f"  ⚠️  {issue}")
    else:
        print("✅ All frontmatter is valid!")
    
    print()
    print("=" * 80)
    
    return len(all_issues)


if __name__ == '__main__':
    exit(main())
