# Airflow OAuth Token Drift Prevention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent local Airflow Databricks 403s caused by restart-time token drift by making OAuth token state single-source in metastore and strengthening runtime health checks.

**Architecture:** Keep `airflow_settings.yaml` as connection shape/host bootstrap only and remove OAuth token persistence from that file. Make `.devcontainer/utils/databricks-oauth-refresh.sh` the sole OAuth token writer for live Airflow connections, with immediate refresh when scheduler appears/reappears. Extend `dpc-check` to verify real Airflow Databricks connection usability (not just refresher heartbeat).

**Tech Stack:** Bash, Python, Databricks CLI, Airflow CLI, Astro CLI, pytest.

## Global Constraints

- OAuth remains the default local auth mode; PAT fallback behavior remains available and unchanged.
- In OAuth mode, do not persist OAuth access tokens in `airflow_settings.yaml`.
- Databricks Airflow connection shape must remain `conn_login: ''` with token in `conn_password`.
- Refresher must stay non-interactive (never call `databricks auth login`).
- `dpc-check` network/Databricks calls must be wrapped by `run_with_timeout`.
- Keep existing connection IDs: `databricks_default` and `caspian-training-databricks`.
- Follow existing tests in `data_products/test_devcontainer_dind_wiring.py` and extend them first (TDD).

---

## File Structure

- **Modify:** `.devcontainer/utils/setup-airflow-settings.sh`  
  Responsibility: bootstrap local `airflow_settings.yaml` without persisting OAuth token; still start refresher in OAuth mode.
- **Modify:** `.devcontainer/utils/databricks-oauth-refresh.sh`  
  Responsibility: detect scheduler reappearance and force immediate sync before long expiry sleep.
- **Modify:** `.devcontainer/check.sh`  
  Responsibility: add OAuth-mode live Airflow Databricks connection usability check.
- **Modify:** `data_products/test_devcontainer_dind_wiring.py`  
  Responsibility: regression tests for file-token persistence prevention, refresher scheduler reappearance behavior, and `dpc-check` live validation logic.
- **Modify:** `docs/superpowers/specs/2026-07-21-databricks-auth-strategy-design.md`  
  Responsibility: align architecture narrative with single token source in metastore.
- **Modify:** `docs/superpowers/plans/2026-07-21-databricks-auth-strategy.md`  
  Responsibility: align prior implementation plan narrative with observed drift edge case and new fix.
- **Modify:** `.devcontainer/README.md`  
  Responsibility: user-facing local auth behavior and recovery flow.
- **Modify (if needed):** `.devcontainer/TROUBLESHOOTING.md`  
  Responsibility: correct troubleshooting guidance for Databricks token drift and recovery.

### Task 1: Prevent OAuth token persistence in `airflow_settings.yaml`

**Files:**
- Modify: `data_products/test_devcontainer_dind_wiring.py`
- Modify: `.devcontainer/utils/setup-airflow-settings.sh`

**Interfaces:**
- Consumes: existing `setup-airflow-settings.sh` rendering flow (`connection_block`, `replace_connection_block`).
- Produces: OAuth-mode file rendering that updates host/login shape but leaves `conn_password` empty or unchanged from empty template (never writes live OAuth token).

- [ ] **Step 1: Write failing tests**

Add tests near existing airflow-settings tests:

