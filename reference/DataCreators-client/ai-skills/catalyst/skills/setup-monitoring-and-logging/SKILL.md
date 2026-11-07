---
name: setup-monitoring-and-logging
description: |
  Configure dbt artifact capture for serverless dbt-on-Databricks jobs and write
  a per-product runbook documenting the log escalation chain (Airflow callback →
  Databricks run page + runs/get-output API → UC Volume for dbt artifacts). Use
  when configuring monitoring and logging for a dbt data product, finding out
  where dbt logs go on serverless, or creating a dbt runbook.
  Trigger phrases: "configure monitoring and logging", "where do my dbt logs go",
  "create dbt runbook".
allowed-tools: Read Bash Write Edit
metadata:
  tier: workflow
  lifecycle-phase: phase-4-build
  dependencies: [databricks-jobs]
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # Canonical (RFD 0012 cross-ref)
    - DBX-SEC-001
    - DBX-BUNDLE-006           # Notifications wired to a configured alert sink (mechanism TBD; not prescribed here)
    # Cross-ref pending RFD 0008
    - DBX-UC-002               # dbt artifact upload destination = /Volumes/<catalog>/<schema>/dbt_artifacts/
    # Proposed (PR 94 prose → IDs; awaiting RFD 0008)
    - DBX-WORKFLOW-002         # Airflow on_failure_callback owns human alerts; DAB notifications own system signals
    - DBX-WORKFLOW-005         # Artifact retention on UC Volume follows the catalog's retention policy
---

# Setup Monitoring and Logging

Configure dbt artifact capture for pipeline jobs running on serverless compute
and write the operational runbook that documents the escalation path from
Airflow alert to root-cause log. This skill produces the `runbook.md` artifact
that on-call engineers use when a pipeline fires, and verifies that the dbt
wrapper uploads dbt artifacts to a UC Volume.

On serverless, Databricks owns the compute and `cluster_log_conf` is rejected
by the Jobs API. Logging is application-side: stdout/stderr is captured by the
platform and retrieved via API; dbt's own artifacts are captured by the wrapper.

---

## Serverless logging architecture

There is no native log-shipping config for serverless — `cluster_log_conf`
is rejected by the Jobs API and has no replacement. The shape below is
the supported workaround per Databricks' own serverless docs ("implement
custom log persistence by writing logs to Unity Catalog volumes or
tables"). Four layers, each with a distinct capture mechanism:

| Layer | Where it lives | How it's retrieved |
|:------|:---------------|:-------------------|
| Task stdout/stderr **(fast path)** | Captured by the Databricks platform — free, no config | Run page UI; `GET /api/2.1/jobs/runs/get-output?run_id=` (caps around 10 MB per task; community reports "output too large" beyond that) |
| Task stdout/stderr **(persistent)** | `dbt_wrapper.py` tees `sys.stdout` + `sys.stderr` to a UC Volume file per task | `/Volumes/<catalog>/<schema>/dbt_logs/<run_id>/<task_key>.log` — survives past the API cap; grep-able across runs |
| dbt artifacts (`target/run_results.json`, `target/manifest.json`, `logs/dbt.log`) | Written by dbt to the project working directory; **ephemeral** on serverless | `dbt_wrapper.py` copies to `/Volumes/<catalog>/<schema>/dbt_artifacts/<run_id>/<task_key>/` after each invocation |
| Run/task lifecycle metadata (state, duration, retries) | `system.lakeflow.*` system tables — populated for serverless | SQL: `SELECT * FROM system.lakeflow.job_run_timeline WHERE ...` — see "Cross-run search" below |

> **Per-run/per-task path is required, not optional.** Databricks'
> serverless docs explicitly warn that "task logs are not isolated per
> task run; logs will contain the output from multiple tasks" if you
> reuse a single path. The `dbt_logs/<run_id>/<task_key>.log` scheme
> above is the only thing that prevents commingled output from concurrent
> tasks. Same shape as `dbt_artifacts/`.

Failure flow:

