# Pattern B — astro-blueprints

Higher-level emission pattern. Uses Astronomer's blueprint framework
(`.blueprints/*.py` Python files loaded by a blueprint loader such as
`data_products/blueprints_loader.py`) to abstract Airflow operators behind
named blueprints. Less portable than dag-factory; more abstracted; emits
much terser YAML.

## When chosen

- Team's repo has a blueprint loader (e.g. `blueprints_loader.py`) wired
  to `.blueprints/*.py`.
- User explicitly opts in to astro-blueprints.

## Blueprints source — `vendored` vs `existing`

| Sub-mode | When | What the skill emits |
|---|---|---|
| `vendored` (legacy default) | Greenfield repo with no existing `.blueprints/` — or the team wants the skill to own the blueprint vocabulary | Emits its own blueprint Python files (`include/shared/databricks_dbt.py`, `include/shared/asset_signal.py`) and references them by their vendored names |
| `existing` (recommended for `edo-ig-data-products`) | Repo already has a populated `data_products/.blueprints/` directory | Reads the target's `.blueprints/*.py` to discover available blueprint names and their Pydantic config schemas; emits a `*.dag.yml` referencing them by name with field names that match. **Does not emit** `include/shared/*.py` |

The skill auto-selects `existing` when it sees a populated `.blueprints/`
directory with at least one of: `databricks_run_now.py`, `dag_args.py`,
or a file matching `*_run_now.py`. Otherwise defaults to `vendored`. The
user can override either way.

### Discovery flow for `existing`

1. `ls data_products/.blueprints/*.py` (or wherever the loader points).
2. For each module, parse the top-level class names that subclass
   `blueprint.Blueprint` (or `blueprint.BlueprintDagArgs`). The class's
   snake_case file name is what `*.dag.yml` references via
   `blueprint: <name>`.
3. For each class, parse its `*Config(BaseModel)` Pydantic class to learn
   the **exact** field names and types the YAML must use. Don't guess
   schemas — read them.
4. If the dataset's needs require a blueprint the target doesn't have,
   **stop and ask** the user to add it under `.blueprints/` rather than
   inlining an operator in the DAG YAML — the abstraction boundary
   matters for RFD 0011 §8.

---

## Canonical blueprints (as shipped in `edo-ig-data-products`)

Read these schemas from `data_products/.blueprints/*.py` directly. The
table below is **a mirror, not a substitute** — when the team adds a
field to a blueprint, update both the `.py` and this section together.

### `dag_args` — DAG-level args (`ProjectDagArgsConfig`)

Top-level dictionary that the blueprint framework converts into kwargs
for the `DAG(...)` constructor. **Defined in `dag_args.py`.**

```python
class ProjectDagArgsConfig(BaseModel):
    schedule: str | None = None
    description: str | None = None
    start_date: str | None = None
    catchup: bool = False
    tags: list[str] = Field(default_factory=list)
    default_args: dict[str, str] = Field(default_factory=dict)
```

**Critical:** `default_args` is typed `dict[str, str]`. Pydantic rejects
`int`, `bool`, `list`, or callables here. What this means for the skill:

- ✅ `default_args.owner: "EDO IG"` — string, valid.
- ❌ `default_args.retries: 3` — int, will fail validation.
- ❌ `default_args.retry_on_exception: <anything>` — there is no such Airflow `BaseOperator` parameter (the scheduler hardcodes "no retry on `AirflowFailException`"); emitting this key is dead config in any pattern. Deterministic fail-fast lives in task code that raises `AirflowFailException`.
- ❌ `default_args.on_failure_callback: "shared.callbacks.x"` — dotted string can't be turned into a callable by the framework.
- ❌ `default_args.execution_timeout: 3600` — int, fails.

The skill must emit ONLY string-valued entries in `default_args` (in
practice, just `owner`). The retry / callback / timeout standards
(PY-AIRFLOW-003/004/008/016/017) are satisfied at the **blueprint
source level**, not at the YAML level — see "What's enforced where"
below.

