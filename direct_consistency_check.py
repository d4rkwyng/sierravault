#!/usr/bin/env python3
"""Direct consistency check runner"""

import sys
import os

# Ensure PyYAML is available
try:
    import yaml
except:
    os.system(f"{sys.executable} -m pip install pyyaml --break-system-packages -q 2>/dev/null")

# Now run the actual consistency check
from pathlib import Path
from collections import defaultdict
import json
import re
import argparse
from dataclasses import dataclass

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ── Constants ─────────────────────────────────────────────────────────────────

FLAGSHIP_SERIES = {
    "King's Quest", "Space Quest", "Quest for Glory",
    "Police Quest", "Leisure Suit Larry", "Gabriel Knight", "Laura Bow"
}

NON_NARRATIVE_GENRES = {
    "sports", "racing", "card game", "card games", "puzzle",
    "educational", "simulation", "strategy", "flight simulation",
    "sports simulation", "action", "arcade", "pinball", "golf",
    "fishing", "baseball", "football", "basketball", "soccer",
    "hockey", "tennis", "real-time strategy", "turn-based strategy",
    "city builder", "city-building", "god game", "management",
    "billiards", "chess", "board game", "casino", "screensaver",
}

NON_NARRATIVE_FOLDERS = {
    "Hoyle", "Front Page Sports", "PGA Championship Golf",
    "NASCAR", "IndyCar", "Trophy Bass", "Red Baron", "A-10 Tank Killer",
    "Aces", "Incredible Machine", "Ground Control", "Homeworld",
    "Empire Earth", "Civil War Generals", "Caesar", "Pharaoh",
    "Zeus", "Lords of the Realm", "Lords of Magic", "SWAT",
    "Power Chess", "Strategy", "Sierra Sports", "Sierra Pro Pilot",
    "BC", "Take a Break!", "Disney", "Education", "Arcade",
    "Metaltech", "Stellar 7", "Thexder", "Jawbreaker", "Oils Well",
    "3D Ultra", "INN",
}

REQUIRED_YAML_FIELDS = [
    "title", "release_year", "developer", "designer", "publisher",
    "genre", "platforms", "series", "engine", "protagonist",
    "sierra_lineage", "last_updated",
]

GAME_INFO_FIELDS = [
    "Developer", "Designer", "Publisher", "Engine",
    "Platforms", "Release Year", "Series", "Protagonist", "Sierra Lineage",
]

CANONICAL_LINEAGE = {
    # Core Sierra
    "Core Sierra",
    # Sierra Labels (per STYLE_GUIDE.md and INCLUSION_CRITERIA.md)
    "Sierra Label (Dynamix)",
    "Sierra Label (Impressions)",
    "Sierra Label (Coktel)",
    "Sierra Label (Coktel Vision)",  # alias for legacy pages
    "Sierra Label (Papyrus)",
    "Sierra Label (Bright Star)",
    "Sierra Label (Synergistic)",
    "Sierra Label (Sierra Attractions)",
    "Sierra Label (Discovery)",
    "Sierra Label (Other)",  # script-only fallback
    # Other relationships
    "Sierra Published",
    "Third-Party Published",
    "Acquired Franchise",
    "Partner Studio",  # script-only legacy alias
    "Licensed Title",  # script-only legacy alias
    # Post-Sierra / fan
    "Fan Project",
    "Fan Sequel",  # script-only alias for fan continuations
    "Alumni Project",
    "Spiritual Successor",
    "Spinoff",
    "Post-Sierra",
    "Cancelled",
}

KNOWN_BAD_LINKS = {
    "[[1983 - B.C.'s Quest for Tires]]",
    "[[1984 - B.C. II: Grog's Revenge]]",
    "[[1999 - Dr. Brain Thinking Games - IQ Adventure]]",
    "[[1999 - The Adventures of Dr. Brain]]",
    "[[1989 - E.S.S. (European Space Simulator)]]",
    "[[Order of the Thorne - The King's Challenge]]",
    "[[1983 - Oil's Well]]",
    "[[King's Quest II - Romancing the Stones (Fan)]]",
    "[[2011 - King's Quest II: Romancing the Stones]]",
    "[[1992 - Red Baron: Mission Builder]]",
    "[[1998 - Red Baron 3-D]]",
    "[[2008 - Red Baron - Arcade]]",
    "[[1996 - The Incredible Toon Machine]]",
    "[[2000 - Return of the Incredible Machine: Contraptions]]",
    "[[EcoQuest 2 - Lost Secret of the Rainforest]]",
}

