![CI](https://github.com/RustyPAW18/cursor-projet/actions/workflows/ci.yml/badge.svg)

# Cursor perso â€” Base propre (v1)

Ce pack crÃ©e une base **saine et minimale** pour nos sessions de code avec le squelette mÃ©thodologique.

## Objectifs
- Baseline immuable + pÃ©rimÃ¨tre rÃ©duit
- Orchestrateur simple: *lint â†’ format â†’ tests*
- Checklists avant/aprÃ¨s patch
- CHANGELOG pour tracer chaque session

## Installation rapide (Windows)
1. DÃ©zippez ce dossier oÃ¹ vous voulez (ex: `C:\Users\Verca\Cursor`).
2. Ouvrez **PowerShell** dans le dossier.
3. ExÃ©cutez :  
   ```powershell
   .\scripts\reset_setup_cursor_perso.ps1
   ```
4. Lancer l'orchestrateur (lint+format+tests) :  
   ```powershell
   .\scripts\run_all.ps1
   ```
   ou en BAT : `scripts\run_all.bat`

## Arborescence
```
.
â”œâ”€ src\cursor_personal\example.py
â”œâ”€ tests\test_example.py
â”œâ”€ scripts\*.ps1 / *.bat
â”œâ”€ pyproject.toml
â”œâ”€ requirements.txt
â”œâ”€ CHANGELOG.md
â””â”€ README.md
```

## Squelette mÃ©thodologique (rÃ©sumÃ©)
- **Cadre** : baseline immuable, patchs minimaux, logs explicites, I/O sÃ©parÃ©es.
- **Rituel dâ€™ouverture** : but unique, dÃ©finition de fini, sauvegarde baseline.
- **Checklists** : avant/aprÃ¨s patch + DoD.
- **Stop rules** : au-delÃ  de 4â€“5 correctifs â†’ **reset propre** dans un nouveau chat.

Voir `docs/squelette.md` pour la version complÃ¨te.
## Index hybride minimal (v1.2)
- FAISS + embedding hashing dÃ©terministe (offline)
- Segmentation symboles via tree-sitter (fallback safe si indispo)
- CLI :
  - Ingestion : `hindex ingest --project . --out .hindex`
  - RequÃªte  : `hindex query --index .hindex --q "..." --k 5`
- Config : `[tool.hindex]` dans `pyproject.toml` (dim, globs)


## ðŸš€ Runner unique (multiplateforme)

Au lieu d'utiliser des scripts `*.ps1` / `*.bat`, utilisez dÃ©sormais :

```bash
python run.py doctor   # affiche les chemins d'outils & PYTHONPATH
python run.py lint     # ruff check src tests
python run.py format   # black src tests
python run.py test     # pytest
python run.py all      # lint â†’ format â†’ test
```

> Le script dÃ©tecte automatiquement le `.venv` (Windows / Linux / macOS) et force `PYTHONPATH=src` pour le layout source.

# Cursor perso â€” hindex (scan & tests)

Mini outillage pour tester `extract_symbols` et gÃ©nÃ©rer un rapport de symboles sur tout `src/`.

## PrÃ©requis
- Windows + PowerShell
- Python 3.12+ (tests validÃ©s en 3.13)
- Environnement virtuel `.venv` activÃ©/reconnu par les scripts
- (pour tests `indexer`) `numpy` installÃ© dans le venv

```powershell
# (facultatif) DÃ©pendances dev
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install numpy pytest ruff




