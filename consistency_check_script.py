#!/usr/bin/env python3
"""
SierraVault Page Consistency Checker - Quick Test Script
Runs consistency checks and saves output to JSON and text format.
"""

import subprocess
import sys
import json
from pathlib import Path

# First, install PyYAML
print("Installing PyYAML...")
subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "--break-system-packages", "-q"], check=False)

# Copy the script from the assets location
REPO_ROOT = Path(__file__).resolve().parent
assets_script = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault/scripts/ACTIVE/consistency_check.py"
output_script = REPO_ROOT / "consistency_check.py"

if assets_script.exists():
    print(f"Copying script from {assets_script}...")
    output_script.write_text(assets_script.read_text())
else:
    print(f"WARNING: Could not find source script at {assets_script}")
    sys.exit(1)

# Make it executable
output_script.chmod(0o755)

# Run the script with --quiet --output for full JSON results
print("\n" + "="*72)
print("RUNNING CONSISTENCY CHECK - FULL RESULTS (--quiet mode)")
print("="*72 + "\n")

vault_path = REPO_ROOT / "vault/Games"
json_output = REPO_ROOT / "vault_report.json"

result = subprocess.run([
    sys.executable, str(output_script),
    "--vault", str(vault_path),
    "--quiet",
    "--output", str(json_output),
], capture_output=False, text=True)

print("\n" + "="*72)
print("RUNNING CONSISTENCY CHECK - FAILING PAGES WITH DETAILS")
print("="*72 + "\n")

# Run again with --failing for detailed issue breakdown
subprocess.run([
    sys.executable, str(output_script),
    "--vault", str(vault_path),
    "--failing",
], capture_output=False, text=True)

# Read and display JSON summary + first 50 pages
if json_output.exists():
    with open(json_output) as f:
        report = json.load(f)

    print("\n" + "="*72)
    print("JSON REPORT SUMMARY")
    print("="*72)
    summary = report.get("summary", {})
    print(json.dumps(summary, indent=2))

    print("\n" + "="*72)
    print("LOWEST SCORING PAGES (first 50)")
    print("="*72)
    pages = report.get("pages", [])
    for page in pages[:50]:
        print(f"\n{page['score']:.1f}% / {page['threshold']}% - {page['filename']} [{page['series']}]")
        if page['issues']:
            for issue in page['issues'][:3]:  # Show top 3 issues per page
                print(f"  - {issue['message'][:70]}")
