#!/usr/bin/env python3
"""
Local Quality Checker - Ollama-powered page validation

Uses local LLM models for fast quality checks:
- Mac Mini (localhost): llama3.2:3b for fast screening
- Mac Studio (remote): llama3.3:70b for deep analysis on escalation

Hybrid approach:
1. Fast screening on Mac Mini's small models
2. Escalate to Mac Studio's 70B models for pages needing deeper review

Output: JSON with score, individual checks, issues, and escalation flag.

Usage:
    python3 local_quality_check.py "vault/Games/Some Game/page.md"
    python3 local_quality_check.py --flagship "vault/Games/Kings Quest/1990 - Kings Quest V.md"
    python3 local_quality_check.py --escalate "vault/Games/page.md"  # Use Mac Studio
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Optional


# Mac Studio Ollama server (via Tailscale)
MAC_STUDIO_HOST = os.environ.get("OLLAMA_STUDIO_HOST", "http://100.90.195.80:11434")
MAC_STUDIO_MODEL = "llama3.3:70b"  # Best general model on Studio

# Promotional language patterns to detect
PROMOTIONAL_WORDS = [
    'amazing', 'incredible', 'must-play', 'must play', 'masterpiece',
    'groundbreaking', 'revolutionary', 'stunning', 'breathtaking',
    'unforgettable', 'unmissable', 'essential', 'definitive',
    'best ever', 'greatest', 'perfect', 'flawless', 'brilliant',
    'phenomenal', 'extraordinary', 'unparalleled', 'unmatched',
]

# Required sections for standard game pages
REQUIRED_SECTIONS = ['Overview', 'Reception', 'Legacy', 'References']

# Required frontmatter fields
REQUIRED_FRONTMATTER = ['title', 'release_year', 'developer', 'publisher', 'platforms']

# Flagship series that need higher standards
FLAGSHIP_SERIES = [
    "king's quest", "kings quest", "space quest", "quest for glory",
    "leisure suit larry", "police quest", "gabriel knight", "phantasmagoria"
]

# Well-known Sierra designers that should have wiki links
NOTABLE_DESIGNERS = [
    'roberta williams', 'ken williams', 'al lowe', 'scott murphy', 'mark crowe',
    'corey cole', 'lori cole', 'jane jensen', 'josh mandel', 'jim walls',
    'lorelei shannon', 'bill davis', 'andy hoyos', 'mark seibert', 'ken allen',
    'christy marx', 'jeff tunnell', 'damon slye', 'david wessman'
]


def run_ollama(prompt: str, model: str = "llama3.2:3b", timeout: int = 60) -> Optional[str]:
    """Run a prompt through local Ollama (Mac Mini) and return the response."""
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        return None


def run_ollama_studio(prompt: str, model: str = None, timeout: int = 300) -> Optional[str]:
    """Run a prompt through Mac Studio's Ollama (70B models) via HTTP API.
    
    Uses subprocess curl for reliable Tailscale connectivity.
    """
    model = model or MAC_STUDIO_MODEL
    
    try:
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 2000,
                "temperature": 0.3
            }
        })
        
        result = subprocess.run(
            ['curl', '-s', '--max-time', str(timeout), '-X', 'POST',
             '-H', 'Content-Type: application/json',
             '-d', payload, f"{MAC_STUDIO_HOST}/api/generate"],
            capture_output=True,
            text=True,
            timeout=timeout + 10
        )
        
        if result.returncode != 0:
            return None
        
        response_data = json.loads(result.stdout)
        return response_data.get('response', '').strip()
        
    except subprocess.TimeoutExpired:
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None


def check_ollama_available() -> bool:
    """Check if local Ollama (Mac Mini) is running and available."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False


def check_studio_available() -> bool:
    """Check if Mac Studio Ollama is reachable."""
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '5', f"{MAC_STUDIO_HOST}/api/tags"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return len(data.get('models', [])) > 0
        return False
    except:
        return False


def is_flagship(content: str, filepath: str) -> bool:
    """Detect if this is a flagship series game requiring higher standards."""
    filepath_lower = str(filepath).lower()
    content_lower = content[:1000].lower()
    
    for series in FLAGSHIP_SERIES:
        if series in filepath_lower or series in content_lower:
            return True
    return False


