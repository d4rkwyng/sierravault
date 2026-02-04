#!/usr/bin/env python3
"""
Enrich Research Files - Extract structured facts from raw research data.

Takes research JSON files with full_text and populates:
- extracted_facts: Structured data (dates, scores, credits, platforms, etc.)
- key_quotes: Citable passages with attribution
- source_significance: What makes this source uniquely valuable

Usage:
  python enrich_research.py kings-quest-vii           # Enrich one game folder
  python enrich_research.py --all                     # Enrich all research folders
  python enrich_research.py kings-quest-vii --file mobygames.json  # Single file
  python enrich_research.py --all --force             # Re-enrich even if already done
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

SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"

# Rate limiting with exponential backoff
MAX_RETRIES = 3
BASE_RETRY_DELAY = 2.0

EXTRACTION_PROMPT = """Analyze this research content about the video game "{game_title}" from {source_type} source.

SOURCE URL: {url}

CONTENT:
{content}

Extract the following in JSON format:

{{
  "extracted_facts": {{
    "release_dates": [
      {{"platform": "DOS", "date": "November 22, 1994", "region": "US"}}
    ],
    "developers": ["Sierra On-Line"],
    "publishers": ["Sierra On-Line"],
    "designers": ["Roberta Williams", "Lorelei Shannon"],
    "composers": ["Jay Usher"],
    "voice_cast": [
      {{"actor": "Carol Bach y Rita", "role": "Valanice"}}
    ],
    "engine": "SCI2.1",
    "platforms": ["DOS", "Windows", "Macintosh"],
    "ratings": {{
      "publication": "Computer Gaming World",
      "score": "4/5",
      "reviewer": "Charles Ardai",
      "date": "February 1995"
    }},
    "sales_data": "300,000-400,000 US units by November 2000",
    "awards": ["CGW Adventure of the Year nominee 1994"],
    "technical_specs": {{
      "resolution": "640x480 SVGA",
      "colors": "256",
      "media": "CD-ROM"
    }},
    "version_info": [
      {{"version": "1.4", "date": "November 1994", "notes": "Original release"}}
    ],
    "trivia": ["First KQ without King Graham", "Disney-style animation"],
    "bugs_issues": ["Crashes in original release"],
    "cut_content": ["King Graham cameo recorded but cut"],
    "easter_eggs": [],
    "development_notes": "Used Russian and Croatian animation studios"
  }},
  "key_quotes": [
    {{
      "quote": "animation of quality that would make Disney proud",
      "attribution": "Charles Ardai, Computer Gaming World",
      "context": "Review praise for animation quality"
    }}
  ],
  "source_significance": "Primary contemporary review with specific scores and quotes"
}}

IMPORTANT RULES:
1. Only extract facts ACTUALLY PRESENT in the content - never invent data
2. If a field has no data in the source, use null or empty array []
3. Include page numbers, issue numbers, exact dates when available
4. Preserve exact wording for quotes
5. Note if information conflicts with common knowledge
6. For reviews, always capture: publication, score format, reviewer name, date
7. For credits, capture full names and specific roles
8. Flag any exceptional claims that might need verification

