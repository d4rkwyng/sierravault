#!/usr/bin/env python3
"""
Centralized metrics tracking for SierraVault scripts.

This module provides simple time-series metrics logging for tracking:
- Script performance over time
- Quality score trends
- API usage and costs
- Processing statistics

Usage:
    from metrics import log_metric, get_metrics, get_summary
    
    # Log a metric
    log_metric("score_page", "average_score", 87.5, {"files": 10})
    
    # Get recent metrics
    recent = get_metrics("score_page", "average_score", days=30)
    
    # Get summary stats
    summary = get_summary("score_page", "average_score", days=7)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# Metrics storage directory
METRICS_DIR = Path(__file__).parent / "metrics"


def _ensure_metrics_dir():
    """Ensure metrics directory exists."""
    METRICS_DIR.mkdir(exist_ok=True)


def log_metric(
    script: str,
    metric: str,
    value: Any,
    metadata: Optional[dict] = None,
    timestamp: Optional[datetime] = None
):
    """
    Log a metric with timestamp.
    
    Args:
        script: Name of the script (e.g., "score_page", "enrich_research")
        metric: Name of the metric (e.g., "average_score", "api_calls")
        value: The metric value (number, string, bool)
        metadata: Optional dict with additional context
        timestamp: Optional timestamp (defaults to now)
    """
    _ensure_metrics_dir()
    
    metrics_file = METRICS_DIR / f"{script}_metrics.jsonl"
    
    entry = {
        "timestamp": (timestamp or datetime.now()).isoformat(),
        "metric": metric,
        "value": value,
        "metadata": metadata or {}
    }
    
    with open(metrics_file, 'a') as f:
        f.write(json.dumps(entry) + '\n')


def get_metrics(
    script: str,
    metric: Optional[str] = None,
    days: int = 30
) -> list:
    """
    Retrieve metrics for analysis.
    
    Args:
        script: Name of the script
        metric: Optional metric name filter
        days: Number of days to look back
    
    Returns:
        List of metric entries
    """
    _ensure_metrics_dir()
    
    metrics_file = METRICS_DIR / f"{script}_metrics.jsonl"
    if not metrics_file.exists():
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    results = []
    
    with open(metrics_file) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry["timestamp"])
                if ts > cutoff:
                    if metric is None or entry["metric"] == metric:
                        results.append(entry)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
    
    return results


def get_summary(script: str, metric: str, days: int = 7) -> dict:
    """
    Get summary statistics for a metric.
    
    Args:
        script: Name of the script
        metric: Metric name
        days: Number of days to analyze
    
    Returns:
        Dict with min, max, avg, count, trend
    """
    entries = get_metrics(script, metric, days)
    
    if not entries:
        return {"count": 0}
    
    values = [e["value"] for e in entries if isinstance(e["value"], (int, float))]
    
    if not values:
        return {"count": len(entries), "non_numeric": True}
    
    # Calculate trend (comparing first half to second half)
    trend = "stable"
    if len(values) >= 4:
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid
        second_half_avg = sum(values[mid:]) / (len(values) - mid)
        diff_pct = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg else 0
        if diff_pct > 5:
            trend = "improving"
        elif diff_pct < -5:
            trend = "declining"
    
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "avg": round(sum(values) / len(values), 2),
        "trend": trend,
        "first": entries[0]["timestamp"][:10],
        "last": entries[-1]["timestamp"][:10],
    }


def list_scripts() -> list:
    """List all scripts that have metrics."""
    _ensure_metrics_dir()
    return [f.stem.replace("_metrics", "") for f in METRICS_DIR.glob("*_metrics.jsonl")]


def list_metrics(script: str) -> list:
    """List all metric names for a script."""
    entries = get_metrics(script, days=365)  # Look back far to find all metrics
    return list(set(e["metric"] for e in entries))


def print_dashboard(days: int = 7):
    """Print a dashboard of recent metrics."""
    scripts = list_scripts()
    
    if not scripts:
        print("No metrics recorded yet.")
        return
    
    print(f"\n{'='*60}")
    print(f"METRICS DASHBOARD (last {days} days)")
    print(f"{'='*60}\n")
    
    for script in sorted(scripts):
        metrics = list_metrics(script)
        if not metrics:
            continue
            
        print(f"📊 {script}")
        for metric in sorted(metrics):
            summary = get_summary(script, metric, days)
            if summary.get("count", 0) == 0:
                continue
            
            if summary.get("non_numeric"):
                print(f"   {metric}: {summary['count']} entries")
            else:
                trend_icon = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(
                    summary.get("trend", "stable"), "➡️"
                )
                print(f"   {metric}: {summary['avg']} (min: {summary['min']}, max: {summary['max']}) {trend_icon}")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View SierraVault metrics")
    parser.add_argument("--days", type=int, default=7, help="Days to look back")
    parser.add_argument("--script", help="Filter to specific script")
    parser.add_argument("--metric", help="Filter to specific metric")
    parser.add_argument("--raw", action="store_true", help="Show raw entries")
    args = parser.parse_args()
    
    if args.script and args.raw:
        entries = get_metrics(args.script, args.metric, args.days)
        for e in entries[-20:]:  # Last 20
            print(json.dumps(e))
    elif args.script and args.metric:
        summary = get_summary(args.script, args.metric, args.days)
        print(json.dumps(summary, indent=2))
    else:
        print_dashboard(args.days)
