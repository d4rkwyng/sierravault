#!/usr/bin/env python3
"""Fix broken wiki links in SierraVault."""

import os
import re
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent / "vault"

# Simple exact replacements
EXACT_FIXES = {
    # Full path links (Designers/Developers files)
    "[[Games/Laura Bow/1992 - Laura Bow in The Dagger of Amon Ra.md]]": "[[1992 - The Dagger of Amon Ra]]",
    "[[Games/Miscellaneous/1991 - Jones in the Fast Lane.md]]": "[[1990 - Jones in the Fast Lane]]",
    "[[Games/Hoyle/1993 - Hoyle Official Book of Games - Volume 5.md]]": "[[1996 - Hoyle Official Book of Games - Volume 5]]",
    "[[Games/Caesar/1993 - Caesar.md]]": "[[1992 - Caesar]]",
    "[[Games/Hoyle/1989 - Hoyle Official Book of Games - Volume 2.md]]": "[[1990 - Hoyle Official Book of Games - Volume 2]]",
    "[[Games/Hoyle/1990 - Hoyle Official Book of Games - Volume 3.md]]": "[[1991 - Hoyle Official Book of Games - Volume 3]]",
    "[[Games/Standalone/1991 - Jones in the Fast Lane.md]]": "[[1990 - Jones in the Fast Lane]]",
    "[[Games/INN/1992 - The Shadow of Yserbius.md]]": "[[1991 - The Shadow of Yserbius]]",
    "[[Games/Hoyle/1996 - Hoyle Crosswords.md]]": "[[2000 - Hoyle Crosswords]]",
    "[[Games/Spiritual Successors/2016 - Order of the Thorne - The King's Challenge.md]]": "[[2015 - Order of the Thorne - The King's Challenge]]",
    "[[Games/Education/1983 - Beginning Reading.md]]": "[[1982 - Alphabet Blocks|Beginning Reading]]",
    "[[Games/Strategy/1990 - Galactic Empire.md]]": "[[1979 - Galactic Empire]]",
    "[[Games/Hoyle/2008 - Hoyle Card Games.md]]": "[[2007 - Hoyle Card Games 2008]]",
    "[[Games/King's Quest/2015 - King's Quest (2015)]]": "[[2015 - King's Quest]]",
    "[[Developers/CrazyBunch]]": "CrazyBunch",
    "[[Designers/Doug MacNeill]]": "Doug MacNeill",
    
    # More missing games/links
    "[[1984 - The Ancient Art of War]]": "[[1984 - The Ancient Art of War|Ancient Art of War]]",
    "[[1984 - Transylvania]]": "[[1982 - Transylvania|Transylvania]]",
    "[[1991 - Hoyle Official Book of Games Volume 3]]": "[[1991 - Hoyle Official Book of Games - Volume 3]]",
    "[[1993 - The Even More! Incredible Machine]]": "[[1993 - The Incredible Machine 2|The Even More! Incredible Machine]]",
    "[[1988 - Abracadabra]]": "Abracadabra (1988)",
    "[[1992 - Crime City]]": "Crime City (1992)",
    "[[2007 - The Lord of the Rings Online]]": "The Lord of the Rings Online (2007)",
    "[[1989 - Kenny Dalglish Soccer Manager]]": "Kenny Dalglish Soccer Manager (1989)",
    
    # Companies without pages
    "[[Sierra Entertainment]]": "Sierra Entertainment",
    "[[Apple II]]": "Apple II",
    "[[Viva Media]]": "Viva Media",
    "[[Golden Sector]]": "Golden Sector",
    "[[Capcom]]": "Capcom",
    "[[Stainless Games]]": "Stainless Games",
    "[[Epyx]]": "Epyx",
    "[[CrazyBunch]]": "CrazyBunch",
    "[[Doug MacNeill]]": "Doug MacNeill",
    "[[1998 - NASCAR Racing 1999 Edition]]": "NASCAR Racing 1999 Edition",
    "[[2000 - NASCAR Racing 3 Craftsman Truck Series Expansion Pack]]": "NASCAR Racing 3 Craftsman Truck Series Expansion Pack",
    
    # Games that don't exist - remove wiki links
    "[[1984 - Transylvania]]": "Transylvania (1982)",
    "[[1984 - The Ancient Art of War]]": "The Ancient Art of War (1984)",
    "[[1991 - Hoyle Official Book of Games Volume 3]]": "[[1991 - Hoyle Official Book of Games - Volume 3]]",
    "[[1993 - The Even More! Incredible Machine]]": "[[1993 - The Even More Incredible Machine]]",
    "[[1988 - Abracadabra]]": "Abracadabra (1988)",
    "[[1992 - Crime City]]": "Crime City (1992)",
    "[[2007 - The Lord of the Rings Online]]": "The Lord of the Rings Online (2007)",
    "[[1989 - Kenny Dalglish Soccer Manager]]": "Kenny Dalglish Soccer Manager (1989)",
    
    # Full path to simple link (without .md usually already handled but adding more)
    "[[Games/Miscellaneous/1991 - Jones in the Fast Lane.md]]": "[[1990 - Jones in the Fast Lane]]",
    "[[Games/Hoyle/1993 - Hoyle Official Book of Games - Volume 5.md]]": "[[1996 - Hoyle Official Book of Games - Volume 5]]",
    "[[Games/Caesar/1993 - Caesar.md]]": "[[1992 - Caesar]]",
    "[[Games/Hoyle/1989 - Hoyle Official Book of Games - Volume 2.md]]": "[[1990 - Hoyle Official Book of Games - Volume 2]]",
    "[[Games/Hoyle/1990 - Hoyle Official Book of Games - Volume 3.md]]": "[[1991 - Hoyle Official Book of Games - Volume 3]]",
    "[[Games/Standalone/1991 - Jones in the Fast Lane.md]]": "[[1990 - Jones in the Fast Lane]]",
    "[[Games/INN/1992 - The Shadow of Yserbius.md]]": "[[1991 - The Shadow of Yserbius]]",
    "[[Games/Hoyle/1996 - Hoyle Crosswords.md]]": "[[2000 - Hoyle Crosswords]]",
    "[[Games/Spiritual Successors/2016 - Order of the Thorne - The King's Challenge.md]]": "[[2015 - Order of the Thorne - The King's Challenge]]",
    "[[Games/Education/1983 - Beginning Reading.md]]": "[[1982 - Alphabet Blocks|Beginning Reading]]",
    "[[Games/Strategy/1990 - Galactic Empire.md]]": "[[1979 - Galactic Empire]]",
    "[[Games/Hoyle/2008 - Hoyle Card Games.md]]": "[[2007 - Hoyle Card Games 2008]]",
    "[[Games/King's Quest/2015 - King's Quest (2015)]]": "[[2015 - King's Quest]]",
    "[[Developers/CrazyBunch]]": "CrazyBunch",
    "[[Designers/Doug MacNeill]]": "Doug MacNeill",
    
    # Year corrections (no alias)
    "[[1989 - Codename - Iceman]]": "[[1990 - Codename - Iceman]]",
    "[[1991 - Jones in the Fast Lane]]": "[[1990 - Jones in the Fast Lane]]",
    "[[1993 - Caesar]]": "[[1992 - Caesar]]",
    "[[1992 - The Shadow of Yserbius]]": "[[1991 - The Shadow of Yserbius]]",
    "[[1990 - Galactic Empire]]": "[[1979 - Galactic Empire]]",
    "[[2016 - Order of the Thorne - The King's Challenge]]": "[[2015 - Order of the Thorne - The King's Challenge]]",
    "[[1982 - Frogger]]": "[[1981 - Frogger]]",
    "[[1981 - Colossal Cave Adventure]]": "[[2023 - Colossal Cave 3D Adventure|1981 - Colossal Cave Adventure]]",
    "[[1983 - Ready, Set, Read!]]": "[[1992 - Ready, Set, Read with Bananas & Jack|1983 - Ready, Set, Read!]]",
    "[[1983 - Beginning Reading]]": "[[1982 - Alphabet Blocks|Beginning Reading]]",
    "[[1992 - Front Page Sports Football]]": "[[1992 - Front Page Sports Football 92]]",
    
    # Hoyle year fixes
    "[[1989 - Hoyle Official Book of Games - Volume 2]]": "[[1990 - Hoyle Official Book of Games - Volume 2]]",
    "[[1990 - Hoyle Official Book of Games - Volume 3]]": "[[1991 - Hoyle Official Book of Games - Volume 3]]",
    "[[1993 - Hoyle Official Book of Games - Volume 5]]": "[[1996 - Hoyle Official Book of Games - Volume 5]]",
    "[[1995 - Hoyle Solitaire]]": "[[1996 - Hoyle Solitaire]]",
    "[[1996 - Hoyle Crosswords]]": "[[2000 - Hoyle Crosswords]]",
    "[[1991 - Hoyle Official Book of Games Volume 3]]": "[[1991 - Hoyle Official Book of Games - Volume 3]]",
    "[[2008 - Hoyle Card Games]]": "[[2007 - Hoyle Card Games 2008]]",
    "[[2008 - Hoyle Card Games 2008]]": "[[2007 - Hoyle Card Games 2008]]",
    
    # Series links
    "[[SWAT]]": "[[1995 - Police Quest - SWAT|SWAT]]",
    "[[Gabriel Knight]]": "[[1993 - Gabriel Knight - Sins of the Fathers|Gabriel Knight]]",
    "[[Transylvania]]": "[[1984 - Transylvania|Transylvania]]",
    "[[1984 - Transylvania]]": "[[1982 - Transylvania|Transylvania]]",
    "[[Front Page Sports]]": "[[1992 - Front Page Sports Football 92|Front Page Sports]]",
    "[[Hoyle]]": "[[1989 - Hoyle Official Book of Games - Volume 1|Hoyle]]",
    "[[Hoyle Casino Series]]": "[[1996 - Hoyle Casino|Hoyle Casino]]",
    "[[The Ancient Art of War]]": "[[1984 - The Ancient Art of War|The Ancient Art of War]]",
    "[[Hi-Res Adventure Series]]": "[[1980 - Hi-Res Adventure 1 - Mystery House|Hi-Res Adventure Series]]",
    
    # Missing links - remove wiki formatting
    "[[1984 - Frogger II: ThreeeDeep!]]": "Frogger II: ThreeeDeep! (1984)",
    "[[1984 - Skyfox]]": "Skyfox (1984)",
    "[[2008 - Death Track - Resurrection]]": "Death Track: Resurrection (2008)",
    "[[2007 - The Lord of the Rings Online]]": "The Lord of the Rings Online (2007)",
    "[[1984 - Rendezvous with Rama]]": "Rendezvous with Rama (1984)",
    "[[1992 - After Dark]]": "After Dark (1992)",
    "[[1994 - More After Dark]]": "More After Dark (1994)",
    "[[Empire Earth II]]": "Empire Earth II (2005)",
    "[[TBA - Gobliiins 6]]": "Gobliiins 6 (TBA)",
    "[[Playtoons 5 - The Stone of Wakan]]": "Playtoons 5: The Stone of Wakan",
    "[[2001 - Hoyle Kids Games 2001]]": "[[2001 - Hoyle Kids Games]]",
    "[[2001 - Hoyle Slots]]": "[[2000 - Hoyle Slots and Video Poker|Hoyle Slots]]",
    "[[Breach 2]]": "Breach 2",
    "[[Lords of the Realm III]]": "Lords of the Realm III",
    "[[Tribes - Vengeance]]": "Tribes: Vengeance (2004)",
    "[[1998 - NASCAR Racing 1999 Edition]]": "NASCAR Racing 1999 Edition",
    "[[2000 - NASCAR Racing 3 Craftsman Truck Series Expansion Pack]]": "NASCAR Racing 3 Craftsman Truck Series Expansion Pack",
    "[[1988 - North-Sea Action]]": "North-Sea Action (1988)",
    "[[1997 - You Don't Know Jack - Volume 4 - The Ride]]": "You Don't Know Jack: Volume 4 - The Ride (1997)",
    "[[1999 - You Don't Know Jack - Volume 5]]": "You Don't Know Jack: Volume 5 (1999)",
    "[[1998 - Pro Pilot 99]]": "Sierra Pro Pilot 99 (1998)",
    "[[1998 - Driver's Education '99]]": "Driver's Education '99 (1998)",
    "[[2000 - Professional Bull Rider 2]]": "Professional Bull Rider 2 (2000)",
    "[[Transylvania III - Vanquish the Night]]": "Transylvania III: Vanquish the Night",
    "[[1996 - Diablo]]": "Diablo (1996)",
    "[[2000 - Diablo II]]": "Diablo II (2000)",
    "[[1993 - Stellar 7 - Draxons Revenge]]": "Stellar 7: Draxon's Revenge (1993)",
    "[[The Ancient Art of War in the Skies]]": "The Ancient Art of War in the Skies (1992)",
    "[[V for Victory - Velikiye Luki]]": "V for Victory: Velikiye Luki",
    "[[Merchant Colony]]": "Merchant Colony",
    "[[1992 - Take a Break! Crossword]]": "Take a Break! Crossword (1992)",
    "[[Team Fortress 2]]": "Team Fortress 2 (2007)",
    "[[2004 - Counter-Strike - Source]]": "Counter-Strike: Source (2004)",
    "[[2006 - Half-Life 2 - Episode One]]": "Half-Life 2: Episode One (2006)",
    "[[2001 - Acropolis]]": "Acropolis expansion",
    "[[2014 - Contraption Maker]]": "Contraption Maker (2014)",
    "[[1996 - IndyCar Racing II]]": "IndyCar Racing II (1996)",
    "[[Jawbreaker IV]]": "Jawbreaker IV",
    "[[2019 - Encore Card Games Collection]]": "Encore Card Games Collection (2019)",
    "[[1993 - Turbo Learning: Mega Math]]": "Turbo Learning: Mega Math (1993)",
    "[[1993 - Ready, Set, Read With Bananas and Jack]]": "[[1992 - Ready, Set, Read with Bananas & Jack|Ready, Set, Read With Bananas and Jack]]",
    "[[1993 - The Even More! Incredible Machine]]": "[[1993 - The Incredible Machine 2|The Even More! Incredible Machine]]",
    "[[1988 - Abracadabra]]": "Abracadabra (1988)",
    "[[1992 - Crime City]]": "Crime City (1992)",
    "[[1989 - Kenny Dalglish Soccer Manager]]": "Kenny Dalglish Soccer Manager (1989)",
    
    # Missing people/companies
    "[[Sierra Entertainment]]": "Sierra Entertainment",
    "[[Sega of America]]": "Sega of America",
    "[[John Garvin]]": "John Garvin",
    "[[Golden Sector]]": "Golden Sector",
    "[[Capcom]]": "Capcom",
    "[[David Kaemmer]]": "David Kaemmer",
    "[[Allen McPheeters]]": "Allen McPheeters",
    "[[Apple II]]": "Apple II",
    "[[Joe Ybarra]]": "Joe Ybarra",
    "[[Stainless Games]]": "Stainless Games",
    "[[César Bittar]]": "César Bittar",
    "[[Epyx]]": "Epyx",
    "[[Gary Owens]]": "Gary Owens",
    "[[Arthur C. Clarke]]": "Arthur C. Clarke",
    "[[LucasArts]]": "LucasArts",
    "[[Viva Media]]": "Viva Media",
    "[[[Himalaya Studios]]": "[[Himalaya Studios]]",
    "[[Vivendi Universal]]": "Vivendi Universal Games",
    
    # Site Index link fix
    "[[Site Index#Cancelled]]": "[[Site Index|Cancelled Games]]",
}

