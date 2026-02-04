#!/usr/bin/env python3
"""
Hallucination Detection Script

Detects potential hallucinations in wiki pages by:
1. Pattern-based checks (fast, no API)
2. Source cross-reference (checks claims against research JSONs)
3. LLM verification (optional, for flagged pages)

Usage:
    python3 detect_hallucinations.py page.md
    python3 detect_hallucinations.py page.md --llm  # Include LLM verification
    python3 detect_hallucinations.py page.md --verbose
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# Research folder path
RESEARCH_DIR = Path(__file__).parent / "research"


def slugify(title: str) -> str:
    """Convert title to research folder slug."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-')
    return slug


def load_research_sources(game_title: str) -> Dict[str, str]:
    """Load all research JSON files for a game."""
    sources = {}

    # Try different slug variations
    slugs_to_try = [
        slugify(game_title),
        slugify(game_title.replace("'", "")),
        slugify(re.sub(r'^\d{4}\s*-\s*', '', game_title)),  # Remove year prefix
    ]

    for slug in slugs_to_try:
        research_path = RESEARCH_DIR / slug
        if research_path.exists():
            for json_file in research_path.glob("*.json"):
                if json_file.name.startswith("_"):
                    continue
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        if "full_text" in data:
                            sources[json_file.stem] = data["full_text"].lower()
                except (json.JSONDecodeError, KeyError):
                    continue
            break

    return sources


def extract_claims(content: str) -> List[Dict]:
    """Extract verifiable claims from page content."""
    claims = []

    # Remove YAML frontmatter
    if content.startswith('---'):
        yaml_end = content.find('---', 3)
        if yaml_end > 0:
            content = content[yaml_end + 3:]

    # Remove references section for claim extraction
    if '## References' in content:
        content = content.split('## References')[0]

    # Pattern: Specific numbers (scores, dates, sales figures)
    # e.g., "sold 230,365 units" or "received 85/100"
    number_claims = re.findall(
        r'([^.]*?\b\d{1,3}(?:,\d{3})*(?:\.\d+)?(?:/\d+|%| units| copies| million| thousand)[^.]*\.)',
        content
    )
    for claim in number_claims:
        citation = bool(re.search(r'\[\^ref-\d+\]', claim))
        claims.append({
            'type': 'number',
            'text': claim.strip()[:200],
            'cited': citation,
            'severity': 'high' if not citation else 'low'
        })

    # Pattern: Specific dates (month day, year)
    date_claims = re.findall(
        r'([^.]*?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}[^.]*\.)',
        content
    )
    for claim in date_claims:
        citation = bool(re.search(r'\[\^ref-\d+\]', claim))
        claims.append({
            'type': 'date',
            'text': claim.strip()[:200],
            'cited': citation,
            'severity': 'medium' if not citation else 'low'
        })

    # Pattern: Quotes without citations
    quote_claims = re.findall(r'([^.]*?"[^"]{20,}"[^.]*\.)', content)
    for claim in quote_claims:
        citation = bool(re.search(r'\[\^ref-\d+\]', claim))
        if not citation:
            claims.append({
                'type': 'quote',
                'text': claim.strip()[:200],
                'cited': False,
                'severity': 'high'
            })

    return claims


