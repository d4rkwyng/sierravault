#!/usr/bin/env python3
"""
Suggest wiki links for entities that have pages in the vault.

Scans markdown files and suggests where to add [[wiki links]] for:
- Games (from Games/ folder)
- Designers (from Designers/ folder)
- Developers (from Developers/ folder)
- Publishers (from Publishers/ folder)

Usage:
    python3 suggest_links.py <file.md>              # Check single file
    python3 suggest_links.py <file.md> --fix        # Auto-fix file
    python3 suggest_links.py --scan Games/          # Scan directory
    python3 suggest_links.py --scan Games/ --fix    # Auto-fix directory
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Repository root (parent of internal/)
REPO_ROOT = Path(__file__).parent.parent


def load_entities() -> Dict[str, Set[str]]:
    """Load all entity names from the vault folders."""
    entities = {
        'designers': set(),
        'developers': set(),
        'publishers': set(),
        'games': set(),
    }

    # Designers
    designers_dir = REPO_ROOT / "Designers"
    if designers_dir.exists():
        for f in designers_dir.glob("*.md"):
            name = f.stem  # "Roberta Williams"
            entities['designers'].add(name)

    # Developers
    developers_dir = REPO_ROOT / "Developers"
    if developers_dir.exists():
        for f in developers_dir.glob("*.md"):
            name = f.stem  # "Sierra On-Line"
            entities['developers'].add(name)

    # Publishers
    publishers_dir = REPO_ROOT / "Publishers"
    if publishers_dir.exists():
        for f in publishers_dir.glob("*.md"):
            name = f.stem
            entities['publishers'].add(name)

    # Games - extract title from filename (after year prefix)
    games_dir = REPO_ROOT / "Games"
    if games_dir.exists():
        for f in games_dir.rglob("*.md"):
            stem = f.stem  # "1984 - King's Quest - Quest for the Crown"
            # Extract title after "YEAR - "
            match = re.match(r'^\d{4}\s*-\s*(.+)$', stem)
            if match:
                title = match.group(1)
                entities['games'].add(title)
            else:
                # Non-standard naming, use full stem
                entities['games'].add(stem)

    return entities


def extract_existing_links(content: str) -> Set[str]:
    """Extract all existing wiki link targets from content."""
    # Match [[link]] and [[link|display]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    matches = re.findall(pattern, content)
    return set(matches)


def find_linkable_mentions(content: str, entities: Dict[str, Set[str]], existing_links: Set[str]) -> List[Tuple[str, str, int, int]]:
    """
    Find mentions of entities that could be linked.

    Returns list of (entity_name, entity_type, start_pos, end_pos)
    """
    suggestions = []

    # Skip YAML frontmatter
    yaml_end = 0
    if content.startswith('---'):
        yaml_match = re.search(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        if yaml_match:
            yaml_end = yaml_match.end()

    # Skip References section
    refs_start = len(content)
    refs_match = re.search(r'^## References\s*$', content, re.MULTILINE)
    if refs_match:
        refs_start = refs_match.start()

    searchable_content = content[yaml_end:refs_start]

    # Build combined pattern for all entities
    all_entities = []
    for entity_type, names in entities.items():
        for name in names:
            all_entities.append((name, entity_type))

    # Sort by length (longest first) to match longer names before shorter
    all_entities.sort(key=lambda x: len(x[0]), reverse=True)

    for name, entity_type in all_entities:
        # Skip if already linked anywhere in doc
        if name in existing_links:
            continue

        # Skip very short names (likely to cause false positives)
        if len(name) < 4:
            continue

        # Escape regex special chars
        escaped_name = re.escape(name)

        # Match whole word, not inside existing links
        # Negative lookbehind for [[ and negative lookahead for ]]
        pattern = rf'(?<!\[\[)(?<!\|)\b({escaped_name})\b(?!\]\])(?!\|)'

        for match in re.finditer(pattern, searchable_content, re.IGNORECASE):
            matched_text = match.group(1)
            # Only suggest if case matches or is title case
            if matched_text == name or matched_text.lower() == name.lower():
                abs_start = yaml_end + match.start()
                abs_end = yaml_end + match.end()

                # Check we're not inside an existing link
                before = content[max(0, abs_start-2):abs_start]
                after = content[abs_end:abs_end+2]
                if '[[' not in before and ']]' not in after:
                    suggestions.append((name, entity_type, abs_start, abs_end))

    # Remove duplicates (keep first occurrence)
    seen_names = set()
    unique_suggestions = []
    for s in suggestions:
        if s[0] not in seen_names:
            seen_names.add(s[0])
            unique_suggestions.append(s)

    return unique_suggestions


def get_context(content: str, start: int, end: int, context_chars: int = 40) -> str:
    """Get surrounding context for a match."""
    ctx_start = max(0, start - context_chars)
    ctx_end = min(len(content), end + context_chars)

    before = content[ctx_start:start]
    match = content[start:end]
    after = content[end:ctx_end]

    # Clean up for display
    before = before.replace('\n', ' ').strip()
    after = after.replace('\n', ' ').strip()

    return f"...{before}>>>{match}<<<{after}..."


def apply_links(content: str, suggestions: List[Tuple[str, str, int, int]]) -> str:
    """Apply wiki links to content."""
    # Sort by position in reverse order to apply from end to start
    sorted_suggestions = sorted(suggestions, key=lambda x: x[2], reverse=True)

    for name, entity_type, start, end in sorted_suggestions:
        original_text = content[start:end]
        # Use display text if case differs
        if original_text != name:
            link = f"[[{name}|{original_text}]]"
        else:
            link = f"[[{name}]]"
        content = content[:start] + link + content[end:]

    return content


def process_file(filepath: Path, entities: Dict[str, Set[str]], fix: bool = False) -> List[Tuple[str, str, str]]:
    """
    Process a single file and return suggestions.

    Returns list of (entity_name, entity_type, context)
    """
    content = filepath.read_text(encoding='utf-8')
    existing_links = extract_existing_links(content)
    suggestions = find_linkable_mentions(content, entities, existing_links)

    results = []
    for name, entity_type, start, end in suggestions:
        context = get_context(content, start, end)
        results.append((name, entity_type, context))

    if fix and suggestions:
        new_content = apply_links(content, suggestions)
        filepath.write_text(new_content, encoding='utf-8')

    return results


def main():
    parser = argparse.ArgumentParser(description="Suggest wiki links for entities in markdown files")
    parser.add_argument('path', nargs='?', help="File or directory to process")
    parser.add_argument('--scan', metavar='DIR', help="Scan directory for files")
    parser.add_argument('--fix', action='store_true', help="Auto-fix by adding links")
    parser.add_argument('--verbose', '-v', action='store_true', help="Show all matches with context")
    args = parser.parse_args()

    # Determine what to process
    if args.scan:
        scan_path = Path(args.scan)
        if not scan_path.is_absolute():
            scan_path = REPO_ROOT / args.scan
        files = list(scan_path.rglob("*.md"))
    elif args.path:
        filepath = Path(args.path)
        if not filepath.is_absolute():
            filepath = Path.cwd() / args.path
        files = [filepath]
    else:
        parser.print_help()
        sys.exit(1)

    # Load entities
    print("Loading entities from vault...")
    entities = load_entities()
    print(f"  Designers: {len(entities['designers'])}")
    print(f"  Developers: {len(entities['developers'])}")
    print(f"  Publishers: {len(entities['publishers'])}")
    print(f"  Games: {len(entities['games'])}")
    print()

    # Process files
    total_suggestions = 0
    files_with_suggestions = 0

    for filepath in sorted(files):
        if not filepath.exists():
            print(f"File not found: {filepath}")
            continue

        results = process_file(filepath, entities, fix=args.fix)

        if results:
            files_with_suggestions += 1
            rel_path = filepath.relative_to(REPO_ROOT) if filepath.is_relative_to(REPO_ROOT) else filepath

            print("=" * 80)
            print(f"FILE: {rel_path}")
            print("=" * 80)

            # Group by entity type
            by_type = {}
            for name, entity_type, context in results:
                if entity_type not in by_type:
                    by_type[entity_type] = []
                by_type[entity_type].append((name, context))

            for entity_type in ['designers', 'developers', 'publishers', 'games']:
                if entity_type in by_type:
                    print(f"\n[{entity_type.upper()}]")
                    for name, context in by_type[entity_type]:
                        total_suggestions += 1
                        if args.verbose:
                            print(f"  • {name}")
                            print(f"    {context}")
                        else:
                            print(f"  • {name}")

            if args.fix:
                print(f"\n✓ Applied {len(results)} links")
            print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files scanned: {len(files)}")
    print(f"Files with suggestions: {files_with_suggestions}")
    print(f"Total suggestions: {total_suggestions}")

    if not args.fix and total_suggestions > 0:
        print("\nRun with --fix to auto-apply links")


if __name__ == "__main__":
    main()
