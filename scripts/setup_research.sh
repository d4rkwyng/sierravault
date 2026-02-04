#!/bin/bash
# Setup script for research_game.py
# Run once to create virtual environment and install dependencies

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Setting up research tools..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install dependencies
echo "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install requests beautifulsoup4

echo ""
echo "Setup complete!"
echo ""
echo "To use the research script:"
echo "  cd $SCRIPT_DIR"
echo "  source .venv/bin/activate"
echo "  python3 research_game.py \"Game Title\""
