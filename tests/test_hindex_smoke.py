from __future__ import annotations
from pathlib import Path
from textwrap import dedent
from hindex.indexer import build_index, query_index

def _sample_repo(tmp: Path) -> None:
    (tmp / "pkg").mkdir(parents=True, exist_ok=True)
    (tmp / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp / "pkg" / "util.py").write_text(
        dedent("""
            import http.client
            class Greeter:
                def __init__(self, name: str) -> None:
                    self.name = name
                def hello(self) -> str:
                    return f"Hello {self.name}"
            def retry_http_get(host: str, path: str, attempts: int = 3) -> bytes:
                for _ in range(attempts):
                    conn = http.client.HTTPSConnection(host, timeout=5)
                    conn.request("GET", path)
                    r = conn.getresponse()
                    if r.status == 200:
                        return r.read()
                raise RuntimeError("failed")
        """).strip(),
        encoding="utf-8",
    )

def test_build_and_query(tmp_path):
    _sample_repo(tmp_path)
    out = tmp_path / ".hindex"
    build_index(tmp_path, out, dim=128, file_globs=("**/*.py",))
    hits = query_index(out, "http client retry logic", k=3)
    assert isinstance(hits, list)
    assert len(hits) >= 1
    assert any("util.py" in h["file"] for h in hits)
