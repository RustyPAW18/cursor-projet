from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .indexer import build_index, query_index

def _default_from_pyproject() -> tuple[int, list[str], list[str]]:
    dim = 768
    globs = ["**/*.py"]
    excludes: list[str] = []
    try:
        import tomllib
        data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
        cfg = data.get("tool", {}).get("hindex", {})
        dim = int(cfg.get("dim", dim))
        globs = list(cfg.get("file_globs", globs))
        excludes = list(cfg.get("exclude_globs", excludes))
    except Exception:
        pass
    return dim, globs, excludes

def cmd_ingest(args: argparse.Namespace) -> int:
    dim, globs, excludes = _default_from_pyproject()
    if args.dim is not None:
        dim = int(args.dim)
    if args.file_glob:
        globs = args.file_glob
    if args.exclude_glob:
        excludes = (excludes or []) + args.exclude_glob
    out = build_index(args.project, args.out, dim=dim, file_globs=globs, exclude_globs=excludes)
    print(f"[hindex] index wr
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
    p = argparse.ArgumentParser(prog="hindex", description="hybrid index (ast + FAISS, with numpy fallback)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest", help="build index from project")
    p_ing.add_argument("--project", type=str, default=".", help="project root path")
    p_ing.add_argument("--out", type=str, default=".hindex", help="output index directory")
    p_ing.add_argument("--dim", type=int, default=None, help="embedding dimension (override)")
    p_ing.add_argument("--file-glob", type=str, action="append", help="file glob(s)")
    p_ing.add_argument("--exclude-glob", type=str, action="append", help="exclude glob(s)")
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
