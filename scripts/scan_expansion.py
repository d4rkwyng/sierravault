#!/usr/bin/env python3
"""
SierraVault Expansion Scanner
Find pages with <15 citations or <1000 words
Suggest specific sections to expand
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("/Users/woodd/Projects/sierravault/vault")
MEMORY_PATH = Path("/Users/woodd/.openclaw/workspace/memory")

def count_citations(content):
    """Count citations (wiki links and URLs)"""
    # Wiki links: [[...]]
    wiki_count = len(re.findall(r'\[\[', content))
    # URLs: http:// or https://
    url_count = len(re.findall(r'https?://', content))
    return wiki_count + url_count

def count_words(content):
    """Count words in content"""
    return len(content.split())

def analyze_section_depth(content, section_title):
    """Check if a section exists and how deep it is"""
    pattern = rf'##\s+{re.escape(section_title)}\s*\n(.*?)(?=\n##\s|$)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return 0, False
    
    section_content = match.group(1)
    has_content = len(section_content.strip()) > 100
    return len(section_content.split()), has_content

def suggest_expansions(content, page_path):
    """Analyze content and suggest specific expansions"""
    suggestions = []
    
    # Check sections
    sections_to_check = [
        ("Purchase", "Add pricing, platform availability, re-release history"),
        ("Technical", "Add system requirements, engine details, performance notes"),
        ("Development", "Add design challenges, engine decisions, team stories"),
        ("Story", "Add plot summary, character details, themes analysis"),
        ("Gameplay", "Add mechanics breakdown, puzzle examples, difficulty notes"),
        ("Reception", "Add reviews, sales data, awards, critical analysis"),
        ("Legacy", "Add sequels, influence, cultural impact"),
    ]
    
    for section_title, reason in sections_to_check:
        depth, has_content = analyze_section_depth(content, section_title)
        
        if depth == 0:
            suggestions.append({
                "section": section_title,
                "status": "missing",
                "suggestion": f"Add {section_title.lower()} section - {reason}"
            })
        elif depth < 300 and has_content:
            suggestions.append({
                "section": section_title,
                "status": "shallow",
                "suggestion": f"Expand {section_title.lower()} section - currently {depth} words, needs more detail"
            })
    
    # Check citation count
    citation_count = count_citations(content)
    if citation_count < 15:
        suggestions.append({
            "section": "References",
            "status": "low_citations",
            "suggestion": f"Add {15 - citation_count}+ citations - currently {citation_count}, needs 15+"
        })
    
    # Check word count
    word_count = count_words(content)
    if word_count < 1000:
        suggestions.append({
            "section": "Overall",
            "status": "short",
            "suggestion": f"Expand content - currently {word_count} words, needs 1000+"
        })
    
    return suggestions

def scan_pages():
    """Scan all game pages for expansion needs"""
    expansion_needed = []
    
    games_path = VAULT_PATH / "Games"
    
    for game_dir in games_path.iterdir():
        if not game_dir.is_dir():
            continue
        
        for page_file in game_dir.glob("*.md"):
            try:
                content = page_file.read_text(encoding='utf-8')
                word_count = count_words(content)
                citation_count = count_citations(content)
                
                if citation_count < 15 or word_count < 1000:
                    suggestions = suggest_expansions(content, page_file)
                    
                    expansion_needed.append({
                        "file": str(page_file.relative_to(VAULT_PATH)),
                        "game": page_file.stem,
                        "word_count": word_count,
                        "citation_count": citation_count,
                        "suggestions": suggestions
                    })
                    
            except Exception as e:
                print(f"Error reading {page_file}: {e}")
    
    # Sort by severity (lowest citations/words first)
    expansion_needed.sort(key=lambda x: (x["citation_count"], x["word_count"]))
    
    return expansion_needed

def generate_report(expansion_list, date):
    """Generate a markdown report"""
    report = f"""# SierraVault Expansion Needed - {date}

**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Pages Scanned:** {len(list((VAULT_PATH / "Games").iterdir()))} game directories
**Pages Needing Expansion:** {len(expansion_list)}

---

## Summary

| Metric | Count |
|--------|-------|
| Low citations (<15) | {sum(1 for p in expansion_list if p['citation_count'] < 15)} |
| Short content (<1000 words) | {sum(1 for p in expansion_list if p['word_count'] < 1000)} |
| Missing sections | {sum(1 for p in expansion_list for s in p['suggestions'] if s['status'] == 'missing')} |
| Shallow sections | {sum(1 for p in expansion_list for s in p['suggestions'] if s['status'] == 'shallow')} |

---

## Priority: Critical (Citations <10)

