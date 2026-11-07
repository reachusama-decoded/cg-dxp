from __future__ import annotations

import os
import subprocess
import tomllib

import yaml

from tests.challenges.conftest import repo_root

CH = repo_root() / "challenges" / "v1" / "02-dbt-pipeline"

RAW_SOURCE_SEEDS = (
    "holdings_raw",
    "positions_raw",
    "prices_raw",
    "refdata_raw",
    "fx_rates_raw",
    "fund_master_raw",
)


def test_challenge_02_ships_raw_source_seeds() -> None:
    # Why: the six raw sources are provisioned as seeds in the trainee's own
    # schema; they must exist in both the working tree and the stubs mirror so
    # `challenge:reset` preserves them.
    for name in RAW_SOURCE_SEEDS:
        assert (CH / "dbt" / "seeds" / f"{name}.csv").exists(), name
        assert (CH / "stubs" / "seeds" / f"{name}.csv").exists(), name


def test_challenge_02_sources_pin_target_schema() -> None:
    # Why: with no schema override, source('custodian','holdings_raw') resolves to
    # <catalog>.custodian.holdings_raw (schema = source name). Pinning to the dbt
    # target makes it resolve to the schema where the seed lands.
    text = (CH / "dbt" / "models" / "sources.yml").read_text()
    assert text.count('database: "{{ target.database }}"') >= 4
    assert text.count('schema: "{{ target.schema }}"') >= 4


def test_dbt_project_and_solution_present() -> None:
    assert (CH / "dbt" / "dbt_project.yml").exists()
    assert any((CH / "solution" / "models").glob("**/*.sql"))
    assert (CH / "dbt_profiles" / "profiles.yml").exists()

def test_profile_uses_shared_env_contract() -> None:
    prof = yaml.safe_load((CH / "dbt_profiles" / "profiles.yml").read_text())
    out = next(iter(prof.values()))["outputs"]["local"]
    assert "DBT_ACCESS_TOKEN" in str(out) or "DATABRICKS_TOKEN" in str(out)
    assert "training_dev" in str(out)  # app_catalog default

def test_no_preflight_run_md_or_own_devcontainer() -> None:
    assert not (CH / "RUN.md").exists()
    assert not (CH / ".devcontainer").exists()

def test_verify_fails_fast_for_missing_models_dir() -> None:
    env = {**os.environ, "DBT_MODELS_DIR": str(CH / "solution" / "models" / "missing")}
    r = subprocess.run(["bash", "verify.sh"], cwd=CH, capture_output=True, text=True, env=env)
    assert r.returncode == 4
    assert "DBT_MODELS_DIR not found" in (r.stdout + r.stderr)


