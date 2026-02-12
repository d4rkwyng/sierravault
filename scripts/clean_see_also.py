#!/usr/bin/env python3
"""Thoroughly clean See Also sections - remove all duplicate navigation styles."""

import os
import re

def clean_see_also(content):
    """Clean up See Also section, keeping only arrow-style nav + series overview."""
    
    see_also_match = re.search(r'(## See Also\n)(.*?)(\n## |\Z)', content, re.DOTALL)
    if not see_also_match:
        return content, False
    
    prefix = see_also_match.group(1)
    section = see_also_match.group(2)
    suffix = see_also_match.group(3)
    
    original_section = section
    
    # Check if we have arrow-style navigation
    has_arrow_prev = bool(re.search(r'←.*Previous', section))
    has_arrow_next = bool(re.search(r'→.*Next', section))
    
    # Remove **Previous:** lines if we have arrow-style prev
    if has_arrow_prev:
        section = re.sub(r'^- \*\*Previous:\*\*.*\n', '', section, flags=re.MULTILINE)
    
    # Remove **Next:** lines if we have arrow-style next
    if has_arrow_next:
        section = re.sub(r'^- \*\*Next:\*\*.*\n', '', section, flags=re.MULTILINE)
    
    # Remove "- Previous:" and "- Next:" lines (non-bold) if arrow versions exist
    if has_arrow_prev:
        section = re.sub(r'^- Previous:.*\n', '', section, flags=re.MULTILINE)
    if has_arrow_next:
        section = re.sub(r'^- Next:.*\n', '', section, flags=re.MULTILINE)
    
    # Remove "**See also:**" subsection header
    section = re.sub(r'^\*\*See also:\*\*\n', '', section, flags=re.MULTILINE)
    
    # Remove prose paragraphs (keep only list items starting with -)
    lines = section.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- ') or stripped == '':
            cleaned_lines.append(line)
    
    section = '\n'.join(cleaned_lines)
    
    # Clean up multiple blank lines
    section = re.sub(r'\n{3,}', '\n\n', section)
    section = section.strip() + '\n'
    
    if section != original_section:
        return content[:see_also_match.start(2)] + section + suffix, True
    
    return content, False

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content, changed = clean_see_also(content)
    
    if changed:
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
    
    print(f"Total fixed: {fixed}")

if __name__ == '__main__':
    main()
