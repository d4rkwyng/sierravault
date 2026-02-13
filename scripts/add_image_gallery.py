#!/usr/bin/env python3
"""Add image gallery section to game pages from MobyGames images.

Usage:
    python add_image_gallery.py "path/to/game.md"
    python add_image_gallery.py --all        # Process all games with images
    python add_image_gallery.py --dry-run    # Preview without changes
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path
from typing import Optional, List, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
INTERNAL_ROOT = Path(os.environ.get("SIERRAVAULT_INTERNAL", REPO_ROOT.parent / "../Library/CloudStorage/ProtonDrive-woodd@mindtricks.io-folder/Assets/sierravault"))
IMAGES_DIR = INTERNAL_ROOT / "images" / "mobygames"
GAMES_DIR = REPO_ROOT / "vault" / "Games"


def slugify(title: str) -> str:
    """Convert a game title to a URL-friendly slug."""
    slug = title.lower()
    # Remove special characters except spaces and hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Collapse multiple hyphens
    return re.sub(r'-+', '-', slug).strip('-')


def extract_title_from_page(page_path: Path) -> str:
    """Extract the game title from a page's frontmatter or filename."""
    content = page_path.read_text(encoding='utf-8')
    
    # Try to get title from frontmatter
    if content.startswith('---'):
        frontmatter_end = content.find('---', 3)
        if frontmatter_end > 0:
            frontmatter = content[3:frontmatter_end]
            for line in frontmatter.split('\n'):
                if line.startswith('title:'):
                    title = line[6:].strip().strip('"\'')
                    return title
    
    # Fall back to filename (remove year prefix)
    name = page_path.stem
    # Pattern: "1990 - Game Title" or just "Game Title"
    match = re.match(r'\d{4}\s*-\s*(.+)', name)
    if match:
        return match.group(1)
    return name


def find_image_folder(title: str) -> Optional[Path]:
    """Find the MobyGames image folder for a game title."""
    slug = slugify(title)
    
    # Exclude fan games unless specifically looking for them
    FAN_GAME_MARKERS = ['redux', 'replicated', 'incinerations', 'lost-chapter', 'vohaul-strikes-back']
    
    # Slugs that are too generic for partial matching (would match wrong games)
    GENERIC_SLUGS = ['kings-quest', 'space-quest', 'police-quest', 'leisure-suit-larry', 
                     'quest-for-glory', 'gabriel-knight']
    
    def is_fan_game(folder_name: str) -> bool:
        return any(marker in folder_name for marker in FAN_GAME_MARKERS)
    
    # Direct match first (exact)
    folder = IMAGES_DIR / slug
    if folder.exists() and not is_fan_game(folder.name):
        return folder
    
    all_folders = [f for f in IMAGES_DIR.iterdir() if f.is_dir() and not is_fan_game(f.name)] if IMAGES_DIR.exists() else []
    
    # Try prefix variations - exact match only
    variations = [
        slug,
        f"{slug}-vga",
        f"{slug}-vga-remake",
        f"roberta-williams-{slug}",
    ]
    
    for var in variations:
        for folder in all_folders:
            if folder.name == var:
                return folder
    
    # Don't do partial matching for generic series names
    if slug in GENERIC_SLUGS:
        return None
    
    # Try partial match - slug is contained in folder name
    for var in variations:
        for folder in all_folders:
            if var in folder.name:
                return folder
    
    # Try key words matching for series games (e.g., "mask-of-eternity" in folder)
    # Extract distinctive part of title (last part after colon or dash)
    distinctive_parts = []
    if ':' in title:
        distinctive_parts.append(slugify(title.split(':')[-1]))
    if ' - ' in title:
        distinctive_parts.append(slugify(title.split(' - ')[-1]))
    
    # Also try the full slug minus common prefixes
    for prefix in ['kings-quest-', 'space-quest-', 'police-quest-', 'quest-for-glory-', 
                   'leisure-suit-larry-', 'gabriel-knight-']:
        if slug.startswith(prefix):
            distinctive_parts.append(slug[len(prefix):])
    
    for part in distinctive_parts:
        if len(part) > 5:  # Only match if distinctive part is meaningful
            for folder in all_folders:
                if part in folder.name:
                    return folder
    
    return None


def get_best_images(image_folder: Path, img_type: str, max_count: int = 6) -> List[Path]:
    """Get the best images from a folder, preferring DOS versions."""
    type_dir = image_folder / img_type
    if not type_dir.exists():
        return []
    
    all_images = list(type_dir.glob("*"))
    if not all_images:
        return []
    
    # Prefer DOS screenshots, then Windows, then others
    def platform_priority(img: Path) -> int:
        name = img.name.lower()
        if '-dos-' in name:
            return 0
        if '-windows-' in name:
            return 1
        if '-amiga-' in name:
            return 2
        if '-fm-towns-' in name:
            return 3
        return 4
    
    # For covers, prefer front covers
    def cover_priority(img: Path) -> int:
        name = img.name.lower()
        if 'front-cover' in name:
            return 0
        if 'back-cover' in name:
            return 1
        if 'spine' in name:
            return 3
        return 2
    
    if img_type == "covers":
        all_images.sort(key=lambda x: (cover_priority(x), platform_priority(x), x.name))
    else:
        all_images.sort(key=lambda x: (platform_priority(x), x.name))
    
    return all_images[:max_count]


