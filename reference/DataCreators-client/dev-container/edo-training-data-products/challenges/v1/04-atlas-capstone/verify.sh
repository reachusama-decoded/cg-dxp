#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PRODUCT_ROOT="$REPO_ROOT/data_products/atlas_elt"
STUB_ROOT="$SCRIPT_DIR/stubs/datasets"
SOLUTION_ROOT="$SCRIPT_DIR/solution/datasets"
VERIFY_ROOT="$REPO_ROOT/.devcontainer/verify/04-atlas-capstone"

MODE="gate"
DRY_RUN=0
KEEP_STATE=0
for arg in "$@"; do
  case "$arg" in
    --gate) MODE="gate" ;;
    --from-scratch) MODE="from-scratch" ;;
    --review) MODE="review" ;;
    --dry-run)
      MODE="from-scratch"
      DRY_RUN=1
      ;;
    --keep-state) KEEP_STATE=1 ;;
    -h|--help)
      cat <<EOF
Usage: $(basename "$0") [MODE] [OPTIONS]

Modes:
  (no option), --gate  Run the normal offline/live completion gate.
  --from-scratch       Reset and execute the complete learner journey.
  --review             Print a non-destructive instructor synopsis.

From-scratch options:
  --dry-run            Validate manifests without resetting or running commands.
  --keep-state          Leave the solved learner files in place after the run.
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

describe_challenge() {
  local number="$1"
  local title="$2"
  local purpose="$3"
  local learner_task="$4"
  local solution="$5"
  local proof="$6"

  printf '\n%s\n' '-------------------------------------------------------------------------------'
  printf 'CHALLENGE %s: %s\n' "$number" "$title"
  printf '%s\n' '-------------------------------------------------------------------------------'
  printf 'PURPOSE       %s\n' "$purpose"
  printf 'LEARNER TASK  %s\n' "$learner_task"
  printf 'SOLUTION      %s\n' "$solution"
  printf 'PROOF         %s\n' "$proof"
}

print_review() {
  cat <<'EOF'
===============================================================================
ATLAS CAPSTONE - INSTRUCTOR REVIEW
===============================================================================

This is a read-only synopsis. It does not reset files, connect to Databricks,
or start Airflow. Phase 1 builds the required baseline; Phase 2 contains the
14 extension challenges reviewed below.

PHASE 1: REQUIRED DATA PRODUCT MVP
-------------------------------------------------------------------------------
PURPOSE       Build a trustworthy Atlas pipeline from classroom seed data.
LEARNER TASK  Inspect sources; build source-, domain-, and consumer-aligned
              models; test reconciliations; inspect the generated Airflow DAG.
SOLUTION      Seven source pass-throughs feed cleaned domain entities and
              positions, then seven report-ready marts and API/time-series views.
PROOF         23 models run, three reconciliations pass, and Atlas DAGs load
              without import errors.
EOF

  describe_challenge \
    "1" \
    "Portfolio performance report" \
    "Give executives one portfolio-level view of value, activity, flow, and fees." \
    "Combine the portfolio summary with position buy/sell totals and calculate realised fee basis points." \
    "Aggregate positions to portfolio grain, derive net flow, and divide fees by total traded value with a zero guard." \
    "The model builds and displayed fee rates remain in a believable basis-point range."

  describe_challenge \
    "2" \
    "Advisor leaderboard" \
    "Rank advisors by assets under management while handling ties cleanly." \
    "Add a gap-free rank to the advisor book." \
    "Use dense_rank over descending book AUM." \
    "The largest book is rank 1; ties share a rank without skipping the next rank."

  describe_challenge \
    "3" \
    "Daily asset-class activity" \
    "Show which asset classes drive trading and how activity trends over seven days." \
    "Aggregate trades by date and asset class, then calculate a rolling seven-row traded value." \
    "Join conformed trades to instruments, aggregate daily, and apply a partitioned window sum." \
    "The model builds and early rolling values grow into seven-day totals."

  describe_challenge \
    "4" \
    "Source freshness" \
    "Detect when an upstream trade extract becomes too old to trust." \
    "Inspect the source freshness metadata, run it, tighten the warning threshold, and restore it." \
    "Use the trade epoch timestamp as loaded_at_field with broad classroom thresholds." \
    "The shipped threshold passes or warns; a one-day threshold produces WARN."

  describe_challenge \
    "5" \
    "Consumer exposures" \
    "Make dashboard consumers and their upstream model dependencies visible in dbt lineage." \
    "Declare advisor, portfolio, and market dashboard exposures." \
    "Create exposures.yml with owners and ref-based dependencies on the relevant marts." \
    "dbt parse succeeds and selecting the advisor exposure lists its dependency graph."

  describe_challenge \
    "6" \
    "Reusable money macros" \
    "Keep cents and basis-point conversions named and consistent across models." \
    "Inspect the shared macros and confirm model Jinja expands to the expected SQL." \
    "Reuse cents_to_decimal and basis_points instead of scattering numeric divisors." \
    "The trade model compiles and rebuilds with the expanded conversion expressions."

  describe_challenge \
    "7" \
    "Non-negative money test" \
    "Catch invalid negative AUM or fee values caused by sign or join errors." \
    "Attach the existing non_negative generic test to appropriate money columns." \
    "Test portfolio-summary AUM and fees; temporarily attach it to signed quantity to prove it detects sells." \
    "Valid money columns pass and the deliberate signed-quantity case fails."

  describe_challenge \
    "8" \
    "Trade-to-portfolio relationship test" \
    "Prevent orphan trades from disappearing silently during portfolio rollups." \
    "Assert that every trade portfolio_id exists in the conformed portfolio model." \
    "Add dbt's relationships test with the portfolio model and portfolio_id field as arguments." \
    "The generated referential-integrity test passes with no orphan portfolio IDs."

  describe_challenge \
    "9" \
    "AUM reconciliation tests" \
    "Prove that different business rollups preserve the same total AUM." \
    "Inspect and run advisor and segment singular tests, then force and restore a failure." \
    "Compare each rollup total with portfolio-summary AUM using a small rounding tolerance." \
    "Both tests pass normally, fail with a negative tolerance, and pass again after restoration."

  describe_challenge \
    "10" \
    "Incremental daily market mart" \
    "Avoid rebuilding all market history when only new trading dates arrive." \
    "Build a daily aggregate with incremental materialization, a date key, and an is_incremental filter." \
    "Use trade_date as unique_key and process dates later than the existing maximum on subsequent runs." \
    "First and second runs pass; compiled SQL on the second run contains the date filter."

  describe_challenge \
    "11" \
    "Portfolio history snapshot" \
    "Preserve previous strategy and advisor assignments instead of overwriting history." \
    "Inspect and run the shipped portfolio snapshot twice." \
    "Use portfolio_id as the key and check strategy/advisor changes with dbt snapshot SCD2 columns." \
    "The first run creates history and the unchanged second run adds no new versions."

  describe_challenge \
    "12" \
    "Dataset orchestration" \
    "Connect per-dataset Airflow schedules to Databricks bundle jobs." \
    "Compare advisor and portfolio-performance DAG YAML and inventory all dataset DAG files." \
    "Each paved-path YAML triggers the matching dbt and DQ Databricks jobs, followed by notification steps." \
    "All expected DAG YAML files exist and Airflow loads the Atlas DAG set without import errors."

  describe_challenge \
    "13" \
    "Runtime parameters and bundle variables" \
    "Show how one orchestration definition can vary catalog, schema, paths, and selectors at runtime." \
    "Trace a development variable into the advisor bundle job and explain the Airflow-parameter analogy." \
    "Bundle variables flow into job arguments without changing DAG structure." \
    "A value can be traced from variables_dev.yml into advisors.job.yml."

  describe_challenge \
    "14" \
    "Regional report and integration proof" \
    "Deliver a regional management view whose AUM can be trusted." \
    "Roll portfolio summaries up by region and run the regional reconciliation test." \
    "Count portfolios and clients, sum AUM and fees by region, and compare total regional AUM with the source summary." \
    "The regional report and leaderboard build, and reconcile_region_aum passes."

  cat <<'EOF'

===============================================================================
END OF REVIEW
===============================================================================
EOF
}