# Regex-based fixes for links with aliases
# Pattern: find wrong link target, preserve alias
REGEX_FIXES = [
    # Full path link fixes with aliases
    (r'\[\[Games/Laura Bow/1992 - Laura Bow in The Dagger of Amon Ra\.md\|', '[[1992 - The Dagger of Amon Ra|'),
    (r'\[\[Games/Miscellaneous/1991 - Jones in the Fast Lane\.md\|', '[[1990 - Jones in the Fast Lane|'),
    (r'\[\[Games/Hoyle/1993 - Hoyle Official Book of Games - Volume 5\.md\|', '[[1996 - Hoyle Official Book of Games - Volume 5|'),
    (r'\[\[Games/Caesar/1993 - Caesar\.md\|', '[[1992 - Caesar|'),
    (r'\[\[Games/Hoyle/1989 - Hoyle Official Book of Games - Volume 2\.md\|', '[[1990 - Hoyle Official Book of Games - Volume 2|'),
    (r'\[\[Games/Hoyle/1990 - Hoyle Official Book of Games - Volume 3\.md\|', '[[1991 - Hoyle Official Book of Games - Volume 3|'),
    (r'\[\[Games/Standalone/1991 - Jones in the Fast Lane\.md\|', '[[1990 - Jones in the Fast Lane|'),
    (r'\[\[Games/INN/1992 - The Shadow of Yserbius\.md\|', '[[1991 - The Shadow of Yserbius|'),
    (r'\[\[Games/Hoyle/1996 - Hoyle Crosswords\.md\|', '[[2000 - Hoyle Crosswords|'),
    (r"\[\[Games/Spiritual Successors/2016 - Order of the Thorne - The King's Challenge\.md\|", "[[2015 - Order of the Thorne - The King's Challenge|"),
    (r'\[\[Games/Education/1983 - Beginning Reading\.md\|', '[[1982 - Alphabet Blocks|'),
    (r'\[\[Games/Strategy/1990 - Galactic Empire\.md\|', '[[1979 - Galactic Empire|'),
    (r'\[\[Games/Hoyle/2008 - Hoyle Card Games\.md\|', '[[2007 - Hoyle Card Games 2008|'),
    (r"\[\[Games/King's Quest/2015 - King's Quest \(2015\)\|", '[[2015 - King\'s Quest|'),
    (r'\[\[Developers/CrazyBunch\|', '[[CrazyBunch|'),
    (r'\[\[Designers/Doug MacNeill\|', '[[Doug MacNeill|'),
    
    # Remove wiki formatting for companies/links without pages (aliased versions)
    (r'\[\[Sierra Entertainment\|([^\]]+)\]\]', r'\1'),
    (r'\[\[Apple II\|([^\]]+)\]\]', r'\1'),
    (r'\[\[Viva Media\|([^\]]+)\]\]', r'\1'),
    (r'\[\[Golden Sector\|([^\]]+)\]\]', r'\1'),
    (r'\[\[Capcom\|([^\]]+)\]\]', r'\1'),
    (r'\[\[Stainless Games\|([^\]]+)\]\]', r'\1'),
    (r'\[\[Epyx\|([^\]]+)\]\]', r'\1'),
    (r'\[\[CrazyBunch\|([^\]]+)\]\]', r'\1'),
    (r'\[\[Doug MacNeill\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1984 - Transylvania\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1984 - The Ancient Art of War\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1993 - The Even More! Incredible Machine\|([^\]]+)\]\]', r'[[\1]]'),
    (r'\[\[1988 - Abracadabra\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1992 - Crime City\|([^\]]+)\]\]', r'\1'),
    (r'\[\[2007 - The Lord of the Rings Online\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1989 - Kenny Dalglish Soccer Manager\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1998 - NASCAR Racing 1999 Edition\|([^\]]+)\]\]', r'\1'),
    (r'\[\[2000 - NASCAR Racing 3 Craftsman Truck Series Expansion Pack\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1991 - Hoyle Official Book of Games Volume 3\|([^\]]+)\]\]', r'[[1991 - Hoyle Official Book of Games - Volume 3|\1]]'),
    
    # Escaped pipe aliases (markdown tables)
    (r'\[\[1993 - The Even More! Incredible Machine\\?\|([^\]]+)\]\]', r'[[1993 - The Even More Incredible Machine|\1]]'),
    (r'\[\[1988 - Abracadabra\\?\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1992 - Crime City\\?\|([^\]]+)\]\]', r'\1'),
    (r'\[\[1989 - Kenny Dalglish Soccer Manager\\?\|([^\]]+)\]\]', r'\1'),
    

    # Year corrections that preserve aliases
    (r'\[\[1989 - Codename - Iceman\|', '[[1990 - Codename - Iceman|'),
    (r'\[\[1989 - Codename - Iceman\\?\|', '[[1990 - Codename - Iceman|'),
    (r'\[\[1991 - Jones in the Fast Lane\|', '[[1990 - Jones in the Fast Lane|'),
    (r'\[\[1991 - Jones in the Fast Lane\\?\|', '[[1990 - Jones in the Fast Lane|'),
    (r'\[\[1993 - Caesar\|', '[[1992 - Caesar|'),
    (r'\[\[1993 - Caesar\\?\|', '[[1992 - Caesar|'),
    (r'\[\[1992 - The Shadow of Yserbius\|', '[[1991 - The Shadow of Yserbius|'),
    (r'\[\[1992 - The Shadow of Yserbius\\?\|', '[[1991 - The Shadow of Yserbius|'),
    (r'\[\[1990 - Galactic Empire\|', '[[1979 - Galactic Empire|'),
    (r'\[\[1990 - Galactic Empire\\?\|', '[[1979 - Galactic Empire|'),
    (r'\[\[2016 - Order of the Thorne - The King\'s Challenge\|', '[[2015 - Order of the Thorne - The King\'s Challenge|'),
    (r'\[\[2016 - Order of the Thorne - The King\'s Challenge\\?\|', '[[2015 - Order of the Thorne - The King\'s Challenge|'),
    (r'\[\[1982 - Frogger\|', '[[1981 - Frogger|'),
    (r'\[\[1982 - Frogger\\?\|', '[[1981 - Frogger|'),
    (r'\[\[1993 - Hoyle Official Book of Games - Volume 5\|', '[[1996 - Hoyle Official Book of Games - Volume 5|'),
    (r'\[\[1993 - Hoyle Official Book of Games - Volume 5\\?\|', '[[1996 - Hoyle Official Book of Games - Volume 5|'),
    (r'\[\[1995 - Hoyle Solitaire\|', '[[1996 - Hoyle Solitaire|'),
    (r'\[\[1995 - Hoyle Solitaire\\?\|', '[[1996 - Hoyle Solitaire|'),
    (r'\[\[1983 - Ready, Set, Read!\|', '[[1992 - Ready, Set, Read with Bananas & Jack|'),
    (r'\[\[1983 - Ready, Set, Read!\\?\|', '[[1992 - Ready, Set, Read with Bananas & Jack|'),
    (r'\[\[1983 - Beginning Reading\|', '[[1982 - Alphabet Blocks|'),
    (r'\[\[1983 - Beginning Reading\\?\|', '[[1982 - Alphabet Blocks|'),
    (r'\[\[1981 - Colossal Cave Adventure\|', '[[2023 - Colossal Cave 3D Adventure|'),
    (r'\[\[1981 - Colossal Cave Adventure\\?\|', '[[2023 - Colossal Cave 3D Adventure|'),
    (r'\[\[2008 - Hoyle Card Games\|', '[[2007 - Hoyle Card Games 2008|'),
    (r'\[\[2008 - Hoyle Card Games\\?\|', '[[2007 - Hoyle Card Games 2008|'),
    (r'\[\[Site Index#Cancelled\|', '[[Site Index|'),
    (r'\[\[Site Index#Cancelled\\?\|', '[[Site Index|'),
    (r'\[\[1992 - Front Page Sports Football\|', '[[1992 - Front Page Sports Football 92|'),
    (r'\[\[1992 - Front Page Sports Football\\?\|', '[[1992 - Front Page Sports Football 92|'),
]

