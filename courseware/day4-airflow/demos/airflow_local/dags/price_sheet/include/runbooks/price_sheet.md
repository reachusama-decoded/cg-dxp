# Runbook: price_sheet_daily

## 1. Service overview

| Field | Value |
|---|---|
| DAG ID | `price_sheet_daily` |
| Schedule | `0 6 * * 1-5` (06:00 UK, Monday to Friday) |
| SLA | Price sheet published by 07:30 UK on weekdays |
| Owner | Pricing data team |
| On-call | `price-sheet-oncall` rotation (xMatters) |

## 2. Architecture

- **Sources:** `vendor_feed.vendor_prices_raw` (by 02:00 UK) and `fx_feed.fx_rates_raw` (by 03:00 UK).
- **Models:** `stg_prices`, `stg_fx_rates`, then `int_prices_usd`, then `fct_prices_usd` and `agg_prices_by_ccy`.
- **DAG:** `start → source_freshness_check → dbt_pipeline (Cosmos) → publish_to_catalog → end`.
- **Alerts:** P1 a Datadog event on task failure (support pages the on-call through xMatters), P2 Microsoft Teams
  on failure and on an SLA miss, P3 a ticket on a retry.

## 3. Common alerts and responses

### Alert 1: Source freshness error

| Field | Details |
|---|---|
| Task | `source_freshness_check` |
| Symptom | Datadog alert and a Teams message naming the task. The log shows `dbt source freshness` failing: the vendor feed is past its `error_after` (6h). |
| Diagnosis | Open the task log from the alert. Run `select max(vendor_ts) from vendor_prices_raw` to confirm the last delivery. |
| Remediation | Feed arrived late: clear `source_freshness_check` in the UI with "Include Downstream". Feed missing: escalate to the vendor desk. |

### Alert 2: dbt build failure

| Field | Details |
|---|---|
| Task | a model task in `dbt_pipeline`, for example `dbt_pipeline.int_prices_usd_run` |
| Symptom | Datadog alert and a Teams message naming the model task. Tasks after it show `upstream_failed`. |
| Diagnosis | Expand `dbt_pipeline` in the Graph view, open the first red task's log, read the dbt error. |
| Remediation | Fix the model, deploy, then clear the failed task with "Include Downstream". |

### Alert 3: dbt test failure

| Field | Details |
|---|---|
| Task | `dbt_pipeline.dbt_test` |
| Symptom | Datadog alert and a Teams message naming the test task. |
| Diagnosis | Open the log; read which test failed and how many rows broke the rule. |
| Remediation | Hold publication: a failed test must not ship wrong prices. Fix the data or the model, then clear from the test task down. |

### Alert 4: SLA miss

| Field | Details |
|---|---|
| Task | `publish_to_catalog` (`sla=90min`) |
| Symptom | A Datadog warning and a Teams message "SLA miss on price_sheet_daily". No page: the DAG is slow, not down. |
| Diagnosis | Open the run; find the task still running and how long it has taken. |
| Remediation | Tell consumers the price sheet will be late, and by how much. |

### Alert 5: Short feed (passes freshness, fails completeness)

| Field | Details |
|---|---|
| Task | `dbt_pipeline.dbt_test`; the cause is upstream |
| Symptom | The feed arrived on time but with a fraction of the usual rows. Freshness passes; the volume panel fires. |
| Diagnosis | Compare today's row count in `vendor_prices_raw` with the trailing 7-day average. |
| Remediation | Hold publication, ask the vendor for a full re-delivery, then clear from the freshness gate down. |

## 4. Manual procedures

- **Trigger a run:** in the Airflow UI, unpause `price_sheet_daily` and click Trigger.
- **Clear and re-run:** open the failed run's Graph view, click the failed task, Clear, tick "Include Downstream", Confirm.
