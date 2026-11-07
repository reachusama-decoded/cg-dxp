#!/usr/bin/env bash
# Run inside the dev container to verify every moving part is healthy.
#
#     dpc-check            (or: bash .devcontainer/check.sh)
#
# Exit code is 0 if everything's green, non-zero if any HARD check failed.
# WARN lines are tolerated when auth has not yet been configured.
# Every FAIL/WARN prints a one-line "fix:" hint pointing at the remedy.

set -u

PASS=0
DPC_HARD_FAILURES=0
DPC_WARNINGS=0
HINT=""   # set before a check() / soft_check() to print a remediation hint
DPC_HARD_FAIL_FILE=$(mktemp -t dpc-check-fail-XXXXXX)
trap 'rm -f "$DPC_HARD_FAIL_FILE"' EXIT

bold()    { printf '\033[1m%s\033[0m' "$*"; }
green()   { printf '\033[1;32m%s\033[0m' "$*"; }
red()     { printf '\033[1;31m%s\033[0m' "$*"; }
yellow()  { printf '\033[1;33m%s\033[0m' "$*"; }

_hint() { [ -n "$HINT" ] && printf '         %s %s\n' "$(yellow 'fix:')" "$HINT"; HINT=""; }

check() {
    local label=$1
    shift
    local out
    if out=$("$@" 2>&1); then
        printf '  %s %s\n' "$(green '[OK]  ')" "$label"
        PASS=$((PASS + 1))
        HINT=""
        return 0
    fi

    printf '  %s %s\n' "$(red '[FAIL]')" "$label"
    printf '%s\n' "$out" | sed 's/^/         /'
    _hint
    DPC_HARD_FAILURES=$((DPC_HARD_FAILURES + 1))
    printf '%s\n' "$label" >>"$DPC_HARD_FAIL_FILE"
    return 1
}

soft_check() {
    local label=$1
    shift
    if "$@" >/dev/null 2>&1; then
        printf '  %s %s\n' "$(green '[OK]  ')" "$label"
        PASS=$((PASS + 1))
        HINT=""
    else
        printf '  %s %s\n' "$(yellow '[WARN]')" "$label"
        _hint
        DPC_WARNINGS=$((DPC_WARNINGS + 1))
    fi
}

run_with_timeout() {
    local secs=$1
    shift
    if command -v timeout >/dev/null 2>&1; then
        timeout -k 5 "$secs" "$@"
    else
        "$@"
    fi
}

section() { printf '\n%s\n' "$(bold "=== $* ===")"; }

if [ -n "${WORKSPACE:-}" ]; then
    WS="$WORKSPACE"
else
    WS=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
fi

if [ -d "$WS/.venv/bin" ]; then
    PATH="$WS/.venv/bin:$PATH"
fi

export SSL_CERT_FILE=/cacert.pem
export REQUESTS_CA_BUNDLE=/cacert.pem
export PIP_CERT=/cacert.pem

