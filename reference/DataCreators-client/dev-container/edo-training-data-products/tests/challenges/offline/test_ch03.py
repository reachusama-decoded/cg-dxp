import pytest

from tests.challenges.conftest import repo_root

PA = repo_root() / "data_products" / "portfolio_analytics"
CH = repo_root() / "challenges" / "v1" / "03-airflow-orchestration"


@pytest.mark.parametrize(
    "profile_path",
    [
        PA / "dbt" / "profiles.yml",
        CH / "stubs" / "dbt" / "profiles.yml",
        CH / "solution" / "dbt" / "profiles.yml",
    ],
)
def test_dbt_profile_defines_local_target(profile_path) -> None:
    # Why: the challenge:dbt / challenge:seed mise tasks invoke dbt with
    # `--target local` (the repo-wide convention shared by every other profile).
    # The portfolio_analytics profile the tasks point at — and the stub/solution
    # copies that `challenge:reset` restores from — MUST define a `local` output,
    # or step 3's `mise run challenge:dbt 03 -- debug` fails with
    # "profile does not have a target named 'local'".
    text = profile_path.read_text()
    assert "    local:" in text, f"{profile_path} must define a 'local' target"
    assert "    dev:" in text


def test_product_placed_natively_no_bundle() -> None:
    assert (PA / "dags" / "portfolio_analytics_daily.py").exists()
    assert (PA / "dbt" / "dbt_project.yml").exists()
    assert not (PA / "databricks.yml").exists()


def test_working_dag_is_the_stub() -> None:
    text = (PA / "dags" / "portfolio_analytics_daily.py").read_text()
    assert "TODO: wire start -> source_freshness_check -> dbt_pipeline -> publish_to_catalog -> end" in text
    assert "schedule_interval" not in text


def test_solution_dag_parses_and_has_tags() -> None:
    text = (CH / "solution" / "dags" / "portfolio_analytics_daily.py").read_text()
    assert "tags=" in text
    assert "schedule=" in text


def test_astro_dag_integrity_file_present() -> None:
    # Why: .astro/test_dag_integrity_default.py is the standard DAG-integrity test
    # that `astro dev init` scaffolds. Without it `astro dev parse` / `astro dev
    # pytest` abort with "does not exist. Please run `astro dev init`". The guide
    # no longer teaches the vacuous `astro dev parse`, but the file must still ship
    # so a fresh clone is a complete, valid astro project.
    path = repo_root() / ".astro" / "test_dag_integrity_default.py"
    assert path.exists(), (
        ".astro/test_dag_integrity_default.py must be committed for `astro dev parse`"
    )
    assert "DagBag" in path.read_text()


@pytest.mark.parametrize(
    "sources_path",
    [
        PA / "dbt" / "models" / "sources.yml",
        CH / "stubs" / "dbt" / "models" / "sources.yml",
        CH / "solution" / "dbt" / "models" / "sources.yml",
    ],
)
def test_sources_pin_database_and_schema_to_target(sources_path) -> None:
    # Why: without database/schema pins, dbt resolves source('custodian', ...) to a
    # schema literally named 'custodian' (the source name), not the trainee's target
    # schema where the tables are provisioned — so the DAG's freshness gate and every
    # staging model hit TABLE_OR_VIEW_NOT_FOUND. Pin both to the dbt target (matches
    # challenge 02) so source() resolves to <catalog>.<your_schema>.<table>.
    text = sources_path.read_text()
    assert text.count('database: "{{ target.database }}"') >= 4, (
        f"{sources_path} must pin database to target for all 4 sources"
    )
    assert text.count('schema: "{{ target.schema }}"') >= 4, (
        f"{sources_path} must pin schema to target for all 4 sources"
    )


def test_raw_seeds_freshen_extracted_at_so_freshness_gate_passes() -> None:
    # Why: challenge 03's DAG freshness gate runs `dbt source freshness` on the
    # custodian feed, which fails unless _extracted_at is recent. The raw sources are
    # provisioned by REUSING challenge 02's seeds (mise run challenge:seed 02) into the
    # same schema; those CSVs carry a static, months-old _extracted_at. A seed post-hook
    # in challenge 02 must refresh _extracted_at to current_timestamp() so a freshly
    # seeded feed passes the gate on a green run. Removing it silently breaks 03 step 9.
    proj = (
        repo_root() / "challenges" / "v1" / "02-dbt-pipeline" / "dbt" / "dbt_project.yml"
    ).read_text()
    assert "post-hook" in proj, "02 seeds must post-hook to refresh _extracted_at"
    assert "_extracted_at = current_timestamp()" in proj