Return ONLY valid JSON, no markdown code blocks."""


def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes and export prefix
                    key = key.replace('export ', '').strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value


def get_client():
    """Get Anthropic client."""
    load_env()
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Add to .env file or environment.")
    return anthropic.Anthropic(api_key=api_key)


def needs_enrichment(data: dict, force: bool = False) -> bool:
    """Check if a research file needs enrichment."""
    if force:
        return True

    # Skip if no content to enrich
    if not data.get('full_text') or len(data.get('full_text', '')) < 100:
        return False

    # Skip if already enriched with substantial data
    facts = data.get('extracted_facts', {})
    quotes = data.get('key_quotes', [])

    # Consider enriched if has meaningful extracted_facts
    if isinstance(facts, dict) and len(facts) > 3:
        # Check if facts have actual content
        has_content = any(
            v and (isinstance(v, list) and len(v) > 0 or isinstance(v, dict) and len(v) > 0 or isinstance(v, str) and len(v) > 5)
            for v in facts.values()
        )
        if has_content:
            return False

    return True


def truncate_content(content: str, max_chars: int = 30000) -> str:
    """Truncate content to fit in context window."""
    if len(content) <= max_chars:
        return content
    # Keep first and last portions
    half = max_chars // 2
    return content[:half] + "\n\n[... content truncated ...]\n\n" + content[-half:]


def enrich_file(file_path: Path, game_title: str, client, force: bool = False) -> dict:
    """Enrich a single research file with extracted facts."""
    try:
        with open(file_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {"status": "error", "reason": f"Invalid JSON: {e}"}

    if not needs_enrichment(data, force):
        return {"status": "skipped", "reason": "already enriched or no content"}

    source_type = data.get('source_type', 'unknown')
    url = data.get('url', 'unknown')
    content = data.get('full_text', '')

    if not content or len(content) < 50:
        return {"status": "skipped", "reason": "no content"}

    # Truncate if too long
    content = truncate_content(content)

    prompt = EXTRACTION_PROMPT.format(
        game_title=game_title,
        source_type=source_type,
        url=url,
        content=content
    )

    # Retry logic with exponential backoff
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            break
        except Exception as e:
            error_str = str(e).lower()
            if 'rate' in error_str or '429' in error_str or 'overloaded' in error_str:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                time.sleep(delay)
                if attempt == MAX_RETRIES - 1:
                    return {"status": "error", "reason": f"Rate limited after {MAX_RETRIES} retries"}
            else:
                return {"status": "error", "reason": str(e)}

    try:
        result_text = response.content[0].text.strip()

        # Clean up response - remove markdown code blocks if present
        if result_text.startswith('```'):
            lines = result_text.split('\n')
            # Remove first and last lines if they're code block markers
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            result_text = '\n'.join(lines)

        result = json.loads(result_text)

        # Update the data
        data['extracted_facts'] = result.get('extracted_facts', {})
        data['key_quotes'] = result.get('key_quotes', [])
        data['source_significance'] = result.get('source_significance', '')
        data['enrichment_date'] = datetime.now().isoformat()

        # Save back
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {"status": "success", "facts_count": len(data['extracted_facts']), "quotes_count": len(data['key_quotes'])}

    except json.JSONDecodeError as e:
        return {"status": "error", "reason": f"JSON parse error: {e}"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def enrich_folder(folder_path: Path, force: bool = False, workers: int = 5):
    """Enrich all research files in a folder using parallel processing."""
    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}")
        return

    # Get game title from manifest or folder name
    manifest_path = folder_path / "_manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        game_title = manifest.get('game_title', folder_path.name.replace('-', ' ').title())
    else:
        game_title = folder_path.name.replace('-', ' ').title()

    # Get all JSON files except manifest
    files = [f for f in folder_path.glob("*.json") if f.name != "_manifest.json"]

    # Filter to only files needing enrichment first (to avoid counting skipped in progress)
    files_to_process = []
    for f in files:
        try:
            with open(f) as fp:
                data = json.load(fp)
            if needs_enrichment(data, force):
                files_to_process.append(f)
        except:
            files_to_process.append(f)

    print(f"\n{'='*60}")
    print(f"Enriching: {game_title}")
    print(f"Files: {len(files_to_process)} to process ({len(files)} total)")
    print(f"Workers: {workers}")
    print(f"{'='*60}")

    if not files_to_process:
        print("No files need enrichment.")
        return {"success": 0, "skipped": len(files), "error": 0}

    client = get_client()
    results = {"success": 0, "skipped": 0, "error": 0}
    completed = 0
    lock = __import__('threading').Lock()

    def process_file(file_path):
        nonlocal completed
        result = enrich_file(file_path, game_title, client, force)
        with lock:
            completed += 1
            status = result['status']
            results[status] = results.get(status, 0) + 1
            if status == "success":
                print(f"  [{completed}/{len(files_to_process)}] {file_path.name}: OK ({result['facts_count']} facts)")
            elif status == "error":
                print(f"  [{completed}/{len(files_to_process)}] {file_path.name}: ERROR - {result['reason'][:50]}")
        return result

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_file, f): f for f in files_to_process}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Unexpected error: {e}")

    print(f"\nResults: {results['success']} enriched, {results['skipped']} skipped, {results['error']} errors")
    return results


def enrich_all(force: bool = False, workers: int = 5):
    """Enrich all research folders, including entity folders."""
    folders = []

    # Get game folders
    if GAMES_RESEARCH_DIR.exists():
        folders.extend(sorted([f for f in GAMES_RESEARCH_DIR.iterdir() if f.is_dir()]))

    # Add entity folders (designers, developers, publishers)
    for entity_type in ['designers', 'developers', 'publishers']:
        entity_dir = RESEARCH_DIR / entity_type
        if entity_dir.exists():
            for entity_folder in entity_dir.iterdir():
                if entity_folder.is_dir():
                    folders.append(entity_folder)

    print(f"Found {len(folders)} research folders (games + entities)")
    print(f"Workers per folder: {workers}")

    total_results = {"success": 0, "skipped": 0, "error": 0}

    for folder in folders:
        results = enrich_folder(folder, force, workers)
        if results:
            for k, v in results.items():
                total_results[k] = total_results.get(k, 0) + v

    print(f"\n{'='*60}")
    print(f"TOTAL: {total_results['success']} enriched, {total_results['skipped']} skipped, {total_results['error']} errors")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Enrich research files with extracted facts")
    parser.add_argument("folder", nargs="?", help="Research folder name (e.g., kings-quest-vii)")
    parser.add_argument("--all", action="store_true", help="Enrich all research folders")
    parser.add_argument("--file", help="Enrich single file within folder")
    parser.add_argument("--force", action="store_true", help="Re-enrich even if already done")
    parser.add_argument("--workers", type=int, default=3, help="Parallel workers (default: 3)")

    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("Error: anthropic package required. Run: pip install anthropic")
        sys.exit(1)

    if args.all:
        enrich_all(args.force, args.workers)
    elif args.folder:
        # Check if it's an entity path (designers/x, developers/x) or a game slug
        if '/' in args.folder or args.folder in ['designers', 'developers', 'publishers']:
            folder_path = RESEARCH_DIR / args.folder
        else:
            folder_path = GAMES_RESEARCH_DIR / args.folder
        if args.file:
            file_path = folder_path / args.file
            if not file_path.exists():
                print(f"Error: File not found: {file_path}")
                sys.exit(1)
            client = get_client()
            game_title = args.folder.replace('-', ' ').title()
            result = enrich_file(file_path, game_title, client, args.force)
            print(f"Result: {result}")
        else:
            enrich_folder(folder_path, args.force, args.workers)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
