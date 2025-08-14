from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

@dataclass
class Symbol:
    file: Path
    kind: str  # "function" | "class" | "module"
    name: str
    start_byte: int
    end_byte: int
    preview: str

def _fallback_chunks(file: Path) -> Iterable[Symbol]:
    txt = file.read_text(encoding="utf-8", errors="ignore")
    yield Symbol(file=file, kind="module", name=file.stem, start_byte=0, end_byte=len(txt.encode("utf-8")), preview=txt[:200])

def extract_symbols(file: Path) -> List[Symbol]:
    try:
        from tree_sitter import Parser  # type: ignore
        from tree_sitter_languages import get_language  # type: ignore
    except Exception:
        return list(_fallback_chunks(file))

    lang = get_language("python")
    parser = Parser(); parser.set_language(lang)
    data = file.read_bytes()
    tree = parser.parse(data); root = tree.root_node
    out: List[Symbol] = []

    def text_slice(n) -> str:
        return data[n.start_byte:n.end_byte].decode("utf-8", errors="ignore")

    def walk(node) -> None:
        if node.type in ("function_definition", "class_definition"):
            name_node = next((c for c in node.children if c.type == "identifier"), None)
            name = data[name_node.start_byte:name_node.end_byte].decode("utf-8", errors="ignore") if name_node else "<anon>"
            kind = "function" if node.type == "function_definition" else "class"
            out.append(Symbol(file=file, kind=kind, name=name, start_byte=node.start_byte, end_byte=node.end_byte, preview=text_slice(node)[:200]))
        for ch in node.children:
            walk(ch)

    walk(root)
    return out or list(_fallback_chunks(file))
