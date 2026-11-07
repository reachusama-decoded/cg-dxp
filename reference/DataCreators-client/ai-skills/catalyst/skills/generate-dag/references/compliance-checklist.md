# Compliance checklist

Per-rule enforcement map. `rfd-0011-citations.md` answers *"what does the
skill emit per directive?"*. This file answers *"what gets checked to
confirm the rule is satisfied, and where?"*. Together they form the
adaptive (skill judgment) + deterministic (CI gate) loop.

Four enforcement points:

- **Emission-time** — the skill greps / inspects its own output before
  writing files. Catches the rule before the user ever sees a failing test.
- **Structural test** — `templates/tests/test_dag_structural.py` parses the
  emitted YAML; runs in pre-commit and CI. No Airflow dependency.
- **Integrity test** — `templates/tests/test_dag_integrity.py` uses
  `DagBag`, `dag.test()`, and `assert_dag_compliant(dag)`. Requires
  Airflow + the platform's `edo_airflow_lib`. CI only.
- **Blueprint source** *(existing-mode astro-blueprints only)* — the
  directive is satisfied by the blueprint's Python `render()` method,
  not by anything in the emitted YAML. E.g. `dag_exec_check.py` hardcodes
  `mode="reschedule"`; `databricks_run_now.py` hardcodes `deferrable=True`
  and its own Databricks-aware `on_failure_callback` that harvests Databricks
  run logs locally. Failure alerting (PY-AIRFLOW-008) is platform-side Datadog
  via Astronomer, not a blueprint-emitted callback. The skill's job in
  this case is to verify the right blueprint is *referenced* in the YAML;
  the platform team owns the blueprint contract.
- **Review** — for rules that are judgment calls (e.g. task granularity),
  reviewer checklist; not automated.

## §1 — Idempotency

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-001** No `datetime.now()` / `date.today()` in DAG file; output partitions reference `{{ ds }}` / `{{ data_interval_* }}` | Emission grep + structural | Grep before write; structural test reads emitted YAML/Python and rejects matches |
| Unity Catalog writes are `MERGE` or `INSERT OVERWRITE` keyed on logical window | Review | DAG itself only references the Databricks job by name; the SQL inside is bundle-side |
| S3 writes under `dt={{ ds }}/` partition path | Review | Same — bundle-side |

