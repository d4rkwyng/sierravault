#!/usr/bin/env python3
"""
Quality Report Generator - Summary reports from quality patrol results

Reads quality_results.jsonl and generates actionable reports.

Usage:
    python3 quality_report.py                    # Full summary
    python3 quality_report.py --top 20           # Show top 20 issues
    python3 quality_report.py --failing          # Only show failing pages
    python3 quality_report.py --flagships        # Only show flagship pages
    python3 quality_report.py --json             # Output as JSON
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


RESULTS_FILE = Path(__file__).parent / "quality_results.jsonl"
STATE_FILE = Path(__file__).parent / "quality_state.json"


def load_results() -> List[Dict]:
    """Load all results from JSONL file."""
    results = []
    
    if not RESULTS_FILE.exists():
        return results
    
    with open(RESULTS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return results


def load_state() -> Dict:
    """Load daemon state."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {}


def deduplicate_results(results: List[Dict]) -> List[Dict]:
    """Keep only the most recent result for each file."""
    latest = {}
    
    for result in results:
        filepath = result.get('file', '')
        timestamp = result.get('timestamp', '')
        
        if filepath not in latest or timestamp > latest[filepath].get('timestamp', ''):
            latest[filepath] = result
    
    return list(latest.values())


def categorize_results(results: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize results by status."""
    categories = {
        'pass': [],
        'review': [],
        'fail': []
    }
    
    for result in results:
        score = result.get('score', 0)
        if score >= 90:
            categories['pass'].append(result)
        elif score >= 70:
            categories['review'].append(result)
        else:
            categories['fail'].append(result)
    
    return categories


def analyze_common_issues(results: List[Dict]) -> List[tuple]:
    """Analyze most common issues across all results."""
    issue_counter = Counter()
    
    for result in results:
        for issue in result.get('issues', []):
            # Normalize issue text
            issue_normalized = issue.lower()
            
            # Categorize issues
            if 'citation' in issue_normalized or 'reference' in issue_normalized:
                issue_counter['Low citation count'] += 1
            elif 'duplicate' in issue_normalized:
                issue_counter['Duplicate reference URLs'] += 1
            elif 'missing section' in issue_normalized:
                issue_counter['Missing required sections'] += 1
            elif 'frontmatter' in issue_normalized:
                issue_counter['Incomplete frontmatter'] += 1
            elif 'promotional' in issue_normalized:
                issue_counter['Promotional language'] += 1
            elif 'wiki link' in issue_normalized:
                issue_counter['Wiki link format issues'] += 1
            elif 'series' in issue_normalized or 'continuity' in issue_normalized:
                issue_counter['Missing series continuity'] += 1
            else:
                issue_counter[issue[:50]] += 1
    
    return issue_counter.most_common(20)


def analyze_by_series(results: List[Dict]) -> Dict[str, Dict]:
    """Analyze results by series folder."""
    series_stats = defaultdict(lambda: {'count': 0, 'total_score': 0, 'failing': []})
    
    for result in results:
        filepath = result.get('file', '')
        score = result.get('score', 0)
        
        # Extract series from path
        path = Path(filepath)
        parts = path.parts
        
        try:
            games_idx = list(parts).index('Games')
            if games_idx < len(parts) - 2:
                series = parts[games_idx + 1]
            else:
                series = 'Standalone'
        except ValueError:
            series = 'Unknown'
        
        series_stats[series]['count'] += 1
        series_stats[series]['total_score'] += score
        
        if score < 90:
            series_stats[series]['failing'].append({
                'file': path.name,
                'score': score
            })
    
    # Calculate averages
    for series in series_stats:
        count = series_stats[series]['count']
        series_stats[series]['average'] = round(
            series_stats[series]['total_score'] / count, 1
        ) if count > 0 else 0
    
    return dict(series_stats)


def print_text_report(
    results: List[Dict],
    top_n: int = 10,
    show_failing: bool = False,
    show_flagships: bool = False
):
    """Print human-readable text report."""
    
    if not results:
        print("No results found. Run quality_daemon.py first.")
        return
    
    # Deduplicate
    results = deduplicate_results(results)
    
    # Filter if requested
    if show_flagships:
        results = [r for r in results if r.get('flagship')]
    
    if show_failing:
        results = [r for r in results if r.get('score', 0) < 70]
    
    # Categorize
    categories = categorize_results(results)
    
    # State info
    state = load_state()
    
    print("=" * 70)
    print("SIERRAVAULT QUALITY REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if state.get('last_run_at'):
        print(f"Last patrol: {state.get('last_run_at')}")
    print()
    
    # Summary stats
    total = len(results)
    pass_count = len(categories['pass'])
    review_count = len(categories['review'])
    fail_count = len(categories['fail'])
    
    print("SUMMARY")
    print("-" * 40)
    print(f"Total pages checked:  {total}")
    print(f"  ✓ PASS (90%+):      {pass_count} ({pass_count/total*100:.1f}%)" if total else "")
    print(f"  ⚠ REVIEW (70-89%):  {review_count} ({review_count/total*100:.1f}%)" if total else "")
    print(f"  ✗ FAIL (<70%):      {fail_count} ({fail_count/total*100:.1f}%)" if total else "")
    
    if total:
        avg_score = sum(r.get('score', 0) for r in results) / total
        print(f"\nAverage score: {avg_score:.1f}%")
    
    # Flagship stats
    flagships = [r for r in results if r.get('flagship')]
    if flagships:
        flagship_avg = sum(r.get('score', 0) for r in flagships) / len(flagships)
        flagship_passing = sum(1 for r in flagships if r.get('score', 0) >= 90)
        print(f"\nFlagship pages: {len(flagships)} (avg: {flagship_avg:.1f}%, passing: {flagship_passing})")
    
    print()
    
    # Most common issues
    print("MOST COMMON ISSUES")
    print("-" * 40)
    common_issues = analyze_common_issues(results)
    for issue, count in common_issues[:top_n]:
        pct = count / total * 100 if total else 0
        print(f"  {count:4d} ({pct:5.1f}%) - {issue}")
    
    print()
    
    # Pages needing attention (sorted by score, lowest first)
    attention_pages = [r for r in results if r.get('score', 0) < 90]
    attention_pages.sort(key=lambda x: (x.get('score', 0), x.get('file', '')))
    
    print(f"PAGES NEEDING ATTENTION ({len(attention_pages)} total)")
    print("-" * 40)
    
    for result in attention_pages[:top_n]:
        score = result.get('score', 0)
        filepath = Path(result.get('file', ''))
        flagship = " [F]" if result.get('flagship') else ""
        escalate = " ⚠️" if result.get('needs_escalation') else ""
        
        status = "FAIL" if score < 70 else "REVIEW"
        print(f"  {status} [{score:3d}]{flagship}{escalate} {filepath.stem[:50]}")
        
        # Show top issues for this page
        issues = result.get('issues', [])
        for issue in issues[:2]:
            print(f"       └─ {issue[:60]}")
    
    if len(attention_pages) > top_n:
        print(f"\n  ... and {len(attention_pages) - top_n} more pages")
    
    print()
    
    # Series breakdown
    print("QUALITY BY SERIES")
    print("-" * 40)
    series_stats = analyze_by_series(results)
    
    # Sort by average score
    sorted_series = sorted(
        series_stats.items(),
        key=lambda x: x[1].get('average', 0)
    )
    
    for series, stats in sorted_series[:15]:
        avg = stats.get('average', 0)
        count = stats.get('count', 0)
        failing_count = len(stats.get('failing', []))
        
        status = "✓" if failing_count == 0 else "⚠" if avg >= 70 else "✗"
        print(f"  {status} {series[:25]:<25} avg:{avg:5.1f}%  ({count} pages, {failing_count} need attention)")
    
    print()
    print("=" * 70)


def generate_json_report(results: List[Dict]) -> Dict:
    """Generate JSON report structure."""
    results = deduplicate_results(results)
    categories = categorize_results(results)
    state = load_state()
    
    total = len(results)
    
    return {
        "generated_at": datetime.now().isoformat(),
        "last_patrol": state.get('last_run_at'),
        "summary": {
            "total_pages": total,
            "pass_count": len(categories['pass']),
            "review_count": len(categories['review']),
            "fail_count": len(categories['fail']),
            "average_score": round(sum(r.get('score', 0) for r in results) / total, 1) if total else 0
        },
        "common_issues": [
            {"issue": issue, "count": count}
            for issue, count in analyze_common_issues(results)
        ],
        "pages_needing_attention": [
            {
                "file": r.get('file'),
                "score": r.get('score'),
                "flagship": r.get('flagship', False),
                "needs_escalation": r.get('needs_escalation', False),
                "issues": r.get('issues', [])
            }
            for r in sorted(results, key=lambda x: x.get('score', 0))
            if r.get('score', 0) < 90
        ],
        "series_breakdown": analyze_by_series(results)
    }


def main():
    parser = argparse.ArgumentParser(description="Generate quality report from patrol results")
    parser.add_argument("--top", type=int, default=10, help="Number of top items to show")
    parser.add_argument("--failing", action="store_true", help="Show only failing pages")
    parser.add_argument("--flagships", action="store_true", help="Show only flagship pages")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--clear", action="store_true", help="Clear results and start fresh")
    
    args = parser.parse_args()
    
    if args.clear:
        if RESULTS_FILE.exists():
            RESULTS_FILE.unlink()
            print(f"Cleared {RESULTS_FILE}")
        if STATE_FILE.exists():
            STATE_FILE.unlink()
            print(f"Cleared {STATE_FILE}")
        return
    
    results = load_results()
    
    if args.json:
        report = generate_json_report(results)
        print(json.dumps(report, indent=2))
    else:
        print_text_report(
            results,
            top_n=args.top,
            show_failing=args.failing,
            show_flagships=args.flagships
        )


if __name__ == "__main__":
    main()
