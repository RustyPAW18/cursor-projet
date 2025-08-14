# \# Changelog — Cursor Perso

# 

# \## \[v1.1] - 2025-08-13

# \### Changements

# \- Corrige encodage de `pyproject.toml` (UTF-8 sans BOM).

# \- Déplace les règles Ruff dans `\[tool.ruff.lint]` et ajoute un `exclude` correct.

# \- Met à jour les orchestrateurs (`run\_all.ps1` et `run\_all.bat`) avec ajout de `PYTHONPATH=src`.

# \- Contourne la signature obligatoire de PowerShell (scope=Process) pour exécuter les scripts.

# \- Vérifie le passage vert de `ruff`, `black` et `pytest` (2 tests OK).

# \- Vérifie l'import du package `cursor\_personal` via `PYTHONPATH=src`.

# 

# \### État

# ✅ Baseline stable et fonctionnelle  

# ✅ Tests unitaires OK  

# ✅ Lint \& format OK  

# ✅ Orchestrateurs fonctionnels



## 1.2.0 — 2025-08-14
### Ajouts
- Index hybride minimal (FAISS + hashing)
- CLI `hindex` : `ingest` / `query`
- Test fumée `tests/test_hindex_smoke.py`
