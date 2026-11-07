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

**Logic Summary:**
- Rename columns to conform to naming conventions
- Cast types (e.g., string dates to timestamps)
- Filter out test/internal records using [criteria]
- Trim whitespace from string fields

**Business Rules:**
- [e.g., Records with `status = 'test'` are excluded]
- [e.g., Null `created_at` defaults to `_loaded_at` timestamp]

**Edge Cases:**
- [e.g., Duplicate source records are deduplicated by taking the latest `_loaded_at`]

---

### 3.2 `stg_source_b__events`

| Field | Value |
|-------|-------|
| Purpose | [Description] |
| Source Model(s) | `raw.source_b.events` |
| Materialization | View |
| Incremental Strategy | N/A |

**Logic Summary:**
- [Describe transformations]

**Business Rules:**
- [List rules]

**Edge Cases:**
- [List edge cases]

---

### 3.3 `int_entities_with_events`

| Field | Value |
|-------|-------|
| Purpose | [Description] |
| Source Model(s) | `stg_source_a__entities`, `stg_source_b__events` |
| Materialization | Ephemeral / View |
| Incremental Strategy | N/A |

**Logic Summary:**
- [Describe join logic, filtering, aggregations]

**Business Rules:**
- [List rules]

**Edge Cases:**
- [e.g., Entities with no matching events are included with null event fields (left join)]

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

**Logic Summary:**
- [Describe transformations]

**Business Rules:**
- [List rules]

**Edge Cases:**
- [e.g., Late-arriving events within 72-hour lookback window are merged on re-run]

---

### 3.5 `dim_entities`

| Field | Value |
|-------|-------|
| Purpose | [Description] |
| Source Model(s) | `stg_source_a__entities` |
| Materialization | Table (full refresh) |
| Incremental Strategy | N/A (full refresh) |

**Logic Summary:**
- [Describe transformations]

**Business Rules:**
- [List rules]

**Edge Cases:**
- [List edge cases]

> Repeat model detail sections as needed for each model in the product.

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

---

## 5. Testing Requirements

### 5.1 Schema Tests

| Model | Test | Description |
|-------|------|-------------|
| `fct_entity_events` | Unique | `event_id` is unique |
| `fct_entity_events` | Not Null | `event_id`, `entity_id`, `event_time` are not null |
| `dim_entities` | Unique | `entity_id` is unique |
| `dim_entities` | Relationships | `entity_id` references `fct_entity_events.entity_id` |
| | | |

### 5.2 Data Quality Tests

| Model | Test | Severity | Description |
|-------|------|----------|-------------|
| `fct_entity_events` | Row count | Warn | Row count per day does not drop > 50% vs previous day |
| `fct_entity_events` | Freshness | Error | Source data is no more than [X] hours old |
| `dim_entities` | Accepted values | Error | `status` is one of `active`, `inactive`, `archived` |
| | | | |

### 5.3 Unit / Logic Tests

| Test | Description | Approach |
|------|-------------|----------|
| [e.g., Status mapping] | Verify status code to label mapping is correct | [e.g., Unit test with fixed input/output fixtures] |
| [e.g., Deduplication logic] | Verify correct record is retained when duplicates exist | [e.g., Unit test with known duplicate input] |
| | | |

---

## Appendix: Revision History

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | | | Initial draft |
| | | | |