```python
def test_airflow_settings_oauth_mode_does_not_persist_access_token(tmp_path) -> None:
    script = REPO_ROOT / ".devcontainer/utils/setup-airflow-settings.sh"
    workspace = tmp_path / "ws"
    (workspace / ".airflow").mkdir(parents=True, exist_ok=True)
    (workspace / ".airflow/airflow_settings.yaml.example").write_text(
        _read(".airflow/airflow_settings.yaml.example"),
        encoding="utf-8",
    )
    (workspace / "airflow_settings.yaml").write_text(
        _read(".airflow/airflow_settings.yaml.example"),
        encoding="utf-8",
    )
    (workspace / ".config/dpc").mkdir(parents=True, exist_ok=True)
    (workspace / ".config/dpc/databricks.env").write_text(
        "export DPC_DATABRICKS_AUTH_MODE=oauth\n"
        "export DATABRICKS_HOST=https://workspace\n",
        encoding="utf-8",
    )
    fake_bin = workspace / "bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    (fake_bin / "databricks").write_text(
        "#!/usr/bin/env bash\n"
        "if [ \"$1\" = \"auth\" ] && [ \"$2\" = \"token\" ]; then\n"
        "  echo '{\"access_token\":\"abc.jwt.token\"}'\n"
        "  exit 0\n"
        "fi\n"
        "if [ \"$1\" = \"current-user\" ]; then\n"
        "  echo '{\"userName\":\"dev@capgroup.com\"}'\n"
        "  exit 0\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    (fake_bin / "databricks").chmod(0o755)

    subprocess.run(
        ["bash", str(script)],
        cwd=workspace,
        check=True,
        env={**os.environ, "HOME": str(workspace), "PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )
    rendered = (workspace / "airflow_settings.yaml").read_text(encoding="utf-8")
    assert "abc.jwt.token" not in rendered
```

- [ ] **Step 2: Run test to verify failure**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py::test_airflow_settings_oauth_mode_does_not_persist_access_token -q`

Expected: FAIL (current OAuth path writes token into file).

- [ ] **Step 3: Implement minimal script change**

In `.devcontainer/utils/setup-airflow-settings.sh`, change token selection/write behavior:

```python
auth_mode = os.environ.get("DPC_DATABRICKS_AUTH_MODE", "").strip().lower()
host_value = os.environ.get("DATABRICKS_HOST") or os.environ.get("DBT_HOST") or ""

if auth_mode == "pat":
    token_value = os.environ.get("DATABRICKS_TOKEN", "")
elif auth_mode == "oauth":
    token_value = ""  # Why: OAuth token state must live only in metastore via refresher.
else:
    token_value = ""
```

and keep Databricks connection block updates conditioned so OAuth does not inject token into file.

- [ ] **Step 4: Run focused tests to verify pass**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py -k "airflow_settings_script_rewrites_connections_with_minted_oauth_token or oauth_mode_does_not_persist_access_token" -q`

Expected: old minted-oauth token persistence test fails and must be updated/replaced; new contract test passes.

- [ ] **Step 5: Update outdated test expectations**

Replace any test asserting OAuth token is written to file with assertions that:

```python
assert "abc.jwt.token" not in rendered
assert "conn_host: 'https://workspace'" in rendered
assert "conn_login: ''" in rendered
```

- [ ] **Step 6: Run full target file**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py -q`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add .devcontainer/utils/setup-airflow-settings.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "fix: stop persisting oauth tokens in airflow settings

In OAuth mode, keep airflow_settings.yaml as connection shape/host bootstrap
only and leave live token state to the metastore refresher to prevent
restart-time token drift.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Add scheduler reappearance convergence to refresher

**Files:**
- Modify: `data_products/test_devcontainer_dind_wiring.py`
- Modify: `.devcontainer/utils/databricks-oauth-refresh.sh`

**Interfaces:**
- Consumes: existing `resolve_scheduler`, `refresh_once`, `run_loop`.
- Produces: loop behavior that forces immediate refresh when scheduler transitions from absent to present or container ID changes.

- [ ] **Step 1: Write failing test**

Add script-content test:

```python
def test_oauth_refresher_forces_refresh_on_scheduler_reappearance() -> None:
    script = _read(".devcontainer/utils/databricks-oauth-refresh.sh")
    assert "last_scheduler" in script
    assert "scheduler_changed" in script
    assert "sleep_s=1" in script or "sleep_s=0" in script
```

- [ ] **Step 2: Run test to verify failure**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py::test_oauth_refresher_forces_refresh_on_scheduler_reappearance -q`

