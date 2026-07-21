"""Shared test helpers.

The repo's scripts are standalone files with hyphens in their names
(`schedule-sync.py`, `render_and_send.py`, …) — not an importable package.
`load_module` imports one by file path so tests can exercise its functions.
"""
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
SKILLS = REPO_ROOT / ".claude" / "skills"

_seq = 0


def load_module(path, name=None):
    """Import a Python file by path and return the module object."""
    global _seq
    path = Path(path)
    if name is None:
        _seq += 1
        name = f"_loaded_{path.stem.replace('-', '_')}_{_seq}"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
