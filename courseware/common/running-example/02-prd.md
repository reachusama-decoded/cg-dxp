---
phase: "02-Discovery"
artifact: "Product Requirements Document"
data_product: "US End-of-Day Price Sheet"
date: "2026-11-09"
---

# Product Requirements Document: US End-of-Day Price Sheet

Generated with the `product-requirements-document` skill from the interview transcript, then reviewed by the creator. Review notes are in square brackets where a generated line was corrected.

### Key Product Information

| Field | Value |
|-------|-------|
| **Product Name** | US End-of-Day Price Sheet (`rpt_eod_prices_us`) |
| **Data Owner** | Head of Pricing Operations (business data owner for prices) |
| **Data Steward** | Pricing Operations analyst lead |
| **Data Product Creator** | Sam Ortega, Investment Data engineering |
| **Domain** | Investment Data › Pricing |
| **Sensitivity** | General |
| **Current Phase** | Triage & Discovery |
| **Author** | Sam Ortega |
| **Last Updated** | 2026-11-09 |

### 1. Executive Summary

The US product team publishes a daily price sheet for US-listed products from a vendor file, a spreadsheet and manual currency conversion. This product replaces that process with a governed table of closing prices in USD, one row per active US-listed instrument per business day, published by 07:30 ET with the FX rate used and a record of which vendor delivery supplied each price. Pricing analysts, the sales desk and the risk team stop re-deriving the same numbers, and a corrected vendor price becomes explainable instead of a mystery.

### 2. Problem & Value

- **Existing Product Check:** The marketplace was searched for "price", "close", "EOD" and "pricing". The vendor landing table exists as a source-aligned asset (global, native currency, every delivery kept). No consumer-aligned US price product exists. [Generated text claimed "no related assets"; corrected to name the landing table.]
- **Current State:** Each morning an analyst opens the latest vendor file, filters to US instruments by hand, converts non-USD prices with the previous day's FX rate, checks moves over 5% by eye and emails a sheet. About forty minutes on a good day; late when the file is late; unanswerable when a vendor correction changes a number risk has already taken.
- **Future State:** The sheet is a table built every US business day by 07:30 ET, with same-day FX, a flag for moves over 5%, the vendor timestamp per price, and a visible list of missing instruments. The email is generated from the table.
- **Why Now?** (1) Risk has escalated two unexplained price changes this quarter. (2) The London product team has asked for the same sheet for UK listings, which is a filter on this product rather than a second spreadsheet. (3) The paved path makes a governed daily table a week of work, not a project.

### 3. Consumers & Use Cases

**Primary Consumers**

| Consumer | Team | What They Need |
|---|---|---|
| Pricing analysts | US product team | The closes they stand behind, by 07:30 ET, with missing instruments listed |
| Sales desk | US distribution | Price lookups by ticker during the morning |
| Risk | Investment risk | USD prices and the rate used, stable once published |

**Key Use Cases**

| Use Case | Consumer | Business Value | Priority | Needed By |
|---|---|---|---|---|
| As a pricing analyst, I want the US sheet built from the latest vendor delivery with same-day FX so that I confirm closes instead of assembling them | Pricing analysts | 40 minutes a day returned; fewer errors | P1 | First release |
| As a risk analyst, I want to see which vendor delivery a price came from so that a changed number is explainable | Risk | Resolves escalations in minutes | P1 | First release |
| As a sales associate, I want to look up a price by ticker so that I answer a client without asking pricing | Sales desk | Faster client answers | P2 | First release |
| As a London analyst, I want the same sheet for UK listings so that we do not build a second process | London product team | Reuse | P3 | Later release |

### 4. Solution Overview

- **What We're Building:** A dbt project on the paved path that stages the vendor price file, the instrument master and the FX feed; deduplicates vendor re-deliveries to the latest timestamp; looks up market, ticker and name from the master; converts to USD with the same-day rate; and publishes a consumer-aligned table filtered to active US instruments. Airflow runs it at 06:30 ET on US business days after checking that both feeds are fresh. Tests enforce the grain, the lookups and completeness.
- **What This Is NOT:** Not intraday or real-time prices. Not a valuation. Not a source of record for instrument reference data. Not an override process (manual prices are out of scope for the first release).
- **Output Ports:**

| Port | Type | Access Method |
|---|---|---|
| `rpt_eod_prices_us` | Table | Databricks, domain catalog; Marketplace listing |
| Morning price email | File | Generated from the table by the existing email job |

- **Key Terms:** *Close*: the vendor's official closing price on the primary listing. *Business date*: the trading date the close belongs to, not the delivery time. *Same-day FX*: the FX close for the same business date. *Active instrument*: flagged active in the instrument master. *Re-delivery*: a second vendor file for the same date with a later vendor timestamp.

### 5. Data Requirements

**Source Systems**