## §2 — Retries

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-003** Every task `retries >= 1`; default 3 | Structural + integrity *(dag-factory / python / vendored-blueprint)*; **Blueprint source** *(existing-blueprint)* | Pattern A/C/B-vendored: YAML asserts `default_args.retries == 3`. Pattern B-existing: `dag_exec_check.py` hardcodes `retries=5`; `databricks_run_now` inherits Airflow defaults. The skill verifies the right blueprints are used. |
| **PY-AIRFLOW-004** `retry_delay`, `retry_exponential_backoff: True`, `max_retry_delay` set | Structural *(dag-factory/python/vendored)*; **Blueprint source** *(existing)* | Same split. `dag_exec_check.py` hardcodes `retry_exponential_backoff=True`, `retry_delay=60s` in `render()`. |
| **PY-AIRFLOW-016** Deterministic failures fail fast via `AirflowFailException` raised from task code | Structural *(all patterns)* asserts `retry_on_exception` is absent (it's not a real Airflow API — `BaseOperator` has no such parameter; the scheduler hardcodes "no retry on `AirflowFailException`") + Review *(correctness — task code wraps deterministic exception types and re-raises as `AirflowFailException`)*; **Blueprint source** *(existing)* | Skill flags this as a platform-team task if existing-mode blueprints don't yet handle deterministic-fail discrimination in their task implementations. |

## §3 — Deferrability

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-017** Databricks operators `deferrable: true`; sensors `mode: reschedule` + explicit `timeout`; DAG-level `execution_timeout` | Structural | Per-task walk asserts `deferrable: true` on Databricks ops, `mode: reschedule` + `timeout` on every `*Sensor`, `default_args.execution_timeout` set |

## §4 — Resourcing

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-005** Every task declares `pool`, `queue`, `executor_config` or T-shirt cluster | Structural (presence) + Review (correctness) | Asserts `pool` set in `default_args` or per-task; reviewer confirms the tier matches workload |
| **PY-AIRFLOW-018** `max_active_runs` + `max_active_tasks` set at DAG level | Structural | Asserts both are positive ints |

## §5 — Scheduling

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-002** `start_date` is a literal `datetime` in UTC; no `days_ago` | Emission grep + structural | Grep for `days_ago(`, `datetime.now()` rejects; structural confirms `start_date` shape |
| **PY-AIRFLOW-006** `catchup` set explicitly; cron carries `# RFD 0011 §5 — reason: ...` | Structural + grep | `catchup` presence asserted; grep for cron without reason comment |
| **PY-AIRFLOW-015** Producer emits data-ready event on success (Asset outlet or `kafka_notify`) | Structural | Last task of producer DAGs declares `outlets=[Asset(...)]` or uses the `kafka_notify` blueprint |
| **PY-AIRFLOW-019** `schedule` defaults to `Asset(...)` / dataset list | Review | Skill default; user opt-out for cron requires reason comment (caught by PY-AIRFLOW-006 check) |

## §6 — Observability + alerting

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-007** Required tag set present (`l1_domain`, `l1_xmatters_group`, `lifecycle_phase`, `data_classification`, `criticality`) with valid values | Structural | Asserts every key present, `criticality` in {`critical`, `high`, `standard`}, `lifecycle_phase` in {`build`, `operate`, `decom`} |
| **PY-AIRFLOW-008** No DAG-level `on_failure_callback` to Datadog (Astronomer provides Datadog alerting platform-side); no `email_on_failure`; no PagerDuty. Routing tags are context support reads for manual Teams/xMatters escalation | Structural *(all patterns)* | Structural asserts there is no Datadog/PagerDuty `on_failure_callback` (`test_no_dag_level_datadog_callback`). Routing-tag presence is checked by PY-AIRFLOW-007. Existing-blueprint: the `databricks_run_now` callback does local log harvesting only — no Datadog emission expected. |

## §7 — Task design

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-009** No module-scope I/O in DAG file | Emission grep + integrity | Grep rejects `Variable.get` / `Connection.get` / HTTP calls at module scope; integrity test parsing latency confirms cheap parse |
| **PY-AIRFLOW-010** TaskFlow / `@task` preferred over `PythonOperator` | Review | Reviewer checklist; auto-rejection too noisy for legitimate cases |
| **PY-AIRFLOW-011** XCom values ≤1KB | Review | Runtime check; structural can't see XCom |

## §8 — Code organization

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-012** DAG ID matches `^[a-z][a-z0-9_]*__[a-z0-9_]+__[a-z0-9_]+$` for new DAGs; existing repos using a different convention keep their legacy IDs and pin via `.catalyst-build.yml#dag_id_style: legacy` | Structural | Regex assert when `dag_id_style: rfd`; skip-with-warning when `legacy` |

## §9 — Secrets

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-013** Credentials via `conn_id`; secrets only via `Variable.get` inside task callables | Emission grep | Rejects `password=`, AWS access key patterns, `Variable.get` at module scope |
| **PY-AIRFLOW-020** No secret values as operator args | Emission grep | Rejects operator arg literals matching `token=`, `api_key=`, etc. |

## §10 — Testing

| Rule | Enforcement point | Check |
|---|---|---|
| **PY-AIRFLOW-014** Integrity test imports + `dag.test()` | Integrity | `test_<dataset>_dag_integrity.py` |
| **PY-AIRFLOW-021** `doc_md` references `astro dev start` | Structural | Grep `doc_md` block for `astro dev start` |
| **PY-AIRFLOW-022** `assert_dag_compliant(dag)` runs | Integrity | Imported from `edo_airflow_lib.compliance` and called in the integrity test |

## What the skill enforces *at emission time*

Before writing files:

- All required tags resolved (PY-AIRFLOW-007). Production mode: refuse to
  emit if any missing. Prototype mode: emit `# TODO` markers and warn.
- `databricks_job_prefix` resolved from `variables_<env>.yml`. Refuse in
  production mode if absent.
- Dataset's ODCS contract exists. If not, warn — the structural test will
  likely fail downstream regardless.
- No `datetime.now()` / `days_ago()` / hardcoded secrets in the emitted
  body (PY-AIRFLOW-001/002/013/020).

After writing files, the skill runs the structural test against the
generated DAG with `pytest -k test_<dataset>_dag` to confirm compliance
locally before the user opens a PR.
