---
name: generate-dag
description: |
  Generate an RFD-0011-compliant Airflow DAG for a data product dataset,
  composing with the Databricks Asset Bundle produced by
  /setup-databricks-asset-bundle. Supports dag-factory (default) and
  astro-blueprints (opt-in) emission patterns. Mode-aware: prototype,
  production, lift-and-shift.
  Trigger phrases: "generate a DAG", "create an airflow dag",
  "scaffold orchestration for my dataset", "wire up airflow for this dataset",
  "scaffold a DAG for edo-ig-data-products", "clean up my DAG",
  "update my DAG to current standards", "lift and shift this DAG".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies:
    - setup-databricks-asset-bundle
    - databricks-jobs
    - scaffold-repo-structure
  consumes:
    - data-contract
    - data-model
  standards:
    # Canonical (RFD 0011 enumerated — every emitted line is anchored to one of these)
    # PY-AIRFLOW-016..022 are discussion-state IDs from PR #87 (tracked in #128)
    # and are treated as provisional until RFD 0011 merges.
    - PY-AIRFLOW-001           # Templated dates via {{ ds }}; no datetime.now() in task bodies
    - PY-AIRFLOW-002           # Static start_date
    - PY-AIRFLOW-003           # Retries configured on every task
    - PY-AIRFLOW-004           # Exponential backoff for retries
    - PY-AIRFLOW-005           # T-shirt cluster sizing; no inline worker overrides
    - PY-AIRFLOW-006           # Explicit schedule; catchup=False
    - PY-AIRFLOW-007           # Required tag set (union): l1_domain, l1_xmatters_group, lifecycle_phase, data_classification, criticality (+ deliver_by_* when critical) + MDS attribution owner, business_function, data_domain, app_id (+ optional l2/l3)
    - PY-AIRFLOW-008           # Failure alerting via Astronomer's platform Datadog integration; no DAG-level callback. Routing tags are context support reads for manual Teams/xMatters escalation
    - PY-AIRFLOW-009           # No module-scope I/O at parse time
    - PY-AIRFLOW-010           # TaskFlow API is the default authoring style
    - PY-AIRFLOW-011           # XCom hygiene
    - PY-AIRFLOW-012           # DAG ID convention <domain>__<dataset>__<frequency>
    - PY-AIRFLOW-013           # No literal tokens or secrets; Variable.get / Connections
    - PY-AIRFLOW-014           # Integrity test stub per DAG
    - PY-AIRFLOW-015           # Emit data-ready event v2 on success (cross-ref RFD 0007)
    - PY-AIRFLOW-016           # Deterministic failures fail fast via AirflowFailException raised from task code (no retry_on_exception API exists)
    - PY-AIRFLOW-017           # Long waits release worker slot: deferrable operators OR mode=reschedule + bounded timeout
    - PY-AIRFLOW-018           # max_active_runs and max_active_tasks bound DAG-level parallelism
    - PY-AIRFLOW-019           # schedule = Asset(...) is the default; cron only when temporal trigger is genuine
    - PY-AIRFLOW-020           # Secrets never passed as operator args (rendered-fields leak to DB + UI)
    - PY-AIRFLOW-021           # Local dev via astro dev start; airflow tasks test for per-task iteration
    - PY-AIRFLOW-022           # Shared assert_dag_compliant runs in CI for every PR
    # DBX-DAB-* (Databricks Asset Bundle composition contract owned by this skill).
    # Renamed from colliding RFD 0008/0012 IDs: DBX-BUNDLE-011 -> DBX-DAB-001,
    # DBX-WORKFLOW-001 -> DBX-DAB-002, DBX-WORKFLOW-002 -> DBX-DAB-003, DBX-WORKFLOW-004 -> DBX-DAB-004.
    - DBX-DAB-001              # Reads ${var.databricks_job_prefix} from the bundle
    - DBX-DAB-002              # Pipeline DAB and compute DAB are separate bundles
    - DBX-DAB-003              # Airflow failure alerting is platform-side (Astronomer Datadog); DAB owns system-signal notifications
    - DBX-DAB-004              # Bundle's databricks_job_prefix var is consumed by this skill
    - DBX-SEC-001
    - DBX-SEC-002              # SP-owned objects; OAuth preferred for any Databricks API calls
  shared-components:
    core: []
    platforms: [airflow, databricks, astronomer]
