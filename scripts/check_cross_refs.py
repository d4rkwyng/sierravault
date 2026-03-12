#!/usr/bin/env python3
"""
Scan SierraVault series folders for missing cross-references.
Check if series games reference each other properly.
"""
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# Configuration
SIERRAVault_ROOT = "/Users/woodd/Projects/sierravault/vault/Games"
SERIES_TO_CHECK = [
    "3D Ultra",
    "A-10 Tank Killer",
    "Aces",
    "Adiboo",
    "After Dark",
    "Arcade",
    "BC",
    "Caesar",
    "Civil War Generals",
    "Coktel",
    "Conquests",
    "Crazy Nick's",
    "Discovery",
    "Disney",
    "Dr. Brain",
    "Dynamix",
    "EcoQuest",
    "Education",
    "Empire Earth",
    "Fan Games",
    "Front Page Sports",
    "Gabriel Knight",
    "Gobliiins",
    "Gold Rush",
    "Ground Control",
    "Hi-Res",
    "Homeworld",
    "Hoyle",
    "INN",
    "Impressions",
    "Inca",
    "Incredible Machine",
    "IndyCar",
    "Jawbreaker",
    "King's Quest",
    "Krondor",
    "Laura Bow",
    "Leisure Suit Larry",
    "Lords of Magic",
    "Lords of the Realm",
    "Manhunter",
    "Metaltech",
    "Mixed Up",
    "Monolith",
    "NASCAR",
    "Oils Well",
    "Outpost",
    "PGA Championship Golf",
    "Phantasmagoria",
    "Pharaoh",
    "Playtoons",
    "Police Quest",
    "Power Chess",
    "Quest for Glory",
    "Red Baron",
    "SWAT",
    "Shivers",
    "Sierra Attractions",
    "Sierra Pro Pilot",
    "Sierra Sports",
    "Space Quest",
    "Spiritual Successors",
    "Standalone",
    "Stellar 7",
    "Strategy",
    "Take a Break!",
    "Thexder",
    "Trophy Bass",
    "Ultima",
    "Ultimate Soccer Manager",
    "Valve",
    "XBLA",
    "Zeus",
]

def extract_series_name(title):
    """Extract series from game title."""
    # Common series patterns
    series_patterns = [
        r"^(King's Quest)",
        r"^(Space Quest)",
        r"^(Quest for Glory)",
        r"^(Police Quest)",
        r"^(Leisure Suit Larry)",
        r"^(Gabriel Knight)",
        r"^(Phantasmagoria)",
    ]
    for pattern in series_patterns:
        match = re.match(pattern, title)
        if match:
            return match.group(1)
    return None

def extract_existing_refs(content):
    """Extract existing cross-references in 'See Also' section."""
    refs = []
    # Match [[Game Name]] or [[Game Name|Alias]] or [[Game Name]] - description
    pattern = r'\[\[([^\]]+)\]\]'
    for match in re.finditer(pattern, content):
        ref = match.group(1)
        # Skip if it's a series overview or similar
        if "Series" not in ref and "Series Overview" not in ref:
            refs.append(ref)
    return refs

def get_all_games_in_series(series_path):
    """Get all games in a series folder."""
    games = []
    if not os.path.exists(series_path):
        return games
    
    for file in os.listdir(series_path):
        if file.endswith('.md'):
            games.append(file)
    return sorted(games)

def check_cross_refs_for_series(series_name, series_path):
    """Check cross-references within a series."""
    print(f"\n{'='*60}")
    print(f"Checking: {series_name}")
    print(f"{'='*60}")
    
    games = get_all_games_in_series(series_path)
    if not games:
        print(f"No games found in {series_path}")
        return []
    
    print(f"Found {len(games)} games:")
    for game in games:
        print(f"  - {game}")
    
    missing_refs = []
    issues = []
    
    for game_file in games:
        game_path = os.path.join(series_path, game_file)
        
        try:
            with open(game_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the game title from the file
            title_match = re.search(r"^\#\s+(.+)$", content, re.MULTILINE)
            game_title = title_match.group(1) if title_match else game_file
            
            # Extract existing references
            existing_refs = extract_existing_refs(content)
            
            # Check what other games in the series should be referenced
            series_games = [g for g in games if g != game_file]
            
            # Check if all other games in series are referenced
            missing = []
            for other_game in series_games:
                # Extract base name without year for comparison
                other_base = re.sub(r'^\d{4}\s*-\s*', '', other_game)
                other_base = re.sub(r'\.md$', '', other_base)
                
                found = False
                for ref in existing_refs:
                    ref_clean = re.sub(r'\|.*$', '', ref)  # Remove alias
                    ref_clean = re.sub(r'^\d{4}\s*-\s*', '', ref_clean)  # Remove year
                    if other_base.lower() in ref_clean.lower() or ref_clean.lower() in other_base.lower():
                        found = True
                        break
                
                if not found:
                    missing.append(other_game)
            
            if missing:
                missing_refs.append({
                    'file': game_file,
                    'title': game_title,
                    'missing': missing,
                    'existing': existing_refs
                })
                issues.append(f"  ⚠️ {game_file}: Missing refs to {len(missing)} games")
                for m in missing:
                    issues.append(f"     → {m}")
            else:
                print(f"  ✓ {game_file}: All series games cross-referenced")
        
        except Exception as e:
            print(f"  ✗ Error reading {game_file}: {e}")
    
    return missing_refs

def main():
    all_missing = []
    
    for series in SERIES_TO_CHECK:
        series_path = os.path.join(SIERRAVault_ROOT, series)
        missing = check_cross_refs_for_series(series, series_path)
        all_missing.extend(missing)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total games with missing cross-references: {len(all_missing)}")
    
    if all_missing:
        for item in all_missing:
            print(f"\n📄 {item['file']}")
            print(f"   Title: {item['title']}")
            print(f"   Missing references to {len(item['missing'])} game(s):")
            for m in item['missing']:
                print(f"      → {m}")
    else:
        print("✓ All series games have proper cross-references!")
    
    return 0 if not all_missing else 1

if __name__ == "__main__":
    sys.exit(main())