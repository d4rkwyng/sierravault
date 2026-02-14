#!/usr/bin/env python3
"""
Remove Developer/Publisher lines from See Also sections.
These belong in Game Info callout, not See Also.
"""

import re
from pathlib import Path

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")

def cleanup_see_also(filepath):
    """Remove Developer and Publisher lines from See Also."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove lines like "- [[Something]] - Developer" or "- [[Something]] - Publisher"
    # Keep lines with other descriptions like "Related series", "Creator", etc.
    content = re.sub(r'\n- \[\[[^\]]+\]\] - Developer\n', '\n', content)
    content = re.sub(r'\n- \[\[[^\]]+\]\] - Publisher\n', '\n', content)
    
    # Also handle cases at end of section (before ## References)
    content = re.sub(r'\n- \[\[[^\]]+\]\] - Developer\n\n## ', '\n\n## ', content)
    content = re.sub(r'\n- \[\[[^\]]+\]\] - Publisher\n\n## ', '\n\n## ', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    games_path = VAULT_PATH / "Games"
    fixed = 0
    
    for md_file in games_path.rglob("*.md"):
        if cleanup_see_also(md_file):
            print(f"Cleaned: {md_file.relative_to(games_path)}")
            fixed += 1
    
    print(f"\n=== Cleaned {fixed} files ===")

if __name__ == "__main__":
    main()
