---
phase: "02-Design"
artifact: "Non-Functional Requirements Specification"
data_product: "[Product Name]"
date: "YYYY-MM-DD"
---

# Non-Functional Requirements Specification

> **When is this needed?** This artifact is optional and intended for complex or high-criticality
> data products. Standard platform NFRs apply by default to all products. Document only
> product-specific deviations or additions here.

---

## 1. Overview

| Field | Value |
|-------|-------|
| Product Name | [Product name] |
| Classification | Sensitivity: [e.g., General / Restricted] |
|                | Criticality: [e.g., Medium / High / Critical] |
| Justification for NFR Spec | [Why this product requires NFRs beyond platform defaults] |

---

## 2. Performance Targets

| Metric | Platform Default | This Product's Requirement | Justification |
|--------|-----------------|---------------------------|---------------|
| Query latency (p95) | [e.g., < 30s] | [e.g., < 5s for dashboard queries] | [e.g., Executive dashboard with real-time refresh] |
| Transformation runtime | [e.g., < 2 hours] | [e.g., < 30 minutes] | [e.g., Tight freshness SLA for downstream consumer] |
| Concurrent query support | [e.g., 10 concurrent] | [e.g., 50 concurrent] | [e.g., Serves 12 consumer teams] |
| Data volume per run | N/A | [e.g., ~500M rows processed per run] | [Baseline for capacity planning] |
| | | | |

---

## 3. Scalability

| Dimension | Current State | 12-Month Projection | Scaling Strategy |
|-----------|--------------|---------------------|------------------|
| Row volume | [e.g., 100M rows] | [e.g., 500M rows] | [e.g., Partition pruning, incremental processing] |
| Source count | [e.g., 2 sources] | [e.g., 5 sources] | [e.g., Modular ingestion, parameterized connectors] |
| Consumer count | [e.g., 3 consumers] | [e.g., 15 consumers] | [e.g., Serving layer auto-scaling, query routing] |
| Storage footprint | [e.g., 50 GB] | [e.g., 250 GB] | [e.g., Lifecycle policies, cold storage tiering] |
| | | | |

### Scaling Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| [e.g., Query latency exceeds target] | [e.g., p95 > 10s for 3 consecutive days] | [e.g., Increase warehouse size, add clustering] |
| [e.g., Transformation runtime exceeds window] | [e.g., > 80% of available window] | [e.g., Optimize models, increase compute] |
| | | |

---

## 4. Reliability & Availability

| Metric | Platform Default | This Product's Requirement |
|--------|-----------------|---------------------------|
| Monthly availability | [e.g., 99.5%] | [e.g., 99.9%] |
| Recovery Time Objective (RTO) | [e.g., 4 hours] | [e.g., 1 hour] |
| Recovery Point Objective (RPO) | [e.g., 24 hours] | [e.g., 1 hour] |
| Planned maintenance window | [e.g., Weekends] | [e.g., Restricted — consumers operate 24/7] |

### Redundancy & Failover

| Component | Redundancy Strategy | Failover Method |
|-----------|-------------------|-----------------|
| [e.g., Serving layer] | [e.g., Multi-region replica] | [e.g., Automatic DNS failover] |
| [e.g., Transformation compute] | [e.g., Fallback warehouse] | [e.g., Manual failover via orchestrator config] |
| | | |

---

## 5. Observability Requirements

> Document observability needs beyond standard platform monitoring.

| Signal | Metric | Alert Threshold | Alert Channel |
|--------|--------|-----------------|---------------|
| Freshness | Time since last successful delivery | > [X] minutes/hours | [e.g., PagerDuty, on-call channel] |
| Volume anomaly | Row count deviation from 7-day average | > [X]% deviation | [e.g., Team notification channel] |
| Query performance | p95 query latency | > [X] seconds | [e.g., Dashboard owner notification] |
| Error rate | Failed quality checks per run | > [X] failures | [e.g., On-call engineer] |
| Cost | Daily compute cost | > [X]% above baseline | [e.g., Team lead notification] |
| | | | |

### Dashboards & Reporting

| Dashboard | Purpose | Audience | Refresh Cadence |
|-----------|---------|----------|-----------------|
| [e.g., Product health dashboard] | [Monitor SLA compliance, freshness, quality] | [Data product team] | [e.g., Real-time / hourly] |
| [e.g., Cost tracking dashboard] | [Monitor compute and storage costs] | [Team lead, finance] | [e.g., Daily] |
| | | | |

---

## 6. Cost Constraints

| Cost Category | Monthly Budget | Current Estimate | Notes |
|---------------|---------------|------------------|-------|
| Compute (transformation) | [e.g., $X/month] | [e.g., $X/month] | [Scaling assumptions] |
| Compute (serving/queries) | [e.g., $X/month] | [e.g., $X/month] | [Based on projected query volume] |
| Storage | [e.g., $X/month] | [e.g., $X/month] | [Including retention policy] |
| Data transfer / egress | [e.g., $X/month] | [e.g., $X/month] | [Cross-region or cross-cloud] |
| **Total** | **$X/month** | **$X/month** | |

### Cost Optimization Levers

- [e.g., Move historical data to cold storage after 90 days]
- [e.g., Reduce warehouse size during off-peak hours]
- [e.g., Convert full-refresh models to incremental where feasible]

---

## 7. Compliance & Auditability

| Requirement | Details |
|-------------|---------|
| Regulatory Framework(s) | [e.g., GDPR, CCPA, SOX, HIPAA — list applicable regulations] |
| Data Retention | [Minimum and maximum retention periods per regulation] |
| Right to Deletion | [How deletion requests are handled across the pipeline] |
| Audit Trail | [What actions are logged: access, modifications, deletions] |
| Audit Log Retention | [How long audit logs are retained] |
| Access Reviews | [Cadence: e.g., Quarterly access certification] |
| Data Lineage | [How end-to-end lineage is tracked and made available for audit] |

---

## Appendix: Revision History

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | | | Initial draft |
| | | | |
