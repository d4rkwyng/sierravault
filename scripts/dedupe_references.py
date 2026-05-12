#!/usr/bin/env python3
"""Merge duplicate `## References` sections in vault pages.

A prior batch-edit accidentally appended a second `## References` block to
many files. This script finds files with >1 `## References` heading and
merges them into a single section, preferring the second section's version
on ref-number conflicts (it usually has the corrected text).
"""
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "vault"

REF_DEF_RE = re.compile(r'^\[\^ref-[\w-]+\]:.*(?:\n(?!\[\^ref-|\n*## ).*)*', re.MULTILINE)
REF_NUM_RE = re.compile(r'^\[\^(ref-[\w-]+)\]:')


def merge_refs(section_a: str, section_b: str) -> str:
    """Return a merged ref block, second-wins on conflicts.

    Each section is the body BELOW the `## References` heading.
    """
    def parse(s: str) -> dict[str, str]:
        out = {}
        for m in REF_DEF_RE.finditer(s):
            line = m.group(0).rstrip()
            key_m = REF_NUM_RE.match(line)
            if key_m:
                out[key_m.group(1)] = line
        return out

    a = parse(section_a)
    b = parse(section_b)
    merged = {**a, **b}  # b overrides a

    # Preserve first-section ordering, then append new keys from second
    order = list(a.keys()) + [k for k in b.keys() if k not in a]

    # Natural sort by numeric suffix when possible
    def key(k: str) -> tuple:
        m = re.fullmatch(r'ref-(\d+)', k)
        return (0, int(m.group(1))) if m else (1, k)
    order = sorted(order, key=key)

    return "\n".join(merged[k] for k in order)


def fix_file(f: Path) -> bool:
    text = f.read_text()
    positions = [m.start() for m in re.finditer(r'^## References\b', text, re.MULTILINE)]
    if len(positions) < 2:
        return False

    first = positions[0]
    second = positions[-1]
    preamble = text[:first].rstrip() + "\n\n"
    section_a = text[first + len("## References"): second]
    section_b = text[second + len("## References"):]

    merged_body = merge_refs(section_a, section_b)
    new_text = preamble + "## References\n\n" + merged_body + "\n"
    f.write_text(new_text)
    return True


def main() -> None:
    fixed = 0
    for f in VAULT.rglob("*.md"):
        try:
            if fix_file(f):
                print(f"  ✓ {f.relative_to(VAULT)}")
                fixed += 1
        except Exception as e:
            print(f"  ! {f.relative_to(VAULT)}: {e}", file=sys.stderr)
    print(f"\nFixed: {fixed} files")


if __name__ == "__main__":
    main()
