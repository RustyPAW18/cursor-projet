# parser_py.py — fallback robuste sans tree-sitter
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Union, List
import re

# ----------------------
# Modèle attendu par indexer.py
# ----------------------
@dataclass
class Symbol:
    file: Path
    kind: str            # "module" | "class" | "function"
    name: str
    start_byte: int
    end_byte: int
    preview: str         # <- requis par indexer.py

# Regex simples pour extraire class/def en fallback
_CLASS_RE = re.compile(r'^\s*class\s+([A-Za-z_]\w*)\s*(\([^)]*\))?\s*:', re.MULTILINE)
_DEF_RE   = re.compile(r'^\s*def\s+([A-Za-z_]\w*)\s*\(', re.MULTILINE)

def _line_at(txt: str, pos: int) -> str:
    """Retourne la ligne (en-tête) contenant pos, tronquée proprement."""
    start = txt.rfind("\n", 0, pos) + 1
    end = txt.find("\n", pos)
    if end == -1:
        end = len(txt)
    return txt[start:end].strip()

def _iter_regex_symbols(txt: str, file: Path) -> Iterable[Symbol]:
    # classes
    for m in _CLASS_RE.finditer(txt):
        name = m.group(1)
        start = m.start()
        # heuristique simple: préview = ligne d'en-tête
        preview = _line_at(txt, start)
        end = txt.find("\n", m.end())
        if end == -1:
            end = len(txt)
        yield Symbol(file=file, kind="class", name=name,
                     start_byte=start, end_byte=end, preview=preview)
    # fonctions
    for m in _DEF_RE.finditer(txt):
        name = m.group(1)
        start = m.start()
        preview = _line_at(txt, start)
        end = txt.find("\n", m.end())
        if end == -1:
            end = len(txt)
        yield Symbol(file=file, kind="function", name=name,
                     start_byte=start, end_byte=end, preview=preview)

def _fallback_symbols(file_or_text: Union[Path, str]) -> List[Symbol]:
    if isinstance(file_or_text, Path):
        path = file_or_text
        txt = path.read_text(encoding="utf-8", errors="ignore")
        mod_name = path.stem
    else:
        txt = str(file_or_text)
        path = Path("<memory>")
        mod_name = "module"

    syms: List[Symbol] = []
    # Toujours un symbole "module" couvrant tout le texte,
    # preview = début de fichier (200 chars) sur une seule ligne
    module_preview = " ".join(txt[:200].split())
    syms.append(Symbol(file=path, kind="module", name=mod_name,
                       start_byte=0, end_byte=len(txt), preview=module_preview))
    # + classes & defs détectées
    syms.extend(_iter_regex_symbols(txt, path))
    return syms

def extract_symbols(file_or_text: Union[Path, str]) -> List[Symbol]:
    """
    Essaie tree_sitter si dispo ; sinon fallback regex.
    Accepte Path OU str (texte). Retourne une liste de Symbol (avec preview).
    """
    try:
        # Si tree_sitter est présent mais sans grammaire Python, on retombe au fallback.
        from tree_sitter import Parser  # type: ignore  # noqa: F401
        # TODO: brancher l'AST réel si/when grammaire Python dispo.
        return _fallback_symbols(file_or_text)
    except Exception:
        return _fallback_symbols(file_or_text)
