from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_dbt_wrappers_do_not_monkeypatch_requests_verify_false() -> None:
    assert "verify=False" not in _read("dbt_wrapper.py")
    assert "verify=False" not in _read("dbt_local.py")
