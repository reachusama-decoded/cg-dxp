# Runbook: portfolio_analytics_daily

This runbook illustrates the native platform workflow. Assigned v2 uses a staged `<prefix>_portfolio_daily` Python DAG, a two-minute practice schedule and a final evidence task; see [shared setup](../../../../challenges/v2/runtime/portfolio/SETUP.md). The production-style schedule, contacts and callback integrations below are reference, not proof of a deployed service.

## 1. Service Overview

| Field | Value |
|-------|-------|
| DAG ID | `portfolio_analytics_daily` |
| Schedule | `0 6 * * 1-5` (06:00 UK, Mon–Fri) |
| SLA | Mart published by 07:30 UK on weekdays |
| Owner | Portfolio Analytics Team |
| On-call | `portfolio-analytics-oncall` rotation (xMatters) |
| Repository | `github.com/<org>/portfolio-analytics-pipeline` |
| Description | Orchestrates the portfolio-analytics dbt project on Databricks: four raw sources → staging → intermediate → the `fct_portfolio_returns` and `agg_fund_exposure` marts, then tests, then publish. |

## 2. Architecture

**Sources** (raw Delta tables, read via dbt `source()`):

| Source | Tables | Expected delivery |
|--------|--------|-------------------|
| `custodian` | `holdings_raw`, `positions_raw` | by 02:00 UK |
| `bloomberg` | `prices_raw`, `refdata_raw` | by 03:00 UK |
| `fx_feed` | `fx_rates_raw` | by 03:00 UK |
| `product_ref` | `fund_master_raw` | reference; slow-changing |

**Transformation** — the portfolio-analytics dbt project on Databricks:

- staging: `stg_holdings`, `stg_positions`, `stg_prices`, `stg_fx_rates`, `stg_funds`
- intermediate: `int_holdings_enriched`, `int_positions_dated`, `int_fund_attributes`
- marts: `fct_portfolio_returns` (daily-grain fact), `agg_fund_exposure` (per fund/date/strategy exposure)

**Orchestration** — the Airflow DAG `portfolio_analytics_daily`:

- `start → source_freshness_check → dbt_pipeline (Cosmos DbtTaskGroup) → publish_to_catalog → end`
- Alert design: automatic events go to Datadog. Support routes P1 to xMatters, P2 to Teams and P3 to a ticket. Missing callback credentials leave log-only observations, as listed below.

**Serving** — the marts are read by RM dashboards, compliance concentration checks, and the client reporting pipeline.

## 3. Access and Credentials

| System | Access | Location |
|--------|--------|----------|
| Airflow UI | SSO | Astronomer deployment `portfolio-analytics` |
| Databricks workspace | SSO | the team's Databricks SQL warehouse |
| Logs | Airflow UI | task instance → Logs tab |
| dbt docs | served site | `dbt docs serve` (port 8080) |

**Credential locations:**

- Databricks: Airflow Connection `databricks_default` (host + SQL-warehouse `http_path` in extras + OAuth M2M service-principal creds; DBX-SEC-002, PAT forbidden in prod). No token in any DAG or dbt file.
- Microsoft Teams webhook: Airflow Connection `alert_webhook` (conn-type http).
- Datadog: `DD_API_KEY` env var on the deployment (unset → the callback logs instead of emitting the event).
- Ticket webhook: `TICKET_WEBHOOK_URL` env var (unset → the callback logs instead of opening a ticket).

## 4. Common Alerts and Responses

### Alert 1: Source freshness error

| Field | Details |
|-------|---------|
| Task | `source_freshness_check` |
| Symptom | Datadog alert (xMatters page) + Teams message "DAG failure … source_freshness_check". The task log shows `dbt source freshness` exit 1 with the custodian source past its `error_after` (6h) threshold. |
| Diagnosis | 1. Open the task log from the alert link. 2. Read which source breached. 3. In Databricks, `select max(_extracted_at) from <catalog>.<schema>.holdings_raw` to confirm the last load. 4. Check whether the custodian SFTP drop ran. |
| Remediation | If the feed arrives late: clear `source_freshness_check` in the UI to re-run; the chain resumes. If the feed is missing: escalate to custodian ops; log the incident. |

### Alert 2: dbt build failure

