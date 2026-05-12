#!/usr/bin/env python3
"""Mechanical auto-fixer for vault pages.

Fixes:
1. Duplicate `<small>Last updated:` lines (keeps the first only)
2. `## Title` immediately after YAML (changes to `# Title`)
3. Missing Game Info callout fields where the YAML has the data
   - Maps YAML `engine:` → `**Engine:**`, `protagonist:` → `**Protagonist:**`,
     `series:` → `**Series:**`, `sierra_lineage:` → `**Sierra Lineage:**`,
     `designer:` → `**Designer:**`, `developer:` → `**Developer:**`,
     `publisher:` → `**Publisher:**`, `platforms:` → `**Platforms:**`,
     `release_year:` → `**Release Year:**`

Touches only pages under vault/Games. Skips pages with no callout.
"""
import re
import sys
import yaml
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "vault"

# Order matches STYLE_GUIDE.md
FIELD_ORDER = [
    ("Developer", "developer"),
    ("Designer", "designer"),
    ("Publisher", "publisher"),
    ("Engine", "engine"),
    ("Platforms", "platforms"),
    ("Release Year", "release_year"),
    ("Series", "series"),
    ("Protagonist", "protagonist"),
    ("Sierra Lineage", "sierra_lineage"),
]


def format_value(v) -> str:
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return str(v)


def split_yaml(text: str) -> tuple[dict, str, str]:
    """Return (yaml_dict, yaml_block_str, body)."""
    if not text.startswith("---\n"):
        return {}, "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, "", text
    yaml_block = text[4:end]
    body = text[end + 5:]
    try:
        data = yaml.safe_load(yaml_block) or {}
    except yaml.YAMLError:
        data = {}
    return data, yaml_block, body


def fix_duplicate_lastupdated(body: str) -> str:
    pattern = re.compile(r'<small[^>]*>Last updated:[^<]*</small>\s*', re.IGNORECASE)
    matches = list(pattern.finditer(body))
    if len(matches) <= 1:
        return body
    # Keep only the first match; remove subsequent ones
    new_body = body
    for m in reversed(matches[1:]):
        new_body = new_body[:m.start()] + new_body[m.end():]
    return new_body


def fix_h2_title(body: str) -> str:
    # If body starts with `## Word`, change to `# Word`
    return re.sub(r'^## ([^\n]+)', r'# \1', body, count=1)


def fix_callout_fields(body: str, yaml_data: dict) -> str:
    """Append missing Game Info callout fields from YAML.

    Strategy: locate the `> [!info]- Game Info` heading line. Walk forward
    through subsequent lines: as long as a line starts with `>`, it's part
    of the callout. The first non-`>` non-empty line ends the callout.
    Skip exactly the single newline immediately after the header (it is
    not a callout line, it's the line terminator).
    """
    m = re.search(r'^> \[!info\]-?\s*Game Info\s*$', body, re.MULTILINE)
    if not m:
        return body
    # Index just past the header line's newline (if any)
    pos = m.end()
    if pos < len(body) and body[pos] == '\n':
        pos += 1

    callout_end = pos
    field_re = re.compile(r'^\>\s*\*\*([^:*]+):\*\*')
    present: set[str] = set()
    while callout_end < len(body):
        nl = body.find('\n', callout_end)
        if nl == -1:
            line_end = len(body)
            line = body[callout_end:line_end]
        else:
            line_end = nl
            line = body[callout_end:line_end]
        if line.startswith('>'):
            fm = field_re.match(line)
            if fm:
                present.add(fm.group(1).strip())
            callout_end = line_end + 1 if nl != -1 else line_end
        else:
            break

    alias_to_canonical = {
        "Design/Writing": "Designer",
        "Design": "Designer",
    }
    canonical_present = {alias_to_canonical.get(p, p) for p in present}

    additions = []
    for label, yaml_key in FIELD_ORDER:
        if label in canonical_present:
            continue
        if yaml_key not in yaml_data or yaml_data[yaml_key] is None:
            continue
        value = format_value(yaml_data[yaml_key])
        if not value or value.lower() == "null":
            continue
        additions.append(f"> **{label}:** {value}")

    if not additions:
        return body

    # Strip trailing newline from the last callout line (if any) so additions slot in cleanly
    insertion = "\n".join(additions) + "\n"
    new_body = body[:callout_end] + insertion + body[callout_end:]
    return new_body


def fix_file(f: Path) -> list[str]:
    text = f.read_text()
    yaml_data, yaml_block, body = split_yaml(text)
    if not yaml_block:
        return []

    fixes = []
    new_body = body

    if "<small" in new_body:
        before = new_body
        new_body = fix_duplicate_lastupdated(new_body)
        if before != new_body:
            fixes.append("dedupe-lastupdated")

    # H2-title fix only if body starts with ## (after leading whitespace)
    stripped = new_body.lstrip()
    if stripped.startswith("## "):
        leading = len(new_body) - len(stripped)
        new_body = new_body[:leading] + fix_h2_title(stripped)
        fixes.append("h2→h1-title")

    before = new_body
    new_body = fix_callout_fields(new_body, yaml_data)
    if before != new_body:
        fixes.append("callout-fields")

    if fixes:
        f.write_text(f"---\n{yaml_block}\n---\n" + new_body)
    return fixes


def main() -> None:
    fixed = 0
    for f in (VAULT / "Games").rglob("*.md"):
        try:
            fixes = fix_file(f)
            if fixes:
                print(f"  ✓ [{'+'.join(fixes)}] {f.relative_to(VAULT)}")
                fixed += 1
        except Exception as e:
            print(f"  ! {f.relative_to(VAULT)}: {e}", file=sys.stderr)
    print(f"\nFixed: {fixed} files")


if __name__ == "__main__":
    main()
