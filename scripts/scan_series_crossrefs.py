#!/usr/bin/env python3
"""
Cross-Reference Scanner for SierraVault Series
Scans series overview files and checks if games reference each other properly.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")
SERIES_PATH = VAULT_PATH / "Series"
GAMES_PATH = VAULT_PATH / "Games"

def extract_series_games(series_file):
    """Extract game titles from a series overview markdown file."""
    games = []
    with open(series_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Look for wiki links in timeline table or game lists
        # Pattern: [[Year - Title\|Display Name]]
        pattern = r'\[\[(\d{4}\s+-\s+.*?)(?:\|([^\]]+))?\]\]'
        matches = re.findall(pattern, content)
        
        for match in matches:
            title = match[1] if match[1] else match[0]
            games.append(title.strip())
    
    return games

def find_existing_cross_refs(content, target_games):
    """Find which target games are already referenced in content."""
    found = []
    for game in target_games:
        # Look for wiki links
        pattern = rf'\[\[{re.escape(game)}\]\]'
        if re.search(pattern, content, re.IGNORECASE):
            found.append(game)
    return found

def check_series_cross_references(series_file):
    """Check if a series file has proper cross-references between games."""
    series_name = series_file.stem.replace(" Series", "")
    games = extract_series_games(series_file)
    
    if not games:
        return None
    
    with open(series_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if games reference each other
    found_refs = []
    missing_refs = []
    
    for i, game in enumerate(games):
        # Check if this game references other games in the series
        for j, other_game in enumerate(games):
            if i != j:
                pattern = rf'\[\[{re.escape(other_game)}\]\]'
                if re.search(pattern, content, re.IGNORECASE):
                    found_refs.append((game, other_game))
                else:
                    # Check if it should reference (e.g., in timeline or related games section)
                    missing_refs.append((game, other_game))
    
    return {
        "series": series_name,
        "file": series_file.name,
        "games_count": len(games),
        "found_references": found_refs,
        "missing_references": missing_refs,
        "total_missing": len(missing_refs)
    }

def main():
    """Main scan function."""
    print("🔍 Scanning series files for cross-references...")
    
    series_files = list(SERIES_PATH.glob("*.md"))
    print(f"Found {len(series_files)} series files\n")
    
    results = []
    total_missing = 0
    
    for series_file in series_files:
        result = check_series_cross_references(series_file)
        if result and result["total_missing"] > 0:
            results.append(result)
            total_missing += result["total_missing"]
    
    output = {
        "scan_date": datetime.now().isoformat(),
        "total_series_scanned": len(series_files),
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
            print(f"\n   {result['series']}:")
            print(f"      Games: {result['games_count']}")
            print(f"      Missing: {result['total_missing']}")
            if result['missing_references'][:5]:  # Show first 5
                for missing in result['missing_references'][:5]:
                    print(f"         - {missing[0]} → {missing[1]}")
                if len(result['missing_references']) > 5:
                    print(f"         ... and {len(result['missing_references']) - 5} more")
    
    return output

if __name__ == "__main__":
    main()