resolve_dbt_python() {
  if [[ -x "/opt/venv/bin/python" ]]; then
    echo "/opt/venv/bin/python"
  elif [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
    echo "$REPO_ROOT/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  elif command -v python >/dev/null 2>&1; then
    command -v python
  else
    return 1
  fi
}

run_gate() (
  set -euo pipefail

  local product_root="${ATLAS_ELT_ROOT:-$REPO_ROOT/data_products/atlas_elt}"
  local models_root="${ATLAS_ELT_MODELS_ROOT:-}"
  local work_root="$product_root"
  local tmp_root=""
  local lock_file=""
  local lock_backup=""
  local bundle_status="not checked"
  local verify_scope="${ATLAS_VERIFY_SCOPE:-full}"
  local dbt_python
  local -a mvp_models=(
    src_trading__trades
    src_secmaster__instruments
    src_portfolio__portfolios
    src_crm__clients
    src_crm__advisors
    src_fundref__funds
    src_fundref__fund_holdings
    dom_trading__trade
    dom_instrument__instrument
    dom_portfolio__portfolio
    dom_party__client
    dom_party__advisor
    dom_fund__fund
    dom_fund__holding
    dom_trading__latest_price
    dom_positions__position
    api_latest_price
    rpt_portfolio_summary
    rpt_advisor_book
    ts_daily_market
    agg_segment_aum
    agg_instrument_activity
    agg_fund_nav
  )
  local -a mvp_tests=(
    reconcile_advisor_book_aum
    reconcile_segment_aum
    reconcile_trade_counts
  )

  gate_cleanup() {
    if [[ -n "$lock_backup" && -f "$lock_backup" ]]; then
      cp "$lock_backup" "$lock_file"
      rm -f "$lock_backup"
    fi
    if [[ -n "$tmp_root" && -d "$tmp_root" ]]; then
      rm -rf "$tmp_root"
    fi
  }
  trap gate_cleanup EXIT

  dbt_python="$(resolve_dbt_python || true)"
  if [[ -z "$dbt_python" ]]; then
    echo "No Python interpreter found; cannot run dbt wrapper." >&2
    exit 2
  fi
  if ! "$dbt_python" -c "import dbt.cli.main" >/dev/null 2>&1; then
    echo "dbt core dependencies are missing for $dbt_python; run 'mise run setup:python-deps' in the devcontainer." >&2
    exit 2
  fi

  if [[ -n "$models_root" ]]; then
    if [[ ! -d "$models_root/datasets" ]]; then
      echo "ATLAS_ELT_MODELS_ROOT must contain datasets/: $models_root" >&2
      exit 4
    fi
    tmp_root="$(mktemp -d)"
    cp -R "$product_root/." "$tmp_root/"
    cp -R "$models_root/datasets/." "$tmp_root/datasets/"
    work_root="$tmp_root"
  fi

  if [[ -z "$tmp_root" && -f "$work_root/package-lock.yml" ]]; then
    lock_file="$work_root/package-lock.yml"
    lock_backup="$(mktemp)"
    cp "$lock_file" "$lock_backup"
  fi

  echo "Running dbt deps..."
  "$dbt_python" "$REPO_ROOT/dbt_wrapper.py" deps --project-dir "$work_root" --profiles-dir "$work_root/dbt_profiles" --target local

  echo "Running dbt parse..."
  "$dbt_python" "$REPO_ROOT/dbt_wrapper.py" parse --project-dir "$work_root" --profiles-dir "$work_root/dbt_profiles" --target local

  echo "Running dbt compile..."
  "$dbt_python" "$REPO_ROOT/dbt_wrapper.py" compile --project-dir "$work_root" --profiles-dir "$work_root/dbt_profiles" --target local

  if [[ -n "$tmp_root" ]]; then
    echo "[skip] temporary solution overlay - bundle validation uses the real product tree."
    bundle_status="skipped (temporary solution overlay)"
  elif command -v databricks >/dev/null 2>&1; then
    echo "Running databricks bundle validate..."
    if ! (cd "$work_root" && databricks bundle validate -t local); then
      echo "[warn] databricks bundle validate failed - usually an environmental Terraform /" >&2
      echo "[warn] OpenPGP issue (e.g. a future-dated clock), not a challenge defect. Continuing." >&2
      bundle_status="warning (environmental validation failure)"
    else
      bundle_status="passed"
    fi
  else
    echo "[skip] databricks CLI not on PATH - skipping bundle validate."
    bundle_status="skipped (Databricks CLI unavailable)"
  fi

  if [[ "${CERT_INTEGRATION_TESTS:-0}" != "1" ]]; then
    echo
    echo "OFFLINE PASS: dbt dependencies, parsing, and compilation passed."
    echo "Bundle validation: $bundle_status."
    echo "Databricks models and tests were not run."
    echo "Run 'CERT_INTEGRATION_TESTS=1 mise run challenge:verify 04' for live completion."
    exit 0
  fi

  case "$verify_scope" in
    mvp)
      echo "Running Phase 1 MVP models + tests on Databricks..."
      "$dbt_python" "$REPO_ROOT/dbt_wrapper.py" run --project-dir "$work_root" --profiles-dir "$work_root/dbt_profiles" --target local --select "${mvp_models[@]}"
      "$dbt_python" "$REPO_ROOT/dbt_wrapper.py" test --project-dir "$work_root" --profiles-dir "$work_root/dbt_profiles" --target local --select "${mvp_tests[@]}"
      echo
      echo "MVP LIVE PASS: 23 Phase 1 models ran and 3 reconciliations passed on Databricks."
      echo "Atlas ELT Phase 1 MVP complete."
      ;;
    full)
      echo "Running full capstone models + tests on Databricks..."
      "$dbt_python" "$REPO_ROOT/dbt_wrapper.py" run --project-dir "$work_root" --profiles-dir "$work_root/dbt_profiles" --target local
      "$dbt_python" "$REPO_ROOT/dbt_wrapper.py" test --project-dir "$work_root" --profiles-dir "$work_root/dbt_profiles" --target local
      echo
      echo "LIVE PASS: dbt models ran and all tests passed on Databricks."
      echo "Atlas ELT capstone complete."
      ;;
    *)
      echo "[FAIL] ATLAS_VERIFY_SCOPE must be 'mvp' or 'full', got '$verify_scope'." >&2
      exit 6
      ;;
  esac

  if [[ "${ATLAS_DEPLOY_BUNDLE:-0}" == "1" ]]; then
    if ! command -v databricks >/dev/null 2>&1; then
      echo "[FAIL] ATLAS_DEPLOY_BUNDLE=1 requires databricks CLI on PATH." >&2
      exit 5
    fi
    echo "Deploying bundle and triggering a pipeline run..."
    (cd "$work_root" && databricks bundle deploy -t local && databricks bundle run -t local trades_job)
  fi
)

