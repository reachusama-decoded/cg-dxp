---
name: optimize-compute
description: |
  Compute-utilization optimizer for Databricks jobs and SQL warehouses
  powering dbt pipelines. Pulls recent run history (jobs API, cluster
  events, query history) and cross-checks the observed numbers against
  the dbt_project.yml/profiles.yml thread settings and the cluster the
  job actually targets. Emits DBX-WASTE-* findings with run-data
  evidence (job ID, run IDs, peak worker count, autoscale floor,
  queueing time) and a recommended config delta. Report-only: writes a
  Markdown report and JSON findings file; never edits config. Flags
  both over- and under-provisioning; does not model dollar cost.
  Trigger phrases: "optimize compute", "right-size this job", "are we
  over-provisioned", "audit databricks utilization", "tune dbt
  threads", "dbx-waste check", "compute optimization report".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: phase-7-operate
  dependencies:
    - connect-databricks
  consumes:
    - databricks.yml
    - dbt_project.yml
    - profiles.yml
  shared-components:
    core: [sql_identifiers, databricks_raw_client]
    platforms: [databricks]
  standards:
    - DBX-WASTE-001
    - DBX-WASTE-002
    - DBX-WASTE-003
    - DBX-WASTE-004
    - DBX-WASTE-005
    - DBX-WASTE-007
    - DBX-WASTE-008
    - DBX-WASTE-009
    - DBX-WASTE-010
---

# /optimize-compute

Compute right-sizing for Databricks jobs and SQL warehouses that run
dbt pipelines. Reads run history from the Databricks APIs, reads
`dbt_project.yml` and `profiles.yml` from the working tree, correlates
the two, and emits `DBX-WASTE-*` findings with the run-data evidence
behind each one. Output is a Markdown report plus a JSON findings
file. This skill is report-only: it never edits config or touches
compute. Acting on a finding is a separate, human-driven step.

This skill is the utilization-side counterpart to `optimize-databricks-job`
(static DAB linter) and `optimize-dbsql-query` (static SQL linter). It
asks a different question: *given how this job actually ran for the
last 30 days, is the compute the right size?*

## When to invoke

Two entry points:

- **Phase 7 (operate) - periodic utilization audit.** A job has been
  running in production for at least 10 runs and someone wants to know
  whether it is over- or under-provisioned. Trigger phrases:
  "optimize compute", "right-size this job", "audit databricks
  utilization", "are we paying for idle workers", "dbx-waste check",
  "is the warehouse oversized".

- **Phase 4 (build) - first-time sizing review.** A new pipeline is
  about to ship and the author wants a sanity check on the cluster
  spec and dbt thread count before the first production run. The skill
  will note that no run history exists yet and lean on the dbt-config
  audit half of its work. Trigger phrases: "size check before ship",
  "review compute config for new pipeline", "tune dbt threads".

Run after the job (or warehouse) has been used enough to produce a
signal. With fewer than 10 historical runs the run-history findings
are weak; the report will say so.

## When NOT to invoke

Refer to `references/composition-with-adjacent-skills.md` for the long
form. Quick routing:

- Static lint of bundle YAML against `DBX-PERF-001..005` (concurrency,
  timeout, Photon, runtime version, autoscale on/off): use
  `optimize-databricks-job`. This skill does not duplicate those
  rules.
- Performance pitfalls inside SQL model bodies (`SELECT *`, cross
  joins, function-wrapped predicates): use `optimize-dbsql-query`.
- Actually creating, resizing, restarting, or deleting a cluster or
  warehouse: use `databricks-execution-compute`. This skill never
  touches compute lifecycle.
- Configuring a SQL warehouse from scratch (size, type, scaling
  range): use `configure-sql-warehouse`. This skill audits an existing
  warehouse, it does not stand one up.
- Building or deploying a DAB: use `databricks-bundles` /
  `write-dab-resource` / `deploy-dab`.
- Dollar-cost modeling, chargeback, FinOps reports: out of scope.
  This skill works in DBU-hours and worker-minutes only.

## Inputs

| Source | What we read |
|---|---|
| `databricks.yml` + `resources/**/*.yml` | Job ID, cluster spec, `tasks[].job_cluster_key`, warehouse references |
| `dbt_project.yml` | Materialization tree, `+threads` overrides, dispatch config, vars |
| `profiles.yml` | `threads:` per target, `http_path` |
| `.dbt/manifest.json` (optional) | Model count and tags, if the project has been compiled |
| Jobs API (`/api/2.1/jobs/get`, `runs/list`, `runs/get`) | Last 30 days of runs, capped at 200 |
| Clusters API (`/api/2.0/clusters/events`) | `RESIZING`, `UPSIZE_COMPLETED`, `AUTOSCALING_STATS_REPORT` events |
| SQL Warehouses API (`/api/2.0/sql/warehouses/{id}`, `/api/2.0/sql/history/queries`) | Warehouse spec, query history, queueing time |
| SQL Warehouses API (`/api/2.0/sql/warehouses/{id}/events`) | Warehouse `SCALED_UP` / `SCALED_DOWN` / `STARTING` / `RUNNING` / `STOPPING` events (signal source for `DBX-WASTE-008`) |