def fix_file(filepath: Path) -> tuple[int, list[str]]:
    """Fix broken links in a file. Returns (count of fixes, list of what was fixed)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    fixes_made = []
    
    # Apply exact string replacements
    for broken, fixed in EXACT_FIXES.items():
        if broken in content:
            count = content.count(broken)
            content = content.replace(broken, fixed)
            fixes_made.append(f"  {broken} → {fixed} ({count}x)")
    
    # Apply regex replacements
    for pattern, replacement in REGEX_FIXES:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            fixes_made.append(f"  regex: {pattern} → {replacement} ({len(matches)}x)")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return len(fixes_made), fixes_made
    
    return 0, []

def main():
    total_fixes = 0
    files_fixed = 0
    
    # Process all markdown files
    for md_file in VAULT_ROOT.rglob("*.md"):
        # Skip internal scripts
        if "internal" in str(md_file) and "scripts" in str(md_file):
            continue
            
        count, fixes = fix_file(md_file)
        if count > 0:
            print(f"\n{md_file.relative_to(VAULT_ROOT)}:")
            for fix in fixes:
                print(fix)
            total_fixes += count
            files_fixed += 1
    
    print(f"\n{'='*60}")
    print(f"Fixed {total_fixes} links in {files_fixed} files")

if __name__ == "__main__":
    main()
