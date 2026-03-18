#!/usr/bin/env python3
"""
Cross-reference builder for SierraVault series folders.
Scans series folders for missing cross-references between games.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault/Games")

def extract_wiki_links(content):
    """Extract all [[Wiki Links]] from content."""
    pattern = r'\[\[([^\]]+)\]\]'
    return re.findall(pattern, content)

def extract_game_titles_from_path(filepath):
    """Extract game title from file path."""
    return Path(filepath).stem

def find_series_folders():
    """Find all series folders (folders with multiple games)."""
    series_folders = []
    for item in VAULT_PATH.iterdir():
        if item.is_dir():
            md_files = list(item.glob("*.md"))
            if len(md_files) > 1:  # Multiple games = series
                series_folders.append(item)
    return series_folders

def get_games_in_series(series_folder):
    """Get all game markdown files in a series folder."""
    games = []
    for file in series_folder.glob("*.md"):
        games.append(file)
    return games

def check_cross_references(series_folder):
    """Check if games in a series reference each other."""
    games = get_games_in_series(series_folder)
    issues = []
    
    for game_file in games:
        content = game_file.read_text(encoding='utf-8')
        wiki_links = extract_wiki_links(content)
        
        # Get expected series members (other games in same folder)
        expected_refs = [
            extract_game_titles_from_path(g) 
            for g in games 
            if g != game_file
        ]
        
        # Check which expected references are missing
        missing_refs = []
        for expected in expected_refs:
            # Normalize for comparison (remove special chars, lowercase)
            expected_normalized = re.sub(r'[^\w\s]', '', expected).lower()
            found = False
            for link in wiki_links:
                link_normalized = re.sub(r'[^\w\s]', '', link).lower()
                if expected_normalized in link_normalized or link_normalized in expected_normalized:
                    found = True
                    break
            
            if not found:
                missing_refs.append(expected)
        
        if missing_refs:
            issues.append({
                'file': game_file,
                'title': game_file.stem,
                'missing': missing_refs
            })
    
    return issues

def main():
    """Main scan function."""
    print("🔍 Scanning SierraVault series folders for missing cross-references...\n")
    
    series_folders = find_series_folders()
    total_issues = 0
    all_issues = []
    
    for series_folder in series_folders:
        issues = check_cross_references(series_folder)
        if issues:
            all_issues.extend(issues)
            total_issues += len(issues)
            print(f"📁 {series_folder.name}:")
            for issue in issues:
                print(f"   ❌ {issue['title']}: Missing {len(issue['missing'])} cross-reference(s)")
                for missing in issue['missing']:
                    print(f"      → [[{missing}]]")
            print()
    
    print(f"📊 Summary: {total_issues} missing cross-reference(s) found across {len(series_folders)} series folders")
    
    # Save report
    report_path = Path("/Users/woodd/Projects/sierravault/vault/cross-reference-report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Cross-Reference Report\n\n")
        f.write(f"Generated: {Path('.').resolve()}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"Found {total_issues} missing cross-reference(s) across {len(series_folders)} series folders.\n\n")
        f.write("## Issues\n\n")
        
        for series_folder in series_folders:
            issues = check_cross_references(series_folder)
            if issues:
                f.write(f"### {series_folder.name}\n\n")
                for issue in issues:
                    f.write(f"#### {issue['title']}\n\n")
                    f.write(f"Missing references:\n")
                    for missing in issue['missing']:
                        f.write(f"- [[{missing}]]\n")
                    f.write("\n")
    
    print(f"💾 Report saved to: {report_path}")
    return all_issues

if __name__ == "__main__":
    main()
