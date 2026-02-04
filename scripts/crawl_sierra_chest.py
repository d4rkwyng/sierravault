#!/usr/bin/env python3
"""Crawl Sierra Chest pages for flagship Sierra games using ScraperAPI with render=true"""
import json
import os
import sys
import time
import hashlib
import httpx
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode

SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')

# Sierra Chest game URLs - organized by series
# Format: (game_slug, sierra_chest_id, description)
# Slugs match our research/ folder names exactly
SIERRA_CHEST_GAMES = [
    # King's Quest Series (using actual folder names)
    ("roberta-williams-kings-quest-i-quest-for-the-crown", 1, "King's Quest I: Quest for the Crown"),
    ("kings-quest-ii-romancing-the-throne", 2, "King's Quest II: Romancing the Throne"),
    # Note: KQ3 original not in our archive, only the Redux fan remake
    ("kings-quest-iv-the-perils-of-rosella", 4, "King's Quest IV: The Perils of Rosella"),
    ("kings-quest-v-absence-makes-the-heart-go-yonder", 5, "King's Quest V: Absence Makes the Heart Go Yonder"),
    ("kings-quest-vi-heir-today-gone-tomorrow", 6, "King's Quest VI: Heir Today, Gone Tomorrow"),
    ("kings-quest-vii-the-princeless-bride", 7, "King's Quest VII: The Princeless Bride"),
    ("kings-quest-viii-mask-of-eternity", 8, "King's Quest VIII: Mask of Eternity"),
    ("kings-quest-i-vga-remake", 232, "King's Quest I SCI Remake"),

    # Space Quest Series
    ("space-quest-i-roger-wilco-in-the-sarien-encounter", 9, "Space Quest I: The Sarien Encounter"),
    ("space-quest-ii-vohauls-revenge", 10, "Space Quest II: Vohaul's Revenge"),
    ("space-quest-iii-the-pirates-of-pestulon", 11, "Space Quest III: The Pirates of Pestulon"),
    ("space-quest-iv-roger-wilco-and-the-time-rippers", 12, "Space Quest IV: Roger Wilco and the Time Rippers"),
    ("space-quest-v-the-next-mutation", 13, "Space Quest V: The Next Mutation"),
    ("space-quest-6-roger-wilco-in-the-spinal-frontier", 14, "Space Quest 6: Roger Wilco in the Spinal Frontier"),
    # Note: SQ1 VGA folder doesn't exist in our archive yet

    # Leisure Suit Larry Series
    ("leisure-suit-larry-in-the-land-of-the-lounge-lizards", 24, "Leisure Suit Larry 1"),
    ("leisure-suit-larry-goes-looking-for-love-in-several-wrong-places", 25, "Leisure Suit Larry 2"),
    ("leisure-suit-larry-iii-passionate-patti-in-pursuit-of-the-pulsating-pectorals", 26, "Leisure Suit Larry 3"),
    ("leisure-suit-larry-5-passionate-patti-does-a-little-undercover-work", 27, "Leisure Suit Larry 5"),
    ("leisure-suit-larry-6-shape-up-or-slip-out", 28, "Leisure Suit Larry 6"),
    ("leisure-suit-larry-love-for-sail", 29, "Leisure Suit Larry 7: Love for Sail!"),
    ("leisure-suit-larry-1-in-the-land-of-the-lounge-lizards-vga", 536, "Leisure Suit Larry 1 VGA"),
    ("leisure-suit-larry-reloaded", 537, "Leisure Suit Larry Reloaded"),
    ("leisure-suit-larry-magna-cum-laude", 30, "Leisure Suit Larry: Magna Cum Laude"),

    # Police Quest Series
    ("police-quest-in-pursuit-of-the-death-angel", 20, "Police Quest 1"),
    ("police-quest-ii-the-vengeance", 21, "Police Quest 2: The Vengeance"),
    ("police-quest-iii-the-kindred", 22, "Police Quest 3: The Kindred"),
    ("police-quest-open-season", 23, "Police Quest 4: Open Season"),
    ("police-quest-swat", 69, "Police Quest: SWAT"),
    ("police-quest-swat-2", 70, "Police Quest: SWAT 2"),
    ("police-quest-sci-remake", 233, "Police Quest 1 VGA"),

    # Quest for Glory Series
    ("quest-for-glory-i-so-you-want-to-be-a-hero", 15, "Quest for Glory I EGA"),
    ("quest-for-glory-ii-trial-by-fire", 16, "Quest for Glory II: Trial by Fire"),
    ("quest-for-glory-iii-wages-of-war", 17, "Quest for Glory III: Wages of War"),
    ("quest-for-glory-iv-shadows-of-darkness", 18, "Quest for Glory IV: Shadows of Darkness"),
    ("quest-for-glory-v-dragon-fire", 19, "Quest for Glory V: Dragon Fire"),
    ("quest-for-glory-i-vga-remake", 293, "Quest for Glory I VGA"),

    # Gabriel Knight Series
    ("gabriel-knight-sins-of-the-fathers", 37, "Gabriel Knight: Sins of the Fathers"),
    ("gabriel-knight-3-blood-of-the-sacred-blood-of-the-damned", 39, "Gabriel Knight 3"),
    ("gabriel-knight-sins-of-the-fathers-20th-anniversary-edition", 532, "Gabriel Knight 20th Anniversary"),
    # Note: GK2 folder name needs verification

    # Phantasmagoria
    ("phantasmagoria", 40, "Phantasmagoria"),
    ("phantasmagoria-a-puzzle-of-flesh", 41, "Phantasmagoria 2: A Puzzle of Flesh"),

    # Laura Bow Series
    ("the-colonels-bequest", 35, "The Colonel's Bequest"),
    ("the-dagger-of-amon-ra", 36, "The Dagger of Amon Ra"),

    # Other Sierra Adventures
    ("conquests-of-camelot-the-search-for-the-grail", 31, "Conquests of Camelot"),
    ("conquests-of-the-longbow-the-legend-of-robin-hood", 32, "Conquests of the Longbow"),
    ("codename-iceman", 33, "Codename: ICEMAN"),
    ("manhunter-new-york", 56, "Manhunter: New York"),
    ("manhunter-san-francisco", 57, "Manhunter 2: San Francisco"),
    ("ecoquest-the-search-for-cetus", 42, "EcoQuest: The Search for Cetus"),
    ("ecoquest-lost-secret-of-the-rainforest", 43, "EcoQuest 2"),
    ("freddy-pharkas-frontier-pharmacist", 44, "Freddy Pharkas: Frontier Pharmacist"),
    ("torins-passage", 46, "Torin's Passage"),
    ("shivers", 47, "Shivers"),
    ("shivers-two-harvest-of-souls", 48, "Shivers II: Harvest of Souls"),
    ("lighthouse-the-dark-being", 49, "Lighthouse: The Dark Being"),
    ("rama", 50, "Rama"),
]

