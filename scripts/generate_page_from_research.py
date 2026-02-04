#!/usr/bin/env python3
"""
Generate Page from Research - Creates game pages from enriched research files.

Reads all JSON files in a research folder and generates a comprehensive page
that uses as many sources as possible.

Usage:
  python generate_page_from_research.py kings-quest-vii
  python generate_page_from_research.py kings-quest-vii -o output.md
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"

GENERATION_PROMPT = """You are generating a comprehensive game page for the Sierra Games Archive.

GAME: {game_title}

I have collected {source_count} research sources for this game. Below is all the extracted data.
Your task is to write a complete wiki-style page that:

1. Uses information from AS MANY sources as possible
2. Includes inline citations [^ref-N] throughout ALL prose sections
3. Has a minimum of 20 references (aim for 30+)
4. Follows the exact section format specified below

RESEARCH DATA:
{research_data}

REQUIRED PAGE STRUCTURE (use exactly this order):

```markdown
---
title: "Game Title"
release_year: YYYY
developer: "Developer Name"
designer:
  - "Designer Name"
publisher: "Publisher Name"
genre: "Adventure"
platforms: ["Platform1", "Platform2"]
series: "Series Name"
engine: "Engine Name"
protagonist: "Character Name"
sierra_lineage: "Core Sierra"
last_updated: "{today}"
---

# Game Title

<small style="color: gray">Last updated: {today_full}</small>

## Overview

[2-3 paragraphs introducing the game, its significance, and key features. MUST have inline citations.]

> [!info]- Game Info
> **Developer:** Developer Name[^ref-1]
> **Designer:** Designer Name[^ref-1]
> **Publisher:** Publisher Name[^ref-1]
> **Engine:** Engine Name[^ref-2]
> **Platforms:** Platform list[^ref-1]
> **Release Year:** Year
> **Series:** Series Name
> **Protagonist:** Character Name
> **Sierra Lineage:** Core Sierra

## Story Summary

[3-4 paragraphs covering the full plot. Include character names, locations, major events. Citations required.]

## Gameplay

### Interface and Controls
[How the game is played - parser, point-and-click, etc. Citations required.]

### Structure and Progression
[Chapters, areas, progression system. If the game has chapters or distinct areas, LIST THEM:]

- **Chapter 1:** Description
- **Chapter 2:** Description
[etc.]

### Puzzles and Mechanics
[Puzzle types, inventory, special mechanics. Citations required.]

## Reception

### Contemporary Reviews
[Magazine reviews from release era with SPECIFIC SCORES. Format: "Publication gave X/5"[^ref-N]. List multiple reviews.]

### Modern Assessment
[Later retrospectives, current ratings, reappraisals. Include aggregate scores.]

**Aggregate Scores:**
- **MobyGames:** X/10 (N reviews)[^ref-N]
- **IMDB:** X/10 (N ratings)[^ref-N]
[etc.]

## Development

### Origins
[How the game came to be, creative vision. Citations required.]

### Production
[Development process, team, challenges. Citations required.]

**Development Credits:**[^ref-N] (Include if available in research)
- **Executive Designer:** Name
- **Co-Designer:** Name
- **Project Manager:** Name
- **Lead Programmer:** Name
- **Programmers:** Names
- **Senior Artists:** Names
- **Composer:** Name
[Include all credited team members from research]

### Animation Production (if outsourced)
[List studios with their specific contributions:]
- **Studio Name** (Location) – What they worked on
- **Studio Name** (Location) – What they worked on

### Technical Achievements
[Engine innovations, graphics, sound. Citations required.]

### Technical Specifications
[Resolution, colors, audio options, disk space, RAM requirements. Format as subsections:]

**CD-ROM Version:**[^ref-N]
- **Resolution:** 640x480, 256 colors
- **Audio:** Sound Blaster, General MIDI, Roland MT-32
- **Disk Space:** XX MB
- **RAM:** X MB

**Floppy Version:** (if applicable)
- **Disks:** N high-density
- **Size:** XX MB

### Cut Content
[Removed features if known. Citations required.]

### Version History

| Version | Date | Platform | Notes |
|---------|------|----------|-------|
| 1.0 | Date | Platform | Initial release[^ref-N] |
[Additional versions...]

**SCI/AGI Interpreter Versions:**[^ref-N] (REQUIRED for Sierra SCI/AGI games - check SCI Wiki, PCGamingWiki)

| Game Version | Interpreter | Type | Notes |
|--------------|-------------|------|-------|
| 1.0 | 1.001.054 | SCI1.1 | Initial release |
| CD-ROM | l.cfs.158 | SCI1.1 | CD version |
[Include ALL versions with actual interpreter numbers from research data. This is critical technical info.]

### Technical Issues
[Known bugs, compatibility issues, patches. Include firecracker-type bugs if relevant.]

### Easter Eggs and Trivia
[Hidden content, pop culture references, debug modes. Be SPECIFIC with examples:]
- Example 1: "Quote or description"[^ref-N]
- Example 2: "Quote or description"[^ref-N]
[etc.]

### Multiple Endings (if applicable)
[Document ending variations and what triggers them. List key variables:]
- **Variable 1:** Whether player did X or Y
- **Variable 2:** Whether item was obtained
The "best" ending requires: [list requirements][^ref-N]

## Voice Cast

(Include if game has voice acting)

| Character | Voice Actor |
|-----------|-------------|
| Protagonist | Actor Name |
| Antagonist | Actor Name |
[Full cast table...]

Voice direction by [Name]; recorded at [Studio][^ref-N].

## Legacy

### Sales and Commercial Impact
[Sales figures, bundling, awards. Citations required.]

### Collections
[Compilations the game appeared in. Citations required.]

### Fan Projects
[Remakes, mods if applicable. Citations required.]

### Related Publications
[Official hint books, strategy guides, novelizations. Include author, publisher, date:]
- **Guidebook Name:** Written by Author, illustrated by Artist, included with game[^ref-N]
- **Official Hint Book:** Author, Publisher, page count[^ref-N]
- **Novelization:** Title by Author (if exists)[^ref-N]

### Critical Perspective
[1-2 paragraphs on the game's historical significance, how it fits in adventure gaming history, its lasting influence or lack thereof. Include retrospective analysis from modern critics.]

## Downloads

**Purchase / Digital Stores**
- [GOG](URL) - if available
- [Steam](URL) - if available

**Download / Preservation**
- [Internet Archive](URL)
- [MyAbandonware](URL)

**Manuals & Extras**
- [Manual PDF](URL) - if found in research

## Series Continuity

[Brief paragraph about where this fits in the series, connections to other games, timeline. Include story connections, returning characters, and how this game sets up or follows from others.]

- **Previous:** [[YEAR - Previous Game Title]]
- **Next:** [[YEAR - Next Game Title]]

**CRITICAL:** Use the ACTUAL sequential games in the series:
- For King's Quest VII (1994): Previous is King's Quest VI (1992), Next is King's Quest VIII/Mask of Eternity (1998)
- For King's Quest VI (1992): Previous is King's Quest V (1990), Next is King's Quest VII (1994)
- Use the release year and full title. Look for series info in research data.
- Omit Previous if first in series, omit Next if last.

## References

[^ref-1]: [Source Name](URL) – what information was cited
[^ref-2]: [Source Name](URL) – what information was cited
[...continue for all references...]
```

