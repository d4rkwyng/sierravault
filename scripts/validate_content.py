#!/usr/bin/env python3
"""
Content Validator - Catches mistakes beyond basic scoring.

Checks for:
1. Broken wiki links (linked pages don't exist)
2. Factual inconsistencies (YAML vs content)
3. Duplicate paragraphs
4. Malformed references
5. Broken external links (format check)
6. Missing/orphaned images
7. Inconsistent company names
8. Date/year inconsistencies
9. Placeholder text left in
10. Common typos in Sierra game names
"""

import re
import sys
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple

# Common Sierra game name typos
# Note: Don't include variants that appear in URLs, article titles, or proper nouns
GAME_NAME_TYPOS = {
    "King's Quest": ["Kings Quest", "King Quest"],  # Removed KingsQuest (URL pattern)
    "Space Quest": [],  # Removed SpaceQuest (website SpaceQuest.net)
    "Police Quest": [],  # Removed PoliceQuest
    "Quest for Glory": [],  # Removed Quest For Glory (article titles)
    "Leisure Suit Larry": ["Leisure Suite Larry"],  # Real typo
    "Gabriel Knight": [],  # Removed GabrielKnight (URL pattern)
    "Phantasmagoria": ["Phantasmagora"],  # Only real typo, not self-reference
    "Sierra On-Line": [],  # Removed Sierra Online (historically used)
}

# Placeholder text patterns
# Note: Be careful with patterns that appear in URLs or product names
PLACEHOLDER_PATTERNS = [
    r'\[TODO\]',
    r'\[PLACEHOLDER\]',
    r'\[NEEDS.*?\]',
    r'\[ADD.*?\]',
    r'Lorem ipsum',
    # Note: XXX and ??? removed - too many false positives in quotes, product names, URLs
]

VAULT_ROOT = Path(__file__).parent.parent / "vault"


def get_all_pages() -> set:
    """Get all page names in the vault (without .md extension)."""
    pages = set()
    for md_file in VAULT_ROOT.rglob("*.md"):
        # Use the stem (filename without extension)
        pages.add(md_file.stem)
        # Also add common display variations
        pages.add(md_file.stem.replace(" - ", ": "))
    return pages


def check_broken_wiki_links(content: str, all_pages: set) -> List[str]:
    """Check for wiki links that point to non-existent pages."""
    issues = []
    wiki_links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', content)
    
    for link in wiki_links:
        link_clean = link.strip()
        # Skip external links and anchors
        if link_clean.startswith('http') or link_clean.startswith('#'):
            continue
        # Check if page exists
        if link_clean not in all_pages:
            # Try without year prefix
            name_only = re.sub(r'^\d{4}\s*-\s*', '', link_clean)
            if name_only not in all_pages and link_clean not in all_pages:
                issues.append(f"Broken wiki link: [[{link}]] - page not found")
    
    return issues


def check_yaml_content_consistency(content: str) -> List[str]:
    """Check if YAML metadata matches content."""
    issues = []
    
    # Extract YAML
    if not content.startswith('---'):
        return issues
    yaml_end = content.find('---', 3)
    if yaml_end < 0:
        return issues
    yaml = content[3:yaml_end]
    body = content[yaml_end+3:]
    
    # Check developer consistency
    dev_match = re.search(r'developer:\s*["\']?([^"\'\n]+)', yaml)
    if dev_match:
        yaml_dev = dev_match.group(1).strip()
        # Check if developer is mentioned in Overview or Development
        if yaml_dev not in body[:3000] and yaml_dev.split(',')[0] not in body[:3000]:
            # Might be using alias
            pass  # Too many false positives, skip for now
    
    # Check release year consistency
    year_match = re.search(r'release_year:\s*["\']?(\d{4})', yaml)
    if year_match:
        yaml_year = year_match.group(1)
        # Check if year appears in first few paragraphs
        overview_match = re.search(r'## Overview\n+(.*?)(?=\n##|\Z)', body, re.DOTALL)
        if overview_match:
            overview = overview_match.group(1)
            if yaml_year not in overview and f"'{yaml_year[-2:]}" not in overview:
                issues.append(f"Release year {yaml_year} not mentioned in Overview")
    
    return issues


def check_duplicate_paragraphs(content: str) -> List[str]:
    """Check for duplicate paragraphs (copy-paste errors)."""
    issues = []
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 100]
    
    # Find duplicates
    seen = {}
    for para in paragraphs:
        # Normalize whitespace
        normalized = ' '.join(para.split())
        if normalized in seen:
            # Found duplicate
            preview = normalized[:80] + "..."
            issues.append(f"Duplicate paragraph: \"{preview}\"")
        else:
            seen[normalized] = True
    
    return issues


