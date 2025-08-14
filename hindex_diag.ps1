# hindex_diag.ps1
# Diagnostic express pour hindex
# Usage :  .\hindex_diag.ps1

$ErrorActionPreference = "Stop"
$root = "C:\Users\Verca\Cursor"
$src  = Join-Path $root "src"
$out  = Join-Path $root ".hindex"
Write-Host "== hindex DIAG ==" -ForegroundColor Cyan
Write-Host "Root: $root"
Write-Host "Src : $src"
Write-Host "Out : $out"

# 0) Contexte Python & version hindex
python -c "import sys,importlib; print('Python:',sys.version); m=importlib.import_module('hindex'); print('hindex:', getattr(m,'__version__','(no __version__)'))" 2>$null

# 1) Lister les fichiers .py vus par l’indexeur
Write-Host "`n[1] _iter_files() apercu" -ForegroundColor Yellow
python - << 'PY'
from pathlib import Path
from hindex import indexer as i
files = list(i._iter_files(Path(r"C:\Users\Verca\Cursor\src"), ["**/*.py"]))
print("Count:", len(files))
for p in files:
    print("-", p)
PY

# 2) Vérifier extract_symbols() sur 2-3 fichiers
Write-Host "`n[2] extract_symbols() check" -ForegroundColor Yellow
python - << 'PY'
from pathlib import Path
from hindex import parser_py as p
from hindex import indexer as i
files = list(i._iter_files(Path(r"C:\Users\Verca\Cursor\src"), ["**/*.py"]))[:3]
for f in files:
    text = Path(f).read_text(encoding="utf-8", errors="ignore")
    syms = list(p.extract_symbols(text, file_path=str(f)))
    print(f"\nFile: {f}\n  symbols:", len(syms))
    for s in syms[:5]:
        size = (getattr(s, "end_byte", 0) or 0) - (getattr(s, "start_byte", 0) or 0)
        print("   -", getattr(s, "kind", "?"), getattr(s, "name", "?"), "size=", size)
PY

# 3) Purge et ingestion (sans exclude-glob)
Write-Host "`n[3] Purge .hindex et ingestion" -ForegroundColor Yellow
if (Test-Path $out) { Remove-Item -Recurse -Force $out }
mkdir $out | Out-Null

# Option : désactiver provisoirement tout filtre de taille via variable env
$env:HINDEX_DEBUG_NO_SIZE_FILTER = "1"

hindex ingest `
  --project $src `
  --out $out `
  --file-glob "**/*.py" `
  --min-symbol-bytes 0

# 4) Inspection rapide de la base (taille et items count)
Write-Host "`n[4] Vérif contenu index" -ForegroundColor Yellow
# Si l’index est un SQLite (index.sqlite) ou jsonl; on teste plusieurs cas courants
$sqlite = Join-Path $out "index.sqlite"
$jsonl  = Join-Path $out "symbols.jsonl"
if (Test-Path $sqlite) {
    Write-Host "index.sqlite présent. Compte items via Python + sqlite3..."
    python - << 'PY'
import sqlite3, os
p = r"C:\Users\Verca\Cursor\.hindex\index.sqlite"
con = sqlite3.connect(p)
cur = con.cursor()
for tbl in ("items","symbols","docs","fts_index"):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(tbl, cur.fetchone()[0])
    except Exception as e:
        pass
con.close()
PY
} elseif (Test-Path $jsonl) {
    Write-Host "symbols.jsonl présent. Compte lignes..."
    $count = (Get-Content $jsonl -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
    Write-Host "items.Count =" $count
} else {
    Write-Host "Aucun fichier d'index standard détecté dans .hindex" -ForegroundColor Red
    Get-ChildItem $out -Recurse
}

# 5) Requête test
Write-Host "`n[5] Requête: ""class Greeter""" -ForegroundColor Yellow
hindex query "class Greeter" --index $out
Write-Host "`n== FIN DIAG ==" -ForegroundColor Cyan