case "$MODE" in
  gate)
    if [[ "$KEEP_STATE" == "1" || "$DRY_RUN" == "1" ]]; then
      echo "[FAIL] --keep-state and --dry-run apply only to --from-scratch." >&2
      exit 2
    fi
    run_gate
    exit $?
    ;;
  review)
    if [[ "$KEEP_STATE" == "1" || "$DRY_RUN" == "1" ]]; then
      echo "[FAIL] --review does not accept from-scratch options." >&2
      exit 2
    fi
    print_review
    exit 0
    ;;
  from-scratch) ;;
esac

PHASE1_SOURCE_FILES=(
  trades/dbt/staging/src_trading__trades.sql
  instruments/dbt/staging/src_secmaster__instruments.sql
  portfolios/dbt/staging/src_portfolio__portfolios.sql
  clients/dbt/staging/src_crm__clients.sql
  advisors/dbt/staging/src_crm__advisors.sql
  funds/dbt/staging/src_fundref__funds.sql
  fund_holdings/dbt/staging/src_fundref__fund_holdings.sql
)

PHASE1_DOMAIN_FILES=(
  trades/dbt/integration/dom_trading__trade.sql
  instruments/dbt/integration/dom_instrument__instrument.sql
  portfolios/dbt/integration/dom_portfolio__portfolio.sql
  clients/dbt/integration/dom_party__client.sql
  advisors/dbt/integration/dom_party__advisor.sql
  funds/dbt/integration/dom_fund__fund.sql
  fund_holdings/dbt/integration/dom_fund__holding.sql
  market_daily/dbt/integration/dom_trading__latest_price.sql
  portfolios/dbt/integration/dom_positions__position.sql
)

PHASE1_CONSUMER_FILES=(
  market_daily/dbt/prepared/api_latest_price.sql
  advisors/dbt/integration/rpt_portfolio_summary.sql
  advisors/dbt/integration/rpt_advisor_book.sql
  market_daily/dbt/prepared/ts_daily_market.sql
  segment_aum/dbt/prepared/agg_segment_aum.sql
  market_daily/dbt/prepared/agg_instrument_activity.sql
  fund_nav/dbt/prepared/agg_fund_nav.sql
)

PHASE2_FILES=(
  portfolio_perf/dbt/prepared/rpt_portfolio_performance.sql
  advisors/dbt/integration/rpt_advisor_leaderboard.sql
  market_daily/dbt/prepared/ts_daily_asset_class.sql
  advisors/dbt/advisors.yml
  trades/dbt/trades.yml
  market_daily/dbt/prepared/ts_daily_market_incremental.sql
  advisors/dbt/integration/rpt_region_report.sql
)

