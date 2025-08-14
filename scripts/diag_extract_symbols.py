# scripts/diag_extract_symbols.py
from pathlib import Path
from hindex import indexer as i
from hindex import parser_py as p

SRC = Path(r"C:\Users\Verca\Cursor\src")

def main():
    files = list(i._iter_files(SRC, ["**/*.py"]))
    print("[diag] py files:", len(files))
    for f in files[:5]:
        text = Path(f).read_text(encoding="utf-8", errors="ignore")
        # -> Votre version de extract_symbols ne supporte pas 'file_path'
        syms = list(p.extract_symbols(text))
        print(f"\nFile: {f}")
        print("  symbols:", len(syms))
        for s in syms[:8]:
            start = getattr(s, "start_byte", None)
            end = getattr(s, "end_byte", None)
            size = (end or 0) - (start or 0)
            print("   -", getattr(s, "kind", "?"), getattr(s, "name", "?"), "size=", size)

if __name__ == "__main__":
    main()