def check_citations(content: str, flagship: bool = False) -> Dict:
    """Check citation count and quality."""
    # Count reference definitions
    ref_definitions = re.findall(r'^\[\^ref-(\d+)\]:', content, re.MULTILINE)
    ref_count = len(ref_definitions)
    
    # Count inline citations
    inline_refs = re.findall(r'\[\^ref-(\d+)\]', content)
    unique_inline = set(inline_refs)
    
    # Thresholds
    min_target = 20 if flagship else 15
    
    result = {
        "pass": ref_count >= min_target,
        "count": ref_count,
        "inline_count": len(inline_refs),
        "unique_refs": len(unique_inline),
        "target": min_target
    }
    
    return result


def check_duplicates(content: str) -> Dict:
    """Check for duplicate reference URLs."""
    # Extract URLs from references section
    ref_section = content.split('## References')[-1] if '## References' in content else ''
    ref_urls = re.findall(r'\]\((https?://[^\s\)]+)\)', ref_section)
    
    # Normalize URLs
    def normalize_url(url: str) -> str:
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = url.rstrip('/')
        url = url.split('#')[0]
        return url.lower()
    
    normalized = [normalize_url(u) for u in ref_urls]
    url_counts = Counter(normalized)
    duplicates = [(url, count) for url, count in url_counts.items() if count > 1]
    
    result = {
        "pass": len(duplicates) == 0,
        "count": len(duplicates),
        "duplicates": duplicates[:5]  # Top 5
    }
    
    return result


def check_sections(content: str) -> Dict:
    """Check for required sections."""
    missing = []
    for section in REQUIRED_SECTIONS:
        if f'## {section}' not in content:
            missing.append(section)
    
    result = {
        "pass": len(missing) == 0,
        "missing": missing
    }
    
    return result


def check_frontmatter(content: str) -> Dict:
    """Check frontmatter completeness."""
    if not content.startswith('---'):
        return {"pass": False, "missing": REQUIRED_FRONTMATTER, "error": "No YAML frontmatter"}
    
    yaml_end = content.find('---', 3)
    if yaml_end < 0:
        return {"pass": False, "missing": REQUIRED_FRONTMATTER, "error": "Malformed YAML"}
    
    yaml_content = content[3:yaml_end]
    
    missing = []
    found = {}
    for field in REQUIRED_FRONTMATTER:
        if f'{field}:' in yaml_content:
            # Extract value
            match = re.search(rf'{field}:\s*["\']?([^"\'\n]+)', yaml_content)
            if match:
                found[field] = match.group(1).strip()
        else:
            missing.append(field)
    
    result = {
        "pass": len(missing) == 0,
        "missing": missing,
        "found": found
    }
    
    return result


def check_promotional_language(content: str, use_llm: bool = False) -> Dict:
    """Check for promotional/biased language."""
    found_words = []
    content_lower = content.lower()
    
    for word in PROMOTIONAL_WORDS:
        if word in content_lower:
            # Count occurrences
            count = content_lower.count(word)
            found_words.append({"word": word, "count": count})
    
    # More sophisticated check using LLM if requested
    llm_analysis = None
    if use_llm and found_words:
        prompt = f"""Analyze this text for promotional or biased language. 
List any phrases that seem overly promotional rather than encyclopedic.
Only list problematic phrases, nothing else. If none found, say "NONE".

TEXT:
{content[:3000]}
"""
        llm_response = run_ollama(prompt, model="qwen2.5-coder:7b", timeout=45)
        if llm_response and llm_response.strip().upper() != "NONE":
            llm_analysis = llm_response
    
    result = {
        "pass": len(found_words) == 0,
        "found_words": found_words[:10],
        "llm_analysis": llm_analysis
    }
    
    return result


def check_wiki_links(content: str) -> Dict:
    """Check wiki link format validation."""
    wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
    
    issues = []
    
    for link in wiki_links:
        # Check for paths (.md extension or / in the link target)
        link_target = link.split('|')[0]  # Get the target, not the alias
        
        if '.md' in link_target:
            issues.append({"link": link, "issue": "Contains .md extension"})
        elif '/' in link_target and not link_target.startswith('http'):
            issues.append({"link": link, "issue": "Contains path separator"})
    
    # Check for backslash-pipe outside of tables
    backslash_issues = []
    for line in content.split('\n'):
        if not line.strip().startswith('|'):  # Not a table row
            matches = re.findall(r'\[\[[^\]]*\\\|[^\]]*\]\]', line)
            for m in matches:
                backslash_issues.append({"link": m, "issue": "Backslash-pipe outside table"})
    
    issues.extend(backslash_issues)
    
    result = {
        "pass": len(issues) == 0,
        "issues": issues[:10],
        "total_links": len(wiki_links)
    }
    
    return result


def check_series_crossrefs(content: str, filepath: str) -> Dict:
    """Check series cross-references if part of a series."""
    path = Path(filepath)
    
    # Detect if in a series folder
    parts = path.parts
    try:
        games_idx = parts.index('Games')
        if games_idx < len(parts) - 2:
            series_folder = parts[games_idx + 1]
        else:
            return {"pass": True, "in_series": False, "note": "Not in series folder"}
    except ValueError:
        return {"pass": True, "in_series": False, "note": "Not in Games folder"}
    
    # Non-series folders
    non_series = {'standalone', 'fan games', 'cancelled', 'dynamix', 'coktel'}
    if series_folder.lower() in non_series:
        return {"pass": True, "in_series": False, "note": "In non-series category folder"}
    
    # Check for Series Continuity section
    has_continuity = '## Series Continuity' in content or '### Series Continuity' in content
    
    # Check for cross-references to other games in series
    wiki_links = re.findall(r'\[\[([^\]|]+)', content)
    series_keywords = series_folder.lower().replace("'", "").replace("'", "").split()
    
    series_refs = 0
    for link in wiki_links:
        link_lower = link.lower()
        if any(kw in link_lower for kw in series_keywords if len(kw) > 2):
            series_refs += 1
    
    result = {
        "pass": has_continuity and series_refs >= 1,
        "in_series": True,
        "series_name": series_folder,
        "has_continuity_section": has_continuity,
        "series_refs_count": series_refs
    }
    
    return result


def check_year_mismatch(content: str, filepath: str) -> Dict:
    """Check if year in filename matches year in frontmatter."""
    path = Path(filepath)
    filename = path.name
    
    # Extract year from filename (e.g., "1990 - King's Quest V.md")
    filename_match = re.match(r'^(\d{4})\s*-', filename)
    filename_year = filename_match.group(1) if filename_match else None
    
    # Extract year from frontmatter
    frontmatter_year = None
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end > 0:
            yaml_content = content[3:yaml_end]
            year_match = re.search(r'release_year:\s*["\']?(\d{4})', yaml_content)
            if year_match:
                frontmatter_year = year_match.group(1)
    
    if filename_year is None:
        return {"pass": True, "details": "No year in filename"}
    
    if frontmatter_year is None:
        return {"pass": False, "details": f"Filename has year {filename_year} but no release_year in frontmatter"}
    
    if filename_year != frontmatter_year:
        return {
            "pass": False,
            "details": f"Year mismatch: filename has {filename_year}, frontmatter has {frontmatter_year}"
        }
    
    return {"pass": True, "details": f"Years match: {filename_year}"}


def check_orphaned_references(content: str) -> Dict:
    """Find citations without definitions and definitions without citations."""
    # Find all inline citations [^ref-N]
    inline_refs = set(re.findall(r'\[\^ref-(\d+)\](?!:)', content))
    
    # Find all reference definitions [^ref-N]:
    definitions = set(re.findall(r'^\[\^ref-(\d+)\]:', content, re.MULTILINE))
    
    # Citations without definitions
    undefined = inline_refs - definitions
    
    # Definitions never cited
    uncited = definitions - inline_refs
    
    issues = []
    if undefined:
        issues.append(f"Undefined citations: {', '.join(sorted(undefined, key=int))}")
    if uncited:
        issues.append(f"Uncited definitions: {', '.join(sorted(uncited, key=int))}")
    
    return {
        "pass": len(undefined) == 0 and len(uncited) == 0,
        "undefined_count": len(undefined),
        "uncited_count": len(uncited),
        "undefined": list(sorted(undefined, key=int))[:10],
        "uncited": list(sorted(uncited, key=int))[:10],
        "details": "; ".join(issues) if issues else "All references valid"
    }


