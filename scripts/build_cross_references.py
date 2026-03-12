#!/usr/bin/env python3
"""
Cross-reference builder for SierraVault series folders.
Scans series folders and adds missing cross-references to 'See Also' sections.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Load scan results
SCAN_FILE = Path("vault/crossref-scan-results.json")

def load_scan_results() -> Dict:
    """Load cross-reference scan results."""
    with open(SCAN_FILE) as f:
        return json.load(f)

def get_series_files(series_dir: Path) -> List[Path]:
    """Get all game files in a series directory."""
    return sorted(series_dir.glob("*.md"))

def extract_game_title(filepath: Path) -> str:
    """Extract game title from filename."""
    # Format: "YYYY - Game Title.md" or "TBD - Game Title.md"
    name = filepath.stem
    # Remove year prefix
    match = re.match(r"^\d{4}\s*-\s*(.+)$", name)
    if match:
        return match.group(1).strip()
    match = re.match(r"^TBD\s*-\s*(.+)$", name)
    if match:
        return match.group(1).strip()
    return name

def find_series_directories() -> List[Tuple[str, Path]]:
    """Find all series directories in vault/Games."""
    games_dir = Path("vault/Games")
    series_dirs = []
    
    for item in games_dir.iterdir():
        if item.is_dir():
            series_dirs.append((item.name, item))
    
    return series_dirs

def build_series_index() -> Dict[str, Set[str]]:
    """Build index of all games by series."""
    series_index = {}
    
    for series_name, series_dir in find_series_directories():
        games = set()
        for filepath in get_series_files(series_dir):
            title = extract_game_title(filepath)
            games.add(title)
        series_index[series_name] = games
    
    return series_index

def find_missing_crossrefs(scan_results: Dict, series_index: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """Find missing cross-references for each game."""
    missing = {}
    
    for issue in scan_results["issues"]:
        series = issue["series"]
        game = issue["game"]
        filepath = issue["filepath"]
        
        if series not in series_index:
            continue
        
        all_games = series_index[series]
        found = set(issue["found"])
        missing_games = all_games - found
        
        if missing_games:
            missing[filepath] = list(missing_games)
    
    return missing

def update_file(filepath: Path, missing_games: List[str]):
    """Update a game file with missing cross-references in 'See Also' section."""
    content = filepath.read_text()
    
    # Check if See Also section exists
    see_also_match = re.search(r'(## See Also.*?)(?=\n##|$)', content, re.DOTALL)
    
    if see_also_match:
        see_also_section = see_also_match.group(1)
        
        # Check if any missing games are already referenced
        existing_refs = set(re.findall(r'\[\[([^\]]+)\]\]', see_also_section))
        new_refs = [g for g in missing_games if g not in existing_refs]
        
        if new_refs:
            # Add new references to See Also
            new_links = "\n".join(f"[[{ref}]]" for ref in sorted(new_refs))
            
            # Find where to insert (before closing of section or end)
            if see_also_section.strip().endswith("\n"):
                insert_pos = see_also_match.end() - 1
            else:
                insert_pos = see_also_match.end()
            
            new_content = content[:insert_pos] + "\n" + new_links + content[insert_pos:]
            
            # Update timestamp
            timestamp_match = re.search(r'updated:\s*\d{4}-\d{2}-\d{2}', content)
            if timestamp_match:
                new_content = re.sub(
                    r'updated:\s*\d{4}-\d{2}-\d{2}',
                    f'updated: {Path(filepath).read_text().split("updated: ")[1].split("\n")[0][:10] if "updated: " in content else "2026-03-11"}',
                    new_content
                )
            
            filepath.write_text(new_content)
            print(f"✓ Updated {filepath.name} with {len(new_refs)} new cross-references")
    else:
        print(f"⚠ No 'See Also' section in {filepath.name}")

def main():
    """Main execution."""
    print("🔍 Loading cross-reference scan results...")
    scan_results = load_scan_results()
    
    print(f"📊 Found {len(scan_results['issues'])} issues across {scan_results['total_series']} series")
    
    print("\n📚 Building series index...")
    series_index = build_series_index()
    print(f"✓ Indexed {len(series_index)} series")
    
    print("\n🔎 Finding missing cross-references...")
    missing = find_missing_crossrefs(scan_results, series_index)
    print(f"✓ Found {len(missing)} files needing updates")
    
    print("\n📝 Updating files...")
    updated_count = 0
    for filepath_str, missing_games in missing.items():
        filepath = Path(filepath_str)
        if filepath.exists():
            update_file(filepath, missing_games)
            updated_count += 1
    
    print(f"\n✅ Completed! Updated {updated_count} files")
    print(f"📈 Total issues found: {scan_results['total_issues']}")

if __name__ == "__main__":
    main()
