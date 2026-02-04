#!/usr/bin/env python3
"""
Batch Developer Page Generation Pipeline

Complete workflow for generating quality developer/studio pages:
1. Verify research quality (10+ sources)
2. Run enrichment on research files
3. Generate page from enriched research
4. Score generated page
5. Copy to vault if passing

Usage:
  python batch_developer_pages.py --developer "Dynamix"
  python batch_developer_pages.py --all
  python batch_developer_pages.py --status
"""

import json
import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Paths
INTERNAL_DIR = Path(__file__).parent
RESEARCH_DIR = INTERNAL_DIR / "research" / "developers"
VAULT_DIR = INTERNAL_DIR.parent
DEVELOPERS_DIR = VAULT_DIR / "Developers"
OUTPUT_DIR = Path("/tmp/developers")

sys.path.insert(0, str(INTERNAL_DIR))

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


def load_env():
    """Load environment variables."""
    env_path = INTERNAL_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.replace('export ', '').strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value


load_env()


def slugify(name: str) -> str:
    """Convert name to slug."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return re.sub(r'-+', '-', slug).strip('-')


def get_research_status(slug: str) -> dict:
    """Get research status for a developer."""
    folder = RESEARCH_DIR / slug
    if not folder.exists():
        return {"status": "NO_RESEARCH", "files": 0, "vault_games": 0}

    files = [f for f in folder.glob("*.json") if not f.name.startswith("_")]

    # Check vault games
    vault_games_file = folder / "_vault_games.json"
    vault_games = 0
    if vault_games_file.exists():
        games = json.loads(vault_games_file.read_text())
        vault_games = len(games)

    # Check enrichment status
    enriched_count = 0
    for f in files:
        try:
            data = json.loads(f.read_text())
            if data.get("extracted_facts") and data.get("enrichment_date"):
                enriched_count += 1
        except:
            pass

    status = "PASS" if len(files) >= 10 else "NEEDS_RESEARCH"
    enrichment_status = "ENRICHED" if enriched_count >= len(files) * 0.8 else "NEEDS_ENRICHMENT"

    return {
        "status": status,
        "files": len(files),
        "enriched": enriched_count,
        "enrichment_status": enrichment_status,
        "vault_games": vault_games
    }


def run_enrichment(slug: str, force: bool = False) -> dict:
    """Run enrichment on research files."""
    from enrich_people import enrich_person
    return enrich_person("developers", slug, force=force)


def load_research(slug: str) -> dict:
    """Load all research for a developer."""
    folder = RESEARCH_DIR / slug
    if not folder.exists():
        raise FileNotFoundError(f"No research folder: {folder}")

    research = {
        "company_name": slug.replace("-", " ").title(),
        "sources": [],
        "all_quotes": [],
        "all_facts": {},
        "vault_games": []
    }

    # Load vault games
    vault_file = folder / "_vault_games.json"
    if vault_file.exists():
        research["vault_games"] = json.loads(vault_file.read_text())

    # Load source files
    for f in folder.glob("*.json"):
        if f.name.startswith("_"):
            continue
        try:
            data = json.loads(f.read_text())
            source = {
                "filename": f.name,
                "url": data.get("url", ""),
                "source_type": data.get("source_id", f.stem),
                "full_text": data.get("full_text", "")[:20000],
                "extracted_facts": data.get("extracted_facts", {}),
                "key_quotes": data.get("key_quotes", [])
            }

            # Collect quotes
            for quote in data.get("key_quotes", []):
                if isinstance(quote, dict):
                    quote["source_url"] = source["url"]
                    research["all_quotes"].append(quote)

            # Merge facts
            for key, value in data.get("extracted_facts", {}).items():
                if value and key not in research["all_facts"]:
                    research["all_facts"][key] = {"value": value, "source": source["url"]}

            if source["full_text"] or source["extracted_facts"]:
                research["sources"].append(source)
        except Exception as e:
            print(f"  Warning: Could not load {f.name}: {e}")

    return research


DEVELOPER_PROMPT = """You are creating a comprehensive profile page for **{company_name}**, a video game development studio.

