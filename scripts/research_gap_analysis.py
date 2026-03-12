#!/usr/bin/env python3
"""
Research Gap Analysis for SierraVault
Identifies pages with low research utilization (<50%) and generates TODO lists.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
PUBLIC_VAULT = Path("/Users/woodd/Projects/sierravault/vault/Games")
RESEARCH_BASE = Path("/Users/woodd/Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault/research/games")
OUTPUT_DIR = Path("/Users/woodd/.openclaw/workspace/memory")

MIN_CITATIONS = 15
MIN_RESEARCH_UTILIZATION = 0.50  # 50% minimum research utilization

def get_research_sources(game_slug):
    """Get list of research files for a game."""
    game_dir = RESEARCH_BASE / game_slug
    if not game_dir.exists():
        return []
    
    sources = []
    for f in game_dir.glob("*.json"):
        if f.name.startswith("gog_") or f.name.startswith("steam_") or f.name.startswith("mobygames_") or \
           f.name.startswith("wikipedia_") or f.name.startswith("giantbomb_") or f.name.startswith("igdb_") or \
           f.name.startswith("sierrahelp_") or f.name.startswith("retrogames_") or f.name.startswith("gamespot_") or \
           f.name.startswith("ign_") or f.name.startswith("pcgamer_") or f.name.startswith("eurogamer_") or \
           f.name.startswith("polygon_") or f.name.startswith("kotaku_") or f.name.startswith("edge_") or \
           f.name.startswith("ruins_") or f.name.startswith("abandonware_") or f.name.startswith("retro_") or \
           f.name.startswith("pcgamingwiki_") or f.name.startswith("wikipediagame_") or f.name.startswith("fandom_"):
            sources.append(f.name)
    return sources

def count_citations_in_page(filepath):
    """Count citations in a game page."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match [[link]] wiki links and [text](url) markdown links
    wiki_links = len(re.findall(r'\[\[.*?\]\]', content))
    markdown_links = len(re.findall(r'\[.*?\]\(https?://[^\)]+\)', content))
    
    return wiki_links + markdown_links

def count_unique_sources(citations):
    """Estimate unique sources from citations."""
    # Rough heuristic: citations are often duplicated, estimate unique
    return max(1, int(citations * 0.7))

def get_game_slug_from_filename(filename):
    """Extract game slug from filename."""
    # Convert "1987 - Space Quest.md" to "space-quest-3"
    name = filename.replace(".md", "").replace(" - ", "-").replace(" ", "-").lower()
    # Clean up special chars but keep hyphens
    name = re.sub(r'[^a-z0-9-]', '', name)
    # Normalize multiple hyphens
    name = re.sub(r'-+', '-', name)
    # Strip leading/trailing hyphens
    name = name.strip('-')
    return name

def find_similar_research_slug(filename, all_research_slugs):
    """Find the best matching research slug for a game page."""
    # Extract key terms from filename
    clean_name = filename.replace(".md", "").lower()
    # Remove year prefix if present
    clean_name = re.sub(r'^\d{4}\s*-\s*', '', clean_name)
    
    # Create searchable version
    searchable = re.sub(r'[^a-z0-9]', ' ', clean_name).lower()
    search_words = searchable.split()
    
    best_match = None
    best_score = 0
    
    for research_slug in all_research_slugs:
        research_words = research_slug.replace('-', ' ').split()
        score = 0
        
        # Score based on word overlap
        for word in search_words:
            if len(word) > 2 and word in research_words:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = research_slug
    
    return best_match, best_score

def preload_research_slugs():
    """Preload all research slugs for fast lookup."""
    research_base = Path("/Users/woodd/Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault/research/games")
    slugs = []
    
    if research_base.exists():
        for dir_path in research_base.iterdir():
            if dir_path.is_dir():
                slugs.append(dir_path.name)
    
    return slugs

def analyze_research_gap(filepath, all_research_slugs=None):
    """Analyze research gap for a single game page."""
    try:
        filename = filepath.name
        citations = count_citations_in_page(filepath)
        generated_slug = get_game_slug_from_filename(filename)
        
        # Try to find matching research slug
        if all_research_slugs is None:
            all_research_slugs = preload_research_slugs()
        
        matched_slug, match_score = find_similar_research_slug(filename, all_research_slugs)
        
        # Use matched slug if good match, otherwise try generated slug
        if match_score > 2:
            game_slug = matched_slug
        else:
            game_slug = generated_slug
        
        research_sources = get_research_sources(game_slug)
        
        # Calculate research utilization
        expected_sources = max(8, citations)  # Expect ~1 source per 2 citations
        actual_sources = len(research_sources)
        
        if expected_sources > 0:
            utilization = actual_sources / expected_sources
        else:
            utilization = 1.0  # No citations = no research needed
        
        return {
            "file": str(filepath),
            "filename": filename,
            "slug": game_slug,
            "citations": citations,
            "research_sources": actual_sources,
            "expected_sources": expected_sources,
            "utilization": utilization,
            "gap": expected_sources - actual_sources,
            "sources_list": research_sources,
            "missing": expected_sources > actual_sources,
        }
    except Exception as e:
        return {
            "file": str(filepath),
            "filename": filepath.name,
            "error": str(e),
        }