```
dbt task on serverless
  ├─ stdout/stderr  → tee'd to /Volumes/<cat>/<schema>/dbt_logs/<run_id>/<task_key>.log
  │                  + mirrored to platform (runs/get-output remains the fast path)
  ├─ dbt artifacts  → wrapper.py uploads /Volumes/<cat>/<schema>/dbt_artifacts/<run_id>/<task_key>/
  ├─ lifecycle      → system.lakeflow.job_run_timeline (run/task state, duration, retries)
  └─ failure        → Databricks marks FAILED
                        └─ Airflow on_failure_callback fetches:
                             - run.run_page_url
                             - tasks[].state.state_message
                             - UC Volume paths for both dbt_logs/ and dbt_artifacts/
```

### Cross-run search

For "find all failed `deps` phases in the last 7 days" or "p95 of `run`
duration last month" queries, lean on `system.lakeflow.*` instead of
API-walking every run. The schema captures task lifecycle for serverless
jobs without any wrapper participation. Typical queries:

```sql
-- All failed dbt tasks in the last 7 days, with their UC Volume log paths
WITH failed AS (
  SELECT job_id, run_id, task_key, period_start_time, period_end_time, result_state
  FROM system.lakeflow.job_task_run_timeline
  WHERE workspace_id = current_workspace_id()
    AND result_state = 'FAILED'
    AND period_start_time >= current_timestamp() - INTERVAL 7 DAYS
)
SELECT
  job_id, run_id, task_key, period_start_time, result_state,
  concat('/Volumes/<catalog>/<schema>/dbt_logs/', run_id, '/', task_key, '.log') AS log_path,
  concat('/Volumes/<catalog>/<schema>/dbt_artifacts/', run_id, '/', task_key, '/') AS artifacts_path
FROM failed
ORDER BY period_start_time DESC;
```

For application-level grep (full stdout/stderr content), open the
`.log` file directly via `READ_FILES('/Volumes/.../dbt_logs/...', format => 'text')`
or `dbutils.fs.head(...)`.

This skill does **not** modify `*.job.yml` files. `cluster_log_conf` is invalid
on serverless and the bundle skill no longer emits a placeholder for it.

---

## Inputs

| Source | How consumed |
|:-------|:-------------|
| `.catalyst-build.yml` | Read `target_catalog`, `schema`, `product_name`, `mode` |
| `dbt_wrapper.py` (written by `/write-dbt-wrapper`) | Verify artifact-upload step is present |
| Conversation context | Product name, environment list, team contact |

If `dbt_wrapper.py` is absent, prompt: *"I need the dbt wrapper first. Run
`/write-dbt-wrapper` to scaffold it, then return here."*

---

## Output Files

```
<product-root>/
└── docs/
    └── runbook.md                        # Operational runbook for this product
```

The skill may also emit `CREATE VOLUME IF NOT EXISTS` SQL for the
`dbt_artifacts` *and* `dbt_logs` volumes when the target catalog/schema
doesn't already have them. Volume creation is shown to the user as a
SQL block to run themselves — the skill never executes it (mirrors the
`create_schema.sql` no-op convention).

---

## Step 1 — Gather context

