Write-Host "=== Orchestrateur: lint → format → tests ==="
$ErrorActionPreference = "Stop"

# Activer le venv si présent
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
}

# Rendre le layout src/ visible pour Python
$env:PYTHONPATH = Join-Path $pwd "src"

ruff check src tests
black src tests
pytest