**Fields `ProjectDagArgsConfig` does NOT expose** (silently dropped if
emitted in YAML):

- `max_active_runs`, `max_active_tasks`, `max_consecutive_failed_dag_runs`
  (PY-AIRFLOW-018)
- `render_template_as_native_obj`
- `on_failure_callback` at DAG level (PY-AIRFLOW-008 lives per-task)
- `dagrun_timeout`, `sla_miss_callback`

For PY-AIRFLOW-018 in particular, the skill emits a top-level comment in
the YAML noting the limitation:

```yaml
# TODO PY-AIRFLOW-018: max_active_runs / max_active_tasks not honored
# in this repo until ProjectDagArgsConfig (data_products/.blueprints/
# dag_args.py) exposes them. Platform-team task tracked separately.
```

### `dag_exec_check` — wait-for-upstream-DAG sensor (`DagExecCheckConfig`)

Polls an external Airflow DAG's task completion via a BashSensor.
**Defined in `dag_exec_check.py`.**

```python
class DagExecCheckConfig(BaseModel):
    upstream_dag: str                                     # required
    dag_task_id: str = "task_std_tag_files"
    dag_exec_check_timeout: int = 36000                   # 10 hours
    lookback_window_seconds: int = 43200                  # 12 hours
    check_manual_run: str = "Y"
    wait_for_failed_dependency: str = "Y"
    sleep_interval_seconds: int = 60
    executor_memory: str = "2g"
    driver_memory: str = "4g"
```

**Hardcoded inside `render()`** (NOT configurable from YAML):

- `mode="reschedule"` ← satisfies PY-AIRFLOW-017 (release worker slot)
- `poke_interval = sleep_interval_seconds`
- `timeout = dag_exec_check_timeout` ← bounded wait
- `retries=5`, `retry_exponential_backoff=True`, `retry_delay=60s`
  ← satisfies PY-AIRFLOW-003/004 for this blueprint

### `databricks_run_now` — run a deployed Databricks job (`DatabricksRunNowConfig`)

