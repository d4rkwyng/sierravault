#!/usr/bin/env python3
"""
SierraVault Consistency Checker - Direct Runner
Reads the source script and executes it programmatically
"""

import sys
import os
from pathlib import Path

# Set up the path
vault_games = Path.home() / "Projects/sierravault/vault/Games"
script_source = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Assets/sierravault/scripts/ACTIVE/consistency_check.py"

# First ensure PyYAML is installed
try:
    import yaml
except ImportError:
    print("Installing PyYAML...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "--break-system-packages", "-q"], check=False)
    import yaml

# Import the consistency check script
sys.path.insert(0, str(script_source.parent))

# Read and execute the script with custom arguments
if script_source.exists():
    print(f"Running consistency check on: {vault_games}")
    print("="*72)

    # Execute with sys.argv modified to pass arguments
    old_argv = sys.argv

    # First run: --quiet --output
    print("\nRUN 1: Generating JSON report...")
    sys.argv = [
        str(script_source),
        "--vault", str(vault_games),
        "--quiet",
        "--output", str(Path.home() / "Projects/sierravault/vault_report.json"),
    ]

    # Import and run main from the script
    exec(open(script_source).read(), {"__name__": "__main__"})

else:
    print(f"ERROR: Script not found at {script_source}")
    sys.exit(1)
