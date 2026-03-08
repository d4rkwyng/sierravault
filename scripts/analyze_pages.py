#!/usr/bin/env python3
"""Analyze SierraVault pages for expansion opportunities."""

import os
import re
from pathlib import Path
from collections import defaultdict

VAULT_PATH = Path("vault/Games")
MIN_CITATIONS = 15
MIN_WORDS = 1000

def count_citations(filepath):
    """Count citation links in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Match [[link]] and [text](url) patterns
    wiki_links = len(re.findall(r'\[\[.*?\]\]', content))
    markdown_links = len(re.findall(r'\[.*?\]\(.*?\)', content))
    return wiki_links + markdown_links

def count_words(filepath):
    """Count words in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(content.split())

def check_section_present(filepath, section_header):
    """Check if a section exists in the file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return f"## {section_header}" in content or f"### {section_header}" in content

def analyze_page(filepath):
    """Analyze a single page for expansion needs."""
    try:
        citations = count_citations(filepath)
        words = count_words(filepath)
        
        sections = {
            "Purchase": check_section_present(filepath, "Purchase"),
            "Technical": check_section_present(filepath, "Technical"),
            "Development": check_section_present(filepath, "Development"),
            "Reception": check_section_present(filepath, "Reception"),
            "Legacy": check_section_present(filepath, "Legacy"),
            "Cast": check_section_present(filepath, "Cast"),
            "Music": check_section_present(filepath, "Music"),
            "Sequel": check_section_present(filepath, "Sequel"),
        }
        
        missing_sections = [s for s, present in sections.items() if not present]
        
        return {
            "file": str(filepath),
            "citations": citations,
            "words": words,
            "missing_sections": missing_sections,
            "needs_citations": citations < MIN_CITATIONS,
            "needs_words": words < MIN_WORDS,
        }
    except Exception as e:
        return {"file": str(filepath), "error": str(e)}

def main():
    """Scan all game pages and identify expansion needs."""
    results = []
    
    for filepath in VAULT_PATH.rglob("*.md"):
        if filepath.is_file():
            result = analyze_page(filepath)
            if "error" not in result:
                if result["needs_citations"] or result["needs_words"] or result["missing_sections"]:
                    results.append(result)
    
    # Sort by severity (missing citations > missing words > missing sections)
    results.sort(key=lambda x: (x["needs_citations"], x["needs_words"], -len(x["missing_sections"])))
    
    # Print summary
    print(f"=== EXPANSION ANALYSIS ===\n")
    print(f"Total pages analyzed: {len(results)}\n")
    
    for r in results[:30]:  # Top 30 needs
        print(f"\n{'='*60}")
        print(f"File: {r['file']}")
        print(f"Citations: {r['citations']} (need {MIN_CITATIONS})")
        print(f"Words: {r['words']} (need {MIN_WORDS})")
        
        if r["missing_sections"]:
            print(f"Missing sections: {', '.join(r['missing_sections'])}")
        
        # Generate suggestions
        suggestions = []
        if r["needs_citations"]:
            suggestions.append("Add more citations (MobyGames, GOG, Steam, Wikipedia, contemporary reviews)")
        if r["needs_words"]:
            suggestions.append("Expand with: development history, reception details, legacy impact")
        if "Purchase" not in r["missing_sections"]:
            suggestions.append("Add Purchase section with current platforms, pricing, availability")
        if "Technical" not in r["missing_sections"]:
            suggestions.append("Add Technical section: system requirements, engines, platforms")
        if "Reception" not in r["missing_sections"]:
            suggestions.append("Add Reception section: critical response, sales, awards")
        if "Legacy" not in r["missing_sections"]:
            suggestions.append("Add Legacy section: influence, re-releases, cultural impact")
        
        if suggestions:
            print(f"Suggestions:\n  - " + "\n  - ".join(suggestions))

if __name__ == "__main__":
    main()