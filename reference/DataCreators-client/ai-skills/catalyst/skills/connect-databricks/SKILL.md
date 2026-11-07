---
name: connect-databricks
description: |
  Authenticate to a Databricks workspace using OAuth client credentials
  (DBX-SEC-002). Refuses Personal Access Tokens. Verifies connection with
  `SELECT 1` against a SQL warehouse before returning.
  Trigger phrases: "connect to databricks", "set up databricks connection",
  "authenticate databricks workspace", "log in to databricks".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - DBX-SEC-002
---

# connect-databricks

Authenticate to a Databricks workspace using OAuth M2M (client credentials).

## When to use

Any time another skill needs a Databricks SDK or SQL client and there is no
active session. `query-databricks`, `query-table`, `dplc-validate`,
`discover-data`, and the new `write-dab-resource` / `deploy-dab` /
`validate-dab` / `run-dbt` / `optimize-databricks-job` skills chain to
this skill.

## Inputs

Required environment variables (per DBX-SEC-002):
- `DATABRICKS_HOST` -- workspace URL (`https://<workspace>.cloud.databricks.com`)
- `DATABRICKS_CLIENT_ID` -- service principal client ID
- `DATABRICKS_CLIENT_SECRET` -- service principal client secret

PATs (`DATABRICKS_TOKEN`) are not accepted. If detected, the skill exits
with a clear error pointing at DBX-SEC-002.

## Outputs

- A configured `databricks.sdk.WorkspaceClient` in memory
- Confirmation that `SELECT 1` against the default warehouse succeeded
- Connection metadata written to `~/.databricks/last_oauth_session.json`
  (host, client_id, warehouse_id, expires_at) -- never the secret

## Standards

- DBX-SEC-002 -- OAuth client credentials only.

## Procedure

1. Verify required env vars are set; refuse and exit if `DATABRICKS_TOKEN`
   is present.
2. Run `scripts/oauth_connect.py` which:
   - Calls the OAuth token endpoint
   - Constructs a `WorkspaceClient`
   - Executes `SELECT 1` against the warehouse named by
     `DATABRICKS_WAREHOUSE_ID` (or first available if unset)
   - Writes session metadata to disk
3. Report success or surface the exact error.

## Failure modes

- Missing env vars -> exit code 2; print which var is missing.
- `DATABRICKS_TOKEN` set -> exit code 3; print DBX-SEC-002 reference.
- OAuth token endpoint 401 -> exit code 4; print remediation steps.
- `SELECT 1` fails -> exit code 5; print warehouse status.
