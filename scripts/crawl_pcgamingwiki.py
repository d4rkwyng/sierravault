#!/usr/bin/env python3
"""Crawl PCGamingWiki pages for Sierra games using ScraperAPI"""
import json
import os
import sys
import time
import httpx
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote

SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')

# PCGamingWiki URLs for flagship Sierra games
# Format: (game_slug, pcgw_page_name)
PCGW_GAMES = [
    # King's Quest Series
    ("roberta-williams-kings-quest-i-quest-for-the-crown", "King%27s_Quest"),
    ("kings-quest-ii-romancing-the-throne", "King%27s_Quest_II:_Romancing_the_Throne"),
    ("kings-quest-iv-the-perils-of-rosella", "King%27s_Quest_IV:_The_Perils_of_Rosella"),
    ("kings-quest-v-absence-makes-the-heart-go-yonder", "King%27s_Quest_V:_Absence_Makes_the_Heart_Go_Yonder!"),
    ("kings-quest-vi-heir-today-gone-tomorrow", "King%27s_Quest_VI:_Heir_Today,_Gone_Tomorrow"),
    ("kings-quest-vii-the-princeless-bride", "King%27s_Quest_VII:_The_Princeless_Bride"),
    ("kings-quest-viii-mask-of-eternity", "King%27s_Quest:_Mask_of_Eternity"),

    # Space Quest Series
    ("space-quest-i-roger-wilco-in-the-sarien-encounter", "Space_Quest:_Chapter_I_-_The_Sarien_Encounter"),
    ("space-quest-ii-vohauls-revenge", "Space_Quest_II:_Vohaul%27s_Revenge"),
    ("space-quest-iii-the-pirates-of-pestulon", "Space_Quest_III:_The_Pirates_of_Pestulon"),
    ("space-quest-iv-roger-wilco-and-the-time-rippers", "Space_Quest_IV:_Roger_Wilco_and_the_Time_Rippers"),
    ("space-quest-v-the-next-mutation", "Space_Quest_V:_The_Next_Mutation"),
    ("space-quest-6-roger-wilco-in-the-spinal-frontier", "Space_Quest_6:_Roger_Wilco_in_the_Spinal_Frontier"),

    # Leisure Suit Larry Series
    ("leisure-suit-larry-in-the-land-of-the-lounge-lizards", "Leisure_Suit_Larry_in_the_Land_of_the_Lounge_Lizards"),
    ("leisure-suit-larry-goes-looking-for-love-in-several-wrong-places", "Leisure_Suit_Larry_Goes_Looking_for_Love_(in_Several_Wrong_Places)"),
    ("leisure-suit-larry-iii-passionate-patti-in-pursuit-of-the-pulsating-pectorals", "Leisure_Suit_Larry_III:_Passionate_Patti_in_Pursuit_of_the_Pulsating_Pectorals"),
    ("leisure-suit-larry-5-passionate-patti-does-a-little-undercover-work", "Leisure_Suit_Larry_5:_Passionate_Patti_Does_a_Little_Undercover_Work"),
    ("leisure-suit-larry-6-shape-up-or-slip-out", "Leisure_Suit_Larry_6:_Shape_Up_or_Slip_Out!"),
    ("leisure-suit-larry-love-for-sail", "Leisure_Suit_Larry:_Love_for_Sail!"),

    # Police Quest Series
    ("police-quest-in-pursuit-of-the-death-angel", "Police_Quest:_In_Pursuit_of_the_Death_Angel"),
    ("police-quest-ii-the-vengeance", "Police_Quest_II:_The_Vengeance"),
    ("police-quest-iii-the-kindred", "Police_Quest_III:_The_Kindred"),
    ("police-quest-open-season", "Police_Quest:_Open_Season"),
    ("police-quest-swat", "Police_Quest:_SWAT"),

    # Quest for Glory Series
    ("quest-for-glory-i-so-you-want-to-be-a-hero", "Quest_for_Glory:_So_You_Want_to_Be_a_Hero"),
    ("quest-for-glory-ii-trial-by-fire", "Quest_for_Glory_II:_Trial_by_Fire"),
    ("quest-for-glory-iii-wages-of-war", "Quest_for_Glory_III:_Wages_of_War"),
    ("quest-for-glory-iv-shadows-of-darkness", "Quest_for_Glory_IV:_Shadows_of_Darkness"),
    ("quest-for-glory-v-dragon-fire", "Quest_for_Glory_V:_Dragon_Fire"),

    # Gabriel Knight Series
    ("gabriel-knight-sins-of-the-fathers", "Gabriel_Knight:_Sins_of_the_Fathers"),
    ("gabriel-knight-3-blood-of-the-sacred-blood-of-the-damned", "Gabriel_Knight_3:_Blood_of_the_Sacred,_Blood_of_the_Damned"),
    ("gabriel-knight-sins-of-the-fathers-20th-anniversary-edition", "Gabriel_Knight:_Sins_of_the_Fathers_-_20th_Anniversary_Edition"),

    # Phantasmagoria
    ("phantasmagoria", "Phantasmagoria"),
    ("phantasmagoria-a-puzzle-of-flesh", "Phantasmagoria:_A_Puzzle_of_Flesh"),

    # Other Sierra Adventures
    ("the-colonels-bequest", "The_Colonel%27s_Bequest"),
    ("the-dagger-of-amon-ra", "The_Dagger_of_Amon_Ra"),
    ("conquests-of-camelot-the-search-for-the-grail", "Conquests_of_Camelot:_The_Search_for_the_Grail"),
    ("conquests-of-the-longbow-the-legend-of-robin-hood", "Conquests_of_the_Longbow:_The_Legend_of_Robin_Hood"),
    ("freddy-pharkas-frontier-pharmacist", "Freddy_Pharkas:_Frontier_Pharmacist"),
    ("torins-passage", "Torin%27s_Passage"),
    ("shivers", "Shivers"),
    ("lighthouse-the-dark-being", "Lighthouse:_The_Dark_Being"),
]


