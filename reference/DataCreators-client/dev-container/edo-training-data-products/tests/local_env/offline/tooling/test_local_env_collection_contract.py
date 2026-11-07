from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_pytest_ini_collects_new_local_env_roots() -> None:
    cfg = _read("pytest.ini")
    assert "testpaths =" in cfg
    assert "data_products" in cfg
    assert "tests/local_env/offline" in cfg
    assert "tests/local_env/live" in cfg


def test_legacy_data_products_testpaths_preserved() -> None:
    cfg = _read("pytest.ini")
    assert "data_products" in cfg
