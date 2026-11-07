# Databricks Auth Strategy — OAuth→Airflow Refresher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make OAuth the working default for Databricks auth across every local surface by adding a devcontainer-side refresher that keeps the local Airflow Databricks connections supplied with a fresh short-lived OAuth token, with PAT as an unchanged whole-system backup.

**Architecture:** dbt and DAB already consume OAuth through Databricks unified auth (`.mise/env.sh` mints a shell token; the CLI auto-refreshes for bundles), so they need no code change. The only surface that cannot consume the browser OAuth session is local Airflow (the provider hook has no U2M path and ignores `~/.databrickscfg`). We add `.devcontainer/utils/databricks-oauth-refresh.sh`, which runs in the devcontainer (where the OAuth session lives), mints a token with the non-interactive `databricks auth token`, and upserts the `databricks_default` and `caspian-training-databricks` Airflow connections by `docker exec`-ing the Astro scheduler's `airflow connections` CLI. A loop refreshes just before each ~1h token expiry; `dpc-check` reports health.

**Bootstrap contract (important):** the refresher is the rotation mechanism, not the initial provisioning mechanism. Initial setup must always seed Airflow Databricks connection state by default (even if Airflow is currently down). If no fresh token is available during setup, scripts must preserve existing connection credentials rather than blanking them; the refresher then converges live connection passwords once the scheduler is up. Importantly, in OAuth mode `airflow_settings.yaml` is a bootstrap-only shape (host + empty login) and must not contain OAuth access tokens: live tokens are stored in the Airflow metastore connections by the OAuth refresher and are not persisted in local settings files.

**Tech Stack:** Bash, Databricks CLI (`databricks auth token`), Astro/Airflow 3 CLI (`airflow connections`), Docker (inner DinD daemon), Python 3 (JSON/RFC3339 parsing), pytest.

## Global Constraints

- Single Databricks workspace; default host `https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com`.
- Exactly one active auth mode, read from `DPC_DATABRICKS_AUTH_MODE` (`oauth`|`pat`) in `~/.config/dpc/databricks.env`. No mixed state.
- The refresher must be a **no-op** unless `DPC_DATABRICKS_AUTH_MODE=oauth`.
- The refresher must **never** launch a browser: only `databricks auth token` (non-interactive), never `databricks auth login`.
- OAuth re-auth remediation is always `mise run setup:databricks` (renamed from `setup:databricks-oauth`; `.devcontainer/setup-databricks-dbt.sh` without `--pat`); PAT backup is `mise run setup:databricks --pat`. Never tell the user to run raw `databricks auth login`.
- Target Airflow connection IDs: `databricks_default` and `caspian-training-databricks`.
- **Airflow connection shape must be the Bearer shape: empty `login`, token in `password`** (or token in `extra.token`). A non-empty `login` (e.g. legacy `conn_login: 'token'`) makes the provider use HTTP Basic auth, which an OAuth token rejects (401). Verified against provider 7.7.4 with a live U2M token via `DatabricksHook.test_connection()`. This shape works for PAT too (a PAT is also a bearer token).
- Astro scheduler container is discovered by name pattern `^edo-training.*-scheduler-1$` (project hash is dynamic).
- **Local Airflow secrets backend must be `airflow.secrets.metastore.MetastoreBackend`** in `docker-compose.override.yml`. The Astro image defaults to AWS Secrets Manager (kwargs from the tracked root `.env`); `EnvironmentVariablesBackend` (prior value) drops the metastore so DB connections don't resolve for hooks. MetastoreBackend wins over `.env` and is required for connection resolution. Verified via `astro dev restart`.
- Follow existing patterns: `nohup` background self-heal like `.devcontainer/ensure-dockerd.sh`; opt-out env var like `DPC_SKIP_DOCKERD_HEAL`; tests live in `data_products/test_devcontainer_dind_wiring.py` and mostly assert on script *text* via the `_read(path)` helper.
- Any `databricks`/network call added to `.devcontainer/check.sh` must be wrapped in `run_with_timeout` (existing test `test_dpc_check_prevents_interactive_auth_hangs` enforces this).
- Status/heartbeat file: `~/.config/dpc/oauth-refresh-status.json`. Log file: `/var/log/dbx-oauth-refresh.log`. Pidfile: `~/.config/dpc/oauth-refresh.pid`.
- Commit after every task. Run the full targeted test file before each commit: `pytest data_products/test_devcontainer_dind_wiring.py -q`.

---

## File Structure

- **Create** `.devcontainer/utils/databricks-oauth-refresh.sh` — the refresher. Two entrypoints: `--once` (single pass) and `--loop` (expiry-driven daemon). Mode-gated, browser-free, self-discovers the scheduler, upserts both connections (Bearer shape), writes heartbeat/log.
- **Modify** `.devcontainer/setup-databricks-dbt.sh` — remove unreachable dead code left in `validate_pat_token` (housekeeping so the auth script we build on is clean).
- **Modify** `docker-compose.override.yml` — set the local secrets backend to `MetastoreBackend` so DB-stored Databricks connections resolve for hooks/operators.
- **Modify** `.airflow/airflow_settings.yaml.example` — change the tracked connection template to the Bearer shape (empty `conn_login`).
- **Modify** `.devcontainer/utils/setup-airflow-settings.sh` — write connections with empty login (Bearer shape) and, in OAuth mode, launch the refresher loop via `nohup` (respecting the opt-out).
- **Modify** `.mise.toml` — add a `databricks:oauth-refresh` task to (re)start the loop manually.
- **Modify** `.devcontainer/check.sh` — in the "Databricks auth" section, print the active mode and, in OAuth mode, a heartbeat-freshness soft check with the correct remediation hints.
- **Modify** `data_products/test_devcontainer_dind_wiring.py` — TDD tests for each of the above.

