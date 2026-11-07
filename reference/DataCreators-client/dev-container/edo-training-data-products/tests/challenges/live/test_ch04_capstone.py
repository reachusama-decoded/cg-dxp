from __future__ import annotations

import os
import subprocess

import pytest

from tests.challenges.conftest import repo_root

pytestmark = pytest.mark.integration


def _run_solution(scope: str) -> subprocess.CompletedProcess[str]:
    ch = repo_root() / "challenges" / "v1" / "04-atlas-capstone"
    env = {
        **os.environ,
        "ATLAS_ELT_MODELS_ROOT": str(ch / "solution"),
        "ATLAS_VERIFY_SCOPE": scope,
    }
    return subprocess.run(
        ["bash", "verify.sh"],
        cwd=ch,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1", reason="needs Databricks")
def test_solution_phase1_mvp_passes() -> None:
    r = _run_solution("mvp")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Done. PASS=23 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=23" in r.stdout
    assert "Done. PASS=3 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=3" in r.stdout
    assert "MVP LIVE PASS" in r.stdout
    assert "Atlas ELT Phase 1 MVP complete" in r.stdout


@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1", reason="needs Databricks")
def test_solution_full_capstone_passes() -> None:
    r = _run_solution("full")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "LIVE PASS" in r.stdout
    assert "Atlas ELT capstone complete" in r.stdout