def check_purchase_links(content: str) -> Dict:
    """Check if page has GOG or Steam purchase links. Warning level only."""
    # Look for Purchase or Downloads section
    has_purchase_section = bool(re.search(r'##\s*(Purchase|Downloads|Availability|Where to Buy)', content, re.IGNORECASE))
    
    # Check for GOG links
    gog_links = re.findall(r'https?://(?:www\.)?gog\.com/[^\s\)]+', content)
    
    # Check for Steam links
    steam_links = re.findall(r'https?://store\.steampowered\.com/[^\s\)]+', content)
    
    has_gog = len(gog_links) > 0
    has_steam = len(steam_links) > 0
    
    # This is a warning-level check (not critical)
    result = {
        "pass": has_gog or has_steam,  # Pass if any purchase link exists
        "warning": not (has_gog or has_steam),  # Flag as warning if missing
        "has_purchase_section": has_purchase_section,
        "has_gog": has_gog,
        "has_steam": has_steam,
        "gog_count": len(gog_links),
        "steam_count": len(steam_links),
        "details": "GOG/Steam links present" if (has_gog or has_steam) else "No GOG or Steam purchase links found"
    }
    
    return result


def check_word_count(content: str) -> Dict:
    """Check word count thresholds (<500 too short, >5000 review for bloat)."""
    # Strip frontmatter
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end > 0:
            content = content[yaml_end + 3:]
    
    # Strip references section (don't count bibliography)
    if '## References' in content:
        content = content.split('## References')[0]
    
    # Count words (simple split)
    words = re.findall(r'\b\w+\b', content)
    word_count = len(words)
    
    if word_count < 500:
        return {
            "pass": False,
            "word_count": word_count,
            "issue": "too_short",
            "details": f"Content too short: {word_count} words (minimum 500)"
        }
    elif word_count > 5000:
        return {
            "pass": True,  # Not a failure, just a review flag
            "warning": True,
            "word_count": word_count,
            "issue": "review_bloat",
            "details": f"Content may be bloated: {word_count} words (review for trimming)"
        }
    else:
        return {
            "pass": True,
            "word_count": word_count,
            "details": f"Word count OK: {word_count}"
        }


def check_timestamp_consistency(content: str) -> Dict:
    """Check that frontmatter last_updated matches footer 'Last updated:' line."""
    # Extract frontmatter last_updated
    frontmatter_date = None
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end > 0:
            yaml_content = content[3:yaml_end]
            date_match = re.search(r"last_updated:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", yaml_content)
            if date_match:
                frontmatter_date = date_match.group(1)
    
    # Extract footer "Last updated: Month Day, Year" or similar formats
    footer_match = re.search(r'Last updated:\s*(\w+\s+\d{1,2},?\s+\d{4})', content)
    footer_date = None
    if footer_match:
        # Parse the footer date
        date_str = footer_match.group(1)
        # Convert "February 4, 2026" to "2026-02-04"
        try:
            from datetime import datetime
            # Handle both "February 4, 2026" and "February 4 2026"
            date_str_clean = date_str.replace(',', '')
            parsed = datetime.strptime(date_str_clean, '%B %d %Y')
            footer_date = parsed.strftime('%Y-%m-%d')
        except ValueError:
            footer_date = date_str  # Keep as-is if parsing fails
    
    issues = []
    if frontmatter_date is None:
        issues.append("Missing last_updated in frontmatter")
    if footer_date is None:
        # Not all pages have footer dates, so this is minor
        pass
    
    if frontmatter_date and footer_date and frontmatter_date != footer_date:
        issues.append(f"Date mismatch: frontmatter={frontmatter_date}, footer={footer_date}")
    
    return {
        "pass": len(issues) == 0,
        "frontmatter_date": frontmatter_date,
        "footer_date": footer_date,
        "details": "; ".join(issues) if issues else "Timestamps consistent"
    }


