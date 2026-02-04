#!/usr/bin/env python3
"""Fix broken references (Reference without URL) in game pages."""

import re
import sys
from pathlib import Path

# URL mappings for common sources
URL_MAPPINGS = {
    # MobyGames
    "the-incredible-machine": "https://www.mobygames.com/game/2473/the-incredible-machine/",
    "return-of-the-incredible-machine-contraptions": "https://www.mobygames.com/game/4087/return-of-the-incredible-machine-contraptions/",
    "metaltech-earthsiege-expansion-pack": "https://www.mobygames.com/game/24568/metaltech-earthsiege-expansion-pack/",
    "metaltech-earthsiege": "https://www.mobygames.com/game/1402/metaltech-earthsiege/",
    "tribes-2": "https://www.mobygames.com/game/3566/tribes-2/",
    "metaltech-earthsiege-speech-pack": "https://www.mobygames.com/game/25267/metaltech-earthsiege-speech-pack/",
    
    # Wikipedia
    "tribes-2-wiki": "https://en.wikipedia.org/wiki/Tribes_2",
    "the-incredible-machine-wiki": "https://en.wikipedia.org/wiki/The_Incredible_Machine_(1993_video_game)",
    "metaltech-earthsiege-wiki": "https://en.wikipedia.org/wiki/Metaltech:_Earthsiege",
    
    # Archive.org
    "tribes-2-archive": "https://archive.org/details/Tribes2UltimateGamePack",
    "the-incredible-machine-archive": "https://archive.org/details/TheIncredibleMachine_1020",
    "metaltech-earthsiege-archive": "https://archive.org/details/metaltech-earthsiege-complete-mr-abandonware",
    
    # MyAbandonware  
    "tribes-2-myabandonware": "https://www.myabandonware.com/game/tribes-2-bhu",
    "the-incredible-machine-myabandonware": "https://www.myabandonware.com/game/the-incredible-machine-1mg",
    "metaltech-earthsiege-expansion-pack-myabandonware": "https://www.myabandonware.com/game/metaltech-earthsiege-expansion-pack-2wb",
    "metaltech-earthsiege-myabandonware": "https://www.myabandonware.com/game/metaltech-earthsiege-2pi",
    
    # PCGamingWiki
    "tribes-2-pcgamingwiki": "https://www.pcgamingwiki.com/wiki/Tribes_2",
    "the-incredible-machine-pcgamingwiki": "https://www.pcgamingwiki.com/wiki/The_Incredible_Machine",
    
    # Other common sources
    "dynamix-fandom": "https://dynamix.fandom.com/wiki/",
    "collection-chamber-earthsiege": "https://collectionchamber.blogspot.com/p/metaltech-earthsiege.html",
    "sierra-help-earthsiege": "https://wiki.sierrahelp.com/index.php/Metaltech:_EarthSiege_Technical",
    "giant-bomb-earthsiege-exp": "https://www.giantbomb.com/metaltech-earthsiege-expansion-pack/3030-16608/",
    "gamespot-tribes-2": "https://www.gamespot.com/reviews/tribes-2-review/1900-2705268/",
    "ign-tribes-2": "https://www.ign.com/articles/2001/03/30/news-briefs-163",
    "eurogamer-tribes-2": "https://www.eurogamer.net/r-tribes2",
    "metacritic-tribes-2": "https://www.metacritic.com/game/tribes-2/",
    "filfre-tim": "https://www.filfre.net/2018/06/the-incredible-machine/",
    "gog-tim": "https://www.gog.com/game/the_incredible_machine_mega_pack",
}


def find_broken_refs(content: str) -> list:
    """Find references without proper URLs."""
    broken = []
    # Match references that don't have [Title](URL) format
    ref_pattern = r'\[\^ref-(\d+)\]:\s*(.+?)$'
    for match in re.finditer(ref_pattern, content, re.MULTILINE):
        ref_num = match.group(1)
        ref_text = match.group(2).strip()
        # Check if it has a URL (markdown link format)
        if not re.search(r'\[.+?\]\(https?://', ref_text):
            broken.append((ref_num, ref_text, match.start(), match.end()))
    return broken


