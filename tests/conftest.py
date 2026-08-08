"""Make the tests directory importable so tests can `from _util import ...`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
