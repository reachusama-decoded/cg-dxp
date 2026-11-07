import os
import subprocess

import pytest

from tests.challenges.conftest import repo_root

pytestmark = pytest.mark.integration


@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1", reason="needs Airflow/Astro")
def test_solution_dag_triggers_green() -> None:
    ch = repo_root() / "challenges" / "v1" / "03-airflow-orchestration"
    root = ch / "solution"
    r = subprocess.run(
        ["bash", "verify.sh"],
        cwd=ch,
        capture_output=True,
        text=True,
        env={**os.environ, "PORTFOLIO_ANALYTICS_ROOT": str(root)},
    )
    assert r.returncode == 0, r.stdout + r.stderr