def get_pcgw_url(page_name):
    """Build PCGamingWiki URL"""
    return f"https://www.pcgamingwiki.com/wiki/{page_name}"


def crawl_with_scraper(url, timeout=60):
    """Crawl URL using ScraperAPI"""
    if not SCRAPER_API_KEY:
        return None, "no_api_key"

    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"

    try:
        resp = httpx.get(api_url, timeout=timeout, follow_redirects=True)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Remove scripts/styles/navigation
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()

            # Try to get main content
            main = soup.find('div', {'id': 'mw-content-text'}) or soup.find('main') or soup
            text = main.get_text(separator='\n', strip=True)

            return text, "success"
        else:
            return None, f"http_{resp.status_code}"
    except Exception as e:
        return None, f"error:{str(e)[:50]}"


def save_source(game_slug, url, text):
    """Save crawled content to research folder"""
    game_dir = GAMES_RESEARCH_DIR / game_slug
    game_dir.mkdir(parents=True, exist_ok=True)

    file_path = game_dir / "pcgamingwiki.json"

    data = {
        "source_id": "pcgamingwiki",
        "url": url,
        "fetch_date": datetime.now().isoformat(),
        "fetch_status": "success",
        "source_type": "pcgamingwiki",
        "full_text": text[:50000] if text else ""
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    return file_path


def main():
    if not SCRAPER_API_KEY:
        print("ERROR: SCRAPER_API_KEY not set")
        sys.exit(1)

    # Filter to games that don't already have PCGamingWiki
    games_to_process = []
    for game_slug, page_name in PCGW_GAMES:
        game_dir = GAMES_RESEARCH_DIR / game_slug
        pcgw_file = game_dir / "pcgamingwiki.json"

        # Skip if already exists with good content
        if pcgw_file.exists():
            try:
                with open(pcgw_file) as f:
                    data = json.load(f)
                if data.get('fetch_status') == 'success' and len(data.get('full_text', '')) > 500:
                    continue
            except:
                pass

        games_to_process.append((game_slug, page_name))

    print(f"PCGamingWiki Crawler")
    print(f"Games to process: {len(games_to_process)}")
    print(f"Estimated ScraperAPI credits: {len(games_to_process)}")
    print()

    if '--dry-run' in sys.argv:
        print("DRY RUN - URLs that would be crawled:")
        for game_slug, page_name in games_to_process:
            print(f"  {game_slug}: {get_pcgw_url(page_name)}")
        return

    success = 0
    failed = 0

    for i, (game_slug, page_name) in enumerate(games_to_process):
        url = get_pcgw_url(page_name)
        print(f"[{i+1}/{len(games_to_process)}] {game_slug}...")

        text, status = crawl_with_scraper(url)

        if status == "success" and text and len(text) > 200:
            save_source(game_slug, url, text)
            print(f"  ✓ Success ({len(text)} chars)")
            success += 1
        else:
            print(f"  ✗ Failed: {status}")
            failed += 1

        time.sleep(2)

    print(f"\n=== COMPLETE ===")
    print(f"Success: {success}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