---

### Task 1: Housekeeping — remove unreachable dead code in `validate_pat_token`

The earlier PAT-hardening left a duplicate, unreachable block after a `return 0` inside `validate_pat_token` in `.devcontainer/setup-databricks-dbt.sh`. Remove it so the auth script we extend is clean and the function has exactly one validation body.

**Files:**
- Modify: `.devcontainer/setup-databricks-dbt.sh` (the `validate_pat_token` function)
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: a `validate_pat_token` that contains exactly one `curl ... /api/2.0/preview/scim/v2/Me` probe and ends at the first `return 0`. Later tasks/tests may assert the duplicate is gone.

- [ ] **Step 1: Write the failing test**

Add to `data_products/test_devcontainer_dind_wiring.py`:

```python
def test_validate_pat_token_has_no_unreachable_duplicate_block() -> None:
    script = _read(".devcontainer/setup-databricks-dbt.sh")
    # The Me-probe curl must appear exactly once inside validate_pat_token.
    assert script.count('/api/2.0/preview/scim/v2/Me') == 1
    # No code after the function's successful 'return 0' before the closing brace.
    func = script.split("validate_pat_token() {", 1)[1].split("\n}", 1)[0]
    lines_after_return = func.split("return 0", 1)[1].strip()
    assert lines_after_return == "", (
        "validate_pat_token has unreachable code after 'return 0':\n" + lines_after_return
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest data_products/test_devcontainer_dind_wiring.py::test_validate_pat_token_has_no_unreachable_duplicate_block -q`
Expected: FAIL — the `Me` probe currently appears twice and there is unreachable code after `return 0`.

- [ ] **Step 3: Remove the dead block**

In `.devcontainer/setup-databricks-dbt.sh`, edit `validate_pat_token` so it ends immediately after the first success path. Delete everything from the line `return 0` up to (but not including) the function's closing `}` — i.e. remove the comment `# Authorization: ******...` and the entire second `if ! http_code=$(curl ...)` / `if [ "$http_code" != "200" ]` duplicate. The function must end:

```bash
  if [ "$http_code" != "200" ]; then
    local details
    details="$(tr -d '\r\n' <"$probe_file" | cut -c1-300)"
    if [ "${DEBUG_PAT_VALIDATE:-0}" = "1" ]; then
      warn "PAT debug: http_code=$http_code"
    fi
    warn "Databricks PAT token authentication failed for $DATABRICKS_HOST."
    [ -n "$details" ] && warn "PAT validation details: $details"
    warn "Set DATABRICKS_TOKEN to a valid PAT and rerun setup with --pat."
    return 1
  fi

  return 0
}
```

- [ ] **Step 4: Run tests to verify pass (and no regressions)**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -q`
Expected: PASS (new test green; all previously passing tests still pass).

- [ ] **Step 5: Commit**

```bash
git add .devcontainer/setup-databricks-dbt.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "refactor: remove unreachable duplicate in validate_pat_token

The PAT validation function had a second, unreachable curl/Me-probe block after
its successful 'return 0'. Collapse to a single validation body so the auth setup
script we extend for the OAuth refresher is clean.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Airflow connection resolution — metastore secrets backend + Bearer shape