| Source System | Data Provided | SoR? | Full/Delta | Contract Link | Sample Data Link | Notes |
|---|---|---|---|---|---|---|
| Vendor price feed (`vendor_feed.vendor_prices_raw`) | Global EOD closes, native currency, vendor timestamp | Yes (vendor) | Full daily file, re-deliveries possible | Vendor contract (Investment Data) | Landing table | Lands about 21:00 ET; no market attribute |
| Instrument master (`refdata.instrument_master_raw`) | ISIN, ticker, name, market, trade currency, active flag | Yes (internal) | Full | Internal | Reference catalog | ISIN is the join key; one primary ISIN per instrument |
| FX feed (`fx_feed.fx_rates_raw`) | Daily FX closes to USD | Yes | Full daily | Internal | Landing table | Lands about 17:00 ET from a different team |

**Engineering Intake Snapshot**

| Field | Value |
|---|---|
| Desired Technical Outcome | One consumer-aligned table, tested, scheduled, discoverable |
| Number of New Outputs | 1 |
| Required SLA | Published by 07:30 ET on US business days; ≥ 99.5% completeness |
| Historical Backfill Required | Yes, 90 business days, to seed the 5% move check |
| Backfill Start Date | 90 business days before go-live |

**Data Quality Requirements**

| Dimension | Target | How Measured |
|---|---|---|
| Freshness | Vendor file received ≤ 12 h before the run (warn), ≤ 24 h (fail) | `dbt source freshness` on `_received_at` |
| Completeness | ≥ 99.5% of active US instruments priced per business date | Singular test `assert_us_completeness` |
| Accuracy | No USD price computed from a missing or stale rate; moves > 5% flagged | `not_null` on `price_usd`; day-on-day comparison |
| Uniqueness | One row per instrument per date | `unique` on `price_key` |

### 6. Technical Design

| Component | Technology | Notes |
|---|---|---|
| Platform | Databricks on S3 (Delta), Unity Catalog | Application catalog for build, domain catalog for publish |
| Framework | dbt (staging → intermediate → mart) | Transformation and tests in one project |
| Orchestration | Airflow on Astronomer, Cosmos task group | 06:30 ET weekdays; freshness gate first |
| Consumption | Databricks SQL, Marketplace listing, email job | Email reads the table |

### 7. Governance

| Consideration | Applicable? | Notes |
|---|---|---|
| Regulatory | No | Published prices from a licensed vendor; licence permits internal use |
| PII/Sensitive Data | No | Instrument data only |
| Retention | Yes | Keep every business date; the landed vendor deliveries are retained by the landing table |

### 8. Success Criteria

| KPI | Target | Measurement Method | By When |
|---|---|---|---|
| Sheet published on time | ≥ 95% of business days by 07:30 ET in the first quarter | DAG end time | Quarter after go-live |
| Analyst time | Morning assembly under 10 minutes | Analyst log | One month after go-live |
| Unexplained price changes escalated by risk | 0 | Risk escalation log | Quarter after go-live |

### 9. Data Marketplace & Catalog

- **Catalog Metadata:** Display Name "US End-of-Day Price Sheet"; Description "Closing prices in USD for active US-listed instruments, one row per instrument per business date, with the FX rate and vendor delivery used"; Domain Investment Data; Sub-Domain Pricing; Data Category Reference/Market data; Update Frequency daily (US business days); Retention indefinite.
- **Discoverability:** Tags `pricing`, `eod`, `usd`, `us-listed`; Keywords "close price", "price sheet"; Related Products: vendor price landing table, instrument master.
- **Access & Entitlements:** Access Level general; Entitlement Group pricing-consumers; Request Process via the Marketplace.
- **Governance Tool Integration:** Collibra Asset ID pending registration; Lineage documented by dbt; Quality Rules registered in the contract; Certification Status pending.

### 10. Approval

| Role | Name | Status | Date |
|---|---|---|---|
| Data Owner | Head of Pricing Operations | Pending | |
| Data Steward | Pricing Operations analyst lead | Pending | |
| Architecture Review | Platform architecture | Pending | |

### Appendix

**Related Documentation**

| Document | Location |
|---|---|
| Data contract | `03-data-contract.md` |
| Source-to-target mapping | `04-sttm.md` |
| Service levels | `05-service-levels.md` |

**Glossary**

| Term | Definition |
|---|---|
| ISIN | International Securities Identification Number; the join key between the vendor feed and the instrument master |
| Primary listing | The exchange whose close the vendor reports as the instrument's official close |
| Business date | The trading date a close belongs to |

**Critical Dependencies**

| Dependency | Owner | Status | Impact if Unresolved |
|---|---|---|---|
| FX feed lands by 17:30 ET | FX data team | Agreed verbally | No USD prices for non-USD instruments; build fails by design |
| Instrument master `market` and `is_active` are maintained | Reference data team | In place | Wrong instruments on the sheet |

**Open Questions**

| Question | Owner | Decision Needed By |
|---|---|---|
| Which US market holiday calendar does the schedule use? | Pricing Operations | Before go-live |
| Should a > 5% move hold publication or publish with a flag? | Head of Pricing Operations | Before go-live |

**Key Risks**

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Vendor re-delivery after 07:30 ET changes a published price | Med | Med | Keep both deliveries; publish the vendor timestamp; notify consumers of corrections |
| Instrument master lags a new listing | Med | Low | Completeness test lists the gap; master owners notified |
