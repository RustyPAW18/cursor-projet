from __future__ import annotations
import json
from pathlib import Path
from textwrap import dedent

import pytest

from hindex.indexer import build_index
from hindex import cli as hcli


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_min_symbol_bytes_filters_small_symbols(tmp_path: Path):
    # Repo de test simple
    pkg = tmp_path / "pkg"
    _write(pkg / "__init__.py", "")
    # une très petite fonction (sera filtrée si threshold > sa taille)
    _write(
        pkg / "tiny.py",
        "def x():\n    return 1\n",
    )
    # une plus grosse fonction
    _write(
        pkg / "big.py",
        dedent(
            """
            def useful(a, b, c):
                s = 0
                for i in range(100):
                    s += (a + b + c + i)
                return s
            """
        ).strip()
    )

    out = tmp_path / ".hindex"

    # Sans filtre : on garde tout
    build_index(tmp_path, out, dim=64, file_globs=("**/*.py",), min_symbol_bytes=0)
    meta_all = json.loads((out / "meta.json").read_text(encoding="utf-8"))["items"]
    assert any("tiny.py" in it["file"] for it in meta_all)
    assert any("big.py" in it["file"] for it in meta_all)

    # Avec filtre strict : la tiny doit disparaître
    out2 = tmp_path / ".hindex2"
    build_index(tmp_path, out2, dim=64, file_globs=("**/*.py",), min_symbol_bytes=40)
    meta_filt = json.loads((out2 / "meta.json").read_text(encoding="utf-8"))["items"]
    assert not any("tiny.py" in it["file"] for it in meta_filt)
    assert any("big.py" in it["file"] for it in meta_filt)


def test_cli_auto_project_src(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    # Structure style projet réel : ./src/...
    src = tmp_path / "src" / "mymod"
    _write(src / "__init__.py", "")
    _write(
        src / "feature.py",
        "class A:\n    def f(self):\n        return 'ok'\n",
    )

    # Se placer dans tmp_path : la CLI doit auto-détecter ./src
    monkeypatch.chdir(tmp_path)
    # Pas d'argument --project -> doit utiliser src/
    rc = hcli.main(["ingest", "--out", ".hindex_cli", "--dim", "64"])
    assert rc == 0

    meta = json.loads((tmp_path / ".hindex_cli" / "meta.json").read_text(encoding="utf-8"))
    files = [it["file"] for it in meta["items"]]
    # Tous les fichiers indexés doivent se trouver sous tmp_path/src
    assert files and all(str(tmp_path / "src") in f for f in files)

    # Rejouer en désactivant l'auto
    out2 = tmp_path / ".hindex_cli2"
    rc2 = hcli.main(["ingest", "--out", str(out2), "--no-auto", "--project", ".", "--dim", "64"])
    assert rc2 == 0

    meta2 = json.loads((out2 / "meta.json").read_text(encoding="utf-8"))
    files2 = [it["file"] for it in meta2["items"]]
    # Cette fois, on a bien scanné depuis ".", donc le chemin peut inclure autre chose que src
    assert files2 and any(str(tmp_path / "src") in f for f in files2)