---

# /generate-dag

Emit an Airflow DAG for a data product dataset that meets every directive
in RFD 0011 (DAG Standards). Composes with the Databricks bundle from
`/setup-databricks-asset-bundle` so the emitted DAG invokes the deployed
job by name. Cites the canonical repo layout from
`skills/scaffold-repo-structure/references/repo-structure.md` for all
path resolution.

## When to invoke

- After `/setup-databricks-asset-bundle` has emitted `databricks.yml` and
  per-dataset `*.job.yml` for the dataset you want to orchestrate.
- When retrofitting an existing DAG to RFD 0011 standards (lift-and-shift mode).
- When scaffolding orchestration for a brand-new dataset before the bundle exists
  (prototype mode — emits a placeholder job name).

## Modes

| Mode | Schedule | MDS tags | Asset triggers | Validation |
|---|---|---|---|---|
| `prototype` | cron OK | optional | optional | lite |
| `production` | Asset-driven required (cron fallback with advisory) | all MDS required | required | full RFD 0011 |
| `lift-and-shift` | preserve existing | warn-and-add | preserve | full RFD 0011 |

See `references/mode-aware-emission.md` for the full mode matrix.

## Emission patterns

Three patterns. The skill auto-detects between the two YAML carriers; pure
Python is opt-in.

| Pattern | Detection | When chosen |
|---|---|---|
| **dag-factory** | Default | Repo has no `.blueprints/` directory OR user explicitly requests dag-factory |
| **astro-blueprints** | Repo has `.blueprints/*.py` + a blueprint loader | Team has the blueprint framework already in place |
| **python** | `pattern=python` explicit opt-in | Use when the DAG needs features YAML carriers can't express cleanly (multi-Asset triggers, dynamic task mapping, branching). |

If the YAML patterns are ambiguous, ask the user. See
`references/pattern-dag-factory.md`, `references/pattern-astro-blueprints.md`,
and `references/pattern-python.md` for the full templates.

## Steps

### Step 1 — Detect emission pattern

The real `edo-ig-data-products` repo runs **both** loaders simultaneously
in the same Airflow process (`blueprints_loader.py` loads
`**/airflow/*.dag.yml` and `**/airflow/*.dag.yaml`; `dags_loader.py`
loads `**/airflow/*.dag-factory.yml`). File extension is the
disambiguator, not "which loader is present." Both can coexist
per-repo and even per-dataset.

Run:

```bash
test -d data_products/.blueprints && echo ".blueprints/ present"
ls data_products/.blueprints/*.py 2>/dev/null | head -8
ls data_products/blueprints_loader.py 2>/dev/null && echo "blueprints loader present"
ls data_products/dags_loader.py 2>/dev/null && echo "dag-factory loader present"
# Per-dataset existing carrier — sticky to whatever the dataset already uses
ls data_products/<product>/datasets/<dataset>/airflow/ 2>/dev/null
```

**Decision tree (per dataset):**

1. **If the dataset's `airflow/` directory already has a file**, the
   existing carrier wins (sticky):
   - `*.dag.yml` or `*.dag.yaml` → `astro-blueprints`.
   - `*.dag-factory.yml` → `dag-factory`.
   - `*_dag.py` → `python`.
2. **Otherwise**, check `.catalyst-build.yml#dag_carrier` for the repo-wide
   default (`blueprints` / `dag-factory` / `python`).
3. **Otherwise**, infer from what's available:
   - `.blueprints/` populated with real blueprint modules (`dag_args.py`
     + `dag_exec_check.py` + `databricks_run_now.py` + `xcom_generation.py`
     + `kafka_notify.py`, the canonical edo-ig-data-products set) →
     `astro-blueprints` with `blueprints-source: existing`. The skill
     references the team's blueprints by name; it does **not** emit
     `include/shared/*.py`.
   - `.blueprints/` empty or absent, `dags_loader.py` present →
     `dag-factory`.
   - Otherwise ask the user.

