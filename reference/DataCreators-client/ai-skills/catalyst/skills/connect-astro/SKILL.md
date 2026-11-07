---
name: connect-astro
description: |
  Authenticate to Astronomer Cloud using an API token sourced from a
  platform secrets backend (PY-SECURITY-*). Refuses to persist the
  plaintext token to disk. Wraps the `astro` CLI to log in and capture
  workspace/deployment metadata for downstream Airflow-authoring skills.
  Trigger phrases: "connect to astronomer", "set up astro connection",
  "authenticate astronomer workspace", "log in to astro".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [astronomer]
  standards:
    - PY-SECURITY-*
---

# connect-astro

Authenticate to Astronomer Cloud via the `astro` CLI using an API token
delivered through the platform secrets backend.

## When to use

Any time another skill needs an authenticated Astronomer session, e.g.
the `authoring-airflow-on-astronomer` skill chain. Should be invoked
before any `astro` deployment, workspace, or DAG-push operation.

## Inputs

Required environment variables (per PY-SECURITY-*):
- `ASTRO_API_TOKEN` -- API token retrieved from the platform secrets
  backend. Must not be hard-coded or committed.

Optional:
- `ASTRO_SESSION_DIR` -- directory for non-secret session metadata.
  Defaults to a per-process tmpdir.

The token must be supplied via env var only. Storing the token in a
file, dotfile, or `.env` checked into the repo is forbidden.

## Outputs

- Active `astro` CLI session in the current shell.
- Session metadata JSON at `${ASTRO_SESSION_DIR}/astro_session.json`
  containing: `workspace_id`, `workspace_name`, `deployments` summary,
  and `context`. The token is never written.

## Standards

- PY-SECURITY-* -- API tokens sourced from secrets backend only;
  plaintext-token persistence is refused.

## Procedure

1. Verify `ASTRO_API_TOKEN` is set and non-empty; exit 2 otherwise.
2. Run `scripts/astro_connect.py` which:
   - Pipes the token to `astro login --token-stdin` (token never on
     argv or disk).
   - Calls `astro context list` to confirm the active context.
   - Calls `astro workspace list` to capture the workspace ID.
   - Calls `astro deployment list` for a summary.
   - Writes non-secret session metadata to
     `${ASTRO_SESSION_DIR}/astro_session.json`.
3. Report success or surface the exact error from the CLI.

## Failure modes

- Missing or empty `ASTRO_API_TOKEN` -> exit code 2.
- Any `astro` CLI failure during login, context list, or workspace
  list -> exit code 3; print CLI stderr (with the token redacted as
  `***`).
- `astro workspace list` returns no workspaces -> exit code 4.
- `astro deployment list` failure is non-fatal: the connector
  downgrades to an empty deployments list in the session metadata
  and continues.
