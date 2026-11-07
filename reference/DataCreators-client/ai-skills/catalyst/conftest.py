"""Root conftest: add the project root to sys.path so that the top-level
``skills`` package is importable without an editable install."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
