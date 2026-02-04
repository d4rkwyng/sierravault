#!/usr/bin/env python3
"""
Standardize sierra_lineage values across all game pages.
Maps 100+ variant values to 10 canonical values.
"""

import os
import re
from pathlib import Path

GAMES_DIR = Path(__file__).parent.parent.parent / "Games"

# Canonical values and their mappings
LINEAGE_MAP = {
    # Core Sierra - Direct Sierra On-Line development/publication (1980-1999)
    "Core Sierra": [
        "Core Sierra",
        "Sierra Attractions",
        "Sierra Sports",
        "Sierra Discovery Series",
        "Sierra Discovery",
        "Late Sierra",
        "SierraVision",
        "SierraVenture",
        "Sierra Entertainment",
        "Sierra Online",
    ],

    # Dynamix - Dynamix studio games
    "Dynamix": [
        "Dynamix",
        "Sierra Label (Dynamix)",
        "Pre-Sierra Dynamix",
        "Sierra Subsidiary (Dynamix)",
        "Dynamix (later Sierra subsidiary)",
        "Sierra Affiliate (Dynamix)",
        "Dynamix Sports",
        "Dynamix Heritage",
        "Dynamix Division",
        "Licensed Dynamix IP",
    ],

    # Impressions - Impressions Games studio
    "Impressions": [
        "Impressions Games",
        "Sierra Subsidiary (Impressions)",
        "Sierra Family (Impressions Games)",
        "Sierra Affiliate (Impressions Games)",
        "Acquired Studio (Impressions)",
    ],

    # Coktel Vision - Coktel Vision studio
    "Coktel Vision": [
        "Coktel Vision",
        "Coktel Vision (Sierra subsidiary)",
        "Coktel Vision (Sierra Subsidiary)",
        "Sierra-Published (Coktel Vision)",
        "Coktel Vision Legacy",
    ],

    # Papyrus - Papyrus Design Group
    "Papyrus": [
        "Sierra Subsidiary (Papyrus)",
    ],

    # Bright Star - Bright Star Technology
    "Bright Star": [
        "Bright Star Technology",
        "Sierra Subsidiary (Bright Star Technology)",
        "Bright Star Educational",
    ],

    # Synergistic - Synergistic Software (Sierra division 1996-1999)
    "Synergistic": [
        "Sierra Subsidiary (Synergistic)",
    ],

    # Sierra Published - Third-party developed, Sierra published with involvement
    "Sierra Published": [
        "Sierra Published",
        "Published by Sierra",
        "Sierra-Published",
        "Sierra Published Original",
        "Sierra Published (Epyx Developed)",
        "Sierra Distributed",
        "Published Title",
        "Published Partner",
        "Related Publisher",
        "External Development",
        "External Developer",
        "Affiliated",
        "Affiliated Studio",
        "Affiliated Developer",
        "Affiliated Publisher",
        "Affiliate",
        "Extended Sierra Family",
        "Related",
        "Sierra Adjacent",
        "Licensed Sierra Port",
        "Acquired/Published",
        "Acquired Title",
        "Acquired Studio",
        "Acquired Franchise",
        "Acquired Property",
        "Later Sierra Acquisition",
        "Franchise Acquisition",
    ],

    # Post-Sierra - Vivendi/Activision/Encore era continuations
    "Post-Sierra": [
        "Post-Sierra",
        "Sierra Legacy",
        "Sierra Legacy (Encore Era)",
        "Sierra Legacy (Vivendi)",
        "Sierra Legacy (Knowledge Adventure)",
        "Sierra Legacy (Encore continuation)",
        "Vivendi Universal Games Era",
        "Vivendi Era",
        "Sierra Revival",
        "Sierra Mobile",
        "Post-Sierra Revival Attempt",
        "Post-Sierra Era (Encore)",
        "Post-Sierra (Knowledge Adventure)",
        "Legacy Title",
        "Legacy Sierra Property",
        "Encore/Viva Media Era",
        "Encore Era",
        "Coktel Vision (post-Sierra revival)",
    ],

    # Fan Project - Fan remakes and fan games
    "Fan Project": [
        "Fan Remake",
        "Fan-Made",
        "Fan Game",
        "Fan Project",
        "Fan-Made Spiritual Successor",
        "Sierra Remake",
    ],

    # Spiritual Successor - Sierra alumni original games
    "Spiritual Successor": [
        "Spiritual Successor",
        "Sierra Alumni",
        "Sierra Spiritual Successor",
        "Post-Sierra (Cole)",
        "Licensed/Successor",
    ],

    # Third Party - Needs review (may not belong in vault)
    "Third Party": [
        "Third Party",
        "Third-Party Published",
        "Third-party Sierra Published",
        "Third-Party Historical",
        "Third-Party / Ported by Dynamix",
        "Third-Party",
        "Licensed Title",
        "Licensed Product",
        "Licensed",
        "Acquired/Licensed",
        "SSI Distribution",
        "Non-Sierra",
    ],
}

