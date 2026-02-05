#!/usr/bin/env python3
"""
LLM-based Page Quality Scorer

Uses both Claude and ChatGPT to score and provide feedback on generated wiki pages.
Provides dual-model validation for higher confidence scoring.

Usage:
    python3 score_page_llm.py page.md
    python3 score_page_llm.py page.md --model claude  # Claude only
    python3 score_page_llm.py page.md --model gpt     # ChatGPT only
    python3 score_page_llm.py /tmp/*.md               # Multiple files
    python3 score_page_llm.py page.md --sections      # Show section-by-section scoring
    python3 score_page_llm.py page.md --feedback "Reception section IS present at line 60"
    python3 score_page_llm.py page.md --claude-code    # Use Claude Code CLI (Max subscription)

Environment variables required:
    ANTHROPIC_API_KEY - for Claude
    OPENAI_API_KEY    - for ChatGPT

Optional: If you have Claude Code CLI installed and a Max subscription,
use --claude-code to route Claude scoring through it (no per-token charges).
"""

import argparse
import json
import os
import subprocess
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional
import re
import glob

# Check for API keys and Claude Code CLI
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
CLAUDE_CODE_PATH = shutil.which("claude")

SCORING_PROMPT = """You are a quality assurance reviewer for a Sierra Games wiki archive.
Score the following wiki page on a scale of 0-100 based on these criteria:

## Scoring Criteria (100 points total)

### References (25 points)
- 15+ unique references defined: 10 pts
- References cited inline throughout content: 10 pts
- References are diverse (Wikipedia, MobyGames, GOG, wikis, reviews): 5 pts

### Content Accuracy (25 points)
- Facts are accurate and verifiable against provided research data: 10 pts
- Release dates, developers, publishers correct: 5 pts
- No obvious errors or contradictions: 5 pts
- No invented awards, rankings, or sales figures without source: 5 pts

CRITICAL - HALLUCINATION DETECTION (-10 points each):
If research data is provided, cross-check ALL claims. Flag as HALLUCINATION if:
- Review scores mentioned that don't appear in research data
- Awards or rankings not found in any source (e.g., "Time magazine named it #X")
- Sales figures or "best-selling" claims without research backing
- Made-up location names, character names, or plot details
- Specific dates, quotes, or statistics not in research

For EACH hallucination found, deduct 10 points from accuracy (can go negative).
List each hallucination explicitly in the "issues" array with prefix "HALLUCINATION:"

### Completeness (25 points)
- Has all required sections (Overview, Story, Gameplay, Reception, Legacy, Downloads): 10 pts
  - IMPORTANT: A section counts as present if it has a ## header (e.g., "## Legacy"). Subsections (### headers) under a main section are VALID and should NOT be penalized. For example, "## Legacy" followed by "### Nadir of the Franchise" is a complete Legacy section.
- Each section has substantive content (either directly under the header OR in subsections): 10 pts
- Includes contemporary AND modern reviews in Reception section: 5 pts

### Structure & Formatting (25 points)
- Proper YAML frontmatter: 5 pts
- Wiki links formatted correctly [[Name]]: 5 pts
  - IMPORTANT: Do NOT penalize wiki links to designers, developers, or publishers (e.g., [[Roberta Williams]], [[Sierra On-Line]], [[Dynamix]]) even if those pages don't exist yet - these are planned future pages
- Game Info callout present and complete: 5 pts
  - IMPORTANT: The format `> [!info]-` is VALID Obsidian syntax for a collapsible callout. Do NOT penalize this format. Both `[!info]` and `[!info]-` are correct.
- Purchase/Download links present: 5 pts
- Clean markdown formatting: 5 pts

## Section Validity Check

For each of these required sections, determine if it EXISTS and is VALID:
1. Overview - First section after title, introduces the game
2. Story Summary - Plot/narrative description
3. Gameplay - Mechanics, interface, controls
4. Reception - Reviews, critical response (should have Contemporary Reviews AND Modern Assessment subsections)
5. Development - Behind the scenes, production info
6. Legacy - Impact, sequels, fan games, modern availability
7. Downloads - Purchase links, preservation links

A section is VALID if:
- It has a proper ## header (exact match not required, e.g., "## Story Summary" or "## Story" both valid)
- It contains substantive content (not just a header)
- Content is relevant to the section purpose

NOTE: "Series Continuity" is an OPTIONAL navigational section showing Previous/Next games in a series. It does NOT require heavy citations since it's just linking to other games. Do not penalize for minimal citations in this section.

## Response Format

Respond with a JSON object containing:
{
    "score": <0-100>,
    "breakdown": {
        "references": <0-25>,
        "accuracy": <0-25>,
        "completeness": <0-25>,
        "formatting": <0-25>
    },
    "sections": {
        "overview": {"present": true/false, "valid": true/false, "line": <line number or null>, "notes": "..."},
        "story": {"present": true/false, "valid": true/false, "line": <line number or null>, "notes": "..."},
        "gameplay": {"present": true/false, "valid": true/false, "line": <line number or null>, "notes": "..."},
        "reception": {"present": true/false, "valid": true/false, "line": <line number or null>, "notes": "..."},
        "development": {"present": true/false, "valid": true/false, "line": <line number or null>, "notes": "..."},
        "legacy": {"present": true/false, "valid": true/false, "line": <line number or null>, "notes": "..."},
        "downloads": {"present": true/false, "valid": true/false, "line": <line number or null>, "notes": "..."}
    },
    "issues": ["list of specific problems found"],
    "strengths": ["list of things done well"],
    "suggestions": ["specific improvement suggestions"]
}

Be critical but fair. A page scoring 90+ should be publication-ready.
A page scoring 80-89 needs minor fixes. Below 80 needs significant work.

IMPORTANT: Before claiming a section is missing, carefully scan the ENTIRE document for ## headers.
Common section header variations:
- "## Overview" or "## Introduction"
- "## Story Summary" or "## Story" or "## Plot"
- "## Gameplay" or "## Game Mechanics"
- "## Reception" (should contain "### Contemporary Reviews" and "### Modern Assessment")
- "## Development" or "## Production" or "## Behind the Scenes"
- "## Legacy" or "## Impact"
- "## Downloads" or "## Availability"

---

"""

