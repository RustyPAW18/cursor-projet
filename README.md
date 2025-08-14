# Cursor perso — Base propre (v1)

Ce pack crée une base **saine et minimale** pour nos sessions de code avec le squelette méthodologique.

## Objectifs
- Baseline immuable + périmètre réduit
- Orchestrateur simple: *lint → format → tests*
- Checklists avant/après patch
- CHANGELOG pour tracer chaque session

## Installation rapide (Windows)
1. Dézippez ce dossier où vous voulez (ex: `C:\Users\Verca\Cursor`).
2. Ouvrez **PowerShell** dans le dossier.
3. Exécutez :  
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
├─ src\cursor_personal\example.py
├─ tests\test_example.py
├─ scripts\*.ps1 / *.bat
├─ pyproject.toml
├─ requirements.txt
├─ CHANGELOG.md
└─ README.md
```

## Squelette méthodologique (résumé)
- **Cadre** : baseline immuable, patchs minimaux, logs explicites, I/O séparées.
- **Rituel d’ouverture** : but unique, définition de fini, sauvegarde baseline.
- **Checklists** : avant/après patch + DoD.
- **Stop rules** : au-delà de 4–5 correctifs → **reset propre** dans un nouveau chat.

Voir `docs/squelette.md` pour la version complète.
## Index hybride minimal (v1.2)
- FAISS + embedding hashing déterministe (offline)
- Segmentation symboles via tree-sitter (fallback safe si indispo)
- CLI :
  - Ingestion : `hindex ingest --project . --out .hindex`
  - Requête  : `hindex query --index .hindex --q "..." --k 5`
- Config : `[tool.hindex]` dans `pyproject.toml` (dim, globs)
