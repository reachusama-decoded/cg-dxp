from __future__ import annotations

from tests.challenges.conftest import repo_root


def test_challenge_02_verify_uses_repo_dbt_wrapper() -> None:
    script = (repo_root() / "challenges" / "v1" / "02-dbt-pipeline" / "verify.sh").read_text()
    assert "dbt_wrapper.py" in script
    assert "import dbt.cli.main" in script
    # Guard against regressions back to bare dbt CLI invocations that depend on PATH tool flavor.
    assert "dbt debug --profiles-dir" not in script
    assert "dbt build --profiles-dir" not in script


def test_challenge_04_verify_uses_repo_dbt_wrapper() -> None:
    script = (repo_root() / "challenges" / "v1" / "04-atlas-capstone" / "verify.sh").read_text()
    assert "dbt_wrapper.py" in script
    assert "import dbt.cli.main" in script
    assert '"$dbt_python" "$REPO_ROOT/dbt_wrapper.py" deps' in script
    assert "Running dbt deps" in script


def test_challenge_02_verify_defaults_to_working_tree_learner_gate() -> None:
    # Why: verify.sh is the trainee's self-check. It must build the learner's own
    # working models by default, so unsolved stubs build RED. CI confirms the
    # challenge is still solvable by pointing DBT_MODELS_DIR at solution/models.
    script = (repo_root() / "challenges" / "v1" / "02-dbt-pipeline" / "verify.sh").read_text()
    assert 'DEFAULT_MODELS_DIR="$PROJECT_DIR/models"' in script
    assert 'DEFAULT_TESTS_DIR="$PROJECT_DIR/tests"' in script
    assert 'DBT_MODELS_DIR="${DBT_MODELS_DIR:-$DEFAULT_MODELS_DIR}"' in script
    assert 'DBT_TESTS_DIR="${DBT_TESTS_DIR:-$DEFAULT_TESTS_DIR}"' in script
    assert 'cp -R "${DBT_TESTS_DIR}/." "$TMP_PROJECT/tests/"' in script
    # The learner gate must not paper over a red build by defaulting to the solution
    # or skipping on missing sources.
    assert 'DEFAULT_MODELS_DIR="$SCRIPT_DIR/solution/models"' not in script
    assert "TABLE_OR_VIEW_NOT_FOUND" not in script


def test_challenge_03_verify_statically_checks_dag_wiring() -> None:
    # Why: a full DagBag load renders the Cosmos dbt graph via `dbt ls`, which only
    # completes inside the fully-configured astro runtime. The offline gate instead
    # statically validates the trainee's DAG wiring (start -> source_freshness_check
    # -> dbt_pipeline -> publish_to_catalog -> end) — fast, deterministic, and with
    # no Airflow/Cosmos/dbt/auth dependency.
    script = (repo_root() / "challenges" / "v1" / "03-airflow-orchestration" / "verify.sh").read_text()
    assert "ast.parse" in script
    assert "run_dbt_fallback_verification" not in script
    for task in ("start", "source_freshness_check", "dbt_pipeline", "publish_to_catalog", "end"):
        assert task in script


def test_challenge_dbt_mise_task_uses_wrapper_and_dependency_check() -> None:
    toml = (repo_root() / ".mise.toml").read_text()
    assert '[tasks."challenge:dbt"]' in toml
    assert "dbt_wrapper.py" in toml
    assert 'import dbt.cli.main' in toml


def test_challenge_02_verify_seeds_then_runs_and_tests() -> None:
    # Why: challenge 02's raw sources ship as seeds; the gate must load them
    # before building so a solved pipeline can resolve source() and pass its tests.
    script = (repo_root() / "challenges" / "v1" / "02-dbt-pipeline" / "verify.sh").read_text()
    assert '"$REPO_ROOT/dbt_wrapper.py" seed' in script
    assert '"$REPO_ROOT/dbt_wrapper.py" run' in script
    assert '"$REPO_ROOT/dbt_wrapper.py" test' in script


def test_challenge_seed_task_exists() -> None:
    toml = (repo_root() / ".mise.toml").read_text()
    assert '[tasks."challenge:seed"]' in toml
    block = toml.split('[tasks."challenge:seed"]', 1)[1].split("\n[tasks.", 1)[0]
    assert "dbt_wrapper.py" in block
    assert "seed" in block
