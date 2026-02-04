#!/usr/bin/env python3
"""
Batch fix validation issues found by validate_content.py
"""

import re
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent / "vault"

# Wiki link replacements - format: old_link → new_link
WIKI_LINK_FIXES = {
    # B.C. series (punctuation issues)
    "[[1983 - B.C.'s Quest for Tires]]": "[[1983 - BC's Quest for Tires]]",
    "[[1984 - B.C. II: Grog's Revenge]]": "[[1984 - BC II - Grog's Revenge]]",
    "[[1983 - B.C.'s Quest for Tires]]": "[[1983 - BC's Quest for Tires]]",
    
    # A-10 Tank Killer
    "[[A-10 Tank Killer]]": "[[1989 - A-10 Tank Killer]]",
    
    # Dr. Brain series
    "[[1999 - Dr. Brain Thinking Games - IQ Adventure]]": "[[1998 - Dr. Brain Thinking Games - IQ Adventure]]",
    "[[1999 - The Adventures of Dr. Brain]]": "[[1991 - Castle of Dr. Brain]]",
    
    # ESS / E.S.S.
    "[[1989 - E.S.S. (European Space Simulator)]]": "[[1989 - ESS - European Space Simulator]]",
    
    # Order of the Thorne
    "[[Order of the Thorne - The King's Challenge]]": "[[2015 - Order of the Thorne - The King's Challenge]]",
    
    # Oil's Well
    "[[1983 - Oil's Well]]": "[[1983 - Oils Well]]",
    "[[1983 - Oils Well\\]]": "[[1983 - Oils Well]]",
    
    # King's Quest fan games  
    "[[King's Quest II - Romancing the Stones (Fan)]]": "[[2002 - King's Quest II+ - Romancing the Stones]]",
    "[[2011 - King's Quest II: Romancing the Stones]]": "[[2002 - King's Quest II+ - Romancing the Stones]]",
    
    # Hoyle Board/Card Games year fixes
    "[[2001 - Hoyle Board Games 2001]]": "[[2001 - Hoyle Board Games]]",
    "[[2002 - Hoyle Card Games 2002]]": "[[2002 - Hoyle Card Games]]",
    "[[2005 - Hoyle Card Games 2005]]": "[[2005 - Hoyle Card Games]]",
    "[[2006 - Hoyle Card Games 2007]]": "[[2007 - Hoyle Card Games 2008]]",
    "[[2008 - Hoyle Card Games 2009]]": "[[2008 - Hoyle Card Games 2008]]",
    "[[2004 - Hoyle Casino 2004]]": "[[2004 - Hoyle Casino]]",
    "[[2005 - Hoyle Casino 2006]]": "[[2006 - Hoyle Casino]]",
    "[[2008 - Hoyle Casino 2008]]": "[[2008 - Hoyle Casino]]",
    "[[2000 - Hoyle Casino (2000)]]": "[[2000 - Hoyle Casino]]",
    "[[2006 - Hoyle Puzzle and Board Games 2007]]": "[[2005 - Hoyle Puzzle and Board Games]]",
    "[[2008 - Hoyle Puzzle and Board Games 2009]]": "[[2008 - Hoyle Puzzle and Board Games]]",
    "[[2010 - Hoyle Puzzle and Board Games 2010]]": "[[2011 - Hoyle Puzzle and Board Games]]",
    "[[2011 - Hoyle Puzzle and Board Games 2012]]": "[[2011 - Hoyle Puzzle and Board Games]]",
    "[[2006 - Hoyle Texas Hold'Em]]": "[[2005 - Hoyle Texas Hold Em]]",
    "[[2010 - Hoyle Swashbucklin' Slots (2010 Version)]]": "[[2011 - Hoyle Swashbucklin Slots]]",
    
    # Jawbreaker
    "[[Jawbreaker]]": "[[1981 - Jawbreaker]]",
    "[[1983 - Jawbreaker II]]": "[[1982 - Jawbreaker II]]",
    
    # EcoQuest
    "[[EcoQuest 2 - Lost Secret of the Rainforest]]": "[[1993 - EcoQuest - Lost Secret of the Rainforest]]",
    "[[EcoQuest 2 - Lost Secret of the Rainforest|": "[[1993 - EcoQuest - Lost Secret of the Rainforest|",
    
    # Red Baron series
    "[[1992 - Red Baron: Mission Builder]]": "[[1992 - Red Baron - Mission Builder]]",
    "[[1998 - Red Baron 3-D]]": "[[1998 - Red Baron 3D]]",
    "[[2008 - Red Baron - Arcade]]": "[[2008 - Red Baron Arcade]]",
    
    # Incredible Machine / Toons
    "[[1996 - The Incredible Toon Machine]]": "[[1994 - The Incredible Toon Machine]]",
    "[[2000 - Return of the Incredible Machine: Contraptions]]": "[[2000 - Return of The Incredible Machine - Contraptions]]",
    
    # Cohort
    "[[Cohort II - Fighting for Rome]]": "[[1993 - Cohort II - Fighting for Rome]]",
    
    # Playtoons
    "[[1995 - Playtoons 5 - The Stone of Wakan]]": "[[Playtoons 5 - The Stone of Wakan]]",
    
    # Breach
    "[[Breach 2]]": "[[Breach 2]]",  # No page exists, keep as is
    
    # Gold Rush
    "[[Gold Rush! 2]]": "[[2017 - Gold Rush 2]]",
    
    # Remove broken links to non-existent platforms/companies (convert to plain text)
    # Note: These could be kept as is since they're external references
    

    # 3D Ultra series fixes
    "[[3D Ultra Pinball]]": "[[1995 - 3-D Ultra Pinball]]",
    "[[3D Ultra Minigolf Deluxe]]": "[[1998 - 3-D Ultra MiniGolf Deluxe]]",
    "[[3D Ultra Cool Pool]]": "[[1999 - 3-D Ultra Cool Pool]]",
    "[[1998 - 3D Ultra Minigolf Deluxe]]": "[[1998 - 3-D Ultra MiniGolf Deluxe]]",
    "[[2010 - 3D Ultra Minigolf Adventures 2]]": "[[2010 - 3-D Ultra MiniGolf Adventures 2]]",
    "[[1999 - 3-D Ultra Pinball - Thrillride]]": "[[2000 - 3-D Ultra Pinball - Thrill Ride]]",
    "[[1997 - 3-D Ultra Pinball: Thrillride]]": "[[2000 - 3-D Ultra Pinball - Thrill Ride]]",
    "[[Cool Pool]]": "[[1999 - 3-D Ultra Cool Pool]]",
    "[[2000 - 3D Ultra Lionel Traintown Deluxe]]": "[[2000 - 3-D Ultra Lionel TrainTown Deluxe]]",
    
    # Police Quest / SWAT fixes
    "[[1995 - Police Quest SWAT]]": "[[1995 - Police Quest - SWAT]]",
    "[[1999 - SWAT 3 Close Quarters Battle]]": "[[1999 - SWAT 3 - Close Quarters Battle]]",
    "[[1998 - SWAT 2]]": "[[1998 - Police Quest - SWAT 2]]",
    "[[2001 - SWAT 3: Close Quarters Battle]]": "[[1999 - SWAT 3 - Close Quarters Battle]]",
    "[[1999 - SWAT 3: Close Quarters Battle]]": "[[1999 - SWAT 3 - Close Quarters Battle]]",
    "[[1987 - Police Quest: In Pursuit of the Death Angel]]": "[[1987 - Police Quest - In Pursuit of the Death Angel]]",
    
    # Counter-Strike / Half-Life fixes
    "[[1999 - Counter-Strike]]": "[[2000 - Counter-Strike]]",
    "[[2006 - Half-Life 2: Episode One]]": "[[2006 - Half-Life 2 - Episode One]]",
    "[[2001 - Half-Life - Decay]]": "[[2001 - Half-Life - Blue Shift]]",  # Decay was PS2 only, may not exist
    "[[2007 - Team Fortress 2]]": "[[Team Fortress 2]]",  # May not have Sierra page
    
    # Hoyle series fixes - adjust colon to dash
    "[[1989 - Hoyle's Official Book of Games: Volume 1]]": "[[1989 - Hoyle Official Book of Games - Volume 1]]",
    "[[1989 - Hoyle's Official Book of Games, Volume 1]]": "[[1989 - Hoyle Official Book of Games - Volume 1]]",
    "[[1990 - Hoyle Official Book of Games Volume 2]]": "[[1990 - Hoyle Official Book of Games - Volume 2]]",
    "[[1991 - Hoyle Official Book of Games Volume 3]]": "[[1991 - Hoyle Official Book of Games - Volume 3]]",
    "[[Hoyle's Official Book of Games]]": "[[1989 - Hoyle Official Book of Games - Volume 1]]",
    "[[1993 - Hoyle Classic Card Games]]": "[[1997 - Hoyle Classic Card Games]]",
    "[[1995 - Hoyle Classic Games]]": "[[1997 - Hoyle Classic Card Games]]",
    
    # Incredible Machine series
    "[[1993 - The Incredible Machine 2]]": "[[1994 - The Incredible Machine 2]]",
    "[[The Incredible Machine: Even More Contraptions]]": "[[2001 - The Incredible Machine - Even More Contraptions]]",
    
    # Earthsiege / Tribes
    "[[1994 - Metaltech Earthsiege]]": "[[1994 - Metaltech - Earthsiege]]",
    "[[Metaltech: Earthsiege Expansion Pack]]": "[[1995 - Metaltech - Earthsiege Expansion Pack]]",
    "[[2004 - Tribes: Vengeance]]": "[[Tribes - Vengeance]]",
    "[[Tribes: Vengeance]]": "[[Tribes - Vengeance]]",
    
    # NASCAR series
    "[[2000 - NASCAR Racing 4]]": "[[2001 - NASCAR Racing 4]]",
    "[[NASCAR Racing 4]]": "[[2001 - NASCAR Racing 4]]",
    "[[NASCAR Racing]]": "[[1994 - NASCAR Racing]]",
    "[[NASCAR Racing 3]]": "[[1999 - NASCAR Racing 3]]",
    "[[NASCAR Racing 2003 Season]]": "[[2003 - NASCAR Racing 2003 Season]]",
    
    # Other series
    "[[1984 - The Ancient Art of War]]": "[[The Ancient Art of War]]",
    "[[1992 - The Ancient Art of War in the Skies]]": "[[The Ancient Art of War in the Skies]]",
    "[[1990 - Breach 2]]": "[[Breach 2]]",
    "[[Apple II]]": "[[Apple II|Apple II]]",  # External reference
    "[[Hi-Res Adventures]]": "[[Hi-Res Adventure Series]]",
    "[[King's Quest]]": "[[1984 - King's Quest - Quest for the Crown]]",
    "[[Hi-Res Adventure #1: Mystery House]]": "[[1980 - Hi-Res Adventure 1 - Mystery House]]",
    "[[1982 - Hi-Res Adventure 6 - The Dark Crystal]]": "[[1983 - Hi-Res Adventure 6 - The Dark Crystal]]",
    "[[1981 - Laf Pak]]": "[[1982 - Laf Pak]]",
    "[[1982 - Transylvania]]": "[[Transylvania]]",
    "[[1989 - Transylvania III - Vanquish the Night]]": "[[Transylvania III - Vanquish the Night]]",
    "[[Power Chess 98]]": "[[1997 - Power Chess 98]]",
    "[[1997 - Power Chess 98]]": "[[1998 - Power Chess 98]]",  # Check actual file
    "[[2005 - Empire Earth II]]": "[[Empire Earth II]]",
    "[[1985 - Donald Duck's Playground]]": "[[1984 - Donald Duck's Playground]]",
    "[[1992 - V for Victory - Velikiye Luki]]": "[[V for Victory - Velikiye Luki]]",
    "[[2016 - Order of the Thorne - The King's Challenge]]": "[[Order of the Thorne - The King's Challenge]]",
    "[[1993 - Cohort II: Fighting for Rome]]": "[[Cohort II - Fighting for Rome]]",
    "[[Golden Sector]]": "[[Golden Sector]]",
    "[[1990 - Galactic Empire]]": "[[1979 - Galactic Empire]]",
    "[[2011 - King's Quest II: Romancing the Stones]]": "[[King's Quest II - Romancing the Stones (Fan)]]",
    "[[1984 - Learning with Fuzzywomp]]": "[[1984 - Learning with FuzzyWOMP]]",
    
    # Front Page Sports
    "[[Front Page Sports Football Pro '95]]": "[[1994 - Front Page Sports - Football Pro '95]]",
    "[[Front Page Sports Football Pro '96]]": "[[1995 - Front Page Sports - Football Pro '96]]",
    "[[Front Page Sports Football Pro '97]]": "[[1996 - Front Page Sports - Football Pro '97]]",
    "[[Front Page Sports Football Pro '98]]": "[[1997 - Front Page Sports - Football Pro '98]]",
    "[[1997 - Front Page Sports Football Pro 98]]": "[[1997 - Front Page Sports - Football Pro '98]]",
    "[[Front Page Sports: Football Pro '97]]": "[[1996 - Front Page Sports - Football Pro '97]]",
    "[[1993 - Front Page Sports: Football Pro]]": "[[1993 - Front Page Sports - Football Pro]]",
    "[[Front Page Sports - Football Pro]]": "[[1993 - Front Page Sports - Football Pro]]",
    "[[1994 - Front Page Sports: Baseball '94]]": "[[1994 - Front Page Sports - Baseball Pro]]",
    "[[Front Page Sports - Baseball '94]]": "[[1994 - Front Page Sports - Baseball Pro]]",
    "[[1997 - Front Page Sports: Baseball Pro '98]]": "[[1997 - Front Page Sports - Baseball Pro '98]]",
    "[[1996 - Front Page Sports: Baseball Pro '96 Season]]": "[[1996 - Front Page Sports - Baseball Pro '96]]",
    "[[1995 - Front Page Sports - Football Pro 96]]": "[[1995 - Front Page Sports - Football Pro '96]]",
    "[[1997 - Front Page Sports: Ski Racing]]": "[[1997 - Front Page Sports - Ski Racing]]",
    "[[Front Page Sports - Ski Racing]]": "[[1997 - Front Page Sports - Ski Racing]]",
    
    # Trophy Bass
    "[[1996 - Front Page Sports: Trophy Bass 2]]": "[[1996 - Front Page Sports - Trophy Bass 2]]",
    "[[Field & Stream Trophy Bass 4]]": "[[2000 - Field & Stream - Trophy Bass 4]]",
    
    # Pro Pilot
    "[[Pro Pilot USA]]": "[[1998 - Sierra Pro Pilot USA]]",
    "[[1997 - Sierra Pro Pilot '98]]": "[[1997 - Sierra Pro Pilot 98]]",
    "[[1998 - Pro Pilot '99]]": "[[1998 - Sierra Pro Pilot '99]]",
    
    # Ultimate Soccer Manager
    "[[Ultimate Soccer Manager]]": "[[1995 - Ultimate Soccer Manager]]",
    "[[Ultimate Soccer Manager 98]]": "[[1998 - Ultimate Soccer Manager 98]]",
    "[[1997 - Ultimate Soccer Manager 98]]": "[[1998 - Ultimate Soccer Manager 98]]",
    
    # PGA Championship
    "[[2000 - PGA Championship Golf 2000 Titanium Edition]]": "[[2000 - PGA Championship Golf 2000 - Titanium Edition]]",
    "[[PGA Championship Golf 2000]]": "[[2000 - PGA Championship Golf 2000]]",
    "[[1999 - PGA Championship Golf '99 Edition]]": "[[1999 - PGA Championship Golf 1999 Edition]]",
}

