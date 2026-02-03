#!/bin/bash
# ShipSight Runner for Linux/Mac

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    ./.venv/bin/pip install -e .
    ./.venv/bin/playwright install chromium
fi

# Run ShipSight
./.venv/bin/python -m shipsight.cli "$@"
