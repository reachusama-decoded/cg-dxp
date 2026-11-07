# Portfolio Analytics Airflow — reference solution

The complete worked orchestration for Challenge 03: an Airflow DAG that drives the
portfolio-analytics dbt project on **Databricks** via Cosmos, with a source-freshness
gate, tiered Slack-free alerting, an SLA, a runbook, and a consumer guide.

The trainee-facing guide — concepts, step-by-step, and the collapsible worked solutions —
is the challenge README: [`../README.md`](../README.md). This folder is the **reference
build**: every DAG, callback, and operational doc is complete here. The stub under
`../stubs/` (mirrored into `data_products/portfolio_analytics/`, which is what astro runs)
is the same project with the DAG wiring left as a `# TODO`. The dbt project is complete in
both — this lab is about orchestration, not authoring the models.

## What is here

```
dags/
  portfolio_analytics_daily.py       # the Cosmos DbtTaskGroup DAG (primary)
  databricks_submit_run_dag.py       # the paved-path DatabricksSubmitRunOperator variant
  callbacks.py                       # tiered alerting: Datadog + xMatters (P1) / Teams (P2) / ticket (P3)
include/
  alerting/notifications.py          # the vendor-neutral send_alert transport
  runbooks/portfolio_analytics.md    # the on-call runbook
  launch/consumer-guide.md           # the consumer onboarding doc
  monitoring/portfolio_analytics.yml # the monitoring panel config
dbt/                                 # the portfolio-analytics dbt project the DAG runs
tests/test_dag_structure.py          # structural DAG checks (files present, stub is stubbed, no secrets)
```

(`check-dag-load.sh` and `verify-with-databricks.sh` are legacy preflight scripts,
superseded by `mise run challenge:verify 03` / `mise run challenge:dbt 03`.)

## Run it (from the repo root, inside the devcontainer)

```bash
mise run setup:databricks            # first time only: browser OAuth login; also starts the
                                     # OAuth -> Airflow token refresher the DAG's auth needs
mise run challenge:seed 02           # provision the four raw feeds into your training schema
astro dev start                      # boot local Airflow
astro dev run dags unpause portfolio_analytics_daily
astro dev run dags trigger portfolio_analytics_daily
```

Airflow runs inside the astro containers, so Airflow CLI commands go through
`astro dev run …` (not a bare `airflow …`).

## Verify

```bash
mise run challenge:verify 03         # static wiring gate — GREEN once the DAG is wired
# after a green DAG run, preview the marts the pipeline landed:
mise run challenge:dbt 03 -- show --select fct_portfolio_returns --limit 5
```

## What the challenges cover

Both phases are sections of [`../README.md`](../README.md):

- **Phase 1 — Orchestrate the dbt pipeline with Airflow + Cosmos** (freshness gate, Cosmos
  `DbtTaskGroup`, dependency chain, schedule, retries, first full run).
- **Phase 2 — Production operations** (alerting transport, tiered callbacks, SLA, the
  freshness contract, monitoring config, runbook + consumer guide, structural tests, the
  paved-path `DatabricksSubmitRunOperator` variant, and the capstone).
