#!/usr/bin/env python3
"""
Convert Games sections in designer pages from list format to table format.
Sorts games by year chronologically.
"""

import re
from pathlib import Path

def parse_game_entry(line):
    """Parse a game list entry and extract year, game link, and role."""
    # Pattern: - [[link|display]] — year, role
    # or: - [[link]] — year, role

    # Match the wiki link
    link_match = re.search(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', line)
    if not link_match:
        return None

    full_link = link_match.group(0)
    link_target = link_match.group(1)
    display_text = link_match.group(2) or link_match.group(1)

    # Extract year and role after the em dash
    after_link = line[link_match.end():]

    # Try to match " — year, role" or " — year"
    meta_match = re.search(r'—\s*(\d{4})(?:,\s*(.+))?$', after_link)
    if meta_match:
        year = meta_match.group(1)
        role = meta_match.group(2).strip() if meta_match.group(2) else ""
    else:
        # Try to extract year from the link itself
        year_in_link = re.search(r'^(\d{4})\s*-', link_target)
        year = year_in_link.group(1) if year_in_link else "????"
        role = ""

    return {
        'year': year,
        'link': full_link,
        'display': display_text,
        'role': role
    }

def convert_games_section(content):
    """Convert the Games section from list to table format."""

    # Find the Games section
    games_header_match = re.search(r'^## Games\s*$', content, re.MULTILINE)
    if not games_header_match:
        return content, False

    start_pos = games_header_match.end()

    # Find where the Games section ends (next ## header or ## References or end)
    next_section = re.search(r'^## ', content[start_pos:], re.MULTILINE)
    if next_section:
        end_pos = start_pos + next_section.start()
    else:
        end_pos = len(content)

    games_section = content[start_pos:end_pos]

    # Check if already a table
    if '| Year |' in games_section or '|Year|' in games_section:
        return content, False

    # Parse all list items
    games = []
    for line in games_section.split('\n'):
        line = line.strip()
        if line.startswith('- [['):
            entry = parse_game_entry(line)
            if entry:
                games.append(entry)

    if not games:
        return content, False

    # Sort by year
    games.sort(key=lambda g: (g['year'], g['display']))

    # Build table
    table_lines = [
        "",
        "| Year | Game | Role |",
        "|------|------|------|"
    ]

    for game in games:
        role = game['role'] if game['role'] else "—"
        # Escape pipe in wiki links for table compatibility
        link = game['link'].replace('|', '\\|')
        table_lines.append(f"| {game['year']} | {link} | {role} |")

    table_lines.append("")

    # Replace the old section with the new table
    new_content = content[:start_pos] + '\n'.join(table_lines) + content[end_pos:]

    return new_content, True

def process_file(filepath):
    """Process a single designer file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content, changed = convert_games_section(content)

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    designers_dir = Path(__file__).parent.parent / 'vault' / 'Designers'

    updated = []
    skipped = []

    for filepath in sorted(designers_dir.glob('*.md')):
        if filepath.name == 'Minor Contributors.md':
            skipped.append(filepath.name)
            continue

        if process_file(filepath):
            updated.append(filepath.name)
            print(f"✓ Updated: {filepath.name}")
        else:
            skipped.append(filepath.name)
            print(f"  Skipped: {filepath.name}")

    print(f"\nUpdated {len(updated)} files, skipped {len(skipped)} files")

if __name__ == '__main__':
    main()