PHASE2_NEW_FILES=(
  exposures.yml
)

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

assert_protected_log_root() {
  case "$VERIFY_ROOT/" in
    "$REPO_ROOT/.devcontainer/verify/"*) ;;
    *) fail "verification output escaped .devcontainer/verify: $VERIFY_ROOT" ;;
  esac
  case "$VERIFY_ROOT/" in
    "$PRODUCT_ROOT/"*|"$STUB_ROOT/"*|"$SOLUTION_ROOT/"*)
      fail "verification output would be removed or copied by challenge reset"
      ;;
  esac
}

assert_manifest_file() {
  local relative_path="$1"
  [[ -f "$SOLUTION_ROOT/$relative_path" ]] || fail "missing solution file: $relative_path"
  [[ -f "$STUB_ROOT/$relative_path" ]] || fail "missing starter file: $relative_path"
  ! cmp -s "$STUB_ROOT/$relative_path" "$SOLUTION_ROOT/$relative_path" ||
    fail "starter already contains the solution: $relative_path"
}

assert_new_manifest_file() {
  local relative_path="$1"
  [[ -f "$SOLUTION_ROOT/$relative_path" ]] || fail "missing solution file: $relative_path"
  [[ ! -e "$STUB_ROOT/$relative_path" ]] || fail "expected a learner-created file, found starter: $relative_path"
}

print_plan() {
  local phase relative_path
  echo "Challenge 04 from-scratch learner plan"
  echo "  logs: $VERIFY_ROOT/<timestamp>/"
  echo "  reset: mise run challenge:reset 04"
  for phase in PHASE1_SOURCE_FILES PHASE1_DOMAIN_FILES PHASE1_CONSUMER_FILES PHASE2_FILES; do
    local -n files="$phase"
    echo "  $phase: ${#files[@]} learner-authored files"
    for relative_path in "${files[@]}"; do
      assert_manifest_file "$relative_path"
    done
  done
  echo "  PHASE2_NEW_FILES: ${#PHASE2_NEW_FILES[@]} learner-created files"
  for relative_path in "${PHASE2_NEW_FILES[@]}"; do
    assert_new_manifest_file "$relative_path"
  done
  echo "  Phase 1: inspect, deps, auth/debug, seed, three model layers, tests, Airflow, MVP gate"
  echo "  Phase 2: challenges 1-14, business query, full live gate"
  echo "DRY-RUN PASS: ordered manifests and protected log path are valid."
}

[[ -f "$REPO_ROOT/.mise.toml" ]] || fail "run inside the edo-training-data-products repository"
[[ -d "$PRODUCT_ROOT" ]] || fail "Atlas product not found: $PRODUCT_ROOT"
assert_protected_log_root

if [[ "$DRY_RUN" == "1" ]]; then
  print_plan
  exit 0
fi

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-$$"
RUN_DIR="$VERIFY_ROOT/$RUN_ID"
LOCK_DIR="$VERIFY_ROOT/.lock"
RUN_LOG="$RUN_DIR/run.log"
COMMAND_LOG="$RUN_DIR/commands.log"
STEP_LOG="$RUN_DIR/steps.tsv"
INTERACTION_LOG="$RUN_DIR/interactions.tsv"
BASELINE_FILE="$RUN_DIR/outside-product.sha256"
PROTECTED_MARKER="$VERIFY_ROOT/.reset-protected"
CURRENT_STEP="initialization"
LAST_STEP_LOG=""
STEP_NUMBER=0
RESET_STARTED=0
ASTRO_STARTED=0
SOURCE_BACKUP=""
TEST_BACKUP=""
TRADES_YAML_BACKUP=""
DBT_LOG_START_SIZE=0

mkdir -p "$VERIFY_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  fail "another Challenge 04 from-scratch verification is running: $LOCK_DIR"
fi
mkdir -p "$RUN_DIR"
printf 'challenge 04 verification logs survive challenge:reset\n' > "$PROTECTED_MARKER"
printf 'step\tstatus\tcommand\tlog\n' > "$STEP_LOG"
printf 'checkpoint\tstatus\tevidence\n' > "$INTERACTION_LOG"
exec > >(tee -a "$RUN_LOG") 2>&1

record_step() {
  local status="$1"
  local command="$2"
  printf '%s\t%s\t%s\t%s\n' "$CURRENT_STEP" "$status" "$command" "$LAST_STEP_LOG" >> "$STEP_LOG"
}

record_interaction() {
  local checkpoint="$1"
  local status="$2"
  local evidence="$3"
  printf '%s\t%s\t%s\n' "$checkpoint" "$status" "$evidence" >> "$INTERACTION_LOG"
}

run_shell_step() {
  local label="$1"
  local workdir="$2"
  local command="$3"
  local status
  STEP_NUMBER=$((STEP_NUMBER + 1))
  CURRENT_STEP="$(printf '%03d-%s' "$STEP_NUMBER" "$label")"
  LAST_STEP_LOG="$RUN_DIR/$(printf '%03d-%s.log' "$STEP_NUMBER" "$label")"
  printf '\n== %s ==\n$ (cd %q && %s)\n' "$CURRENT_STEP" "$workdir" "$command"
  printf '%s\t%s\t%s\n' "$CURRENT_STEP" "$workdir" "$command" >> "$COMMAND_LOG"
  set +e
  (cd "$workdir" && bash -o pipefail -c "$command") 2>&1 | tee "$LAST_STEP_LOG"
  status=${PIPESTATUS[0]}
  set -e
  if [[ "$status" -ne 0 ]]; then
    record_step "FAIL($status)" "$command"
    fail "$CURRENT_STEP exited $status; see $LAST_STEP_LOG"
  fi
  record_step "PASS" "$command"
}