For `pattern=python` (the third carrier — pure-Python TaskFlow), the
user must opt in explicitly. See `references/pattern-python.md`.

**Reminder:** the existing-mode blueprints schema is in
`references/pattern-astro-blueprints.md` — the schemas there are
mirrored from the team's actual `.blueprints/*.py` Pydantic models.
Don't invent fields; if the dataset needs a blueprint that's not in
that doc, stop and ask the user to add it under `.blueprints/`.

### Step 2 — Read Databricks bundle artifacts

Run:

```bash
# Per RFD 0003: each dataset IS a product; bundle/ is a subdirectory of the product subtree.
cat data_products/<product>/datasets/<dataset>/bundle/databricks.yml
cat data_products/<product>/datasets/<dataset>/bundle/resources/<dataset>.job.yml
cat data_products/<product>/datasets/<dataset>/bundle/variables_<env>.yml
```

Extract:
- The job's resource key (e.g., `daily_positions_job`).
- The rendered job name pattern (e.g., `${var.databricks_job_prefix}daily_positions_job`).
- The Databricks workspace targets (dev/qa/sqa/prd).

If `databricks.yml` is absent:
- `production` mode → STOP. Report: "No databricks.yml found. Run /setup-databricks-asset-bundle first, or point me at an existing job."
  In this branch, do **not** emit DAG YAML/Python, tests, `include/` helpers,
  or proposal artifacts. Return only the stop message, the prerequisite step
  (`/setup-databricks-asset-bundle`), and an explicit note that the user can
  rerun in `prototype` mode if they want a placeholder scaffold.
- `prototype` mode → emit a placeholder `job_name: "{{ var.value.databricks_job_prefix }}<dataset>_job  # TODO: confirm job name when bundle is deployed"` with a warning.

See `references/compose-with-bundle.md` for the full discovery + emission walk-through.

### Step 3 — Collect required tags (RFD 0011 §6 PY-AIRFLOW-007)

**Auto-derive first, then prompt only on misses.** Read the ODCS contract at
`data_products/<product>/datasets/<dataset>/contract/<dataset>.odcs.yaml`
and pre-fill what you can; prompt only for the unresolved keys.

| Tag | Resolution order |
|---|---|
| `l1_domain` | (1) contract's `domain` field → (2) prompt user |
| `data_classification` | (1) contract's `classification` field → (2) **production mode: stop and ask**; **prototype mode: emit `# TODO PY-AIRFLOW-007: data_classification` and warn**. Never silently default. |
| `l1_xmatters_group` | prompt — AD group name (no contract field for this) |
| `lifecycle_phase` | default `build` for new DAGs; ask if user signals a retrofit |
| `criticality` | **required prompt — no default.** Ask the user three questions so the answer is grounded: (a) is there a regulatory or SLO dependency on this dataset? (b) does it have business-hours-only consumers, or 24×7? (c) does an on-call rotation own it today? Map: any "yes" to (a) **and** (c) → `critical`; "yes" to (a) **or** any 24×7 dependency → `high`; otherwise → `standard`. Silent defaults page nobody. |

Optional (only prompt if the user signals they want them): `l2_xmatters_group`, `l3_xmatters_group`, `app_id`, `business_function`.

See `references/mds-tags.md` for the full set and the routing model. In
`prototype` mode, unresolved required tags become `# TODO PY-AIRFLOW-007:
<tag>` comments and the skill warns; in `production` mode, the required
set is enforced before emission and the skill refuses to write if any are
unresolved.

### Step 4 — Ask for trigger mode

Two options:
- **Asset-driven** (default for `production`): which upstream dataset's
  data-ready event triggers this DAG? (e.g., `raw_positions_ready`)
- **Schedule (cron)**: emit a cron schedule. Advisory comment notes the
  preference for Asset-driven.

Also collect the DAG ID frequency token for PY-AIRFLOW-012. This is the
third DAG ID segment in `<domain_or_app>__<dataset>__<frequency>` and must
be a lowercase snake_case slug (for example: `daily`, `hourly`,
`intraday_15m`, `weekly`).

