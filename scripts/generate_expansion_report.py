#!/usr/bin/env python3
"""Generate expansion TODO report with specific section suggestions."""

import os
import re
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("vault/Games")
MIN_CITATIONS = 15
MIN_WORDS = 1000

def count_citations(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    wiki_links = len(re.findall(r'\[\[.*?\]\]', content))
    markdown_links = len(re.findall(r'\[.*?\]\(.*?\)', content))
    return wiki_links + markdown_links

def count_words(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(content.split())

def check_section_present(filepath, section_header):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return f"## {section_header}" in content or f"### {section_header}" in content

def get_specific_suggestions(filepath):
    """Generate specific section suggestions based on what's missing."""
    suggestions = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    citations = count_citations(filepath)
    words = count_words(filepath)
    
    # Check each section
    sections_to_add = []
    if not check_section_present(filepath, "Purchase"):
        sections_to_add.append("Purchase: Add current availability (GOG, Steam, Epic), pricing, bundle info")
    if not check_section_present(filepath, "Technical"):
        sections_to_add.append("Technical: Add engine (SCSI/SCI version), system requirements, platforms released on")
    if not check_section_present(filepath, "Development"):
        sections_to_add.append("Development: Add dev timeline, design challenges, team changes, cancellation history if applicable")
    if not check_section_present(filepath, "Reception"):
        sections_to_add.append("Reception: Add review scores (PC Gamer, Computer Gaming World), sales figures, awards/nominations")
    if not check_section_present(filepath, "Legacy"):
        sections_to_add.append("Legacy: Add re-release history, influence on later games, cult following, modern relevance")
    if not check_section_present(filepath, "Cast"):
        sections_to_add.append("Cast: Add voice actors, character actors, performance capture details")
    if not check_section_present(filepath, "Music"):
        sections_to_add.append("Music: Add composer, notable tracks, soundtrack releases, music style analysis")
    if not check_section_present(filepath, "Sequel"):
        sections_to_add.append("Sequel: Add info about direct sequel or spiritual successor")
    
    # Word count expansion suggestions
    if words < MIN_WORDS:
        deficit = MIN_WORDS - words
        suggestions.append(f"Word count expansion needed (~{deficit} words short):")
        suggestions.append("  - Expand Development section with design philosophy and challenges")
        suggestions.append("  - Add Reception details from contemporary reviews")
        suggestions.append("  - Expand Legacy with re-release and influence details")
    
    # Citation expansion suggestions
    if citations < MIN_CITATIONS:
        deficit = MIN_CITATIONS - citations
        suggestions.append(f"Citation expansion needed ({deficit} more minimum):")
        suggestions.append("  - Add MobyGames as primary source")
        suggestions.append("  - Include GOG/Steam store pages for current availability")
        suggestions.append("  - Add Wikipedia article if exists")
        suggestions.append("  - Include 2-3 contemporary review sources (CGW, PC Gamer, etc.)")
    
    return sections_to_add, suggestions

def analyze_page(filepath):
    citations = count_citations(filepath)
    words = count_words(filepath)
    sections_to_add, expansion_suggestions = get_specific_suggestions(filepath)
    
    needs_attention = citations < MIN_CITATIONS or words < MIN_WORDS or len(sections_to_add) > 0
    
    if needs_attention:
        return {
            "file": str(filepath),
            "citations": citations,
            "words": words,
            "sections_to_add": sections_to_add,
            "expansion_suggestions": expansion_suggestions,
            "priority": "high" if citations < 10 or words < 500 else "medium"
        }
    return None

def main():
    """Generate the expansion report."""
    results = []
    
    for filepath in VAULT_PATH.rglob("*.md"):
        if filepath.is_file():
            result = analyze_page(filepath)
            if result:
                results.append(result)
    
    # Sort by priority and severity
    results.sort(key=lambda x: (x["priority"] == "high", x["citations"], x["words"]))
    
    # Create report
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# SierraVault Expansion Opportunities
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Criteria:** <{MIN_CITATIONS} citations or <{MIN_WORDS} words

---

## Summary

- **Total pages analyzed:** 507
- **Pages needing expansion:** {len(results)}
- **High priority:** {sum(1 for r in results if r["priority"] == "high")}
- **Medium priority:** {sum(1 for r in results if r["priority"] == "medium")}

---

## High Priority Items

### 1. Pages with <10 Citations or <500 Words

"""
    
    high_priority = [r for r in results if r["priority"] == "high"]
    for i, r in enumerate(high_priority[:15], 1):
        report += f"""
### {i}. {r['file'].replace('vault/Games/', '')}
- **Citations:** {r['citations']} (need {MIN_CITATIONS})
- **Words:** {r['words']} (need {MIN_WORDS})
- **Missing Sections:**
"""
        for section in r["sections_to_add"][:5]:
            report += f"  - {section}\n"
        report += """
**Action Items:**
"""
        for suggestion in r["expansion_suggestions"][:4]:
            report += f"  - {suggestion}\n"
    
    report += """
---

## Medium Priority Items

### Pages Missing Key Sections (but adequate citations/length)

"""
    
    medium_priority = [r for r in results if r["priority"] == "medium"]
    for i, r in enumerate(medium_priority[:20], 1):
        if r["sections_to_add"]:
            report += f"""
### {i}. {r['file'].replace('vault/Games/', '')}
- **Citations:** {r['citations']} | **Words:** {r['words']}
- **Add these sections:**
"""
            for section in r["sections_to_add"]:
                report += f"  - {section}\n"
    
    report += """
---

## Recommended Work Order

### Day 1-2: Fix Critical Gaps
1. Add Purchase sections to flagship titles (KQ, SQ, QFG series)
2. Add Technical sections to pre-SCI games
3. Expand Reception sections for games without review data

### Day 3-4: Fill Section Gaps
1. Add Legacy sections to older games
2. Add Cast sections to voice-acted games (LSL, Day of the Tentacle)
3. Add Music sections to games with notable soundtracks

### Day 5+: Citation Expansion
1. Add MobyGames to all pages missing it
2. Include contemporary reviews (CGW, PC Gamer, Computer Entertainer)
3. Add Wikipedia where available
4. Verify GOG/Steam links

---

## TODO for Tomorrow

```bash
# Quick wins - add Purchase sections
cd /Users/woodd/Projects/sierravault

# Flagship games first
python3 scripts/add_timestamps.py "vault/Games/Kings_Quest/1987 - Kings Quest.md"
python3 scripts/add_timestamps.py "vault/Games/Space_Quest/1986 - Space Quest.md"

# Bulk add Purchase sections using template
# (Create script to insert Purchase section if missing)

# Then verify citations
python3 scripts/find_duplicate_refs.py "vault/Games/..."
```

---

## Notes

- Focus on Sierra flagships first (KQ, SQ, QFG, LSL, Day of the Tentacle)
- Fan games and cancelled projects can be lower priority
- Always verify facts before adding sections
- Update timestamps after any edits

**Next review:** Run this analysis again after completing TODO items.
"""
    
    # Save report
    report_path = Path("/Users/woodd/.openclaw/workspace/memory/expansion-needed-2026-03-03.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report saved to: {report_path}")
    print(f"\nFound {len(results)} pages needing expansion")
    print(f"High priority: {len(high_priority)}")
    print(f"Medium priority: {len(medium_priority)}")

if __name__ == "__main__":
    main()