def generate_gallery_section(image_folder: Path, max_screenshots: int = 6, max_covers: int = 3) -> str:
    """Generate a markdown Gallery section for Obsidian."""
    screenshots = get_best_images(image_folder, "screenshots", max_screenshots)
    covers = get_best_images(image_folder, "covers", max_covers)
    
    if not screenshots and not covers:
        return ""
    
    # Build relative path from Games folder to images
    rel_path = image_folder.relative_to(INTERNAL_ROOT)
    
    lines = ["## Gallery", ""]
    
    if covers:
        lines.append("### Cover Art")
        for img in covers:
            img_path = rel_path / "covers" / img.name
            lines.append(f"![[{img_path}|300]]")
        lines.append("")
    
    if screenshots:
        lines.append("### Screenshots")
        for img in screenshots:
            img_path = rel_path / "screenshots" / img.name
            lines.append(f"![[{img_path}|400]]")
        lines.append("")
    
    return "\n".join(lines)


def has_gallery(content: str) -> bool:
    """Check if page already has a Gallery section."""
    return "\n## Gallery" in content or "\n## Gallery\n" in content


def add_gallery_to_page(page_path: Path, gallery_section: str, dry_run: bool = False) -> bool:
    """Add a Gallery section to a game page before References."""
    content = page_path.read_text(encoding='utf-8')
    
    if has_gallery(content):
        return False  # Already has gallery
    
    # Find the References section to insert before it
    ref_patterns = [
        r'\n## References\n',
        r'\n## References\s*$',
        r'\n\[\^ref-1\]',  # First footnote
    ]
    
    insert_pos = None
    for pattern in ref_patterns:
        match = re.search(pattern, content)
        if match:
            insert_pos = match.start()
            break
    
    if insert_pos is None:
        # No References section found, append at end
        insert_pos = len(content)
    
    # Insert gallery before References
    new_content = content[:insert_pos] + "\n" + gallery_section + "\n" + content[insert_pos:]
    
    if dry_run:
        print(f"Would add gallery to: {page_path}")
        print(f"  Gallery: {len(gallery_section)} chars")
        return True
    
    page_path.write_text(new_content, encoding='utf-8')
    return True


def process_page(page_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
    """Process a single game page."""
    title = extract_title_from_page(page_path)
    image_folder = find_image_folder(title)
    
    if not image_folder:
        return False, f"No images found for: {title}"
    
    gallery = generate_gallery_section(image_folder)
    if not gallery:
        return False, f"Empty gallery for: {title}"
    
    if add_gallery_to_page(page_path, gallery, dry_run):
        return True, f"Added gallery from {image_folder.name}"
    else:
        return False, "Already has gallery"


def find_all_game_pages() -> List[Path]:
    """Find all game markdown pages."""
    pages = []
    for md_file in GAMES_DIR.rglob("*.md"):
        # Skip index files and non-game pages
        if md_file.name.startswith('_') or 'index' in md_file.name.lower():
            continue
        pages.append(md_file)
    return sorted(pages)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add image galleries to game pages")
    parser.add_argument("path", nargs="?", help="Path to a specific game page")
    parser.add_argument("--all", action="store_true", help="Process all games with images")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--series", help="Process all games in a series folder (e.g., 'King\\'s Quest')")
    args = parser.parse_args()
    
    if args.path:
        # Single page
        page = Path(args.path)
        if not page.exists():
            page = REPO_ROOT / args.path
        if not page.exists():
            print(f"Error: Page not found: {args.path}")
            sys.exit(1)
        success, msg = process_page(page, args.dry_run)
        print(f"{'✓' if success else '✗'} {page.name}: {msg}")
    
    elif args.series:
        # All games in a series
        series_dir = GAMES_DIR / args.series
        if not series_dir.exists():
            print(f"Error: Series folder not found: {args.series}")
            sys.exit(1)
        
        added = 0
        for page in sorted(series_dir.glob("*.md")):
            success, msg = process_page(page, args.dry_run)
            status = '✓' if success else '✗'
            print(f"{status} {page.name}: {msg}")
            if success:
                added += 1
        print(f"\nAdded galleries to {added} pages")
    
    elif args.all:
        # All games
        pages = find_all_game_pages()
        added = 0
        skipped = 0
        for page in pages:
            success, msg = process_page(page, args.dry_run)
            if success:
                print(f"✓ {page.relative_to(GAMES_DIR)}: {msg}")
                added += 1
            else:
                skipped += 1
        print(f"\n{'Would add' if args.dry_run else 'Added'} galleries to {added} pages ({skipped} skipped)")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
