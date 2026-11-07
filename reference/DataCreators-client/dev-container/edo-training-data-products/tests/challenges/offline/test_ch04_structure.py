from __future__ import annotations

import subprocess

from tests.challenges.conftest import repo_root

AE = repo_root() / "data_products" / "atlas_elt"
CH = repo_root() / "challenges" / "v1" / "04-atlas-capstone"
ENTITIES = ["advisors", "clients", "funds", "fund_holdings", "instruments", "portfolios", "trades"]
MARTS = ["fund_nav", "portfolio_perf", "market_daily", "segment_aum"]


def test_product_shell_present() -> None:
    for f in ("dbt_project.yml", "databricks.yml", "dbt_profiles/profiles.yml", "datasets/sources.yml"):
        assert (AE / f).exists(), f


def test_entity_and_mart_datasets_have_paved_path_set() -> None:
    for name in ENTITIES + MARTS:
        d = AE / "datasets" / name
        for sub in ("dbt", "bundle", "airflow", "contract", "runtime"):
            assert (d / sub).exists(), f"{name}/{sub}"


def test_mapping_doc_lists_layers() -> None:
    readme = (AE / "README.md").read_text()
    for token in ("staging", "integration", "prepared"):
        assert token in readme


def test_models_placed_by_refinement_role() -> None:
    # a source-aligned model lands in a dataset's staging layer; a mart in prepared.
    assert (AE / "datasets" / "trades" / "dbt" / "staging").exists()
    marts = list((AE / "datasets").glob("*/dbt/prepared/*.sql"))
    assert marts, "at least one consumer mart must live in a dataset's prepared/ layer"


def test_working_models_are_stubs() -> None:
    any_stub = list((AE / "datasets").glob("*/dbt/**/*.sql"))
    assert any_stub and any("select 1 as placeholder" in p.read_text().lower() for p in any_stub)


def test_contracts_ship_as_spec_files_only() -> None:
    contracts = list((AE / "datasets").glob("*/contract/*.odcs.yaml"))
    assert contracts  # spec files present; no contract:migrate anywhere in challenge steps


def test_atlas_dbt_project_defines_alignment_tags() -> None:
    # Why: the guide's whole build flow uses `dbt run --select tag:source-aligned|
    # domain-aligned|consumer-aligned`. Those tags are applied folder-level in
    # dbt_project.yml so trainee-authored SQL inherits them. The port shipped a minimal
    # models: block with NO tags, so every tag selector matched 0 nodes and the entire
    # Phase 1 -> Phase 2 build cascaded into TABLE_OR_VIEW_NOT_FOUND. Guard the tags.
    text = (AE / "dbt_project.yml").read_text()
    for tag in ("source-aligned", "domain-aligned", "consumer-aligned"):
        assert f'+tags: ["{tag}"]' in text, f"missing {tag} tag in dbt_project.yml"


def test_ch04_guide_avoids_inline_sql() -> None:
    # Why: `mise run challenge:dbt 04 -- show --inline "<SQL>"` word-splits under mise (and
    # `select *` glob-expands to the repo listing), so the §4/§6 peeks errored with "Got
    # unexpected extra arguments". That is a property of the WRAPPER, not of --inline: the
    # guide now uses raw `dbt`, which quotes correctly, so --inline is allowed here for the
    # same reason it is allowed in challenge 02 (see
    # test_guide_never_pairs_inline_sql_with_the_mise_wrapper). It is needed for at least one
    # real case: `dbt show --select <seed>` rebuilds the seed and ignores --limit, so
    # previewing a few rows of a seed requires querying the relation inline.
    text = (CH / "README.md").read_text()
    for line in text.splitlines():
        if "--inline" in line:
            assert "challenge:dbt" not in line, (
                f"--inline must not be routed through the mise wrapper: {line}"
            )


def test_ch04_verify_bundle_validate_is_non_fatal() -> None:
    # Why: `databricks bundle validate` shells to Terraform, which fails with "openpgp: key
    # expired" in a future-dated sandbox — environmental, not a challenge defect. Under
    # `set -e` that aborted the whole verify gate before the dbt parse/compile pass. It must
    # be non-fatal so `mise run challenge:verify 04` still gates on dbt.
    text = (CH / "verify.sh").read_text()
    assert "databricks bundle validate" in text
    assert "not a challenge defect. Continuing." in text