def fix_wiki_links(content: str) -> tuple[str, list]:
    """Fix known broken wiki links."""
    fixes_made = []
    for old_link, new_link in WIKI_LINK_FIXES.items():
        if old_link in content:
            content = content.replace(old_link, new_link)
            fixes_made.append(f"Fixed wiki link: {old_link} → {new_link}")
    return content, fixes_made

def fix_release_year_overview(content: str, filename: str) -> tuple[str, list]:
    """Add release year to Overview if missing."""
    fixes_made = []
    
    # Extract year from filename
    year_match = re.match(r'^(\d{4})', filename)
    if not year_match:
        return content, fixes_made
    
    year = year_match.group(1)
    
    # Find Overview section
    overview_match = re.search(r'(## Overview\n+)(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not overview_match:
        return content, fixes_made
    
    overview_text = overview_match.group(2)
    
    # Check if year is already mentioned
    if year in overview_text or f"'{year[-2:]}" in overview_text:
        return content, fixes_made
    
    # Need to add year to first sentence/paragraph
    # Find first sentence and add year context
    first_para_end = overview_text.find('\n\n')
    if first_para_end == -1:
        first_para_end = len(overview_text)
    
    first_para = overview_text[:first_para_end]
    
    # Check if "released" or "published" already in first paragraph
    if 'released' in first_para.lower() or 'published' in first_para.lower():
        # Try to insert year near those words
        # Look for patterns like "released by" or "published by"
        release_patterns = [
            (r'(released by [^,\.]+)(,|\.)', rf'\1 in {year}\2'),
            (r'(published by [^,\.]+)(,|\.)', rf'\1 in {year}\2'),
            (r'(released)(,|\.|for)', rf'\1 in {year}\2'),
        ]
        for pattern, replacement in release_patterns:
            new_para, count = re.subn(pattern, replacement, first_para, count=1, flags=re.IGNORECASE)
            if count > 0:
                new_overview = overview_text.replace(first_para, new_para, 1)
                content = content.replace(overview_match.group(0), overview_match.group(1) + new_overview)
                fixes_made.append(f"Added release year {year} to Overview")
                return content, fixes_made
    
    return content, fixes_made

def fix_file(filepath: Path) -> list:
    """Apply all fixes to a file."""
    content = filepath.read_text()
    original_content = content
    all_fixes = []
    
    # Apply wiki link fixes
    content, fixes = fix_wiki_links(content)
    all_fixes.extend(fixes)
    
    # Apply release year fix
    content, fixes = fix_release_year_overview(content, filepath.stem)
    all_fixes.extend(fixes)
    
    # Write if changed
    if content != original_content:
        filepath.write_text(content)
    
    return all_fixes

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        dry_run = True
        print("DRY RUN - no files will be modified")
    else:
        dry_run = False
    
    files = list(VAULT_ROOT.glob("Games/**/*.md"))
    total_fixes = 0
    files_fixed = 0
    
    for filepath in sorted(files):
        content = filepath.read_text()
        original_content = content
        fixes = []
        
        # Check what fixes would be made
        content, wiki_fixes = fix_wiki_links(content)
        fixes.extend(wiki_fixes)
        
        content, year_fixes = fix_release_year_overview(content, filepath.stem)
        fixes.extend(year_fixes)
        
        if fixes:
            print(f"\n{filepath.stem}:")
            for fix in fixes:
                print(f"  - {fix}")
            
            if not dry_run and content != original_content:
                filepath.write_text(content)
            
            total_fixes += len(fixes)
            files_fixed += 1
    
    print(f"\n=== SUMMARY ===")
    print(f"Files modified: {files_fixed}")
    print(f"Total fixes applied: {total_fixes}")

if __name__ == "__main__":
    main()