Expected: FAIL.

- [ ] **Step 3: Implement minimal loop enhancement**

In `run_loop()` of `.devcontainer/utils/databricks-oauth-refresh.sh`, track scheduler identity:

```bash
local sleep_s last_scheduler="" current_scheduler=""
while :; do
  current_scheduler="$(resolve_scheduler || true)"
  scheduler_changed=0
  if [ -n "$current_scheduler" ] && [ "$current_scheduler" != "$last_scheduler" ]; then
    scheduler_changed=1
  fi

  refresh_once
  rc=$?
  last_scheduler="$current_scheduler"

  case $rc in
    0)
      if [ "$scheduler_changed" -eq 1 ]; then
        sleep_s=1
      else
        sleep_s=$(seconds_until_refresh "${REFRESH_EXPIRY:-}")
      fi
      ;;
    2) sleep_s=30 ;;
    *) sleep_s=60 ;;
  esac
  log "sleeping ${sleep_s}s before next refresh"
  sleep "$sleep_s"
done
```

- [ ] **Step 4: Run focused refresher tests**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py -k "oauth_refresh and scheduler_reappearance" -q`

Expected: PASS.

- [ ] **Step 5: Run full target file**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .devcontainer/utils/databricks-oauth-refresh.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "fix: refresh databricks connections when scheduler reappears

Detect scheduler reappearance/container change in the OAuth refresher loop and
force immediate token sync so Airflow does not remain on stale credentials
until near-expiry refresh.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 3: Strengthen `dpc-check` with live Airflow Databricks connection validation

**Files:**
- Modify: `data_products/test_devcontainer_dind_wiring.py`
- Modify: `.devcontainer/check.sh`

**Interfaces:**
- Consumes: existing Databricks auth section and OAuth heartbeat soft check in `check.sh`.
- Produces: OAuth-mode soft check that validates actual Airflow Databricks connection health with timeout and actionable remediation.

- [ ] **Step 1: Write failing tests**

Add test assertions:

```python
def test_dpc_check_oauth_health_includes_live_airflow_databricks_validation() -> None:
    script = _read(".devcontainer/check.sh")
    assert "OAuth Airflow databricks_default connection works" in script
    assert "airflow connections test databricks_default" in script
    assert "run_with_timeout" in script
```

- [ ] **Step 2: Run test to verify failure**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py::test_dpc_check_oauth_health_includes_live_airflow_databricks_validation -q`

Expected: FAIL.

- [ ] **Step 3: Implement check in `.devcontainer/check.sh`**

Inside OAuth block, add:

```bash
HINT="Databricks Airflow connection is stale/invalid; run: mise run databricks:oauth-refresh or mise run setup:databricks-oauth"
soft_check "OAuth Airflow databricks_default connection works" run_with_timeout 25 bash -c '
  sched=$(docker ps --format "{{.Names}}" | grep -E "^edo-training.*-scheduler-1$" | head -1)
  [ -n "$sched" ] || exit 1
  docker exec "$sched" airflow connections test databricks_default >/dev/null 2>&1
'
```

- [ ] **Step 4: Run focused tests**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py -k "dpc_check_oauth_health_includes_live_airflow_databricks_validation or dpc_check_prevents_interactive_auth_hangs" -q`

Expected: PASS.

- [ ] **Step 5: Run full target file**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .devcontainer/check.sh data_products/test_devcontainer_dind_wiring.py
git commit -m "feat: dpc-check validates live airflow databricks connection

Add OAuth-mode health validation for databricks_default in the scheduler so
dpc-check can detect connection drift that heartbeat-only checks miss.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 4: Update docs/design/plan to the new contract

**Files:**
- Modify: `docs/superpowers/specs/2026-07-21-databricks-auth-strategy-design.md`
- Modify: `docs/superpowers/plans/2026-07-21-databricks-auth-strategy.md`
- Modify: `.devcontainer/README.md`
- Modify: `.devcontainer/TROUBLESHOOTING.md` (if needed)

**Interfaces:**
- Consumes: new contract from `docs/superpowers/specs/2026-07-23-airflow-oauth-token-drift-prevention-design.md`.
- Produces: aligned documentation that explicitly states OAuth token is metastore-only live state, not persisted in `airflow_settings.yaml`.

- [ ] **Step 1: Write failing doc assertions test**

Add a lightweight regression test in `data_products/test_devcontainer_dind_wiring.py`:

```python
def test_docs_state_oauth_token_not_persisted_in_airflow_settings() -> None:
    readme = _read(".devcontainer/README.md")
    assert "does not persist OAuth access tokens in airflow_settings.yaml" in readme
