# RFD 0011 Directive Map

Every emission decision in `/generate-dag` traces back to a specific section
of RFD 0011. This map is the master reference; the per-pattern templates
(`pattern-dag-factory.md`, `pattern-astro-blueprints.md`) cite back to
entries here in their inline `# RFD 0011 §<N>` comments.

If RFD 0011 numbering changes after revision, update this file FIRST, then
the templates inherit.

## §1 — Idempotency

| Skill emits | How |
|---|---|
| Partition-keyed write | `partition_key: "{{ ds }}"` in `notebook_params:` or `params:` |
| MERGE on identity key | Delegated to the Databricks job; DAG passes `execution_date` as a partition discriminator |
| NO watermark tables | Skill never emits a watermark sensor or watermark update task (anti-goal) |

## §2 — Retries and failure handling

| Skill emits | How |
|---|---|
| `retries: 3` | `default_args.retries: 3` |
| Exponential backoff | `default_args.retry_exponential_backoff: true` |
| Fail-fast on deterministic errors | All patterns: task code raises `AirflowFailException` for deterministic failures (SQL compile, schema mismatch, contract validation). Airflow's scheduler hardcodes "no retry on `AirflowFailException`" — there is no per-operator `retry_on_exception` predicate API, so the skill emits no callable filter. |
| `retry_delay_seconds: 30` | Initial backoff seed |

Task code that needs to distinguish deterministic vs. transient failures
catches the deterministic types (e.g., SQL compile errors, schema
mismatches) and re-raises as `AirflowFailException`. The Databricks
Airflow provider exception module (`airflow.providers.databricks.exceptions`)
exports `DatabricksSqlExecutionError` and `DatabricksSqlExecutionTimeout`;
there is no `DatabricksTransientError` class.

## §3 — Resourcing and configuration

| Skill emits | How |
|---|---|
| Pool slot allocation | `pool: databricks_<tier>` and `pool_slots: <n>` per t-shirt tier (xs=1, sm=2, md=4, lg=8) |
| Benchmarking methodology | Inline comment cites `skills/dbt-best-practices/references/sql-warehouse-sizing.md` |
| `deferrable: true` | Async-friendly operator config to reduce slot occupancy |

## §4 — Scheduling and triggering

| Skill emits | How |
|---|---|
| `start_date: <today UTC>` | Set at generation time to UTC |
| `catchup: false` | Always |
| `render_template_as_native_obj: true` | Always |
| Asset-driven trigger (default for production) | `schedule: [- dataset: "<upstream>_ready"]` |
| Cron fallback (with advisory) | `schedule: "<cron-string>"` + advisory comment |

## §5 / new §6 — Observability, alerting, SLAs

(Section renumbered §5 → §6 in the discussion-state RFD 0011; kept under
the old heading here for diff-friendliness. PY-AIRFLOW-007 and -008 are
the load-bearing directives.)

| Skill emits | How |
|---|---|
| Required tag set — operational (PY-AIRFLOW-007) | `tags:` list of `key:value` strings: `l1_domain`, `l1_xmatters_group`, `lifecycle_phase`, `data_classification`, `criticality` (+ `deliver_by_day`/`deliver_by_time` when `criticality: critical`; optional `l2_xmatters_group`, `l3_xmatters_group`). See `mds-tags.md` |
| Required tag set — MDS attribution (PY-AIRFLOW-007) | `owner`, `business_function`, `data_domain`, `app_id` — a union with the operational set, sharing `data_classification`. See `mds-tags.md` |
| Failure alerting (PY-AIRFLOW-008) | Provided by Astronomer's platform Datadog integration; **no** DAG-level `on_failure_callback` is emitted, and no blueprint emits a Datadog event |
| Routing-tag context (PY-AIRFLOW-008) | `criticality`, `l1_xmatters_group`, `l2_xmatters_group`, `l3_xmatters_group`, `lifecycle_phase`, `l1_domain`, `data_classification` are tags support and Datadog's tag-based monitors read to decide **manual** Teams/xMatters escalation — context, not triggers, and not carried by a DAG-emitted event |
| Databricks click-through on_success | `on_success_callback: "include.callbacks.on_success_log_databricks_url.callback"` |
| SLA — emit ONLY if contract has SLA field | `default_args.sla.minutes: <from-contract>` OR commented-out block with directive comment |
| NEVER default an SLA | Skill emits no `sla:` field if contract has no SLA value |
| No PagerDuty, no Slack | xMatters paging is **manual** by support, not from DAG code. Teams is the chat surface. PagerDuty / Slack are anti-goals. |

## §6 — Task design

| Skill emits | How |
|---|---|
| `DatabricksRunNowOperator` for compute | All compute tasks use this operator referencing a deployed bundle job |
| NO `PythonOperator` for calculation logic | Explicit anti-goal; emitter refuses to emit `PythonOperator` with task body referencing data ops |
| TaskFlow only for orchestration glue | Sensor polling, conditional branching, XCOM manipulation OK; data calculations not OK |
| Small tasks | Default: one task per DAG (the Databricks job); split only when teams need finer-grained retry boundaries |
| No top-level side effects | Skill emits no module-level code in generated DAG files |

## §7 — Code organisation

| Skill emits | How |
|---|---|
| DAG ID convention `<l1_domain>__<dataset>__<frequency>` | Three-part with `__` separators per RFD 0011 §8 (PY-AIRFLOW-012). New DAGs follow this exactly. **Tie-breaker for existing repos:** when a repo already uses a different convention (e.g. `edo-ig-data-products` uses bare `<dataset>`), leave existing DAG IDs alone, but emit new DAGs in the RFD form. The skill prompts the user once per repo to confirm the convention and writes the choice to `.catalyst-build.yml#dag_id_style: rfd | legacy` so subsequent runs are deterministic. |
| Vendored shared helpers | `include/assets.py`, `include/callbacks/*`, `include/shared/*` (Pattern B); see `pattern-*.md` |
| No skill-emitted pip-installable Catalyst runtime helper library | Anti-goal (§9) — generated helper modules are shipped via file emission, while platform-shared `edo_airflow_lib` remains in scope for integrity/compliance tests |

