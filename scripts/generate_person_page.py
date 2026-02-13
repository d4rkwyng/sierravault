#!/usr/bin/env python3
"""
Generate Designer/Developer pages from enriched research.

Usage:
  python generate_person_page.py designers/al-lowe -o /tmp/al_lowe.md
  python generate_person_page.py developers/dynamix -o /tmp/dynamix.md
  python generate_person_page.py --all-designers
  python generate_person_page.py --all-developers
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

INTERNAL_ROOT = Path(os.environ.get("SIERRAVAULT_INTERNAL", Path(__file__).parent.parent.parent / "../Library/CloudStorage/ProtonDrive-woodd@mindtricks.io-folder/Assets/sierravault"))
RESEARCH_DIR = INTERNAL_ROOT / "research"
VAULT_DIR = Path(__file__).parent.parent  # sierravault repo root


def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value


def get_client():
    """Get Anthropic client."""
    load_env()
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=api_key)


def load_research(person_type: str, person_slug: str) -> dict:
    """Load all research files for a person - comprehensive extraction."""
    folder = RESEARCH_DIR / person_type / person_slug
    if not folder.exists():
        raise FileNotFoundError(f"Research folder not found: {folder}")

    research = {
        "person_name": person_slug.replace("-", " ").title(),
        "person_type": person_type.rstrip("s"),  # designers -> designer
        "sources": [],
        "all_quotes": [],
        "all_facts": {}
    }

    for f in folder.glob("*.json"):
        if f.name.startswith("_"):
            continue
        try:
            data = json.load(open(f))
            url = data.get("url", "")

            # Extract source info
            source = {
                "filename": f.name,
                "url": url,
                "source_type": data.get("source_type", f.stem),
                "full_text": data.get("full_text", "")[:20000],  # Increased from 15K
                "extracted_facts": data.get("extracted_facts", {}),
                "key_quotes": data.get("key_quotes", []),
                "source_significance": data.get("source_significance", "")
            }

            # Collect ALL quotes with source attribution
            for quote in data.get("key_quotes", []):
                if isinstance(quote, dict):
                    quote["source_url"] = url
                    quote["source_file"] = f.name
                    research["all_quotes"].append(quote)

            # Merge extracted facts
            for key, value in data.get("extracted_facts", {}).items():
                if value and key not in research["all_facts"]:
                    research["all_facts"][key] = {"value": value, "source": url}

            if source["full_text"] or source["extracted_facts"]:
                research["sources"].append(source)
        except Exception as e:
            print(f"  Warning: Could not load {f.name}: {e}")

    return research


def get_existing_games(person_name: str) -> list:
    """Find games by this person in the vault."""
    games = []
    games_dir = VAULT_DIR / "Games"

    for md_file in games_dir.rglob("*.md"):
        try:
            content = md_file.read_text()
            # Check if person is mentioned in designer/developer fields
            if person_name.lower() in content.lower():
                # Extract year from filename
                filename = md_file.stem
                year = filename[:4] if filename[:4].isdigit() else "Unknown"
                title = filename[7:] if filename[:4].isdigit() else filename
                games.append({
                    "title": title,
                    "year": year,
                    "path": str(md_file.relative_to(VAULT_DIR))
                })
        except:
            pass

    return sorted(games, key=lambda x: x.get("year", "0000"))


DESIGNER_PROMPT = """You are writing a comprehensive biography page for {person_name}, a video game designer.

=== MANDATORY SOURCE URLS (you MUST cite ALL of these) ===
{source_urls}

=== EXTRACTED FACTS FROM RESEARCH ===
{research_json}

=== GAMES BY THIS DESIGNER (from vault) ===
{games_list}

Write a complete Obsidian markdown page following this EXACT format:

