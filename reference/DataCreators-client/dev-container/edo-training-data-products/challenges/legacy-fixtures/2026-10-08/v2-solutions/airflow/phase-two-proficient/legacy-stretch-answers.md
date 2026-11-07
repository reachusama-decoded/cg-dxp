# Instructor legacy stretch answers — airflow

Preserved from `challenges/v2/airflow/phase-two-proficient/stretch/README.md` before separation. These legacy exercises retain their separate v1 runtime and access requirements; they are not evidence of v2 live execution. No real notification or external publishing is authorized.
## Answer 1: Solution

`send_alert` is the one transport boundary. It resolves the webhook from the
`alert_webhook` Airflow connection and posts the message — no vendor named in
the code.

```python
from airflow.providers.http.hooks.http import HttpHook


def send_alert(text, channel=None, conn_id="alert_webhook"):
    hook = HttpHook(method="POST", http_conn_id=conn_id)
    payload = {"text": text}
    if channel is not None:
        payload["channel"] = channel
    hook.run(endpoint="", json=payload)
```

Swapping the team's chat tool means re-pointing the `alert_webhook` connection
— no code change.

Reference: `challenges/v1/03-airflow-orchestration/solution/include/alerting/notifications.py`.


## Answer 2: Solution

The failure callback is the P1 tier: it pages and notifies. `_emit_datadog`
posts to the Datadog Events API (or logs when `DD_API_KEY` is unset); support
pages via xMatters from the payload; `send_alert` posts to Microsoft Teams.

```python
def on_failure_callback(context):
    ti = context["task_instance"]
    dag_run = context.get("dag_run")
    detail = {
        "dag_id": ti.dag_id,
        "task_id": ti.task_id,
        "run_id": dag_run.run_id if dag_run else None,
        "log_url": ti.log_url,
        "exception": str(context.get("exception")),
    }
    _emit_datadog(summary=f"DAG failure: {ti.dag_id}.{ti.task_id}",
          severity="error", detail=detail)
    send_alert(text=(
        f"*DAG failure (Datadog alerted, xMatters paged)*\n*DAG:* {ti.dag_id}\n"
        f"*Task:* {ti.task_id}\n*Log:* {ti.log_url}\n"
        f"*Runbook:* https://wiki.internal/runbooks/{ti.dag_id}"
    ))
```

It is set in `default_args`, so it covers every task — and only fires after
retries are exhausted, so a transient blip never pages.

Reference: `challenges/v1/03-airflow-orchestration/solution/dags/callbacks.py`.


## Answer 3: Solution

The SLA-miss callback is P2 (notify, no page); the retry callback is P3
(ticket only).

```python
def on_sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    missed = ", ".join(t.task_id for t in task_list) or "(none)"
    send_alert(text=(
        f"*SLA miss on {dag.dag_id}*\n*Tasks past SLA:* {missed}\n"
        f"Check the run and warn downstream consumers if the 07:30 UK mart "
        f"is at risk.\n*Runbook:* https://wiki.internal/runbooks/{dag.dag_id}"
    ))


def on_retry_callback(context):
    ti = context["task_instance"]
    open_ticket(
        summary=f"Retry: {ti.dag_id}.{ti.task_id} (attempt {ti.try_number})",
        detail={"task_id": ti.task_id, "log_url": ti.log_url},
    )
```

Severity drives channel: down → page, slow → notify, flaky → ticket.

Reference: `challenges/v1/03-airflow-orchestration/solution/dags/callbacks.py`.


## Answer 4: Solution

Each callback is attached at its correct scope; the SLA is a timedelta on the
publish task.

```python
from callbacks import (
    on_failure_callback, on_retry_callback,
    on_sla_miss_callback, on_success_callback,
)

default_args = {
    ...
    "on_failure_callback": on_failure_callback,   # every task
    "on_retry_callback": on_retry_callback,        # every task
}

with DAG(
    ...
    sla_miss_callback=on_sla_miss_callback,        # DAG-level
) as dag:
    publish_to_catalog = PythonOperator(
        task_id="publish_to_catalog",
        python_callable=_publish_to_catalog,       # logs a publish message
        sla=timedelta(minutes=90),                 # times the whole run
        on_success_callback=on_success_callback,   # final task only
    )
```

Scope is the whole lesson: failure/retry are per-task defaults, SLA-miss is
DAG-level, success is final-task-only.

Reference: `challenges/v1/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py`.


## Answer 5: Solution

The freshness contract lives in `sources.yml`; `error_after` is the threshold
that actually blocks the DAG.

```yaml
sources:
  - name: custodian
    config:
      loaded_at_field: _extracted_at
      freshness:
        warn_after:  {count: 4, period: hour}
        error_after: {count: 6, period: hour}
    tables:
      - name: holdings_raw
      - name: positions_raw
```

