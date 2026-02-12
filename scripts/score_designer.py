#!/usr/bin/env python3
"""
Designer Page Scoring Script for SierraVault
Scores designer biography pages on completeness and quality.

Scoring Criteria (100 points total):
- Has proper frontmatter (title, type, companies) - 10 pts
- Has Overview section with career summary - 15 pts
- Has Career section with era-based headers and date ranges - 20 pts
- Games tables have "Title" column header (not "Game") - 5 pts
- Has Post-Sierra/Later Career section if applicable - 10 pts
- Has References section with 5+ unique sources - 20 pts
- No duplicate reference URLs - 10 pts
- Wiki links only to games that exist in vault - 10 pts

PASS = 80+, REVIEW = 60-79, FAIL = <60
"""

import sys
import re
import os
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse


# Path to the vault's Games directory
VAULT_ROOT = Path("/Users/woodd/Projects/sierravault/vault")
GAMES_DIR = VAULT_ROOT / "Games"


def get_all_game_files() -> set:
    """Build a set of all game file stems (without extension) in the vault."""
    games = set()
    for md_file in GAMES_DIR.rglob("*.md"):
        # Get the filename without extension
        games.add(md_file.stem)
        # Also add common variations (with/without year prefix)
        stem = md_file.stem
        # Extract just the game name after year prefix if present
        match = re.match(r'^\d{4}\s*-\s*(.+)$', stem)
        if match:
            games.add(match.group(1).strip())
    return games


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Extract YAML frontmatter from content."""
    frontmatter = {}
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        for line in fm_text.split('\n'):
            if ':' in line:
                key, _, value = line.partition(':')
                frontmatter[key.strip()] = value.strip().strip('"\'')
    return frontmatter


def extract_wiki_links(content: str) -> List[str]:
    """Extract all wiki links from content."""
    # Pattern matches [[link]] or [[link|alias]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    # Handle escaped pipes too: [[link\|alias]]
    pattern2 = r'\[\[([^\]\\]+)\\?\|[^\]]+\]\]'
    
    links = re.findall(r'\[\[([^\]|\\]+)', content)
    return links


def extract_reference_urls(content: str) -> List[str]:
    """Extract all URLs from reference section."""
    # Find references section
    ref_match = re.search(r'^## References\s*\n(.*?)(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
    if not ref_match:
        return []
    
    ref_section = ref_match.group(1)
    # Extract URLs
    url_pattern = r'https?://[^\s\)>\]]+[^\s\)>\.\,\]"]'
    urls = re.findall(url_pattern, ref_section)
    return urls


def count_unique_references(content: str) -> int:
    """Count unique reference footnotes."""
    # Count [^ref-N] patterns
    refs = re.findall(r'\[\^ref-\d+\]:', content)
    return len(set(refs))


def has_section(content: str, section_name: str) -> bool:
    """Check if a section header exists."""
    pattern = rf'^##\s+{re.escape(section_name)}\s*$'
    return bool(re.search(pattern, content, re.MULTILINE | re.IGNORECASE))


def has_career_section_with_eras(content: str) -> Tuple[bool, List[str]]:
    """Check for Career section with era-based subsections."""
    # First check if Career section exists
    if not has_section(content, "Career"):
        return False, []
    
    # Look for ### headers under Career that have years/eras
    # Pattern: ### Something (YYYY-YYYY) or ### Something Years (YYYY-YYYY)
    era_pattern = r'^###\s+.+(?:\(\d{4}[–-]\d{4}\)|\(\d{4}[–-](?:present|Present)\)|\bYears?\b|\bEra\b|\bPeriod\b)'
    eras = re.findall(era_pattern, content, re.MULTILINE | re.IGNORECASE)
    
    # Also check for ### headers with date ranges in any format
    date_headers = re.findall(r'^###\s+.+\d{4}', content, re.MULTILINE)
    
    all_eras = list(set(eras + date_headers))
    return len(all_eras) >= 2, all_eras


def has_post_sierra_section(content: str) -> bool:
    """Check if page has Post-Sierra or Later Career section."""
    patterns = [
        r'^###?\s+Post[- ]Sierra',
        r'^###?\s+Later Career',
        r'^###?\s+After Sierra',
        r'^###?\s+Post[- ]Microsoft',
        r'^###?\s+Freelance',
        r'^###?\s+Independent',
        r'^##\s+Legacy',  # Legacy section often covers post-Sierra
    ]
    for pattern in patterns:
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            return True
    return False


def check_games_table_headers(content: str) -> Tuple[bool, List[str]]:
    """Check that games tables use 'Title' not 'Game' as column header."""
    issues = []
    
    # Find table headers (lines with |---|)
    table_sections = re.findall(r'(\|[^\n]+\|\n\|[-:| ]+\|)', content)
    
    for table in table_sections:
        header_line = table.split('\n')[0]
        # Check if it has "Game" but not "Title"
        if re.search(r'\|\s*Game\s*\|', header_line, re.IGNORECASE):
            if not re.search(r'\|\s*Title\s*\|', header_line, re.IGNORECASE):
                issues.append("Table uses 'Game' instead of 'Title'")
    
    return len(issues) == 0, issues


def check_overview_quality(content: str) -> Tuple[int, str]:
    """Score the Overview section (0-15 points)."""
    if not has_section(content, "Overview"):
        return 0, "Missing Overview section"
    
    # Extract Overview section
    overview_match = re.search(r'^## Overview\s*\n(.*?)(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
    if not overview_match:
        return 0, "Empty Overview section"
    
    overview_text = overview_match.group(1).strip()
    word_count = len(overview_text.split())
    
    if word_count < 50:
        return 5, f"Overview too short ({word_count} words)"
    elif word_count < 100:
        return 10, f"Overview adequate ({word_count} words)"
    else:
        return 15, f"Overview comprehensive ({word_count} words)"


def score_designer_page(filepath: str, all_games: set) -> Dict:
    """Score a designer page and return detailed results."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    results = {
        'file': filename,
        'path': filepath,
        'scores': {},
        'issues': [],
        'total': 0
    }
    
    # 1. Frontmatter (10 pts)
    frontmatter = parse_frontmatter(content)
    fm_score = 0
    required_fields = ['title', 'type', 'companies']
    missing_fields = []
    for field in required_fields:
        if field in frontmatter and frontmatter[field]:
            fm_score += 3
        else:
            missing_fields.append(field)
    if fm_score >= 9:
        fm_score = 10
    
    results['scores']['frontmatter'] = fm_score
    if missing_fields:
        results['issues'].append(f"Missing frontmatter: {', '.join(missing_fields)}")
    
    # 2. Overview section (15 pts)
    overview_score, overview_note = check_overview_quality(content)
    results['scores']['overview'] = overview_score
    if overview_score < 15:
        results['issues'].append(overview_note)
    
    # 3. Career section with eras (20 pts)
    has_career, eras = has_career_section_with_eras(content)
    if has_career:
        career_score = 20
    elif has_section(content, "Career"):
        career_score = 10
        results['issues'].append(f"Career section lacks era-based headers (found: {len(eras)} era headers)")
    else:
        career_score = 0
        results['issues'].append("Missing Career section")
    results['scores']['career'] = career_score
    
    # 4. Games table headers (5 pts)
    tables_ok, table_issues = check_games_table_headers(content)
    if tables_ok:
        results['scores']['table_headers'] = 5
    else:
        results['scores']['table_headers'] = 0
        results['issues'].extend(table_issues)
    
    # 5. Post-Sierra section (10 pts)
    # Check if this is even applicable - does the person have post-Sierra career?
    has_post = has_post_sierra_section(content)
    # Check if there's evidence of post-Sierra work in the content
    post_sierra_indicators = ['after leaving Sierra', 'post-Sierra', 'later career', 
                              'after Sierra', 'left Sierra', 'departed Sierra',
                              'Microsoft', 'freelance', 'independent']
    has_post_career = any(ind.lower() in content.lower() for ind in post_sierra_indicators)
    
    if has_post:
        results['scores']['post_sierra'] = 10
    elif has_post_career:
        results['scores']['post_sierra'] = 0
        results['issues'].append("Has post-Sierra career but missing dedicated section")
    else:
        # N/A - full points if they only worked at Sierra
        results['scores']['post_sierra'] = 10
    
    # 6. References section (20 pts)
    ref_count = count_unique_references(content)
    if ref_count >= 5:
        results['scores']['references'] = 20
    elif ref_count >= 3:
        results['scores']['references'] = 10
        results['issues'].append(f"Only {ref_count} references (need 5+)")
    elif ref_count >= 1:
        results['scores']['references'] = 5
        results['issues'].append(f"Only {ref_count} references (need 5+)")
    else:
        results['scores']['references'] = 0
        results['issues'].append("No references found")
    
    # 7. No duplicate URLs (10 pts)
    urls = extract_reference_urls(content)
    unique_urls = set(urls)
    if len(urls) == len(unique_urls):
        results['scores']['no_duplicates'] = 10
    else:
        dup_count = len(urls) - len(unique_urls)
        results['scores']['no_duplicates'] = max(0, 10 - (dup_count * 2))
        results['issues'].append(f"{dup_count} duplicate reference URL(s)")
    
    # 8. Valid wiki links (10 pts)
    wiki_links = extract_wiki_links(content)
    invalid_links = []
    for link in wiki_links:
        # Clean up the link
        link_clean = link.strip()
        # Check if it's a game link (looks like a year-prefixed title)
        if re.match(r'^\d{4}\s*-', link_clean):
            # It's a game link - verify it exists
            found = False
            for game in all_games:
                if game.lower() == link_clean.lower() or link_clean.lower() in game.lower():
                    found = True
                    break
            if not found:
                invalid_links.append(link_clean)
    
    if len(invalid_links) == 0:
        results['scores']['valid_links'] = 10
    else:
        penalty = min(10, len(invalid_links) * 2)
        results['scores']['valid_links'] = max(0, 10 - penalty)
        if len(invalid_links) <= 3:
            results['issues'].append(f"Invalid wiki links: {', '.join(invalid_links[:3])}")
        else:
            results['issues'].append(f"{len(invalid_links)} invalid wiki links")
    
    # Calculate total
    results['total'] = sum(results['scores'].values())
    
    # Determine status
    if results['total'] >= 80:
        results['status'] = 'PASS'
    elif results['total'] >= 60:
        results['status'] = 'REVIEW'
    else:
        results['status'] = 'FAIL'
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Score SierraVault designer pages')
    parser.add_argument('paths', nargs='*', help='Specific files or directories to score')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    # Build games list for link validation
    print("Building games index...", file=sys.stderr)
    all_games = get_all_game_files()
    print(f"Found {len(all_games)} game files", file=sys.stderr)
    
    # Determine files to score
    files_to_score = []
    if args.paths:
        for path in args.paths:
            if os.path.isfile(path):
                files_to_score.append(path)
            elif os.path.isdir(path):
                files_to_score.extend(glob.glob(os.path.join(path, '*.md')))
    else:
        # Default: all designers
        designers_dir = VAULT_ROOT / "Designers"
        files_to_score = list(designers_dir.glob('*.md'))
    
    # Score all files
    results = []
    for filepath in sorted(files_to_score):
        result = score_designer_page(str(filepath), all_games)
        results.append(result)
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
        return
    
    # Print results
    pass_count = 0
    review_count = 0
    fail_count = 0
    
    for r in results:
        status_emoji = {'PASS': '✅', 'REVIEW': '⚠️', 'FAIL': '❌'}[r['status']]
        
        if r['status'] == 'PASS':
            pass_count += 1
        elif r['status'] == 'REVIEW':
            review_count += 1
        else:
            fail_count += 1
        
        print(f"{status_emoji} {r['file']}: {r['total']}/100 [{r['status']}]")
        
        if args.verbose or r['status'] != 'PASS':
            # Show score breakdown
            print(f"   Scores: FM={r['scores']['frontmatter']}/10 | OV={r['scores']['overview']}/15 | "
                  f"Career={r['scores']['career']}/20 | Tables={r['scores']['table_headers']}/5 | "
                  f"Post={r['scores']['post_sierra']}/10 | Refs={r['scores']['references']}/20 | "
                  f"NoDup={r['scores']['no_duplicates']}/10 | Links={r['scores']['valid_links']}/10")
            if r['issues']:
                for issue in r['issues'][:5]:
                    print(f"   ⚡ {issue}")
        print()
    
    # Summary
    print("=" * 60)
    print(f"SUMMARY: {len(results)} pages scored")
    print(f"  ✅ PASS (80+):   {pass_count}")
    print(f"  ⚠️  REVIEW (60-79): {review_count}")
    print(f"  ❌ FAIL (<60):   {fail_count}")
    
    if review_count + fail_count > 0:
        print("\nPages needing work:")
        for r in sorted(results, key=lambda x: x['total']):
            if r['status'] != 'PASS':
                print(f"  {r['total']:3d} - {r['file']}: {', '.join(r['issues'][:2])}")


if __name__ == '__main__':
    main()
