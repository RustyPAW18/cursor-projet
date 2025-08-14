Param(
    [string]$VenvName = ".venv"
)

Write-Host "=== Reset & Setup Cursor perso (v1) ==="

# 1) Crée venv si absent
if (-Not (Test-Path $VenvName)) {
    Write-Host "[1/4] Création de l'environnement virtuel..."
    python -m venv $VenvName
} else {
    Write-Host "[1/4] Environnement virtuel déjà présent."
}

# 2) Activer venv
$activate = Join-Path $VenvName "Scripts\Activate.ps1"
if (Test-Path $activate) {
    Write-Host "[2/4] Activation de l'environnement..."
    . $activate
} else {
    Write-Error "Activation introuvable: $activate"
    exit 1
}

# 3) Installer outils de base (lint/format/tests)
Write-Host "[3/4] Installation des paquets..."
python -m pip install --upgrade pip
pip install -U ruff black pytest -r requirements.txt

# 4) Vérification rapide
Write-Host "[4/4] Vérification: lint, format (check), tests"
ruff check src tests
black --check src tests
pytest

Write-Host "OK. Lancez: .\scripts\run_all.ps1"