def check_review_scores(content: str) -> Dict:
    """Check if Reception section has actual numeric review scores."""
    # Find Reception section
    reception_match = re.search(r'##\s*Reception\s*\n(.*?)(?=\n##\s|\Z)', content, re.DOTALL)
    
    if not reception_match:
        return {"pass": True, "details": "No Reception section"}
    
    reception_text = reception_match.group(1)
    
    # Look for score patterns: "85%", "8/10", "8.5/10", "4/5", "91% score", etc.
    score_patterns = [
        r'\d{1,3}%',           # 85%, 91%
        r'\d+\.?\d*/\d+',      # 8/10, 8.5/10, 4/5
        r'\d+\.?\d*\s*out of\s*\d+',  # 8 out of 10
        r'score[d]?\s+\d+',    # scored 85
        r'\d+\.?\d*\s*stars?', # 4 stars, 4.5 star
    ]
    
    found_scores = []
    for pattern in score_patterns:
        matches = re.findall(pattern, reception_text, re.IGNORECASE)
        found_scores.extend(matches)
    
    has_scores = len(found_scores) > 0
    
    # Also check for "Aggregate Scores" section
    has_aggregate = 'Aggregate Scores' in reception_text or 'aggregate' in reception_text.lower()
    
    return {
        "pass": has_scores,
        "has_aggregate_section": has_aggregate,
        "scores_found": len(found_scores),
        "sample_scores": found_scores[:5],
        "details": f"Found {len(found_scores)} review scores" if has_scores else "Reception section has no numeric scores"
    }


def check_designer_links(content: str) -> Dict:
    """Check if notable Sierra designers have wiki links in Development section."""
    # Find Development section
    dev_match = re.search(r'##\s*Development\s*\n(.*?)(?=\n##\s|\Z)', content, re.DOTALL)
    
    if not dev_match:
        return {"pass": True, "details": "No Development section"}
    
    dev_text = dev_match.group(1)
    dev_text_lower = dev_text.lower()
    
    # Find wiki-linked names
    wiki_linked = set()
    for match in re.finditer(r'\[\[([^\]|]+)', dev_text):
        wiki_linked.add(match.group(1).lower())
    
    # Check for notable designers mentioned without wiki links
    unlinked_designers = []
    for designer in NOTABLE_DESIGNERS:
        # Check if designer name appears in text
        if designer in dev_text_lower:
            # Check if it's wiki-linked
            is_linked = any(designer in linked for linked in wiki_linked)
            if not is_linked:
                # Format nicely
                unlinked_designers.append(designer.title())
    
    return {
        "pass": len(unlinked_designers) == 0,
        "unlinked_count": len(unlinked_designers),
        "unlinked_designers": unlinked_designers[:5],
        "details": f"Unlinked designers: {', '.join(unlinked_designers)}" if unlinked_designers else "All notable designers linked"
    }


