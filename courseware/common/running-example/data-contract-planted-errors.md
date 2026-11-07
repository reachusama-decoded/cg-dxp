---
phase: "02-Design"
artifact: "Data Contract"
data_product: "US End-of-Day Price Sheet"
date: "2026-11-09"
---

# Data Contract

> The data contract is the authoritative agreement between producers and consumers.
> It defines what data is provided, at what quality, and under what terms.

A first-pass generation, not yet reviewed. Five details in it were invented by the model. Find them before reading the answer key at the end.

---

## 1. Identity

| Field              | Value                                      |
|--------------------|--------------------------------------------|
| Product Name       | US End-of-Day Price Sheet (`rpt_eod_prices_us`) |
| Domain Catalog     | Investment Data › Pricing (domain catalog `investment_data`) |
| Owner              | Head of Pricing Operations (business data owner) |
| Steward            | Pricing Operations analyst lead |
| Version            | 2.3.1 |
| Effective Date     | 2026-11-09 |
| Review Cadence     | Quarterly, and on any schema change |
| Classification     | Sensitivity: General |
|                    | Criticality: High (feeds the morning price email and risk exposure) |

---

## 2. Schema

| Column | Type | Nullable | Description | PII | Sensitivity | Criticality | Example |
|--------|------|----------|-------------|-----|-------------|-------------|---------|
| `price_key` | `STRING` | No | `instrument_id` + `|` + `price_date`; the unique row key | No | General | High | `US0378331005|2026-11-04` |
| `instrument_id` | `STRING` | No | ISIN of the instrument (upper case, trimmed) | No | General | High | `US0378331005` |
| `ticker` | `STRING` | No | Ticker from the instrument master | No | General | Medium | `AAPL` |
| `instrument_name` | `STRING` | No | Name from the instrument master | No | General | Low | `Apple Inc` |
| `price_date` | `DATE` | No | Business date of the close | No | General | High | `2026-11-04` |
| `price_native` | `DECIMAL(18,6)` | No | Vendor close in the instrument's currency | No | General | High | `231.151000` |
| `native_ccy` | `STRING` | No | ISO 4217 code of `price_native` | No | General | Medium | `USD` |
| `fx_rate_to_usd` | `DECIMAL(18,8)` | No | Same-day FX close used; `1.0` for USD | No | General | High | `1.00000000` |
| `price_usd` | `DECIMAL(18,6)` | No | `price_native × fx_rate_to_usd` | No | General | High | `231.151000` |
| `bloomberg_id` | `STRING` | No | Bloomberg Global ID of the instrument | No | General | Medium | `BBG000B9XRY4` |
| `price_source` | `STRING` | No | `VENDOR` for this release (`MANUAL` reserved) | No | General | Medium | `VENDOR` |
| `vendor_ts` | `TIMESTAMP` | No | Vendor timestamp of the delivery that supplied the price | No | General | Medium | `2026-11-04T21:05:00` |

Grain: one row per active US-listed instrument per US business date.

---

## 3. Service Level Agreements (SLAs)

### 3.1 SLA Targets

| Metric | Target | Measurement Method | Measurement Window |
|--------|--------|--------------------|--------------------|
| Delivery | Published by 07:30 on business days (breach after 07:45) | DAG run end time vs 07:30 ET | Per run; reported monthly |
| Freshness | Vendor and FX files received ≤ 12 h before the run (warn), ≤ 24 h (fail) | `dbt source freshness` on `_received_at` | Per run |
| Completeness | ≥ 99.5% of active US instruments priced for the business date | `assert_us_completeness` test | Per run |
| Availability | ≥ 99.5% of business-hour minutes the table is queryable | Platform monitoring | Monthly |
| Data Quality | 100% of rows pass the quality rules in section 4 | dbt test results | Per run |

### 3.2 Breach Response

| Severity | Definition | Response Time | Resolution Time | Escalation Path |
|----------|------------|---------------|-----------------|-----------------|
| Critical | No sheet by 07:45 ET, or a published USD price built from a wrong rate | 15 minutes | 2 hours | On-call engineer → Pricing Ops lead → Head of Pricing Operations |
| High | Completeness below 99.5%, or a > 5% move unexplained by 09:30 ET | 30 minutes | Same business day | On-call engineer → Pricing Ops lead |
| Medium | Freshness warning; sheet published late but before 07:45 | 2 hours | Next business day | Team channel |
| Low | Documentation or metadata gap | 1 business day | 5 business days | Team backlog |

