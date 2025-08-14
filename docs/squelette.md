# Squelette méthodologique — Rappel rapide

1. **Cadre de travail**
   - Baseline immuable, branche unique, périmètre réduit.
   - Tests rapides, CHANGELOG à jour.

2. **Rituel d’ouverture (par session)**
   - But unique, contrainte, entrées/sorties, DoD.

3. **Style de patch**
   - Minimal, fonctions pures, logs explicites, erreurs gérées proprement.

4. **Checklists**
   - Avant patch : objectif unique ? périmètre OK ? sauvegarde ?
   - Après patch : lint OK, tests OK, docs/README/CHANGELOG mis à jour.

5. **Tests micro**
   - Cas heureux, cas bord, cas erreur.

6. **Stop rules**
   - Si > 4–5 correctifs enchaînés ou dérive du périmètre → **reset propre**.