FEEDBACK_PROMPT = """
## Reviewer Feedback

The human reviewer has provided the following corrections to previous LLM assessments of this page.
Please incorporate this feedback into your evaluation:

{feedback}

---

"""

RESEARCH_DATA_PROMPT = """
## Research Data for Fact Verification

Below is the extracted research data from verified sources. Use this to verify claims in the page.
Any facts in the page that CONTRADICT this research data should be flagged as potential hallucinations.
Any extraordinary claims (awards, rankings, sales figures) NOT found in this research should be flagged.

{research_summary}

---

"""


def load_research_facts(research_path: str) -> Optional[str]:
    """Load extracted_facts from all research JSON files and summarize for validation."""
    research_dir = Path(research_path)
    if not research_dir.exists() or not research_dir.is_dir():
        return None

    facts_summary = []
    json_files = list(research_dir.glob("*.json"))

    # Skip manifest
    json_files = [f for f in json_files if f.name != "_manifest.json"]

    if not json_files:
        return None

    # Collect key facts from each source
    review_scores = []
    release_dates = {}
    developers = set()
    publishers = set()
    platforms = set()
    awards = []
    sales_data = []
    key_quotes = []
    voice_cast = []

    for json_file in json_files:
        try:
            with open(json_file) as f:
                data = json.load(f)

            source_id = data.get('source_id', json_file.stem)
            facts = data.get('extracted_facts', {})

            if not facts:
                continue

            # Collect reviews - handle both dict and list formats
            if 'ratings' in facts:
                ratings_data = facts['ratings']
                if isinstance(ratings_data, dict):
                    for pub, score in ratings_data.items():
                        if score and str(score).strip() not in ['', 'null', 'None']:
                            review_scores.append(f"{pub}: {score} ({source_id})")
                elif isinstance(ratings_data, list):
                    for rating in ratings_data:
                        if isinstance(rating, dict):
                            pub = rating.get('publication', 'Unknown')
                            score = rating.get('score', '')
                            platform = rating.get('platform', '')
                            if score:
                                if platform:
                                    review_scores.append(f"{pub}: {score} ({platform}) ({source_id})")
                                else:
                                    review_scores.append(f"{pub}: {score} ({source_id})")

            if 'reviews' in facts:
                for rev in facts['reviews']:
                    if isinstance(rev, dict):
                        pub = rev.get('publication', 'Unknown')
                        score = rev.get('score', '')
                        if score:
                            review_scores.append(f"{pub}: {score} ({source_id})")

            # Release dates
            if 'release_dates' in facts:
                for platform, date in facts['release_dates'].items():
                    if date:
                        release_dates[platform] = f"{date} ({source_id})"
            if 'release_date' in facts:
                release_dates['Primary'] = f"{facts['release_date']} ({source_id})"

            # Developer/Publisher
            if facts.get('developer'):
                developers.add(str(facts['developer']))
            if facts.get('publisher'):
                publishers.add(str(facts['publisher']))

            # Platforms
            if facts.get('platforms'):
                platforms.update(facts['platforms'] if isinstance(facts['platforms'], list) else [facts['platforms']])

            # Awards
            if facts.get('awards'):
                for award in facts['awards']:
                    awards.append(f"{award} ({source_id})")

            # Sales
            if facts.get('sales'):
                sales_data.append(f"{facts['sales']} ({source_id})")

            # Voice cast
            if facts.get('voice_cast'):
                for actor, role in facts['voice_cast'].items():
                    voice_cast.append(f"{actor} as {role}")

            # Key quotes (limit to avoid overwhelming)
            quotes = data.get('key_quotes', [])
            if isinstance(quotes, list):
                for q in quotes[:2]:
                    if isinstance(q, dict):
                        key_quotes.append(f"\"{q.get('quote', '')}\" - {q.get('attribution', source_id)}")
                    elif isinstance(q, str):
                        key_quotes.append(f"\"{q}\" ({source_id})")

        except Exception as e:
            continue

    # Build summary
    lines = [f"Sources analyzed: {len(json_files)} research files\n"]

    if release_dates:
        lines.append("VERIFIED RELEASE DATES:")
        for platform, date in list(release_dates.items())[:10]:
            lines.append(f"  - {platform}: {date}")
        lines.append("")

    if developers:
        lines.append(f"VERIFIED DEVELOPERS: {', '.join(developers)}")
    if publishers:
        lines.append(f"VERIFIED PUBLISHERS: {', '.join(publishers)}")
    if platforms:
        lines.append(f"VERIFIED PLATFORMS: {', '.join(list(platforms)[:15])}")
    lines.append("")

    if review_scores:
        lines.append("VERIFIED REVIEW SCORES:")
        for score in sorted(set(review_scores))[:20]:
            lines.append(f"  - {score}")
        lines.append("")

    if awards:
        lines.append("VERIFIED AWARDS:")
        for award in awards[:10]:
            lines.append(f"  - {award}")
        lines.append("")

    if sales_data:
        lines.append("VERIFIED SALES DATA:")
        for sale in sales_data[:5]:
            lines.append(f"  - {sale}")
        lines.append("")

    if voice_cast:
        lines.append("VERIFIED VOICE CAST:")
        for vc in sorted(set(voice_cast))[:15]:
            lines.append(f"  - {vc}")
        lines.append("")

    if key_quotes:
        lines.append("KEY QUOTES FROM SOURCES:")
        for q in key_quotes[:10]:
            lines.append(f"  {q}")
        lines.append("")

    return "\n".join(lines)

