from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
py = ROOT / "pyproject.toml"
bak = ROOT / "pyproject.toml.bak"

txt = py.read_text(encoding="utf-8")
lines = txt.splitlines(keepends=True)
hdr = re.compile(r"^\s*\[([^\]]+)\]\s*$")

seen = set()
out = []
i = 0
while i < len(lines):
    m = hdr.match(lines[i])
    if m:
        name = m.group(1).strip()
        if name in seen:
            # drop jusqu'au prochain header
            j = i + 1
            while j < len(lines) and not hdr.match(lines[j]):
                j += 1
            print(f"[FIX] Removed duplicate section [{name}] at line {i+1}")
            i = j
            continue
        seen.add(name)
    out.append(lines[i])
    i += 1

bak.write_text(txt, encoding="utf-8")
py.write_text("".join(out), encoding="utf-8")
print("[OK] Deduplicated. Backup:", bak)
