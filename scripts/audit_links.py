#!/usr/bin/env python3
"""Audit purchase and download links across all game pages."""

import os
import re
from pathlib import Path
from collections import defaultdict

GAMES_DIR = Path(__file__).parent.parent / "vault" / "Games"

def analyze_file(filepath):
    """Analyze a game file for link types."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {
        'gog_store': len(re.findall(r'gog\.com/game/', content)),
        'gog_dreamlist': len(re.findall(r'gog\.com/dreamlist', content)),
        'steam': len(re.findall(r'store\.steampowered\.com', content)),
        'archive_org': len(re.findall(r'archive\.org', content)),
        'itch_io': len(re.findall(r'itch\.io', content)),
        'humble': len(re.findall(r'humblebundle\.com', content)),
    }

def main():
    results = {
        'dreamlist_only': [],  # Only GOG dreamlist, no real purchase options
        'has_steam': [],       # Has Steam links (need verification)
        'no_archive': [],      # Missing archive.org
        'has_purchase': [],    # Has real purchase options
    }
    
    for md_file in sorted(GAMES_DIR.rglob("*.md")):
        rel_path = md_file.relative_to(GAMES_DIR)
        analysis = analyze_file(md_file)
        
        has_real_purchase = (
            analysis['gog_store'] > 0 or 
            analysis['steam'] > 0 or 
            analysis['itch_io'] > 0 or
            analysis['humble'] > 0
        )
        
        if analysis['steam'] > 0:
            results['has_steam'].append(str(rel_path))
        
        if analysis['gog_dreamlist'] > 0 and not has_real_purchase:
            results['dreamlist_only'].append(str(rel_path))
        
        if analysis['archive_org'] == 0:
            results['no_archive'].append(str(rel_path))
        
        if has_real_purchase:
            results['has_purchase'].append(str(rel_path))
    
    print("=" * 60)
    print("LINK AUDIT SUMMARY")
    print("=" * 60)
    
    print(f"\n📦 Games with REAL purchase options: {len(results['has_purchase'])}")
    
    print(f"\n⚠️ Games with ONLY GOG Dreamlist (no real purchase): {len(results['dreamlist_only'])}")
    for p in results['dreamlist_only'][:20]:
        print(f"  - {p}")
    if len(results['dreamlist_only']) > 20:
        print(f"  ... and {len(results['dreamlist_only']) - 20} more")
    
    print(f"\n🔗 Games with Steam links (need verification): {len(results['has_steam'])}")
    for p in results['has_steam'][:10]:
        print(f"  - {p}")
    if len(results['has_steam']) > 10:
        print(f"  ... and {len(results['has_steam']) - 10} more")
    
    print(f"\n📁 Games MISSING archive.org links: {len(results['no_archive'])}")
    for p in results['no_archive'][:20]:
        print(f"  - {p}")
    if len(results['no_archive']) > 20:
        print(f"  ... and {len(results['no_archive']) - 20} more")
    
    # Save detailed lists for processing
    with open("/tmp/audit_dreamlist_only.txt", "w") as f:
        f.write("\n".join(results['dreamlist_only']))
    with open("/tmp/audit_has_steam.txt", "w") as f:
        f.write("\n".join(results['has_steam']))
    with open("/tmp/audit_no_archive.txt", "w") as f:
        f.write("\n".join(results['no_archive']))
    
    print("\n\nDetailed lists saved to /tmp/audit_*.txt")

if __name__ == "__main__":
    main()