def calculate_score(checks: Dict, flagship: bool = False) -> int:
    """Calculate overall quality score from checks.
    
    Scoring weights (total 100):
    - Citations: 25 points
    - Duplicates: 10 points
    - Sections: 15 points
    - Frontmatter: 10 points
    - Promotional language: 8 points
    - Wiki links: 5 points
    - Series cross-refs: 5 points
    - Year mismatch: 5 points
    - Orphaned references: 5 points
    - Purchase links: 2 points (warning only)
    - Word count: 5 points
    - Timestamp consistency: 2 points
    - Review scores: 3 points
    - Designer links: 2 points (warning only)
    """
    score = 100
    
    # Citations (25 points)
    citations = checks.get('citations', {})
    if not citations.get('pass'):
        count = citations.get('count', 0)
        target = citations.get('target', 15)
        shortfall = max(0, target - count)
        score -= min(25, shortfall * 2)
    
    # Duplicates (10 points)
    duplicates = checks.get('duplicates', {})
    if not duplicates.get('pass'):
        dup_count = duplicates.get('count', 0)
        score -= min(10, dup_count * 2)
    
    # Sections (15 points)
    sections = checks.get('sections', {})
    if not sections.get('pass'):
        missing = len(sections.get('missing', []))
        score -= min(15, missing * 4)
    
    # Frontmatter (10 points)
    frontmatter = checks.get('frontmatter', {})
    if not frontmatter.get('pass'):
        missing = len(frontmatter.get('missing', []))
        score -= min(10, missing * 2)
    
    # Promotional language (8 points)
    promotional = checks.get('promotional', {})
    if not promotional.get('pass'):
        found_count = len(promotional.get('found_words', []))
        score -= min(8, found_count * 2)
    
    # Wiki links (5 points)
    wiki = checks.get('wiki_links', {})
    if not wiki.get('pass'):
        issues = len(wiki.get('issues', []))
        score -= min(5, issues)
    
    # Series cross-refs (5 points)
    series = checks.get('series_crossrefs', {})
    if series.get('in_series') and not series.get('pass'):
        score -= 5
    
    # Year mismatch (5 points)
    year = checks.get('year_mismatch', {})
    if not year.get('pass'):
        score -= 5
    
    # Orphaned references (5 points)
    orphaned = checks.get('orphaned_references', {})
    if not orphaned.get('pass'):
        undefined = orphaned.get('undefined_count', 0)
        uncited = orphaned.get('uncited_count', 0)
        score -= min(5, undefined + uncited)
    
    # Purchase links (2 points - warning level)
    purchase = checks.get('purchase_links', {})
    if purchase.get('warning'):
        score -= 2
    
    # Word count (5 points)
    word_count = checks.get('word_count', {})
    if not word_count.get('pass'):
        score -= 5
    
    # Timestamp consistency (2 points)
    timestamp = checks.get('timestamp_consistency', {})
    if not timestamp.get('pass'):
        score -= 2
    
    # Review scores (3 points)
    review = checks.get('review_scores', {})
    if not review.get('pass'):
        score -= 3
    
    # Designer links (2 points - warning level)
    designer = checks.get('designer_links', {})
    if not designer.get('pass'):
        score -= 2
    
    return max(0, score)


def determine_escalation(checks: Dict, score: int) -> bool:
    """Determine if this page needs escalation to Claude for deeper review."""
    # Escalate if score is borderline (70-85)
    if 70 <= score <= 85:
        return True
    
    # Escalate if there are structural issues
    if not checks.get('sections', {}).get('pass'):
        return True
    
    # Escalate if frontmatter is incomplete
    if not checks.get('frontmatter', {}).get('pass'):
        missing = checks.get('frontmatter', {}).get('missing', [])
        if 'title' in missing or 'release_year' in missing:
            return True
    
    # Escalate if promotional language detected with LLM analysis
    promo = checks.get('promotional', {})
    if promo.get('llm_analysis'):
        return True
    
    return False


def generate_issues_list(checks: Dict) -> List[str]:
    """Generate human-readable issues list."""
    issues = []
    warnings = []
    
    # Citations
    citations = checks.get('citations', {})
    if not citations.get('pass'):
        issues.append(f"Low citation count: {citations.get('count')} (target: {citations.get('target')})")
    
    # Duplicates
    duplicates = checks.get('duplicates', {})
    if not duplicates.get('pass'):
        dup_count = duplicates.get('count', 0)
        issues.append(f"{dup_count} duplicate reference URLs found")
    
    # Sections
    sections = checks.get('sections', {})
    if not sections.get('pass'):
        missing = sections.get('missing', [])
        issues.append(f"Missing sections: {', '.join(missing)}")
    
    # Frontmatter
    frontmatter = checks.get('frontmatter', {})
    if not frontmatter.get('pass'):
        missing = frontmatter.get('missing', [])
        if frontmatter.get('error'):
            issues.append(f"Frontmatter error: {frontmatter.get('error')}")
        else:
            issues.append(f"Missing frontmatter fields: {', '.join(missing)}")
    
    # Promotional
    promotional = checks.get('promotional', {})
    if not promotional.get('pass'):
        words = [w['word'] for w in promotional.get('found_words', [])[:5]]
        issues.append(f"Promotional language detected: {', '.join(words)}")
    
    # Wiki links
    wiki = checks.get('wiki_links', {})
    if not wiki.get('pass'):
        issue_count = len(wiki.get('issues', []))
        issues.append(f"{issue_count} wiki link format issues")
    
    # Series
    series = checks.get('series_crossrefs', {})
    if series.get('in_series') and not series.get('pass'):
        if not series.get('has_continuity_section'):
            issues.append(f"Missing Series Continuity section (in {series.get('series_name')} folder)")
        if series.get('series_refs_count', 0) == 0:
            issues.append("No cross-references to other games in series")
    
    # Year mismatch
    year = checks.get('year_mismatch', {})
    if not year.get('pass'):
        issues.append(year.get('details', 'Year mismatch detected'))
    
    # Orphaned references
    orphaned = checks.get('orphaned_references', {})
    if not orphaned.get('pass'):
        issues.append(orphaned.get('details', 'Orphaned references found'))
    
    # Purchase links (warning level)
    purchase = checks.get('purchase_links', {})
    if purchase.get('warning'):
        warnings.append("⚠️ " + purchase.get('details', 'No purchase links'))
    
    # Word count
    word_count = checks.get('word_count', {})
    if not word_count.get('pass'):
        issues.append(word_count.get('details', 'Word count issue'))
    elif word_count.get('warning'):
        warnings.append("⚠️ " + word_count.get('details', 'Word count warning'))
    
    # Timestamp consistency
    timestamp = checks.get('timestamp_consistency', {})
    if not timestamp.get('pass'):
        issues.append(timestamp.get('details', 'Timestamp inconsistency'))
    
    # Review scores
    review = checks.get('review_scores', {})
    if not review.get('pass'):
        issues.append(review.get('details', 'Missing review scores in Reception'))
    
    # Designer links (warning level)
    designer = checks.get('designer_links', {})
    if not designer.get('pass'):
        warnings.append("⚠️ " + designer.get('details', 'Unlinked designers'))
    
    # Append warnings at end
    issues.extend(warnings)
    
    return issues


def run_deep_analysis(content: str, filepath: str, basic_result: Dict) -> Dict:
    """Run deep analysis on Mac Studio's 70B model for escalated pages.
    
    This provides more nuanced analysis than the fast Mini checks:
    - Better promotional language detection (understands context)
    - Accuracy assessment (can reason about claims)
    - Structure quality (not just presence of sections)
    """
    if not check_studio_available():
        return {"available": False, "error": "Mac Studio not reachable"}
    
    # Build a focused prompt for the 70B model
    issues_summary = "\n".join(f"- {i}" for i in basic_result.get('issues', [])[:10])
    
    prompt = f"""Analyze this Sierra games wiki page for quality issues.

Current automated findings:
{issues_summary}

Focus on:
1. Are there any factual claims that seem questionable or unsourced?
2. Is the promotional language contextually appropriate (e.g., quoting a review) or genuinely promotional?
3. Are there structural issues beyond missing sections?
4. Any other quality concerns?

Be brief. List only real issues, not false positives from automated checks.

PAGE CONTENT:
{content[:8000]}

Respond with a JSON object:
{{"issues": ["list of real issues"], "false_positives": ["automated flags that are actually OK"], "score_adjustment": 0}}
"""
    
    response = run_ollama_studio(prompt)
    if not response:
        return {"available": True, "error": "No response from model"}
    
    # Try to parse JSON from response
    try:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return {"available": True, "analysis": json.loads(json_match.group())}
        else:
            return {"available": True, "raw_response": response[:500]}
    except json.JSONDecodeError:
        return {"available": True, "raw_response": response[:500]}


