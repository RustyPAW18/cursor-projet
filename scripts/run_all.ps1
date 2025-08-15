Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root   = Split-Path -Parent $PSScriptRoot
$py     = (Join-Path $root ".venv\Scripts\python.exe")
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "=== Orchestrateur: lint → types → tests → scan ==="

# Kill-switch: SKIP_LINT_TYPES=1 pour sauter ruff + mypy (utile en CI si besoin)
$skip = ($env:SKIP_LINT_TYPES -eq "1")

# Lint (ruff) si dispo et non skippé
if (-not $skip) {
  $hasRuff = $false
  try { & $py -m ruff --version | Out-Null; if ($LASTEXITCODE -eq 0) { $hasRuff = $true } } catch {}
  if ($hasRuff) {
    $ruffCfg = Join-Path $root ".ruff.toml"
    if (Test-Path $ruffCfg) {
      & $py -m ruff check $root --config $ruffCfg
    } else {
      & $py -m ruff check $root
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
} else {
  Write-Host "[INFO] SKIP_LINT_TYPES=1 → ruff/mypy sautés."
}

# Type-check (mypy) si dispo et non skippé
if (-not $skip) {
  $hasMypy = $false
  try { & $py -m mypy --version | Out-Null; if ($LASTEXITCODE -eq 0) { $hasMypy = $true } } catch {}
  if ($hasMypy) {
    $cfg = Join-Path $root "mypy.ini"
    $target = Join-Path $root "src"
    & $py -m mypy $target --config-file $cfg
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
}

# Tests
& $py -m pytest -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Rapport hindex
& $py (Join-Path $PSScriptRoot "hindex_scan_src.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "[OK] Orchestrateur terminé."
