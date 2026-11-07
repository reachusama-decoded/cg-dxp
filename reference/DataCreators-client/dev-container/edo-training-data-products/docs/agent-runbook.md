# Agent Runbook

## Start Here (Required)
- Confirm you are in the devcontainer-backed Astro environment.
- Wait for devcontainer startup to finish before taking setup/debug actions. Readiness is when `dpc-check` runs in the devcontainer terminal and prints results.
- Verify the active scheduler container name matches `edo-training.*-scheduler-1`.
- Do not ask users to manually configure `databricks_job_prefix`.
- Ensure Databricks setup is complete before Astro startup (`mise run setup:databricks`).
- If Astro was started before Databricks setup, rerun setup and restart Astro (`astro dev restart --wait 5m`). Symptom: `astro dev run dags list-import-errors` shows ``Invalid catalog name : ``.`` while `dbt debug` in your terminal still passes — the containers captured an empty environment at boot.

## Deterministic Execution Order
1. Complete Databricks setup (`mise run setup:databricks`).
2. Deploy DAB jobs first.
3. Start or restart Astro after deployment.
4. Refresh Databricks OAuth-backed Airflow connections.
5. Verify `databricks_job_prefix` resolves from Databricks identity and is present in Airflow.
6. Verify the target Databricks job exists with the prefixed name.
7. Trigger the DAG or task.

## Failure Classification
1. Job lookup stage: missing or mismatched prefixed job name.
2. Auth stage: invalid or stale OAuth token, or connection drift.
3. Runtime stage: dbt or Databricks failures after launch.

## Auto-Remediation Playbook
- On an auth-stage failure, **prove the user is deauthenticated before prompting them.** Most
  auth failures in this repo are delivery bugs: the user *is* authenticated, but the token never
  reached the shell/container that failed. The decisive check is whether a token can be minted
  right now — `mise exec -- sh -c 'databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json'`.
  If that returns an `access_token`, do **not** prompt; fix delivery instead (`mise run setup:mise`
  for a missing `/etc/profile.d/mise-init.sh`, `exec bash -l` for a shell opened before
  authentication, `cd` into the repo because mise's env is directory-scoped).
  `databricks auth describe` reads `~/.databrickscfg`, not the variable dbt sends, so it can
  report success while dbt fails and vice versa — never prompt on that alone. A
  `databricks: command not found` / `No version is set for shim` error is a missing `mise exec --`,
  not an auth failure. The full procedure is in `.github/copilot-instructions.md`
  ("Databricks Auth Contract"); background in
  `docs/rca/2026-08-04-databricks-env-not-propagated-to-shells.md`.
- Only once that check shows a genuine expiry: prompt the user FIRST — do not skip or abandon the
  task, and do not blame auth to avoid the work. Ask them to run `mise run setup:databricks`
  (OAuth — complete the browser pop-up) or `mise run setup:databricks --pat` (paste a valid
  token), then resume the original task.
- If Astro started before Databricks setup, rerun setup then restart Astro.
- Recompute the prefix from Databricks identity.
- Refresh OAuth-backed Airflow Databricks connections.
- Re-verify job existence and prefixed name alignment.
- Retry the task only after lookup and auth checks pass.

## Known Failure Modes (RCA index)

Read the matching RCA before debugging one of these — each has a confirmed root cause and fix.

| Symptom | RCA |
|---|---|
| `dbt` hangs forever with no output; port 8020 held open | `docs/rca/2026-08-03-dbt-databricks-auth-hang.md` |
| `dbt` exits with `AttributeError: 'str' object has no attribute 'get'` (Windows clones) | `docs/rca/2026-08-03-profiles-symlink-windows.md` |
| `dbt` dies with no error — exit 139, or exit 0 with empty output | `docs/rca/2026-08-03-challenge-04-dbt-segfault.md` |
| DAG import fails with ``Invalid catalog name : ``.`` while terminal `dbt` works | `docs/rca/2026-08-03-airflow-blank-databricks-env-at-boot.md` |
| Challenge 02 guide/stub defects (`docs serve`, seed-mutating peek, invisible `OPTIMIZE`) | `docs/rca/2026-08-03-challenge-02-raw-dbt-walkthrough.md` |

Two recurring classes worth internalising:

- **Empty is not unset.** dbt's `env_var(name, default)` only falls back when a variable is
  *unset*; a set-but-empty value wins and defeats the default. This has caused three separate
  incidents (auth hang, blank Airflow catalog, profile sentinels).
- **A green `dbt debug` does not mean dbt works.** It only performs a handshake and returns no
  rows. Smoke-test result handling with `dbt show --inline "select 1 as a" --limit 1`.
