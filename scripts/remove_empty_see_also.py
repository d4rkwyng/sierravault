#!/usr/bin/env python3
"""
Remove empty See Also sections from game pages.
"""

import re
from pathlib import Path

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")

def remove_empty_see_also(filepath):
    """Remove See Also section if it's empty."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Match ## See Also followed by only whitespace until ## References or end
    # Pattern: ## See Also\n\n## References or ## See Also\n## References
    content = re.sub(r'\n## See Also\n+## References', '\n## References', content)
    content = re.sub(r'\n## See Also\n+## ', '\n## ', content)
    
    # Also handle case where See Also is at end of file with nothing after
    content = re.sub(r'\n## See Also\n*$', '', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    games_path = VAULT_PATH / "Games"
    removed = 0
    
    for md_file in games_path.rglob("*.md"):
        if remove_empty_see_also(md_file):
            print(f"Removed empty See Also: {md_file.relative_to(games_path)}")
            removed += 1
    
    print(f"\n=== Removed {removed} empty See Also sections ===")

if __name__ == "__main__":
    main()
