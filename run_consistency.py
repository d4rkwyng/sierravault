#!/usr/bin/env python3
"""
SierraVault Consistency Checker - Direct Runner
Reads the source script and executes it programmatically
"""

import sys
import os
from pathlib import Path

# Set up the path. SIERRAVAULT_INTERNAL (see .claude/README.md) takes
# priority; the default matches the internal tree's scripts/sv_paths.py.
REPO_ROOT = Path(__file__).resolve().parent
vault_games = REPO_ROOT / "vault/Games"
_internal_root = os.environ.get("SIERRAVAULT_INTERNAL")
_assets_root = (
    Path(_internal_root) if _internal_root
    else Path.home() / "SierraVault-internal"
)
script_source = _assets_root / "scripts/ACTIVE/consistency_check.py"

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
        "--output", str(REPO_ROOT / "vault_report.json"),
    ]

    # Import and run main from the script
    # __file__ lets the script locate its sibling sv_paths resolver.
    exec(open(script_source).read(), {"__name__": "__main__", "__file__": str(script_source)})

else:
    print(f"ERROR: Script not found at {script_source}")
    print("Set SIERRAVAULT_INTERNAL to the private repo's location (see .claude/README.md).")
    sys.exit(1)
