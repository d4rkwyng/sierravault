#!/usr/bin/env python3
"""
Quality Daemon - Continuous quality patrol for SierraVault

Loops through all game pages and runs local quality checks.
Tracks progress and logs results for reporting.

Usage:
    python3 quality_daemon.py                    # Run continuously
    python3 quality_daemon.py --hours 2          # Run for 2 hours
    python3 quality_daemon.py --batch 10         # Check 10 pages then stop
    python3 quality_daemon.py --rate 60          # 60 seconds between pages
    python3 quality_daemon.py --resume           # Resume from last state
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Import the local quality checker
from local_quality_check import run_quality_check, check_ollama_available


# Paths
VAULT_PATH = Path(__file__).parent.parent / "vault" / "Games"
RESULTS_FILE = Path(__file__).parent / "quality_results.jsonl"
STATE_FILE = Path(__file__).parent / "quality_state.json"


def get_all_game_pages() -> List[Path]:
    """Get all game page markdown files."""
    if not VAULT_PATH.exists():
        print(f"Error: Vault path not found: {VAULT_PATH}", file=sys.stderr)
        return []
    
    pages = []
    for md_file in VAULT_PATH.rglob("*.md"):
        # Skip index files and READMEs
        if md_file.name.lower() in ['readme.md', 'index.md', '_index.md']:
            continue
        pages.append(md_file)
    
    return sorted(pages)


def load_state() -> Dict:
    """Load daemon state from file."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    
    return {
        "last_checked": None,
        "checked_files": [],
        "total_checked": 0,
        "pass_count": 0,
        "review_count": 0,
        "fail_count": 0,
        "started_at": None,
        "last_run_at": None
    }