Two prerequisites make the local Airflow Databricks connection actually usable by hooks/operators.
(1) **Resolution:** the secrets backend must be `MetastoreBackend` so DB-stored connections are found —
the prior `EnvironmentVariablesBackend` dropped the metastore and made every DB connection invisible
(and removing it falls back to the image's AWS Secrets Manager default). (2) **Transport:** the tracked
template and the PAT-mode generator both write `conn_login: 'token'`, which forces HTTP Basic auth;
that only works for PATs, and an OAuth token is rejected (401). Fix both to the Bearer shape (empty
login, token in password) so the same shape serves both modes. Both facts were verified live via
`astro dev restart` + `DatabricksHook.test_connection()`.

**Files:**
- Modify: `docker-compose.override.yml` (secrets backend)
- Modify: `.airflow/airflow_settings.yaml.example`
- Modify: `.devcontainer/utils/setup-airflow-settings.sh` (the `connection_block` writer and `replace_connection_block` matcher)
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: a local secrets backend that resolves DB connections, and connection artifacts whose
  `conn_login` is empty. The refresher (Task 3) writes the same empty-login shape to the DB, which now
  resolves because of the metastore backend.

- [ ] **Step 1a: Write the failing secrets-backend test**

Add to `data_products/test_devcontainer_dind_wiring.py`:

```python
def test_compose_override_uses_metastore_secrets_backend() -> None:
    compose = _read("docker-compose.override.yml")
    # MetastoreBackend is required so DB-stored connections resolve for hooks.
    assert "airflow.secrets.metastore.MetastoreBackend" in compose
    # The prior value dropped the metastore and broke DB connections.
    assert "environment_variables.EnvironmentVariablesBackend" not in compose
```

- [ ] **Step 1b: Run it to verify it fails**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k metastore_secrets_backend -q`
Expected: FAIL — the override still names `EnvironmentVariablesBackend`.

- [ ] **Step 1c: Change the secrets backend**

In `docker-compose.override.yml`, replace the `AIRFLOW__SECRETS__BACKEND` value (keep `_KWARGS: "{}"`):

```yaml
    # Local secrets backend: the Astro image defaults to AWS Secrets Manager and
    # the rendered dev1 `.env` supplies its kwargs. For local dev we override to the
    # metastore so DB-stored connections (imported from airflow_settings.yaml, or
    # written by `airflow connections add`) actually resolve for Databricks
    # operators/hooks. Do NOT use EnvironmentVariablesBackend here: it drops the
    # metastore from the search path, so DB connections become invisible. MetastoreBackend
    # is fully local and wins over the `.env` AWS Secrets Manager default.
    AIRFLOW__SECRETS__BACKEND: "airflow.secrets.metastore.MetastoreBackend"
    AIRFLOW__SECRETS__BACKEND_KWARGS: "{}"
```

- [ ] **Step 1d: Run it to verify it passes**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k metastore_secrets_backend -q`
Expected: PASS. (The running stack needs `astro dev restart` to pick up the change — covered in Live Verification.)

- [ ] **Step 1: Write the failing tests**

Add to `data_products/test_devcontainer_dind_wiring.py`:

```python
def test_airflow_settings_template_uses_bearer_connection_shape() -> None:
    tmpl = _read(".airflow/airflow_settings.yaml.example")
    # Bearer requires an EMPTY login; a non-empty login forces HTTP Basic auth,
    # which an OAuth token rejects (verified: 401 via DatabricksHook).
    assert "conn_login: 'token'" not in tmpl
    assert "conn_login: ''" in tmpl


def test_airflow_settings_generator_writes_empty_login() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert "conn_login: 'token'" not in script
    assert "conn_login: ''" in script
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k "bearer_connection_shape or generator_writes_empty_login" -q`
Expected: FAIL — both the template and the generator currently contain `conn_login: 'token'`.

- [ ] **Step 3: Fix the template**

In `.airflow/airflow_settings.yaml.example`, change both connections' `conn_login: 'token'` to `conn_login: ''`. The file becomes:

```yaml
airflow:
  connections:
    - conn_id: 'databricks_default'
      conn_type: 'databricks'
      conn_host: ''
      conn_login: ''
      conn_password: ''
    - conn_id: 'caspian-training-databricks'
      conn_type: 'databricks'
      conn_host: ''
      conn_login: ''
      conn_password: ''
  pools: []
  variables:
    - variable_name: databricks_job_prefix
      variable_value: ""
```

- [ ] **Step 4: Fix the generator**

In `.devcontainer/utils/setup-airflow-settings.sh`, the `connection_block` function writes the login line and `replace_connection_block` matches it. Change both occurrences of `'token'` for `conn_login` to `''`.

In `connection_block`, change:

```python
        "      conn_login: 'token'\n"
```

to:

```python
        "      conn_login: ''\n"
```

In `replace_connection_block`, change the matcher line:

```python
        r"      conn_login: 'token'\n"
```

to:

```python
        r"      conn_login: ''\n"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k "bearer_connection_shape or generator_writes_empty_login" -q`
Expected: PASS. Also re-run any existing template test: `pytest data_products/test_devcontainer_dind_wiring.py -k airflow_settings -q` — update any prior test that asserted `conn_login: 'token'` to expect `conn_login: ''`.

- [ ] **Step 6: Run the full file and commit**

```bash
pytest data_products/test_devcontainer_dind_wiring.py -q
git add docker-compose.override.yml .airflow/airflow_settings.yaml.example .devcontainer/utils/setup-airflow-settings.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "fix: local Airflow can resolve + Bearer-auth Databricks connections

Two verified fixes so Databricks operators/hooks can authenticate locally:
- secrets backend -> MetastoreBackend (EnvironmentVariablesBackend dropped the
  metastore so DB connections were invisible; removing it exposes the image's AWS
  Secrets Manager default). Confirmed via astro dev restart.
- connection shape -> empty login (conn_login: 'token' forces HTTP Basic, which an
  OAuth token rejects with 401; empty login sends Authorization: Bearer, valid for
  both OAuth and PAT). Fix the tracked template and the PAT-mode generator.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Refresher core — single-pass refresh (`--once`)

Create the refresher with a single-pass mode that: gates on OAuth mode, mints a token without a browser, discovers the scheduler, upserts both connections, and writes a heartbeat. This task delivers a runnable `--once` pass; the loop comes in Task 4.

**Files:**
- Create: `.devcontainer/utils/databricks-oauth-refresh.sh`
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: `~/.config/dpc/databricks.env` (`DPC_DATABRICKS_AUTH_MODE`, `DATABRICKS_HOST`), the `databricks` CLI, the inner `docker` daemon, the Astro scheduler's `airflow` CLI.
- Produces: an executable `databricks-oauth-refresh.sh` supporting `--once`. Internal functions later tasks rely on: `refresh_once` (returns 0 on success, 2 if scheduler not up, 3 on mint failure), `write_status <state> <expiry>`, `resolve_scheduler` (echoes container name or empty), `mint_payload` (echoes `databricks auth token` JSON). Heartbeat JSON shape: `{"state": "...", "last_refresh": "<rfc3339>", "token_expiry": "<rfc3339-or-empty>"}`.

- [ ] **Step 1: Write the failing tests**

Add to `data_products/test_devcontainer_dind_wiring.py`:

```python
import os
import subprocess
import tempfile


REFRESHER = ".devcontainer/utils/databricks-oauth-refresh.sh"


def test_oauth_refresher_exists_and_is_executable() -> None:
    path = REPO_ROOT / REFRESHER
    assert path.exists(), "refresher script missing"
    assert os.access(path, os.X_OK), "refresher script must be executable"


def test_oauth_refresher_core_contract() -> None:
    script = _read(REFRESHER)
    # Mode gate: no-op unless oauth.
    assert 'if [ "${DPC_DATABRICKS_AUTH_MODE:-}" != "oauth" ]; then' in script
    # Browser-free minting only.
    assert "databricks auth token" in script
    assert "databricks auth login" not in script
    # Scheduler discovery by dynamic-hash pattern.
    assert "^edo-training.*-scheduler-1$" in script
    # Upserts BOTH connection ids via the Airflow CLI.
    assert "databricks_default" in script
    assert "caspian-training-databricks" in script
    assert "airflow connections add" in script
    assert "airflow connections delete" in script
    # Heartbeat + log destinations from the design.
    assert "oauth-refresh-status.json" in script
    assert "/var/log/dbx-oauth-refresh.log" in script
    # Bearer connection shape: empty login (NOT login: token). An OAuth token is
    # rejected over HTTP Basic, which a non-empty login would trigger.
    assert '"login": ""' in script
    assert '"login": "token"' not in script


def test_oauth_refresher_is_noop_when_mode_is_pat(tmp_path) -> None:
    # Running --once in pat mode must exit 0 without touching databricks/docker.
    home = tmp_path
    cfg_dir = home / ".config" / "dpc"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "databricks.env").write_text("export DPC_DATABRICKS_AUTH_MODE=pat\n")
    # A PATH with NO databricks/docker so any attempt to call them would fail.
    bindir = tmp_path / "bin"
    bindir.mkdir()
    env = {"HOME": str(home), "PATH": str(bindir)}
    result = subprocess.run(
        ["bash", str(REPO_ROOT / REFRESHER), "--once"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k oauth_refresher -q`
Expected: FAIL — script does not exist yet.

- [ ] **Step 3: Create the refresher (single-pass)**

Create `.devcontainer/utils/databricks-oauth-refresh.sh`:

```bash
#!/usr/bin/env bash
# Keep local Airflow's Databricks connections supplied with a fresh short-lived
# OAuth token. Runs in the devcontainer, where the OAuth session lives.
#
#   databricks-oauth-refresh.sh --once   # single refresh pass
#   databricks-oauth-refresh.sh --loop   # expiry-driven daemon (Task 4)
#
# No-op unless DPC_DATABRICKS_AUTH_MODE=oauth. Never launches a browser: it only
# calls the non-interactive `databricks auth token`.

set -u

CONFIG_FILE="$HOME/.config/dpc/databricks.env"
STATUS_FILE="$HOME/.config/dpc/oauth-refresh-status.json"
LOG_FILE="/var/log/dbx-oauth-refresh.log"
CONN_IDS="databricks_default caspian-training-databricks"

log() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >>"$LOG_FILE" 2>/dev/null || true
}

write_status() {
  local state=$1 expiry=${2:-}
  mkdir -p "$(dirname "$STATUS_FILE")" 2>/dev/null || true
  printf '{"state": "%s", "last_refresh": "%s", "token_expiry": "%s"}\n' \
    "$state" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$expiry" >"$STATUS_FILE" 2>/dev/null || true
}

load_contract() {
  [ -f "$CONFIG_FILE" ] && . "$CONFIG_FILE"
}

resolve_scheduler() {
  docker ps --format '{{.Names}}' 2>/dev/null | grep -E '^edo-training.*-scheduler-1$' | head -1
}

mint_payload() {
  databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json 2>/dev/null
}

_json_field() {
  # _json_field <field>  (reads JSON from stdin)
  python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get(sys.argv[1], ""))
except Exception:
    print("")' "$1" 2>/dev/null
}

