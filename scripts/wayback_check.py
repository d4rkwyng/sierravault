#!/usr/bin/env python3
"""Batch-check Wayback Machine availability for dead URLs.

Reads docs/dead_urls_worklist.csv, queries archive.org/wayback/available
for each row missing a wayback_snapshot, writes results back.
"""
import csv
import httpx
import sys
import time
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "docs" / "dead_urls_worklist.csv"
WAYBACK_API = "https://archive.org/wayback/available"


def check_wayback(client: httpx.Client, url: str) -> str:
    """Return the closest Wayback snapshot URL, or empty string if none."""
    try:
        r = client.get(WAYBACK_API, params={"url": url}, timeout=20)
        r.raise_for_status()
        data = r.json()
        snap = data.get("archived_snapshots", {}).get("closest", {})
        if snap.get("available") and snap.get("status") == "200":
            return snap.get("url", "")
    except Exception as e:
        print(f"  ! error {url[:60]}: {e}", file=sys.stderr)
    return ""


def main() -> None:
    rows = list(csv.DictReader(CSV_PATH.open()))
    print(f"Loaded {len(rows)} rows from {CSV_PATH.name}")

    needs_check = [r for r in rows if not r.get("wayback_snapshot")]
    print(f"  {len(needs_check)} rows missing wayback_snapshot — checking…")

    found = 0
    with httpx.Client(headers={"User-Agent": "SierraVault-Archivist/1.0"}) as client:
        for i, row in enumerate(needs_check, 1):
            url = row["dead_url"]
            snap = check_wayback(client, url)
            row["wayback_snapshot"] = snap
            if snap:
                found += 1
            status = "OK" if snap else "--"
            print(f"  [{i:>3}/{len(needs_check)}] {status} {url[:70]}")
            time.sleep(0.2)  # be nice to the API

    fieldnames = ["host", "class", "dead_url", "wayback_snapshot", "file", "ref_num"]
    with CSV_PATH.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"\nDone — recovered {found}/{len(needs_check)} via Wayback")
    print(f"  Snapshots: {sum(1 for r in rows if r['wayback_snapshot'])}/{len(rows)} total")


if __name__ == "__main__":
    main()
