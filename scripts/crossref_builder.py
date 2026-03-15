#!/usr/bin/env python3
"""
Cross-Reference Builder for SierraVault
Scans series folders for missing cross-references between games in the same series.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")
GAMES_PATH = VAULT_PATH / "Games"
SERIES_PATH = VAULT_PATH / "Series"

def get_series_folders():
    """Get all series game folders."""
    series_folders = []
    for folder in GAMES_PATH.iterdir():
        if folder.is_dir() and folder.name.startswith("19") or folder.name[0].isdigit():
            series_folders.append(folder)
    return series_folders

def extract_game_titles_from_folder(folder):
    """Extract game titles from markdown files in a folder."""
    games = []
    for md_file in folder.glob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract title from frontmatter or first heading
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                games.append(title)
    return games

def find_cross_references(content, target_series_games):
    """Find existing cross-references to games in the target series."""
    references = []
    for game in target_series_games:
        # Look for wiki links to the game
        pattern = rf'\[\[{re.escape(game)}\]\]'
        if re.search(pattern, content, re.IGNORECASE):
            references.append(game)
    return references

def check_missing_cross_references(folder, all_series_games):
    """Check if a series folder is missing cross-references to other games in the series."""
    folder_name = folder.name
    games_in_folder = extract_game_titles_from_folder(folder)
    
    if not games_in_folder:
        return None
    
    # Get all games in this series (from all folders)
    series_games = all_series_games.get(folder_name, [])
    
    missing_refs = []
    found_refs = []
    
    for md_file in folder.glob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            game_title = md_file.stem
            
            # Find existing references to other series games
            for other_game in series_games:
                if other_game != game_title:
                    pattern = rf'\[\[{re.escape(other_game)}\]\]'
                    if re.search(pattern, content, re.IGNORECASE):
                        found_refs.append((md_file.name, other_game))
                    else:
                        # Check if this game should reference the other
                        # Look for series indicators in the content
                        if "series" in content.lower() or folder_name.lower() in other_game.lower():
                            missing_refs.append((md_file.name, other_game))
    
    return {
        "folder": folder_name,
        "games_count": len(games_in_folder),
        "found_references": found_refs,
        "missing_references": missing_refs,
        "total_missing": len(missing_refs)
    }

def build_series_index():
    """Build an index of all series folders and their games."""
    series_index = {}
    series_folders = get_series_folders()
    
    for folder in series_folders:
        games = extract_game_titles_from_folder(folder)
        if games:
            series_index[folder.name] = games
    
    return series_index

def main():
    """Main scan function."""
    print("🔍 Building series index...")
    series_index = build_series_index()
    
    print(f"Found {len(series_index)} series folders\n")
    
    results = []
    total_missing = 0
    
    for folder in get_series_folders():
        scan_result = check_missing_cross_references(folder, series_index)
        if scan_result and scan_result["total_missing"] > 0:
            results.append(scan_result)
            total_missing += scan_result["total_missing"]
    
    output = {
        "scan_date": datetime.now().isoformat(),
        "total_series_scanned": len(list(get_series_folders())),
        "series_with_missing_refs": len(results),
        "total_missing_references": total_missing,
        "details": results
    }
    
    # Save results
    output_path = VAULT_PATH / "crossref-scan-results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Scan complete!")
    print(f"   Series scanned: {output['total_series_scanned']}")
    print(f"   Series with missing refs: {output['series_with_missing_refs']}")
    print(f"   Total missing references: {output['total_missing_references']}")
    print(f"   Results saved to: {output_path}")
    
    # Print summary
    if results:
        print("\n📋 Series with missing cross-references:")
        for result in results:
            print(f"\n   {result['folder']}:")
            print(f"      Games: {result['games_count']}")
            print(f"      Missing: {result['total_missing']}")
            if result['missing_references'][:3]:  # Show first 3
                for missing in result['missing_references'][:3]:
                    print(f"         - {missing[0]} → {missing[1]}")
                if len(result['missing_references']) > 3:
                    print(f"         ... and {len(result['missing_references']) - 3} more")
    
    return output

if __name__ == "__main__":
    main()
