import os, subprocess
import pytest
from tests.challenges.conftest import repo_root

pytestmark = pytest.mark.integration

@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1", reason="needs Databricks")
def test_solution_builds_green() -> None:
    # Maintainer/live baseline: the retained solution must build + test green on Databricks.
    ch = repo_root() / "challenges" / "v1" / "02-dbt-pipeline"
    r = subprocess.run(["bash", "verify.sh"], cwd=ch, capture_output=True, text=True,
                       env={**os.environ, "DBT_MODELS_DIR": str(ch / "solution" / "models")})
    assert r.returncode == 0, r.stdout + r.stderr