=== VERIFIED SOURCE URLs (CITE ALL OF THESE) ===
{source_urls}

=== EXTRACTED FACTS FROM RESEARCH ===
{facts_json}

=== KEY QUOTES ===
{quotes_json}

=== GAMES IN VAULT (format as wiki links) ===
{games_list}

Write a complete Obsidian markdown page following this EXACT structure:

---
title: "{company_name}"
type: developer
founded: [year if known]
defunct: [year if applicable, else null]
headquarters: "[city, state/country]"
notable_games: ["Game 1", "Game 2", "Game 3"]
parent_company: "[if acquired]"
last_updated: "{today}"
---
# {company_name}

<small style="color: gray">Last updated: {today_formatted}</small>

## Overview
[2-3 paragraphs with comprehensive company history. Include founding, key people, business focus, significance to gaming.]

## History

### Founding and Early Years
[How the company started, founders, initial projects, early focus]

### Sierra Era
[Relationship with Sierra On-Line - acquisition, partnership, or publishing deal. Key projects during this period.]

### Later Years / Closure
[What happened after Sierra - acquisition, closure, spinoffs, or continued operation]

## Notable Games

### [Most Famous Game] (Year)
[2-3 sentences about the game, development, reception, significance.][^ref-X]

### [Second Notable Game] (Year)
[Similar detail with citations][^ref-X]

### [Third Notable Game] (Year)
[At least 3 notable games with detailed subsections]

## Key People
[Founders, notable designers, key employees who shaped the company]

## Legacy
[Impact on gaming industry, influence on other studios, what happened to team members]

## Games

| Year | Game | Genre |
|------|------|-------|
| YYYY | [[Path/To/Game.md\\|Game Title]] | Genre |

## References

[^ref-1]: [Source Name](url) — what information was sourced
[^ref-2]: [Source Name](url) — what information was sourced
... (continue for ALL {source_count} URLs)

CRITICAL RULES:
1. **EVERY source URL must appear in References** - {source_count} references minimum
2. **Use inline citations [^ref-X] throughout prose** - at least 2 per paragraph
3. **Wiki links ONLY for vault games** - use [[Games/Series/YYYY - Title.md\\|Title]]
4. **Escape pipes in tables** - use \\| not | in wiki links within tables
5. **Include quotes** - use direct quotes from research with attribution
6. **Target 1500+ words** - comprehensive depth required
7. **Dates/years throughout** - specific years for all events
8. **Games table with actual genres** - Adventure, Simulation, Strategy, etc.

