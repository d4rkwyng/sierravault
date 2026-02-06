#!/usr/bin/env python3
"""
Fix broken GOG Dreamlist links in SierraVault pages.

Strategy:
1. Apply slug corrections (from API crawl fuzzy matching)
2. Keep verified working slugs as-is
3. Replace remaining broken links with generic dreamlist URL
"""

import json
import re
import sys
from pathlib import Path

# Load corrections from API crawl
SCRIPT_DIR = Path(__file__).parent
CORRECTIONS_FILE = SCRIPT_DIR.parent / "dreamlist_corrections.json"

# Slug corrections: old_slug -> correct_slug (from 90%+ fuzzy matches)
SLUG_CORRECTIONS = {
    "metaltech-battledrome": "metaltech-battledrome-1994",
    "3-d-ultra-nascar-pinball": "3-d-ultra-nascar-pinball-1998",
    "ecoquest-ii-lost-secret-of-the-rainforest": "ecoquest-ii-lost-secret-of-the-rainforest-1993",
    "ultima-escape-from-mt-drash": "ultima-escape-from-mt-drash-1983",
    "donald-ducks-playground": "donald-duck-s-playground-1984",
    "adiboo-pazirals-secret": "adiboo-paziral-s-secret-2003",
    "cohort-ii-fighting-for-rome": "cohort-ii-fighting-for-rome-1993",
    "the-rise-rule-of-ancient-empires": "the-rise-rule-of-ancient-empires-1996",
    "counter-strike-condition-zero": "counter-strike-condition-zero-2004",
    "police-quest-open-season": "police-quest-open-season-1993",
    "fire-hawk-thexder-the-second-contact": "fire-hawk-thexder-the-second-contact-1990",
    "front-page-sports-golf": "front-page-sports-golf-1997",
    "nascar-racing-2002-season": "nascar-racing-2002-season-2002",
    "3d-ultra-minigolf-adventures": "3d-ultra-minigolf-adventures-2006",
    "no-one-lives-forever-2-a-spy-in-harms-way": "no-one-lives-forever-2-a-spy-in-h-a-r-m-s-way",
    "birthright-the-gorgons-alliance": "birthright-the-gorgon-s-alliance",
    "3-d-ultra-minigolf-deluxe": "3-d-ultra-minigolf-deluxe-1998",
    "3-d-ultra-pinball-the-lost-continent": "3-d-ultra-pinball-the-lost-continent-1997",
    "cohort-fighting-for-rome": "cohort-fighting-for-rome-1991",
    "the-time-warp-of-dr-brain": "the-time-warp-of-dr-brain-1996",
    "fast-attack-high-tech-submarine-warfare": "fast-attack-high-tech-submarine-warfare-1996",
    "indianapolis-500-the-simulation": "indianapolis-500-the-simulation-1989",
    "winnie-the-pooh-in-the-hundred-acre-wood": "winnie-the-pooh-in-the-hundred-acre-wood-1986",
    "discovery-in-the-steps-of-columbus": "discovery-in-the-steps-of-columbus-1992",
    "pga-championship-golf-1999-edition": "pga-championship-golf-1999-edition-1999",
    "sierra-championship-boxing": "sierra-championship-boxing-1985",
    "mickeys-space-adventure": "mickey-s-space-adventure-1984",
    "learning-with-fuzzywomp": "learning-with-fuzzywomp-1984",
    "sid-als-incredible-toons": "sid-al-s-incredible-toons-1993",
    "alien-legacy": "alien-legacy-1994",
    "3-d-ultra-minigolf-adventures-2": "3d-ultra-minigolf-adventures-2006",
    "front-page-sports-trophy-bass-1995": "front-page-sports-trophy-bass-2-1996",
    "3-d-helicopter-simulator": "3-d-helicopter-simulator-1987",
    "hoyle-card-games-2008": "hoyle-card-games-2000",
    "dr-brain-action-reaction": "dr-brain-action-reaction-1999",
    "smart-games-word-puzzles-1": "smart-games-word-puzzles-1996",
    "nascar-racing-3": "nascar-racing-3-1999",
    "3-d-ultra-minigolf": "3d-ultra-minigolf-1997",
}