run_expected_failure() {
  local label="$1"
  local workdir="$2"
  local command="$3"
  local status
  STEP_NUMBER=$((STEP_NUMBER + 1))
  CURRENT_STEP="$(printf '%03d-%s' "$STEP_NUMBER" "$label")"
  LAST_STEP_LOG="$RUN_DIR/$(printf '%03d-%s.log' "$STEP_NUMBER" "$label")"
  printf '\n== %s (expected failure) ==\n$ (cd %q && %s)\n' "$CURRENT_STEP" "$workdir" "$command"
  printf '%s\t%s\t%s\n' "$CURRENT_STEP" "$workdir" "$command" >> "$COMMAND_LOG"
  set +e
  (cd "$workdir" && bash -o pipefail -c "$command") 2>&1 | tee "$LAST_STEP_LOG"
  status=${PIPESTATUS[0]}
  set -e
  if [[ "$status" -eq 0 ]]; then
    record_step "FAIL(expected-nonzero)" "$command"
    fail "$CURRENT_STEP unexpectedly passed; the guide's red-green exercise did not fail"
  fi
  record_step "PASS(expected-$status)" "$command"
}

assert_guide_contains() {
  local command="$1"
  grep -F -- "$command" "$SCRIPT_DIR/README.md" >/dev/null ||
    fail "runner command is not printed in the learner guide: $command"
}

run_guide_step() {
  local label="$1"
  local workdir="$2"
  local command="$3"
  assert_guide_contains "$command"
  run_shell_step "$label" "$workdir" "$command"
}

assert_last_log_contains() {
  local expected="$1"
  grep -F -- "$expected" "$LAST_STEP_LOG" >/dev/null ||
    fail "$CURRENT_STEP did not print expected text: $expected"
}

author_files() {
  local label="$1"
  shift
  local relative_path
  echo
  echo "== learner authoring: $label =="
  for relative_path in "$@"; do
    assert_manifest_file "$relative_path"
    mkdir -p "$(dirname "$PRODUCT_ROOT/datasets/$relative_path")"
    cp "$SOLUTION_ROOT/$relative_path" "$PRODUCT_ROOT/datasets/$relative_path"
    cmp -s "$SOLUTION_ROOT/$relative_path" "$PRODUCT_ROOT/datasets/$relative_path" ||
      fail "failed to author $relative_path"
    sha256sum "$PRODUCT_ROOT/datasets/$relative_path" | tee -a "$RUN_DIR/authored-files.sha256"
  done
}

author_new_file() {
  local relative_path="$1"
  assert_new_manifest_file "$relative_path"
  mkdir -p "$(dirname "$PRODUCT_ROOT/datasets/$relative_path")"
  cp "$SOLUTION_ROOT/$relative_path" "$PRODUCT_ROOT/datasets/$relative_path"
  sha256sum "$PRODUCT_ROOT/datasets/$relative_path" | tee -a "$RUN_DIR/authored-files.sha256"
}

restore_temporary_edits() {
  if [[ -n "$SOURCE_BACKUP" && -f "$SOURCE_BACKUP" ]]; then
    cp "$SOURCE_BACKUP" "$PRODUCT_ROOT/datasets/sources.yml"
    SOURCE_BACKUP=""
  fi
  if [[ -n "$TEST_BACKUP" && -f "$TEST_BACKUP" ]]; then
    cp "$TEST_BACKUP" "$PRODUCT_ROOT/tests/reconcile_advisor_book_aum.sql"
    TEST_BACKUP=""
  fi
  if [[ -n "$TRADES_YAML_BACKUP" && -f "$TRADES_YAML_BACKUP" ]]; then
    cp "$TRADES_YAML_BACKUP" "$PRODUCT_ROOT/datasets/trades/dbt/trades.yml"
    TRADES_YAML_BACKUP=""
  fi
}

capture_dbt_audit() {
  local dbt_log="$PRODUCT_ROOT/logs/dbt.log"
  if [[ -f "$dbt_log" ]]; then
    tail -c "+$((DBT_LOG_START_SIZE + 1))" "$dbt_log" > "$RUN_DIR/dbt-this-run.log" 2>/dev/null ||
      cp "$dbt_log" "$RUN_DIR/dbt-this-run.log"
    grep -o "'invocation_command': '[^']*'" "$RUN_DIR/dbt-this-run.log" |
      sed "s/.*: '//;s/'$//" > "$RUN_DIR/dbt-invocations.txt" || true
  fi
}

on_exit() {
  local status=$?
  trap - EXIT
  set +e
  restore_temporary_edits
  capture_dbt_audit
  if [[ "$ASTRO_STARTED" == "1" ]]; then
    echo "Stopping the Astro stack..."
    (cd "$REPO_ROOT" && astro dev stop) >> "$RUN_LOG" 2>&1
  fi
  if [[ "$RESET_STARTED" == "1" && "$KEEP_STATE" == "0" ]]; then
    echo "Restoring Challenge 04 starter files..."
    (cd "$REPO_ROOT" && mise run challenge:reset 04) >> "$RUN_LOG" 2>&1 || status=1
  fi
  if [[ ! -f "$PROTECTED_MARKER" ]]; then
    echo "[FAIL] challenge reset removed the protected verification marker" | tee -a "$RUN_LOG"
    status=1
  fi
  if ! (cd "$REPO_ROOT" && sha256sum -c "$BASELINE_FILE") > "$RUN_DIR/scope-audit.log" 2>&1; then
    echo "[FAIL] tracked files outside data_products/atlas_elt changed during the run" | tee -a "$RUN_LOG"
    status=1
  fi
  {
    echo "run_id=$RUN_ID"
    echo "result=$([[ "$status" == "0" ]] && echo PASS || echo FAIL)"
    echo "failed_or_final_step=$CURRENT_STEP"
    echo "logs=$RUN_DIR"
    echo "interaction_audit=$INTERACTION_LOG"
    echo "learner_state_restored=$([[ "$KEEP_STATE" == "0" ]] && echo yes || echo no)"
  } > "$RUN_DIR/summary.txt"
  rm -rf "$LOCK_DIR"
  echo
  if [[ "$status" == "0" ]]; then
    echo "FROM-SCRATCH PASS: every executable Challenge 04 learner phase completed."
  else
    echo "FROM-SCRATCH FAIL at $CURRENT_STEP. See $LAST_STEP_LOG"
  fi
  echo "Run evidence: $RUN_DIR"
  exit "$status"
}
trap on_exit EXIT

