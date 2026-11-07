---
phase: "Intake & Discovery"
artifact: "Consumer Use Case Map"
data_product: "[Product Name]"
date_created: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
---

# Consumer Use Case Map

Maps each known consumer to their use cases, consumption patterns, and SLA
expectations. This artifact drives requirements and informs design decisions.

---

## Consumer Summary

| #  | Consumer / Team     | Primary Use Case           | Access Pattern          | Freshness Need | Priority |
|----|---------------------|----------------------------|-------------------------|----------------|----------|
| 1  |                     |                            |                         |                |          |
| 2  |                     |                            |                         |                |          |
| 3  |                     |                            |                         |                |          |

---

## Detailed Use Cases

### UC-1: [Use Case Name]

| Field                | Details                        |
|----------------------|--------------------------------|
| Consumer / Team      |                                |
| Description          |                                |
| Access Pattern       | _e.g., SQL query, API call, file export, dashboard, event stream_ |
| Freshness            | _e.g., real-time, hourly, daily, weekly_ |
| Completeness         | _e.g., must include all records, tolerates partial loads_ |
| Expected Volume      | _e.g., rows per day, GB per refresh_ |
| Latency Tolerance    | _e.g., < 5s query response, < 1hr from source change_ |
| Downstream Dependencies | _Systems or processes that depend on this consumer's output_ |
| SLA Expectations     | _Availability, support hours, incident response_ |
| Sensitivity / Criticality | _Classification of data as consumed_ |

**Notes:**

<!-- Any additional context, edge cases, or seasonal variations. -->

---

### UC-2: [Use Case Name]

| Field                | Details                        |
|----------------------|--------------------------------|
| Consumer / Team      |                                |
| Description          |                                |
| Access Pattern       |                                |
| Freshness            |                                |
| Completeness         |                                |
| Expected Volume      |                                |
| Latency Tolerance    |                                |
| Downstream Dependencies |                             |
| SLA Expectations     |                                |
| Sensitivity / Criticality |                            |

**Notes:**

---

_Copy the use case block above for each additional consumer use case._

---

## Overlapping Needs

Identify patterns shared across consumers to guide design toward reuse.

| Need / Pattern              | Consumers Sharing It         | Design Implication           |
|-----------------------------|------------------------------|------------------------------|
|                             |                              |                              |
|                             |                              |                              |

## Open Questions

| #  | Question                                        | Owner          | Status   |
|----|-------------------------------------------------|----------------|----------|
| 1  |                                                 |                |          |
| 2  |                                                 |                |          |
