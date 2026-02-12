#!/usr/bin/env python3
"""
Local Quality Checker - Ollama-powered page validation

Uses local LLM models for fast quality checks:
- llama3.2:3b for fast screening (citations, patterns)
- qwen2.5-coder:7b for deeper analysis (structure, promotional language)

Output: JSON with score, individual checks, issues, and escalation flag.

Usage:
    python3 local_quality_check.py "vault/Games/Some Game/page.md"
    python3 local_quality_check.py --flagship "vault/Games/Kings Quest/1990 - Kings Quest V.md"
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Optional


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


def run_ollama(prompt: str, model: str = "llama3.2:3b", timeout: int = 60) -> Optional[str]:
    """Run a prompt through Ollama and return the response."""
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


def check_ollama_available() -> bool:
    """Check if Ollama is running and available."""
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


def calculate_score(checks: Dict, flagship: bool = False) -> int:
    """Calculate overall quality score from checks."""
    score = 100
    
    # Citations (30 points)
    citations = checks.get('citations', {})
    if not citations.get('pass'):
        count = citations.get('count', 0)
        target = citations.get('target', 15)
        shortfall = max(0, target - count)
        score -= min(30, shortfall * 2)
    
    # Duplicates (15 points)
    duplicates = checks.get('duplicates', {})
    if not duplicates.get('pass'):
        dup_count = duplicates.get('count', 0)
        score -= min(15, dup_count * 3)
    
    # Sections (20 points)
    sections = checks.get('sections', {})
    if not sections.get('pass'):
        missing = len(sections.get('missing', []))
        score -= min(20, missing * 5)
    
    # Frontmatter (15 points)
    frontmatter = checks.get('frontmatter', {})
    if not frontmatter.get('pass'):
        missing = len(frontmatter.get('missing', []))
        score -= min(15, missing * 3)
    
    # Promotional language (10 points)
    promotional = checks.get('promotional', {})
    if not promotional.get('pass'):
        found_count = len(promotional.get('found_words', []))
        score -= min(10, found_count * 2)
    
    # Wiki links (5 points)
    wiki = checks.get('wiki_links', {})
    if not wiki.get('pass'):
        issues = len(wiki.get('issues', []))
        score -= min(5, issues)
    
    # Series cross-refs (5 points)
    series = checks.get('series_crossrefs', {})
    if series.get('in_series') and not series.get('pass'):
        score -= 5
    
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
    
    return issues


def run_quality_check(filepath: str, flagship: bool = False, use_llm: bool = True, verbose: bool = False) -> Dict:
    """Run full quality check on a page."""
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
    
    # Run all checks
    checks = {
        "citations": check_citations(content, flagship),
        "duplicates": check_duplicates(content),
        "sections": check_sections(content),
        "frontmatter": check_frontmatter(content),
        "promotional": check_promotional_language(content, use_llm=use_llm),
        "wiki_links": check_wiki_links(content),
        "series_crossrefs": check_series_crossrefs(content, filepath)
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
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Local LLM quality checker for SierraVault pages")
    parser.add_argument("file", help="Markdown file to check")
    parser.add_argument("--flagship", action="store_true", help="Apply flagship standards (20+ citations)")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM analysis (faster)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output only JSON")
    
    args = parser.parse_args()
    
    # Check Ollama availability if using LLM
    if not args.no_llm:
        if not check_ollama_available():
            print("Warning: Ollama not available, skipping LLM analysis", file=sys.stderr)
            args.no_llm = True
    
    result = run_quality_check(
        args.file,
        flagship=args.flagship,
        use_llm=not args.no_llm,
        verbose=args.verbose
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
        
        if result.get('needs_escalation'):
            print("\n⚠️  Needs escalation to Claude for deeper review")
        
        if args.verbose:
            print("\nDetailed checks:")
            print(json.dumps(result['checks'], indent=2))


if __name__ == "__main__":
    main()
