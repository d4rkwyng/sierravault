#!/usr/bin/env python3
"""Consolidate duplicate references in a markdown file.

Finds all reference definitions, identifies duplicate URLs, 
keeps only unique references with sequential numbering,
and updates all inline citations accordingly.
"""

import re
import sys
from pathlib import Path
from collections import OrderedDict


def consolidate_references(filepath: str) -> tuple[str, dict]:
    """Consolidate duplicate references in a markdown file.
    
    Returns:
        tuple: (new_content, stats_dict)
    """
    content = Path(filepath).read_text()
    
    # Find all reference definitions: [^ref-N]: [text](url)
    ref_pattern = re.compile(r'^\[(\^ref-\d+)\]:\s*\[([^\]]*)\]\(([^)]+)\)\s*(?:—.*)?$', re.MULTILINE)
    
    # Extract all references with their full definition
    refs = {}
    ref_full_lines = {}
    for match in ref_pattern.finditer(content):
        ref_id = match.group(1)  # ^ref-N
        text = match.group(2)
        url = match.group(3)
        full_line = match.group(0)
        refs[ref_id] = url
        ref_full_lines[ref_id] = full_line
    
    if not refs:
        print(f"No references found in {filepath}")
        return content, {"total": 0, "unique": 0, "duplicates": 0}
    
    # Group refs by URL to find duplicates
    url_to_refs = {}
    for ref_id, url in refs.items():
        if url not in url_to_refs:
            url_to_refs[url] = []
        url_to_refs[url].append(ref_id)
    
    # Count duplicates
    total_refs = len(refs)
    unique_urls = len(url_to_refs)
    duplicates = total_refs - unique_urls
    
    print(f"Found {total_refs} references, {unique_urls} unique URLs, {duplicates} duplicates")
    
    # Create mapping: old ref -> new ref number
    # Sort URLs by first appearance in document (lowest ref number)
    def first_ref_num(url):
        ref_ids = url_to_refs[url]
        nums = [int(r.replace('^ref-', '')) for r in ref_ids]
        return min(nums)
    
    sorted_urls = sorted(url_to_refs.keys(), key=first_ref_num)
    
    # Build old->new mapping
    old_to_new = {}
    new_ref_num = 1
    url_to_new_ref = {}
    
    for url in sorted_urls:
        new_ref_id = f"^ref-{new_ref_num}"
        url_to_new_ref[url] = new_ref_id
        for old_ref in url_to_refs[url]:
            old_to_new[old_ref] = new_ref_id
        new_ref_num += 1
    
    # Split content into body and references section
    # Find where references start (## References header)
    ref_section_match = re.search(r'^## References\s*\n', content, re.MULTILINE)
    if not ref_section_match:
        print("Could not find ## References section")
        return content, {"total": total_refs, "unique": unique_urls, "duplicates": duplicates}
    
    body = content[:ref_section_match.start()]
    
    # Update inline citations in body: [^ref-N] -> [^ref-M]
    def replace_citation(m):
        old_ref = m.group(1)
        new_ref = old_to_new.get(old_ref, old_ref)
        return f"[{new_ref}]"
    
    body = re.sub(r'\[(\^ref-\d+)\]', replace_citation, body)
    
    # Build new references section with unique refs only
    new_refs_lines = ["## References\n"]
    for url in sorted_urls:
        # Get the first ref that used this URL to preserve the original text
        first_ref = min(url_to_refs[url], key=lambda r: int(r.replace('^ref-', '')))
        original_line = ref_full_lines[first_ref]
        new_ref_id = url_to_new_ref[url]
        # Replace the old ref id with new one in the line
        new_line = re.sub(r'\[\^ref-\d+\]:', f'[{new_ref_id}]:', original_line)
        new_refs_lines.append(new_line)
    
    new_content = body + "\n".join(new_refs_lines) + "\n"
    
    stats = {
        "total": total_refs,
        "unique": unique_urls,
        "duplicates": duplicates
    }
    
    return new_content, stats


def main():
    if len(sys.argv) < 2:
        print("Usage: python consolidate_refs.py <file.md> [--dry-run]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    new_content, stats = consolidate_references(filepath)
    
    if dry_run:
        print(f"\n[DRY RUN] Would consolidate {stats['total']} refs to {stats['unique']} unique refs")
        print(f"Would remove {stats['duplicates']} duplicates")
    else:
        Path(filepath).write_text(new_content)
        print(f"\nConsolidated {stats['total']} refs to {stats['unique']} unique refs")
        print(f"Removed {stats['duplicates']} duplicates")
        print(f"Updated {filepath}")


if __name__ == "__main__":
    main()