def extract_names(content: str) -> Set[str]:
    """Extract proper names from content."""
    names = set()

    # Pattern: Two capitalized words (likely names)
    name_pattern = re.findall(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b', content)
    for name in name_pattern:
        # Filter out common false positives
        if name not in ['Game Info', 'Story Summary', 'Release Year', 'Last Updated',
                        'Digital Stores', 'Version History', 'Technical Specifications',
                        'Critical Perspective', 'Commercial Impact', 'Sierra Entertainment',
                        'Sierra Online', 'New World', 'Video Poker', 'Board Games']:
            names.add(name)

    return names


def check_names_in_sources(names: Set[str], sources: Dict[str, str]) -> List[str]:
    """Check which names appear in sources."""
    unverified = []
    all_source_text = ' '.join(sources.values())

    for name in names:
        name_lower = name.lower()
        if name_lower not in all_source_text:
            unverified.append(name)

    return unverified


def check_claims_in_sources(claims: List[Dict], sources: Dict[str, str]) -> List[Dict]:
    """Check which claims have support in sources."""
    flagged = []
    all_source_text = ' '.join(sources.values())

    for claim in claims:
        if claim['severity'] == 'low':
            continue

        # Extract key numbers/facts from claim
        numbers = re.findall(r'\b(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\b', claim['text'])

        # Check if any key numbers appear in sources
        found_in_source = False
        for num in numbers:
            if num in all_source_text:
                found_in_source = True
                break

        if not found_in_source and numbers:
            claim['source_verified'] = False
            flagged.append(claim)
        elif not claim['cited']:
            claim['source_verified'] = 'unknown'
            flagged.append(claim)

    return flagged


def pattern_check(content: str, sources: Dict[str, str]) -> Dict:
    """Run fast pattern-based hallucination checks."""
    results = {
        'issues': [],
        'warnings': [],
        'score': 100,
    }

    # Extract and check claims
    claims = extract_claims(content)
    uncited_claims = [c for c in claims if not c['cited'] and c['severity'] != 'low']

    if uncited_claims:
        high_severity = [c for c in uncited_claims if c['severity'] == 'high']
        if high_severity:
            results['issues'].append(f"{len(high_severity)} uncited high-severity claims (quotes, numbers)")
            results['score'] -= len(high_severity) * 5

        medium_severity = [c for c in uncited_claims if c['severity'] == 'medium']
        if medium_severity:
            results['warnings'].append(f"{len(medium_severity)} uncited specific dates")
            results['score'] -= len(medium_severity) * 2

    # Check claims against sources
    if sources:
        flagged_claims = check_claims_in_sources(claims, sources)
        unverified = [c for c in flagged_claims if c.get('source_verified') == False]
        if unverified:
            results['issues'].append(f"{len(unverified)} claims with numbers not found in sources")
            results['score'] -= len(unverified) * 10
    else:
        results['warnings'].append("No research sources found to cross-reference")

    # Check names against sources
    names = extract_names(content)
    if sources and names:
        unverified_names = check_names_in_sources(names, sources)
        if len(unverified_names) > 5:
            results['warnings'].append(f"{len(unverified_names)} names not found in sources")
            results['score'] -= min(10, len(unverified_names))

    # Check for placeholder text that might indicate incomplete verification
    placeholders = ['[citation needed]', '[source?]', 'TBD', '[needs verification]']
    for p in placeholders:
        if p.lower() in content.lower():
            results['issues'].append(f"Contains placeholder: {p}")
            results['score'] -= 15

    results['score'] = max(0, results['score'])
    results['uncited_claims'] = uncited_claims[:5]  # Sample

    return results


def llm_verify(content: str, sources: Dict[str, str], api_key: str = None) -> Dict:
    """Use LLM to verify claims against sources."""
    try:
        import anthropic
    except ImportError:
        return {'error': 'anthropic package not installed'}

    if not api_key:
        api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        return {'error': 'No API key available'}

    # Truncate sources if too long
    source_text = '\n\n---\n\n'.join([
        f"SOURCE {i+1}:\n{text[:3000]}"
        for i, text in enumerate(list(sources.values())[:5])
    ])

    # Truncate content
    page_content = content[:8000]

    prompt = f"""Analyze this wiki page for potential hallucinations or unsupported claims.

WIKI PAGE:
{page_content}

AVAILABLE SOURCES:
{source_text}

Please identify:
1. Claims that are NOT supported by any of the provided sources
2. Specific facts (dates, numbers, names) that cannot be verified
3. Quotes that don't appear in sources
4. Any suspicious or likely fabricated information

Format your response as JSON:
{{
    "hallucination_risk": "low|medium|high",
    "unsupported_claims": ["claim 1", "claim 2"],
    "suspicious_facts": ["fact 1", "fact 2"],
    "verification_notes": "brief summary"
}}
"""

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result_text = response.content[0].text
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {'raw_response': result_text}
    except (json.JSONDecodeError, IndexError):
        return {'raw_response': response.content[0].text if response.content else 'No response'}


def detect_hallucinations(filepath: str, use_llm: bool = False, verbose: bool = False) -> Dict:
    """Main detection function."""
    with open(filepath) as f:
        content = f.read()

    # Get game title from filename
    game_title = Path(filepath).stem

    # Load research sources
    sources = load_research_sources(game_title)

    # Run pattern checks
    pattern_results = pattern_check(content, sources)

    results = {
        'file': filepath,
        'game': game_title,
        'sources_found': len(sources),
        'pattern_score': pattern_results['score'],
        'issues': pattern_results['issues'],
        'warnings': pattern_results['warnings'],
    }

    if verbose:
        results['sample_uncited_claims'] = pattern_results.get('uncited_claims', [])

    # Run LLM verification if requested and issues found
    if use_llm and (pattern_results['issues'] or pattern_results['score'] < 80):
        llm_results = llm_verify(content, sources)
        results['llm_verification'] = llm_results

    return results


def print_results(results: Dict, verbose: bool = False):
    """Print detection results."""
    score = results['pattern_score']

    if score >= 90:
        status = "CLEAN"
    elif score >= 70:
        status = "WARNING"
    else:
        status = "FLAGGED"

    print(f"{status} {results['game']}: {score}/100 ({results['sources_found']} sources)")

    if results['issues'] or verbose:
        for issue in results['issues']:
            print(f"  ❌ {issue}")
        for warning in results['warnings']:
            print(f"  ⚠️  {warning}")

    if 'llm_verification' in results:
        llm = results['llm_verification']
        if 'hallucination_risk' in llm:
            print(f"  🤖 LLM Risk: {llm['hallucination_risk']}")
            if llm.get('unsupported_claims'):
                for claim in llm['unsupported_claims'][:3]:
                    print(f"     - {claim[:100]}")

    if verbose and results.get('sample_uncited_claims'):
        print("  Sample uncited claims:")
        for claim in results['sample_uncited_claims'][:3]:
            print(f"    - [{claim['type']}] {claim['text'][:80]}...")


def main():
    parser = argparse.ArgumentParser(description="Detect potential hallucinations in wiki pages")
    parser.add_argument("files", nargs='+', help="Markdown files to check")
    parser.add_argument("--llm", action="store_true", help="Use LLM verification for flagged pages")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    all_results = []
    for filepath in args.files:
        if Path(filepath).exists():
            results = detect_hallucinations(filepath, use_llm=args.llm, verbose=args.verbose)
            all_results.append(results)
            if not args.json:
                print_results(results, args.verbose)
        else:
            print(f"File not found: {filepath}", file=sys.stderr)

    if args.json:
        print(json.dumps(all_results, indent=2))
    elif len(all_results) > 1:
        avg = sum(r['pattern_score'] for r in all_results) / len(all_results)
        flagged = sum(1 for r in all_results if r['pattern_score'] < 70)
        print(f"\n=== SUMMARY ===")
        print(f"Average: {avg:.1f}/100")
        print(f"Flagged (<70): {flagged}/{len(all_results)}")


if __name__ == "__main__":
    main()
