#!/usr/bin/env python3
"""
Enrich People Research Files - Extract structured facts about designers/developers.

Usage:
  python enrich_people.py designers/roberta-williams           # Single person
  python enrich_people.py --all-designers                       # All designers
  python enrich_people.py --all-developers                      # All developers
  python enrich_people.py designers/roberta-williams --force   # Re-enrich
"""

import json
import os
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("Warning: anthropic not installed. Run: pip install anthropic")

RESEARCH_DIR = Path(__file__).parent / "research"

MAX_RETRIES = 3
BASE_RETRY_DELAY = 2.0


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


DESIGNER_EXTRACTION_PROMPT = """Analyze this research content about video game designer "{person_name}" from {source_type} source.

SOURCE URL: {url}

CONTENT:
{content}

Extract the following in JSON format:

{{
  "extracted_facts": {{
    "full_name": "Complete legal name if mentioned",
    "birth_date": "YYYY-MM-DD or partial date if known",
    "birth_place": "City, State/Country",
    "death_date": "YYYY-MM-DD or null if still living",
    "education": ["Schools, degrees, fields of study"],
    "career_timeline": [
      {{"year": "YYYY", "event": "Started at Sierra", "role": "Designer"}},
      {{"year": "YYYY", "event": "Left Sierra", "role": null}}
    ],
    "companies_worked": ["Company names with roles/years if known"],
    "games_designed": ["Game titles with years if known"],
    "games_contributed": ["Games where they had other roles"],
    "awards": ["Award name - year - organization"],
    "notable_achievements": ["First-evers, industry firsts, etc."],
    "design_philosophy": "Quotes or descriptions of their approach to design",
    "personal_life": "Spouse, children, hobbies if mentioned",
    "influences": ["People or things that influenced their work"],
    "legacy_impact": "How they influenced the industry"
  }},
  "key_quotes": [
    {{
      "quote": "Exact quote from or about the person",
      "attribution": "Who said it or source",
      "context": "What the quote is about",
      "year": "Year if known"
    }}
  ],
  "source_significance": "What makes this source uniquely valuable for a biography"
}}

IMPORTANT:
- Only include facts ACTUALLY present in the content
- Use null for unknown values, don't guess
- Preserve exact quotes with proper attribution
- Note year/date for each career event when available
- Include both first-hand quotes and descriptions about the person

Return ONLY valid JSON, no other text."""


DEVELOPER_EXTRACTION_PROMPT = """Analyze this research content about video game developer/studio "{person_name}" from {source_type} source.

SOURCE URL: {url}

CONTENT:
{content}

Extract the following in JSON format:

{{
  "extracted_facts": {{
    "company_name": "Official company name",
    "founded_date": "YYYY or YYYY-MM-DD",
    "founded_location": "City, State/Country",
    "founders": ["Founder names"],
    "closure_date": "YYYY-MM-DD or null if still active",
    "parent_company": "Parent/owner company name",
    "acquisition_history": [
      {{"year": "YYYY", "event": "Acquired by X", "amount": "$X million"}}
    ],
    "key_people": ["Name - Role - Years"],
    "games_developed": ["Game titles with years"],
    "games_published": ["Game titles if publisher"],
    "notable_technologies": ["Engines, tools, innovations"],
    "employee_count": "Peak or notable employee counts",
    "studios_locations": ["Office locations"],
    "subsidiaries": ["Child companies"],
    "awards": ["Award name - year"],
    "industry_impact": "How they influenced gaming"
  }},
  "key_quotes": [
    {{
      "quote": "Exact quote about the company",
      "attribution": "Source",
      "context": "What the quote is about",
      "year": "Year if known"
    }}
  ],
  "source_significance": "What makes this source uniquely valuable for a company profile"
}}

IMPORTANT:
- Only include facts ACTUALLY present in the content
- Use null for unknown values
- Note acquisition/merger details when available
- Include employee counts, office locations if mentioned

Return ONLY valid JSON, no other text."""


def get_client():
    """Get Anthropic client with API key."""
    load_env()
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Check .env file.")
    return anthropic.Anthropic(api_key=api_key)


def clean_html_content(text: str) -> str:
    """Extract readable text from HTML."""
    import re
    # Remove script/style content
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags but keep content
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode entities
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()[:15000]  # Limit content length