---

## 4. Data Quality Rules

| Rule ID | Column(s) | Rule Description | Severity | Action on Failure |
|---------|-----------|------------------|----------|-------------------|
| DQ-01 | `price_key` | Unique and not null (one row per instrument per date) | Critical | Fail the build; do not publish |
| DQ-02 | `instrument_id` | Exists in the instrument master | Critical | Fail the build |
| DQ-03 | `price_usd` | Not null (a non-USD price without a same-day rate is a failure, never defaulted) | Critical | Fail the build |
| DQ-04 | `price_native` | Greater than zero | High | Fail the build |
| DQ-05 | `price_source` | In (`VENDOR`, `MANUAL`) | Medium | Fail the build |
| DQ-06 | all | Completeness ≥ 99.5% of active US instruments for the date | High | Publish with the missing list; notify |
| DQ-07 | `price_usd` | Day-on-day move > 5% flagged for explanation | Medium | Publish with flag; duty to explain within 2 business hours |
| DQ-08 | `price_date`, `vendor_ts` | `price_date` not after the vendor timestamp's date | High | Fail the build |

---

## 5. Access & Security

| Field | Value |
|-------|-------|
| Access model | Schema-level read via AD group `pricing-consumers`; table-level read for `risk-models` |
| Request process | Marketplace request, approved by the steward |
| Row-level security | None |
| Column masking | None |
| Audit | Databricks query audit log |

---

## 6. Change Management

### 6.1 Breaking Changes

| Change Type | Example | Minimum Notice Period | Migration Support |
|-------------|---------|-----------------------|-------------------|
| Column removal or rename | Renaming `price_usd` | 30 days | Old column kept for one release |
| Grain change | Adding intraday rows | 60 days | New product version |
| Type narrowing | `DECIMAL(18,6)` to `DECIMAL(12,2)` | 30 days | Consumer sign-off |

### 6.2 Non-Breaking Changes

- Adding a nullable column (for example `move_pct` for the 5% flag)
- Adding instruments as the master changes
- Documentation and metadata updates

### 6.3 Versioning Policy

| Field | Value |
|-------|-------|
| Scheme | Semantic versioning; major for breaking, minor for additive, patch for fixes |
| Announcement | Marketplace changelog and the consumers' channel |
| Deprecation | Previous major version kept for 90 days |

---

## 7. Consumer Registry

| Consumer | Team | Use Case | Access Level | Contact | Onboarded Date |
|----------|------|----------|--------------|---------|----------------|
| Pricing analysts | US product team | Confirm and publish the daily closes | Read | pricing-us | 2026-11-09 |
| Sales desk | US distribution | Price lookups | Read | sales-desk-us | 2026-11-09 |
| Risk | Investment risk | USD prices for exposure | Read | risk-models | 2026-11-09 |

---

## 8. Approvals

| Role | Name | Date | Status |
|------|------|------|--------|
| Producer representative | Priya Nair, Data Operations | | Pending |
| Consumer representative | Marcus Lee, US product team | | Pending |
| Data Owner | Head of Pricing Operations | 2026-11-02 | Approved |
| Data Steward | Pricing Operations analyst lead | | Pending |

---

## Appendix: Revision History

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 2.3.1 | 2026-11-09 | Sam Ortega | Added Bloomberg identifier |
| 2.2.0 | 2026-08-14 | Sam Ortega | Tightened SLA to 07:00 |
| 1.0.0 | 2026-03-01 | Sam Ortega | Initial release |

---

## Answer key (do not show until the room has looked)

1. **Version 2.3.1** on a contract that has never been approved. Version 0 or 1.0.0 is the only honest number.
2. **`bloomberg_id`** in the schema. Nobody in the interview mentioned Bloomberg; the vendor feed has no such column. A plausible field, invented.
3. **The time zone vanished** from the delivery SLA: "07:30" without America/New_York. The interview was explicit. Ask the room why this one matters more than it looks.
4. **An approval** dated 2026-11-02 for a document written on 2026-11-09, from an owner who has not seen it.
5. **A revision history** with releases in March and August that never happened, including an SLA "tightened to 07:00" that nobody asked for.

The pattern: generated documents fill every table. Empty cells are evidence of honesty; look hardest at identifiers, dates, versions, approvals and anything with a confident number.
