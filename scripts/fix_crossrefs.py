#!/usr/bin/env python3
"""
Cross-Reference Fixer for SierraVault
Automatically adds missing cross-references to series games.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")
GAMES_PATH = VAULT_PATH / "Games"

def load_scan_results():
    """Load previous scan results."""
    results_path = VAULT_PATH / "crossref-scan-results.json"
    with open(results_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_series_folders():
    """Get all series game folders."""
    series_folders = []
    for folder in GAMES_PATH.iterdir():
        if folder.is_dir() and (folder.name.startswith("19") or folder.name[0].isdigit()):
            series_folders.append(folder)
    return series_folders

def extract_game_titles_from_folder(folder):
    """Extract game titles from markdown files in a folder."""
    games = []
    for md_file in folder.glob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                games.append(title)
    return games

def build_series_index():
    """Build an index of all series folders and their games."""
    series_index = {}
    for folder in get_series_folders():
        games = extract_game_titles_from_folder(folder)
        if games:
            series_index[folder.name] = games
    return series_index

def find_or_create_see_also_section(content):
    """Find existing See Also section or create one."""
    # Look for existing See Also section
    see_also_pattern = r'(##\s+See\s+Also\s+.*?)(?=\n##|\Z)'
    match = re.search(see_also_pattern, content, re.DOTALL)
    
    if match:
        return match.group(1), match.start(), match.end()
    
    # Create new section after Purchase section if exists
    purchase_pattern = r'(##\s+Purchase\s+.*?)(?=\n##|\Z)'
    purchase_match = re.search(purchase_pattern, content, re.DOTALL)
    
    if purchase_match:
        insert_pos = purchase_match.end()
        return None, insert_pos, insert_pos
    
    # Otherwise, add at the end before any existing ## sections or at very end
    existing_sections = re.findall(r'^##\s+.+$', content, re.MULTILINE)
    if existing_sections:
        # Find position of last section
        last_section_match = re.search(r'(##\s+.+)$', content, re.MULTILINE)
        if last_section_match:
            insert_pos = last_section_match.end()
            return None, insert_pos, insert_pos
    
    # Fallback: add at end
    return None, len(content), len(content)

def add_cross_references_to_content(content, new_references):
    """Add new cross-references to the See Also section."""
    if not new_references:
        return content, 0
    
    see_also_section, start_pos, end_pos = find_or_create_see_also_section(content)
    
    # Build new references list
    ref_lines = []
    for ref in new_references:
        ref_lines.append(f"- [[{ref}]]")
    
    new_refs_text = "\n".join(ref_lines)
    
    if see_also_section:
        # Append to existing section
        new_section = see_also_section + "\n\n" + new_refs_text
        content = content[:start_pos] + new_section + content[end_pos:]
    else:
        # Create new section
        section_header = "## See Also\n\n"
        content = content[:start_pos] + section_header + new_refs_text + "\n\n" + content[start_pos:]
    
    return content, len(new_references)

def fix_series_folder(folder, series_index, scan_results):
    """Fix cross-references in a series folder."""
    folder_name = folder.name
    
    # Find this folder in scan results
    folder_results = None
    for result in scan_results.get('details', []):
        if result['folder'] == folder_name:
            folder_results = result
            break
    
    if not folder_results:
        return 0
    
    fixed_count = 0
    games_in_folder = extract_game_titles_from_folder(folder)
    
    for md_file in folder.glob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        game_title = md_file.stem
        
        # Find missing references for this file
        missing_for_file = [
            ref for file_name, ref in folder_results['missing_references']
            if file_name == md_file.name
        ]
        
        if missing_for_file:
            new_content, count = add_cross_references_to_content(content, missing_for_file)
            
            if count > 0:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                # Update timestamp
                update_timestamp(md_file)
                
                fixed_count += count
                print(f"   ✅ {md_file.name}: Added {count} cross-reference(s)")
    
    return fixed_count

def update_timestamp(md_file):
    """Update the last_modified timestamp in frontmatter."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update or add last_modified timestamp
    timestamp_pattern = r'(\nlast_modified:\s+\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    if re.search(timestamp_pattern, content):
        content = re.sub(timestamp_pattern, f'\nlast_modified: {current_timestamp}', content)
    else:
        # Add timestamp after frontmatter
        frontmatter_end = content.find('\n---', 7)
        if frontmatter_end > 0:
            content = content[:frontmatter_end+3] + f"\nlast_modified: {current_timestamp}" + content[frontmatter_end+3:]
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Main fix function."""
    print("🔧 Cross-Reference Fixer")
    print("=" * 50)
    
    # Load scan results
    print("\n📊 Loading scan results...")
    scan_results = load_scan_results()
    
    # Build fresh series index
    print("📚 Building series index...")
    series_index = build_series_index()
    
    total_fixed = 0
    
    # Fix each series folder
    for folder in get_series_folders():
        folder_name = folder.name
        print(f"\n📁 Processing: {folder_name}")
        
        fixed = fix_series_folder(folder, series_index, scan_results)
        total_fixed += fixed
        
        if fixed == 0:
            print(f"   ℹ️  No fixes needed")
    
    print("\n" + "=" * 50)
    print(f"✅ Fix complete!")
    print(f"   Total cross-references added: {total_fixed}")
    
    # Update scan results with fix report
    scan_results['fix_report'] = {
        "fix_date": datetime.now().isoformat(),
        "total_fixed": total_fixed
    }
    
    output_path = VAULT_PATH / "crossref-scan-results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scan_results, f, indent=2)
    
    print(f"   Report saved to: {output_path}")
    
    return total_fixed

if __name__ == "__main__":
    main()
