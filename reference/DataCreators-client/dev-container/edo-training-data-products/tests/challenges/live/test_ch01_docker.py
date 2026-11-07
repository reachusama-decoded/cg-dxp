from __future__ import annotations

import os
import subprocess

import pytest

from tests.challenges.conftest import repo_root

pytestmark = pytest.mark.integration


@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1", reason="needs docker")
def test_docker_build_and_run_passes() -> None:
    ch = repo_root() / "challenges" / "v1" / "01-docker-intro"
    env = {**os.environ, "CHALLENGE_DOCKER_CONTEXT": "solution"}
    r = subprocess.run(
        ["bash", "verify.sh"],
        cwd=ch,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout
