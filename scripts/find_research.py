#!/usr/bin/env python3
"""Find research folder for a game page, or vice versa."""
import os
import sys
import json
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: find_research.py <search query>")
        print("Example: find_research.py king's quest v")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:]).lower()
    
    # Find the index file
    script_dir = Path(__file__).parent
    internal_root = Path(os.environ.get("SIERRAVAULT_INTERNAL", script_dir.parent.parent / "sierravault-internal"))
    index_file = internal_root / "research" / "GAME_INDEX.json"
    
    if not index_file.exists():
        print(f"Error: Index file not found at {index_file}")
        print("Run generate_game_index.py first.")
        sys.exit(1)
    
    index = json.loads(index_file.read_text())
    
    found = False
    for m in index["mappings"]:
        if query in m["page"].lower() or query in m["folder"].lower() or query in m["title"].lower():
            found = True
            exists_icon = "✅" if m["folder_exists"] else "❌"
            print(f"Page:   {m['page']}")
            print(f"Title:  {m['title']}")
            print(f"Year:   {m['year']}")
            print(f"Folder: research/games/{m['folder']}/")
            print(f"Exists: {exists_icon}")
            print()
    
    if not found:
        print(f"No matches found for: {query}")
        
        # Check orphan folders
        for folder in index["orphan_folders"]:
            if query in folder.lower():
                print(f"\nFound in orphan folders:")
                print(f"  research/games/{folder}/")


if __name__ == "__main__":
    main()
