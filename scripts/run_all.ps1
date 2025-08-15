Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root   = Split-Path -Parent $PSScriptRoot
$py     = (Join-Path $root ".venv\Scripts\python.exe")
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "=== Orchestrateur: lint → types → tests → scan ==="

# Lint (ruff) si dispo
$hasRuff = $false
try { & $py -m ruff --version | Out-Null; if ($LASTEXITCODE -eq 0) { $hasRuff = $true } } catch {}
if ($hasRuff) {
  & $py -m ruff check $root
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

# Type-check (mypy) si dispo
$hasMypy = $false
try { & $py -m mypy --version | Out-Null; if ($LASTEXITCODE -eq 0) { $hasMypy = $true } } catch {}
if ($hasMypy) {
  $cfg = Join-Path $root "mypy.ini"
  $target = Join-Path $root "src"
  & $py -m mypy $target --config-file $cfg
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

# Tests
& $py -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Rapport hindex
& $py (Join-Path $PSScriptRoot "hindex_scan_src.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[OK] Orchestrateur terminé."