Detailed signal extraction lives in
`references/run-history-signals.md`. Detailed dbt config rules live in
`references/dbt-config-audit.md`. The `SKILL.md` does not restate
either.

**Trust prerequisites.** This skill's autoscale-based findings
(`DBX-WASTE-001`, `DBX-WASTE-002`) assume the target cluster actually
autoscales. If the cluster has `min_workers == max_workers` or
`num_workers` set fixed, run `/optimize-databricks-job` first - its
`DBX-PERF-002` rule covers fixed-worker static configs - and come
back here once the cluster is genuinely on autoscale. Running this
skill against a non-autoscaling cluster produces signal that is at
best uninteresting and at worst misleading.

## Mode

The skill runs in a single read-only `report` mode. It writes
`compute-optimization-report.md` and `compute-optimization-findings.json`
to the current working directory. No code, config, or compute is
changed. Each finding carries a recommended config delta that a human
applies manually.

Each finding in the emitted JSON carries
`remediation.config_delta` (a map keyed by config name where each
entry has `current` and `proposed` values) and `apply_mode_supported`
(boolean). In this PR `apply_mode_supported` is always `false` by
design; the field is in the schema today so downstream tooling has a
stable contract once an apply mode lands.

**Future: apply mode (Phase 2).** This PR ships a read-only analyzer
only. A follow-up PR is planned to add an opt-in apply mode; the
single rule slated for auto-apply is `DBX-WASTE-007` (stale Spark /
driver config keys on DBR 13+), with per-`--config-key` opt-in so each
invocation edits exactly one key in one file. All other rules
(materialization changes, autoscale retuning, warehouse resizing, task
consolidation) will remain report-only suggestions. The JSON
`generated_at` timestamp is emitted today and the planned apply mode
will use it as a freshness check, but that behavior is deferred to the
Phase 2 design doc.

## Steps

The skill runs these five steps in order on every invocation, after a
one-time setup.

**Setup (first run only).** Install the script dependencies before
invoking any step. The evaluator hard-requires `jsonschema`, and the
collector imports `requests` and `pyyaml`; a fresh venv without these
will fail with an `ImportError` on step 2 or 4. On the Capital Group
corporate network, public PyPI is blocked, so `--index-url` pointing
at the internal Nexus mirror is required — without it pip will time
out or 404 against `pypi.org`.

```
pip install --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ \
    -r skills/optimize-compute/scripts/requirements.txt
```

1. **Confirm Databricks auth and resolve the target.** Verify
   `connect-databricks` has produced an active session; if not,
   instruct the user to run it first and stop. Then resolve the job ID
   or warehouse ID. If the user passed one explicitly, use it. If not,
   scan `databricks.yml` and `resources/**/*.yml` for job and
   warehouse resources; if exactly one is found, use it; if more than
   one, ask the user which.

2. **Collect run history.** Invoke
   `python scripts/collect_run_history.py [--job-id <id>] [--warehouse-id <id>] [--bundle-dir <bundle-root>] --output runs.json`.
   At least one of `--job-id` / `--warehouse-id` is required; both may
   be supplied for a combined job+warehouse audit. Pass `--bundle-dir`
   (typically `.`) so findings can cite the exact `databricks.yml` /
   `resources/**/*.yml` paths to edit. The script writes a
   normalized JSON document covering the last 30 days of job runs
   (capped at 200), or the last 14 days of warehouse queries (capped at
   2000), with the signals listed in
   `references/run-history-signals.md`. Rules that can't fire on the
   available signal (insufficient runs, missing warehouse query history,
   no dbt config) are surfaced in `insufficient_data.skipped_rules` in
   the findings output — the report calls them out per-rule.

3. **Audit dbt config.** Invoke
   `python scripts/audit_dbt_config.py --project-dir . [--profile-name <name>] [--target <env>] --output dbt-config.json`.
   The script writes a JSON snapshot of `dbt_project.yml`,
   `profiles.yml`, and (if present) `.dbt/manifest.json`: per-target
   threads, dispatch config, materialization tree, `+threads`
   overrides, and the `http_path` the dbt run actually hits.
   Detection logic lives in `references/dbt-config-audit.md`.