Renders to `DatabricksRunNowOperator`. **Defined in
`databricks_run_now.py`.** (The skill's prior `databricks_dbt` reference
is wrong — that blueprint doesn't exist in this repo.)

```python
class DatabricksRunNowConfig(BaseModel):
    job_name: str                                         # required
    databricks_conn_id: str = "caspian-ig-databricks"
```

**Hardcoded inside `render()`**:

- `deferrable=True` ← satisfies PY-AIRFLOW-017
- `on_failure_callback=_databricks_failure_callback` — a module-local
  callback that pulls Databricks run logs into the Airflow task log. This is
  a local diagnostic, not an alerting hop: failure alerting (PY-AIRFLOW-008) is
  provided by Astronomer's platform Datadog integration, not emitted by this
  callback. The skill cannot override the blueprint callback from YAML.

**PY-AIRFLOW-008 in `existing` mode:** no per-blueprint Datadog wiring is
required or expected. Datadog alerting is built into Astronomer at the platform
level, so the `databricks_run_now` callback is expected to do local log
harvesting only — the skill does not require (or add) Datadog emission in the
blueprint to claim PY-AIRFLOW-008 compliance.

Only two fields are user-settable: `job_name` and `databricks_conn_id`.
That's the entire surface.

### `xcom_generation` — generate xcom payload from a contract (`XcomGenerationConfig`)

Queries Databricks via SQL warehouse to build the data-ready event
payload that `kafka_notify` later publishes. **Defined in
`xcom_generation.py`.**

```python
class XcomGenerationConfig(BaseModel):
    configuration: str                                    # path to ODCS contract yaml
    target_schema: str                                    # "<catalog>.<schema>"
    operation_type: str = "change"
    pre_checkpoint: str = "NA"
    post_checkpoint: str = "NA"
    partition_date_column: str = "partitiondate"
    process_date: str = "{{ (data_interval_end - macros.timedelta(days=1)).strftime('%Y-%m-%d') }}"
    databricks_conn_id: str = "caspian-ig-databricks"
    http_path: str                                        # required
    retries: int = 3
    retry_delay_seconds: int = 30
```

The `configuration` and `target_schema` fields typically use Airflow
Variable templates so the resolved path stays per-environment:

```yaml
configuration: "{{ var.value.data_products_path }}/shared_ref/datasets/<dataset>/contract/<dataset>.odcs.yaml"
target_schema: "{{ var.value.default_catalog }}.{{ var.value.default_schema }}"
http_path: "{{ var.value.http_path }}"
```

### `kafka_notify` — publish the data-ready Kafka event (`KafkaNotifyConfig`)

Renders to a `PythonOperator` that invokes the team's `data_notify.DataNotify`
helper to publish the event. **Defined in `kafka_notify.py`.** (The skill's
prior `dataset_uri` / `logical_window` field names are wrong — the real
fields are `xcom_pull_task` and `model`.)

```python
class KafkaNotifyConfig(BaseModel):
    xcom_pull_task: str                                   # required — name of the xcom_generation step
    model:          str                                   # required — model / dataset name
    # Kafka infra (Airflow Variable templates by default; rarely overridden):
    kafka_topic:          str = "{{ var.value.data_notify_topic }}"
    kafka_secret_arn:     str = "{{ var.value.kafka_secret_arn }}"
    rootca_secret_arn:    str = "{{ var.value.rootca_secret_arn }}"
    bootstrap_brokers:    str = "{{ var.value.bootstrap_brokers }}"
    schema_registry_url:  str = "{{ var.value.schema_registry_url }}"
    platform:             str = "caspian-ig"
    aws_region:           str = "{{ var.value.aws_region }}"
    source:               str = "caspian"
    aws_conn_id:          str = "aws_default"
    retries:              int = 3
    retry_delay_seconds:  int = 30
```

Typical usage: pass `xcom_pull_task` matching the `xcom_generation` step
name, and `model` matching the dataset name.

---

## Canonical worked example — `currency.dag.yml`

The skill's `existing`-mode emission for a new dataset should be
structurally identical to `data_products/shared_ref/datasets/currency/airflow/currency.dag.yml`:

```yaml
dag_id: <dataset>
description: Run <dataset> dataset pipeline (includes dbt)
schedule: "@daily"                                # or "- dataset: <upstream>_ready" for Asset-driven
start_date: "<YYYY-MM-DD>"
catchup: false
tags:
  - "l1_domain:<l1_domain>"                       # PY-AIRFLOW-007 — required set
  - "l1_xmatters_group:<l1_xmatters_group>"
  - "lifecycle_phase:build"
  - "data_classification:<classification>"
  - "criticality:<criticality>"
  - <product>                                     # repo convention: bare product tag

default_args:
  owner: <owner>                                  # ONLY string-valued entries here per ProjectDagArgsConfig

# TODO PY-AIRFLOW-018: max_active_runs / max_active_tasks not honored
# until ProjectDagArgsConfig exposes them. Platform-team task tracked
# separately.

steps:
  run_dag_exec_check:
    blueprint: dag_exec_check                     # PY-AIRFLOW-017 — built-in mode=reschedule + bounded timeout
    upstream_dag: <upstream-airflow-dag-id>
    dag_task_id: <upstream-terminal-task-id>
    lookback_window_seconds: 300

  run_<dataset>_dbt:
    blueprint: databricks_run_now                 # PY-AIRFLOW-010/-017 — built-in deferrable + databricks-aware callback
    job_name: "{{ var.value.get('databricks_job_prefix', '') }}<dataset>_job"
    databricks_conn_id: caspian-ig-databricks

  run_<dataset>_dq:
    depends_on: [run_<dataset>_dbt]
    blueprint: databricks_run_now
    job_name: "{{ var.value.get('databricks_job_prefix', '') }}<dataset>_dq_job"
    databricks_conn_id: caspian-ig-databricks

  xcom_generation:
    depends_on: [run_<dataset>_dq]
    blueprint: xcom_generation                    # PY-AIRFLOW-015 — produces the data-ready event payload
    configuration: "{{ var.value.data_products_path }}/<product>/datasets/<dataset>/contract/<dataset>.odcs.yaml"
    target_schema: "{{ var.value.default_catalog }}.{{ var.value.default_schema }}"
    operation_type: change
    http_path: "{{ var.value.http_path }}"

  notify_<dataset>:
    depends_on: [xcom_generation]
    blueprint: kafka_notify                       # PY-AIRFLOW-015 — publishes the event
    xcom_pull_task: xcom_generation
    model: <dataset>
```

---

## What's enforced where (existing-mode `*.dag.yml`)

PY-AIRFLOW directives in the existing-mode pattern split into three buckets:

| Where enforced | Directives | Notes |
|---|---|---|
| **YAML structural test** (the skill's existing structural test, run by CI) | PY-AIRFLOW-002 (start_date literal), PY-AIRFLOW-006 (catchup explicit), PY-AIRFLOW-007 (required tags), PY-AIRFLOW-012 (DAG ID — legacy form per `.catalyst-build.yml#dag_id_style: legacy` in this repo), PY-AIRFLOW-019 (schedule explicit) | YAML parse + tag-key presence + value range |
| **Blueprint source level** (asserted at the Python class, not YAML) | PY-AIRFLOW-003 (retries), PY-AIRFLOW-004 (backoff), PY-AIRFLOW-016 (deterministic-fail), PY-AIRFLOW-017 (deferrability — `mode=reschedule` in dag_exec_check, `deferrable=True` in databricks_run_now) | The skill verifies the right blueprint is *used* in the YAML; the blueprint's `.py` source is what actually meets the standard. If a blueprint is replaced or modified, that's the platform team's contract. |
| **Platform-side** (nothing the skill or blueprint emits) | PY-AIRFLOW-008 (failure alerting) | Datadog alerting is built into Astronomer; no DAG- or blueprint-level callback. Routing tags are context support reads for manual Teams/xMatters escalation. |
| **Not honored today** (TODO comments in emitted YAML; platform-team change needed) | PY-AIRFLOW-018 (max_active_runs / max_active_tasks — not exposed by `ProjectDagArgsConfig`) | The skill emits the rule as a `# TODO PY-AIRFLOW-018` comment with a pointer to the platform-team task to extend `dag_args.py`. |

## Vendored sub-mode template (legacy fallback)

For repos without a populated `.blueprints/`, the skill falls back to
emitting its own blueprint helpers. That path is preserved in
`templates/include/shared/` for the small number of repos that haven't
yet been migrated to the team-owned blueprint pattern. The same RFD-0011
directives apply, enforced YAML-side in the vendored sub-mode (because
the vendored helpers were designed to expose retries / callbacks /
timeouts as configurable fields).

The skill chooses vendored only when `.blueprints/` is absent or empty —
existing populated `.blueprints/` always wins.

## Placeholder fill-in

Same matrix as Pattern A (see `pattern-dag-factory.md`) plus:

| Placeholder | Source |
|---|---|
| `blueprint` refs | `vendored`: defaults to `.blueprints.databricks_dbt` family. `existing`: names discovered from target repo's `.blueprints/*.py` (e.g. `dag_exec_check`, `databricks_run_now`, `xcom_generation`, `kafka_notify`). |
| `<upstream-airflow-dag-id>` | The Airflow DAG ID that produces the upstream dataset. For `edo-ig-data-products`, ingestion DAGs follow the pattern `ingestion-rdm-<source>_rdm_<dataset>_f2_v1_t3`. |
| `xcom_pull_task` | The step ID of the `xcom_generation` step in this DAG (typically `xcom_generation`). |
| `model` in `kafka_notify` | The dataset name. |
