#!/usr/bin/env python3
"""
Auto-fix missing cross-references in SierraVault series folders.
Adds [[WikiLinks]] to 'See Also' sections for games that are missing them.
"""

import os
import re
from pathlib import Path

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault/Games")

def extract_game_name_from_path(file_path):
    """Extract the game name from a file path."""
    return Path(file_path).stem

def find_series_games(series_path):
    """Find all game markdown files in a series folder."""
    games = []
    if series_path.exists():
        for md_file in series_path.glob("*.md"):
            games.append(md_file)
    return sorted(games)

def extract_existing_references(file_path):
    """Extract existing [[WikiLinks]] from a file's 'See Also' section."""
    content = file_path.read_text(encoding='utf-8')
    
    # Find the "See Also" section
    see_also_match = re.search(r'## See Also.*?(?=## |$)', content, re.DOTALL)
    
    if not see_also_match:
        return []
    
    see_also_content = see_also_match.group(0)
    
    # Find all wiki links like [[Game Name]] or [[Game Name|Display]]
    wiki_links = re.findall(r'\[\[([^\]]+)\]\]', see_also_content)
    
    return wiki_links

def ensure_see_also_section(content):
    """Ensure the file has a '## See Also' section."""
    if '## See Also' not in content:
        # Add it before the last heading or at the end
        # Find the last heading
        last_heading_match = re.search(r'^(## .+)$', content, re.MULTILINE)
        
        if last_heading_match:
            # Insert before the last heading
            insert_pos = last_heading_match.start()
            content = content[:insert_pos] + "\n## See Also\n\n" + content[insert_pos:]
        else:
            # Add at the end
            content += "\n\n## See Also\n\n"
    
    return content

def add_reference_to_see_also(content, game_name):
    """Add a [[WikiLink]] to the See Also section."""
    # Ensure section exists
    content = ensure_see_also_section(content)
    
    # Find the See Also section
    see_also_match = re.search(r'(## See Also\s*\n)(.*?)(?=## |\Z)', content, re.DOTALL | re.IGNORECASE)
    
    if not see_also_match:
        return content
    
    section_content = see_also_match.group(2)
    section_start = see_also_match.start(2)
    section_end = see_also_match.end(2)
    
    # Check if already exists
    if f'[[{game_name}]]' in section_content or f'[[{game_name.replace("-", " ").replace("_", " ")}]]' in section_content:
        return content
    
    # Add to the section
    new_line = f"[[{game_name}]]\n"
    
    # If section has content, add a newline before
    if section_content.strip():
        new_content = section_content + "\n" + new_line
    else:
        new_content = new_line
    
    content = content[:section_start] + new_content + content[section_end:]
    
    return content

def get_series_name(series_path):
    """Extract series name from path."""
    return series_path.name

def fix_series(series_path):
    """Fix missing cross-references in a series folder."""
    games = find_series_games(series_path)
    if len(games) <= 1:
        return 0  # Skip single-game series
    
    fixed_count = 0
    series_name = get_series_name(series_path)
    
    for game_file in games:
        content = game_file.read_text(encoding='utf-8')
        existing_refs = extract_existing_references(game_file)
        
        # Get the base game names (without display aliases)
        existing_bases = []
        for ref in existing_refs:
            # Handle [[Game Name|Display Name]] format
            base_name = ref.split('|')[0].strip()
            existing_bases.append(base_name)
        
        # Check which other games in the series need to be referenced
        for other_game in games:
            if other_game == game_file:
                continue
            
            other_base_name = extract_game_name_from_path(other_game)
            
            # Check if this game is already referenced
            referenced = False
            for existing in existing_bases:
                if existing.lower() == other_base_name.lower():
                    referenced = True
                    break
                # Also check variations
                if other_base_name.replace('-', ' ').replace('_', ' ').lower() in existing.lower():
                    referenced = True
                    break
            
            if not referenced:
                # Add the reference
                new_content = add_reference_to_see_also(content, other_base_name)
                
                if new_content != content:
                    content = new_content
                    fixed_count += 1
                    game_file.write_text(content, encoding='utf-8')
    
    return fixed_count

def main():
    print(f"Fixing cross-references in {VAULT_PATH}...\n")
    
    total_fixed = 0
    
    # Process each series folder
    for series_path in sorted(VAULT_PATH.iterdir()):
        if not series_path.is_dir():
            continue
        
        fixed = fix_series(series_path)
        if fixed > 0:
            print(f"✅ {series_path.name}: Fixed {fixed} missing cross-references")
            total_fixed += fixed
    
    print(f"\nTotal files modified: {len([p for p in VAULT_PATH.iterdir() if p.is_dir() and fix_series(p) > 0])}")
    print(f"Total cross-references added: {total_fixed}")

if __name__ == "__main__":
    main()