---
phase: "02-Design"
artifact: "Transformation Specification"
data_product: "[Product Name]"
date: "YYYY-MM-DD"
---

# Transformation Specification

---

## 1. Overview

| Field | Value |
|-------|-------|
| Product Name | [Product name] |
| Transformation Framework | [e.g., dbt, Spark, SQL scripts] |
| Target Platform | [e.g., Cloud data warehouse, lakehouse] |
| Repository / Project | [Location of transformation code] |
| Classification | Sensitivity: [e.g., General / Restricted] |
|                | Criticality: [e.g., Medium / High] |

---

## 2. Model Map

| Model Name | Layer | Materialization | Description |
|------------|-------|----------------|-------------|
| `stg_source_a__entities` | Staging | View | Clean and rename columns from source A |
| `stg_source_b__events` | Staging | View | Clean and rename columns from source B |
| `int_entities_with_events` | Intermediate | Ephemeral / View | Join entities with their events |
| `fct_entity_events` | Mart | Incremental | Fact table of entity events at event grain |
| `dim_entities` | Mart | Table | Dimension table of entity attributes |
| | | | |

---

## 3. Model Details

### 3.1 `stg_source_a__entities`

| Field | Value |
|-------|-------|
| Purpose | Standardize column names, types, and apply basic cleaning to source A entity data |
| Source Model(s) | `raw.source_a.entities` |
| Materialization | View |
| Incremental Strategy | N/A |

---

### 3.2 `stg_source_b__events`

| Field | Value |
|-------|-------|
| Purpose | [Description] |
| Source Model(s) | `raw.source_b.events` |
| Materialization | View |
| Incremental Strategy | N/A |

---

### 3.3 `int_entities_with_events`

| Field | Value |
|-------|-------|
| Purpose | [Description] |
| Source Model(s) | `stg_source_a__entities`, `stg_source_b__events` |
| Materialization | Ephemeral / View |
| Incremental Strategy | N/A |

---

### 3.4 `fct_entity_events`

| Field | Value |
|-------|-------|
| Purpose | [Description] |
| Source Model(s) | `int_entities_with_events` |
| Materialization | Incremental |
| Incremental Strategy | [e.g., Append new records where `event_time > max(event_time)` in target] |
| Unique Key | [e.g., `event_id`] |
| Partition / Cluster | [e.g., Partitioned by `event_date`, clustered by `entity_id`] |

---

### 3.5 `dim_entities`

| Field | Value |
|-------|-------|
| Purpose | [Description] |
| Source Model(s) | `stg_source_a__entities` |
| Materialization | Table (full refresh) |
| Incremental Strategy | N/A (full refresh) |

> Repeat model detail sections as needed for each model in the product.

> **Where the dropped content lives now:**
> - **Per-column quality rules and business rules** -> data contract (`contract/contract.yaml`, RFD 0009 ODCS).
> - **Transformation logic** -> dbt SQL (`dbt/<layer>/<model>.sql`), implemented via `write-dbt-model`.
> - **Edge cases** -> inline comments in the relevant dbt model SQL, or as explicit DQ rules in the contract.

---

## 4. Backfill Strategy

| Field | Value |
|-------|-------|
| Historical Range | [e.g., 3 years of history from 2023-01-01] |
| Backfill Approach | [e.g., Full refresh of all models, chunked by month] |
| Estimated Duration | [e.g., ~4 hours for full historical load] |
| Resource Requirements | [e.g., Requires larger compute during backfill] |
| Validation Steps | [e.g., Row count reconciliation against source, spot-check business metrics] |
| Rollback Plan | [e.g., Drop and recreate from raw if backfill produces incorrect results] |

> **Where test definitions live:** dbt schema tests and data tests are declared
> in `dbt/<layer>/_<layer>__models.yml` (alongside the model SQL); contract-level
> quality rules are declared in `contract/contract.yaml` per RFD 0009. This
> template no longer carries a separate Testing Requirements section.

---

## Appendix: Revision History

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | | | Initial draft |
| | | | |