def generate_report(analyses):
    """Generate a markdown report of research gaps."""
    report_lines = [
        "# Research Gap Analysis Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
    ]
    
    total_pages = len(analyses)
    low_research = [a for a in analyses if a.get("utilization", 1.0) < MIN_RESEARCH_UTILIZATION]
    critical_low = [a for a in low_research if a.get("utilization", 1.0) < 0.25]
    
    report_lines.extend([
        f"- **Total pages analyzed:** {total_pages}",
        f"- **Pages with <50% research utilization:** {len(low_research)}",
        f"- **Critical (<25% utilization):** {len(critical_low)}",
        "",
        "## TODO List - Pages Needing Research Integration",
        "",
    ])
    
    # Sort by utilization (lowest first)
    sorted_gaps = sorted([a for a in analyses if not a.get("error")], 
                         key=lambda x: x.get("utilization", 1.0))
    
    for i, gap in enumerate(sorted_gaps, 1):
        if gap.get("utilization", 1.0) >= MIN_RESEARCH_UTILIZATION:
            break
            
        report_lines.extend([
            f"### {i}. {gap['filename']}",
            f"- **File:** `{gap['file']}`",
            f"- **Slug:** `{gap['slug']}`",
            f"- **Citations:** {gap['citations']}",
            f"- **Research Sources:** {gap['research_sources']}/{gap['expected_sources']}",
            f"- **Utilization:** {gap['utilization']*100:.1f}%",
            f"- **Gap:** {gap['gap']} sources needed",
            "",
            "#### Current Sources:",
        ])
        
        for src in gap.get("sources_list", [])[:5]:
            report_lines.append(f"- {src}")
        
        if len(gap.get("sources_list", [])) > 5:
            report_lines.append(f"- ... and {len(gap['sources_list']) - 5} more")
        
        report_lines.extend([
            "",
            "#### Recommended Actions:",
            "- [ ] Add citations from: MobyGames, GOG, Steam, Wikipedia, contemporary reviews",
            "- [ ] Cross-reference with related games in series",
            "- [ ] Verify release dates and platform availability",
            "",
            "---",
            "",
        ])
    
    # Add quick action commands
    report_lines.extend([
        "## Quick Actions",
        "",
        "### Open pages in Obsidian:",
        "",
    ])
    
    for gap in sorted_gaps[:20]:
        if gap.get("utilization", 1.0) < MIN_RESEARCH_UTILIZATION:
            slug = gap.get("slug", "")
            report_lines.append(f"- `{obsidian_open_command(gap['file'])}`")
    
    report_lines.extend([
        "",
        "### Batch research commands:",
        "",
        "```bash",
        "# Check research folders for specific games",
        f"ls -la {RESEARCH_BASE}/<game-slug>/",
        "",
        "# Find games with no research at all",
        f"find {RESEARCH_BASE} -maxdepth 1 -type d | wc -l",
        "",
        "```",
        "",
        "## Notes",
        "",
        "- Research utilization should be ≥50% for all games",
        "- Flagship titles (KQ, SQ, QFG series) should aim for ≥75%",
        "- Each citation should ideally come from a unique source",
        "- Missing sources often include: contemporary reviews, technical documentation, developer interviews",
        "",
    ])
    
    return "\n".join(report_lines)

def obsidian_open_command(filepath):
    """Generate obsidian-cli command to open a file."""
    return f"obsidian-cli open \"{filepath}\""

def main():
    """Main analysis function."""
    print("=== RESEARCH GAP ANALYSIS ===")
    print(f"Analyzing pages in: {PUBLIC_VAULT}")
    print(f"Research base: {RESEARCH_BASE}")
    print(f"Minimum utilization target: {MIN_RESEARCH_UTILIZATION*100}%")
    print()
    
    # Scan all game pages
    analyses = []
    total = 0
    
    for filepath in PUBLIC_VAULT.rglob("*.md"):
        if filepath.is_file():
            total += 1
            result = analyze_research_gap(filepath)
            analyses.append(result)
            
            if total % 50 == 0:
                print(f"Analyzed {total} pages...")
    
    print(f"\nAnalyzed {total} pages total")
    
    # Generate report
    report = generate_report(analyses)
    
    # Save report
    output_path = OUTPUT_DIR / "research-gaps-2026-03-03.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_path}")
    
    # Print summary
    low_research = [a for a in analyses if a.get("utilization", 1.0) < MIN_RESEARCH_UTILIZATION and not a.get("error")]
    critical_low = [a for a in low_research if a.get("utilization", 1.0) < 0.25]
    
    print(f"\n=== SUMMARY ===")
    print(f"Pages with <50% research utilization: {len(low_research)}")
    if critical_low:
        print(f"Critical cases (<25% utilization): {len(critical_low)}")
        print("\nTop critical gaps:")
        for gap in sorted(critical_low, key=lambda x: x.get("utilization", 1.0))[:5]:
            print(f"  - {gap['filename']}: {gap['utilization']*100:.1f}% ({gap['research_sources']}/{gap['expected_sources']} sources)")

if __name__ == "__main__":
    main()