#!/usr/bin/env python3
"""Generate GAME_INDEX.json mapping game pages to research folders."""
import json
import re
from pathlib import Path
from typing import Optional, Tuple


def slugify(title: str) -> str:
    """Convert game title to research folder slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return re.sub(r'-+', '-', slug).strip('-')


def extract_title_year(filename: str) -> Tuple[Optional[int], str]:
    """Parse 'YYYY - Title.md' format."""
    match = re.match(r'(\d{4})\s*-\s*(.+)\.md$', filename)
    if match:
        return int(match.group(1)), match.group(2)
    return None, filename.replace('.md', '')


def main():
    # Paths relative to sierravault root
    script_dir = Path(__file__).parent
    root = script_dir.parent.parent  # Up from internal/scripts to sierravault
    
    games_dir = root / "Games"
    research_dir = root / "internal" / "research" / "games"
    output_file = root / "internal" / "research" / "GAME_INDEX.json"
    
    mappings = []
    
    # Process all game pages
    for md_file in games_dir.rglob("*.md"):
        year, title = extract_title_year(md_file.name)
        slug = slugify(title)
        folder_exists = (research_dir / slug).exists()
        
        # Get relative path from root
        rel_path = md_file.relative_to(root)
        
        mappings.append({
            "page": str(rel_path),
            "folder": slug,
            "folder_exists": folder_exists,
            "title": title,
            "year": year
        })
    
    # Find orphan research folders (folders with no matching game page)
    existing_folders = set(f.name for f in research_dir.iterdir() if f.is_dir())
    mapped_folders = set(m["folder"] for m in mappings)
    orphan_folders = existing_folders - mapped_folders
    
    # Build output
    output = {
        "generated": "2026-01-30",
        "mappings": sorted(mappings, key=lambda x: x["page"]),
        "orphan_folders": sorted(list(orphan_folders)),
        "stats": {
            "total_pages": len(mappings),
            "pages_with_research": sum(1 for m in mappings if m["folder_exists"]),
            "pages_without_research": sum(1 for m in mappings if not m["folder_exists"]),
            "orphan_folders": len(orphan_folders)
        }
    }
    
    # Write output
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated {output_file}")
    print(f"Stats:")
    print(f"  Total game pages: {output['stats']['total_pages']}")
    print(f"  Pages with research: {output['stats']['pages_with_research']}")
    print(f"  Pages without research: {output['stats']['pages_without_research']}")
    print(f"  Orphan research folders: {output['stats']['orphan_folders']}")


if __name__ == "__main__":
    main()
