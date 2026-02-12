#!/usr/bin/env python3
"""Remove duplicate Previous/Next links in See Also sections, keeping only arrow style."""

import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Find See Also section
    see_also_match = re.search(r'## See Also\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if not see_also_match:
        return False
    
    see_also = see_also_match.group(1)
    
    # Check if we have both styles
    has_old_style = bool(re.search(r'^- (Previous|Next):', see_also, re.MULTILINE))
    has_arrow_style = bool(re.search(r'\[\[.*[←→]', see_also))
    
    if not (has_old_style and has_arrow_style):
        return False
    
    # Remove old-style Previous/Next lines
    new_see_also = re.sub(r'^- Previous:.*\n', '', see_also, flags=re.MULTILINE)
    new_see_also = re.sub(r'^- Next:.*\n', '', new_see_also, flags=re.MULTILINE)
    
    # Also remove "- VGA Remake:" if there's already a VGA reference with arrow or in the list
    # Actually, keep VGA Remake - it's useful info
    
    # Clean up multiple blank lines
    new_see_also = re.sub(r'\n{3,}', '\n\n', new_see_also)
    
    new_content = content[:see_also_match.start(1)] + new_see_also + content[see_also_match.end(1):]
    
    if new_content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def main():
    vault_path = '/Users/woodd/Projects/sierravault/vault/Games'
    fixed = 0
    
    for root, dirs, files in os.walk(vault_path):
        for fname in files:
            if fname.endswith('.md'):
                fpath = os.path.join(root, fname)
                if fix_file(fpath):
                    fixed += 1
                    print(f"Fixed: {os.path.relpath(fpath, vault_path)}")
    
    print(f"\nTotal fixed: {fixed}")

if __name__ == '__main__':
    main()
