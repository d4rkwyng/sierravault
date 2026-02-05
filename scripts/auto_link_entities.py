#!/usr/bin/env python3
"""
Auto-link first mention of entities (designers, developers, publishers) in pages.

Links entities in:
1. Game Info callout (always)
2. First mention in body text (Game Info doesn't count as first mention)

Usage:
  python auto_link_entities.py --dry-run          # Preview changes
  python auto_link_entities.py                    # Apply changes
  python auto_link_entities.py --file "path.md"  # Single file
"""

import re
import argparse
from pathlib import Path

VAULT = Path(__file__).parent.parent / "vault"

def get_entities():
    """Build master list of linkable entities."""
    entities = {}

    # Designers
    designers_dir = VAULT / "Designers"
    if designers_dir.exists():
        for f in designers_dir.glob("*.md"):
            name = f.stem
            if len(name) >= 6:  # Skip short names
                entities[name] = f"[[{name}]]"

    # Developers
    developers_dir = VAULT / "Developers"
    if developers_dir.exists():
        for f in developers_dir.glob("*.md"):
            name = f.stem
            if len(name) >= 6:
                entities[name] = f"[[{name}]]"

    # Publishers
    publishers_dir = VAULT / "Publishers"
    if publishers_dir.exists():
        for f in publishers_dir.glob("*.md"):
            name = f.stem
            if len(name) >= 6:
                entities[name] = f"[[{name}]]"

    return entities

def is_already_linked_in_section(content, entity):
    """Check if entity is already wiki-linked in a section."""
    patterns = [
        rf'\[\[{re.escape(entity)}\]\]',
        rf'\[\[{re.escape(entity)}\|[^\]]+\]\]',
        rf'\[\[[^\]]+\|{re.escape(entity)}\]\]',
    ]
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def is_in_yaml_or_reference(content, pos):
    """Check if position is in YAML frontmatter or reference section."""
    # Check if in YAML (between --- markers at start)
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end != -1 and pos < yaml_end:
            return True

    # Check if in reference line (starts with [^ref or is a URL)
    line_start = content.rfind('\n', 0, pos) + 1
    line_end = content.find('\n', pos)
    if line_end == -1:
        line_end = len(content)
    line = content[line_start:line_end]
    if '[^ref' in line or 'http' in line.lower():
        return True

    return False

def find_game_info_section(content):
    """Find the Game Info callout section bounds."""
    # Match > [!info]- Game Info or similar patterns
    match = re.search(r'^> \[!info\][+-]? ?Game Info', content, re.MULTILINE | re.IGNORECASE)
    if not match:
        return None, None

    start = match.start()
    # Find end of callout (next line not starting with >)
    lines = content[start:].split('\n')
    end = start
    for i, line in enumerate(lines):
        if i == 0:
            end += len(line) + 1
            continue
        if line.startswith('>'):
            end += len(line) + 1
        else:
            break

    return start, end

def find_credits_section(content):
    """Find Development Credits section bounds."""
    # Look for ## Development or ### Development Credits or similar
    match = re.search(r'^##+ .*(?:Development|Credits).*$', content, re.MULTILINE | re.IGNORECASE)
    if not match:
        return None, None

    start = match.start()
    # Find end (next ## heading or end of file)
    rest = content[match.end():]
    next_heading = re.search(r'^##+ ', rest, re.MULTILINE)
    if next_heading:
        end = match.end() + next_heading.start()
    else:
        end = len(content)

    return start, end

def link_entity_in_text(text, entity, link):
    """Replace first unlinked mention of entity in text."""
    pattern = rf'(?<!\[\[)(?<!\|)\b({re.escape(entity)})\b(?!\]\])(?!\|)'

    for match in re.finditer(pattern, text, re.IGNORECASE):
        start, end = match.span()
        return text[:start] + link + text[end:], True

    return text, False

def process_file(filepath, entities, dry_run=False):
    """Process a single file, linking in Game Info, Credits, and first body mention."""
    try:
        content = filepath.read_text()
        original = content
        changes = []

        for entity, link in entities.items():
            locations = []

            # 1. Link in Game Info callout (if present and not already linked there)
            gi_start, gi_end = find_game_info_section(content)
            if gi_start is not None:
                game_info = content[gi_start:gi_end]
                if not is_already_linked_in_section(game_info, entity):
                    new_gi, changed = link_entity_in_text(game_info, entity, link)
                    if changed:
                        content = content[:gi_start] + new_gi + content[gi_end:]
                        locations.append("info")

            # 2. Link in Credits/Development section (if present and not already linked)
            cr_start, cr_end = find_credits_section(content)
            if cr_start is not None:
                credits = content[cr_start:cr_end]
                if not is_already_linked_in_section(credits, entity):
                    new_cr, changed = link_entity_in_text(credits, entity, link)
                    if changed:
                        content = content[:cr_start] + new_cr + content[cr_end:]
                        locations.append("credits")

            # 3. Link first mention in body (excluding YAML, refs, Game Info, Credits)
            # Find body text (everything except special sections)
            gi_start, gi_end = find_game_info_section(content)
            cr_start, cr_end = find_credits_section(content)

            # Check if already linked anywhere in content
            if not is_already_linked_in_section(content, entity):
                pattern = rf'(?<!\[\[)(?<!\|)\b({re.escape(entity)})\b(?!\]\])(?!\|)'
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    pos = match.start()

                    # Skip if in YAML or references
                    if is_in_yaml_or_reference(content, pos):
                        continue

                    # Skip if in Game Info section
                    if gi_start is not None and gi_start <= pos < gi_end:
                        continue

                    # Skip if in Credits section
                    if cr_start is not None and cr_start <= pos < cr_end:
                        continue

                    # Found valid body mention - link it
                    start, end = match.span()
                    content = content[:start] + link + content[end:]
                    locations.append("body")
                    break

            if locations:
                changes.append(f"{entity}({'+'.join(locations)})")

        if changes and content != original:
            rel_path = filepath.relative_to(VAULT)
            if dry_run:
                print(f"{rel_path}: Would link {', '.join(changes)}")
            else:
                filepath.write_text(content)
                print(f"{rel_path}: Linked {', '.join(changes)}")
            return len(changes)

        return 0
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description="Auto-link entities in pages")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--file", help="Process single file")
    parser.add_argument("--folder", help="Process specific folder (e.g., 'Games/King's Quest')")
    args = parser.parse_args()

    entities = get_entities()
    print(f"Loaded {len(entities)} linkable entities\n")

    total_changes = 0
    files_changed = 0

    if args.file:
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = VAULT / filepath
        changes = process_file(filepath, entities, args.dry_run)
        if changes:
            files_changed = 1
            total_changes = changes
    else:
        # Process Games and Series folders
        folders = ["Games", "Series"]
        if args.folder:
            folders = [args.folder]

        for folder in folders:
            folder_path = VAULT / folder
            if folder_path.exists():
                for md_file in sorted(folder_path.rglob("*.md")):
                    changes = process_file(md_file, entities, args.dry_run)
                    if changes:
                        files_changed += 1
                        total_changes += changes

    print(f"\n{'Would make' if args.dry_run else 'Made'} {total_changes} links across {files_changed} files")

if __name__ == "__main__":
    main()
