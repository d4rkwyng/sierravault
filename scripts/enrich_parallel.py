#!/usr/bin/env python3
"""Parallel enrichment - processes multiple files concurrently."""
import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic

SCRIPTS_DIR = Path(__file__).parent
INTERNAL_DIR = SCRIPTS_DIR.parent
RESEARCH_DIR = INTERNAL_DIR / "research"
GAMES_RESEARCH_DIR = RESEARCH_DIR / "games"
DEFAULT_WORKERS = 10
DEFAULT_MODEL = "claude-haiku-4-20250514"  # Haiku is faster

EXTRACTION_PROMPT = """Extract facts from this game research content. Return JSON only.

Game: {game_title}
Source: {url}

Content:
{content}

Return this JSON structure (use null/[] for missing data):
{{
  "extracted_facts": {{
    "release_dates": [{{"platform": "X", "date": "Y", "region": "Z"}}],
    "developers": [],
    "publishers": [],
    "designers": [],
    "composers": [],
    "voice_cast": [{{"actor": "X", "role": "Y"}}],
    "engine": null,
    "platforms": [],
    "ratings": {{"publication": "X", "score": "Y", "reviewer": "Z", "date": "W"}},
    "sales_data": null,
    "awards": [],
    "technical_specs": {{}},
    "version_info": [],
    "trivia": [],
    "easter_eggs": [],
    "development_notes": null
  }},
  "key_quotes": [{{"quote": "X", "attribution": "Y", "context": "Z"}}],
  "source_significance": "What makes this source valuable"
}}"""

def enrich_file(file_path: Path, game_title: str, client, model: str) -> dict:
    """Enrich a single file."""
    try:
        with open(file_path) as f:
            data = json.load(f)
    except:
        return {"status": "error", "file": file_path.name}
    
    # Skip if already enriched or no content
    if data.get("extracted_facts"):
        return {"status": "skipped", "file": file_path.name}
    
    content = data.get("full_text", "")
    if not content or len(content) < 100:
        return {"status": "skipped", "file": file_path.name}
    
    url = data.get("url", "unknown")
    
    # Truncate long content
    if len(content) > 15000:
        content = content[:15000] + "\n[TRUNCATED]"
    
    try:
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT.format(
                    game_title=game_title,
                    url=url,
                    content=content
                )
            }]
        )
        
        result_text = response.content[0].text
        
        # Parse JSON from response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        enrichment = json.loads(result_text.strip())
        
        # Update file
        data["extracted_facts"] = enrichment.get("extracted_facts", {})
        data["key_quotes"] = enrichment.get("key_quotes", [])
        data["source_significance"] = enrichment.get("source_significance", "")
        data["enriched_at"] = datetime.now().isoformat()
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        facts = len([v for v in data["extracted_facts"].values() if v])
        return {"status": "success", "file": file_path.name, "facts": facts}
        
    except Exception as e:
        return {"status": "error", "file": file_path.name, "error": str(e)[:50]}

def enrich_game(folder_name: str, workers: int, model: str):
    """Enrich a game folder with parallel workers."""
    folder_path = GAMES_RESEARCH_DIR / folder_name
    if not folder_path.exists():
        print(f"Folder not found: {folder_name}")
        return None
    
    # Get game title
    manifest_path = folder_path / "_manifest.json"
    if manifest_path.exists():
        game_title = json.loads(manifest_path.read_text()).get('game_title', folder_name)
    else:
        game_title = folder_name.replace('-', ' ').title()
    
    # Get files needing enrichment
    files = [f for f in folder_path.glob("*.json") 
             if f.name not in ("_manifest.json", "_urls.json")]
    
    print(f"Enriching: {game_title} ({len(files)} files, {workers} workers, {model})")
    
    client = anthropic.Anthropic()
    results = {"success": 0, "skipped": 0, "error": 0}
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(enrich_file, f, game_title, client, model): f 
            for f in files
        }
        
        for future in as_completed(futures):
            result = future.result()
            results[result["status"]] = results.get(result["status"], 0) + 1
    
    print(f"  Done: {results['success']} enriched, {results['skipped']} skipped, {results['error']} errors")
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", nargs="?")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()
    
    print(f"Config: {args.model}, {args.workers} workers")
    
    if args.folder:
        enrich_game(args.folder, args.workers, args.model)
    else:
        print("Usage: python enrich_parallel.py <folder-name> [--workers N] [--model X]")

if __name__ == "__main__":
    main()