def add_line_numbers(content: str) -> str:
    """Add line numbers to content for easier reference."""
    lines = content.split('\n')
    numbered = []
    for i, line in enumerate(lines, 1):
        numbered.append(f"{i:4d}| {line}")
    return '\n'.join(numbered)


def score_with_claude(content: str, feedback: Optional[str] = None, research_summary: Optional[str] = None, use_api: bool = False) -> Optional[Dict]:
    """Score using Claude Code CLI (default) or direct Anthropic API.

    By default, routes through Claude Code CLI which uses the Claude Max
    subscription. Pass use_api=True to use direct Anthropic API calls instead.
    """
    prompt = SCORING_PROMPT
    if research_summary:
        prompt += RESEARCH_DATA_PROMPT.format(research_summary=research_summary)
    if feedback:
        prompt += FEEDBACK_PROMPT.format(feedback=feedback)
    prompt += "PAGE TO REVIEW (with line numbers):\n\n" + add_line_numbers(content)

    if not use_api:
        return _score_with_claude_code(prompt)
    else:
        return _score_with_claude_api(prompt)


def _score_with_claude_code(prompt: str) -> Optional[Dict]:
    """Score using Claude Code CLI (uses Max subscription)."""
    if not CLAUDE_CODE_PATH:
        print("Warning: 'claude' CLI not found in PATH, falling back to API", file=sys.stderr)
        return _score_with_claude_api(prompt)

    try:
        # Use claude -p (print mode) with --output-format json for structured output
        # Pipe the prompt via stdin to avoid arg length limits
        result = subprocess.run(
            [CLAUDE_CODE_PATH, "-p", "--output-format", "text", "--max-turns", "1"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"Claude Code CLI error (exit {result.returncode}): {result.stderr[:200]}", file=sys.stderr)
            print("Falling back to API...", file=sys.stderr)
            return _score_with_claude_api(prompt)

        response_text = result.stdout

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())
        else:
            print(f"Claude Code: Could not parse JSON from response", file=sys.stderr)
            print(f"Response preview: {response_text[:300]}...", file=sys.stderr)
            return None

    except subprocess.TimeoutExpired:
        print("Claude Code CLI timed out (120s)", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Claude Code CLI error: {e}", file=sys.stderr)
        return None


def _score_with_claude_api(prompt: str) -> Optional[Dict]:
    """Score using direct Anthropic API (billed per-token)."""
    if not ANTHROPIC_KEY:
        print("Warning: ANTHROPIC_API_KEY not set, skipping Claude scoring", file=sys.stderr)
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())
        else:
            print(f"Claude API: Could not parse JSON from response", file=sys.stderr)
            return None

    except ImportError:
        print("Error: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Claude API error: {e}", file=sys.stderr)
        return None