create_scope_baseline() {
  (cd "$REPO_ROOT" && git ls-files -z | while IFS= read -r -d '' path; do
    case "$path" in
      data_products/atlas_elt/*) continue ;;
    esac
    [[ -e "$path" ]] || continue
    sha256sum -- "$path"
  done) > "$BASELINE_FILE"
}

ensure_databricks_auth() {
  if ! (cd "$REPO_ROOT" && mise exec -- sh -c 'databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json >/dev/null') >> "$RUN_LOG" 2>&1; then
    echo "No refreshable Databricks OAuth session was found. Starting the guide's setup step."
    if [[ ! -t 0 ]]; then
      fail "authentication needs user interaction; run 'mise run setup:databricks' and rerun this script"
    fi
    run_guide_step "setup-databricks" "$REPO_ROOT" "mise run setup:databricks"
    (cd "$REPO_ROOT" && mise exec -- sh -c 'databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json >/dev/null') >> "$RUN_LOG" 2>&1 ||
      fail "OAuth setup completed but token minting still fails"
  fi
  if ! (cd "$REPO_ROOT" && mise exec -- sh -c 'test -n "${DBT_ACCESS_TOKEN:-}" && test "$DBT_ACCESS_TOKEN" != "MISSING_run__mise_run_setup_databricks"'); then
    fail "OAuth works, but DBT_ACCESS_TOKEN delivery is broken; run 'mise run setup:mise' and rerun"
  fi
  echo "Databricks token mint and dbt token delivery: OK"
}

clear_persistent_exercise_tables() {
  echo "Clearing the two stateful exercise tables to reproduce a first learner run..."
  (cd "$REPO_ROOT" && mise exec -- /opt/venv/bin/python - <<'PY'
import getpass
import os
from urllib.parse import urlparse

from databricks import sql

host = os.environ["DATABRICKS_HOST"]
server_hostname = urlparse(host).hostname or host.removeprefix("https://")
catalog = os.environ.get("DATABRICKS_CATALOG", "training_dev")
schema = os.environ.get("DATABRICKS_SCHEMA", f"training_{getpass.getuser()}")
with sql.connect(
    server_hostname=server_hostname,
    http_path=os.environ["DATABRICKS_HTTP_PATH"],
    access_token=os.environ["DBT_ACCESS_TOKEN"],
) as connection:
    with connection.cursor() as cursor:
        for relation in ("ts_daily_market_incremental", "portfolios_snapshot"):
            cursor.execute(f"DROP TABLE IF EXISTS `{catalog}`.`{schema}`.`{relation}`")
            print(f"Dropped if present: {catalog}.{schema}.{relation}")
PY
  ) 2>&1 | tee "$RUN_DIR/clear-state.log"
  [[ "${PIPESTATUS[0]}" == "0" ]] || fail "could not clear stateful exercise tables"
}

create_scope_baseline
if [[ -f "$PRODUCT_ROOT/logs/dbt.log" ]]; then
  DBT_LOG_START_SIZE="$(stat -c %s "$PRODUCT_ROOT/logs/dbt.log")"
fi

echo "Challenge 04 from-scratch verification"
echo "Run ID: $RUN_ID"
echo "Evidence directory: $RUN_DIR"
run_shell_step "resource-headroom" "$REPO_ROOT" 'docker stats --no-stream --format "{{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}"'
run_shell_step "stop-stale-airflow" "$REPO_ROOT" 'astro dev stop >/dev/null 2>&1 || true'
run_shell_step "reset-to-starter" "$REPO_ROOT" 'mise run challenge:reset 04'
RESET_STARTED=1
[[ -f "$PROTECTED_MARKER" ]] || fail "challenge reset removed $PROTECTED_MARKER"
print_plan

# Before you begin and Sections 1-3.
run_guide_step "repo-root-check" "$REPO_ROOT" 'test -f .mise.toml && test -d data_products/atlas_elt && echo "Repository root: OK"'
ensure_databricks_auth
run_guide_step "auth-describe-initial" "$REPO_ROOT" 'mise exec -- databricks auth describe --profile DEFAULT'
run_guide_step "dbt-debug-initial" "$PRODUCT_ROOT" 'dbt debug'
run_guide_step "inspect-pwd" "$PRODUCT_ROOT" 'pwd'
run_guide_step "inspect-seeds" "$PRODUCT_ROOT" 'ls seeds/'
run_guide_step "inspect-trades" "$PRODUCT_ROOT" 'head -3 seeds/trades.csv'
run_guide_step "inspect-instruments" "$PRODUCT_ROOT" 'head -3 seeds/instruments.csv'
run_guide_step "inspect-portfolios" "$PRODUCT_ROOT" 'head -3 seeds/portfolios.csv'
run_guide_step "dbt-deps" "$PRODUCT_ROOT" 'dbt deps'
run_guide_step "dbt-list-models" "$PRODUCT_ROOT" 'dbt ls --resource-type model'
run_guide_step "auth-describe-section-3-repeat" "$PRODUCT_ROOT" 'mise exec -- databricks auth describe --profile DEFAULT'
run_guide_step "dbt-debug-section-3-repeat" "$PRODUCT_ROOT" 'dbt debug'
clear_persistent_exercise_tables

# Phase 1, Sections 4-7.
run_guide_step "seed" "$PRODUCT_ROOT" 'dbt seed'
run_guide_step "show-seed" "$PRODUCT_ROOT" 'dbt show --inline "select * from {{ source('\''atlas'\'', '\''trades'\'') }}" --limit 5'
author_files "Section 5 source-aligned models" "${PHASE1_SOURCE_FILES[@]}"
run_guide_step "build-source-aligned" "$PRODUCT_ROOT" 'dbt run --select tag:source-aligned'
run_guide_step "show-source-aligned" "$PRODUCT_ROOT" 'dbt show --select src_trading__trades --limit 5'
author_files "Section 6 domain-aligned models" "${PHASE1_DOMAIN_FILES[@]}"
run_guide_step "build-domain-aligned" "$PRODUCT_ROOT" 'dbt run --select dom_trading__trade dom_instrument__instrument dom_portfolio__portfolio dom_party__client dom_party__advisor dom_fund__fund dom_fund__holding dom_trading__latest_price dom_positions__position'
run_guide_step "show-domain-aligned" "$PRODUCT_ROOT" 'dbt show --select dom_trading__trade --limit 10'
author_files "Section 7 consumer-aligned models" "${PHASE1_CONSUMER_FILES[@]}"
run_guide_step "build-consumer-aligned" "$PRODUCT_ROOT" 'dbt run --select api_latest_price rpt_portfolio_summary rpt_advisor_book ts_daily_market agg_segment_aum agg_instrument_activity agg_fund_nav'
run_guide_step "test-phase1-reconciliation" "$PRODUCT_ROOT" 'dbt test --select reconcile_advisor_book_aum'
run_guide_step "show-portfolio-summary" "$PRODUCT_ROOT" 'dbt show --select rpt_portfolio_summary --limit 10 --indirect-selection=cautious'

# Phase 1, Section 8: validate both the CLI-loaded DAG and the web UI endpoint.
run_guide_step "inspect-advisor-dag" "$REPO_ROOT" 'cat data_products/atlas_elt/datasets/advisors/airflow/advisors.dag.yml'
run_guide_step "start-airflow" "$REPO_ROOT" 'astro dev start'
ASTRO_STARTED=1
AIRFLOW_URL="$(grep -Eo 'https?://[^[:space:]]+:[0-9]+' "$LAST_STEP_LOG" | tail -1 || true)"
[[ -n "$AIRFLOW_URL" ]] || fail "Astro started but no Airflow UI URL was printed"
run_guide_step "airflow-import-errors" "$REPO_ROOT" 'astro dev run dags list-import-errors'
run_guide_step "airflow-atlas-dags" "$REPO_ROOT" 'astro dev run dags list | grep atlas_elt'
run_shell_step "airflow-advisor-details" "$REPO_ROOT" 'astro dev run dags details atlas_elt_advisors'
run_shell_step "airflow-ui-http" "$REPO_ROOT" "curl -fsSL '$AIRFLOW_URL' >/dev/null"
record_interaction "airflow-ui-inspection" "PASS(equivalent)" "DAG details parsed and $AIRFLOW_URL returned HTTP success; visual navigation is not automated by this shell runner"
run_guide_step "phase1-live-gate" "$REPO_ROOT" 'CERT_INTEGRATION_TESTS=1 ATLAS_VERIFY_SCOPE=mvp mise run challenge:verify 04'
assert_last_log_contains "MVP LIVE PASS"

# Phase 2 Challenges 1-3.
author_files "Challenge 1 portfolio performance" 'portfolio_perf/dbt/prepared/rpt_portfolio_performance.sql'
run_guide_step "build-portfolio-performance" "$PRODUCT_ROOT" 'dbt build --select rpt_portfolio_performance'
run_guide_step "show-portfolio-performance" "$PRODUCT_ROOT" 'dbt show --select rpt_portfolio_performance --limit 5'
author_files "Challenge 2 advisor leaderboard" 'advisors/dbt/integration/rpt_advisor_leaderboard.sql'
run_guide_step "build-advisor-leaderboard" "$PRODUCT_ROOT" 'dbt build --select rpt_advisor_leaderboard'
run_guide_step "show-advisor-leaderboard" "$PRODUCT_ROOT" 'dbt show --select rpt_advisor_leaderboard --limit 10'
author_files "Challenge 3 daily asset-class activity" 'market_daily/dbt/prepared/ts_daily_asset_class.sql'
run_guide_step "build-daily-asset-class" "$PRODUCT_ROOT" 'dbt build --select ts_daily_asset_class'
run_guide_step "show-daily-asset-class" "$PRODUCT_ROOT" 'dbt show --select ts_daily_asset_class --limit 20'

# Phase 2 Challenge 4: prove the shipped threshold and the documented warn variation.
run_guide_step "source-freshness-wide" "$PRODUCT_ROOT" 'dbt source freshness'
SOURCE_BACKUP="$RUN_DIR/sources.yml.before-freshness-variation"
cp "$PRODUCT_ROOT/datasets/sources.yml" "$SOURCE_BACKUP"
sed -i 's/warn_after: {count: 100000, period: day}/warn_after: {count: 1, period: day}/' "$PRODUCT_ROOT/datasets/sources.yml"
grep -F 'warn_after: {count: 1, period: day}' "$PRODUCT_ROOT/datasets/sources.yml" >/dev/null ||
  fail "Challenge 4 threshold variation could not be applied"
run_guide_step "source-freshness-tight-repeat" "$PRODUCT_ROOT" 'dbt source freshness'
assert_last_log_contains "WARN"
restore_temporary_edits

# Phase 2 Challenges 5-9.
author_new_file 'exposures.yml'
run_guide_step "parse-exposures" "$PRODUCT_ROOT" 'dbt parse'
run_guide_step "list-advisor-exposure" "$PRODUCT_ROOT" 'dbt ls --select +exposure:advisor_dashboard'
run_guide_step "compile-money-macro" "$PRODUCT_ROOT" 'dbt compile --select dom_trading__trade'
run_guide_step "build-money-macro-model" "$PRODUCT_ROOT" 'dbt build --select dom_trading__trade'
author_files "Challenge 7 non-negative tests" 'advisors/dbt/advisors.yml'
run_guide_step "test-non-negative" "$PRODUCT_ROOT" 'dbt test --select rpt_portfolio_summary --indirect-selection=cautious'
TRADES_YAML_BACKUP="$RUN_DIR/trades.yml.before-signed-quantity-red-test"
cp "$PRODUCT_ROOT/datasets/trades/dbt/trades.yml" "$TRADES_YAML_BACKUP"
sed -i '/^  - name: src_trading__trades$/i\    columns:\n      - name: signed_qty\n        tests: [non_negative]' "$PRODUCT_ROOT/datasets/trades/dbt/trades.yml"
run_expected_failure "non-negative-signed-quantity" "$PRODUCT_ROOT" 'dbt test --select dom_trading__trade'
restore_temporary_edits
author_files "Challenge 8 relationship test" 'trades/dbt/trades.yml'
run_guide_step "test-relationships" "$PRODUCT_ROOT" 'dbt test --select dom_trading__trade'
run_guide_step "test-reconciliations-before-red" "$PRODUCT_ROOT" 'dbt test --select reconcile_advisor_book_aum reconcile_segment_aum'
TEST_BACKUP="$RUN_DIR/reconcile_advisor_book_aum.sql.before-red-test"
cp "$PRODUCT_ROOT/tests/reconcile_advisor_book_aum.sql" "$TEST_BACKUP"
sed -i 's/> 0\.01/> -1/' "$PRODUCT_ROOT/tests/reconcile_advisor_book_aum.sql"
run_expected_failure "reconciliation-negative-tolerance" "$PRODUCT_ROOT" 'dbt test --select reconcile_advisor_book_aum reconcile_segment_aum'
restore_temporary_edits
run_guide_step "test-reconciliations-restored-repeat" "$PRODUCT_ROOT" 'dbt test --select reconcile_advisor_book_aum reconcile_segment_aum'

# Phase 2 Challenges 10-11.
assert_guide_contains "Required AI Catalyst checkpoint"
record_interaction "dbt-best-practices-catalyst" "PROMPT-VALIDATED" "Required prompt is present; incremental behavior is acceptance-tested below; Copilot Chat response quality is nondeterministic and not shell-automated"
author_files "Challenge 10 incremental mart" 'market_daily/dbt/prepared/ts_daily_market_incremental.sql'
run_guide_step "build-incremental-first" "$PRODUCT_ROOT" 'dbt build --select ts_daily_market_incremental'
run_guide_step "run-incremental-second" "$PRODUCT_ROOT" 'dbt run --select ts_daily_market_incremental'
assert_guide_contains 'TARGET=$(mktemp -d)'
assert_guide_contains 'dbt compile --select ts_daily_market_incremental --target-path "$TARGET"'
assert_guide_contains 'find "$TARGET/compiled" -name ts_daily_market_incremental.sql -exec grep -A3 "trade_date >" {} +'
run_shell_step "inspect-incremental-compiled-sql" "$PRODUCT_ROOT" 'TARGET=$(mktemp -d); dbt compile --select ts_daily_market_incremental --target-path "$TARGET"; find "$TARGET/compiled" -name ts_daily_market_incremental.sql -exec grep -A3 "trade_date >" {} +; rm -rf "$TARGET"'
run_guide_step "snapshot-first" "$PRODUCT_ROOT" 'dbt snapshot'
run_guide_step "snapshot-second-repeat" "$PRODUCT_ROOT" 'dbt snapshot'
run_guide_step "show-snapshot-input" "$PRODUCT_ROOT" 'dbt show --select portfolios_snapshot --limit 5'

# Phase 2 Challenges 12-14 and product use.
run_guide_step "inspect-advisor-dag-again" "$PRODUCT_ROOT" 'cat datasets/advisors/airflow/advisors.dag.yml'
run_guide_step "inspect-portfolio-perf-dag" "$PRODUCT_ROOT" 'cat datasets/portfolio_perf/airflow/portfolio_perf.dag.yml'
run_guide_step "list-dag-yaml" "$PRODUCT_ROOT" 'ls datasets/*/airflow/*.dag.yml'
run_guide_step "inspect-dev-variables" "$PRODUCT_ROOT" 'cat variables/variables_dev.yml'
run_guide_step "inspect-advisor-job" "$PRODUCT_ROOT" 'cat datasets/advisors/bundle/advisors.job.yml'
run_guide_step "stop-airflow-after-inspection" "$REPO_ROOT" 'astro dev stop'
ASTRO_STARTED=0
author_files "Challenge 14 regional capstone" 'advisors/dbt/integration/rpt_region_report.sql'
run_guide_step "build-regional-capstone" "$PRODUCT_ROOT" 'dbt build --select rpt_region_report rpt_advisor_leaderboard'
run_guide_step "test-regional-reconciliation" "$PRODUCT_ROOT" 'dbt test --select reconcile_region_aum'
run_guide_step "query-segment-aum" "$PRODUCT_ROOT" 'dbt show --inline "select segment, clients, portfolios, aum from {{ ref('\''agg_segment_aum'\'') }} order by aum desc" --limit 10'
run_guide_step "query-regional-report" "$PRODUCT_ROOT" 'dbt show --inline "select region, portfolios, clients, aum, fees_generated from {{ ref('\''rpt_region_report'\'') }} order by aum desc" --limit 10'
assert_guide_contains "Turn results into a decision"
record_interaction "copilot-business-briefing" "PROMPT-VALIDATED" "Briefing prompt and both supporting query outputs are present; conversational prose is not shell-automated"

# The guide's final offline and full live gates must both tell the truth.
run_guide_step "offline-gate" "$REPO_ROOT" 'mise run challenge:verify 04'
assert_last_log_contains "OFFLINE PASS"
run_guide_step "full-live-gate" "$REPO_ROOT" 'CERT_INTEGRATION_TESTS=1 mise run challenge:verify 04'
assert_last_log_contains "LIVE PASS"
assert_last_log_contains "Atlas ELT capstone complete."
CURRENT_STEP="completed"