upsert_connection() {
  local sched=$1 conn_id=$2 host=$3 token=$4 conn_json
  # Bearer shape: EMPTY login + token in password. An OAuth access token is only
  # accepted as Authorization: Bearer; a non-empty login makes the provider use
  # HTTP Basic auth, which OAuth rejects (verified: 401 vs 200 via DatabricksHook).
  conn_json=$(printf '{"conn_type": "databricks", "host": "%s", "login": "", "password": "%s"}' "$host" "$token")
  docker exec "$sched" airflow connections delete "$conn_id" >/dev/null 2>&1 || true
  docker exec "$sched" airflow connections add "$conn_id" --conn-json "$conn_json" >/dev/null 2>&1
}

# Echoes the token expiry (rfc3339) on success; sets globals REFRESH_RC.
refresh_once() {
  load_contract
  if [ "${DPC_DATABRICKS_AUTH_MODE:-}" != "oauth" ]; then
    log "mode=${DPC_DATABRICKS_AUTH_MODE:-unset}; not oauth, no-op"
    REFRESH_EXPIRY=""
    return 0
  fi

  if [ -z "${DATABRICKS_HOST:-}" ]; then
    log "DATABRICKS_HOST unset; cannot refresh"
    write_status "misconfigured" ""
    REFRESH_EXPIRY=""
    return 3
  fi

  local sched
  sched=$(resolve_scheduler)
  if [ -z "$sched" ]; then
    log "scheduler not running yet; skipping this pass"
    write_status "scheduler_down" ""
    REFRESH_EXPIRY=""
    return 2
  fi

  local payload token expiry
  payload=$(mint_payload)
  token=$(printf '%s' "$payload" | _json_field access_token)
  expiry=$(printf '%s' "$payload" | _json_field expiry)
  if [ -z "$token" ]; then
    log "databricks auth token returned no access_token (session likely expired)"
    write_status "session_expired" ""
    REFRESH_EXPIRY=""
    return 3
  fi

  local cid
  for cid in $CONN_IDS; do
    upsert_connection "$sched" "$cid" "$DATABRICKS_HOST" "$token"
  done

  log "refreshed connections ($CONN_IDS) token_expiry=$expiry"
  write_status "ok" "$expiry"
  REFRESH_EXPIRY="$expiry"
  return 0
}

main() {
  local mode=${1:---once}
  case "$mode" in
    --once)
      refresh_once
      exit $?
      ;;
    --loop)
      echo "loop mode not implemented yet" >&2
      exit 64
      ;;
    *)
      echo "usage: databricks-oauth-refresh.sh [--once|--loop]" >&2
      exit 64
      ;;
  esac
}

main "$@"
```

Then make it executable:

```bash
chmod +x .devcontainer/utils/databricks-oauth-refresh.sh
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k oauth_refresher -q`
Expected: PASS (all three refresher tests green; pat-mode `--once` exits 0 without needing databricks/docker).

- [ ] **Step 5: Run the full file and commit**

```bash
pytest data_products/test_devcontainer_dind_wiring.py -q
git add .devcontainer/utils/databricks-oauth-refresh.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: add OAuth->Airflow refresher single-pass (--once)