## §8 — Secrets and connections

| Skill emits | How |
|---|---|
| `databricks_conn_id` via Astronomer Connection | `"{{ conn.databricks_default.conn_id }}"` |
| Job name prefix via Airflow Variable | `"{{ var.value.databricks_job_prefix }}"` |
| NO literal tokens | Skill refuses to emit any `token=` or `password=` literal |
| Workspace URL via Variable | `Variable.get("databricks_workspace_url")` in `include/callbacks/on_success_log_databricks_url.py` |

## §9 — Testing

| Skill emits | How |
|---|---|
| `<dataset>.dq.yml` for DQ checks | Per-dataset, alongside the DAG file. Derived from data contract DQ rules |
| Structural pytest | `tests/dags/test_<dataset>_dag.py` from `templates/tests/test_dag_structural.py` — parses the emitted DAG YAML and asserts MDS tag completeness, retry list presence, no PythonOperator |

## §10 — CI / CD enforcement

Out of scope for this skill. Emitted DAGs are tag-compliant so a future CI
gate can parse them without modification. The gate itself is a separate
deliverable (e.g., a pre-commit hook or GitHub Action that runs the
emitted structural tests + a tag completeness check).

---

## PY-AIRFLOW-016..022 — directives added in the discussion-state RFD 0011

The IDs below come from `rfd/0011/README.md` on the `rfd/0011` branch
(state: discussion). When that RFD merges, the §-numbering above will
shift; this section is held separate so the diff stays surgical.

### PY-AIRFLOW-016 — Deterministic failures fail fast

| Skill emits | How |
|---|---|
| Surface non-retriable exception types | All patterns rely on `AirflowFailException` raised from task callables (Airflow's scheduler hardcodes "do not retry on `AirflowFailException`"). Deterministic types — SQL compile, schema mismatch, contract validation — must be caught at the call site and re-raised as `AirflowFailException`. There is no `retry_on_exception` parameter on `BaseOperator`; the skill does not emit one. |
| No blanket retry on everything | Task code catches deterministic exceptions explicitly; everything else falls through to the bounded `retries` / `retry_delay` / `max_retry_delay` policy. |

See `compose-with-bundle.md` for the authoritative Databricks-provider
exception class list at emission time.

### PY-AIRFLOW-017 — Deferrability and bounded waits

| Skill emits | How |
|---|---|
| Deferrable Databricks operator | `deferrable: true` on every `DatabricksRunNowOperator` task |
| Bounded `execution_timeout` | DAG-level default + per-sensor explicit `timeout` |
| Sensor mode | When a classic sensor is emitted (cron-only paths, fallback waits), `mode: reschedule` is set so the worker slot releases between pokes; default `poke` mode is refused |
| No unbounded waits | Skill refuses to emit a sensor without `timeout` set |

### PY-AIRFLOW-018 — Bounded parallelism

| Skill emits | How |
|---|---|
| DAG-level cap on concurrent runs | `max_active_runs: 1` (override only with justification) |
| DAG-level cap on concurrent tasks | `max_active_tasks: 4` default; tunable per dataset |
| Backfill safety with `catchup: true` | If a team overrides to `catchup: true`, the skill enforces `max_active_runs: 1` to prevent every-missed-interval-at-once thundering herd |

### PY-AIRFLOW-019 — Asset-driven by default

| Skill emits | How |
|---|---|
| Default `schedule` shape | `schedule: - dataset: "<upstream>_ready"` (dag-factory) or `schedule=[Asset(...)]` (pure Python) |
| Cron is opt-in with reason | When the user picks cron, the skill requires a one-line reason and emits it as `# RFD 0011 §5 — reason: <reason>` next to the schedule literal |
| Manual-only DAGs | `schedule: null` / `schedule=None` with the same reason convention |

### PY-AIRFLOW-020 — No secret values in operator args

| Skill emits | How |
|---|---|
| Secret material via `conn_id` only | Passed by name; hook resolves the credential at task runtime |
| Refuses literal secret values | Pre-emit grep rejects `password=`, `token=`, `api_key=`, AWS access key patterns, and any operator arg whose value resolves to `Variable.get(...)` at module scope (PY-AIRFLOW-009 / PY-AIRFLOW-013 overlap) |
| Inline runtime fetch when unavoidable | When the operator has no `conn_id` for the credential, the skill emits a task callable that fetches via `boto3.client("secretsmanager")` (or equivalent) inside the task body — never as an operator argument |

### PY-AIRFLOW-021 — Local dev guidance in emitted artifact

| Skill emits | How |
|---|---|
| `doc_md` "Local dev" section | Includes the canonical `astro dev start` invocation and a `airflow tasks test <dag_id> <task_id> <YYYY-MM-DD>` example for the emitted DAG. Authors iterate locally before pushing — CI is not the inner loop. |

### PY-AIRFLOW-022 — Shared compliance check

| Skill emits | How |
|---|---|
| Test imports `assert_dag_compliant` | `from edo_airflow_lib.compliance import assert_dag_compliant` — single org-wide source of truth for what "compliant" means |
| Test runs `assert_dag_compliant(dag)` | After loading the DAG via `DagBag`, the test calls the shared helper to enforce §1–§9 in one place. Per-DAG tests do not re-implement the checks. |

The shared helper itself is a deliverable of the platform team (RFD 0011
§8 + §11), not of this skill. The skill emits a test that *uses* it.