def test_ch04_guide_verifies_only_via_mise() -> None:
    # Why: verify.sh runs dbt with `--target local`, whose Databricks token is exported by
    # `.mise/env.sh`. That file is sourced only by mise (the interactive prompt hook or a
    # `mise run` task), so a bare `bash challenges/v1/04-atlas-capstone/verify.sh` has an empty
    # DBT_ACCESS_TOKEN and dbt-databricks falls back to OAuth: "auth_type: oauth is required
    # when not using access token". `mise run challenge:verify 04` loads the env and passes.
    # ch02/ch03 verify only through `mise run challenge:verify NN`; keep ch04 aligned so a
    # fresh-clone trainee is never told to run the script standalone.
    text = (CH / "README.md").read_text()
    assert "bash verify.sh" not in text
    assert "bash challenges/v1/04-atlas-capstone/verify.sh" not in text
    assert "mise run challenge:verify 04" in text


def test_ch04_profiles_discoverable_in_project_dir() -> None:
    # Why: trainees cd into data_products/atlas_elt and run bare `dbt build`; dbt
    # resolves profiles.yml from the current directory. A real profiles.yml copy in
    # the project dir enables that; dbt_profiles/profiles.yml stays for verify.sh,
    # the bundle, and mise run dbt:*. It must NOT be a symlink -- see
    # test_no_tracked_symlinks.
    proj = AE / "profiles.yml"
    canonical = AE / "dbt_profiles" / "profiles.yml"
    assert proj.exists(), "data_products/atlas_elt/profiles.yml must exist"
    assert not proj.is_symlink(), "must be a real file, not a symlink (breaks Windows clones)"
    assert proj.read_text() == canonical.read_text(), "project-dir profiles.yml must match dbt_profiles/profiles.yml"


def test_ch04_guide_uses_raw_dbt_and_deps() -> None:
    # Why: the capstone teaches real dbt; the guide runs raw dbt from the project dir
    # and installs the local 'shared' package with `dbt deps`. The verify gate and
    # reset stay on mise.
    text = (CH / "README.md").read_text()
    assert "mise run challenge:dbt" not in text
    assert "mise run challenge:seed" not in text
    assert "dbt deps" in text
    assert "dbt build" in text
    assert "mise run challenge:verify 04" in text
    assert "mise run challenge:reset 04" in text


def test_ch04_guide_has_safe_learner_flow() -> None:
    text = (CH / "README.md").read_text()
    assert "<!--" not in text, "inline review comments must be resolved, not shipped"
    assert "Edit files only under `data_products/atlas_elt/`" in text
    assert "Do not edit `challenges/v1/04-atlas-capstone/stubs/`" in text
    assert "Run from the repository root" in text
    assert "Run from `data_products/atlas_elt`" in text


def test_ch04_guide_includes_airflow_catalyst_and_business_outcome() -> None:
    text = (CH / "README.md").read_text()
    assert "astro dev start" in text
    assert "astro dev run dags list-import-errors" in text
    assert "dbt best practices" in text.lower()
    assert "## Use the product" in text
    assert "intended consumer" in text.lower()


def test_ch04_verifier_distinguishes_offline_and_live_success() -> None:
    text = (CH / "verify.sh").read_text()
    assert "OFFLINE PASS" in text
    assert "Databricks models and tests were not run" in text
    assert "ATLAS_VERIFY_SCOPE" in text
    assert "MVP LIVE PASS" in text
    assert "Atlas ELT Phase 1 MVP complete" in text
    assert "LIVE PASS" in text
    assert "Atlas ELT capstone complete" in text
    assert 'ATLAS_DEPLOY_BUNDLE:-0' in text


def test_ch04_guide_exposes_mvp_gate_and_phase2_dependencies() -> None:
    text = (CH / "README.md").read_text()
    assert "## Complete Phase 1" in text
    assert "ATLAS_VERIFY_SCOPE=mvp" in text
    phase2 = text[text.index("## 🚀 Phase 2"):text.index("### Challenge 1:")]
    assert "### Phase 2 dependency map" in phase2
    assert "Challenge 14" in phase2
    assert "Challenge 2" in phase2
    assert "Challenge 9" in phase2


