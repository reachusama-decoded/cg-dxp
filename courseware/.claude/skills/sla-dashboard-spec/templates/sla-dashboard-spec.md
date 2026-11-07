# SLA Dashboard Specification

```yaml
Phase:          7 - Operate
Artifact:       SLA Dashboard Specification (Optional)
Data Product:   [Product Name]
Date:           [YYYY-MM-DD]
```

> **When to use:** This template captures the requirements for an operational dashboard that surfaces SLA health and cost metrics for a data product.

## Dashboard Overview

| Field              | Detail                                                |
|--------------------|-------------------------------------------------------|
| Dashboard Name     | [e.g., Product Name — SLA & Health Dashboard]         |
| Target Audience    | [e.g., DataOps, Product Owner, Consumers, Leadership] |
| Refresh Frequency  | [e.g., Every 15 minutes, Hourly, Daily]               |
| Data Sources       | [List source systems feeding the dashboard]           |

## Metrics to Display

| Metric           | Definition                                                    | Target / Threshold | Display Type          |
|------------------|---------------------------------------------------------------|--------------------|-----------------------|
| Freshness        | Time since last successful data refresh                       | [e.g., < 2 hours] | [e.g., gauge, trend]  |
| Completeness     | Percentage of expected records or fields present              | [e.g., >= 99.5%]  | [e.g., percentage bar]|
| Availability     | Uptime of the data product endpoint or storage layer          | [e.g., 99.9%]     | [e.g., gauge, trend]  |
| Quality Score    | Composite score from data quality checks                      | [e.g., >= 95]     | [e.g., scorecard]     |
| Cost             | Compute and storage cost for the current period               | [e.g., < $X/mo]   | [e.g., trend, table]  |
| Incident Count   | Open and recent incidents by severity                         | [informational]    | [e.g., table, count]  |

## Alert Thresholds & Notifications

| Alert Condition                     | Severity | Notification Channel              | Recipients         |
|-------------------------------------|----------|-----------------------------------|---------------------|
| Freshness exceeds SLA threshold     | High     | [e.g., email, chat, pager]        | [Team / Role]       |
| Completeness drops below target     | High     | [e.g., email, chat, pager]        | [Team / Role]       |
| Availability below target           | Critical | [e.g., pager]                     | [Team / Role]       |
| Quality score below threshold       | Medium   | [e.g., email, chat]               | [Team / Role]       |
| Cost exceeds budget threshold       | Medium   | [e.g., email]                     | [Team / Role]       |

## Access Controls

| Audience             | Access Level              | Notes                       |
|----------------------|---------------------------|-----------------------------|
| DataOps Team         | Full (edit + configure)   |                             |
| Product Owner        | View                      |                             |
| Consumers            | View (filtered)           | [Scope of visible metrics]  |
| Leadership           | View (summary only)       |                             |

## Layout & Sections

> Describe the logical sections of the dashboard. Adapt to your organization's dashboarding platform.

| Section              | Contents                                           | Position       |
|----------------------|----------------------------------------------------|----------------|
| Health Summary       | Freshness, completeness, availability gauges       | Top            |
| Quality Detail       | Quality score trend, failing checks breakdown      | Middle         |
| Cost Overview        | Period-over-period cost trend, cost by component   | Middle         |
| Incident Tracker     | Open incidents, recent resolutions                 | Bottom         |
| SLA Trend            | Historical SLA compliance over time                | Bottom         |
