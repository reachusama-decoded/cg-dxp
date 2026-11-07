---
phase: "Intake & Discovery"
artifact: "Feasibility Report"
data_product: "[Product Name]"
date_created: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
---

# Feasibility Report

Assesses whether the proposed data product can be built given current data
availability, technical capabilities, regulatory constraints, and organizational
capacity.

---

## Executive Summary

<!-- Two to four sentences: can we build this, under what conditions, and what are
     the primary risks? State the recommendation up front. -->

---

## 1. Data Availability

Evaluate each required source for accessibility, quality, and readiness.

| Source System / Dataset | Owner          | Access Available? | Quality Assessment | Known Gaps            | Risk Level |
|-------------------------|----------------|-------------------|--------------------|-----------------------|------------|
|                         |                | _Yes / Partial / No_ |                 |                       | _H / M / L_ |
|                         |                |                   |                    |                       |            |

**Summary:** <!-- Are all critical sources accessible and fit for purpose? -->

## 2. Technical Feasibility

### Ingestion

| Factor                        | Assessment                     |
|-------------------------------|--------------------------------|
| Ingestion Method              | _e.g., batch, streaming, CDC, API_ |
| Connectivity                  | _Can we reach the source?_     |
| Volume Handling               | _Can the platform handle the expected volume?_ |
| Incremental Load Support      | _Yes / No / Partial_           |

### Transformation

| Factor                        | Assessment                     |
|-------------------------------|--------------------------------|
| Complexity                    | _Low / Medium / High_          |
| Existing Reusable Assets      | _e.g., shared models, common transforms_ |
| Platform Fit                  | _Does the current platform support the required transformations?_ |

### Serving

| Factor                        | Assessment                     |
|-------------------------------|--------------------------------|
| Serving Layer                 | _e.g., catalog, warehouse, API, file export_ |
| Latency Requirements Met?     | _Yes / No — explain_           |
| Consumer Access Mechanisms    | _e.g., SQL, REST, event subscription_ |
| Catalog Integration           | _e.g., Unity Catalog, Snowflake, Datahub — platform-dependent_ |

## 3. Regulatory & Compliance

| Factor                        | Assessment                     |
|-------------------------------|--------------------------------|
| PII Present                   | _Yes / No / Unknown_           |
| Privacy Impact Assessment Required | _Yes / No_               |
| Regulatory Requirements       |                                |
| Data Sensitivity              | _Public / General / Restricted / Highly Restricted_ <!-- See your organisation's data classification policy for level definitions --> |
| Data Criticality              | _Mission-Critical / Business-Critical / Standard / Low_ |
| Cross-Border Transfer         | _Yes / No_                     |
| Retention Requirements        |                                |

## 4. Organizational Feasibility

| Factor                        | Assessment                     |
|-------------------------------|--------------------------------|
| Team Capacity                 | _Available / Constrained / Unavailable_ |
| Required Skills               |                                |
| Cross-Team Dependencies       |                                |
| Stakeholder Availability      |                                |

## 5. Conditions & Blockers

| #  | Item                                   | Type              | Owner          | Mitigation / Resolution     |
|----|----------------------------------------|-------------------|----------------|-----------------------------|
| 1  |                                        | _Blocker / Condition_ |            |                             |
| 2  |                                        |                   |                |                             |

## 6. Completeness Check

All items below must be checked before this document is considered complete.

- [ ] Every identified source system has a data availability verdict (Feasible / Feasible with conditions / Not feasible)
- [ ] Technical feasibility addresses ingestion, transformation, AND serving (not just one)
- [ ] Regulatory/compliance verdict is stated (Clear / Needs review / Blocker identified)
- [ ] Every condition or blocker has an owner and a resolution path
- [ ] The recommendation is one of: Proceed / Proceed with conditions / Defer / Cancel (no "TBD")
- [ ] If PII = Yes or Unknown: Privacy Impact Assessment is flagged as required in linked artifacts

---

## 7. Recommendation

| Decision                      | Rationale                      |
|-------------------------------|--------------------------------|
| **Proceed**                   |                                |
| **Proceed with Conditions**   |                                |
| **Defer**                     |                                |
| **Cancel**                    |                                |

_Select one. Provide rationale and reference the conditions or blockers above._

---

## Approvals

| Role                       | Name               | Date       | Decision           |
|----------------------------|---------------------|------------|--------------------|
| Data Product Manager       |                     |            |                    |
| Technical Lead             |                     |            |                    |
| Domain Owner               |                     |            |                    |