| Field | Details |
|-------|---------|
| Task | a model task inside `dbt_pipeline` (e.g. `dbt_pipeline.int_holdings_enriched_run`) |
| Symptom | Datadog alert (xMatters page) + Teams message naming the failed model task. Downstream model tasks show `upstream_failed`. |
| Diagnosis | 1. Expand the `dbt_pipeline` group in the Graph view; find the first red task. 2. Open its log; read the dbt error (compilation vs database). 3. If a database error: check the Databricks SQL warehouse is running. |
| Remediation | If a SQL/model error: review and release the model fix through the approved process, then clear the named failed task with "Include Downstream". If the warehouse is down: restart it, then clear the task. Transient timeouts auto-retry (retries=2, exponential backoff). |

### Alert 3: dbt test failure

| Field | Details |
|-------|---------|
| Task | a test task inside `dbt_pipeline` (e.g. the historical fixture comparison `assert_nav_within_tolerance`) |
| Symptom | Datadog alert (xMatters page) + Teams message naming the failed test task. |
| Diagnosis | 1. Open the test task log; read which test failed and the failing-row count. 2. For that historical comparison, query `fct_portfolio_returns.calc_nav_per_unit` against `seed_custodian_nav.nav_per_unit` to inspect fixture drift. The compatible calculated field is holdings-only GBP exposure divided by 100 million synthetic units, cash excluded; the comparison does not verify official NAV, actual outstanding shares or share-class accounting. 3. Decide: source-data issue (upstream) or transformation logic (our code). |
| Remediation | Hold publication — a failed test must not ship wrong numbers. If source data: notify the data owner; log the incident. If logic: fix the model/test, deploy, clear from the test gate down. |

### Alert 4: SLA miss

| Field | Details |
|-------|---------|
| Task | `publish_to_catalog` (`sla=90min`) |
| Symptom | Datadog warning + Teams message "SLA miss on portfolio_analytics_daily" (no page — the DAG is slow, not down). |
| Diagnosis | 1. Open the DAG run; find the task still running and its duration. 2. Check Databricks warehouse load / queueing. 3. Check scheduler/worker capacity. |
| Remediation | If a query is slow: consider scaling the SQL warehouse temporarily. If an upstream feed was late: warn downstream consumers of the expected delay. |

### Alert 5: Partial / truncated source feed (passes freshness, fails completeness)

| Field | Details |
|-------|---------|
| Task | a `dbt_pipeline` test task (failure surfaces here; root cause is upstream) |
| Symptom | A completeness test fails while `source_freshness_check` and the build both PASSED — the feed was on time but short (a fraction of the usual row count). Freshness watches the clock, not the volume. |
| Diagnosis | 1. Confirm the failing tests are completeness checks, not value checks. 2. Compare today's landed `holdings_raw` row count to the trailing 7-day average. 3. A partial extract is typically a fraction of normal volume with a current timestamp. |
| Remediation | Hold publication. Confirm the truncated extract with custodian ops and request a full re-delivery. When it lands, clear from the test gate down. Notify downstream consumers. Follow-up: add a row-count / volume-anomaly monitor (see the monitoring config) so a short feed is caught at ingestion, not at the test gate. |

## 5. Escalation Matrix

| Level | Contact | When |
|-------|---------|------|
| Primary on-call | current on-call (xMatters) | first responder for all P1 pages; resolve within 30 min |
| Secondary on-call | senior data engineer on rotation | primary cannot resolve in 30 min, or infra change needed |
| Team lead | Portfolio Analytics Team Lead | SLA at risk, or cross-team coordination needed |

## 6. Manual Procedures

### Trigger a run

In the Airflow UI, find `portfolio_analytics_daily`, unpause it, and click Trigger.

### Clear a failed task and re-run

Open the failed run's Graph view, click the failed task → Clear → check "Include Downstream" → Confirm. Airflow re-queues that task and everything after it.

### Full rebuild

Clear `source_freshness_check` with "Include Downstream" to re-run the whole chain, or run `dbt build` directly against the project for an out-of-band rebuild.

## 7. Contacts

| Role | Channel |
|------|---------|
| Pipeline owner | Microsoft Teams `portfolio-analytics` |
| On-call rotation | xMatters `portfolio-analytics-oncall` |
| Custodian ops | custodian operations team |
| Databricks admin | platform engineering |
| Downstream consumers | portfolio managers, reporting |
