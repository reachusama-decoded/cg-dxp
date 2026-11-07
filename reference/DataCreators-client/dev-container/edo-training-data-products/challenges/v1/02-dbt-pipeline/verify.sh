#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PROJECT_DIR="$SCRIPT_DIR/dbt"
PROFILES_DIR="$SCRIPT_DIR/dbt_profiles"
# Why: verify.sh is the trainee's self-check, so it must build the learner's own
# working models by default — unsolved stubs are expected to build RED. CI can
# confirm the challenge is still solvable by setting DBT_MODELS_DIR to the
# retained solution (challenges/v1/02-dbt-pipeline/solution/models). When an
# alternate models directory has a sibling tests/ directory, overlay that too.
DEFAULT_MODELS_DIR="$PROJECT_DIR/models"
DEFAULT_TESTS_DIR="$PROJECT_DIR/tests"
DBT_MODELS_DIR="${DBT_MODELS_DIR:-$DEFAULT_MODELS_DIR}"
if [[ -z "${DBT_TESTS_DIR:-}" && "$DBT_MODELS_DIR" != "$DEFAULT_MODELS_DIR" ]]; then
  ALTERNATE_TESTS_DIR="$(dirname "$DBT_MODELS_DIR")/tests"
  if [[ -d "$ALTERNATE_TESTS_DIR" ]]; then
    DBT_TESTS_DIR="$ALTERNATE_TESTS_DIR"
  fi
fi
DBT_TESTS_DIR="${DBT_TESTS_DIR:-$DEFAULT_TESTS_DIR}"
WORK_PROJECT="$PROJECT_DIR"
TMP_PROJECT=""

# Preserve the historical fail-fast contract for bad model paths, regardless of local dbt install state.
if [ -n "${DBT_MODELS_DIR:-}" ] && [ ! -d "${DBT_MODELS_DIR}" ]; then
  echo "DBT_MODELS_DIR not found: ${DBT_MODELS_DIR}" >&2
  exit 4
fi
if [ -n "${DBT_TESTS_DIR:-}" ] && [ ! -d "${DBT_TESTS_DIR}" ]; then
  echo "DBT_TESTS_DIR not found: ${DBT_TESTS_DIR}" >&2
  exit 4
fi

resolve_dbt_python() {
  if [ -x "/opt/venv/bin/python" ]; then
    echo "/opt/venv/bin/python"
    return
  fi
  if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
    echo "$REPO_ROOT/.venv/bin/python"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi
  return 1
}

DBT_PY="$(resolve_dbt_python || true)"
if [[ -z "$DBT_PY" ]]; then
  echo "No Python interpreter found; cannot run dbt wrapper." >&2
  exit 2
fi
if ! "$DBT_PY" -c "import dbt.cli.main" >/dev/null 2>&1; then
  echo "dbt core dependencies are missing for $DBT_PY; run 'mise run setup:python-deps' in the devcontainer." >&2
  exit 2
fi

cleanup() {
  if [[ -n "$TMP_PROJECT" && -d "$TMP_PROJECT" ]]; then
    rm -rf "$TMP_PROJECT"
  fi
}
trap cleanup EXIT

# Build in an isolated copy so solution overlays never mutate the trainee's
# working tree.
TMP_PROJECT="$(mktemp -d)"
cp -R "$PROJECT_DIR/." "$TMP_PROJECT/"
# Overlay authored models and tests while preserving project scaffolding such as
# models/sources.yml, seeds, profiles, and dbt_project.yml.
cp -R "${DBT_MODELS_DIR}/." "$TMP_PROJECT/models/"
cp -R "${DBT_TESTS_DIR}/." "$TMP_PROJECT/tests/"
WORK_PROJECT="$TMP_PROJECT"

cd "$WORK_PROJECT"

printf "Running dbt debug (profiles-dir=%s)...\n" "$PROFILES_DIR"
if ! "$DBT_PY" "$REPO_ROOT/dbt_wrapper.py" debug --project-dir "$WORK_PROJECT" --profiles-dir "$PROFILES_DIR" --target local; then
  echo "dbt debug failed" >&2
  exit 2
fi

# Provision the raw sources (shipped as seeds) into the trainee's schema before
# building so source() resolves. dbt seed is idempotent (create or replace).
printf "Seeding raw sources + reference seeds...\n"
if ! "$DBT_PY" "$REPO_ROOT/dbt_wrapper.py" seed --project-dir "$WORK_PROJECT" --profiles-dir "$PROFILES_DIR" --target local; then
  echo "dbt seed failed" >&2
  exit 3
fi

# Why: a red run/test is the intended learner signal — unsolved stubs and
# incorrect models must fail. Green means the trainee solved it.
printf "Running dbt run...\n"
if ! "$DBT_PY" "$REPO_ROOT/dbt_wrapper.py" run --project-dir "$WORK_PROJECT" --profiles-dir "$PROFILES_DIR" --target local; then
  echo "dbt run failed" >&2
  exit 3
fi

printf "Running dbt test...\n"
if ! "$DBT_PY" "$REPO_ROOT/dbt_wrapper.py" test --project-dir "$WORK_PROJECT" --profiles-dir "$PROFILES_DIR" --target local; then
  echo "dbt test failed" >&2
  exit 3
fi

echo "DBT build + tests succeeded"
exit 0
