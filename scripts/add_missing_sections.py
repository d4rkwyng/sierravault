#!/usr/bin/env python3
"""Add minimal Downloads and See Also sections to failing game pages.

For pages that lack ## Downloads or ## See Also sections, this script
inserts default-populated versions:

- See Also: links to all sibling .md files in the same folder
- Downloads: search-link template for GOG/Steam/MobyGames/Archive.org

Only touches pages that are CURRENTLY FAILING the consistency check for
these specific reasons. Reads vault_report.json to determine which pages
to fix.
"""
import json
import re
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "vault"
REPORT = REPO / "vault_report.json"


def title_from_filename(name: str) -> str:
    """Extract human-readable title from `YYYY - Title.md` filename."""
    stem = name.removesuffix(".md")
    m = re.match(r"^(?:\d{4}|CXL|TBD|TBA)\s*-\s*(.+)$", stem)
    return m.group(1) if m else stem


def build_see_also(file: Path) -> str:
    siblings = sorted(p.name for p in file.parent.glob("*.md") if p.name != file.name)
    if not siblings:
        return ""
    links = [f"- [[{s[:-3]}]]" for s in siblings]
    return "## See Also\n\n" + "\n".join(links) + "\n"


def build_downloads(file: Path) -> str:
    title = title_from_filename(file.name)
    q = urllib.parse.quote_plus(title)
    return f"""## Downloads

**Purchase / Digital Stores**
- [GOG.com search](https://www.gog.com/en/games?query={q})
- [Steam search](https://store.steampowered.com/search/?term={q})

**Download / Preservation**
- [MobyGames search](https://www.mobygames.com/search/?q={q})
- [Internet Archive search](https://archive.org/search?query={q})
- [MyAbandonware search](https://www.myabandonware.com/search/q/{q})
"""


def insert_section(text: str, section: str, before: list[str] | None = None) -> str:
    """Insert `section` before the first occurrence of any heading in `before`.

    If no `before` heading exists, append at end (before any final newlines).
    """
    if before:
        for heading in before:
            pattern = re.compile(rf"^{re.escape(heading)}\s*$", re.MULTILINE)
            m = pattern.search(text)
            if m:
                return text[:m.start()] + section + "\n" + text[m.start():]
    # Append at end
    return text.rstrip() + "\n\n" + section


def main() -> None:
    r = json.loads(REPORT.read_text())
    failing = [p for p in r["pages"] if not p["passes"]]

    fixed = 0
    for p in failing:
        # Find the page file
        candidates = list(VAULT.rglob(p["filename"]))
        if not candidates:
            print(f"  ? {p['filename']} — not found")
            continue
        f = candidates[0]
        text = f.read_text()
        original = text
        fixes = []

        missing_downloads = any("Missing ## Downloads" in i["message"] for i in p["issues"])
        missing_see_also = any("Missing ## See Also" in i["message"] for i in p["issues"])

        if missing_downloads:
            text = insert_section(text, build_downloads(f), before=["## See Also", "## References"])
            fixes.append("downloads")

        if missing_see_also:
            text = insert_section(text, build_see_also(f), before=["## References"])
            fixes.append("see-also")

        if text != original:
            f.write_text(text)
            fixed += 1
            print(f"  ✓ [{'+'.join(fixes)}] {f.relative_to(VAULT)}")

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
