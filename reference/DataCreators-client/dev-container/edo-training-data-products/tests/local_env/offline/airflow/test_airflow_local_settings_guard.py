import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

import importlib

import airflow_local_settings as als


def test_guard_disabled_for_untested_version(monkeypatch):
    monkeypatch.setenv("TRAINING_AIRFLOW3_SUPERVISOR_PATCHES", "1")
    assert als._airflow_supervisor_patches_enabled("2.10.5") is False
    assert als._airflow_supervisor_patches_enabled("3.2.0") is False


def test_guard_enabled_only_for_tested_version_and_optin(monkeypatch):
    monkeypatch.setenv("TRAINING_AIRFLOW3_SUPERVISOR_PATCHES", "1")
    assert als._airflow_supervisor_patches_enabled("3.1.0") is True
    monkeypatch.delenv("TRAINING_AIRFLOW3_SUPERVISOR_PATCHES", raising=False)
    assert als._airflow_supervisor_patches_enabled("3.1.0") is False