```markdown
---
title: "{person_name}"
type: designer
birth_year: [year if known, else null]
death_year: [year if applicable, else null]
notable_games: ["Game 1", "Game 2", "Game 3"]
companies: ["Company 1", "Company 2"]
last_updated: "{today}"
---
# {person_name}

## Overview
[2-3 paragraphs providing a comprehensive biography. Include birth/death dates if known, education, how they entered the game industry, and their overall significance to gaming history.]

## Career
### Early Career
[Details about how they started in gaming]

### Sierra Years
[Their work at Sierra On-Line - projects, roles, achievements]

### Later Career
[Post-Sierra work if applicable]

## Notable Works

### [Game Title 1] (Year)
[2-3 sentences about their specific contribution to this game, development challenges, quotes from interviews]

### [Game Title 2] (Year)
[Similar detail]

[Continue for 3-5 most significant games]

## Design Philosophy
[If quotes or information available about their approach to game design]

## Legacy
[Their impact on the gaming industry, influence on other designers, awards, recognitions]

## Games
[List ALL games from the vault, formatted as wiki links]
- [[Game Path|Game Title]] — Year, Series

## References
[^ref-1]: [Source Name](URL) — what information was used
[^ref-2]: [Source Name](URL) — what information was used
[Continue for all sources used - minimum 8 references]
```

CRITICAL RULES - FAILURE TO FOLLOW WILL RESULT IN REJECTION:
1. **EVERY URL from MANDATORY SOURCE URLS section MUST appear in your References** - no exceptions!
2. You MUST have at least {source_count} references (one for each source URL provided)
3. NEVER invent or make up sources - only use the URLs provided above
4. Include inline citations [^ref-X] throughout ALL prose sections
5. If birth/death dates unknown, use null in YAML
6. Use wiki links [[...]] for game titles in the Games section
7. Be specific about contributions - avoid vague praise
8. Include direct quotes where available (with attribution)
9. Each Notable Works subsection MUST have specific development details with citations

REFERENCE FORMAT - USE EXACTLY THIS FORMAT:
[^ref-1]: [Source Name](exact_url_from_list_above) — what info was used
[^ref-2]: [Source Name](exact_url_from_list_above) — what info was used
... continue for ALL {source_count} sources

QUALITY REQUIREMENTS:
- Target 2000+ words of content
- Minimum {source_count} references (cite every source provided)
- At least 2-3 inline citations per source
- Include specific dates, years, quotes, and factual details

Return ONLY the markdown content, no explanations."""


DEVELOPER_PROMPT = """You are writing a comprehensive page for {person_name}, a video game development studio.

=== MANDATORY SOURCE URLS (you MUST cite ALL of these) ===
{source_urls}

=== EXTRACTED FACTS FROM RESEARCH ===
{research_json}

=== GAMES BY THIS DEVELOPER (from vault) ===
{games_list}

Write a complete Obsidian markdown page following this EXACT format:

```markdown
---
title: "{person_name}"
type: developer
founded: [year]
defunct: [year or null if still active]
headquarters: "City, State/Country"
key_people: ["Person 1", "Person 2"]
parent_company: "Parent Company or null"
last_updated: "{today}"
---
# {person_name}

## Overview
[2-3 paragraphs providing company history. Include founding date, founders, location, acquisition history, and closure if applicable.]

## History
### Founding and Early Years
[How the company was founded, by whom, initial projects]

### Sierra Era
[Their relationship with Sierra - acquisition, collaboration, key projects]

### [Later Period if applicable]
[Post-Sierra history, acquisition, closure]

## Notable Games

### [Game Title 1] (Year)
[2-3 sentences about this game's development, significance, reception]

### [Game Title 2] (Year)
[Similar detail]

[Continue for 3-5 most significant games]

## Technology and Innovation
[Notable engines, tools, or technical achievements if applicable]

## Legacy
[Company's impact on gaming, notable alumni, influence]

## Games
[List ALL games from the vault, formatted as wiki links]
- [[Game Path|Game Title]] — Year

## References
[^ref-1]: [Source Name](URL) — what information was used
[^ref-2]: [Source Name](URL) — what information was used
[Continue for all sources used - minimum 8 references]
```

CRITICAL RULES - FAILURE TO FOLLOW WILL RESULT IN REJECTION:
1. **EVERY URL from MANDATORY SOURCE URLS section MUST appear in your References** - no exceptions!
2. You MUST have at least {source_count} references (one for each source URL provided)
3. NEVER invent or make up sources - only use the URLs provided above
4. Include inline citations [^ref-X] throughout ALL prose sections
5. Use null for unknown/not applicable fields in YAML
6. Use wiki links [[...]] for game titles
7. Be specific about company achievements
8. Include founding/closure dates where known
9. If Sierra acquired them, note the acquisition details

