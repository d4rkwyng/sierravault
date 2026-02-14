#!/usr/bin/env python3
"""
Fix See Also sections:
1. Remove fake prev/next from non-series folders
2. Add series overview links to actual series games
"""

import os
import re
from pathlib import Path

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")

# Folders that should NOT have prev/next navigation (standalone games)
NON_SERIES_FOLDERS = {
    "Standalone", "Arcade", "Coktel", "Spiritual Successors", 
    "Fan Games", "Hi-Res", "Dynamix", "Strategy", "Education",
    "Disney", "Discovery", "INN", "Monolith", "Oils Well",
    "Power Chess", "Sierra Attractions", "Sierra Sports",
    "Take a Break!", "Ultima", "Ultimate Soccer Manager", "XBLA"
}

# Series with overview pages
SERIES_WITH_OVERVIEW = {
    "King's Quest": "King's Quest Series",
    "Space Quest": "Space Quest Series", 
    "Quest for Glory": "Quest for Glory Series",
    "Leisure Suit Larry": "Leisure Suit Larry Series",
    "Police Quest": "Police Quest Series",
    "Gabriel Knight": "Gabriel Knight Series",
    "Laura Bow": "Laura Bow Series",
}

def get_frontmatter(content):
    """Extract frontmatter from markdown file (simple parser)."""
    fm = {}
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            fm_text = content[3:end]
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    # Handle arrays like [Sierra On-Line, Dynamix]
                    if val.startswith('[') and val.endswith(']'):
                        val = val[1:-1].split(',')[0].strip()
                    fm[key] = val
    return fm

def fix_non_series_see_also(filepath):
    """Remove fake prev/next from non-series games, add developer link."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm = get_frontmatter(content)
    developer = fm.get('developer', 'Sierra On-Line')
    if isinstance(developer, list):
        developer = developer[0]
    
    # Find See Also section
    see_also_match = re.search(r'## See Also\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if not see_also_match:
        return False, "No See Also section"
    
    old_section = see_also_match.group(1)
    
    # Check if it has fake prev/next
    if '→ Next:' not in old_section and '← Previous:' not in old_section:
        return False, "No fake prev/next found"
    
    # Create new section with just developer link
    new_section = f"- [[{developer}]] - Developer\n"
    
    new_content = content[:see_also_match.start(1)] + new_section + content[see_also_match.end(1):]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"Fixed: {developer}"

def add_series_overview(filepath, series_name, overview_page):
    """Add series overview link if missing."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has series overview link
    if f'[[{overview_page}]]' in content:
        return False, "Already has series overview"
    
    # Find See Also section
    see_also_match = re.search(r'(## See Also\n)(.*?)(\n## |\Z)', content, re.DOTALL)
    if not see_also_match:
        return False, "No See Also section"
    
    old_section = see_also_match.group(2)
    
    # Add series overview link at the end
    new_line = f"- [[{overview_page}]] - Series overview\n"
    new_section = old_section.rstrip() + "\n" + new_line
    
    new_content = content[:see_also_match.start(2)] + new_section + content[see_also_match.end(2):]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, "Added series overview"

def main():
    games_path = VAULT_PATH / "Games"
    
    fixed_non_series = 0
    fixed_series = 0
    
    for folder in games_path.iterdir():
        if not folder.is_dir():
            continue
        
        folder_name = folder.name
        
        # Phase 1: Fix non-series folders
        if folder_name in NON_SERIES_FOLDERS:
            for md_file in folder.glob("*.md"):
                success, msg = fix_non_series_see_also(md_file)
                if success:
                    print(f"[NON-SERIES] {md_file.name}: {msg}")
                    fixed_non_series += 1
        
        # Phase 2: Add series overview to actual series
        elif folder_name in SERIES_WITH_OVERVIEW:
            overview_page = SERIES_WITH_OVERVIEW[folder_name]
            for md_file in folder.glob("*.md"):
                success, msg = add_series_overview(md_file, folder_name, overview_page)
                if success:
                    print(f"[SERIES] {md_file.name}: {msg}")
                    fixed_series += 1
    
    print(f"\n=== Summary ===")
    print(f"Fixed non-series pages: {fixed_non_series}")
    print(f"Added series overview: {fixed_series}")

if __name__ == "__main__":
    main()