See `references/mode-aware-emission.md` for the schedule selection logic.

### Step 5 — Ask for resourcing tier (Pattern A / vendored Pattern B only)

Map the dataset's compute demand to one of:
- `xs` → `pool: databricks_xs`, `pool_slots: 1`
- `sm` → `pool: databricks_sm`, `pool_slots: 2`
- `md` → `pool: databricks_md`, `pool_slots: 4`
- `lg` → `pool: databricks_lg`, `pool_slots: 8`

Cite `skills/dbt-best-practices/references/sql-warehouse-sizing.md` for
the benchmarking methodology.

**Not applicable for `existing` blueprints mode.** The team's
`databricks_run_now` blueprint exposes only `job_name` +
`databricks_conn_id` — it doesn't carry pool / pool_slots fields. The
job itself controls its compute via the deployed Databricks job's
cluster spec (managed by `/setup-databricks-asset-bundle`). Skip Step 5
when `blueprints-source: existing`.

### Step 6 — Emit files

Per dataset, write the following files. Each file's content is templated
from the references; see `references/pattern-dag-factory.md` (Pattern A) or
`references/pattern-astro-blueprints.md` (Pattern B) for the exact YAML.

Per-dataset path (correct path: `data_products/` with underscore, not
`data-products/`):

- Pattern A (dag-factory): `data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml`
- Pattern B (astro-blueprints): `data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag.yml`
- Pattern C (python): `data_products/<product>/datasets/<dataset>/airflow/<dataset>_dag.py`
- All patterns: `<dataset>.dq.yml` (DQ checks)

Repo-shared (one-time, idempotent — skip-if-modified). Emitted under
`include/` because Astronomer auto-adds `include/` to `sys.path`, which
is what makes `from include.callbacks.X import callback` resolve:
- `include/assets.py`
- `include/callbacks/on_success_log_databricks_url.py`
- `include/shared/databricks_dbt.py` — **Pattern B `vendored` only.** Skipped when `blueprints-source: existing` (the team's `.blueprints/` already provides equivalents).
- `include/shared/asset_signal.py` — same: Pattern B `vendored` only.

**Important — what NOT to emit in `existing` blueprint mode.** The team's
`ProjectDagArgsConfig` (in `data_products/.blueprints/dag_args.py`) types
`default_args` as `dict[str, str]` and exposes only `schedule`,
`description`, `start_date`, `catchup`, `tags`, `default_args`. That
means:

- ❌ Don't emit `default_args.retries: 3`, `retry_*`, `execution_timeout`,
  `on_failure_callback` — they'll fail Pydantic validation (int / list /
  callable types) or be silently dropped.
- ❌ Don't emit top-level `max_active_runs`, `max_active_tasks`,
  `render_template_as_native_obj` — `ProjectDagArgs.render()` doesn't
  include them. Emit a `# TODO PY-AIRFLOW-018` comment instead, pointing
  at the platform-team task to extend `dag_args.py`.
- ✅ Do emit `default_args.owner: <owner>` — string, valid.
- ✅ All retry / timeout standards (PY-AIRFLOW-003/004/016/017)
  are satisfied **inside the blueprints themselves** (`dag_exec_check`
  hardcodes `retries=5` + `mode=reschedule`; `databricks_run_now` hardcodes
  `deferrable=True` + its own Databricks-aware failure callback that harvests
  the Databricks run logs locally). Failure alerting (PY-AIRFLOW-008) is
  provided by Astronomer's platform Datadog integration — not a DAG- or
  blueprint-emitted callback. The skill's job is to verify the right blueprint
  is *used*, not to set these fields in YAML. See
  `references/pattern-astro-blueprints.md` "What's enforced where" for
  the full split.

Tests (per-dataset):
- `tests/dags/test_<dataset>_dag.py` — YAML-level structural checks
  (PY-AIRFLOW-007/-012/-018 etc.); runs without Airflow installed so it's
  pre-commit-friendly.
- `tests/dags/test_<dataset>_dag_integrity.py` — DagBag-based integrity +
  `dag.test()` against a stub env (PY-AIRFLOW-014) + the shared
  `assert_dag_compliant(dag)` (PY-AIRFLOW-022). Requires Airflow installed;
  this is the canonical compliance gate.