1. Read `.catalyst-build.yml` for `target_catalog`, `schema`, `product_name`, `mode`.
2. Confirm the two UC Volume path conventions with the user:
   - **Artifacts:** `/Volumes/${var.catalog}/${var.schema}/dbt_artifacts/{{job.run_id}}/<task_key>/`
   - **Logs:**      `/Volumes/${var.catalog}/${var.schema}/dbt_logs/{{job.run_id}}/<task_key>.log`
   - `${var.catalog}` / `${var.schema}` resolve at bundle-deploy time;
     `{{job.run_id}}` resolves at task launch.
   - Both schemes use per-`{{job.run_id}}/<task_key>` partitioning. For
     artifacts this prevents the four-task layout (deps / seed / run /
     test) from clobbering itself; for logs it's required to keep
     concurrent tasks from commingling output (serverless's "task logs
     are not isolated per task run" warning).
3. List the existing UC Volumes in the target schema (`list_volumes`,
   read-only). If `dbt_artifacts` or `dbt_logs` is missing, surface the
   `CREATE VOLUME` SQL for the user to run — never execute it from the
   skill.

---

## Step 2 — Verify wrapper-driven artifact capture

dbt's artifacts live in the project working directory and are **ephemeral** on
serverless — once the task exits the working directory is gone. The dbt wrapper
is the only thing that can persist them.

### Confirm the wrapper uploads artifacts

Read `dbt_wrapper.py`. After each `dbt` invocation (regardless of
success/failure) it must copy:

- `target/run_results.json`
- `target/manifest.json`
- `logs/dbt.log`

to:

```
/Volumes/${var.catalog}/${var.schema}/dbt_artifacts/{{job.run_id}}/<task_key>/
```

If the wrapper doesn't have an upload step, prompt the user to re-run
`/write-dbt-wrapper` with the upload enabled, or add the upload block in place.

### Volume creation

In `prototype` mode, the sandbox catalog may not have a pre-created volume.
The wrapper writes there, so the volume must exist before the first run. Emit:

```sql
CREATE VOLUME IF NOT EXISTS ${var.catalog}.${var.schema}.dbt_artifacts;
```

The skill may invoke this directly via the Databricks SDK or print the SQL for
the user to run.

---

## Step 3 — Write `docs/runbook.md`

Write a runbook per data product at `<product-root>/docs/runbook.md`.

The runbook answers, for an on-call engineer:
1. Where does the alert originate?
2. What does the alert tell you?
3. Where do I find the detailed logs?
4. What is the escalation path?
5. What does the Airflow `on_failure_callback` fetch?

### Sample `runbook.md` skeleton

```markdown
# Runbook — <Product Name> Pipeline

**Product**: <product_name>
**Owner**: <team-name>
**Last updated**: <date>
**On-call rotation**: <link-to-pagerduty-or-servicenow>

---

## Overview

This runbook covers the dbt pipeline for **<product_name>**. The pipeline is
orchestrated by Airflow and executed as a Databricks Asset Bundle job on
serverless compute.

Escalation chain: **Airflow alert → Databricks run page + runs/get-output API →
UC Volume `dbt_artifacts/`**.

---

## Alert Sources

### 1. Airflow on_failure_callback

When any task in the Databricks job fails, Airflow's `on_failure_callback`
fires. The callback:

1. Calls `GET /api/2.1/jobs/runs/get?run_id=<run_id>` to retrieve the run's
   task-level error messages.
2. Extracts `state.result_state` (`FAILED` / `TIMEDOUT`) and
   `tasks[].state.state_message` for the failing task key.
3. Posts the summary to the team's configured alert sink (the channel/mechanism
   is owned by the DAG layer — see `/generate-dag`).

**What the callback surfaces:**

| Field | API path | Purpose |
|:------|:---------|:--------|
| Run state | `run.state.result_state` | FAILED / TIMEDOUT / SKIPPED |
| Failing task | `run.tasks[].task_key` where `state.result_state == FAILED` | Which dbt step failed |
| Error message | `run.tasks[].state.state_message` | dbt error summary |
| Run page URL | `run.run_page_url` | Direct link for engineer |
| Artifact path | `/Volumes/${catalog}/${schema}/dbt_artifacts/${run_id}/${task_key}/` | Where dbt artifacts live |

### 2. Databricks Run Page + runs/get-output

Navigate to the run page URL provided in the alert for the UI view, or fetch
stdout/stderr programmatically:

```bash
databricks jobs get-run-output --run-id <run_id>
# or
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  "$DATABRICKS_HOST/api/2.1/jobs/runs/get-output?run_id=<run_id>"
```

`runs/get-output` returns the first ~10MB of stdout/stderr per task — enough
for most dbt failures. No UC Volume is needed for stdout/stderr on serverless;
the platform captures it for free.

### 3. UC Volume — `dbt_artifacts/`

dbt's own artifacts (`run_results.json`, `manifest.json`, `dbt.log`) are
uploaded by the wrapper after every `dbt` invocation to:

```
/Volumes/<catalog>/<schema>/dbt_artifacts/<run_id>/<task_key>/
```

Access via Databricks UI: **Catalog** → `<catalog>` → `<schema>` → **Volumes**
→ `dbt_artifacts` → `<run_id>` → `<task_key>`.

Or via CLI:
```bash
databricks fs ls /Volumes/<catalog>/<schema>/dbt_artifacts/<run_id>/<task_key>/
databricks fs cp /Volumes/<catalog>/<schema>/dbt_artifacts/<run_id>/<task_key>/dbt.log .
```

---

## Common Failure Modes

| Symptom | Likely Cause | First Step |
|:--------|:-------------|:-----------|
| `deps` task fails | cgrepo CA cert / network block | Fetch stdout via `runs/get-output`; run `/troubleshoot-dbt-on-databricks` |
| `run` task fails with SQL error | Model logic error or missing table | Open `dbt_artifacts/<run_id>/run/dbt.log`, search for `ERROR` |
| `test` task fails | Data quality assertion violation | Check `dbt_artifacts/<run_id>/test/run_results.json` for failing test + row count |
| `seed` task fails | Missing or malformed seed CSV | Check `data/seeds/` directory and column types |
| All tasks timeout | Compute provisioning lag, large backfill | Increase `timeout_seconds` in job YAML; check Databricks status |

---

## Escalation Path

```
Airflow alert fires
  └─ on_failure_callback posts summary to configured alert sink
       └─ Engineer opens Databricks run page URL from alert
            └─ Identify failing task key (deps / seed / run / test)
                 └─ Fetch stdout/stderr via runs/get-output API (or run page)
                      └─ Open UC Volume artifacts:
                         /Volumes/<cat>/<schema>/dbt_artifacts/<run_id>/<task_key>/
                           └─ Inspect dbt.log + run_results.json
                                └─ If unresolved → escalate to <team-lead>
```

---

## Contacts

| Role | Name | Contact |
|:-----|:-----|:--------|
| Product Owner | <name> | <email> |
| Data Engineer | <name> | <email> |
| Platform On-Call | Databricks team | <pagerduty-link> |
```

---

## Step 4 — Confirm the `/generate-dag` contract

Document the contract between this skill and `/generate-dag` explicitly.

The Airflow `on_failure_callback` that `/generate-dag` emits **must**:

1. Accept `context` dict from Airflow with the Databricks `run_id`.
2. Call `GET /api/2.1/jobs/runs/get?run_id=<run_id>` for run metadata.
3. Extract `run.run_page_url` and `run.tasks[].state.state_message` for the
   failing task.
4. Construct the UC Volume artifact path from the `run_id` and `task_key`:
   `/Volumes/<catalog>/<schema>/dbt_artifacts/<run_id>/<task_key>/`
5. Include both the run page URL and the artifact path in the alert message so
   the on-call engineer can fetch stdout/stderr via `runs/get-output` and the
   dbt artifacts from the volume without navigating the UI.

If the existing DAG written by `/generate-dag` does not include this callback
pattern, prompt the user to re-run `/generate-dag` with the
`on_failure_callback` parameter set.

---

## Step 5 — Report

Print a summary table:

| File / Resource | Action |
|:----------------|:-------|
| `dbt_wrapper.py` | Verified artifact-upload step present (or prompted re-run of `/write-dbt-wrapper`) |
| `dbt_artifacts` UC Volume | Created (or `CREATE VOLUME` SQL emitted) |
| `docs/runbook.md` | Created |

Then prompt:
> *"Monitoring configured. Next step: run `/generate-dag` with the
> `on_failure_callback` contract documented in `docs/runbook.md`, or verify
> the existing DAG callback fetches `run_page_url` and the UC Volume artifact
> path."*

---

## Notes

- **DBX-SEC-001**: UC Volume paths are subject to UC access controls. Ensure
  the service principal running the job has `READ VOLUME` + `WRITE VOLUME` on
  `<catalog>.<schema>.dbt_artifacts`.
- **DBX-WORKFLOW-005**: Artifact retention on the UC Volume follows the
  catalog's default retention policy. For PII-adjacent pipelines, confirm the
  policy with the platform team before deploying.
- Do not configure `email_notifications.on_failure` at the Databricks job
  level. Airflow owns alerting; duplicating notifications here creates alert
  fatigue.
- **Classic compute is out of scope.** If a product needs classic-cluster log
  capture, file a follow-up — `cluster_log_conf` belongs behind an explicit
  `compute: classic` branch, not in the serverless default path.