# Build reverse mapping
def build_reverse_map():
    reverse = {}
    for canonical, variants in LINEAGE_MAP.items():
        for variant in variants:
            reverse[variant] = canonical
    return reverse

REVERSE_MAP = build_reverse_map()

def get_lineage_from_file(filepath):
    """Extract current sierra_lineage value from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'^sierra_lineage:\s*["\']?([^"\'"\n]+)["\']?', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def update_lineage_in_file(filepath, old_value, new_value):
    """Update sierra_lineage value in file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Handle both quoted and unquoted values
    patterns = [
        (rf'^sierra_lineage:\s*"{re.escape(old_value)}"', f'sierra_lineage: "{new_value}"'),
        (rf"^sierra_lineage:\s*'{re.escape(old_value)}'", f'sierra_lineage: "{new_value}"'),
        (rf'^sierra_lineage:\s*{re.escape(old_value)}$', f'sierra_lineage: "{new_value}"'),
    ]

    updated = False
    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        if count > 0:
            content = new_content
            updated = True
            break

    if updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    # Collect all changes
    changes = []
    unknown_values = []

    for md_file in GAMES_DIR.rglob("*.md"):
        current = get_lineage_from_file(md_file)
        if current is None:
            continue

        if current in REVERSE_MAP:
            canonical = REVERSE_MAP[current]
            if current != canonical:
                changes.append((md_file, current, canonical))
        else:
            unknown_values.append((md_file.name, current))

    # Report
    print("=" * 60)
    print("SIERRA LINEAGE STANDARDIZATION")
    print("=" * 60)

    if unknown_values:
        print(f"\n⚠️  UNKNOWN VALUES ({len(unknown_values)}):")
        for filename, value in sorted(set(unknown_values), key=lambda x: x[1]):
            print(f"  {value}: {filename}")

    print(f"\n📝 CHANGES TO APPLY ({len(changes)}):")

    # Group by change type
    by_change = {}
    for filepath, old, new in changes:
        key = (old, new)
        if key not in by_change:
            by_change[key] = []
        by_change[key].append(filepath.name)

    for (old, new), files in sorted(by_change.items(), key=lambda x: -len(x[1])):
        print(f"\n  '{old}' → '{new}' ({len(files)} files)")
        for f in files[:5]:
            print(f"    - {f}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")

    # Apply changes
    if changes:
        print(f"\n" + "=" * 60)
        response = input(f"Apply {len(changes)} changes? [y/N]: ").strip().lower()
        if response == 'y':
            success = 0
            for filepath, old, new in changes:
                if update_lineage_in_file(filepath, old, new):
                    success += 1
                    print(f"  ✓ {filepath.name}")
                else:
                    print(f"  ✗ {filepath.name} (failed)")
            print(f"\n✅ Updated {success}/{len(changes)} files")
        else:
            print("Cancelled.")
    else:
        print("\n✅ No changes needed - all values already standardized!")

if __name__ == "__main__":
    main()