A 5-hour-old feed warns but exits zero (pipeline runs); a 7-hour-old feed
errors and the freshness gate fails. Tightening `error_after` blocks
sooner at the cost of false alarms — that trade-off is the decision the
threshold encodes.

Reference: `challenges/v1/03-airflow-orchestration/solution/dbt/models/sources.yml`
and the `source_freshness_check` task in
`challenges/v1/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py`.


## Answer 6: Solution

Six panels; the sixth is the volume-anomaly panel that catches a
fresh-but-short feed. Channels are datadog / teams / ticket only.

```yaml
  - name: "Source volume anomaly"
    metric: >
      landed row count on the current load date for holdings_raw, vs the
      trailing 7-day average for the same weekday.
    alert_condition: >
      fire when today's rows are below 80% of the trailing-7-day average —
      a likely partial / truncated extract.
    alert_channel: "datadog, teams"
```

Freshness watches the clock; this watches the volume. Firing here lets the
on-call hold publication before exposure is understated, rather than
diagnosing a completeness-test failure after the fact.

Reference: `challenges/v1/03-airflow-orchestration/solution/include/monitoring/portfolio_analytics.yml`.


## Answer 7: Solution

The runbook's common-alerts table is the page an on-call engineer reads at
03:00 — each row is symptom → numbered diagnosis → remediation, and the
escalation path is Datadog auto-alert + xMatters page + Microsoft Teams. The
consumer guide documents all three marts with runnable sample queries and the
07:30 UK freshness SLA.

The five alert rows are: source-freshness error, dbt build failure, dbt test
failure, SLA miss, and the fresh-but-truncated feed (the failure mode freshness
alone misses). All channels are Datadog / xMatters / Microsoft Teams / ticket
— no Slack, no PagerDuty.

Reference: `challenges/v1/03-airflow-orchestration/solution/include/runbooks/portfolio_analytics.md`
and `challenges/v1/03-airflow-orchestration/solution/include/launch/consumer-guide.md`.


## Answer 8: Solution

The suite parses the DAG files and asserts the callback/SLA wiring and the
absence of secrets — all without airflow or a warehouse.

```python
def test_no_secret_literals_in_dag_files():
    leak = re.compile(r"dapi[0-9a-f]{16,}|cloud\.databricks\.com|adb-\d+\.\d+\.")
    for py in DAGS_DIR.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert not leak.search(text), f"possible secret literal in {py.name}"
```

The parse test, the callback/SLA test, and the secret test together catch the
breakage that eyeballing the DAG misses — an unwired callback, a missing SLA, a
pasted token.

Reference: `challenges/v1/03-airflow-orchestration/solution/tests/test_dag_structure.py`.


## Answer 9: Solution

The same pipeline, dbt-inside-Databricks. Each step is a notebook submission;
the run is one Databricks Job per task rather than a Cosmos task per model.

```python
run_dbt_models = DatabricksSubmitRunOperator(
    task_id="run_dbt_models",
    databricks_conn_id="databricks_default",
    json={
        "run_name": "portfolio_analytics_dbt_build",
        "existing_cluster_id": DATABRICKS_EXISTING_CLUSTER_ID,
        "notebook_task": {
            "notebook_path": f"{DBT_NOTEBOOK_BASE}/run_dbt_models",
        },
    },
    polling_period_seconds=60,
    timeout_seconds=3600,
    sla=timedelta(minutes=60),
)

check_source_freshness >> run_dbt_models >> test_dbt_models >> generate_dbt_docs
```

It reuses two of the Phase 2 callbacks — `on_failure_callback` (P1) and
`on_sla_miss_callback` (P2) — so those tiers behave identically to the Cosmos DAG
while only the execution surface changes. P3 (`on_retry_callback`) and the
success signal are absent here, which is worth noticing before copying this
shape into a real pipeline that sets `retries`.

Reference: `challenges/v1/03-airflow-orchestration/solution/dags/databricks_submit_run_dag.py`.


## Answer 10: Solution

The capstone is not new code — it is the composition. `portfolio_analytics_daily`
already carries every checklist item: the timezone-aware weekday schedule, the
freshness gate first, the Cosmos group, retries with backoff, the three
callback tiers at their correct scopes, the 90-minute SLA with the success
ping, and the runbook / consumer / monitoring docs alongside.

```bash
pytest data_products/portfolio_analytics/tests/ -q
mise run challenge:verify 03
```

Passing structural tests plus a green wiring gate is a complete, operable,
Slack-free production DAG on Databricks.

Reference: `challenges/v1/03-airflow-orchestration/solution/dags/portfolio_analytics_daily.py`,
with `challenges/v1/03-airflow-orchestration/solution/dags/callbacks.py`,
`challenges/v1/03-airflow-orchestration/solution/include/`, and
`challenges/v1/03-airflow-orchestration/solution/tests/test_dag_structure.py`.