_DAGS = [
    PA / "dags" / "portfolio_analytics_daily.py",
    CH / "stubs" / "dags" / "portfolio_analytics_daily.py",
    CH / "solution" / "dags" / "portfolio_analytics_daily.py",
]
_PROFILES = [
    PA / "dbt" / "profiles.yml",
    CH / "stubs" / "dbt" / "profiles.yml",
    CH / "solution" / "dbt" / "profiles.yml",
]


@pytest.mark.parametrize("profile_path", _PROFILES)
def test_profile_has_airflow_token_target(profile_path) -> None:
    # Why: in the astro runtime the DAG's freshness gate must authenticate with the
    # fresh OAuth token from the databricks_default connection, not the static oauth
    # profile, which falls back to interactive external-browser auth and hangs the task.
    # It runs dbt against an `airflow` target that reads DBT_ACCESS_TOKEN (token auth).
    text = profile_path.read_text()
    assert "    airflow:" in text, f"{profile_path} must define an 'airflow' target"
    assert "env_var('DBT_ACCESS_TOKEN'" in text


@pytest.mark.parametrize("dag_path", _DAGS)
def test_freshness_gate_auths_via_connection_token(dag_path) -> None:
    # Why: the freshness gate must reuse the databricks_default connection's fresh token
    # (like Cosmos) and run dbt with --target airflow; the static oauth profile hangs on
    # interactive browser OAuth in the astro runtime.
    text = dag_path.read_text()
    assert 'get_connection("databricks_default")' in text
    assert '"airflow"' in text


@pytest.mark.parametrize("dag_path", _DAGS)
def test_freshness_gate_surfaces_real_error_not_only_stale(dag_path) -> None:
    # Why: dbt returns a non-zero exit for BOTH a real freshness breach AND a
    # connection/config error (e.g. missing http_path when the astro stack was started
    # before the Databricks env was ready — the common cold-start failure). The gate
    # used to report "breached error_after" for EVERY failure, sending trainees to chase
    # a stale feed when the stack just needs `astro dev restart`. It must capture dbt's
    # output and, on a connection error, point at the real fix.
    text = dag_path.read_text()
    assert "capture_output=True" in text, "gate must capture dbt output to diagnose the failure"
    assert "astro dev restart" in text, "gate must hint the cold-start fix on a connection error"
    assert "http_path" in text, "gate must detect the missing-config (connection) failure mode"


def test_compose_forwards_dbt_schema_and_catalog() -> None:
    # Why: the astro containers resolve the trainee's schema from DBT_SCHEMA/DBT_CATALOG.
    # docker-compose.override.yml must forward them into the containers, or Cosmos and the
    # freshness gate build into the wrong schema (training_student) instead of the
    # trainee's training_<user>.
    text = (repo_root() / "docker-compose.override.yml").read_text()
    assert "DBT_SCHEMA:" in text
    assert "DBT_CATALOG:" in text


@pytest.mark.parametrize("dag_path", _DAGS)
def test_cosmos_reads_profile_via_profiles_yml_filepath(dag_path) -> None:
    # Why: Cosmos reads the repo dbt profile directly via
    # ProfileConfig(profiles_yml_filepath=...) rather than a profile *mapping*. The mapping
    # variants do a BaseHook.get_connection lookup at task-execution time, which
    # intermittently failed to resolve databricks_default during Airflow-3 local
    # `astro dev run dags test`; reading profiles.yml (target=dev, token auth) avoids that.
    # The OAuth M2M mapping (DatabricksOauthProfileMapping) is also wrong here (needs
    # client_id/secret the local connection lacks), so neither profile mapping may reappear.
    text = dag_path.read_text()
    assert "profiles_yml_filepath" in text
    assert "DatabricksTokenProfileMapping" not in text
    assert "DatabricksOauthProfileMapping" not in text


def test_guide_uses_astro_dev_run_not_bare_airflow() -> None:
    # Why: Airflow runs inside the astro containers, so bare `airflow ...` commands are
    # not on the devcontainer PATH — the guide must invoke them via `astro dev run ...`.
    # And `mise run challenge:dbt 03 -- show --inline "<SQL>"` breaks (mise word-splits the
    # multi-word SQL), so the guide uses `show --select <model>` for the parity preview.
    text = (CH / "README.md").read_text()
    assert "--inline" not in text
    assert "airflow dags " not in text
    assert "airflow tasks " not in text


