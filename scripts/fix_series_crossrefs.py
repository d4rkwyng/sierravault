#!/usr/bin/env python3
"""
Cross-Reference Fixer for SierraVault Series
Automatically adds missing cross-references to series overview files.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")
SERIES_PATH = VAULT_PATH / "Series"

def load_scan_results():
    """Load the cross-reference scan results."""
    results_path = VAULT_PATH / "crossref-scan-results.json"
    with open(results_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_series_games(series_file):
    """Extract game titles from a series overview markdown file."""
    games = []
    with open(series_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Look for wiki links in timeline table or game lists
        pattern = r'\[\[(\d{4}\s+-\s+.*?)(?:\|([^\]]+))?\]\]'
        matches = re.findall(pattern, content)
        
        for match in matches:
            title = match[1] if match[1] else match[0]
            games.append(title.strip())
    
    return games

def find_or_create_section(content, section_name):
    """Find existing section or create new one at end."""
    # Look for existing "See Also" section
    pattern = rf'(##\s+{re.escape(section_name)}\s*\n(?:.*?\n)*?)(?=\n##|\Z)'
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    
    if match:
        return match.group(1), match.start(), match.end()
    
    # Create new section
    return None, None, None

def add_cross_references_to_section(content, missing_refs, section_name="See Also"):
    """Add missing cross-references to the See Also section."""
    # Get unique games that need references
    games_to_add = set()
    for ref in missing_refs:
        games_to_add.add(ref[1])  # Add the target game
    
    if not games_to_add:
        return content, 0
    
    # Create reference list
    ref_lines = []
    for game in sorted(games_to_add):
        ref_lines.append(f"- [[{game}]]")
    
    new_refs_text = "\n".join(ref_lines)
    
    # Find or create section
    existing_section, start, end = find_or_create_section(content, section_name)
    
    if existing_section:
        # Append to existing section
        # Find the end of the section content
        section_pattern = rf'(##\s+{re.escape(section_name)}\s*\n(?:.*?\n)*?)(?=\n##|\Z)'
        match = re.search(section_pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            # Insert before the closing of the section
            insert_pos = match.end() - 1  # Before the last newline
            content = content[:insert_pos] + "\n" + new_refs_text + content[insert_pos:]
    else:
        # Create new section at the end (before References if exists)
        refs_pattern = r'(##\s+References\s*\n.*?)(?=\n##|\Z)'
        refs_match = re.search(refs_pattern, content, re.DOTALL)
        
        if refs_match:
            # Insert before References section
            insert_pos = refs_match.start()
            section_text = f"\n## {section_name}\n\n{new_refs_text}\n"
            content = content[:insert_pos] + section_text + content[insert_pos:]
        else:
            # Append at very end
            section_text = f"\n## {section_name}\n\n{new_refs_text}\n"
            content = content + section_text
    
    return content, len(games_to_add)

def fix_series_file(series_file, missing_refs):
    """Fix a single series file with missing cross-references."""
    with open(series_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add missing references
    new_content, count = add_cross_references_to_section(content, missing_refs)
    
    if count > 0:
        # Update timestamp
        timestamp_pattern = r"(last_updated:\s*')[^']+'(\s*)$"
        now = datetime.now().strftime("%Y-%m-%d")
        new_content = re.sub(timestamp_pattern, f"last_updated: '{now}'", new_content, flags=re.MULTILINE)
        
        # Write back
        with open(series_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, count
    
    return False, 0

def main():
    """Main fix function."""
    print("🔧 Loading scan results...")
    scan_results = load_scan_results()
    
    print(f"Found {scan_results['total_missing_references']} missing references to fix\n")
    
    fixed_count = 0
    files_modified = []
    
    for series_data in scan_results['details']:
        series_name = series_data['series']
        missing_refs = series_data['missing_references']
        
        if not missing_refs:
            continue
        
        # Find the series file
        series_file = SERIES_PATH / f"{series_name} Series.md"
        
        if not series_file.exists():
            print(f"⚠️  Series file not found: {series_file}")
            continue
        
        print(f"📝 Fixing {series_name} Series...")
        
        success, count = fix_series_file(series_file, missing_refs)
        
        if success:
            fixed_count += count
            files_modified.append(series_file.name)
            print(f"   ✅ Added {count} cross-references")
        else:
            print(f"   ⚠️  No changes needed for {series_file.name}")
    
    # Save fix report
    fix_report = {
        "fix_date": datetime.now().isoformat(),
        "total_fixed": fixed_count,
        "files_modified": files_modified
    }
    
    output_path = VAULT_PATH / "crossref-fix-report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(fix_report, f, indent=2)
    
    print(f"\n✅ Fix complete!")
    print(f"   Total references added: {fixed_count}")
    print(f"   Files modified: {len(files_modified)}")
    print(f"   Report saved to: {output_path}")
    
    if files_modified:
        print("\n📋 Modified files:")
        for f in files_modified:
            print(f"   - {f}")
    
    return fix_report

if __name__ == "__main__":
    main()