def test_ch04_guide_frames_the_mixed_audience_and_workshop_day() -> None:
    text = (CH / "README.md").read_text()
    lower = text.lower()
    assert "hackathon" not in lower
    assert "## Purpose" in text
    assert "## Learning Outcomes" in text
    assert "## Who This Is For" in text
    for audience in ("non-technical learners", "technical managers", "data engineers"):
        assert audience in lower
    assert "certify attendees as **Data Creators**" in text
    assert "AI Catalyst, dbt, Databricks, Airflow" in text
    assert "operational hand-offs" in text
    for time_marker in ("09:00", "12:00–13:00", "14:30", "15:00"):
        assert time_marker in text
    assert "Take short breaks whenever you need them" in text
    assert "nominate one person to present" in text
    assert "choose a handful from the nominated presenters" in text


def test_ch04_guide_uses_flexible_phase_guidance_not_section_estimates() -> None:
    text = (CH / "README.md").read_text()
    assert "## 🎯 Phase 1: Baseline for Every Team" in text
    assert "**1–3 hours**" in text
    assert "about one hour" in text
    assert "reference point rather than a deadline" in text
    assert "## 🚀 Phase 2: Advanced Technical Extensions" in text
    assert "3+ hours" in text
    assert "You are not expected to finish all 14" in text
    assert "### Time budget" not in text
    assert "Approx. time" not in text
    assert "~10 min per challenge" not in text
    assert "~45–60 min" not in text


def test_ch04_learning_outcomes_cover_design_handoff_and_communication() -> None:
    text = (CH / "README.md").read_text()
    outcomes = text[text.index("## Learning Outcomes"):text.index("## Who This Is For")]
    for competency in ("keys", "joins", "operational", "hand-off", "next steps"):
        assert competency in outcomes


def test_ch04_guided_setup_does_not_repeat_the_learning_journey() -> None:
    text = (CH / "README.md").read_text()
    setup = text[
        text.index("## Prepare the Guided Atlas Environment"):
        text.index("## Understand the data")
    ]
    assert "If you chose the guided path, you will:" not in setup
    assert "Optionally extend the product" not in setup
    assert "complete these readiness checks before starting Phase 1" in setup
    assert "**Before you begin**" not in text


def test_ch04_phase_boundaries_have_closing_rules() -> None:
    text = (CH / "README.md").read_text()
    phase1_intro = text[
        text.index("## 🎯 Phase 1: Baseline for Every Team"):
        text.index("### 1. Inspect the source data")
    ]
    phase2_intro = text[
        text.index("## 🚀 Phase 2: Advanced Technical Extensions"):
        text.index("### Phase 2 dependency map")
    ]
    assert phase1_intro.rstrip().endswith("---")
    assert phase2_intro.rstrip().endswith("---")


def test_ch04_opening_team_activity_is_consumer_backwards_and_inclusive() -> None:
    text = (CH / "README.md").read_text()
    activity_start = text.index("## Atlas Product Discovery and Reverse-Mapping")
    phase1_start = text.index("## 🎯 Phase 1: Baseline for Every Team")
    activity = text[activity_start:phase1_start]
    assert activity_start < phase1_start
    for role in ("producers", "Data Creator", "consumers"):
        assert role in activity
    for source in (
        "`trades`",
        "`instruments`",
        "`portfolios`",
        "`clients`",
        "`advisors`",
        "`funds`",
        "`fund_holdings`",
    ):
        assert source in activity
    for output in (
        "`rpt_portfolio_summary`",
        "`rpt_advisor_book`",
        "`agg_segment_aum`",
        "`ts_daily_market`",
        "`agg_instrument_activity`",
        "`agg_fund_nav`",
        "`api_latest_price`",
    ):
        assert output in activity
    assert "two business-facing outputs" in activity
    assert "work backwards from consumer need" in activity
    assert "Producer–Creator–Consumer map" in activity
    assert "Consumer-backwards map" in activity
    assert "Mini-STTM" in activity
    assert "Shared glossary and trust questions" in activity
    assert "Transformation in plain English" in activity
    assert "Do not write implementation SQL yet" in activity
    assert "design a database schema" in activity


def test_ch04_opening_activity_roles_and_transition_are_clear() -> None:
    text = (CH / "README.md").read_text()
    activity = text[
        text.index("## Atlas Product Discovery and Reverse-Mapping"):
        text.index("## Choose Your Capstone Path")
    ]
    normalized = " ".join(activity.split())
    for role in ("facilitator", "scribe", "quality challenger", "playback spokesperson"):
        assert role in activity
    assert "Combine roles in smaller teams" in normalized
    assert "30–60 minute discovery timebox" in normalized
    assert "facilitation guides, not completion targets" in normalized
    assert "working hypothesis" in normalized
    assert "Phase 1 tests" in normalized
    assert "Phase 2 lets technical learners extend" in normalized
    assert "final presentation" in normalized


