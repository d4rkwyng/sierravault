#!/usr/bin/env python3
"""Fix duplicate ## See Also sections by merging them."""

import os
import re
import sys

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count occurrences
    count = content.count('## See Also')
    if count <= 1:
        return False
    
    # Split by ## See Also
    parts = content.split('## See Also')
    
    if len(parts) != 3:
        print(f"  Skipping {filepath} - unexpected structure ({len(parts)} parts)")
        return False
    
    before = parts[0]
    first_section = parts[1]
    second_section = parts[2]
    
    # The second section starts with the content after "## See Also"
    # We need to merge the content but remove the duplicate heading
    
    # Find where the second See Also section ends (at ## References or end of file)
    ref_match = re.search(r'\n## References', second_section)
    if ref_match:
        second_content = second_section[:ref_match.start()].strip()
        after_second = second_section[ref_match.start():]
    else:
        second_content = second_section.strip()
        after_second = ''
    
    # Merge: keep first heading, combine content
    # The second content usually has Series/Next links, append to first
    merged = before + '## See Also' + first_section.rstrip() + '\n' + second_content + '\n' + after_second
    
    # Clean up any triple+ newlines
    merged = re.sub(r'\n{3,}', '\n\n', merged)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(merged)
    
    return True

def main():
    vault_path = '/Users/woodd/Projects/sierravault/vault/Games'
    fixed = 0
    
    for root, dirs, files in os.walk(vault_path):
        for fname in files:
            if fname.endswith('.md'):
                fpath = os.path.join(root, fname)
                if fix_file(fpath):
                    fixed += 1
                    print(f"Fixed: {fpath}")
    
    print(f"\nTotal fixed: {fixed}")

if __name__ == '__main__':
    main()
