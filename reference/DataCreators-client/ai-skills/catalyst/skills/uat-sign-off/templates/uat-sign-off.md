---
phase: "4 - Validate"
artifact: "UAT Sign-Off"
data_product: "[Data Product Name]"
date: "YYYY-MM-DD"
author: "[Author]"
status: "Draft | In Progress | Complete"
---

# UAT Sign-Off

## UAT Test Scenarios

| ID | Scenario | Expected Result | Actual Result | Pass / Fail | Tester | Date |
|----|----------|-----------------|---------------|-------------|--------|------|
| UAT-001 | | | | | | |
| UAT-002 | | | | | | |
| UAT-003 | | | | | | |
| UAT-004 | | | | | | |
| UAT-005 | | | | | | |

| UAT Summary | Value |
|-------------|-------|
| Total scenarios | |
| Passed | |
| Failed | |
| Pass rate | % |

---

## Business Logic Validation

Confirm that the data product output matches business expectations and approved specifications.

| Validation Check | Description | Expected | Actual | Result | Tester |
|------------------|-------------|----------|--------|--------|--------|
| | | | | Pass / Fail | |
| | | | | Pass / Fail | |
| | | | | Pass / Fail | |

Notes:
> _Describe any business logic edge cases tested, sample queries used, or comparison methodology._

---

## Data Completeness Check

Verify that the data product contains the expected scope of data (time range, entities, dimensions).

| Completeness Check | Expected | Actual | Result |
|--------------------|----------|--------|--------|
| Date range coverage | | | Pass / Fail |
| Entity/record count | | | Pass / Fail |
| Dimension coverage (e.g., all regions, all product lines) | | | Pass / Fail |
| Null rate within acceptable thresholds | | | Pass / Fail |
| Sensitivity and criticality classifications applied | | | Pass / Fail |

Notes:
> _Describe any expected gaps, known exclusions, or filtering logic that affects completeness._

---

## Consumer Access Verification

Confirm that downstream consumers can access the data product through their intended interfaces.

| Consumer / Consumer Group | Access Method | Access Granted | Verified Working | Tester | Date |
|---------------------------|---------------|----------------|------------------|--------|------|
| | (e.g., SQL query, API, dashboard, file export) | Yes / No | Yes / No | | |
| | | Yes / No | Yes / No | | |
| | | Yes / No | Yes / No | | |

Notes:
> _Describe any access issues encountered and their resolution._

---

## Known Issues and Accepted Risks

| ID | Description | Severity | Impact | Mitigation / Workaround | Accepted By | Date |
|----|-------------|----------|--------|--------------------------|-------------|------|
| 1 | | Critical / High / Medium / Low | | | | |
| 2 | | Critical / High / Medium / Low | | | | |

> **Critical** severity issues must be resolved before sign-off. Any accepted risks require Data Owner approval.

---

## Formal Sign-Off

By signing below, the approver confirms the data product meets the acceptance criteria for User Acceptance Testing and is approved to proceed to production release.

| Role | Name | Decision | Date |
|------|------|----------|------|
| Data Owner | | Approved / Approved with Conditions / Rejected | |
| Data Steward | | Approved / Approved with Conditions / Rejected | |
| InfoSec / Security | | Approved / Approved with Conditions / Rejected / N/A | |

> **InfoSec / Security sign-off:** Required for products classified Restricted or above, or subject to a named regulation. N/A for all other products.

**Conditions (if applicable):**
> _List any conditions that must be met before or shortly after production release._