Mint a short-lived OAuth token with non-interactive 'databricks auth token' and
upsert the databricks_default and caspian-training-databricks Airflow connections
via the scheduler's airflow CLI. No-op unless DPC_DATABRICKS_AUTH_MODE=oauth; never
launches a browser. Writes a heartbeat to ~/.config/dpc/oauth-refresh-status.json.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 4: Refresher loop — expiry-driven daemon (`--loop`)

Add the `--loop` entrypoint: single-instance guard, opt-out env var, and an expiry-driven sleep that refreshes ~120s before the 1h token expiry (with a safe fallback when expiry is unknown or a pass fails).

**Files:**
- Modify: `.devcontainer/utils/databricks-oauth-refresh.sh`
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: `refresh_once` and `REFRESH_EXPIRY` from Task 3.
- Produces: `--loop` behavior; honors `DPC_SKIP_OAUTH_REFRESH` (exit 0 immediately) and a pidfile at `~/.config/dpc/oauth-refresh.pid`. Sleep helper `seconds_until_refresh <expiry>` echoes an integer (expiry−120s, floored to 30s; `3300` when expiry empty/unparseable).

- [ ] **Step 1: Write the failing tests**

Add to `data_products/test_devcontainer_dind_wiring.py`:

```python
def test_oauth_refresher_loop_contract() -> None:
    script = _read(REFRESHER)
    assert "--loop" in script
    # Opt-out consistent with DPC_SKIP_DOCKERD_HEAL.
    assert "DPC_SKIP_OAUTH_REFRESH" in script
    # Single-instance guard.
    assert "oauth-refresh.pid" in script
    assert "kill -0" in script
    # Expiry-driven sleep with a safe fallback (~55 min) and a lead time.
    assert "seconds_until_refresh" in script
    assert "3300" in script
    assert "120" in script


def test_oauth_refresher_loop_opts_out_immediately(tmp_path) -> None:
    home = tmp_path
    (home / ".config" / "dpc").mkdir(parents=True)
    (home / ".config" / "dpc" / "databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
    )
    env = {
        "HOME": str(home),
        "PATH": os.environ.get("PATH", ""),
        "DPC_SKIP_OAUTH_REFRESH": "1",
    }
    result = subprocess.run(
        ["bash", str(REPO_ROOT / REFRESHER), "--loop"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_seconds_until_refresh_helper(tmp_path) -> None:
    # Source the script and call the helper directly.
    probe = (
        f'source "{REPO_ROOT / REFRESHER}" --source-only 2>/dev/null; '
        'seconds_until_refresh ""; '
        'echo "---"; '
        'seconds_until_refresh "not-a-date"'
    )
    result = subprocess.run(
        ["bash", "-c", probe],
        env={"HOME": str(tmp_path), "PATH": os.environ.get("PATH", "")},
        capture_output=True, text=True, timeout=30,
    )
    out = [line for line in result.stdout.splitlines() if line.strip()]
    # Empty and unparseable expiry both fall back to 3300.
    assert out[0] == "3300"
    assert out[-1] == "3300"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k "loop or seconds_until_refresh" -q`
Expected: FAIL — `--loop` prints "not implemented", no `seconds_until_refresh`, no `--source-only` guard.

- [ ] **Step 3: Implement the loop**

In `.devcontainer/utils/databricks-oauth-refresh.sh`, add the helper and loop, and add a `--source-only` guard so tests can source the file without running `main`. Insert `seconds_until_refresh` after `_json_field`:

```bash
seconds_until_refresh() {
  # Echo seconds to sleep before the next refresh: (expiry - 120s), floored to
  # 30s. Falls back to 3300s (55 min) when expiry is empty/unparseable.
  local expiry=$1
  if [ -z "$expiry" ]; then
    echo 3300
    return 0
  fi
  python3 -c '
import sys, datetime
raw = sys.argv[1]
try:
    exp = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    secs = int((exp - now).total_seconds()) - 120
    print(max(secs, 30))
except Exception:
    print(3300)
' "$expiry" 2>/dev/null || echo 3300
}

run_loop() {
  if [ -n "${DPC_SKIP_OAUTH_REFRESH:-}" ]; then
    log "DPC_SKIP_OAUTH_REFRESH set; loop disabled"
    exit 0
  fi

  local pidfile="$HOME/.config/dpc/oauth-refresh.pid"
  mkdir -p "$(dirname "$pidfile")" 2>/dev/null || true
  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile" 2>/dev/null)" 2>/dev/null; then
    log "refresher already running (pid $(cat "$pidfile")); exiting"
    exit 0
  fi
  echo $$ >"$pidfile"
  trap 'rm -f "$pidfile"' EXIT

  local sleep_s
  while :; do
    refresh_once
    case $? in
      0) sleep_s=$(seconds_until_refresh "${REFRESH_EXPIRY:-}") ;;   # fresh; sleep to near-expiry
      2) sleep_s=30 ;;                                               # scheduler down; retry soon
      *) sleep_s=60 ;;                                               # mint/misconfig failure; back off
    esac
    log "sleeping ${sleep_s}s before next refresh"
    sleep "$sleep_s"
  done
}
```

Update `main` to handle `--loop` and the `--source-only` guard:

```bash
main() {
  local mode=${1:---once}
  case "$mode" in
    --once)
      refresh_once
      exit $?
      ;;
    --loop)
      run_loop
      ;;
    --source-only)
      return 0
      ;;
    *)
      echo "usage: databricks-oauth-refresh.sh [--once|--loop]" >&2
      exit 64
      ;;
  esac
}

main "$@"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k "loop or seconds_until_refresh" -q`
Expected: PASS (opt-out exits 0; helper returns 3300 for empty and unparseable input).