4. **Evaluate findings.** Invoke
  `python scripts/evaluate_findings.py --runs runs.json --dbt-config dbt-config.json --output compute-optimization-findings.json`.
   The script applies the `DBX-WASTE-001..010` rules (full detection
   logic in `references/findings-catalog.md`) and writes a findings
   JSON document. Each finding carries `rule_id`, `severity`, `target`
   (file path or API resource), `evidence` (run IDs, observed
   numbers), a `remediation.config_delta` map (keyed by config name,
   each entry holds `current` / `proposed` values), and
   `apply_mode_supported` (boolean, always `false` in this PR; reserved
   for Phase 2).

   **Exit codes.** The evaluator distinguishes a clean run with an
   intentional CI gate signal from an actual crash. Under `set -e`, exit
   `1` will halt the pipeline — that is deliberate, not a bug; the JSON
   output on the next line is still valid and complete.
   - `0` — clean run, no findings or only info/warning findings.
   - `1` — clean run, at least one finding with `severity=error`
     (intentional CI gate signal; JSON output is still valid).
   - `2` — bad input (missing flag, file not found, malformed
     `runs.json`).
   - `3` — schema validation failure (would-be output didn't match
     `templates/compute-optimization-findings.json`).

   If CI should NOT fail on error-severity findings, wrap the call as
   `python … || true` or check the exit code explicitly.

5. **Render the report.** The template
   `templates/compute-optimization-report.md` is interpolated by the
   calling model — there is no Jinja runtime in this skill's
   `scripts/`. Substitute the findings-JSON fields into the template's
   `{{ … }}` placeholders, write `compute-optimization-findings.json`
   to the cwd verbatim alongside the rendered Markdown, and print a
   one-screen summary (counts by severity, top three findings by
   estimated worker-minute impact). Stop. Do not loop, do not
   re-collect history, do not propose follow-up runs.

## Findings catalog

The skill emits findings under the `DBX-WASTE-*` family. Each finding
carries the run-data evidence behind it (job ID, run IDs, observed
peak/avg values) and a recommended config delta. Full detection logic,
thresholds, evidence requirements, and apply-safety for each rule live
in `references/findings-catalog.md`. The table below is a one-line
index; do not read thresholds off it. `DBX-WASTE-005` is an info-only
diagnostic: it reports observed read counts without recommending an
action. `DBX-WASTE-006` is withdrawn — see the catalog for rationale;
the ID is reserved and not reused.

| Rule ID | One-line rule | Severity |
|---|---|---|
| DBX-WASTE-001 | Job cluster oversized vs. peak observed workers | warning |
| DBX-WASTE-002 | Autoscale floor never relaxes (cluster sits at `min_workers`) | warning |
| DBX-WASTE-003 | Long idle gaps between tasks within a job run | info |
| DBX-WASTE-004 | dbt `threads` vs. cluster cores mismatch (over- or under-subscribed) | warning |
| DBX-WASTE-005 | Materialization heavier than usage justifies | info |
| DBX-WASTE-007 | Spark config overrides likely stale or misconfigured (DBR 13+) | warning |
| DBX-WASTE-008 | SQL warehouse oversized vs. query history | warning |
| DBX-WASTE-009 | SQL warehouse under-provisioned (queueing) | warning |
| DBX-WASTE-010 | dbt target points at all-purpose cluster for scheduled runs | error |

## Anti-goals

- **Not a static linter.** Static rules against DAB YAML
  (`DBX-PERF-001..005`) belong in `optimize-databricks-job`. This
  skill only fires when there is run-data evidence, or - in
  build-phase mode - when the dbt-config audit catches a misalignment
  that does not need run history.
- **Not a SQL optimizer.** SQL anti-patterns inside dbt model bodies
  (`SELECT *`, cross joins, function-wrapped predicates) belong in
  `optimize-dbsql-query`.
- **Not a cost-in-dollars tool.** All measurements are in
  worker-minutes, DBU-hours, and queueing seconds. No DBU pricing, no
  currency conversion, no chargeback estimation.
- **Not an autonomous cluster operator.** The skill never creates,
  resizes, starts, stops, or deletes a cluster or warehouse. Lifecycle
  operations belong to `databricks-execution-compute`.
- **Not a one-way cost-cutter.** `DBX-WASTE-009` exists specifically
  so the skill flags under-provisioning (SQL warehouse queueing past
  threshold) as a waste problem too: a workload that runs twice as
  long as it should because it is starved is also wasting compute.
  The recommendation may be "increase capacity," not just "shrink
  it."

## See also

- `references/findings-catalog.md` - full detection logic, thresholds,
  evidence requirements, and apply-safety for `DBX-WASTE-001..010`.
- `references/run-history-signals.md` - which API endpoints to call,
  which fields to extract, how to compute peak/avg worker count,
  autoscale floor reached, task gap time, and warehouse queueing.
- `references/dbt-config-audit.md` - how to read `dbt_project.yml`,
  `profiles.yml`, and `.dbt/manifest.json`, and what to check against
  the cluster spec.
- `references/composition-with-adjacent-skills.md` - long-form routing
  to `optimize-databricks-job`, `optimize-dbsql-query`,
  `databricks-execution-compute`, `configure-sql-warehouse`, and the
  DAB-authoring skills.
- `templates/compute-optimization-report.md` - report scaffold.
- `templates/compute-optimization-findings.json` - findings JSON
  scaffold.
- `scripts/collect_run_history.py` - step 2 implementation.
- `scripts/audit_dbt_config.py` - step 3 implementation.
- `scripts/evaluate_findings.py` - step 4 implementation.
