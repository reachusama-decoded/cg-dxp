"""Functional tests for the optimize-databricks-job capability skill.

Loads optimize.py via importlib (the skill dir uses a hyphen). Scans a
rendered DAB tree's resources/*.yml files and produces findings under
DBX-PERF-* (with light overlap with DBX-BUNDLE-*).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "skills" / "optimize-databricks-job" / "scripts" / "optimize.py"


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "optimize_databricks_job_optimize", SCRIPT_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def optimize():
    return _load_script()


def _make_bundle(
    tmp_path: Path,
    *,
    max_concurrent_runs: int | None = 1,
    timeout_seconds: int | None = 3600,
    min_workers: int = 1,
    max_workers: int = 4,
    spark_version: str = "14.3.x-scala2.12",
    use_photon: bool = True,
) -> Path:
    bundle = tmp_path / "bundle"
    (bundle / "resources").mkdir(parents=True)
    (bundle / "databricks.yml").write_text("bundle:\n  name: test_bundle\n")

    job: dict = {"name": "etl_job"}
    if max_concurrent_runs is not None:
        job["max_concurrent_runs"] = max_concurrent_runs
    if timeout_seconds is not None:
        job["timeout_seconds"] = timeout_seconds
    job["tasks"] = [
        {
            "task_key": "main",
            "new_cluster": {
                "spark_version": spark_version,
                "autoscale": {
                    "min_workers": min_workers,
                    "max_workers": max_workers,
                },
                "runtime_engine": "PHOTON" if use_photon else "STANDARD",
            },
        }
    ]
    doc = {"resources": {"jobs": {"etl_job": job}}}
    (bundle / "resources" / "etl_job.yml").write_text(yaml.safe_dump(doc))
    return bundle


def test_report_on_bundle_prints_findings(tmp_path, capsys, optimize):
    bundle = _make_bundle(tmp_path, max_concurrent_runs=None)
    rc = optimize.main(["--bundle-path", str(bundle), "--mode", "report"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "DBX-PERF-001" in out


def test_dbx_perf_001_fires_when_max_concurrent_runs_missing(
    tmp_path, capsys, optimize
):
    bundle = _make_bundle(tmp_path, max_concurrent_runs=None)
    optimize.main(["--bundle-path", str(bundle), "--mode", "report"])
    out = capsys.readouterr().out
    assert "DBX-PERF-001" in out


def test_apply_mode_adds_max_concurrent_runs_1(tmp_path, capsys, optimize):
    bundle = _make_bundle(tmp_path, max_concurrent_runs=None)
    rc = optimize.main(["--bundle-path", str(bundle), "--mode", "apply"])
    assert rc == 0
    doc = yaml.safe_load((bundle / "resources" / "etl_job.yml").read_text())
    assert doc["resources"]["jobs"]["etl_job"]["max_concurrent_runs"] == 1


def test_dbx_perf_002_fires_when_min_equals_max_workers(
    tmp_path, capsys, optimize
):
    bundle = _make_bundle(tmp_path, min_workers=4, max_workers=4)
    optimize.main(["--bundle-path", str(bundle), "--mode", "report"])
    out = capsys.readouterr().out
    assert "DBX-PERF-002" in out


def test_dbx_perf_003_fires_on_dbr_13(tmp_path, capsys, optimize):
    bundle = _make_bundle(tmp_path, spark_version="13.3.x-scala2.12")
    optimize.main(["--bundle-path", str(bundle), "--mode", "report"])
    out = capsys.readouterr().out
    assert "DBX-PERF-003" in out


def test_dbx_perf_004_fires_when_timeout_seconds_missing(
    tmp_path, capsys, optimize
):
    bundle = _make_bundle(tmp_path, timeout_seconds=None)
    optimize.main(["--bundle-path", str(bundle), "--mode", "report"])
    out = capsys.readouterr().out
    assert "DBX-PERF-004" in out


def test_apply_mode_adds_timeout_seconds_3600(tmp_path, capsys, optimize):
    bundle = _make_bundle(tmp_path, timeout_seconds=None)
    rc = optimize.main(["--bundle-path", str(bundle), "--mode", "apply"])
    assert rc == 0
    doc = yaml.safe_load((bundle / "resources" / "etl_job.yml").read_text())
    assert doc["resources"]["jobs"]["etl_job"]["timeout_seconds"] == 3600


def test_dbx_perf_005_fires_when_photon_disabled(tmp_path, capsys, optimize):
    bundle = _make_bundle(tmp_path, use_photon=False)
    optimize.main(["--bundle-path", str(bundle), "--mode", "report"])
    out = capsys.readouterr().out
    assert "DBX-PERF-005" in out


def test_missing_databricks_yml_exits_2(tmp_path, capsys, optimize):
    empty = tmp_path / "empty"
    empty.mkdir()
    rc = optimize.main(["--bundle-path", str(empty), "--mode", "report"])
    assert rc == 2


def test_json_format_returns_valid_list(tmp_path, capsys, optimize):
    bundle = _make_bundle(tmp_path, max_concurrent_runs=None)
    rc = optimize.main(
        ["--bundle-path", str(bundle), "--mode", "report", "--format", "json"]
    )
    out = capsys.readouterr().out
    assert rc == 0
    parsed = json.loads(out)
    assert isinstance(parsed, list)
    assert any(f["rule_id"] == "DBX-PERF-001" for f in parsed)


def test_token_redaction_bearer_scrubbed(tmp_path, capsys, optimize):
    bundle = _make_bundle(tmp_path, max_concurrent_runs=None)
    # Inject a Bearer token into the resource file name path so it surfaces
    # in the finding's target/message and would be redacted.
    job_yml = bundle / "resources" / "etl_job.yml"
    text = job_yml.read_text()
    job_yml.write_text(text + "\n# token: Bearer abc.def-123_XYZ\n")
    optimize.main(
        ["--bundle-path", str(bundle), "--mode", "report", "--format", "json"]
    )
    out = capsys.readouterr().out
    assert "abc.def-123_XYZ" not in out