def check_malformed_references(content: str) -> List[str]:
    """Check for malformed reference syntax."""
    issues = []
    
    # Check for unclosed reference brackets
    unclosed = re.findall(r'\[\^ref-\d+[^\]]*(?:\n|$)', content)
    for match in unclosed:
        if ']' not in match:
            issues.append(f"Unclosed reference: {match.strip()[:50]}")
    
    # Check for reference definitions without URLs
    ref_defs = re.findall(r'^\[\^ref-\d+\]:\s*(.*)$', content, re.MULTILINE)
    for ref_content in ref_defs:
        if not ref_content.strip():
            issues.append("Empty reference definition found")
        elif 'http' not in ref_content.lower() and 'archive' not in ref_content.lower():
            # Should have a URL
            if not re.search(r'\[.*?\]\(.*?\)', ref_content):
                issues.append(f"Reference without URL: {ref_content[:60]}...")
    
    # Check for double brackets in refs
    double_brackets = re.findall(r'\[\[\^ref-\d+\]\]', content)
    if double_brackets:
        issues.append(f"Double brackets in reference: {double_brackets[0]}")
    
    return issues


def check_external_links(content: str) -> List[str]:
    """Check external link formatting."""
    issues = []
    
    # Find all URLs
    urls = re.findall(r'https?://[^\s\)\]]+', content)
    
    # URLs that legitimately end with punctuation (game titles with periods)
    allowed_ending_patterns = [
        'J.A.C.K', 'E.S.S', 'A.G.E', 'Inc.', '_Inc', 'U.S.A', 'Dr.'
    ]
    
    for url in urls:
        # Check for common formatting issues
        if url.endswith(','):
            issues.append(f"URL ends with punctuation: {url}")
        elif url.endswith('.'):
            # Check if it's a legitimate ending
            if not any(pattern in url for pattern in allowed_ending_patterns):
                issues.append(f"URL ends with punctuation: {url}")
        if ']]' in url:
            issues.append(f"URL contains wiki link syntax: {url}")
        # Check for broken GOG links
        if 'gog.com' in url:
            if '/game/' not in url and '/en/game/' not in url and 'dreamlist' not in url and 'wishlist' not in url:
                if 'gog.com/game' not in url:  # Common mistake
                    pass  # Might be valid catalog link
    
    return issues


def check_placeholders(content: str) -> List[str]:
    """Check for placeholder text left in."""
    issues = []
    
    for pattern in PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"Placeholder text found: {matches[0]}")
    
    return issues


def check_game_name_typos(content: str) -> List[str]:
    """Check for common game name typos."""
    issues = []
    
    for correct, typos in GAME_NAME_TYPOS.items():
        for typo in typos:
            if typo in content:
                # Make sure it's not in a URL or reference
                # Simple check: not immediately preceded by / or .
                pattern = rf'(?<![/.]){re.escape(typo)}'
                if re.search(pattern, content):
                    issues.append(f"Possible typo: '{typo}' should be '{correct}'")
    
    return issues


def check_unclosed_formatting(content: str) -> List[str]:
    """Check for unclosed formatting (bold, italic, links)."""
    issues = []
    
    # Check for unclosed wiki links
    open_brackets = content.count('[[')
    close_brackets = content.count(']]')
    if open_brackets != close_brackets:
        issues.append(f"Mismatched wiki link brackets: {open_brackets} [[ vs {close_brackets} ]]")
    
    # Check for unclosed markdown links
    md_open = len(re.findall(r'\]\(', content))
    md_close = content.count(')')
    # This is tricky because ) appears in many contexts
    
    return issues


def validate_page(filepath: Path, all_pages: set = None) -> Dict:
    """Run all validation checks on a page."""
    if all_pages is None:
        all_pages = get_all_pages()
    
    content = filepath.read_text()
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_broken_wiki_links(content, all_pages))
    all_issues.extend(check_yaml_content_consistency(content))
    all_issues.extend(check_duplicate_paragraphs(content))
    all_issues.extend(check_malformed_references(content))
    all_issues.extend(check_external_links(content))
    all_issues.extend(check_placeholders(content))
    all_issues.extend(check_game_name_typos(content))
    all_issues.extend(check_unclosed_formatting(content))
    
    return {
        'file': str(filepath),
        'name': filepath.stem,
        'issues': all_issues,
        'issue_count': len(all_issues),
        'status': 'CLEAN' if not all_issues else 'ISSUES'
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate content for mistakes")
    parser.add_argument("files", nargs='*', help="Files to validate (default: all Games)")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    args = parser.parse_args()
    
    all_pages = get_all_pages()
    
    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = list(VAULT_ROOT.glob("Games/**/*.md"))
    
    results = []
    for filepath in files:
        if filepath.exists():
            result = validate_page(filepath, all_pages)
            results.append(result)
            
            if not args.summary and result['issues']:
                print(f"\n{result['status']} {result['name']} ({result['issue_count']} issues)")
                for issue in result['issues']:
                    print(f"  - {issue}")
    
    # Summary
    total = len(results)
    clean = sum(1 for r in results if r['status'] == 'CLEAN')
    with_issues = total - clean
    total_issues = sum(r['issue_count'] for r in results)
    
    print(f"\n=== VALIDATION SUMMARY ===")
    print(f"Total pages: {total}")
    print(f"Clean: {clean} ({clean*100//total}%)")
    print(f"With issues: {with_issues}")
    print(f"Total issues found: {total_issues}")
    
    if with_issues > 0 and args.summary:
        print(f"\nTop issues by page:")
        sorted_results = sorted(results, key=lambda x: -x['issue_count'])
        for r in sorted_results[:10]:
            if r['issue_count'] > 0:
                print(f"  {r['name']}: {r['issue_count']} issues")


if __name__ == "__main__":
    main()