"""
    
    critical = [p for p in expansion_list if p['citation_count'] < 10]
    if critical:
        for page in critical:
            report += f"### [[{page['game']}]]\n"
            report += f"- **Citations:** {page['citation_count']}/15 (need {15 - page['citation_count']}+)\n"
            report += f"- **Words:** {page['word_count']}/1000\n"
            report += f"- **File:** `{page['file']}`\n"
            for s in page['suggestions'][:3]:
                report += f"  - ✍️ {s['suggestion']}\n"
            report += "\n"
    else:
        report += "*None*\n\n"
    
    report += "---\n\n## Priority: High (Citations 10-14)\n\n"
    
    high = [p for p in expansion_list if 10 <= p['citation_count'] < 15]
    if high:
        for page in high:
            report += f"### [[{page['game']}]]\n"
            report += f"- **Citations:** {page['citation_count']}/15 (need {15 - page['citation_count']}+)\n"
            report += f"- **Words:** {page['word_count']}/1000\n"
            report += f"- **File:** `{page['file']}`\n"
            for s in page['suggestions'][:2]:
                report += f"  - ✍️ {s['suggestion']}\n"
            report += "\n"
    else:
        report += "*None*\n\n"
    
    report += "---\n\n## Priority: Medium (Short Content)\n\n"
    
    short = [p for p in expansion_list if 15 <= p['citation_count'] and p['word_count'] < 1000]
    if short:
        for page in short:
            report += f"### [[{page['game']}]]\n"
            report += f"- **Words:** {page['word_count']}/1000 (need {1000 - page['word_count']}+)\n"
            report += f"- **File:** `{page['file']}`\n"
            for s in page['suggestions'][:2]:
                report += f"  - ✍️ {s['suggestion']}\n"
            report += "\n"
    else:
        report += "*None*\n\n"
    
    report += "---\n\n## TODO Items for Next Day\n\n"
    
    # Generate actionable TODO items
    report += "### Today's Tasks\n\n"
    
    task_num = 1
    # Start with critical citation pages
    for page in critical[:5]:
        report += f"- [ ] Expand `{page['file']}` - add {15 - page['citation_count']}+ citations\n"
        for s in page['suggestions']:
            if s['status'] == 'missing':
                report += f"    - Create {s['section']} section\n"
        task_num += 1
    
    # Add high priority pages
    for page in high[:5]:
        report += f"- [ ] Expand `{page['file']}` - add {15 - page['citation_count']}+ citations\n"
        task_num += 1
    
    # Add short content pages
    for page in short[:5]:
        report += f"- [ ] Expand `{page['file']}` - add {1000 - page['word_count']}+ words\n"
        task_num += 1
    
    report += "\n---\n\n## Quick Stats\n\n"
    if expansion_list:
        avg_citations = sum(p['citation_count'] for p in expansion_list) / len(expansion_list)
        avg_words = sum(p['word_count'] for p in expansion_list) / len(expansion_list)
        report += f"- **Average citations (expansion needed):** {avg_citations:.1f}/15\n"
        report += f"- **Average word count (expansion needed):** {avg_words:.0f}/1000\n"
    
    # Section frequency
    section_freq = {}
    for page in expansion_list:
        for s in page['suggestions']:
            if s['section'] in section_freq:
                section_freq[s['section']] += 1
            else:
                section_freq[s['section']] = 1
    
    report += "\n### Most Common Expansion Needs\n\n"
    for section, count in sorted(section_freq.items(), key=lambda x: -x[1])[:5]:
        report += f"- **{section}:** {count} pages\n"
    
    return report

def main():
    print("🔍 Scanning SierraVault for expansion opportunities...")
    
    expansion_list = scan_pages()
    
    date = datetime.now().strftime("%Y-%m-%d")
    report = generate_report(expansion_list, date)
    
    # Save report
    MEMORY_PATH.mkdir(parents=True, exist_ok=True)
    report_path = MEMORY_PATH / f"expansion-needed-{date}.md"
    report_path.write_text(report, encoding='utf-8')
    
    print(f"✅ Report saved to: {report_path}")
    print(f"📊 Found {len(expansion_list)} pages needing expansion")
    
    # Quick summary
    critical = len([p for p in expansion_list if p['citation_count'] < 10])
    high = len([p for p in expansion_list if 10 <= p['citation_count'] < 15])
    short = len([p for p in expansion_list if 15 <= p['citation_count'] and p['word_count'] < 1000])
    
    print(f"   - Critical (<10 citations): {critical}")
    print(f"   - High (10-14 citations): {high}")
    print(f"   - Short content only: {short}")

if __name__ == "__main__":
    main()