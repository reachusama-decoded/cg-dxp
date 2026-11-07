# Airflow OAuth Token Drift Prevention Design

## Context

Local Astro uses `airflow_settings.yaml` plus metastore-backed Airflow connections for Databricks auth.
Recent investigation reproduced a failure where `healthcheck_connections.databricks_default` returned `403 Invalid Token` even though:

- Databricks CLI OAuth session was healthy.
- OAuth refresher heartbeat was fresh.
- Token had not yet reached expiry.

Root cause evidence showed a restart-time drift:

1. Refresher wrote a valid token into metastore connections.
2. `astro dev restart` reloaded Databricks connection password from `airflow_settings.yaml`.
3. The file carried a stale token value, so metastore state regressed to invalid.
4. Refresher process was alive but sleeping until near expiry, leaving a failure window.

## Problem Statement

OAuth token state currently exists in two sources of truth:

1. `airflow_settings.yaml`
2. Airflow metastore connection rows

This dual-source model allows restart-time token drift and transient auth failures.

## Goals

1. Eliminate restart-time token drift for local Airflow Databricks connections.
2. Keep OAuth as default and PAT fallback unchanged.
3. Preserve setup simplicity for new clones.
4. Make health checks validate actual connection usability, not only heartbeat freshness.

## Non-Goals

1. Changing remote/cloud deployment auth behavior.
2. Replacing the current OAuth refresher architecture.
3. Modifying non-Databricks Airflow connection behavior.

## Chosen Approach

Adopt a **file-host + DB-token** model:

- `airflow_settings.yaml` stores Databricks connection shape only (host + empty login), never OAuth access token.
- OAuth refresher is the only writer of live token values to Airflow metastore connections.
- Refresher performs immediate sync when scheduler appears/reappears.

Why: this removes duplicate token sources while preserving current OAuth/PAT entrypoints and avoiding scheduler blocking behavior.

## Design

### 1) Connection State Contract

For OAuth mode:

- `airflow_settings.yaml` must not contain OAuth access tokens.
- Databricks connection rows in file use:
  - `conn_type: databricks`
  - `conn_host: <workspace host>`
  - `conn_login: ''`
  - `conn_password: ''` (or no credential value)

For PAT mode:

- Existing PAT behavior remains as-is.
- PAT can still be written into live Airflow connections by setup flow.

### 2) Refresher Responsibilities

`databricks-oauth-refresh.sh` remains the OAuth bridge but adds restart convergence behavior:

1. Detect scheduler availability transitions (down -> up or container ID change).
2. Perform immediate token upsert on scheduler appearance, regardless of expiry schedule.
3. Continue expiry-driven refresh for steady-state operation.
4. Keep single-instance guard and current status logging (`oauth-refresh-status.json`).

### 3) Setup Script Responsibilities

`setup-airflow-settings.sh` changes for OAuth mode:

1. Write Databricks connection shape (host/login) without token persistence.
2. Ensure OAuth mode always starts refresher loop (existing behavior retained).
3. Avoid writing short-lived OAuth token into `airflow_settings.yaml`.

### 4) Health Check Contract (`dpc-check`)

In OAuth mode, `dpc-check` should report healthy only when:

1. Databricks CLI auth is healthy.
2. Refresher heartbeat is fresh.
3. Live Airflow Databricks connection test succeeds (`DatabricksHook.test_connection()` or equivalent CLI-backed check).

Why: this directly validates the surface used by DAG tasks and closes the observability gap seen in the incident.

## Error Handling

1. If token mint fails (`session_expired`), keep prior DB token unchanged and emit remediation to rerun OAuth setup.
2. If scheduler is down, mark `scheduler_down`, retry quickly, and force immediate sync on scheduler return.
3. If live Airflow connection test fails, surface explicit warning/failure in `dpc-check`.

## Testing Strategy

1. Unit/regression tests for `setup-airflow-settings.sh` ensuring OAuth mode does not persist token in file.
2. Refresher behavior tests for scheduler reappearance-triggered sync.
3. `dpc-check` tests validating live Databricks connection health branch in OAuth mode.
4. Local integration sequence:
   - OAuth setup
   - successful Databricks task test
   - `astro dev restart`
   - successful Databricks task test without manual `--once` repair

## Compatibility and Rollout

1. No user workflow change for standard OAuth setup command.
2. Existing PAT fallback remains valid.
3. Existing repos/users gain safer restart behavior and stronger diagnostics after pull/update.

## Documentation Updates Required

Update these documents to match the new contract:

1. `docs/superpowers/specs/2026-07-21-databricks-auth-strategy-design.md`
2. `docs/superpowers/plans/2026-07-21-databricks-auth-strategy.md`
3. `.devcontainer/README.md`
4. `.devcontainer/TROUBLESHOOTING.md` (if it implies token persistence in local settings)

Specifically remove/replace any text claiming OAuth tokens are persisted in `airflow_settings.yaml`.
