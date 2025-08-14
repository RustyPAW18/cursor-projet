from __future__ import annotations
import json, fnmatch
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import numpy as np

try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except Exception:
    faiss = None  # type: ignore
    _HAS_FAISS = False

from .embedding import hashing_vectorize
from .parser_py import Symbol, extract_symbols

@dataclass
class MetaItem:
    id: int
    file: str
    kind: str
    name: str
    start_byte: int
    end_byte: int
    preview: str

@dataclass
class IndexMeta:
    dim: int
    items: List[MetaItem]
    version: str = "1.1"

_DEFAULT_EXCLUDES = (
    ".venv/**", "**/.venv/**",
    "**/.git/**", "**/.hindex/**",
    "dist/**", "build/**",
    "**/site-packages/**",
)

def _iter_files(project: Path, globs: Iterable[str], exclude_globs: Iterable[str]) -> Iterable[Path]:
    ex = list(exclude_globs)
    for g in globs:
        for p in project.glob(g):
            if not p.is_file():
                continue
            rel = p.relative_to(project)
            rel_s = str(rel).replace("\\", "/")
            skip = any(Path(rel_s).match(e) or fnmatch.fnmatch(rel_s, e) for e in ex)
            if skip:
                continue
            yield p

def build_index(
    project_path: str | Path,
    out_dir: str | Path,
    *,
    dim: int = 768,
    file_globs: Iterable[str] = ("**/*.py",),
    exclude_globs: Iterable[str] = _DEFAULT_EXCLUDES,
) -> Path:
    project = Path(project_path).resolve()
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    vectors: List[np.ndarray] = []
    meta_items: List[MetaItem] = []
    next_id = 0

    for file in _iter_files(project, file_globs, exclude_globs):
        if not file.is_file() or file.suffix != ".py":
            continue
        try:
            symbols = extract_symbols(file)
        except Exception:
            continue
        for sym in symbols:
            try:
                data = file.read_bytes()
                snippet = data[sym.start_byte:sym.end_byte].decode("utf-8", errors="ignore")
            except Exception:
                snippet = sym.preview
            vec = hashing_vectorize(snippet, dim=dim)
            vectors.append(vec)
            meta_items.append(MetaItem(
                id=next_id, file=str(sym.file), kind=sym.kind, name=sym.name,
                start_byte=sym.start_byte, end_byte=sym.end_byte, preview=sym.preview
            ))
            next_id += 1

    xb = np.vstack(vectors).astype(np.float32) if vectors else np.zeros((0, dim), dtype=np.float32)

    if _HAS_FAISS:
        index = faiss.IndexFlatIP(dim)
        if xb.shape[0] > 0:
            index.add(xb)
        faiss.write_index(index, str(out / "index.faiss"))
    else:
        np.save(out / "vectors.npy", xb)

    with (out / "meta.json").open("w", encoding="utf-8") as f:
        json.dump(asdict(IndexMeta(dim=dim, items=meta_items)), f, ensure_ascii=False, indent=2)
    return out

def _load(out_dir: str | Path):
    out = Path(out_dir)
    meta_raw = json.loads((out / "meta.json").read_text(encoding="utf-8"))
    items = [MetaItem(**mi) for mi in meta_raw["items"]]
    meta = IndexMeta(dim=meta_raw["dim"], items=items, version=meta_raw.get("version", "1.1"))
    if _HAS_FAISS and (out / "index.faiss").exists():
        index = faiss.read_index(str(out / "index.faiss"))
        return ("faiss", index, meta)
    else:
        xb_path = out / "vectors.npy"
        xb = np.load(xb_path) if xb_path.exists() else np.zeros((0, meta.dim), dtype=np.float32)
        return ("numpy", xb, meta)

def _cosine_search_numpy(xb: np.ndarray, q: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
    if xb.shape[0] == 0:
        return np.array([[]], dtype=np.float32), np.array([[-1]*k], dtype=np.int32)
    scores = xb @ q.reshape(-1, 1)
    idx = np.argsort(-scores.flatten())[:k]
    return scores[idx].reshape(1, -1), idx.reshape(1, -1)

def query_index(index_dir: str | Path, query: str, *, k: int = 5) -> List[Dict[str, str]]:
    kind, idx_obj, meta = _load(index_dir)
    qv = hashing_vectorize(query, dim=meta.dim).astype(np.float32)

    if kind == "faiss":
        if idx_obj.ntotal == 0:
            return []
        D, I = idx_obj.search(qv.reshape(1, -1), k)
    else:
        xb = idx_obj
        D, I = _cosine_search_numpy(xb, qv, k)

    results: List[Dict[str, str]] = []
    for dist, idx in zip(D[0].tolist(), I[0].tolist()):
        if idx < 0 or idx >= len(meta.items):
            continue
        it = meta.items[idx]
        results.append({
            "score": f"{float(dist):.4f}",
            "file": it.file,
            "symbol": f"{it.kind} {it.name}",
            "preview": it.preview.replace("\n", " ")[:200],
        })
    return results
