#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"

def which(cmds):
    for c in cmds:
        if Path(c).exists():
            return str(c)
    return None

def venv_bin(name):
    if os.name == "nt":
        return PROJECT_ROOT / ".venv" / "Scripts" / f"{name}.exe"
    else:
        return PROJECT_ROOT / ".venv" / "bin" / name

def pick_executable(name):
    # prefer venv executable
    candidates = [venv_bin(name)]
    # fallback to PATH
    candidates += [name]
    if os.name == "nt":
        candidates += [f"{name}.exe", f"{name}.bat"]
    return which(candidates)

def run(cmd, **kwargs):
    print("→", " ".join(cmd))
    return subprocess.call(cmd, **kwargs)

def ensure_env():
    os.environ.setdefault("PYTHONPATH", str(SRC_DIR))
    return True

def doctor():
    ensure_env()
    print("PYTHON:", sys.executable)
    print("PYTHONPATH:", os.environ["PYTHONPATH"])
    for tool in ["python", "ruff", "black", "isort", "pytest"]:
        exe = pick_executable(tool)
        print(f"{tool:6}:", exe or "NOT FOUND")

def do_lint():
    ensure_env()
    exe = pick_executable("ruff") or "ruff"
    return run([exe, "check", str(SRC_DIR), str(TESTS_DIR)])

def do_format():
    ensure_env()
    exe_black = pick_executable("black") or "black"
    exe_isort = pick_executable("isort") or "isort"
    rc1 = run([exe_isort, str(SRC_DIR), str(TESTS_DIR)])
    rc2 = run([exe_black, str(SRC_DIR), str(TESTS_DIR)])
    return rc1 or rc2

def do_test():
    ensure_env()
    exe = pick_executable("pytest") or "pytest"
    return run([exe, "-q"])

def do_all():
    rc = do_lint()
    if rc != 0: 
        print("Lint failed; continuing to format and tests…")
    rc |= do_format()
    rc |= do_test()
    return rc

def main():
    actions = {
        "doctor": doctor,
        "lint": do_lint,
        "format": do_format,
        "test": do_test,
        "all": do_all,
    }
    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        print("Usage: python run.py [doctor|lint|format|test|all]")
        return 2
    return actions[sys.argv[1]]() or 0

if __name__ == "__main__":
    sys.exit(main())