# Sierra Chest sections to crawl for each game
SECTIONS = ['general', 'walkthrough', 'maps', 'eggs', 'music', 'publications', 'making', 'tech', 'demos']


def get_sierra_chest_url(game_id, section='general'):
    """Build Sierra Chest URL for a game and section"""
    base = "https://www.sierrachest.com/index.php"
    params = {'a': 'games', 'id': game_id, 'fld': section}
    return f"{base}?{urlencode(params)}"


def crawl_with_scraper(url, timeout=60, use_render=False):
    """Crawl URL using ScraperAPI (render=false works for Sierra Chest)"""
    if not SCRAPER_API_KEY:
        return None, "no_api_key"

    # Sierra Chest doesn't need render=true, saves API credits (1 vs 25)
    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    if use_render:
        api_url += "&render=true"

    try:
        resp = httpx.get(api_url, timeout=timeout, follow_redirects=True)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Remove navigation/footer
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()

            # Try to get main content
            main = soup.find('div', {'id': 'content'}) or soup.find('main') or soup
            text = main.get_text(separator='\n', strip=True)

            return text, "success"
        else:
            return None, f"http_{resp.status_code}"
    except Exception as e:
        return None, f"error:{str(e)[:50]}"


def save_source(game_slug, source_id, url, text, section):
    """Save crawled content to research folder"""
    game_dir = GAMES_RESEARCH_DIR / game_slug
    game_dir.mkdir(parents=True, exist_ok=True)

    file_path = game_dir / f"{source_id}.json"

    data = {
        "source_id": source_id,
        "url": url,
        "fetch_date": datetime.now().isoformat(),
        "fetch_status": "success",
        "render_mode": True,
        "source_type": "sierra_chest",
        "section": section,
        "full_text": text[:50000] if text else ""
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    return file_path


def main():
    if not SCRAPER_API_KEY:
        print("ERROR: SCRAPER_API_KEY not set in environment")
        sys.exit(1)

    # Parse arguments
    sections_to_crawl = ['general']  # Default to just general
    if '--all-sections' in sys.argv:
        sections_to_crawl = SECTIONS

    games_to_process = SIERRA_CHEST_GAMES
    if len(sys.argv) > 1 and sys.argv[1] not in ['--all-sections', '--dry-run']:
        # Filter to specific game slug
        filter_slug = sys.argv[1]
        games_to_process = [g for g in SIERRA_CHEST_GAMES if filter_slug in g[0]]

    dry_run = '--dry-run' in sys.argv

    total_urls = len(games_to_process) * len(sections_to_crawl)
    print(f"Sierra Chest Crawler")
    print(f"Games: {len(games_to_process)}")
    print(f"Sections: {sections_to_crawl}")
    print(f"Total URLs: {total_urls}")
    print(f"Estimated ScraperAPI credits: {total_urls} (no render needed)")
    print()

    if dry_run:
        print("DRY RUN - URLs that would be crawled:")
        for game_slug, game_id, desc in games_to_process:
            for section in sections_to_crawl:
                url = get_sierra_chest_url(game_id, section)
                print(f"  {game_slug} [{section}]: {url}")
        return

    success = 0
    failed = 0
    skipped = 0

    for i, (game_slug, game_id, desc) in enumerate(games_to_process):
        game_dir = GAMES_RESEARCH_DIR / game_slug

        for section in sections_to_crawl:
            source_id = f"sierrachest_{section}"
            file_path = game_dir / f"{source_id}.json"

            # Skip if already exists with content
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        existing = json.load(f)
                    if existing.get('fetch_status') == 'success' and len(existing.get('full_text', '')) > 500:
                        print(f"[{i+1}/{len(games_to_process)}] {desc} [{section}] - SKIP (exists)")
                        skipped += 1
                        continue
                except:
                    pass

            url = get_sierra_chest_url(game_id, section)
            print(f"[{i+1}/{len(games_to_process)}] {desc} [{section}]...")

            text, status = crawl_with_scraper(url)

            if status == "success" and text and len(text) > 200:
                save_source(game_slug, source_id, url, text, section)
                print(f"  ✓ Success ({len(text)} chars)")
                success += 1
            else:
                print(f"  ✗ Failed: {status}")
                failed += 1

            time.sleep(2)  # Rate limit between requests

        # Progress update
        if (i + 1) % 10 == 0:
            print(f"\n=== Progress: {i+1}/{len(games_to_process)} games ===\n")

    print(f"\n=== COMPLETE ===")
    print(f"Success: {success}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