def enrich_file(filepath: Path, person_name: str, person_type: str, force: bool = False) -> dict:
    """Enrich a single research file."""
    with open(filepath) as f:
        data = json.load(f)

    # Skip if already enriched (unless force)
    if not force and data.get("extracted_facts") and data.get("enrichment_date"):
        return {"status": "skipped", "file": filepath.name}

    # Get content to analyze
    content = data.get("full_text", "")
    if not content:
        return {"status": "no_content", "file": filepath.name}

    # Clean HTML if present
    if "<html" in content.lower() or "<!doctype" in content.lower():
        content = clean_html_content(content)

    if len(content) < 200:
        return {"status": "too_short", "file": filepath.name}

    # Select prompt based on person type
    if person_type == "designers":
        prompt_template = DESIGNER_EXTRACTION_PROMPT
    else:
        prompt_template = DEVELOPER_EXTRACTION_PROMPT

    prompt = prompt_template.format(
        person_name=person_name,
        source_type=data.get("source_id", filepath.stem),
        url=data.get("url", "Unknown"),
        content=content
    )

    # Call Claude with retry logic
    client = get_client()
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text.strip()

            # Clean JSON from markdown blocks
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]

            extracted = json.loads(result_text)

            # Update original data
            data["extracted_facts"] = extracted.get("extracted_facts", {})
            data["key_quotes"] = extracted.get("key_quotes", [])
            data["source_significance"] = extracted.get("source_significance", "")
            data["enrichment_date"] = datetime.now().isoformat()

            # Save back
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            return {"status": "enriched", "file": filepath.name}

        except json.JSONDecodeError as e:
            print(f"    JSON error in {filepath.name}: {e}")
            return {"status": "json_error", "file": filepath.name}

        except anthropic.RateLimitError:
            delay = BASE_RETRY_DELAY * (2 ** attempt)
            print(f"    Rate limited, waiting {delay}s...")
            time.sleep(delay)

        except Exception as e:
            print(f"    Error enriching {filepath.name}: {e}")
            return {"status": "error", "file": filepath.name, "error": str(e)}

    return {"status": "failed", "file": filepath.name}


def enrich_person(person_type: str, person_slug: str, force: bool = False, workers: int = 3) -> dict:
    """Enrich all research files for a person."""
    folder = RESEARCH_DIR / person_type / person_slug
    if not folder.exists():
        print(f"  Folder not found: {folder}")
        return {"enriched": 0, "skipped": 0, "errors": 0}

    person_name = person_slug.replace("-", " ").title()
    files = [f for f in folder.glob("*.json") if not f.name.startswith("_")]

    print(f"  Enriching {person_type}/{person_slug}: {len(files)} files")

    results = {"enriched": 0, "skipped": 0, "errors": 0, "no_content": 0}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(enrich_file, f, person_name, person_type, force): f
            for f in files
        }

        for future in as_completed(futures):
            result = future.result()
            status = result.get("status", "error")

            if status == "enriched":
                results["enriched"] += 1
                print(f"    ✓ {result['file']}")
            elif status == "skipped":
                results["skipped"] += 1
            elif status == "no_content" or status == "too_short":
                results["no_content"] += 1
            else:
                results["errors"] += 1
                print(f"    ✗ {result['file']}: {status}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Enrich people research files")
    parser.add_argument("person", nargs="?", help="Person path (e.g., designers/roberta-williams)")
    parser.add_argument("--all-designers", action="store_true", help="Enrich all designers")
    parser.add_argument("--all-developers", action="store_true", help="Enrich all developers")
    parser.add_argument("--force", action="store_true", help="Re-enrich even if already done")
    parser.add_argument("--workers", type=int, default=3, help="Parallel workers")

    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("Error: anthropic package required")
        sys.exit(1)

    totals = {"enriched": 0, "skipped": 0, "errors": 0, "no_content": 0}

    if args.person:
        parts = args.person.split("/")
        if len(parts) != 2:
            print("Person must be in format: designers/name or developers/name")
            sys.exit(1)
        person_type, person_slug = parts
        results = enrich_person(person_type, person_slug, args.force, args.workers)
        totals = results

    elif args.all_designers:
        designers_dir = RESEARCH_DIR / "designers"
        if not designers_dir.exists():
            print("No designers folder found")
            sys.exit(1)

        for folder in sorted(designers_dir.iterdir()):
            if folder.is_dir():
                results = enrich_person("designers", folder.name, args.force, args.workers)
                for k in totals:
                    totals[k] += results.get(k, 0)
                print()

    elif args.all_developers:
        developers_dir = RESEARCH_DIR / "developers"
        if not developers_dir.exists():
            print("No developers folder found")
            sys.exit(1)

        for folder in sorted(developers_dir.iterdir()):
            if folder.is_dir():
                results = enrich_person("developers", folder.name, args.force, args.workers)
                for k in totals:
                    totals[k] += results.get(k, 0)
                print()

    else:
        parser.print_help()
        sys.exit(0)

    print(f"\n{'='*50}")
    print(f"ENRICHMENT COMPLETE")
    print(f"  Enriched: {totals['enriched']}")
    print(f"  Skipped:  {totals['skipped']}")
    print(f"  Errors:   {totals['errors']}")
    print(f"  No content: {totals['no_content']}")


if __name__ == "__main__":
    main()