- [ ] **Step 5: Run the full file and commit**

```bash
pytest data_products/test_devcontainer_dind_wiring.py -q
git add .devcontainer/utils/databricks-oauth-refresh.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: add expiry-driven loop to OAuth->Airflow refresher

--loop refreshes ~120s before each 1h token expiry (fallback 55m), guarded by a
pidfile and the DPC_SKIP_OAUTH_REFRESH opt-out. Scheduler-down and mint failures
back off and retry so the loop self-heals once Astro is up.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 5: Auto-start the loop from setup + add a mise task

In OAuth mode, `setup-airflow-settings.sh` should kick the loop off in the background (nohup, self-heal pattern) so a learner never starts it by hand. Also add a `mise run databricks:oauth-refresh` task to (re)start it manually.

**Post-implementation note:** a later regression showed that "start refresher" alone is insufficient if setup does not bootstrap connections or if setup rewrites existing credentials to blank while token minting is unavailable. The expected behavior is now explicit: setup seeds/preserves connection state; refresher rotates credentials when possible. A second regression then surfaced in OAuth mode: setup minted a fresh token in shell scope but did not export it to the Python renderer, so `airflow_settings.yaml` kept a stale PAT while logs claimed OAuth was written. The fix is to always mint in OAuth mode and export `DPC_DATABRICKS_AUTH_MODE`, `DATABRICKS_HOST`, `DBT_HOST`, and `DATABRICKS_TOKEN` before rendering.

**Files:**
- Modify: `.devcontainer/utils/setup-airflow-settings.sh`
- Modify: `.mise.toml`
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: `.devcontainer/utils/databricks-oauth-refresh.sh --loop` from Tasks 3–4; `DPC_DATABRICKS_AUTH_MODE` from the sourced contract.
- Produces: a background loop started at setup time in OAuth mode; a `databricks:oauth-refresh` mise task.

- [ ] **Step 1: Write the failing tests**

Add to `data_products/test_devcontainer_dind_wiring.py`:

```python
def test_airflow_setup_starts_oauth_refresher_in_oauth_mode() -> None:
    script = _read(".devcontainer/utils/setup-airflow-settings.sh")
    assert "databricks-oauth-refresh.sh" in script
    assert "--loop" in script
    assert "nohup" in script
    # Only in oauth mode.
    assert 'DPC_DATABRICKS_AUTH_MODE:-}" = "oauth"' in script
    # Respect the opt-out.
    assert "DPC_SKIP_OAUTH_REFRESH" in script


def test_mise_has_oauth_refresh_task() -> None:
    toml = _read(".mise.toml")
    assert '[tasks."databricks:oauth-refresh"]' in toml
    assert "databricks-oauth-refresh.sh" in toml
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k "starts_oauth_refresher or oauth_refresh_task" -q`
Expected: FAIL — neither the setup hook nor the mise task exists.

- [ ] **Step 3: Add the setup hook**

At the end of `.devcontainer/utils/setup-airflow-settings.sh` (after the existing auth-mode echo block), append:

```bash
# In OAuth mode, keep the Airflow Databricks connections fresh with a background
# refresher (same nohup self-heal pattern as ensure-dockerd.sh). No-op in PAT mode
# (PAT is long-lived) and when the learner opts out.
if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ] && [ -z "${DPC_SKIP_OAUTH_REFRESH:-}" ]; then
  REFRESHER="$(cd "$(dirname "$0")" && pwd)/databricks-oauth-refresh.sh"
  if [ -x "$REFRESHER" ]; then
    nohup "$REFRESHER" --loop >/var/log/dbx-oauth-refresh.log 2>&1 </dev/null &
    echo "  Started OAuth->Airflow token refresher (background). Check: dpc-check"
  fi
fi
```

- [ ] **Step 4: Add the mise task**

In `.mise.toml`, after the `[tasks."setup:airflow-settings"]` block, add:

```toml
[tasks."databricks:oauth-refresh"]
description = "Restart the OAuth->Airflow token refresher (OAuth mode only)"
run = "nohup .devcontainer/utils/databricks-oauth-refresh.sh --loop >/var/log/dbx-oauth-refresh.log 2>&1 </dev/null & echo started"
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k "starts_oauth_refresher or oauth_refresh_task" -q`
Expected: PASS.

- [ ] **Step 6: Run the full file and commit**

```bash
pytest data_products/test_devcontainer_dind_wiring.py -q
git add .devcontainer/utils/setup-airflow-settings.sh .mise.toml data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: auto-start OAuth refresher at setup + add mise task

In OAuth mode, setup-airflow-settings.sh launches the refresher loop via nohup
(respecting DPC_SKIP_OAUTH_REFRESH); add 'mise run databricks:oauth-refresh' to
restart it manually.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 6: `dpc-check` health — report mode + heartbeat freshness + remediation

Extend the "Databricks auth" section of `.devcontainer/check.sh` to print the active mode and, in OAuth mode, a soft check that the refresher heartbeat is recent and `state` is `ok`, with remediation that points at the setup script (not raw `databricks auth login`).

**Files:**
- Modify: `.devcontainer/check.sh`
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: `~/.config/dpc/oauth-refresh-status.json` (written by Tasks 3–4); `DPC_DATABRICKS_AUTH_MODE` (already sourced near the top of `check.sh`).
- Produces: new report/soft-check lines. No new network calls (reads a local file), so the existing anti-hang test stays green.

- [ ] **Step 1: Write the failing tests**

Add to `data_products/test_devcontainer_dind_wiring.py`:

