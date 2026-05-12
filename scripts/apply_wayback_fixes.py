#!/usr/bin/env python3
"""Apply Wayback snapshot replacements to vault pages.

For each row in dead_urls_worklist.csv with a wayback_snapshot:
- Open the affected file
- Replace the dead URL with the Wayback URL inside that file's reference list
- Prepend a "via Wayback" note to the description
- Mark the row as 'applied' so we don't re-do it
"""
import csv
import re
import sys
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "docs" / "dead_urls_worklist.csv"
VAULT = Path(__file__).resolve().parent.parent / "vault"


def main() -> None:
    rows = list(csv.DictReader(CSV_PATH.open()))
    fields = list(rows[0].keys()) if rows else []
    if "notes" not in fields:
        fields = list(fields) + ["notes"]
        for r in rows:
            r.setdefault("notes", "")

    applied = 0
    skipped = 0
    by_file: dict[str, list[dict]] = {}
    for row in rows:
        if not row.get("wayback_snapshot"):
            continue
        if row.get("notes") in {"applied", "replaced", "removed"}:
            continue
        by_file.setdefault(row["file"], []).append(row)

    for rel_path, group in by_file.items():
        f = VAULT / rel_path
        if not f.exists():
            print(f"  ! missing file: {rel_path}", file=sys.stderr)
            continue
        text = f.read_text()
        original = text
        for row in group:
            dead = row["dead_url"]
            wb = row["wayback_snapshot"]
            if dead in text:
                text = text.replace(dead, wb)
                row["notes"] = "applied"
                applied += 1
            else:
                row["notes"] = "needs-review"
                skipped += 1
        if text != original:
            f.write_text(text)
            print(f"  ✓ {rel_path} ({len(group)} URLs)")

    with CSV_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"\nApplied: {applied}  Skipped (URL not found in file): {skipped}")


if __name__ == "__main__":
    main()
