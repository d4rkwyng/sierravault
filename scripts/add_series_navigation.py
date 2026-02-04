#!/usr/bin/env python3
"""Add series navigation (See Also sections) to game pages."""

import os
import re
from pathlib import Path
from collections import defaultdict

VAULT_ROOT = Path(__file__).parent.parent / "vault"
GAMES_DIR = VAULT_ROOT / "Games"
SERIES_DIR = VAULT_ROOT / "Series"

# Major series that have dedicated overview pages
MAJOR_SERIES = {
    "King's Quest": "King's Quest Series",
    "Space Quest": "Space Quest Series",
    "Quest for Glory": "Quest for Glory Series",
    "Leisure Suit Larry": "Leisure Suit Larry Series",
    "Police Quest": "Police Quest Series",
    "Gabriel Knight": "Gabriel Knight Series",
    "Laura Bow": "Laura Bow Series",
}

def get_games_in_folder(folder_path):
    """Get all game files in a folder, sorted by year."""
    games = []
    for f in folder_path.glob("*.md"):
        # Extract year from filename (e.g., "1990 - King's Quest V...")
        match = re.match(r'(\d{4}) - (.+)\.md', f.name)
        if match:
            year = int(match.group(1))
            title = match.group(2)
            games.append((year, title, f))
    return sorted(games, key=lambda x: (x[0], x[1]))

def get_series_index_page(folder_name):
    """Get the series index page if it exists."""
    for series_name, index_name in MAJOR_SERIES.items():
        if series_name.lower() in folder_name.lower():
            index_path = SERIES_DIR / f"{index_name}.md"
            if index_path.exists():
                return index_name
    return None

def create_see_also_section(game_file, prev_game, next_game, series_index):
    """Create a See Also section for a game."""
    lines = []
    lines.append("\n## See Also\n")
    
    # Series navigation
    if series_index:
        lines.append(f"- [[{series_index}]] - Series overview\n")
    
    if prev_game:
        year, title, _ = prev_game
        lines.append(f"- [[{year} - {title}|← Previous: {title}]]\n")
    
    if next_game:
        year, title, _ = next_game
        lines.append(f"- [[{year} - {title}|→ Next: {title}]]\n")
    
    return "".join(lines)

def add_navigation_to_file(game_file, prev_game, next_game, series_index):
    """Add See Also section to a game file if it doesn't exist."""
    content = game_file.read_text(encoding='utf-8')
    
    # Check if See Also section already exists
    if "## See Also" in content:
        return False, "Already has See Also"
    
    # Find position to insert (before References section)
    refs_match = re.search(r'\n## References\n', content)
    if refs_match:
        insert_pos = refs_match.start()
        see_also = create_see_also_section(game_file, prev_game, next_game, series_index)
        new_content = content[:insert_pos] + see_also + content[insert_pos:]
        game_file.write_text(new_content, encoding='utf-8')
        return True, "Added See Also section"
    else:
        return False, "No References section found"

def process_series_folder(folder_path):
    """Process all games in a series folder."""
    folder_name = folder_path.name
    games = get_games_in_folder(folder_path)
    series_index = get_series_index_page(folder_name)
    
    results = []
    for i, (year, title, game_file) in enumerate(games):
        prev_game = games[i-1] if i > 0 else None
        next_game = games[i+1] if i < len(games)-1 else None
        
        success, msg = add_navigation_to_file(game_file, prev_game, next_game, series_index)
        if success:
            results.append(f"  ✓ {year} - {title}")
    
    return results

def main():
    # Get all game folders with more than 1 game
    total_modified = 0
    
    for folder in sorted(GAMES_DIR.iterdir()):
        if not folder.is_dir():
            continue
        
        games = get_games_in_folder(folder)
        if len(games) < 2:
            continue  # Skip folders with single games
        
        print(f"\n## {folder.name} ({len(games)} games)")
        results = process_series_folder(folder)
        
        if results:
            for r in results:
                print(r)
            total_modified += len(results)
        else:
            print("  (all games already have navigation or no References section)")
    
    print(f"\n\nTotal files modified: {total_modified}")

if __name__ == "__main__":
    main()