CRITICAL RULES:
1. Every factual claim MUST have a citation - no orphan facts
2. Use [[Roberta Williams]] style wiki links for designers/developers (plain text in YAML/callout)
3. Include SPECIFIC review scores (not just "praised" or "well-received")
4. Minimum 20 unique references, aim for 30+
5. For reviews, always include: publication name, score, reviewer name if known, date
6. Do not invent any facts not present in the research data
7. Include Voice Cast table if game has voice acting
8. Include Easter Eggs section with specific examples if available in research
9. Include Series Continuity with CORRECT Previous/Next links based on release years
10. Include Development Credits block with all credited team members from research
11. Include SCI/AGI interpreter version table with ACTUAL version numbers from SCI Wiki/PCGamingWiki
12. Include Technical Specifications subsection with resolution, audio, disk space
13. Include Related Publications section for hint books, manuals, guides
14. Include Critical Perspective subsection analyzing the game's historical significance

**REFERENCE FORMATTING (MANDATORY)**:
- Use HUMAN-READABLE titles, not source_ids
- Format: [^ref-N]: [Human Title – Subtitle](URL) – facts cited
- Examples:
  - GOOD: [^ref-1]: [MobyGames – King's Quest VII](https://mobygames.com/...) – ratings, credits, releases
  - BAD: [^ref-1]: [mobygames](https://mobygames.com/...) – ratings, credits
  - GOOD: [^ref-2]: [Computer Gaming World #127 (February 1995)](https://archive.org/...) – Charles Ardai review
  - BAD: [^ref-2]: [cgw_127_ocr](https://archive.org/...) – review
- Transform source_ids to readable names:
  - mobygames → "MobyGames – [Game Title]"
  - wikipedia → "Wikipedia – [Game Title]"
  - sierra_fandom → "Sierra Fandom Wiki"
  - kq_fandom → "King's Quest Omnipedia"
  - cgw_NNN_ocr → "Computer Gaming World #NNN"
  - archive_org → "Internet Archive"
  - sciwiki → "SCI Wiki"
  - pcgamingwiki → "PCGamingWiki"
  - tvtropes → "TV Tropes"
  - imdb_* → "IMDB"
  - btva → "Behind The Voice Actors"

**REFERENCE CONSOLIDATION (MANDATORY)**:
- Each unique source gets exactly ONE reference number
- If MobyGames is cited 10 times, ALL 10 citations use the SAME [^ref-N]
- The References section must have ONE LINE per unique source

Generate the complete page now. Include ALL sections. Do not truncate."""


def load_env():
    """Load environment variables from .env file."""
    env_path = INTERNAL_DIR / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value


def load_research(folder_path: Path) -> tuple[str, list[dict]]:
    """Load all research files from a folder."""
    manifest_path = folder_path / "_manifest.json"

    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        game_title = manifest.get('game_title', folder_path.name.replace('-', ' ').title())
    else:
        game_title = folder_path.name.replace('-', ' ').title()

    sources = []
    for file_path in sorted(folder_path.glob("*.json")):
        if file_path.name == "_manifest.json":
            continue

        with open(file_path) as f:
            data = json.load(f)

        # Skip failed/blocked sources with no content
        if data.get('fetch_status') in ['failed', 'blocked'] and not data.get('full_text'):
            continue

        # Build source summary
        source = {
            'source_id': data.get('source_id', file_path.stem),
            'url': data.get('url', ''),
            'source_type': data.get('source_type', 'unknown'),
            'extracted_facts': data.get('extracted_facts', {}),
            'key_quotes': data.get('key_quotes', []),
            'source_significance': data.get('source_significance', ''),
        }

        # Include truncated full_text for context if no extracted_facts
        if not source['extracted_facts'] and data.get('full_text'):
            source['content_preview'] = data['full_text'][:2000]

        sources.append(source)

    return game_title, sources


def format_research_data(sources: list[dict]) -> str:
    """Format research data for the prompt."""
    output = []

    for i, src in enumerate(sources, 1):
        output.append(f"\n--- SOURCE {i}: {src['source_id']} ({src['source_type']}) ---")
        output.append(f"URL: {src['url']}")

        if src.get('source_significance'):
            output.append(f"Significance: {src['source_significance']}")

        if src.get('extracted_facts'):
            output.append(f"Extracted Facts: {json.dumps(src['extracted_facts'], indent=2)}")

        if src.get('key_quotes'):
            output.append("Key Quotes:")
            for q in src['key_quotes']:
                if isinstance(q, dict):
                    output.append(f"  - \"{q.get('quote', '')}\" - {q.get('attribution', '')}")
                elif isinstance(q, str):
                    output.append(f"  - \"{q}\"")

        if src.get('content_preview'):
            output.append(f"Content Preview: {src['content_preview']}")

    return '\n'.join(output)


def generate_page(game_slug: str, output_path: Path = None) -> bool:
    """Generate a page from enriched research."""
    load_env()

    folder_path = GAMES_RESEARCH_DIR / game_slug
    if not folder_path.exists():
        print(f"Error: Research folder not found: {folder_path}")
        return False

    print(f"Loading research from: {folder_path}")
    game_title, sources = load_research(folder_path)

    if not sources:
        print("Error: No valid sources found in research folder")
        return False

    print(f"Found {len(sources)} sources for: {game_title}")

    # Format research data
    research_data = format_research_data(sources)

    # Truncate if too long (Claude can handle ~200k tokens, but keep it reasonable)
    if len(research_data) > 150000:
        print(f"Warning: Research data truncated from {len(research_data)} to 150000 chars")
        research_data = research_data[:150000]

    today = datetime.now().strftime("%Y-%m-%d")
    today_full = datetime.now().strftime("%B %d, %Y")

    prompt = GENERATION_PROMPT.format(
        game_title=game_title,
        source_count=len(sources),
        research_data=research_data,
        today=today,
        today_full=today_full
    )

    print(f"Prompt length: {len(prompt)} chars")
    print("Generating page with Claude Opus 4.5 (highest quality)...")

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        return False

    client = anthropic.Anthropic(api_key=api_key)

    # Use Opus 4.5 for highest quality page generation
    # Opus produces pages comparable to interactive generation with better:
    # - Fact synthesis from multiple sources
    # - Reference consolidation
    # - Series continuity accuracy
    # - Overall coherence
    response = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}]
    )

    page_content = response.content[0].text

    # Clean up - remove markdown code blocks if wrapped
    if page_content.startswith('```'):
        lines = page_content.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        page_content = '\n'.join(lines)

    # Save output
    if output_path is None:
        output_path = Path(f"/tmp/{game_slug}.md")

    with open(output_path, 'w') as f:
        f.write(page_content)

    print(f"\nPage generated: {output_path}")
    print(f"Length: {len(page_content)} chars")

    # Count references
    import re
    refs = re.findall(r'\[\^ref-\d+\]:', page_content)
    print(f"References: {len(refs)}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Generate page from enriched research")
    parser.add_argument("game_slug", help="Research folder name (e.g., kings-quest-vii)")
    parser.add_argument("-o", "--output", type=Path, help="Output file path")

    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("Error: anthropic package required. Run: pip install anthropic")
        sys.exit(1)

    success = generate_page(args.game_slug, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
