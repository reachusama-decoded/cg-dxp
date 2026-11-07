---
phase: "7 - Operate"
artifact: "Runbook"
data_product: "[Data Product Name]"
version: "1.0"
owner: "[DataOps Team / Name]"
last_reviewed: "YYYY-MM-DD"
---

# Runbook — [Data Product Name]

Operational procedures for DataOps to run, monitor, and recover this data
product in steady-state. This document is a living reference — update it when
procedures change, incidents reveal gaps, or the pipeline evolves.

---

## Product Overview

| Field | Detail |
|-------|--------|
| Product name | |
| Domain | |
| Data Owner | |
| DataOps primary contact | |
| Dev team escalation contact | |
| SLA tier | *(Mission-Critical / Business-Critical / Standard / Low)* |
| Data sensitivity | *(Public / General / Restricted / Highly Restricted)* |
| Catalog entry | *(link)* |
| Data contract | *(link)* |

---

## Schedule and Normal Operations

| Field | Detail |
|-------|--------|
| Pipeline trigger | *(cron schedule, event-driven, manual)* |
| Expected run window | *(e.g., completes by 06:00 UTC daily)* |
| Typical run duration | |
| Orchestration tool | *(e.g., Airflow DAG name, dbt job ID)* |
| Pipeline location | *(repo path or link)* |

### Starting / Stopping the Pipeline

```
# How to trigger a manual run:

# How to pause/disable the schedule:

# How to re-enable the schedule:
```

---

## Health Checks

Run these checks to confirm the pipeline is operating normally.

| Check | How to verify | Expected result |
|-------|--------------|-----------------|
| Last successful run | | |
| Row count within expected range | | |
| Freshness SLA met | | |
| No open critical alerts | | |
| Consumer queries returning results | | |

---

## Alerts and Responses

| Alert | Meaning | First response |
|-------|---------|----------------|
| Pipeline run failed | Last execution did not complete | Check logs → see [Pipeline Failure](#pipeline-failure) |
| Freshness SLA breached | Data is older than the contracted threshold | Check logs → notify consumers if > [X] minutes late |
| Row count anomaly | Output volume outside tolerance band | Validate source → compare to prior run |
| Data quality test failure | DQ rule in the contract is violated | Do not promote to consumers → investigate → escalate if unresolved in [X] hours |
| Source unavailable | Upstream dependency is unreachable | Wait [X] minutes and retry → escalate to source team if unresolved |

---

## Runbook Procedures

### Pipeline Failure

1. Check the orchestration logs for the failed task.
2. Identify the failure type: source error, transformation error, or output error.
3. If transient (connectivity, timeout): retry the run.
4. If data error: do not retry until root cause is identified. Escalate if unresolved within [X] hours.
5. Log the incident in `incident-log.md`.
6. Notify consumers if SLA is at risk.

### Data Quality Failure

1. Identify which DQ rule failed (check test output or monitoring dashboard).
2. Determine if the failure is in the source or in the transformation.
3. Do not promote bad data downstream.
4. Engage the Data Owner to assess impact.
5. Escalate to the dev team if the fix requires a code change.

### Backfill / Reprocessing

1. Confirm the backfill window with the Data Owner.
2. Disable the scheduled run if needed to avoid conflicts.
3. Trigger the backfill job: `[command or DAG run instruction]`
4. Verify output row counts and DQ tests after completion.
5. Re-enable the scheduled run.
6. Notify consumers of the reprocessed data.

### Consumer Access Issue

1. Verify the consumer's permissions against the access control matrix in the data contract.
2. If access should exist: check for permission drift and remediate.
3. If access was never granted: route through the standard access request process.
4. Log the request and resolution in the consumer feedback log.

---

## Escalation Paths

| Scenario | Escalate to | SLA for escalation |
|----------|-------------|-------------------|
| Pipeline down > [X] hours | Dev team lead | Immediately |
| S1/S2 data quality incident | Data Owner + Dev team lead | Within [X] hours |
| Source team unresponsive | Data Domain Lead | Within [X] hours |
| Security or access concern | InfoSec | Immediately |

---

## Maintenance

| Task | Frequency | Owner | Notes |
|------|-----------|-------|-------|
| Review alert thresholds | Quarterly | DataOps | Adjust if false-positive rate is high |
| Confirm consumer list is current | Quarterly | Data Owner | Check against catalog entry |
| Rotate credentials / service accounts | Per org policy | InfoSec | |
| Review and update this runbook | After each significant incident | DataOps | |

---

## Change Log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | | | Initial runbook created |
