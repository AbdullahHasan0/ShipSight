# ShipSight Runner for Windows

# Check if .venv exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & .\.venv\Scripts\pip install -e .
    & .\.venv\Scripts\playwright install chromium
}

# Run ShipSight
& .\.venv\Scripts\python -m shipsight.cli $args