def run_quality_check(filepath: str, flagship: bool = False, use_llm: bool = True, 
                      verbose: bool = False, escalate: bool = False) -> Dict:
    """Run full quality check on a page.
    
    Args:
        filepath: Path to markdown file
        flagship: Apply flagship standards (20+ citations)
        use_llm: Use local LLM for promotional language check
        verbose: Verbose output
        escalate: Use Mac Studio 70B for deep analysis on flagged pages
    """
    path = Path(filepath)
    
    if not path.exists():
        return {
            "file": str(filepath),
            "error": "File not found",
            "score": 0,
            "checks": {},
            "issues": ["File not found"],
            "needs_escalation": True
        }
    
    with open(path) as f:
        content = f.read()
    
    # Auto-detect flagship if not specified
    if not flagship:
        flagship = is_flagship(content, filepath)
    
    # Run all checks (fast, on Mac Mini)
    checks = {
        # Original checks
        "citations": check_citations(content, flagship),
        "duplicates": check_duplicates(content),
        "sections": check_sections(content),
        "frontmatter": check_frontmatter(content),
        "promotional": check_promotional_language(content, use_llm=use_llm),
        "wiki_links": check_wiki_links(content),
        "series_crossrefs": check_series_crossrefs(content, filepath),
        # New Tier 1 checks
        "year_mismatch": check_year_mismatch(content, filepath),
        "orphaned_references": check_orphaned_references(content),
        "purchase_links": check_purchase_links(content),
        "word_count": check_word_count(content),
        "timestamp_consistency": check_timestamp_consistency(content),
        "review_scores": check_review_scores(content),
        "designer_links": check_designer_links(content),
    }
    
    # Calculate score
    score = calculate_score(checks, flagship)
    
    # Generate issues list
    issues = generate_issues_list(checks)
    
    # Determine escalation
    needs_escalation = determine_escalation(checks, score)
    
    result = {
        "file": str(filepath),
        "score": score,
        "flagship": flagship,
        "checks": checks,
        "issues": issues,
        "needs_escalation": needs_escalation
    }
    
    # Run deep analysis on Mac Studio if escalate is enabled and needed
    if escalate and needs_escalation:
        deep = run_deep_analysis(content, filepath, result)
        result["deep_analysis"] = deep
        
        # Adjust score if deep analysis found false positives
        if deep.get("analysis", {}).get("score_adjustment"):
            result["score"] += deep["analysis"]["score_adjustment"]
            result["score"] = max(0, min(100, result["score"]))  # Clamp 0-100
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Local LLM quality checker for SierraVault pages")
    parser.add_argument("file", help="Markdown file to check")
    parser.add_argument("--flagship", action="store_true", help="Apply flagship standards (20+ citations)")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM analysis (faster)")
    parser.add_argument("--escalate", action="store_true", 
                        help="Use Mac Studio 70B for deep analysis on flagged pages")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output only JSON")
    
    args = parser.parse_args()
    
    # Check Ollama availability if using LLM
    if not args.no_llm:
        if not check_ollama_available():
            print("Warning: Ollama not available, skipping LLM analysis", file=sys.stderr)
            args.no_llm = True
    
    # Check Mac Studio availability if escalating
    if args.escalate:
        if not check_studio_available():
            print("Warning: Mac Studio not reachable, escalation disabled", file=sys.stderr)
            args.escalate = False
        else:
            print("Mac Studio available for deep analysis", file=sys.stderr)
    
    result = run_quality_check(
        args.file,
        flagship=args.flagship,
        use_llm=not args.no_llm,
        verbose=args.verbose,
        escalate=args.escalate
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        score = result['score']
        status = "PASS" if score >= 90 else "REVIEW" if score >= 70 else "FAIL"
        flagship_tag = " [FLAGSHIP]" if result.get('flagship') else ""
        
        print(f"{status} {Path(result['file']).stem}{flagship_tag}: {score}/100")
        
        if result.get('issues'):
            print("\nIssues:")
            for issue in result['issues']:
                print(f"  - {issue}")
        
        if result.get('needs_escalation') and not result.get('deep_analysis'):
            print("\n⚠️  Needs escalation for deeper review (use --escalate)")
        
        # Show deep analysis results if available
        if result.get('deep_analysis'):
            deep = result['deep_analysis']
            if deep.get('analysis'):
                analysis = deep['analysis']
                print("\n🔬 Deep Analysis (Mac Studio 70B):")
                if analysis.get('false_positives'):
                    print("  False positives (OK to ignore):")
                    for fp in analysis['false_positives']:
                        print(f"    ✓ {fp}")
                if analysis.get('issues'):
                    print("  Additional issues found:")
                    for issue in analysis['issues']:
                        print(f"    - {issue}")
                if analysis.get('score_adjustment'):
                    print(f"  Score adjusted by {analysis['score_adjustment']:+d}")
            elif deep.get('error'):
                print(f"\n⚠️  Deep analysis error: {deep['error']}")
        
        if args.verbose:
            print("\nDetailed checks:")
            print(json.dumps(result['checks'], indent=2))


if __name__ == "__main__":
    main()