Return ONLY the markdown content."""


def generate_page(slug: str, research: dict, output_path: Path) -> str:
    """Generate a developer page from research."""
    if not HAS_ANTHROPIC:
        raise ImportError("anthropic package required")

    # Build source URL list
    source_urls = []
    for src in research["sources"][:20]:
        url = src.get("url", "")
        if url and url.startswith("http"):
            source_urls.append(f"- {url}")

    # Build facts summary
    facts_summary = {}
    for key, data in research.get("all_facts", {}).items():
        value = data.get("value")
        if isinstance(value, list) and len(value) > 0:
            facts_summary[key] = value[:10] if len(value) > 10 else value
        elif value:
            facts_summary[key] = value

    # Build quotes list
    quotes_list = []
    for q in research.get("all_quotes", [])[:15]:
        if isinstance(q, dict) and q.get("quote"):
            quotes_list.append({
                "quote": q["quote"][:300],
                "attribution": q.get("attribution", ""),
                "context": q.get("context", "")
            })

    # Build games list with paths
    vault_games = []
    for g in research.get("vault_games", []):
        vault_games.append(f"- [[{g['path']}|{g['title']}]] ({g['year']})")

    # Format prompt
    today = datetime.now()
    prompt = DEVELOPER_PROMPT.format(
        company_name=research["company_name"],
        source_urls="\n".join(source_urls) if source_urls else "No verified URLs",
        source_count=len(source_urls),
        facts_json=json.dumps(facts_summary, indent=2, default=str)[:15000],
        quotes_json=json.dumps(quotes_list, indent=2)[:5000],
        games_list="\n".join(vault_games) if vault_games else "No vault games found",
        today=today.strftime("%Y-%m-%d"),
        today_formatted=today.strftime("%B %d, %Y")
    )

    # Call Claude
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    print(f"  Calling Claude API for {research['company_name']}...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text.strip()

    # Clean markdown code blocks
    if content.startswith("```markdown"):
        content = content[11:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    print(f"  Saved to {output_path}")

    return content


def score_page(filepath: Path) -> dict:
    """Score a generated page."""
    from score_person_page import score_page as _score
    return _score(filepath, "developer")


def process_developer(name: str, skip_enrichment: bool = False,
                     force_enrichment: bool = False, auto_publish: bool = False) -> dict:
    """Complete workflow for one developer."""
    slug = slugify(name)

    print(f"\n{'='*60}")
    print(f"Processing: {name}")
    print('='*60)

    result = {
        "name": name,
        "slug": slug,
        "status": "INCOMPLETE"
    }

    # 1. Check research status
    status = get_research_status(slug)
    print(f"  Research: {status['files']} files, {status['vault_games']} vault games [{status['status']}]")
    result["research_files"] = status["files"]
    result["vault_games"] = status["vault_games"]

    if status["status"] == "NO_RESEARCH":
        print(f"  ERROR: No research folder found. Run research pipeline first.")
        result["status"] = "NO_RESEARCH"
        return result

    if status["files"] < 5:
        print(f"  WARNING: Only {status['files']} research files. Consider more research.")

    # 2. Run enrichment if needed
    if not skip_enrichment:
        if status["enrichment_status"] == "NEEDS_ENRICHMENT" or force_enrichment:
            print(f"  Running enrichment...")
            try:
                enrich_result = run_enrichment(slug, force=force_enrichment)
                print(f"  Enriched: {enrich_result.get('enriched', 0)} files")
            except Exception as e:
                print(f"  Enrichment error: {e}")

    # 3. Load research
    try:
        research = load_research(slug)
        print(f"  Loaded {len(research['sources'])} sources, {len(research['vault_games'])} vault games")
    except Exception as e:
        print(f"  ERROR loading research: {e}")
        result["status"] = "LOAD_ERROR"
        return result

    # 4. Generate page
    output_path = OUTPUT_DIR / f"{slug}.md"
    try:
        content = generate_page(slug, research, output_path)
        result["output_path"] = str(output_path)
    except Exception as e:
        print(f"  ERROR generating page: {e}")
        result["status"] = "GENERATION_ERROR"
        return result

    # 5. Score page
    try:
        score_result = score_page(output_path)
        result["score"] = score_result["percentage"]
        result["passed"] = score_result["passed"]

        print(f"\n  Score: {score_result['percentage']}% [{' PASS' if score_result['passed'] else 'FAIL'}]")
        for cat, data in score_result["scores"].items():
            print(f"    {cat}: {data['score']}/{data['max']}")

        if score_result["issues"]:
            print(f"  Issues:")
            for issue in score_result["issues"]:
                print(f"    - {issue}")

    except Exception as e:
        print(f"  ERROR scoring page: {e}")
        result["score"] = 0
        result["passed"] = False

    # 6. Copy to vault if passing and auto_publish
    if result.get("passed") and auto_publish:
        dest = DEVELOPERS_DIR / f"{name}.md"
        shutil.copy(output_path, dest)
        print(f"  Published to {dest}")
        result["published"] = True
        result["status"] = "PUBLISHED"
    elif result.get("passed"):
        result["status"] = "READY_TO_PUBLISH"
    else:
        result["status"] = "NEEDS_IMPROVEMENT"

    return result


def show_status():
    """Show status of all developers."""
    print("Developer Research Status")
    print("="*70)

    all_developers = [
        "Sierra On-Line", "Dynamix", "Impressions Games", "Coktel Vision",
        "Berkeley Systems", "Papyrus Design Group", "On-Line Systems",
        "Synergistic Software", "Bright Star Technology", "Sierra Entertainment",
        "Knowledge Adventure", "Headgate Studios", "Game Arts",
        "Valve Corporation", "Monolith Productions", "Massive Entertainment",
        "Jeff Tunnell Productions", "Gearbox Software", "Evryware",
        "AGD Interactive", "Infamous Adventures", "Infamous Quests",
        "Phoenix Online Studios",
    ]

    stats = {"ready": 0, "needs_research": 0, "needs_enrichment": 0}

    for name in sorted(all_developers):
        slug = slugify(name)
        status = get_research_status(slug)

        if status["status"] == "NO_RESEARCH":
            marker = "✗"
            state = "No research"
            stats["needs_research"] += 1
        elif status["status"] == "NEEDS_RESEARCH":
            marker = "○"
            state = f"{status['files']} files (need more)"
            stats["needs_research"] += 1
        elif status["enrichment_status"] == "NEEDS_ENRICHMENT":
            marker = "◐"
            state = f"{status['files']} files, {status['enriched']} enriched"
            stats["needs_enrichment"] += 1
        else:
            marker = "✓"
            state = f"{status['files']} files, {status['vault_games']} games"
            stats["ready"] += 1

        print(f"  {marker} {name:25} {state}")

    print(f"\nSummary: {stats['ready']} ready, {stats['needs_enrichment']} need enrichment, {stats['needs_research']} need research")


def main():
    parser = argparse.ArgumentParser(description="Batch developer page generation")
    parser.add_argument("--developer", help="Process single developer")
    parser.add_argument("--all", action="store_true", help="Process all developers")
    parser.add_argument("--status", action="store_true", help="Show research status")
    parser.add_argument("--skip-enrichment", action="store_true", help="Skip enrichment step")
    parser.add_argument("--force-enrichment", action="store_true", help="Force re-enrichment")
    parser.add_argument("--auto-publish", action="store_true", help="Auto-publish passing pages")

    args = parser.parse_args()

    if args.status:
        show_status()
        return

    if not HAS_ANTHROPIC:
        print("ERROR: anthropic package required. Run: pip install anthropic")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.developer:
        process_developer(args.developer, args.skip_enrichment,
                         args.force_enrichment, args.auto_publish)

    elif args.all:
        all_developers = [
            "Sierra On-Line", "Dynamix", "Impressions Games", "Coktel Vision",
            "Berkeley Systems", "Papyrus Design Group", "On-Line Systems",
            "Synergistic Software", "Bright Star Technology", "Sierra Entertainment",
            "Knowledge Adventure", "Headgate Studios", "Game Arts",
            "Valve Corporation", "Monolith Productions", "Massive Entertainment",
            "Jeff Tunnell Productions", "Gearbox Software", "Evryware",
            "AGD Interactive", "Infamous Adventures", "Infamous Quests",
            "Phoenix Online Studios",
        ]

        results = []
        for name in all_developers:
            result = process_developer(name, args.skip_enrichment,
                                       args.force_enrichment, args.auto_publish)
            results.append(result)

        # Summary
        print("\n" + "="*60)
        print("BATCH SUMMARY")
        print("="*60)

        published = [r for r in results if r.get("status") == "PUBLISHED"]
        ready = [r for r in results if r.get("status") == "READY_TO_PUBLISH"]
        needs_work = [r for r in results if r.get("status") == "NEEDS_IMPROVEMENT"]
        errors = [r for r in results if "ERROR" in r.get("status", "")]

        print(f"Published: {len(published)}")
        print(f"Ready to publish: {len(ready)}")
        print(f"Needs improvement: {len(needs_work)}")
        print(f"Errors: {len(errors)}")

        if ready:
            print("\nReady to publish:")
            for r in ready:
                print(f"  - {r['name']}: {r.get('score', 0)}%")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