def test_guide_teaches_profiles_yml_filepath() -> None:
    # Why: the guide must teach the same Cosmos wiring the DAG actually uses. The shipped
    # DAG reads the dbt profile via profiles_yml_filepath (not a profile mapping), so §5's
    # prose and code snippets must match — teaching DatabricksTokenProfileMapping or
    # DatabricksOauthProfileMapping would contradict the stub/solution the trainee opens.
    text = (CH / "README.md").read_text()
    assert "profiles_yml_filepath" in text
    assert "DatabricksTokenProfileMapping" not in text
    assert "DatabricksOauthProfileMapping" not in text


def test_guide_phase2_checks_are_runnable() -> None:
    # Why: the trainee's default `python` (.venv) lacks pytest and PyYAML (deps install
    # --system into /opt/venv), so `python -m pytest` and `python -c "import yaml"` fail.
    # The guide must use bare `pytest` (resolves to /opt/venv/bin/pytest) and yaml-free
    # checks so Phase 2's verification commands actually run for a trainee.
    text = (CH / "README.md").read_text()
    assert "python -m pytest" not in text
    assert "import yaml" not in text


@pytest.mark.parametrize(
    "test_path",
    [
        PA / "tests" / "test_dag_structure.py",
        CH / "stubs" / "tests" / "test_dag_structure.py",
        CH / "solution" / "tests" / "test_dag_structure.py",
    ],
)
def test_structural_test_is_static_and_checks_callbacks_sla(test_path) -> None:
    # Why: Airflow lives only in the astro containers, so the trainee-runnable structural
    # test (Ch8) must be static — no DagBag/airflow import — so it runs with a plain
    # `pytest`. It must check the tiered callbacks + 90-minute SLA (pre-wired in the stub,
    # so it passes on the shipped stub AND the solution, keeping CI green); the wiring
    # chain is the learner gate in verify.sh. All three copies stay identical.
    text = test_path.read_text()
    assert "DagBag(" not in text
    assert "import airflow" not in text and "from airflow" not in text
    assert "on_failure_callback" in text and "on_sla_miss_callback" in text
    assert "minutes=90" in text


def test_guide_does_not_teach_vacuous_astro_dev_parse() -> None:
    # Why: `astro dev parse` mounts only include/tests/plugins/.astro — NOT
    # data_products/ where the DAGs live — so it finds 0 DAGs and passes
    # vacuously ("1 skipped"), teaching nothing. Step 2 uses a real static
    # `ast.parse`; sections 4/5 run the task in the live scheduler. The guide
    # must not prefix those checks with the vacuous command.
    text = (CH / "README.md").read_text()
    assert "astro dev parse" not in text


def test_guide_boots_stack_before_section_4() -> None:
    # Why: sections 4 and 5 check with `astro dev run tasks test/list`, which
    # exec into the RUNNING scheduler. The guide only started the stack in a
    # later section, so a trainee following it linearly reached sections 4/5
    # with a stopped stack -> exit 1, empty output, dead end. `astro dev start`
    # must appear in the Prerequisites, before section 1.
    text = (CH / "README.md").read_text()
    prereqs = text.split("### Prerequisites", 1)[1].split("### 1.", 1)[0]
    assert "astro dev start" in prereqs
    # Why: starting the stack before `setup:databricks` finishes captures an empty
    # Databricks env (the failure the trainee actually hit mid-startup). The guide must
    # tell them to restart to recover, or they chase a phantom "stale feed".
    assert "astro dev restart" in prereqs


def test_ch03_guide_uses_raw_dbt_for_peeks() -> None:
    # Why: challenge 03 is an Airflow challenge, but every dbt command it shows -- the
    # read-only peeks (debug, show, source freshness) AND the cross-challenge raw-feed
    # provisioning -- is raw dbt, run from the relevant dbt project. Only the verify gate
    # and reset stay on mise. The seed step used to be `mise run challenge:seed 02`; that
    # was the one place a guide still ran dbt through the wrapper, which contradicted the
    # "challenges teach real dbt" rule the other guides follow.
    text = (CH / "README.md").read_text()
    assert "mise run challenge:dbt 03" not in text
    assert "dbt debug" in text
    assert "dbt source freshness" in text
    assert "cd challenges/v1/02-dbt-pipeline/dbt && dbt seed" in text
    assert "mise run challenge:verify 03" in text
    assert "mise run challenge:reset 03" in text
    # Interleaved peeks sit next to `astro dev run` (run from the repo root), so they
    # must be self-contained subshells that cd into the dbt project — otherwise bare
    # dbt fails to find dbt_project.yml from the repo root.
    assert "cd data_products/portfolio_analytics/dbt && dbt show --select fct_portfolio_returns" in text
    assert "cd data_products/portfolio_analytics/dbt && dbt source freshness" in text
