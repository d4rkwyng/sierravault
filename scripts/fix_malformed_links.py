#!/usr/bin/env python3
"""Fix malformed wiki links that have backslash before pipe: .md\| -> .md|"""

import os
import re
from pathlib import Path

VAULT_ROOT = Path(__file__).parent.parent / "vault"
EXCLUDE_DIRS = {"internal", ".obsidian", ".git", "Images"}

def fix_malformed_links(content):
    """Fix links like [[path/file.md\|Display]] -> [[path/file.md|Display]]"""
    # Pattern matches .md\ followed by |
    fixed = re.sub(r'\.md\\+\|', '.md|', content)
    return fixed

def process_file(filepath):
    """Process a single file and fix malformed links."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        fixed = fix_malformed_links(content)
        
        if fixed != original:
            filepath.write_text(fixed, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    files_fixed = 0
    total_files = 0
    
    for root, dirs, filenames in os.walk(VAULT_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in filenames:
            if f.endswith(".md"):
                total_files += 1
                filepath = Path(root) / f
                if process_file(filepath):
                    files_fixed += 1
                    print(f"Fixed: {filepath.relative_to(VAULT_ROOT)}")
    
    print(f"\n\nTotal files processed: {total_files}")
    print(f"Files fixed: {files_fixed}")

if __name__ == "__main__":
    main()