```python
def test_dpc_check_reports_auth_mode_and_refresher_health() -> None:
    script = _read(".devcontainer/check.sh")
    # Reports the active mode.
    assert "DPC_DATABRICKS_AUTH_MODE" in script
    # Heartbeat freshness check in oauth mode.
    assert "oauth-refresh-status.json" in script
    # Remediation points at the setup script (no --pat), never raw auth login.
    assert "setup:databricks" in script or "setup-databricks-dbt.sh" in script
    # PAT backup is offered as the fallback.
    assert "--pat" in script


def test_dpc_check_refresher_health_is_read_only(tmp_path) -> None:
    # The new heartbeat check must not shell out to databricks/network — grep the
    # oauth-status region for a network call.
    script = _read(".devcontainer/check.sh")
    region = script.split("oauth-refresh-status.json", 1)[1][:400]
    assert "databricks " not in region, "heartbeat check must be read-only (no CLI call)"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k "reports_auth_mode or refresher_health_is_read_only" -q`
Expected: FAIL — `check.sh` has no mode report or heartbeat check yet.

- [ ] **Step 3: Add the health block**

In `.devcontainer/check.sh`, inside the `section "Databricks auth"` block (after the existing `soft_check "databricks current-user me works" ...` line and before the final summary), add:

```bash
# Report the active auth mode (single source of truth: the env contract).
printf '  %s active auth mode: %s\n' "$(bold 'i')" "${DPC_DATABRICKS_AUTH_MODE:-unset}"

# In OAuth mode, the local Airflow connections are kept fresh by the background
# refresher. Verify its heartbeat is recent and healthy (read-only; no CLI call).
if [ "${DPC_DATABRICKS_AUTH_MODE:-}" = "oauth" ]; then
    HINT="rerun OAuth setup: mise run setup:databricks (i.e. .devcontainer/setup-databricks-dbt.sh, no --pat); or use PAT backup: mise run setup:databricks --pat"
    soft_check "OAuth->Airflow refresher heartbeat is fresh" bash -c '
        f="$HOME/.config/dpc/oauth-refresh-status.json"
        [ -f "$f" ] || exit 1
        state=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(\"state\",\"\"))" "$f" 2>/dev/null)
        ts=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(\"last_refresh\",\"\"))" "$f" 2>/dev/null)
        [ "$state" = "ok" ] || exit 1
        # Fresh if last_refresh is within the last 2 hours.
        python3 -c "import sys,datetime as d; t=d.datetime.fromisoformat(sys.argv[1].replace(\"Z\",\"+00:00\")); now=d.datetime.now(d.timezone.utc); sys.exit(0 if (now-t).total_seconds() < 7200 else 1)" "$ts" 2>/dev/null
    '
fi
```

- [ ] **Step 4: Run tests to verify they pass (and anti-hang test still green)**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k "dpc_check" -q`
Expected: PASS — new checks green; `test_dpc_check_prevents_interactive_auth_hangs` and `test_dpc_check_matches_documented_health_contract` still pass.

- [ ] **Step 5: Run the full file and commit**

```bash
pytest data_products/test_devcontainer_dind_wiring.py -q
git add .devcontainer/check.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: dpc-check reports auth mode and OAuth refresher heartbeat

Print the active DPC_DATABRICKS_AUTH_MODE and, in OAuth mode, a read-only soft check
that the refresher heartbeat is recent and healthy. Remediation points at the OAuth
setup script (no --pat) with the PAT backup as fallback.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 7: Documentation — single-mode model and remediation

Document the OAuth-primary / PAT-backup model, the refresher, and remediation in the devcontainer README so learners understand the one-mode contract and how to recover.

**Files:**
- Modify: `.devcontainer/README.md` (the "Databricks Auth" area referenced in its Quick Navigation)
- Test: `data_products/test_devcontainer_dind_wiring.py`

**Interfaces:**
- Consumes: behavior from all prior tasks.
- Produces: a documentation section describing modes, the refresher, and remediation commands.

- [ ] **Step 1: Write the failing test**

Add to `data_products/test_devcontainer_dind_wiring.py`:

```python
def test_readme_documents_single_mode_auth_and_refresher() -> None:
    readme = _read(".devcontainer/README.md")
    assert "DPC_DATABRICKS_AUTH_MODE" in readme
    # Both modes named, OAuth primary + PAT backup.
    assert "OAuth" in readme and "PAT" in readme
    # The refresher is described.
    assert "databricks-oauth-refresh.sh" in readme or "token refresher" in readme
    # Remediation points at the setup script, not raw auth login.
    assert "setup:databricks" in readme or "setup-databricks-dbt.sh" in readme
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k readme_documents_single_mode -q`
Expected: FAIL — README does not yet cover the single-mode model or the refresher.

- [ ] **Step 3: Add the documentation**

In `.devcontainer/README.md`, first reconcile the stale PAT sentence so the section stays internally consistent with the now-interactive PAT flow. Replace this line:

```markdown
PAT authentication is an explicit fallback: add a real token to the git-ignored `.devcontainer/.env`, then run `bash .devcontainer/setup-databricks-dbt.sh --pat`. The placeholder token in the tracked example is never treated as a credential.
```

with:

```markdown
PAT authentication is an explicit fallback: run `bash .devcontainer/setup-databricks-dbt.sh --pat`. It prompts for the workspace host and token (or reuses `DATABRICKS_TOKEN` if already set), validates the token before writing config, and lets you pick a SQL warehouse. The placeholder token in the tracked example is never treated as a credential.
```

Then, under the existing "Databricks Auth" section (near the bottom, referenced by the Quick Navigation `[Databricks Auth](#databricks-auth)`), add:

```markdown
### Databricks auth: one mode at a time (OAuth primary, PAT backup)

This repo uses a single active auth mode, recorded in
`~/.config/dpc/databricks.env` as `DPC_DATABRICKS_AUTH_MODE` (`oauth` or `pat`).
Every surface — local dbt, Databricks Asset Bundles, and local Airflow — uses that
one mode. You do not mix OAuth and PAT.

- **OAuth (default, recommended):** one browser login.
  Run `mise run setup:databricks` (renamed from `setup:databricks-oauth`; i.e. `.devcontainer/setup-databricks-dbt.sh`
  without `--pat`). dbt and bundles refresh automatically. Local Airflow cannot use
  the browser session directly, so a background **token refresher**
  (`.devcontainer/utils/databricks-oauth-refresh.sh`) keeps the `databricks_default`
  and `caspian-training-databricks` connections supplied with a fresh token. It starts
  automatically in OAuth mode; restart it with `mise run databricks:oauth-refresh`.
  Disable it with `DPC_SKIP_OAUTH_REFRESH=1`.

- **PAT (backup):** if OAuth (or the Airflow refresher) is broken and you need in
  quickly, run `.devcontainer/setup-databricks-dbt.sh --pat` and paste a token from
  the Databricks UI. This switches the whole system to the PAT.

**Check health / recover:** run `dpc-check`. It prints the active mode and, in OAuth
mode, whether the refresher heartbeat is fresh. If it is stale, re-run
`mise run setup:databricks`, or switch to the PAT backup above.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest data_products/test_devcontainer_dind_wiring.py -k readme_documents_single_mode -q`
Expected: PASS.

- [ ] **Step 5: Run the full file and commit**

```bash
pytest data_products/test_devcontainer_dind_wiring.py -q
git add .devcontainer/README.md data_products/test_devcontainer_dind_wiring.py
git commit -m "docs: document single-mode Databricks auth and OAuth refresher

Explain the one-active-mode model (DPC_DATABRICKS_AUTH_MODE), OAuth-primary with the
background Airflow token refresher, and PAT as the whole-system backup, with dpc-check
as the recovery entrypoint.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Live Verification (after Task 7, in the running devcontainer)

These are manual, human-in-the-loop checks — not automated — because they require a real browser OAuth login and a running Astro stack.

- [ ] **Secrets backend takes effect:** After changing `docker-compose.override.yml`, run `astro dev restart --wait 3m`, then confirm the effective backend: `docker exec <edo-training_*-scheduler-1> airflow config get-value secrets backend` returns `airflow.secrets.metastore.MetastoreBackend`. Without this, DB connections resolve as "isn't defined" for hooks.
- [ ] **OAuth end-to-end:** In the devcontainer terminal, run `mise run setup:databricks` and complete the browser login. Then `astro dev start --wait 3m`. Confirm the refresher started (`dpc-check` shows a fresh heartbeat) and that a Databricks connection works from Airflow: `docker exec <edo-training_*-scheduler-1> airflow connections get databricks_default -o json` shows an **empty login** and a non-null password, and `airflow connections test databricks_default` (or a `DatabricksHook.test_connection()`) returns success. Run an Atlas DAG task and confirm it authenticates.
- [ ] **Bearer shape regression guard:** Confirm the generated `airflow_settings.yaml` and both live connections have empty `login` (not `token`). A non-empty login silently downgrades OAuth to HTTP Basic and fails with 401.
- [ ] **Stale-PAT replacement check:** Seed `airflow_settings.yaml` with a PAT-like `dapi...` connection password, then run `bash .devcontainer/utils/setup-airflow-settings.sh` in OAuth mode. Confirm both Databricks connection passwords are rewritten to a JWT-like value and match `databricks auth token --profile DEFAULT --output json` (`access_token`).
- [ ] **Silent refresh:** Confirm `/var/log/dbx-oauth-refresh.log` shows a subsequent refresh with no browser prompt.
- [ ] **PAT backup:** Run `mise run setup:databricks --pat`, paste a valid token; confirm `dpc-check` reports mode `pat`, both Databricks connection passwords are rewritten to the PAT value, and the refresher is a no-op (its loop logs "not oauth, no-op").
- [ ] **Windows spot check (if available):** On a Windows Docker Desktop host, confirm the browser callback completes and the refresher path works after `astro dev start`.

---

## Self-Review

**Spec coverage:**
- §2 single mode / §8 idempotency → the mode gate lives in the refresher (Tasks 3–4) and every surface reads `DPC_DATABRICKS_AUTH_MODE`; switching modes is handled by the existing setup script (unchanged) plus the mode-gated refresher. ✅
- §4.1 dbt / §4.2 DAB → no code change required (documented in §4; verified in Live Verification). ✅
- §4.3 Airflow secrets backend (MetastoreBackend) + Bearer connection shape → Task 2 (compose override + template + generator); refresher writes the same shape to the DB in Task 3. ✅
- §4.3 Airflow / §6 refresher → Tasks 3–5. ✅
- §6 health via dpc-check → Task 6. ✅
- §6/§7 browser-free + remediation entrypoint → enforced by Global Constraints and asserted in Tasks 3 and 6. ✅
- §9 testing → TDD in every task + Live Verification for the things unit tests cannot cover (real browser login, running Astro, Bearer-vs-Basic behavior). ✅
- Housekeeping of dead code in the auth script we extend → Task 1. ✅

**Placeholder scan:** No TBD/TODO; every code step shows complete content. ✅

**Type/name consistency:** `refresh_once`, `REFRESH_EXPIRY`, `seconds_until_refresh`, `resolve_scheduler`, `mint_payload`, `write_status`, status path `~/.config/dpc/oauth-refresh-status.json`, pidfile `~/.config/dpc/oauth-refresh.pid`, log `/var/log/dbx-oauth-refresh.log`, conn IDs `databricks_default` / `caspian-training-databricks`, scheduler pattern `^edo-training.*-scheduler-1$`, Bearer connection shape (empty `login`) — used identically across Tasks 2–7. ✅