def test_ch04_guide_offers_a_guarded_advanced_own_product_path() -> None:
    text = (CH / "README.md").read_text()
    advanced = text[
        text.index("### 🚀 Advanced Path: Build Your Own Paved-Path Data Product"):
        text.index("## Prepare the Guided Atlas Environment")
    ]
    normalized = " ".join(advanced.split())
    assert "already working in-role as Data Creators" in normalized
    assert "skip the individual guided Atlas implementation" in normalized
    for technology in ("AI Catalyst", "dbt", "Databricks", "Airflow"):
        assert technology in advanced
    assert "evidence equivalent to the Phase 1 baseline" in normalized
    assert "approved or synthetic source data" in normalized
    assert "Do not use sensitive data or deploy to production" in normalized


def test_ch04_appendix_hides_a_complete_opening_activity_example() -> None:
    text = (CH / "README.md").read_text()
    appendix_start = text.index("## Appendix: Quick Reference and Opening Team Activity Example")
    glossary_start = text.index("## Glossary", appendix_start)
    appendix = text[appendix_start:glossary_start]
    assert "<details><summary>Example solution: Atlas Product Discovery and Reverse-Mapping</summary>" in appendix
    assert appendix.strip().endswith("---")
    assert "</details>" in appendix
    for section in (
        "### Producer–Creator–Consumer Map",
        "### Consumer-Backwards Map",
        "### Mini-STTM",
        "### Shared Glossary",
        "### Trust Questions and Assumptions",
    ):
        assert section in appendix
    assert "This is one reasonable response, not the only correct design" in appendix
    assert "FX conversion" in appendix


def test_ch04_appendix_puts_devcontainer_help_before_the_hidden_solution() -> None:
    text = (CH / "README.md").read_text()
    appendix_start = text.index("## Appendix: Quick Reference and Opening Team Activity Example")
    help_start = text.index("### Working in the Devcontainer", appendix_start)
    solution_start = text.index(
        "<details><summary>Example solution: Atlas Product Discovery and Reverse-Mapping</summary>",
        appendix_start,
    )
    assert appendix_start < help_start < solution_start
    help_text = text[help_start:solution_start]
    assert "inside the VS Code devcontainer" in help_text
    assert "| Command type | Directory |" in help_text
    for command in (
        "dbt debug",
        "dbt ls --resource-type model",
        "dbt build --select +rpt_portfolio_summary --indirect-selection=cautious",
        "astro dev run dags list-import-errors",
        "mise run challenge:verify 04",
        "git status --short",
    ):
        assert command in help_text


def test_ch04_appendix_separates_safe_and_destructive_commands() -> None:
    text = (CH / "README.md").read_text()
    help_text = text[
        text.index("### Working in the Devcontainer"):
        text.index("### Opening Team Activity Example")
    ]
    assert "# Non-destructive instructor overview" in help_text
    assert "# MAINTAINERS ONLY: destructive to learner work" in help_text
    assert "deletes your authored challenge files" in help_text
    assert "does not delete tables or views" in help_text
    assert "Never paste access tokens" in help_text
    assert "do not assume it uses port 8080" in help_text


def test_agentic_capstone_check_is_safe_and_reusable() -> None:
    prompt = repo_root() / "challenges" / "v1" / "00-environment-check" / "AGENTIC_CAPSTONE_CHECK.md"
    assert prompt.exists()
    text = prompt.read_text()
    assert "isolated" in text.lower()
    assert "challenge-trainee-runs" in text
    assert "docs/challenge-run-brief.md" in text
    assert "one challenge at a time" in text.lower()
    assert "do not work around" in text.lower()
    assert "challenge-runs.md" in text