def score_with_gpt(content: str, model: str = "gpt-4.1", feedback: Optional[str] = None, research_summary: Optional[str] = None) -> Optional[Dict]:
    """Score using OpenAI GPT API."""
    if not OPENAI_KEY:
        print("Warning: OPENAI_API_KEY not set, skipping GPT scoring", file=sys.stderr)
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_KEY)

        prompt = SCORING_PROMPT
        if research_summary:
            prompt += RESEARCH_DATA_PROMPT.format(research_summary=research_summary)
        if feedback:
            prompt += FEEDBACK_PROMPT.format(feedback=feedback)
        prompt += "PAGE TO REVIEW (with line numbers):\n\n" + add_line_numbers(content)

        response = client.chat.completions.create(
            model=model,
            max_completion_tokens=3000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"}
        )

        response_text = response.choices[0].message.content
        return json.loads(response_text)

    except ImportError:
        print("Error: openai package not installed. Run: pip install openai", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ChatGPT API error: {e}", file=sys.stderr)
        return None


def print_section_results(sections: Dict):
    """Print section validity results."""
    print("\n  Section Validity:")
    section_names = {
        'overview': 'Overview',
        'story': 'Story Summary',
        'gameplay': 'Gameplay',
        'reception': 'Reception',
        'development': 'Development',
        'legacy': 'Legacy',
        'downloads': 'Downloads'
    }

    for key, name in section_names.items():
        if key in sections:
            sec = sections[key]
            present = sec.get('present', False)
            valid = sec.get('valid', False)
            line = sec.get('line')
            notes = sec.get('notes', '')

            if present and valid:
                status = "✓"
                color_status = "VALID"
            elif present:
                status = "~"
                color_status = "PRESENT but incomplete"
            else:
                status = "✗"
                color_status = "MISSING"

            line_info = f" (line {line})" if line else ""
            print(f"    {status} {name}: {color_status}{line_info}")
            if notes and not (present and valid):
                print(f"      → {notes}")


def print_results(filename: str, claude_result: Optional[Dict], gpt_result: Optional[Dict],
                  verbose: bool = False, show_sections: bool = False):
    """Print formatted scoring results."""
    name = Path(filename).stem

    print(f"\n{'='*60}")
    print(f"FILE: {name}")
    print('='*60)

    scores = []

    if claude_result:
        scores.append(claude_result['score'])
        status = "PASS" if claude_result['score'] >= 90 else "REVIEW" if claude_result['score'] >= 80 else "FAIL"
        print(f"\n[CLAUDE] Score: {claude_result['score']}/100 - {status}")
        print(f"  Breakdown: refs={claude_result['breakdown']['references']}/25, "
              f"accuracy={claude_result['breakdown']['accuracy']}/25, "
              f"completeness={claude_result['breakdown']['completeness']}/25, "
              f"formatting={claude_result['breakdown']['formatting']}/25")

        if show_sections and claude_result.get('sections'):
            print_section_results(claude_result['sections'])

        if verbose or claude_result['score'] < 90:
            if claude_result.get('issues'):
                print(f"  Issues:")
                for issue in claude_result['issues'][:5]:
                    print(f"    - {issue}")
            if claude_result.get('suggestions'):
                print(f"  Suggestions:")
                for sug in claude_result['suggestions'][:3]:
                    print(f"    - {sug}")

    if gpt_result:
        scores.append(gpt_result['score'])
        status = "PASS" if gpt_result['score'] >= 90 else "REVIEW" if gpt_result['score'] >= 80 else "FAIL"
        print(f"\n[GPT-4.1] Score: {gpt_result['score']}/100 - {status}")
        print(f"  Breakdown: refs={gpt_result['breakdown']['references']}/25, "
              f"accuracy={gpt_result['breakdown']['accuracy']}/25, "
              f"completeness={gpt_result['breakdown']['completeness']}/25, "
              f"formatting={gpt_result['breakdown']['formatting']}/25")

        if show_sections and gpt_result.get('sections'):
            print_section_results(gpt_result['sections'])

        if verbose or gpt_result['score'] < 90:
            if gpt_result.get('issues'):
                print(f"  Issues:")
                for issue in gpt_result['issues'][:5]:
                    print(f"    - {issue}")
            if gpt_result.get('suggestions'):
                print(f"  Suggestions:")
                for sug in gpt_result['suggestions'][:3]:
                    print(f"    - {sug}")

    if len(scores) == 2:
        avg = sum(scores) / 2
        diff = abs(scores[0] - scores[1])
        print(f"\n[COMBINED] Average: {avg:.1f}/100, Difference: {diff} points")
        if diff > 10:
            print("  WARNING: Large score discrepancy between models")

    return scores


def load_feedback(filepath: str) -> Optional[str]:
    """Load stored feedback for a file from .feedback.json."""
    feedback_file = Path(filepath).with_suffix('.feedback.json')
    if feedback_file.exists():
        with open(feedback_file) as f:
            data = json.load(f)
            return data.get('feedback')
    return None


def save_feedback(filepath: str, feedback: str):
    """Save feedback for a file to .feedback.json."""
    feedback_file = Path(filepath).with_suffix('.feedback.json')
    existing = {}
    if feedback_file.exists():
        with open(feedback_file) as f:
            existing = json.load(f)

    # Append or set feedback
    if existing.get('feedback'):
        existing['feedback'] += '\n\n' + feedback
    else:
        existing['feedback'] = feedback

    with open(feedback_file, 'w') as f:
        json.dump(existing, f, indent=2)

    print(f"Feedback saved to {feedback_file}")


def score_page(filepath: str, models: List[str] = ['claude', 'gpt'],
               feedback: Optional[str] = None, research_path: Optional[str] = None,
               claude_use_api: bool = False) -> Dict:
    """Score a single page with specified models."""
    with open(filepath) as f:
        content = f.read()

    # Load any stored feedback
    stored_feedback = load_feedback(filepath)
    combined_feedback = feedback
    if stored_feedback:
        if combined_feedback:
            combined_feedback = stored_feedback + '\n\n' + combined_feedback
        else:
            combined_feedback = stored_feedback

    # Load research data if path provided
    research_summary = None
    if research_path:
        research_summary = load_research_facts(research_path)
        if research_summary:
            print(f"  Loaded research data from {research_path}", file=sys.stderr)

    results = {
        'file': filepath,
        'claude': None,
        'gpt': None,
        'feedback_used': combined_feedback is not None,
        'research_used': research_summary is not None
    }

    if 'claude' in models:
        results['claude'] = score_with_claude(content, combined_feedback, research_summary, use_api=claude_use_api)

    if 'gpt' in models:
        results['gpt'] = score_with_gpt(content, feedback=combined_feedback, research_summary=research_summary)

    return results


def main():
    parser = argparse.ArgumentParser(description="LLM-based wiki page quality scorer")
    parser.add_argument("files", nargs='+', help="Markdown files to score")
    parser.add_argument("--model", choices=['claude', 'gpt', 'both'], default='both',
                        help="Which model(s) to use for scoring")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show detailed feedback even for passing scores")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--sections", "-s", action="store_true",
                        help="Show section-by-section validity check")
    parser.add_argument("--feedback", "-f", type=str,
                        help="Provide feedback to correct LLM misconceptions (e.g., 'Reception section IS present at line 60')")
    parser.add_argument("--save-feedback", action="store_true",
                        help="Save the provided feedback for future scoring runs")
    parser.add_argument("--log", type=str, default=None,
                        help="Log all scoring results and suggestions to a JSON file for review")
    parser.add_argument("--research", "-r", type=str, default=None,
                        help="Path to research folder to validate facts against (enables hallucination detection)")
    parser.add_argument("--claude-code", action="store_true",
                        help="Use Claude Code CLI instead of Anthropic API (uses Max subscription, no per-token cost)")

    args = parser.parse_args()

    models = ['claude', 'gpt'] if args.model == 'both' else [args.model]

    # Check Claude availability
    if 'claude' in models:
        if args.claude_code:
            if not CLAUDE_CODE_PATH:
                print("Error: 'claude' CLI not found (required with --claude-code)", file=sys.stderr)
                print("Install: https://docs.anthropic.com/en/docs/claude-code", file=sys.stderr)
                if args.model == 'claude':
                    sys.exit(1)
                models.remove('claude')
            else:
                print("Using Claude Code CLI (Max subscription)", file=sys.stderr)
        elif not ANTHROPIC_KEY:
            print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
            if args.model == 'claude':
                sys.exit(1)
            models.remove('claude')

    if 'gpt' in models and not OPENAI_KEY:
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        if args.model == 'gpt':
            sys.exit(1)
        models.remove('gpt')

    if not models:
        print("Error: No valid models available (check API keys)", file=sys.stderr)
        sys.exit(1)

    all_results = []
    all_scores = []

    for filepath in args.files:
        if not Path(filepath).exists():
            print(f"File not found: {filepath}", file=sys.stderr)
            continue

        # Save feedback if requested
        if args.feedback and args.save_feedback:
            save_feedback(filepath, args.feedback)

        print(f"\nScoring {filepath}...", file=sys.stderr)
        results = score_page(filepath, models, args.feedback, args.research,
                             claude_use_api=not args.claude_code)
        all_results.append(results)

        if results.get('feedback_used'):
            print("  (Using stored/provided feedback)", file=sys.stderr)
        if results.get('research_used'):
            print("  (Validating against research data - hallucination detection enabled)", file=sys.stderr)

        if not args.json:
            scores = print_results(filepath, results['claude'], results['gpt'],
                                   args.verbose, args.sections)
            all_scores.extend(scores)

    if args.json:
        print(json.dumps(all_results, indent=2))
    elif len(all_scores) > 0:
        print(f"\n{'='*60}")
        print("SUMMARY")
        print('='*60)
        avg = sum(all_scores) / len(all_scores)
        passing = sum(1 for s in all_scores if s >= 90)
        print(f"Total scores: {len(all_scores)}")
        print(f"Average: {avg:.1f}/100")
        print(f"Passing (90+): {passing}/{len(all_scores)} ({passing/len(all_scores)*100:.0f}%)")

    # Log results and suggestions to file if requested
    if args.log:
        from datetime import datetime
        log_entries = []
        for result in all_results:
            entry = {
                'file': Path(result['file']).name,
                'timestamp': datetime.now().isoformat(),
                'scores': {}
            }
            for model in ['claude', 'gpt']:
                if result.get(model):
                    r = result[model]
                    entry['scores'][model] = {
                        'score': r.get('score'),
                        'breakdown': r.get('breakdown'),
                        'issues': r.get('issues', []),
                        'suggestions': r.get('suggestions', []),
                        'strengths': r.get('strengths', [])
                    }
            log_entries.append(entry)

        # Append to or create log file
        log_path = Path(args.log)
        existing_log = []
        if log_path.exists():
            try:
                with open(log_path) as f:
                    existing_log = json.load(f)
            except:
                existing_log = []

        existing_log.extend(log_entries)
        with open(log_path, 'w') as f:
            json.dump(existing_log, f, indent=2)
        print(f"\nResults logged to {args.log}")


if __name__ == "__main__":
    main()