def save_state(state: Dict):
    """Save daemon state to file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, default=str)


def append_result(result: Dict):
    """Append a result to the JSONL log file."""
    result['timestamp'] = datetime.now().isoformat()
    
    with open(RESULTS_FILE, 'a') as f:
        f.write(json.dumps(result) + '\n')


def get_next_page(state: Dict, all_pages: List[Path]) -> Optional[Path]:
    """Get the next page to check based on state."""
    checked = set(state.get('checked_files', []))
    
    for page in all_pages:
        if str(page) not in checked:
            return page
    
    # All pages checked - start over
    state['checked_files'] = []
    save_state(state)
    
    if all_pages:
        return all_pages[0]
    return None


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def run_daemon(
    hours: Optional[float] = None,
    batch: Optional[int] = None,
    rate_limit: float = 30.0,
    resume: bool = True,
    verbose: bool = False,
    no_llm: bool = False,
    escalate: bool = False
):
    """Run the quality daemon.
    
    Args:
        escalate: Use Mac Studio 70B for deep analysis on flagged pages
    """
    
    # Calculate end time if hours specified
    end_time = None
    if hours:
        end_time = datetime.now() + timedelta(hours=hours)
        print(f"Running for {hours} hours (until {end_time.strftime('%H:%M:%S')})")
    
    # Load or initialize state
    if resume:
        state = load_state()
        print(f"Resuming from state: {state.get('total_checked', 0)} pages checked previously")
    else:
        state = {
            "last_checked": None,
            "checked_files": [],
            "total_checked": 0,
            "pass_count": 0,
            "review_count": 0,
            "fail_count": 0,
            "started_at": datetime.now().isoformat(),
            "last_run_at": None
        }
    
    state['last_run_at'] = datetime.now().isoformat()
    
    # Get all game pages
    all_pages = get_all_game_pages()
    total_pages = len(all_pages)
    print(f"Found {total_pages} game pages in {VAULT_PATH}")
    
    if not all_pages:
        print("No pages found to check!")
        return
    
    # Check Ollama availability
    ollama_ok = check_ollama_available()
    if not ollama_ok:
        print("Warning: Ollama not available - running without LLM analysis")
        no_llm = True
    
    # Check Mac Studio availability if escalating
    if escalate:
        from local_quality_check import check_studio_available
        if check_studio_available():
            print("✓ Mac Studio available for deep analysis (llama3.3:70b)")
        else:
            print("Warning: Mac Studio not reachable - disabling escalation")
            escalate = False
    
    checked_this_run = 0
    start_time = time.time()
    
    print(f"\nStarting quality patrol (rate limit: {rate_limit}s between pages)")
    print("-" * 60)
    
    try:
        while True:
            # Check termination conditions
            if batch and checked_this_run >= batch:
                print(f"\n✓ Batch complete: checked {checked_this_run} pages")
                break
            
            if end_time and datetime.now() >= end_time:
                print(f"\n✓ Time limit reached: ran for {hours} hours")
                break
            
            # Get next page
            page = get_next_page(state, all_pages)
            if not page:
                print("\n✓ All pages checked!")
                break
            
            # Run quality check
            try:
                result = run_quality_check(
                    str(page),
                    use_llm=not no_llm,
                    verbose=verbose,
                    escalate=escalate
                )
                
                # Update counters
                score = result.get('score', 0)
                if score >= 90:
                    status = "PASS"
                    state['pass_count'] = state.get('pass_count', 0) + 1
                elif score >= 70:
                    status = "REVIEW"
                    state['review_count'] = state.get('review_count', 0) + 1
                else:
                    status = "FAIL"
                    state['fail_count'] = state.get('fail_count', 0) + 1
                
                # Log result
                append_result(result)
                
                # Update state
                state['last_checked'] = str(page)
                state['checked_files'].append(str(page))
                state['total_checked'] = state.get('total_checked', 0) + 1
                checked_this_run += 1
                
                # Progress output
                progress = len(state['checked_files']) / total_pages * 100
                elapsed = time.time() - start_time
                pages_per_hour = checked_this_run / (elapsed / 3600) if elapsed > 0 else 0
                
                flagship_tag = " [F]" if result.get('flagship') else ""
                deep_tag = " 🔬" if result.get('deep_analysis', {}).get('analysis') else ""
                escalate_tag = " ⚠️" if result.get('needs_escalation') and not deep_tag else ""
                
                print(f"{status} [{score:3d}]{flagship_tag}{deep_tag}{escalate_tag} {page.stem[:50]}")
                
                if verbose and result.get('issues'):
                    for issue in result['issues'][:3]:
                        print(f"     └─ {issue}")
                
                # Save state periodically
                if checked_this_run % 5 == 0:
                    save_state(state)
                
            except Exception as e:
                print(f"ERROR checking {page.name}: {e}", file=sys.stderr)
                # Still mark as checked to avoid infinite loop
                state['checked_files'].append(str(page))
            
            # Rate limit
            if rate_limit > 0:
                time.sleep(rate_limit)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        # Final state save
        save_state(state)
        
        # Summary
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("QUALITY PATROL SUMMARY")
        print("=" * 60)
        print(f"Pages checked this run: {checked_this_run}")
        print(f"Total pages checked:    {state.get('total_checked', 0)}")
        print(f"Time elapsed:           {format_duration(elapsed)}")
        if elapsed > 0:
            print(f"Rate:                   {checked_this_run / (elapsed / 60):.1f} pages/min")
        print()
        print(f"PASS (90%+):   {state.get('pass_count', 0)}")
        print(f"REVIEW (70-89): {state.get('review_count', 0)}")
        print(f"FAIL (<70):    {state.get('fail_count', 0)}")
        print()
        print(f"Results saved to: {RESULTS_FILE}")
        print(f"State saved to:   {STATE_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Quality daemon for SierraVault")
    parser.add_argument("--hours", type=float, help="Run for N hours then stop")
    parser.add_argument("--batch", type=int, help="Check N pages then stop")
    parser.add_argument("--rate", type=float, default=30.0, help="Seconds between pages (default: 30)")
    parser.add_argument("--resume", action="store_true", default=True, help="Resume from last state (default)")
    parser.add_argument("--fresh", action="store_true", help="Start fresh, ignore previous state")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM analysis")
    parser.add_argument("--escalate", action="store_true", 
                        help="Use Mac Studio 70B for deep analysis on flagged pages")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    run_daemon(
        hours=args.hours,
        batch=args.batch,
        rate_limit=args.rate,
        resume=not args.fresh,
        verbose=args.verbose,
        no_llm=args.no_llm,
        escalate=args.escalate
    )


if __name__ == "__main__":
    main()
