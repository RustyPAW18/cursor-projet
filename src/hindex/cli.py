from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .indexer import build_index, query_index

def _default_from_pyproject() -> tuple[int, list[str], int]:
    dim = 768
    globs = ["**/*.py"]
    min_bytes = 0
    try:
        import tomllib
        data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        cfg = data.get("tool", {}).get("hindex", {})
        dim = int(cfg.get("dim", dim))
        globs = list(cfg.get("file_globs", globs))
        min_bytes = int(cfg.get("min_symbol_bytes", min_bytes))
    except Exception:
        pass
    return dim, globs, min_bytes

def cmd_ingest(args: argparse.Namespace) -> int:
    dim, globs, min_bytes_cfg = _default_from_pyproject()
    if args.dim is not None:
        dim = int(args.dim)
    if args.file_glob:
        globs = args.file_glob
    # auto --project src si présent (sauf --no-auto)
    project = args.project
    if (project is None or project == ".") and (not args.no_auto) and Path("src").exists():
        project = "src"
    min_symbol_bytes = args.min_symbol_bytes if args.min_symbol_bytes is not None else min_bytes_cfg

    out = build_index(project, args.out, dim=dim, file_globs=globs, min_symbol_bytes=min_symbol_bytes)
    print(f"[hindex] index written to: {out}")
    return 0

def cmd_query(args: argparse.Namespace) -> int:
    hits = query_index(args.index, args.q, k=args.k)
    if args.jsonl:
        for h in hits:
            print(json.dumps(h, ensure_ascii=False))
    else:
        if not hits:
            print("[hindex] no results.")
        for i, h in enumerate(hits, 1):
            print(f"{i:>2}. {h['score']}  {h['symbol']}  —  {h['file']}")
            print(f"    {h['preview']}")
    return 0

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="hindex",
        description="hybrid index (tree-sitter/ast + FAISS, with numpy fallback)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest", help="build index from project")
    p_ing.add_argument("--project", type=str, default=".", help="project root path (auto 'src' if present)")
    p_ing.add_argument("--out", type=str, default=".hindex", help="output index directory")
    p_ing.add_argument("--dim", type=int, default=None, help="embedding dimension (override)")
    p_ing.add_argument("--file-glob", type=str, action="append", help="file glob(s)")
    p_ing.add_argument("--min-symbol-bytes", type=int, default=None, help="drop symbols smaller than N bytes")
    p_ing.add_argument("--no-auto", action="store_true", help="disable auto-detection of project=src")
    p_ing.set_defaults(func=cmd_ingest)

    p_q = sub.add_parser("query", help="query an existing index")
    p_q.add_argument("--index", type=str, default=".hindex", help="index directory")
    p_q.add_argument("--q", type=str, required=True, help="free text query")
    p_q.add_argument("--k", type=int, default=5, help="top-k")
    p_q.add_argument("--jsonl", action="store_true", help="output JSONL")
    p_q.set_defaults(func=cmd_query)

    args = p.parse_args(argv)
    return int(args.func(args))

if __name__ == "__main__":
    sys.exit(main())