REFERENCE FORMAT - USE EXACTLY THIS FORMAT:
[^ref-1]: [Source Name](exact_url_from_list_above) — what info was used
[^ref-2]: [Source Name](exact_url_from_list_above) — what info was used
... continue for ALL {source_count} sources

QUALITY REQUIREMENTS:
- Target 2000+ words of content
- Minimum {source_count} references (cite every source provided)
- At least 2-3 inline citations per source
- Include specific dates, years, quotes, and factual details

Return ONLY the markdown content, no explanations."""


def generate_page(person_type: str, person_slug: str, output_path: Path = None) -> str:
    """Generate a page for a designer or developer."""
    print(f"Generating page for {person_type}/{person_slug}...")

    # Load research
    research = load_research(person_type, person_slug)
    print(f"  Loaded {len(research['sources'])} research sources")

    # Get games from vault
    games = get_existing_games(research["person_name"])
    print(f"  Found {len(games)} games in vault")

    # Prepare explicit source URL list
    source_urls = []
    for src in research["sources"][:15]:
        url = src.get("url", "")
        if url and url.startswith("http"):
            source_urls.append(f"- {url}")

    source_urls_str = "\n".join(source_urls) if source_urls else "No URLs available"
    source_count = len(source_urls)
    print(f"  Requiring {source_count} references (sources with URLs)")

    # Prepare research JSON (truncated for context window)
    research_json = json.dumps(research["sources"][:15], indent=2, default=str)[:50000]

    # Prepare games list
    games_list = "\n".join([
        f"- {g['title']} ({g['year']}) - {g['path']}"
        for g in games[:30]  # Limit to 30 games
    ]) or "No games found in vault"

    # Select prompt based on type
    if person_type == "designers":
        prompt = DESIGNER_PROMPT
    else:
        prompt = DEVELOPER_PROMPT

    prompt = prompt.format(
        person_name=research["person_name"],
        source_urls=source_urls_str,
        source_count=source_count,
        research_json=research_json,
        games_list=games_list,
        today=datetime.now().strftime("%Y-%m-%d")
    )

    # Call Claude
    client = get_client()
    print("  Calling Claude API...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text.strip()

    # Clean up markdown code blocks if present
    if content.startswith("```markdown"):
        content = content[11:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # Save if output path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        print(f"  Saved to {output_path}")

    return content


def main():
    parser = argparse.ArgumentParser(description="Generate designer/developer pages")
    parser.add_argument("person", nargs="?", help="Person path (e.g., designers/al-lowe)")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--all-designers", action="store_true", help="Generate all designer pages")
    parser.add_argument("--all-developers", action="store_true", help="Generate all developer pages")
    parser.add_argument("--dry-run", action="store_true", help="List what would be generated")

    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("Error: anthropic package required. Run: pip install anthropic")
        sys.exit(1)

    if args.all_designers:
        designers_dir = RESEARCH_DIR / "designers"
        if not designers_dir.exists():
            print("No designers research folder found")
            sys.exit(1)

        for folder in sorted(designers_dir.iterdir()):
            if folder.is_dir():
                if args.dry_run:
                    print(f"Would generate: {folder.name}")
                else:
                    output = Path(f"/tmp/designers/{folder.name}.md")
                    try:
                        generate_page("designers", folder.name, output)
                    except Exception as e:
                        print(f"  Error: {e}")

    elif args.all_developers:
        developers_dir = RESEARCH_DIR / "developers"
        if not developers_dir.exists():
            print("No developers research folder found")
            sys.exit(1)

        for folder in sorted(developers_dir.iterdir()):
            if folder.is_dir():
                if args.dry_run:
                    print(f"Would generate: {folder.name}")
                else:
                    output = Path(f"/tmp/developers/{folder.name}.md")
                    try:
                        generate_page("developers", folder.name, output)
                    except Exception as e:
                        print(f"  Error: {e}")

    elif args.person:
        parts = args.person.split("/")
        if len(parts) != 2:
            print("Person must be in format: designers/name or developers/name")
            sys.exit(1)

        person_type, person_slug = parts
        output = Path(args.output) if args.output else None

        content = generate_page(person_type, person_slug, output)

        if not output:
            print("\n" + "="*60)
            print(content)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