def test_verify_fails_fast_for_missing_tests_dir() -> None:
    env = {**os.environ, "DBT_TESTS_DIR": str(CH / "solution" / "tests" / "missing")}
    r = subprocess.run(
        ["bash", "verify.sh"],
        cwd=CH,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert r.returncode == 4
    assert "DBT_TESTS_DIR not found" in (r.stdout + r.stderr)


def test_working_models_are_stubs_but_solution_is_solved() -> None:
    work = (CH / "dbt" / "models" / "staging" / "stg_holdings.sql").read_text()
    soln = (CH / "solution" / "models" / "staging" / "stg_holdings.sql").read_text()
    assert "select 1 as placeholder" in work.lower()
    assert "TODO" in work
    assert "select 1 as placeholder" not in soln.lower()


def test_stub_mirror_matches_working_tree() -> None:
    assert (CH / "stubs" / "models" / "staging" / "stg_holdings.sql").exists()


def test_reset_restores_into_dbt_project_dir() -> None:
    # Why: challenge 02's dbt project lives at CH/dbt/ and its stubs mirror the dbt/
    # contents, so the generic reset must copy stubs into dbt/ — not the challenge root,
    # which would strand dbt_project.yml/models at CH/ and never re-blank CH/dbt/models.
    toml = (repo_root() / ".mise.toml").read_text()
    assert 'cp -R "$DIR/stubs/." "$DIR/dbt/"' in toml
    assert (CH / "stubs" / "dbt_project.yml").exists()


def _reset_task_script() -> str:
    with (repo_root() / ".mise.toml").open("rb") as fh:
        return tomllib.load(fh)["tasks"]["challenge:reset"]["run"]


def test_reset_removes_files_the_trainee_creates_from_scratch(tmp_path) -> None:
    # Why: `cp -R stubs/.` only overwrites paths the stub tree ships, so the three files a
    # trainee CREATES (models/staging/schema.yml in S8, plus the C10 capstone mart and its
    # reconcile test) survived `challenge:reset` and left a previous answer behind — the
    # reset silently did not reset. The prune must delete exactly the solution-minus-stubs
    # difference and must not touch generated (target/, logs/) or provisioned (profiles.yml)
    # files that legitimately have no stub counterpart.
    ch = tmp_path / "challenges" / "v1" / "02-dbt-pipeline"
    for rel, body in (
        ("stubs/models/staging/stg_holdings.sql", "select 1 as placeholder"),
        ("solution/models/staging/stg_holdings.sql", "select real_sql"),
        ("solution/models/staging/schema.yml", "version: 2"),
        ("solution/models/marts/agg_fund_daily_exposure.sql", "select real_sql"),
        ("solution/tests/reconcile_daily_exposure.sql", "select real_sql"),
        # The trainee's working tree: authored answers plus files reset must preserve.
        ("dbt/models/staging/stg_holdings.sql", "my authored answer"),
        ("dbt/models/staging/schema.yml", "my authored answer"),
        ("dbt/models/marts/agg_fund_daily_exposure.sql", "my authored answer"),
        ("dbt/tests/reconcile_daily_exposure.sql", "my authored answer"),
        ("dbt/profiles.yml", "provisioned, not a stub"),
        ("dbt/target/run_results.json", "{}"),
    ):
        path = ch / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)

    script = f"usage_challenge=02\n{_reset_task_script()}"
    r = subprocess.run(["bash", "-c", script], cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr

    for created in (
        "dbt/models/staging/schema.yml",
        "dbt/models/marts/agg_fund_daily_exposure.sql",
        "dbt/tests/reconcile_daily_exposure.sql",
    ):
        assert not (ch / created).exists(), f"reset left the trainee-created {created} in place"
    assert (ch / "dbt/models/staging/stg_holdings.sql").read_text() == "select 1 as placeholder"
    assert (ch / "dbt/profiles.yml").exists(), "reset must not delete provisioned config"
    assert (ch / "dbt/target/run_results.json").exists(), "reset must not delete generated output"


def test_stubs_contain_no_stray_sql_after_the_placeholder() -> None:
    # Why: two stubs (int_holdings_enriched, fct_portfolio_returns) shipped with the tail
    # of their solution SQL left dangling after `select 1 as placeholder` -- a botched
    # find-replace. The guide promises the skeleton "still parses", but `dbt build` on a
    # fresh clone died with a Databricks SQL syntax error pointing at a placeholder file.
    # A stub must be exactly its TODO comment plus the placeholder select, nothing else.
    for base in (CH / "dbt" / "models", CH / "stubs" / "models"):
        for sql in base.rglob("*.sql"):
            lines = [ln for ln in sql.read_text().splitlines() if ln.strip()]
            placeholder_idx = next(
                (i for i, ln in enumerate(lines) if "select 1 as placeholder" in ln.lower()),
                None,
            )
            if placeholder_idx is None:
                continue
            trailing = lines[placeholder_idx + 1 :]
            assert not trailing, (
                f"{sql.relative_to(repo_root())} has stray SQL after the placeholder: {trailing}"
            )


def test_guide_never_pairs_inline_sql_with_the_mise_wrapper() -> None:
    # Why: `mise run challenge:dbt 02 -- show --inline "<multi-word SQL>"` passes the SQL
    # through a mise variadic that word-splits on spaces (and `select *` glob-expands to
    # the repo file listing), so every --inline peek errors:
    #   UsageError("Got unexpected extra arguments (1 as a, 2 as b')")
    # Raw `dbt show --inline "..."` has no such wrapper in the way and quotes correctly,
    # so the guide (converted to raw dbt) may use --inline freely -- it just must never
    # route --inline through `mise run challenge:dbt`.
    text = (CH / "README.md").read_text()
    for line in text.splitlines():
        if "--inline" in line:
            assert "challenge:dbt" not in line, (
                f"--inline must not be routed through the mise wrapper: {line}"
            )


def test_guide_uses_challenge_project_namespace() -> None:
    # Why: this dbt project is named portfolio_analytics_challenge, not
    # portfolio_analytics. A models:/seeds: block keyed on the bare `portfolio_analytics:`
    # name is silently ignored by dbt, so the guide's config snippets must use the
    # challenge namespace or they teach a config that does nothing.
    assert "\n  portfolio_analytics:\n" not in (CH / "README.md").read_text()


def test_dbt_project_ships_models_and_seed_config_in_dbt_and_stubs() -> None:
    # Why: the guide relies on folder-level config — +tags (S5 `tag:staging`),
    # +materialized (S6 view/table), the marts OPTIMIZE ZORDER post-hook (C9), and the
    # seed post-hook that refreshes _extracted_at so `source freshness` (S3) passes. It
    # must ship in BOTH dbt/ and stubs/, or `challenge:reset` downgrades the project and
    # freshness breaks. The two copies must be byte-identical.
    dbt_text = (CH / "dbt" / "dbt_project.yml").read_text()
    stub_text = (CH / "stubs" / "dbt_project.yml").read_text()
    assert dbt_text == stub_text, "dbt/ and stubs/ dbt_project.yml must match (reset safety)"
    assert "+tags:" in dbt_text and '"staging"' in dbt_text and '"marts"' in dbt_text
    assert "+materialized: table" in dbt_text and "+materialized: view" in dbt_text
    assert "OPTIMIZE {{ this }} ZORDER BY (fund_id, position_date)" in dbt_text
    assert "set _extracted_at = current_timestamp()" in dbt_text
    assert "portfolio_analytics_challenge:" in dbt_text


def test_marts_schema_ships_without_capstone() -> None:
    # Why: guide C5 says the marts' schema.yml "ships with the test declarations already
    # in place — read it and run it", so it exists in dbt/ + stubs/ with the fct + agg
    # tests. The capstone mart's tests are ADDED by the trainee in C10, so the shipped
    # schema must NOT already test agg_fund_daily_exposure — that would fail C7's full
    # build while the capstone is still a stub. The solution copy carries all three.
    for base in (CH / "dbt", CH / "stubs"):
        text = (base / "models" / "marts" / "schema.yml").read_text()
        assert "fct_portfolio_returns" in text and "agg_fund_exposure" in text
        assert "- name: agg_fund_daily_exposure" not in text
    assert "- name: agg_fund_daily_exposure" in (CH / "solution" / "models" / "marts" / "schema.yml").read_text()


def test_staging_schema_is_authored_solution_only() -> None:
    # Why: S8 is an authoring task ("Create dbt/models/staging/schema.yml"), so the file
    # must NOT ship in dbt/ or stubs/, and the solution must carry the reference.
    assert not (CH / "dbt" / "models" / "staging" / "schema.yml").exists()
    assert not (CH / "stubs" / "models" / "staging" / "schema.yml").exists()
    assert (CH / "solution" / "models" / "staging" / "schema.yml").exists()


def test_capstone_is_created_in_c10_not_shipped() -> None:
    # Why: C10 says "Create" the capstone mart + its reconcile test, and S2 counts ten
    # models. Shipping them as stubs makes eleven models and breaks C7's full build (the
    # placeholder capstone cannot run the marts OPTIMIZE ZORDER, and the pre-solved
    # reconcile test references columns the placeholder lacks). They live in solution/ only.
    for base in (CH / "dbt", CH / "stubs"):
        assert not (base / "models" / "marts" / "agg_fund_daily_exposure.sql").exists()
        assert not (base / "tests" / "reconcile_daily_exposure.sql").exists()
    assert (CH / "solution" / "models" / "marts" / "agg_fund_daily_exposure.sql").exists()
    assert (CH / "solution" / "tests" / "reconcile_daily_exposure.sql").exists()


def test_assert_nav_ships_as_stub_solution_is_real() -> None:
    # Why: C6 says "Complete dbt/tests/assert_nav_within_tolerance.sql", so it ships as a
    # failing placeholder the trainee completes; the solution holds the real reconciliation.
    for base in (CH / "dbt", CH / "stubs"):
        stub = (base / "tests" / "assert_nav_within_tolerance.sql").read_text()
        assert "select 1 as placeholder" in stub.lower() and "TODO" in stub
    soln = (CH / "solution" / "tests" / "assert_nav_within_tolerance.sql").read_text()
    assert "select 1 as placeholder" not in soln.lower()


def test_solution_models_override_also_overlays_sibling_tests() -> None:
    # The retained solution spans solution/models and solution/tests. Pointing the
    # verifier at solution/models must replace the learner's failing singular-test
    # stub and add the capstone reconciliation test in the isolated project copy.
    script = (CH / "verify.sh").read_text()
    assert 'ALTERNATE_TESTS_DIR="$(dirname "$DBT_MODELS_DIR")/tests"' in script
    assert 'cp -R "${DBT_TESTS_DIR}/." "$TMP_PROJECT/tests/"' in script
    assert (CH / "solution" / "tests" / "assert_nav_within_tolerance.sql").exists()
    assert (CH / "solution" / "tests" / "reconcile_daily_exposure.sql").exists()


def test_ch02_profiles_discoverable_in_project_dir() -> None:
    # Why: trainees cd into dbt/ and run bare `dbt build`; dbt resolves profiles.yml
    # from the current directory. A real profiles.yml copy in the project dir enables
    # that, while dbt_profiles/profiles.yml stays in place for verify.sh and the
    # existing tests. It must NOT be a symlink -- see test_no_tracked_symlinks.
    proj = CH / "dbt" / "profiles.yml"
    canonical = CH / "dbt_profiles" / "profiles.yml"
    assert proj.exists(), "challenges/v1/02-dbt-pipeline/dbt/profiles.yml must exist"
    assert not proj.is_symlink(), "must be a real file, not a symlink (breaks Windows clones)"
    assert proj.read_text() == canonical.read_text(), "project-dir profiles.yml must match dbt_profiles/profiles.yml"


def test_ch02_guide_uses_raw_dbt_not_mise_wrapper() -> None:
    # Why: the challenge teaches real dbt, so the guide's dbt/seed commands are raw
    # `dbt ...`, not the mise wrapper. The verify gate and reset stay on mise.
    text = (CH / "README.md").read_text()
    assert "mise run challenge:dbt" not in text
    assert "mise run challenge:seed" not in text
    assert "dbt debug" in text and "dbt seed" in text and "dbt build" in text
    assert "mise run challenge:verify 02" in text
    assert "mise run challenge:reset 02" in text


def test_ch02_guide_matches_source_and_solution_layout() -> None:
    text = (CH / "README.md").read_text()
    assert "`solution/models/` and `solution/tests/`" in text
    assert "The modeled pipeline reads five of them" in text
    assert "loads all eight CSV seeds" in text
    assert "`dbt/models/sources.yml`" in text
    assert "solution/models/sources.yml" not in text
