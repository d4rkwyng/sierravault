#!/usr/bin/env python3
"""Fix last_updated timestamps to match git commit dates."""

import subprocess
from pathlib import Path
import re
import sys

def get_git_date(filepath: Path) -> str:
    """Get the last git commit date for a file."""
    result = subprocess.run(
        ['git', 'log', '-1', '--format=%cs', '--', str(filepath)],
        capture_output=True, text=True, cwd=filepath.parent
    )
    return result.stdout.strip() if result.returncode == 0 else None

def fix_timestamps(dry_run=True):
    """Scan all game pages and fix mismatched timestamps."""
    games_dir = Path(__file__).parent.parent / 'vault' / 'Games'
    fixed = 0
    mismatched = []
    
    for md_file in games_dir.rglob('*.md'):
        content = md_file.read_text()
        
        # Extract current last_updated from YAML
        match = re.search(r'^last_updated:\s*(\d{4}-\d{2}-\d{2})', content, re.MULTILINE)
        if not match:
            continue
            
        yaml_date = match.group(1)
        git_date = get_git_date(md_file)
        
        if not git_date:
            continue
            
        if yaml_date != git_date:
            mismatched.append((md_file.name, yaml_date, git_date))
            
            if not dry_run:
                new_content = re.sub(
                    r'^(last_updated:\s*)\d{4}-\d{2}-\d{2}',
                    f'\\g<1>{git_date}',
                    content,
                    count=1,
                    flags=re.MULTILINE
                )
                md_file.write_text(new_content)
                fixed += 1
    
    # Print results
    print(f"Found {len(mismatched)} mismatched timestamps")
    if mismatched:
        print("\nMismatches (first 20):")
        for name, yaml, git in mismatched[:20]:
            print(f"  {name}: YAML={yaml} Git={git}")
        if len(mismatched) > 20:
            print(f"  ... and {len(mismatched) - 20} more")
    
    if not dry_run:
        print(f"\nFixed {fixed} files")
    else:
        print("\n(Dry run - use --fix to apply changes)")

if __name__ == '__main__':
    dry_run = '--fix' not in sys.argv
    fix_timestamps(dry_run)