# Working slugs (exact matches from API + previously verified)
WORKING_SLUGS = {
    # From API exact matches (60)
    "3-d-ultra-pinball-1995",
    "3-d-ultra-pinball-creep-night-1996",
    "3-d-ultra-radio-control-racers",
    "3d-ultra-cool-pool-1999",
    "3d-ultra-lionel-traintown-1999",
    "a-10-tank-killer",
    "aces-of-the-deep-1994",
    "aces-of-the-pacific",
    "apple-cider-spider",
    "babylon-5-into-the-fire",
    "cannonball-blitz",
    "castle-of-dr-brain",
    "cluck-yegger-in-escape-from-the-planet-of-the-poultroid",
    "command-aces-of-the-deep",
    "counter-strike",
    "crazy-nick-s-software-picks-parlor-games-with-laura-bow",
    "curse-you-red-baron",
    "cyberstorm-2-corporate-wars",
    "dr-brain-thinking-games-puzzle-madness",
    "ecoquest-the-search-for-cetus",
    "half-life-blue-shift",
    "half-life-opposing-force",
    "hoyle-board-games-1998",
    "hoyle-classic-board-games",
    "hoyle-classic-card-games",
    "hoyle-majestic-chess-2003",
    "hoyle-official-book-of-games-volume-1",
    "hoyle-official-book-of-games-volume-2",
    "hoyle-official-book-of-games-volume-3",
    "indycar-racing-ii-1995",
    "jones-in-the-fast-lane",
    "jumpstart-advanced-3rd-grade-mystery-mountain",
    "jumpstart-advanced-4th-grade-haunted-island",
    "jumpstart-advanced-5th-grade-jo-hammet-kid-detective",
    "laser-surgeon-the-microscopic-mission",
    "leisure-suit-larry",
    "manhunter-2-san-francisco",
    "metaltech-earthsiege",
    "metaltech-earthsiege-expansion-pack",
    "metaltech-earthsiege-speech-pack",
    "nascar-craftsman-truck-series-racing",
    "pga-championship-golf-2000",
    "playtoons-1-uncle-archibald",
    "playtoons-2-the-case-of-the-counterfeit-colaborator",
    "playtoons-3-the-secret-of-the-castle",
    "playtoons-4-the-mandarine-prince",
    "ready-set-read-with-bananas-jack-1996",
    "robert-e-lee-civil-war-general-1996",
    "silent-thunder-a-10-tank-killer-ii",
    "spelling-blizzard-1994",
    "starsiege-tribes",
    "stellar-7-draxons-revenge",
    "swat-global-strike-team-2003",
    "the-ancient-art-of-war-at-sea-1987",
    "the-beverly-hillbillies",
    "the-bizarre-adventures-of-woodruff-and-the-schnibble",
    "the-black-cauldron-1986",
    "the-incredible-toon-machine-1994",
    "the-island-of-dr-brain",
    "the-lost-mind-of-dr-brain",
    "the-operative-no-one-lives-forever",
    "the-realm-online",
    "the-ruins-of-cawdor",
    "ultimate-soccer-manager-2-1996",
    "ultimate-soccer-manager-98-99-1999",
    "v-for-victory-d-day-utah-beach",
    "front-page-sports-baseball-pro-98",
    "front-page-sports-football-pro-97",
    "front-page-sports-football-pro-98",
    "gunman-chronicles",
    # Previously verified (from original list)
    "jones-in-the-fast-lane",
    "the-ruins-of-cawdor",
    "the-beverly-hillbillies",
    "laser-surgeon-the-microscopic-mission",
    "cannonball-blitz",
    "silent-thunder-a-10-tank-killer-ii",
    "apple-cider-spider",
    "cluck-yegger-in-escape-from-the-planet-of-the-poultroid",
    "half-life-opposing-force",
    "half-life-blue-shift",
    "gunman-chronicles",
    "aces-of-the-pacific",
    "command-aces-of-the-deep",
    "aces-of-the-deep-1994",
}

GENERIC_DREAMLIST = "https://www.gog.com/dreamlist"
DREAMLIST_PATTERN = re.compile(r'https://www\.gog\.com/dreamlist/game/([a-z0-9-]+)')


def fix_dreamlist_links(content: str, filepath: str) -> tuple[str, int, int, int]:
    """
    Fix Dreamlist links in content.
    
    Returns: (new_content, links_corrected, links_preserved, links_genericized)
    """
    corrected = 0
    preserved = 0
    genericized = 0
    
    def replace_link(match):
        nonlocal corrected, preserved, genericized
        slug = match.group(1)
        
        # Check if we have a correction
        if slug in SLUG_CORRECTIONS:
            corrected += 1
            new_slug = SLUG_CORRECTIONS[slug]
            return f"https://www.gog.com/dreamlist/game/{new_slug}"
        
        # Check if it's already working
        if slug in WORKING_SLUGS:
            preserved += 1
            return match.group(0)
        
        # Fall back to generic
        genericized += 1
        return GENERIC_DREAMLIST
    
    new_content = DREAMLIST_PATTERN.sub(replace_link, content)
    return new_content, corrected, preserved, genericized


def process_file(filepath: Path, dry_run: bool = True) -> tuple[int, int, int]:
    """Process a single file. Returns (corrected, preserved, genericized) counts."""
    content = filepath.read_text(encoding='utf-8')
    new_content, corrected, preserved, genericized = fix_dreamlist_links(content, str(filepath))
    
    total_changes = corrected + genericized
    if total_changes > 0:
        if dry_run:
            print(f"  [DRY RUN] {filepath.name}: {corrected} corrected, {preserved} kept, {genericized} genericized")
        else:
            filepath.write_text(new_content, encoding='utf-8')
            print(f"  ✓ {filepath.name}: {corrected} corrected, {preserved} kept, {genericized} genericized")
    
    return corrected, preserved, genericized


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fix broken GOG Dreamlist links')
    parser.add_argument('--apply', action='store_true', help='Actually modify files (default: dry run)')
    parser.add_argument('--vault', default='vault', help='Path to vault directory')
    args = parser.parse_args()
    
    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"Error: Vault path '{vault_path}' not found")
        sys.exit(1)
    
    dry_run = not args.apply
    if dry_run:
        print("🔍 DRY RUN - no files will be modified\n")
        print(f"Corrections available: {len(SLUG_CORRECTIONS)}")
        print(f"Working slugs: {len(WORKING_SLUGS)}")
        print()
    else:
        print("⚡ APPLYING FIXES\n")
    
    total_corrected = 0
    total_preserved = 0
    total_genericized = 0
    files_modified = 0
    
    for md_file in vault_path.rglob('*.md'):
        corrected, preserved, genericized = process_file(md_file, dry_run)
        if corrected + genericized > 0:
            files_modified += 1
        total_corrected += corrected
        total_preserved += preserved
        total_genericized += genericized
    
    print(f"\n{'Would' if dry_run else 'Did'}:")
    print(f"  Correct: {total_corrected} slugs (better URLs)")
    print(f"  Preserve: {total_preserved} working links")
    print(f"  Genericize: {total_genericized} broken links")
    print(f"  Files affected: {files_modified}")
    
    if dry_run and (total_corrected + total_genericized) > 0:
        print(f"\nRun with --apply to make changes")


if __name__ == '__main__':
    main()
