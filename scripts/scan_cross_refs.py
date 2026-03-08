#!/usr/bin/env python3
"""
Cross-reference scanner for SierraVault series folders.
Identifies missing cross-references between series games.
"""

import os
import re
from pathlib import Path

SERIES_DIR = "/Users/woodd/Projects/sierravault/vault/Games"

def extract_title_from_file(filepath):
    """Extract the page title from a markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                return line[2:].strip()
    return None

def find_series_games():
    """Find all series folders with multiple games."""
    series_games = {}
    
    for entry in os.listdir(SERIES_DIR):
        series_path = os.path.join(SERIES_DIR, entry)
        if os.path.isdir(series_path):
            md_files = [f for f in os.listdir(series_path) if f.endswith('.md')]
            if len(md_files) >= 2:  # Only consider series with 2+ games
                games = []
                for md_file in md_files:
                    filepath = os.path.join(series_path, md_file)
                    title = extract_title_from_file(filepath)
                    if title:
                        games.append((title, filepath, md_file))
                series_games[entry] = games
    
    return series_games

def check_cross_refs(game_title, filepath):
    """Check if a game references its series siblings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all [[wiki links]] in the file
    wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
    
    return wiki_links

def analyze_series(series_games):
    """Analyze each series for missing cross-references."""
    results = []
    
    for series_name, games in series_games.items():
        print(f"\n📁 Series: {series_name}")
        print("=" * 60)
        
        # Get all game titles in this series
        all_titles = [g[0] for g in games]
        game_count = len(games)
        
        for title, filepath, filename in games:
            print(f"\n  🎮 {title}")
            wiki_links = check_cross_refs(title, filepath)
            
            # Check if other series games are referenced
            missing_refs = []
            found_refs = []
            
            for other_title in all_titles:
                if other_title == title:
                    continue
                
                # Check if other_title appears in wiki links
                if any(other_title in link for link in wiki_links):
                    found_refs.append(other_title)
                else:
                    missing_refs.append(other_title)
            
            # Report
            if missing_refs:
                print(f"    ❌ Missing {len(missing_refs)}/{game_count - 1} series refs")
                for ref in missing_refs[:5]:  # Show first 5
                    print(f"       - [[{ref}]]")
                if len(missing_refs) > 5:
                    print(f"       ... and {len(missing_refs) - 5} more")
                
                results.append({
                    'series': series_name,
                    'game': title,
                    'filepath': filepath,
                    'missing': missing_refs,
                    'found': found_refs
                })
            else:
                print(f"    ✅ All {game_count - 1} series refs present")
    
    return results

def main():
    print("🔍 SierraVault Cross-Reference Scanner")
    print("=" * 60)
    
    series_games = find_series_games()
    print(f"\n📊 Found {len(series_games)} series with 2+ games")
    
    if not series_games:
        print("No multi-game series found!")
        return
    
    results = analyze_series(series_games)
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    if results:
        print(f"❌ {len(results)} games need cross-reference updates")
        for r in results:
            print(f"\n  📝 {r['game']} ({r['series']})")
            print(f"     File: {r['filepath']}")
            print(f"     Missing refs: {len(r['missing'])}")
    else:
        print("✅ All games have proper cross-references!")
    
    # Save results to JSON
    import json
    output_path = "/Users/woodd/Projects/sierravault/vault/crossref-scan-results.json"
    with open(output_path, 'w') as f:
        json.dump({
            'scan_date': '2026-03-04',
            'total_series': len(series_games),
            'total_issues': len(results),
            'issues': results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_path}")

if __name__ == "__main__":
    main()