#!/usr/bin/env python3
"""
Add appropriate links to series games that don't have series overview pages.
Keep existing prev/next navigation, add developer/related links.
"""

import re
from pathlib import Path

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")

# Series without overview pages and what to link them to
SERIES_LINKS = {
    "SWAT": [
        ("Police Quest Series", "Related series (SWAT spun off from Police Quest)"),
        ("Sierra On-Line", "Publisher"),
    ],
    "Hoyle": [
        ("Sierra On-Line", "Publisher"),
    ],
    "3D Ultra": [
        ("Sierra On-Line", "Publisher"),
    ],
    "Metaltech": [
        ("Dynamix", "Developer"),
    ],
    "Dr. Brain": [
        ("Sierra On-Line", "Publisher"),
    ],
    "Gobliiins": [
        ("Coktel Vision", "Developer"),
    ],
    "Red Baron": [
        ("Dynamix", "Developer"),
        ("Aces", "Related flight sim series"),
    ],
    "Homeworld": [
        ("Relic Entertainment", "Developer"),
        ("Sierra On-Line", "Publisher"),
    ],
    "Incredible Machine": [
        ("Dynamix", "Developer"),
        ("Jeff Tunnell", "Creator"),
    ],
    "NASCAR": [
        ("Papyrus Design Group", "Developer"),
        ("Sierra On-Line", "Publisher"),
    ],
    "Front Page Sports": [
        ("Dynamix", "Developer"),
        ("Sierra On-Line", "Publisher"),
    ],
    "Aces": [
        ("Dynamix", "Developer"),
    ],
    "Caesar": [
        ("Impressions Games", "Developer"),
    ],
    "Pharaoh": [
        ("Impressions Games", "Developer"),
    ],
    "Zeus": [
        ("Impressions Games", "Developer"),
    ],
    "Lords of the Realm": [
        ("Impressions Games", "Developer"),
    ],
    "Empire Earth": [
        ("Stainless Steel Studios", "Developer"),
        ("Sierra Entertainment", "Publisher"),
    ],
    "Ground Control": [
        ("Massive Entertainment", "Developer"),
        ("Sierra Entertainment", "Publisher"),
    ],
    "Trophy Bass": [
        ("Sierra On-Line", "Publisher"),
    ],
    "Thexder": [
        ("Game Arts", "Developer"),
    ],
    "A-10 Tank Killer": [
        ("Dynamix", "Developer"),
    ],
    "Stellar 7": [
        ("Dynamix", "Developer"),
    ],
    "Shivers": [
        ("Sierra On-Line", "Developer"),
    ],
    "Phantasmagoria": [
        ("Sierra On-Line", "Developer"),
        ("Roberta Williams", "Creator"),
    ],
    "Outpost": [
        ("Sierra On-Line", "Developer"),
    ],
    "Manhunter": [
        ("Evryware", "Developer"),
        ("Sierra On-Line", "Publisher"),
    ],
    "Krondor": [
        ("Dynamix", "Developer"),
    ],
    "EcoQuest": [
        ("Sierra On-Line", "Developer"),
    ],
    "Conquests": [
        ("Sierra On-Line", "Developer"),
        ("Christy Marx", "Designer"),
    ],
    "Mixed Up": [
        ("Sierra On-Line", "Developer"),
    ],
    "Gold Rush": [
        ("Sierra On-Line", "Developer"),
    ],
    "BC": [
        ("Sierra On-Line", "Publisher"),
    ],
    "After Dark": [
        ("Berkeley Systems", "Developer"),
    ],
    "Adiboo": [
        ("Coktel Vision", "Developer"),
    ],
    "Civil War Generals": [
        ("Sierra On-Line", "Publisher"),
    ],
    "IndyCar": [
        ("Papyrus Design Group", "Developer"),
    ],
    "Lords of Magic": [
        ("Impressions Games", "Developer"),
    ],
    "Playtoons": [
        ("Coktel Vision", "Developer"),
    ],
    "Sierra Pro Pilot": [
        ("Sierra On-Line", "Developer"),
    ],
    "PGA Championship Golf": [
        ("Headgate Studios", "Developer"),
    ],
    "Inca": [
        ("Coktel Vision", "Developer"),
    ],
    "Crazy Nick's": [
        ("Sierra On-Line", "Publisher"),
    ],
}

def add_links_to_series(filepath, links_to_add):
    """Add links to See Also section if not already present."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find See Also section
    see_also_match = re.search(r'(## See Also\n)(.*?)(\n## |\Z)', content, re.DOTALL)
    if not see_also_match:
        return False, "No See Also section"
    
    old_section = see_also_match.group(2)
    new_lines = []
    added = []
    
    for link_target, link_desc in links_to_add:
        # Check if already has this link
        if f'[[{link_target}]]' in old_section or f'[[{link_target}|' in old_section:
            continue
        new_lines.append(f"- [[{link_target}]] - {link_desc}")
        added.append(link_target)
    
    if not new_lines:
        return False, "Already has all links"
    
    # Add new lines at end of section
    new_section = old_section.rstrip() + "\n" + "\n".join(new_lines) + "\n"
    
    new_content = content[:see_also_match.start(2)] + new_section + content[see_also_match.end(2):]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"Added: {', '.join(added)}"

def main():
    games_path = VAULT_PATH / "Games"
    
    total_fixed = 0
    
    for folder in games_path.iterdir():
        if not folder.is_dir():
            continue
        
        folder_name = folder.name
        
        if folder_name in SERIES_LINKS:
            links_to_add = SERIES_LINKS[folder_name]
            for md_file in folder.glob("*.md"):
                success, msg = add_links_to_series(md_file, links_to_add)
                if success:
                    print(f"[{folder_name}] {md_file.name}: {msg}")
                    total_fixed += 1
    
    print(f"\n=== Summary ===")
    print(f"Pages updated: {total_fixed}")

if __name__ == "__main__":
    main()