Packaging handoff (required for generated callbacks/tests):
- Ensure the consumer repo's Python deps include the platform-provided
  `edo_airflow_lib` package used by the integrity test.
- Per org policy, installs must use cgrepo, not public PyPI. In
  `requirements.txt`, set:

```txt
--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/
```

Templates live in `templates/airflow/dataset_dag.py`, `templates/include/*`
(shared callbacks + blueprint helpers), `templates/tests/test_dag_structural.py`,
and `templates/tests/test_dag_integrity.py`. Skill reads them at emission
time and writes them to the team's repo.

For Pattern A (dag-factory), emit `databricks_conn_id` via Astronomer
Connection templating:

```yaml
databricks_conn_id: "{{ conn.databricks_default.conn_id }}"
```

Also add a short inline note or summary sentence that `job_name` is templated
with `databricks_job_prefix` to match the bundle's deployed naming convention
(the compose-with-bundle contract).

**Per-pattern substitutions for `test_dag_structural.py`** — the structural
template carries two placeholders the skill MUST resolve so the test points
at the file the pattern just emitted (otherwise `DAG_PATH.exists()` is
False and the gate is a silent no-op):

| Placeholder | Pattern A | Pattern B | Pattern C |
|---|---|---|---|
| `{{DAG_FILE_NAME}}` | `<dataset>.dag-factory.yml` | `<dataset>.dag.yml` | `<dataset>_dag.py` |
| `{{PATTERN}}` | `dag-factory` | `astro-blueprints` | `python` |

Pattern C's DAG file is `.py`, so the template short-circuits with a
module-level `pytest.skip(..., allow_module_level=True)` when
`PATTERN == "python"` — compliance is covered by the integrity test's
`assert_dag_compliant(dag)` (PY-AIRFLOW-022).

### Step 7 — Lift-and-shift specifics

If `mode: lift-and-shift`, output goes to **non-runtime location**:

```
workspace/dag-proposals/data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
```

This mirrors the canonical layout under the `workspace/` prefix so Airflow's
DAG scanner cannot pick it up. User diffs against the runtime original and
merges manually.

When emitting lift-and-shift output, the final response must include all of:

- The exact proposal path under `workspace/dag-proposals/` (never the runtime path).
- A `Changed` section listing what was rewritten to meet RFD 0011.
- A `Preserved` section listing what stayed as-is from the original DAG.
- Inline `# ADDED by /generate-dag` comments on newly added required MDS tags.

See `references/lift-and-shift.md` for the full flow.

## RFD 0011 directive map

Every emitted YAML/Python file carries `# PY-AIRFLOW-NNN` inline comments
at the relevant lines. Two reference docs cover the two angles:

- `references/rfd-0011-citations.md` — "what the skill emits per directive"
- `references/compliance-checklist.md` — "what gets checked, and where
  (emission grep / structural test / integrity test / review)"

The compliance checklist is the canonical map of which rules block which
test step.

## Anti-goals

- No PythonOperator for compute (compute lives in Databricks).
- No DAG-level alerting callbacks — Datadog alerting is provided by Astronomer at the platform level, not emitted by the DAG. No PagerDuty, no Slack. From the Datadog alert, Teams notification (Datadog→Teams) and xMatters paging are both **manual** by support; the routing tags are the context they read.
- No watermark-table idempotency (partition-keyed writes + MERGE only).
- No S3-as-handoff defaults (Unity Catalog is default).
- No skill-emitted pip-installable Catalyst runtime helper library
  (helpers are vendored). Platform-shared `edo_airflow_lib` is in scope
  for the integrity/compliance gate.
- No DLT / Lakeflow.
- No dbt Cloud, no MCP.

## When NOT to use this skill

- The team's DAG is not Catalyst-shaped (not in `data_products/<product>/datasets/<dataset>/`).
- The team uses a non-Airflow orchestrator (e.g., Prefect, Dagster). Out of scope.
- Bulk retro-fitting 50+ DAGs at once. Single-dataset-at-a-time only (see OQ-4).