def suggest_fix(ref_text: str, game_slug: str) -> str:
    """Suggest a fix for a broken reference."""
    text_lower = ref_text.lower()
    
    # Source-specific patterns
    source_urls = {
        "mobygames": URL_MAPPINGS.get(game_slug, "https://www.mobygames.com/"),
        "wikipedia": URL_MAPPINGS.get(f"{game_slug}-wiki", "https://en.wikipedia.org/"),
        "myabandonware": URL_MAPPINGS.get(f"{game_slug}-myabandonware", "https://www.myabandonware.com/"),
        "archive.org": URL_MAPPINGS.get(f"{game_slug}-archive", "https://archive.org/"),
        "pcgamingwiki": URL_MAPPINGS.get(f"{game_slug}-pcgamingwiki", "https://www.pcgamingwiki.com/"),
        "gog": "https://www.gog.com/",
        "ign": "https://www.ign.com/",
        "gamespot": "https://www.gamespot.com/",
        "eurogamer": "https://www.eurogamer.net/",
        "metacritic": "https://www.metacritic.com/",
        "dynamix fandom": URL_MAPPINGS.get("dynamix-fandom", "https://dynamix.fandom.com/"),
        "collection chamber": URL_MAPPINGS.get("collection-chamber-earthsiege", ""),
        "sierra help": URL_MAPPINGS.get("sierra-help-earthsiege", "https://wiki.sierrahelp.com/"),
        "giant bomb": URL_MAPPINGS.get("giant-bomb-earthsiege-exp", "https://www.giantbomb.com/"),
        "digital antiquarian": "https://www.filfre.net/",
        "gamefaqs": "https://gamefaqs.gamespot.com/",
        "tribesnext": "https://www.tribesnext.com/",
        "shacknews": "https://www.shacknews.com/",
        "rate your music": "https://rateyourmusic.com/",
        "tv tropes": "https://tvtropes.org/",
    }
    
    # Check for consolidated/internal refs that should be removed or replaced
    if any(x in text_lower for x in ["consolidated", "internal reference", "basic info", 
                                      "technical specs", "development notes", "trivia",
                                      "version history", "awards data", "credits data",
                                      "multiple sources", "various sources"]):
        return None  # Mark for removal
    
    # Find matching source
    for source, url in source_urls.items():
        if source in text_lower:
            # Extract the description part after the source name
            parts = ref_text.split(" - ", 1)
            if len(parts) == 2:
                source_name = parts[0].strip()
                desc = parts[1].strip()
                return f"[{source_name}]({url}) - {desc}"
            else:
                return f"[{ref_text}]({url})"
    
    return None  # No automatic fix available


def process_file(filepath: Path, dry_run: bool = True) -> int:
    """Process a single file and fix broken references."""
    content = filepath.read_text()
    broken = find_broken_refs(content)
    
    if not broken:
        return 0
    
    # Determine game slug from path
    game_slug = filepath.stem.lower()
    for part in filepath.parts:
        if part.lower() in ["games"]:
            continue
        slug = part.lower().replace(" ", "-").replace("'", "").replace(":", "")
        if slug:
            game_slug = slug
            break
    
    # Normalize game slug
    slug_map = {
        "return of the incredible machine - contraptions": "return-of-the-incredible-machine-contraptions",
        "1995 - metaltech - earthsiege expansion pack": "metaltech-earthsiege-expansion-pack",
        "1994 - metaltech - earthsiege speech pack": "metaltech-earthsiege-speech-pack",
        "2001 - tribes 2": "tribes-2",
        "1992 - the incredible machine": "the-incredible-machine",
    }
    
    fname_lower = filepath.stem.lower()
    for k, v in slug_map.items():
        if k in fname_lower or fname_lower.endswith(k):
            game_slug = v
            break
    
    print(f"\n{'='*60}")
    print(f"File: {filepath}")
    print(f"Game slug: {game_slug}")
    print(f"Found {len(broken)} broken references")
    
    to_remove = []
    fixes = []
    
    for ref_num, ref_text, start, end in broken:
        fix = suggest_fix(ref_text, game_slug)
        if fix is None:
            to_remove.append((ref_num, ref_text))
            print(f"  [REMOVE] ^ref-{ref_num}: {ref_text[:60]}...")
        else:
            fixes.append((ref_num, ref_text, fix))
            print(f"  [FIX] ^ref-{ref_num}: {fix[:60]}...")
    
    if dry_run:
        print(f"\nDry run - would fix {len(fixes)} and remove {len(to_remove)} refs")
        return len(broken)
    
    # Apply fixes
    new_content = content
    for ref_num, old_text, new_text in fixes:
        old_line = f"[^ref-{ref_num}]: {old_text}"
        new_line = f"[^ref-{ref_num}]: {new_text}"
        new_content = new_content.replace(old_line, new_line)
    
    filepath.write_text(new_content)
    print(f"Applied {len(fixes)} fixes")
    return len(fixes)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix broken references in game pages")
    parser.add_argument("files", nargs="*", help="Files to process (or use --all)")
    parser.add_argument("--all", action="store_true", help="Process all game files")
    parser.add_argument("--apply", action="store_true", help="Apply fixes (default is dry run)")
    args = parser.parse_args()
    
    vault = Path(__file__).parent.parent / "vault"
    
    if args.all:
        files = list(vault.glob("Games/**/*.md"))
    elif args.files:
        files = [Path(f) for f in args.files]
    else:
        # Default: process the known problem files
        files = [
            vault / "Games/Incredible Machine/2000 - Return of The Incredible Machine - Contraptions.md",
            vault / "Games/Metaltech/1995 - Metaltech - Earthsiege Expansion Pack.md",
            vault / "Games/Metaltech/1994 - Metaltech - Earthsiege Speech Pack.md",
            vault / "Games/Metaltech/2001 - Tribes 2.md",
            vault / "Games/Incredible Machine/1992 - The Incredible Machine.md",
        ]
    
    total_fixed = 0
    for f in files:
        if f.exists():
            total_fixed += process_file(f, dry_run=not args.apply)
    
    print(f"\n{'='*60}")
    print(f"Total broken references found: {total_fixed}")


if __name__ == "__main__":
    main()
