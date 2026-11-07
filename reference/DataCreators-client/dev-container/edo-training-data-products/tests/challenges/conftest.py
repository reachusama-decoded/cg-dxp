from __future__ import annotations
import re
from pathlib import Path
import pytest


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def challenge_dirs() -> list[Path]:
    root = repo_root() / "challenges" / "v1"
    return sorted(p for p in root.glob("*") if p.is_dir() and re.match(r"\d\d-", p.name))


@pytest.fixture
def root() -> Path:
    return repo_root()
