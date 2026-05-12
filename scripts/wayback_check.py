#!/usr/bin/env python3
"""Batch-check Wayback Machine availability for dead URLs.

Reads docs/dead_urls_worklist.csv, queries archive.org/wayback/available
for each row missing a wayback_snapshot in parallel, writes results back
incrementally so progress is preserved if interrupted.
"""
import csv
import httpx
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "docs" / "dead_urls_worklist.csv"
WAYBACK_API = "https://archive.org/wayback/available"
WORKERS = 8  # parallel requests
SAVE_EVERY = 20  # write CSV every N completions


def check_wayback(url: str) -> str:
    """Return the closest Wayback snapshot URL, or empty string if none."""
    try:
        with httpx.Client(timeout=30) as client:
            r = client.get(WAYBACK_API, params={"url": url}, headers={"User-Agent": "SierraVault-Archivist/1.0"})
            r.raise_for_status()
            data = r.json()
            snap = data.get("archived_snapshots", {}).get("closest", {})
            if snap.get("available") and snap.get("status") == "200":
                return snap.get("url", "")
    except Exception as e:
        print(f"  ! err {url[:60]}: {e}", file=sys.stderr, flush=True)
    return ""


def save(rows: list[dict], fieldnames: list[str]) -> None:
    tmp = CSV_PATH.with_suffix(".csv.tmp")
    with tmp.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    tmp.replace(CSV_PATH)


def main() -> None:
    rows = list(csv.DictReader(CSV_PATH.open()))
    fieldnames = list(rows[0].keys()) if rows else []
    print(f"Loaded {len(rows)} rows", flush=True)

    needs_check = [(i, r) for i, r in enumerate(rows) if not r.get("wayback_snapshot")]
    print(f"  {len(needs_check)} rows missing wayback_snapshot — checking {WORKERS} in parallel", flush=True)

    found = 0
    done = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(check_wayback, r["dead_url"]): (i, r) for i, r in needs_check}
        for fut in as_completed(futs):
            i, row = futs[fut]
            snap = fut.result()
            row["wayback_snapshot"] = snap
            if snap:
                found += 1
            done += 1
            elapsed = time.time() - start
            rate = done / elapsed if elapsed else 0
            eta = (len(needs_check) - done) / rate if rate else 0
            status = "OK" if snap else "--"
            print(f"  [{done:>3}/{len(needs_check)}] {status} eta {eta:>4.0f}s  {row['dead_url'][:70]}", flush=True)
            if done % SAVE_EVERY == 0:
                save(rows, fieldnames)

    save(rows, fieldnames)
    print(f"\nDone — recovered {found}/{len(needs_check)} via Wayback in {time.time()-start:.0f}s", flush=True)
    print(f"  Total snapshots in CSV: {sum(1 for r in rows if r['wayback_snapshot'])}/{len(rows)}")


if __name__ == "__main__":
    main()