def test_ch04_from_scratch_runner_dry_run_validates_manifests() -> None:
    runner = CH / "verify.sh"
    result = subprocess.run(
        ["bash", str(runner), "--dry-run"],
        cwd=repo_root(),
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PHASE1_SOURCE_FILES: 7" in result.stdout
    assert "PHASE1_DOMAIN_FILES: 9" in result.stdout
    assert "PHASE1_CONSUMER_FILES: 7" in result.stdout
    assert "Phase 2: challenges 1-14" in result.stdout
    assert "DRY-RUN PASS" in result.stdout


def test_ch04_from_scratch_runner_preserves_evidence_and_resets_state() -> None:
    text = (CH / "verify.sh").read_text()
    assert 'VERIFY_ROOT="$REPO_ROOT/.devcontainer/verify/04-atlas-capstone"' in text
    assert "challenge 04 verification logs survive challenge:reset" in text
    assert text.count("mise run challenge:reset 04") >= 2
    assert "sha256sum -c" in text
    assert '[[ -e "$path" ]] || continue' in text
    assert "capture_dbt_audit" in text
    assert "astro dev stop" in text
    assert "astro dev run dags details atlas_elt_advisors" in text
    assert "astro dev run tasks list" not in text
    assert "interactions.tsv" in text
    assert "PROMPT-VALIDATED" in text
    assert "trap on_exit EXIT" in text
    assert "FROM-SCRATCH PASS" in text
    assert ".devcontainer/verify/" in (repo_root() / ".gitignore").read_text()


def test_ch04_from_scratch_runner_covers_learner_gates_in_order() -> None:
    verifier = (CH / "verify.sh").read_text()
    text = verifier[verifier.index("# Before you begin and Sections 1-3.") :]
    commands = [
        "dbt seed",
        "dbt run --select tag:source-aligned",
        "dbt run --select dom_trading__trade",
        "dbt run --select api_latest_price",
        "astro dev start",
        "ATLAS_VERIFY_SCOPE=mvp",
        "dbt build --select rpt_portfolio_performance",
        "dbt source freshness",
        "dbt ls --select +exposure:advisor_dashboard",
        "dbt test --select rpt_portfolio_summary --indirect-selection=cautious",
        'run_expected_failure "non-negative-signed-quantity"',
        "dbt build --select ts_daily_market_incremental",
        "dbt snapshot",
        "dbt build --select rpt_region_report rpt_advisor_leaderboard",
        "CERT_INTEGRATION_TESTS=1 mise run challenge:verify 04",
    ]
    offsets = [text.index(command) for command in commands]
    assert offsets == sorted(offsets)


def test_ch04_phase2_test_solutions_and_compiled_sql_check_are_actionable() -> None:
    stub_advisors = (CH / "stubs/datasets/advisors/dbt/advisors.yml").read_text()
    solution_advisors = (CH / "solution/datasets/advisors/dbt/advisors.yml").read_text()
    stub_trades = (CH / "stubs/datasets/trades/dbt/trades.yml").read_text()
    solution_trades = (CH / "solution/datasets/trades/dbt/trades.yml").read_text()
    guide = (CH / "README.md").read_text()
    assert stub_advisors != solution_advisors
    assert "tests: [non_negative]" in solution_advisors
    assert stub_trades != solution_trades
    assert "relationships:" in solution_trades
    assert "arguments:" in solution_trades
    assert "dbt compile --select ts_daily_market_incremental --target-path \"$TARGET\"" in guide
    assert "TARGET=$(awk '/^target-path:" not in guide


def test_ch04_guide_documents_destructive_maintainer_runner() -> None:
    guide = (CH / "README.md").read_text()
    assert "### Maintainer-only from-scratch verification" in guide
    assert "challenges/v1/04-atlas-capstone/verify.sh --from-scratch" in guide
    assert "destructive to work under `data_products/atlas_elt/datasets/`" in guide
    assert ".devcontainer/verify/04-atlas-capstone/" in guide
    assert "interactions.tsv" in guide
    assert "--dry-run" in guide


def test_ch04_review_mode_is_plain_ascii_and_non_destructive() -> None:
    verifier = CH / "verify.sh"
    result = subprocess.run(
        ["bash", str(verifier), "--review"],
        cwd=repo_root(),
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PHASE 1: REQUIRED DATA PRODUCT MVP" in result.stdout
    assert result.stdout.count("\nCHALLENGE ") == 14
    for label in ("PURPOSE", "LEARNER TASK", "SOLUTION", "PROOF"):
        assert label in result.stdout
    for markdown_token in ("# ", "**", "```"):
        assert markdown_token not in result.stdout
    assert "challenge:reset" not in result.stdout
    assert "Databricks" not in result.stderr


def test_ch04_unified_verifier_dispatches_without_recursion() -> None:
    text = (CH / "verify.sh").read_text()
    assert 'MODE="gate"' in text
    assert '--from-scratch) MODE="from-scratch"' in text
    assert '--review) MODE="review"' in text
    assert "run_gate" in text
    assert "mise run challenge:verify 04" in text
    assert not (CH / "verify-from-scratch.sh").exists()
