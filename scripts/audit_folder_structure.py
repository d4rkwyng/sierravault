#!/usr/bin/env python3
"""
Audit Folder Structure

Validates naming conventions across the vault:
- Game files follow YYYY - Title.md format
- Series folders are properly organized
- No orphaned games that should be in series folders
- Consistent capitalization

Usage:
    python3 audit_folder_structure.py
    python3 audit_folder_structure.py --fix  # Apply safe fixes
"""

import argparse
import os
import re
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path(__file__).parent.parent / 'vault'
GAMES_PATH = VAULT_PATH / 'Games'

# Valid prefixes for special game types
VALID_PREFIXES = ['CXL', 'TBD', 'TBA']

# Year range for valid game years
MIN_YEAR = 1979
MAX_YEAR = 2030


def check_game_filename(filepath: Path) -> list:
    """Check if a game filename follows conventions."""
    issues = []
    filename = filepath.stem  # Without .md extension
    
    # Check for special prefixes
    has_prefix = False
    for prefix in VALID_PREFIXES:
        if filename.startswith(f'{prefix} - ') or filename.startswith(f'{prefix}-'):
            has_prefix = True
            # Remove prefix for further checks
            filename = re.sub(f'^{prefix}\\s*-\\s*', '', filename)
            break
    
    # Check for YYYY - Title format
    year_match = re.match(r'^(\d{4})\s*-\s*(.+)$', filename)
    
    if not year_match and not has_prefix:
        # TBD/TBA games might not have year
        if not any(filename.startswith(p) for p in VALID_PREFIXES):
            issues.append(f"Missing year prefix: {filepath.name}")
    elif year_match:
        year = int(year_match.group(1))
        title = year_match.group(2)
        
        if year < MIN_YEAR or year > MAX_YEAR:
            issues.append(f"Invalid year {year}: {filepath.name}")
        
        # Check for curly quotes in title
        if ''' in title or ''' in title or '"' in title or '"' in title:
            issues.append(f"Curly quotes in title: {filepath.name}")
        
        # Check for redundant year in title
        if re.search(r'\(\d{4}\)$', title):
            issues.append(f"Redundant year in parentheses: {filepath.name}")
    
    return issues


def check_series_organization(games_path: Path) -> list:
    """Check if games are properly organized into series folders."""
    issues = []
    
    # Track games by series (from YAML frontmatter)
    series_games = defaultdict(list)
    folder_games = defaultdict(list)
    
    for folder in games_path.iterdir():
        if not folder.is_dir():
            continue
        
        for game_file in folder.glob('*.md'):
            folder_games[folder.name].append(game_file)
            
            # Read YAML to get series
            try:
                content = game_file.read_text(encoding='utf-8')
                series_match = re.search(r'^series:\s*["\']?([^"\'\n]+)', content, re.MULTILINE)
                if series_match:
                    series = series_match.group(1).strip()
                    series_games[series].append(game_file)
            except Exception:
                pass
    
    # Check for series with games in multiple folders
    for series, games in series_games.items():
        folders_containing = set(g.parent.name for g in games)
        if len(folders_containing) > 1 and series != 'Standalone':
            issues.append(
                f"Series '{series}' has games in multiple folders: {', '.join(sorted(folders_containing))}"
            )
    
    # Check for potential series in Standalone
    standalone_games = folder_games.get('Standalone', [])
    for game in standalone_games:
        try:
            content = game.read_text(encoding='utf-8')
            series_match = re.search(r'^series:\s*["\']?([^"\'\n]+)', content, re.MULTILINE)
            if series_match:
                series = series_match.group(1).strip()
                # Check if a series folder exists
                if series and series != 'Standalone':
                    potential_folder = games_path / series
                    if potential_folder.exists():
                        issues.append(
                            f"Game '{game.name}' in Standalone but series folder '{series}' exists"
                        )
        except Exception:
            pass
    
    return issues


def check_folder_naming(games_path: Path) -> list:
    """Check folder naming conventions."""
    issues = []
    
    for folder in sorted(games_path.iterdir()):
        if not folder.is_dir():
            continue
        
        folder_name = folder.name
        
        # Check for consistent capitalization (Title Case)
        words = folder_name.replace('-', ' ').replace("'", ' ').split()
        for word in words:
            # Skip small words that might be lowercase
            if word.lower() in ['of', 'the', 'and', 'for', 'in', 'at', 'to', 'a', 'an']:
                continue
            if word and not word[0].isupper() and not word[0].isdigit():
                issues.append(f"Folder not Title Case: {folder_name}")
                break
        
        # Check for empty folders
        md_files = list(folder.glob('*.md'))
        if not md_files:
            issues.append(f"Empty folder (no .md files): {folder_name}")
        
        # Check for single-game folders that should maybe be in Standalone
        if len(md_files) == 1:
            issues.append(f"Single-game folder (consider Standalone?): {folder_name}")
    
    return issues


def check_duplicate_games(games_path: Path) -> list:
    """Check for potential duplicate game entries."""
    issues = []
    
    # Collect all game titles (normalized)
    games = {}
    
    for folder in games_path.iterdir():
        if not folder.is_dir():
            continue
        
        for game_file in folder.glob('*.md'):
            filename = game_file.stem
            
            # Normalize: remove year, lowercase, remove punctuation
            normalized = re.sub(r'^\d{4}\s*-\s*', '', filename)
            normalized = re.sub(r'[^\w\s]', '', normalized.lower())
            normalized = ' '.join(normalized.split())  # Normalize whitespace
            
            if normalized in games:
                issues.append(
                    f"Potential duplicate: '{game_file.name}' vs '{games[normalized].name}'"
                )
            else:
                games[normalized] = game_file
    
    return issues


def main():
    parser = argparse.ArgumentParser(description='Audit folder structure')
    parser.add_argument('--fix', action='store_true', help='Apply safe fixes (not implemented)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all checks')
    args = parser.parse_args()
    
    print("=" * 80)
    print("FOLDER STRUCTURE AUDIT")
    print("=" * 80)
    print()
    
    all_issues = []
    
    # Check game filenames
    print("Checking game filenames...")
    for folder in GAMES_PATH.iterdir():
        if not folder.is_dir():
            continue
        for game_file in folder.glob('*.md'):
            issues = check_game_filename(game_file)
            all_issues.extend(issues)
    
    # Check series organization
    print("Checking series organization...")
    issues = check_series_organization(GAMES_PATH)
    all_issues.extend(issues)
    
    # Check folder naming
    print("Checking folder naming...")
    issues = check_folder_naming(GAMES_PATH)
    all_issues.extend(issues)
    
    # Check for duplicates
    print("Checking for duplicates...")
    issues = check_duplicate_games(GAMES_PATH)
    all_issues.extend(issues)
    
    # Report
    print()
    print("=" * 80)
    
    if all_issues:
        print(f"Found {len(all_issues)} issues:\n")
        for issue in sorted(all_issues):
            print(f"  ⚠️  {issue}")
    else:
        print("✅ No issues found!")
    
    print()
    print("=" * 80)
    
    return len(all_issues)


if __name__ == '__main__':
    exit(main())