@dataclass
class Issue:
    category: str
    severity: str
    message: str
    points_lost: float = 0.0

@dataclass
class PageResult:
    path: Path
    filename: str
    series: str
    page_type: str
    is_flagship: bool
    is_non_narrative: bool
    threshold: int
    score: float
    max_score: float
    issues: list
    ref_count: int

    @property
    def percentage(self) -> float:
        if self.max_score <= 0:
            return 0.0
        return round((self.score / self.max_score) * 100, 1)

    @property
    def passes(self) -> bool:
        return self.percentage >= self.threshold

    @property
    def status(self) -> str:
        pct = self.percentage
        if pct >= self.threshold:
            return "PASS"
        if pct >= self.threshold - 5:
            return "CLOSE"
        return "FAIL"

def parse_frontmatter(content: str) -> tuple:
    if not content.startswith("---"):
        return "", {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return "", {}, content
    fm_text = content[3:end]
    body = content[end + 4:]
    if HAS_YAML:
        try:
            fm = yaml.safe_load(fm_text) or {}
        except:
            fm = {}
    else:
        fm = {}
    return fm_text, fm, body

def h2_sections(content: str) -> set:
    return {m.group(1).strip() for m in re.finditer(r'^## (.+)', content, re.MULTILINE)}

def h3_sections(content: str) -> set:
    return {m.group(1).strip() for m in re.finditer(r'^### (.+)', content, re.MULTILINE)}

def count_ref_definitions(body: str) -> int:
    return len(re.findall(r'^\[\^ref-\d+\]:', body, re.MULTILINE))

def count_inline_citations(body: str) -> int:
    return len(re.findall(r'\[\^ref-\d+\](?!:)', body))

def find_duplicate_urls(body: str) -> list:
    refs = re.findall(r'^\[\^ref-\d+\]:.*?\((https?://[^)\s]+)\)', body, re.MULTILINE)
    seen, dupes = {}, []
    for url in refs:
        if url in seen and url not in dupes:
            dupes.append(url)
        seen[url] = True
    return dupes

def wiki_link_errors(body: str) -> tuple:
    md = re.findall(r'\[\[[^\]]*\.md[^\]]*\]\]', body)
    folders = re.findall(r'\[\[(?:Games|Designers|Developers|Publishers)/[^\]]*\]\]', body)
    return md, folders

def yaml_wiki_links(fm_text: str) -> list:
    return re.findall(r'\[\[[^\]]*\]\]', fm_text)

def detect_page_type(filename: str, folder: str) -> str:
    fn = filename.strip()
    if fn.startswith("TBD -") or fn.startswith("TBA -"):
        return "tbd"
    if fn.startswith("CXL -"):
        return "cancelled"
    if folder == "Fan Games":
        return "fan"
    if folder == "Spiritual Successors":
        return "spiritual"
    return "standard"

def is_non_narrative_page(genre: str, folder: str) -> bool:
    if genre and genre.lower() in NON_NARRATIVE_GENRES:
        return True
    return folder in NON_NARRATIVE_FOLDERS

def extract_callout(content: str) -> str:
    m = re.search(r'>\s*\[!info\]-?\s*Game Info\n((?:>.*\n?)*)', content)
    return m.group(1) if m else ""

def extract_nav_links(content: str) -> list:
    m = re.search(r'^## (?:See Also|Related Games|Series Continuity)\n([\s\S]+?)(?=^## |\Z)', content, re.MULTILINE)
    if not m:
        return []
    return re.findall(r'\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]', m.group(1))

def has_numeric_scores(content: str) -> bool:
    m = re.search(r'^## Reception([\s\S]+?)(?=^## |\Z)', content, re.MULTILINE)
    if not m:
        return True
    return bool(re.search(r'\b\d+(?:\.\d+)?(?:\s*/\s*\d+|%|\s+(?:out of|stars?|points?))', m.group(1), re.IGNORECASE))

def known_bad_links_in(content: str) -> list:
    return [link for link in KNOWN_BAD_LINKS if link in content]

def score_page(filepath: Path, all_basenames: set) -> PageResult:
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return PageResult(
            path=filepath, filename=filepath.name, series=filepath.parent.name,
            page_type="error", is_flagship=False, is_non_narrative=False,
            threshold=90, score=0, max_score=100, ref_count=0,
            issues=[Issue("File", "error", f"Cannot read file: {e}", 100)],
        )

    filename = filepath.name
    folder = filepath.parent.name
    fm_text, fm, body = parse_frontmatter(content)

    page_type = detect_page_type(filename, folder)
    genre_raw = str(fm.get("genre") or "").strip()
    series_name = str(fm.get("series") or "").strip()

    non_narrative = is_non_narrative_page(genre_raw, folder)
    is_cancelled = page_type == "cancelled"
    is_tbd = page_type == "tbd"
    is_flagship = series_name in FLAGSHIP_SERIES
    threshold = 95 if (is_flagship and not is_tbd and not is_cancelled) else 90

    h2 = h2_sections(content)
    h3 = h3_sections(content)
    ref_count = count_ref_definitions(body)

    issues = []
    score = 0.0
    max_score = 0.0

    def chk(cat: str, ok: bool, msg: str, pts: float, sev: str = "error"):
        nonlocal score, max_score
        max_score += pts
        if ok:
            score += pts
        else:
            issues.append(Issue(cat, sev, msg, pts))

    # YAML
    for fname in REQUIRED_YAML_FIELDS:
        # Accept explicit null as "acknowledged unknown" per STYLE_GUIDE.md
        # The field must exist as a key, but null is a valid value.
        chk("YAML", fname in fm, f"Missing YAML field: `{fname}`", 1.2)
    chk("YAML", len(yaml_wiki_links(fm_text)) == 0, "YAML contains wiki links — use plain text only", 3)
    sl = str(fm.get("sierra_lineage") or "")
    chk("YAML", sl in CANONICAL_LINEAGE, f"Non-canonical `sierra_lineage`: '{sl}'", 1.4, "warning")

    # Timestamp
    chk("Structure", bool(re.search(r'<small[^>]*>Last updated:', content, re.IGNORECASE)), "Missing `<small>Last updated:` line", 2)

    # Sections
    chk("Structure", "Overview" in h2, "Missing ## Overview section", 3)
    has_callout = bool(re.search(r'>\s*\[!info\]-?\s*Game Info', content, re.IGNORECASE))
    chk("Structure", has_callout, "Missing `> [!info]- Game Info` callout", 3)

    if not non_narrative and not is_cancelled:
        chk("Structure", "Story Summary" in h2, "Missing ## Story Summary", 3)

    if not is_cancelled:
        chk("Structure", "Gameplay" in h2, "Missing ## Gameplay section", 3)
        if not non_narrative:
            chk("Structure", "Interface and Controls" in h3, "Missing ### Interface and Controls", 2)
            chk("Structure", "Structure and Progression" in h3, "Missing ### Structure and Progression", 2)
            chk("Structure", "Puzzles and Mechanics" in h3, "Missing ### Puzzles and Mechanics", 2)

    chk("Structure", "Reception" in h2, "Missing ## Reception section", 4)
    chk("Structure", "Contemporary Reviews" in h3, "Missing ### Contemporary Reviews", 2)
    chk("Structure", "Modern Assessment" in h3, "Missing ### Modern Assessment", 2)
    chk("Structure", "Development" in h2, "Missing ## Development section", 3)
    chk("Structure", "Origins" in h3 or "Production" in h3, "Missing ### Origins or ### Production", 2)
    chk("Structure", "Technical Achievements" in h3, "Missing ### Technical Achievements", 2, "warning")
    chk("Structure", "Legacy" in h2, "Missing ## Legacy section", 3)

    if not is_cancelled:
        chk("Structure", "Downloads" in h2, "Missing ## Downloads section", 2)

    has_nav = any(s in h2 for s in ("See Also", "Related Games", "Series Continuity"))
    chk("Series Continuity", has_nav, "Missing ## See Also / Related Games section", 3)

    chk("References", "References" in h2, "Missing ## References section", 1)

    # Game Info Fields — accept style-guide alternative labels per STYLE_GUIDE.md
    # (e.g. **Design/Writing:** is interchangeable with **Designer:**)
    GAME_INFO_ALTS = {
        "Designer": ["Designer", "Design/Writing", "Design"],
    }
    if has_callout:
        callout = extract_callout(content)
        for fi in GAME_INFO_FIELDS:
            alternates = GAME_INFO_ALTS.get(fi, [fi])
            present = any(re.search(rf'\*\*{re.escape(alt)}:\*\*', callout) for alt in alternates)
            chk("Game Info", present, f"Missing `**{fi}:**`", 1)
    else:
        max_score += len(GAME_INFO_FIELDS)

    # References
    min_refs = 5 if (is_cancelled or is_tbd) else 15
    target_refs = 10 if (is_cancelled or is_tbd) else 20

    chk("References", ref_count >= min_refs, f"Only {ref_count} references — minimum is {min_refs}", 10)
    chk("References", ref_count >= target_refs, f"Reference count below target of {target_refs}", 2, "warning")

    inline = count_inline_citations(body)
    chk("References", inline >= 5, f"Only {inline} inline citation(s) in prose", 5)

    dupes = find_duplicate_urls(body)
    chk("References", len(dupes) == 0, f"Duplicate reference URL(s): {dupes[:3]}", 5)

    if not is_cancelled and not is_tbd:
        chk("References", has_numeric_scores(content), "Reception section has no numeric scores", 2, "warning")

    # Wiki Links
    md_links, folder_links = wiki_link_errors(body)
    chk("Wiki Links", len(md_links) == 0, f"{len(md_links)} wiki link(s) with .md extension", 4)
    chk("Wiki Links", len(folder_links) == 0, f"{len(folder_links)} wiki link(s) with folder paths", 4)

    # Nav Links
    nav_links = extract_nav_links(content)
    if nav_links and has_nav:
        broken = [lnk for lnk in nav_links if (lnk.strip() + ".md") not in all_basenames]
        chk("Series Continuity", len(broken) == 0, f"{len(broken)} unresolved See Also link(s)", 4)
    elif has_nav:
        max_score += 4
        score += 4

    # Known Bad Links
    bad = known_bad_links_in(content)
    chk("Wiki Links", len(bad) == 0, f"Contains known-bad wiki link(s): {bad[:3]}", 2)

    return PageResult(
        path=filepath, filename=filename, series=folder, page_type=page_type,
        is_flagship=is_flagship, is_non_narrative=non_narrative, threshold=threshold,
        score=round(score, 2), max_score=round(max_score, 2), issues=issues, ref_count=ref_count,
    )

def format_page(r: PageResult, verbose: bool = True) -> str:
    lines = []
    icon = {"PASS": "✅", "CLOSE": "⚠️", "FAIL": "❌"}.get(r.status, "?")
    tags = " ".join(filter(None, [
        f"[{r.page_type.upper()}]" if r.page_type != "standard" else "",
        "[NON-NARRATIVE]" if r.is_non_narrative else "",
        "[FLAGSHIP]" if r.is_flagship else "",
    ]))
    lines.append(f"\n{icon} {r.percentage:5.1f}% / {r.threshold}%  refs:{r.ref_count:>3}  {r.filename}")
    if tags:
        lines.append(f"       {tags}")
    if verbose and r.issues:
        by_cat = defaultdict(list)
        for iss in r.issues:
            by_cat[iss.category].append(iss)
        for cat in ["YAML", "Structure", "Game Info", "References", "Wiki Links", "Series Continuity"]:
            if cat in by_cat:
                lines.append(f"    [{cat}]")
                for iss in by_cat[cat]:
                    pre = {"error": "  ✗", "warning": "  ~", "info": "  ·"}.get(iss.severity, "  ?")
                    pts = f"(-{iss.points_lost:.1f})" if iss.points_lost > 0 else "(info)"
                    lines.append(f"    {pre} {pts} {iss.message}")
    return "\n".join(lines)

def print_series_summary(results: list) -> None:
    by_series = defaultdict(list)
    for r in results:
        by_series[r.series].append(r)
    rows = []
    for series, pages in by_series.items():
        passing = sum(1 for p in pages if p.passes)
        avg = sum(p.percentage for p in pages) / len(pages)
        mn = min(p.percentage for p in pages)
        rows.append((series, len(pages), passing, avg, mn))
    rows.sort(key=lambda x: x[3])
    print("\n" + "═" * 72)
    print("SERIES SUMMARY  (sorted by average score, worst first)")
    print("═" * 72)
    print(f"  {'Series':<34} {'Pages':>5} {'Pass':>5} {'Avg%':>6} {'Min%':>6}")
    print("─" * 72)
    for series, total, passing, avg, mn in rows:
        icon = "✅" if passing == total else ("⚠️" if avg >= 85 else "❌")
        print(f"  {icon} {series:<32} {total:>5} {passing:>5} {avg:>5.1f}% {mn:>5.1f}%")
    print("─" * 72)
    total_p = len(results)
    total_pass = sum(1 for r in results if r.passes)
    avg_all = sum(r.percentage for r in results) / total_p if total_p else 0
    print(f"  {'TOTAL':<34} {total_p:>5} {total_pass:>5} {avg_all:>5.1f}%")

def print_issue_leaderboard(results: list) -> None:
    counts = defaultdict(lambda: {"n": 0, "pts": 0.0})
    for r in results:
        for iss in r.issues:
            key = f"[{iss.category}] {iss.message[:90]}"
            counts[key]["n"] += 1
            counts[key]["pts"] += iss.points_lost
    rows = sorted(counts.items(), key=lambda x: -x[1]["n"])
    print("\n" + "═" * 72)
    print("TOP ISSUES  (by frequency across all pages)")
    print("═" * 72)
    for msg, data in rows[:30]:
        print(f"  {data['n']:>4}x  {msg}")

def build_json(results: list) -> dict:
    pages = []
    for r in results:
        pages.append({
            "filename": r.filename, "series": r.series, "page_type": r.page_type,
            "is_flagship": r.is_flagship, "is_non_narrative": r.is_non_narrative,
            "threshold": r.threshold, "score": r.percentage, "passes": r.passes,
            "status": r.status, "ref_count": r.ref_count,
            "issues": [{"category": i.category, "severity": i.severity, "message": i.message, "points_lost": i.points_lost} for i in r.issues],
        })
    pages.sort(key=lambda x: x["score"])
    total, passing = len(results), sum(1 for r in results if r.passes)
    avg = sum(r.percentage for r in results) / total if total else 0
    return {
        "summary": {"total_pages": total, "passing": passing, "failing": total - passing, "pass_rate_pct": round(passing / total * 100, 1) if total else 0, "average_score": round(avg, 1)},
        "pages": pages,
    }

# Main execution
vault = Path.home() / "Projects/sierravault/vault/Games"
if not vault.exists():
    print(f"ERROR: vault not found at {vault}")
    sys.exit(1)

all_md = list(vault.rglob("*.md"))
all_basenames = {f.name for f in all_md}

print("\n" + "="*72)
print(f"SCANNING {len(all_md)} MARKDOWN FILES")
print("="*72)

results = [score_page(f, all_basenames) for f in all_md]
display_failing = [r for r in results if not r.passes]

print("\n" + "="*72)
print("OVERALL CONSISTENCY CHECK RESULTS (--quiet mode)")
print("="*72)

for r in results:
    print(format_page(r, verbose=False))

print_series_summary(results)
print_issue_leaderboard(results)

total = len(results)
passing = sum(1 for r in results if r.passes)
avg = sum(r.percentage for r in results) / total if total else 0
print(f"\n{'═' * 72}")
print(f"OVERALL: {passing}/{total} pages passing  |  average: {avg:.1f}%")
print("═" * 72)

# Save JSON
json_out = Path.home() / "Projects/sierravault/vault_report.json"
json_out.write_text(json.dumps(build_json(results), indent=2))
print(f"\nJSON report saved to: {json_out}")

# Print failing pages details
print("\n" + "="*72)
print(f"FAILING PAGES WITH DETAILS ({len(display_failing)} pages)")
print("="*72)

for r in display_failing:
    print(format_page(r, verbose=True))

# Print JSON summary and first 50 pages
print("\n" + "="*72)
print("JSON REPORT SUMMARY AND LOWEST 50 PAGES")
print("="*72)

report = json.loads(json_out.read_text())
print(json.dumps(report["summary"], indent=2))

print("\n" + "─" * 72)
print("LOWEST SCORING PAGES (first 50)")
print("─" * 72)
for i, page in enumerate(report["pages"][:50], 1):
    print(f"\n{i:2}. {page['score']:5.1f}% / {page['threshold']}%  refs:{page['ref_count']:>2}  {page['filename']} [{page['series']}]")
    if page['issues']:
        for issue in page['issues'][:4]:
            sev_icon = {"error": "X", "warning": "~", "info": "."}.get(issue["severity"], "?")
            print(f"     [{sev_icon}] {issue['message'][:75]}")