```

- [ ] **Step 2: Run test to verify failure**

Run:  
`pytest data_products/test_devcontainer_dind_wiring.py::test_docs_state_oauth_token_not_persisted_in_airflow_settings -q`

Expected: FAIL.

- [ ] **Step 3: Update docs with explicit replacement language**

Apply wording like:

```md
In OAuth mode, `airflow_settings.yaml` is bootstrap shape only (host/login).
Live OAuth access tokens are written to Airflow metastore connections by the
OAuth refresher and are not persisted in local settings files.
```

Ensure any contradictory previous wording is removed.

- [ ] **Step 4: Run doc assertion + full target test file**

Run:
1. `pytest data_products/test_devcontainer_dind_wiring.py::test_docs_state_oauth_token_not_persisted_in_airflow_settings -q`
2. `pytest data_products/test_devcontainer_dind_wiring.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-07-21-databricks-auth-strategy-design.md \
        docs/superpowers/plans/2026-07-21-databricks-auth-strategy.md \
        .devcontainer/README.md .devcontainer/TROUBLESHOOTING.md \
        data_products/test_devcontainer_dind_wiring.py
git commit -m "docs: align databricks oauth airflow token source-of-truth

Document the metastore-only live token contract and remove guidance that
implies OAuth access tokens are persisted in airflow_settings.yaml.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 5: End-to-end verification in running devcontainer

**Files:**
- Modify: none (verification only)
- Uses: `.devcontainer/utils/databricks-oauth-refresh.sh`, `.devcontainer/check.sh`, healthcheck DAG task

**Interfaces:**
- Consumes: all code from Tasks 1-4.
- Produces: proof that restart no longer introduces Databricks connection drift.

- [ ] **Step 1: Verify OAuth mode and check health**

Run (inside devcontainer workspace):

```bash
dpc-check
```

Expected: OAuth mode shown; live Airflow Databricks check passes.

- [ ] **Step 2: Capture pre-restart Databricks task result**

Run:

```bash
astro dev run tasks test healthcheck_connections databricks_default 2026-07-23
```

Expected: success (`Done. Returned value was: None`).

- [ ] **Step 3: Restart Astro and retest without manual `--once`**

Run:

```bash
astro dev restart --wait 5m
astro dev run tasks test healthcheck_connections databricks_default 2026-07-23
```

Expected: success; no `403 Invalid Token`.

- [ ] **Step 4: Verify refresher/scheduler convergence logs**

Run:

```bash
tail -n 80 /var/log/dbx-oauth-refresh.log
```

Expected: evidence of refresh shortly after scheduler availability/restart.

- [ ] **Step 5: Final commit (if any verification-script/test adjustments were made)**

```bash
if [ -n "$(git status --porcelain)" ]; then
  git add data_products/test_devcontainer_dind_wiring.py .devcontainer/check.sh .devcontainer/utils/databricks-oauth-refresh.sh .devcontainer/utils/setup-airflow-settings.sh
  git commit -m "test: verify oauth airflow auth survives astro restart

Add/adjust verification coverage proving Databricks connection health remains
valid across local scheduler restarts without manual repair.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
fi
```