if [ -f "$HOME/.config/dpc/databricks.env" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.config/dpc/databricks.env"
fi

if [ -x /opt/venv/bin/python ]; then
    PYTHON_BIN=/opt/venv/bin/python
elif [ -x "$WS/.venv/bin/python" ]; then
    PYTHON_BIN="$WS/.venv/bin/python"
else
    PYTHON_BIN="${PYTHON_BIN:-$(command -v python)}"
fi

# --- CLIs ---
section "CLI tools"
check "python on PATH"             which python
check "python is 3.13.x"           "$PYTHON_BIN" -c "import sys; assert sys.version.startswith('3.13.')"
check "astro on PATH"              which astro
check "astro responds"             astro version
check "databricks on PATH"         which databricks
check "databricks responds"        databricks --version
check "dbt on PATH"                which dbt
check "docker CLI on PATH"         which docker
check "dbt-core installed"         "$PYTHON_BIN" -m pip show dbt-core >/dev/null 2>&1
check "dbt-databricks installed"   "$PYTHON_BIN" -m pip show dbt-databricks >/dev/null 2>&1
check "pytest installed"           "$PYTHON_BIN" -m pip show pytest >/dev/null 2>&1

# --- Inner dockerd ---
section "Inner dockerd (DinD)"
HINT="run: /usr/local/bin/ensure-dockerd.sh (or: /usr/local/bin/start-dockerd.sh), then rerun dpc-check"
check "dockerd process running"    pgrep -x dockerd
HINT="run: /usr/local/bin/ensure-dockerd.sh (or: /usr/local/bin/start-dockerd.sh), then rerun dpc-check"
check "/var/run/docker.sock exists" test -S /var/run/docker.sock
HINT="run: /usr/local/bin/ensure-dockerd.sh (or: /usr/local/bin/start-dockerd.sh), then rerun dpc-check"
check "docker info responds"       docker info

# --- TLS / corp CA plumbing ---
section "TLS / corp CA plumbing"
check "/cacert.pem exists"         test -s /cacert.pem
check "/cacert.pem has >100 certs"  bash -c '[ "$(grep -c "BEGIN CERTIFICATE" /cacert.pem)" -gt 100 ]'
check "/etc/pip.conf uses corp index" bash -c 'grep -q "cgrepo-aws.capgroup.com/repository/cgpypi/simple" /etc/pip.conf'
check "/etc/pip.conf uses corp extra index" bash -c 'grep -q "cgrepo.capgroup.com/repository/cgpypi/simple" /etc/pip.conf'
check "SSL_CERT_FILE points to corp bundle"  bash -c '[ "$SSL_CERT_FILE" = /cacert.pem ]'
check "REQUESTS_CA_BUNDLE set"      bash -c '[ "$REQUESTS_CA_BUNDLE" = /cacert.pem ]'
check "PIP_CERT set"               bash -c '[ "$PIP_CERT" = /cacert.pem ]'
check "DOCKER_BUILDKIT=1"          bash -c '[ "$DOCKER_BUILDKIT" = 1 ]'
check "sitecustomize loaded (VERIFY_X509_STRICT off)" \
    "$PYTHON_BIN" -c "import ssl; assert not (ssl.create_default_context().verify_flags & ssl.VERIFY_X509_STRICT)"
# Network reachability is environmental (corp VPN / Zscaler); pip resolves via
# cgrepo.capgroup.com, not pypi.org. WARN, not a hard FAIL.
HINT="needs corp network/VPN; pip installs resolve via cgrepo.capgroup.com"
soft_check "pip can resolve a package (corp index)" \
    pip download --no-deps --quiet --dest /tmp/check-pip requests

# --- Astro build readiness ---
section "Astro build readiness"
HINT="post-start.sh patches Dockerfile for runtime/cert compatibility; restart the container if it changed"
check "Dockerfile uses the corp runtime mirror" \
    bash -c "grep -qE '^FROM[[:space:]]+(cgprdregistry-aws|cgregistry-aws)\\.capgroup\\.com/[^[:space:]]*astro[^[:space:]]*:[^[:space:]]+([[:space:]]+[Aa][Ss][[:space:]]+[^[:space:]]+)?$' '$WS/Dockerfile'"
check "Dockerfile pins the corp pip index" \
    bash -c "grep -q 'cgrepo-aws.capgroup.com/repository/cgpypi/simple' '$WS/Dockerfile'"
check "requirements.txt requests pip runtime for Astro ONBUILD" \
    bash -c "grep -q 'ASTRO_RUNTIME_USE_PIP' '$WS/requirements.txt'"
soft_check "airflow_settings.yaml exists" \
    test -f "$WS/airflow_settings.yaml"
soft_check ".astro/config.yaml exists" \
    test -f "$WS/.astro/config.yaml"

# --- Local Airflow runtime ---
section "Local Airflow runtime"
HINT="run: astro dev start --wait 5m (if a restart/start was interrupted, rerun and wait for completion)"
soft_check "astro scheduler container running" \
    bash -c "astro dev ps 2>/dev/null | grep -Eq 'scheduler-1[[:space:]]+running'"
HINT="run: astro dev start --wait 5m (if a restart/start was interrupted, rerun and wait for completion)"
soft_check "astro api-server container running" \
    bash -c "astro dev ps 2>/dev/null | grep -Eq 'api-server-1[[:space:]]+running'"

# --- Data product scaffolding ---
section "Data product scaffolding"
check "data_products/ exists"           test -d "$WS/data_products"
check "dbt wrapper exists"             test -f "$WS/dbt_wrapper.py"
check "verify-with-databricks gate exists" \
    test -f "$WS/scripts/verify-with-databricks.sh"
# Learner downloads leave out the retired Atlas product.
if [ -d "$WS/data_products/atlas_elt" ]; then
check "atlas_elt dbt profile exists" \
    test -f "$WS/data_products/atlas_elt/dbt_profiles/profiles.yml"
check "atlas_elt dbt project exists" \
    test -f "$WS/data_products/atlas_elt/dbt_project.yml"
check "atlas_elt profile wires DBT_HOST" \
    bash -c "grep -q \"env_var('DBT_HOST'\" '$WS/data_products/atlas_elt/dbt_profiles/profiles.yml'"
check "atlas_elt profile wires DBT_ACCESS_TOKEN" \
    bash -c "grep -q \"env_var('DBT_ACCESS_TOKEN'\" '$WS/data_products/atlas_elt/dbt_profiles/profiles.yml'"
check "atlas_elt profile wires DBT_HTTP_PATH" \
    bash -c "grep -q \"env_var('DBT_HTTP_PATH'\" '$WS/data_products/atlas_elt/dbt_profiles/profiles.yml'"

# dbt parse compiles the manifest WITHOUT opening a Databricks connection, so
# placeholder connection vars are enough to validate the project SQL/refs.
HINT="cd $WS/data_products/atlas_elt && dbt parse via dbt_wrapper.py (shows the compile error)"
soft_check "atlas_elt dbt project parses" \
    run_with_timeout 20 env DBT_HOST=https://placeholder DATABRICKS_HOST=https://placeholder \
        DBT_HTTP_PATH=/sql/1.0/warehouses/x DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/x \
        DBT_ACCESS_TOKEN=dpc_check_placeholder DATABRICKS_TOKEN=dpc_check_placeholder \
        DATABRICKS_AUTH_TYPE=pat "$PYTHON_BIN" "$WS/dbt_wrapper.py" parse \
        --project-dir "$WS/data_products/atlas_elt" \
        --profiles-dir "$WS/data_products/atlas_elt/dbt_profiles" \
        --target local --quiet
else
    echo "  i atlas_elt is not in this project; its scaffolding checks are skipped"
fi

# --- Databricks auth ---
section "Databricks auth"
HINT="run: bash .devcontainer/setup-databricks-dbt.sh"
soft_check "~/.databrickscfg has DEFAULT profile" \
    bash -c 'grep -q "^\[DEFAULT\]" "$HOME/.databrickscfg" 2>/dev/null'
HINT="run: bash .devcontainer/setup-databricks-dbt.sh, then open a NEW terminal"
soft_check "DATABRICKS_HOST is set"  bash -c '[ -n "${DATABRICKS_HOST:-}" ]'
HINT="Databricks OAuth session may be expired or missing; rerun: bash .devcontainer/setup-databricks-dbt.sh (PAT fallback: mise run setup:databricks --pat)"
soft_check "databricks current-user me works"  run_with_timeout 20 databricks current-user me

# Report the active auth mode (single source of truth: the env contract).
printf '  %s active auth mode: %s\n' "$(bold 'i')" "${DPC_DATABRICKS_AUTH_MODE:-unset}"

# In OAuth mode, the local Airflow connections are kept fresh by the background
# refresher. Verify its heartbeat is recent and healthy (read-only; no CLI call).
if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ]; then
    HINT="either OAuth refresher has not run yet, or local Airflow is not up yet; start Airflow with astro dev start --wait 5m, then rerun dpc-check. If still WARN, rerun OAuth setup: mise run setup:databricks"
    set +u
    soft_check "OAuth->Airflow refresher heartbeat is fresh" bash -c '
        f="$HOME/.config/dpc/oauth-refresh-status.json"
        if [ ! -f "$f" ]; then
            echo "OAuth refresher status file is missing (setup/refresh has not run yet)." >&2
            exit 1
        fi
        state=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(\"state\",\"\"))" "$f" 2>/dev/null)
        ts=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(\"last_refresh\",\"\"))" "$f" 2>/dev/null)
        if [ "$state" != "ok" ]; then
            echo "OAuth refresher state is '$state' (expected 'ok')." >&2
            exit 1
        fi
        if ! python3 -c "import sys,datetime as d; t=d.datetime.fromisoformat(sys.argv[1].replace(\"Z\",\"+00:00\")); now=d.datetime.now(d.timezone.utc); sys.exit(0 if (now-t).total_seconds() < 7200 else 1)" "$ts" 2>/dev/null; then
            echo "OAuth refresher heartbeat is stale (>2h since last_refresh)." >&2
            exit 1
        fi
    '
    set -u

    HINT="either local Airflow is not up yet, or Databricks connection is stale/invalid. Start Airflow with astro dev start --wait 5m, then rerun dpc-check. If still WARN, run: mise run databricks:oauth-refresh"
    set +u
    soft_check "OAuth Airflow databricks_default connection works" run_with_timeout 25 bash -c '
      sched=$(docker ps --format "{{.Names}}" | grep -E "^edo-training.*-scheduler-1$" | head -1)
      if [ -z "$sched" ]; then
          echo "Airflow scheduler container not found (local Airflow may not be up yet)." >&2
          exit 1
      fi
      out=$(docker exec "$sched" airflow connections test databricks_default 2>&1)
      rc=$?
      if [ "$rc" -eq 0 ]; then
          exit 0
      fi
      if printf "%s" "$out" | grep -q "Testing connections is disabled"; then
          echo "Airflow is up, but connection testing is disabled in this runtime." >&2
      else
          echo "Connection test failed (Databricks connection may be stale, or Airflow is still starting)." >&2
      fi
      exit 1
    '
    set -u
fi

# --- Summary ---
section "Summary"
HARD_FAIL_COUNT=$(wc -l < "$DPC_HARD_FAIL_FILE" 2>/dev/null || printf '0')

printf '  %s %d   %s %d   %s %d\n\n' \
    "$(green OK:)" "$PASS" \
    "$(red FAIL:)" "$HARD_FAIL_COUNT" \
    "$(yellow WARN:)" "$DPC_WARNINGS"

if [ "$HARD_FAIL_COUNT" -eq 0 ]; then
    if [ "$DPC_WARNINGS" -gt 0 ]; then
        printf '%s\n' "$(yellow 'Healthy. WARNs are usually expected before first-run setup (databricks auth login). See the fix: hints above.')"
    else
        printf '%s\n' "$(green 'All checks passed.')"
    fi
    exit 0
fi

printf '%s\n' "$(red 'One or more checks FAILED. See the fix: hint under each [FAIL] above.')"
exit 1
