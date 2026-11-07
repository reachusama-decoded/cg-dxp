---
phase: "4 - Validate"
artifact: "Data Quality Sign-Off"
data_product: "[Data Product Name]"
date: "YYYY-MM-DD"
author: "[Author]"
status: "Draft | Complete"
---

# Data Quality Sign-Off

## Summary

| Metric | Value |
|--------|-------|
| Total DQ rules evaluated | |
| Passing | |
| Failing | |
| Pass rate | % |
| Environment | |
| Evaluation date/time | |
| **Verdict** | **Pass / Conditional Pass / Fail** |

> **Pass:** All rules passing. **Conditional Pass:** Failing rules have accepted exceptions documented below. **Fail:** Unresolved failures remain.

---

## Rule-by-Rule Results

| Rule ID | Rule Description | Rule Type | Sensitivity | Criticality | Severity | Expected | Actual | Result |
|---------|------------------|-----------|-------------|-------------|----------|----------|--------|--------|
| DQ-001 | | Not null / Unique / Referential / Range / Format / Freshness / Custom | | | Critical / High / Medium / Low | | | Pass / Fail |
| DQ-002 | | Not null / Unique / Referential / Range / Format / Freshness / Custom | | | Critical / High / Medium / Low | | | Pass / Fail |
| DQ-003 | | Not null / Unique / Referential / Range / Format / Freshness / Custom | | | Critical / High / Medium / Low | | | Pass / Fail |
| DQ-004 | | Not null / Unique / Referential / Range / Format / Freshness / Custom | | | Critical / High / Medium / Low | | | Pass / Fail |

---

## Exception Log

For any failing rules where the failure is accepted and will not block release.

| Rule ID | Rule Description | Failure Detail | Justification for Acceptance | Accepted By | Remediation Plan | Target Date |
|---------|------------------|----------------|------------------------------|-------------|------------------|-------------|
| | | | | | | |
| | | | | | | |

> Exceptions for **Critical** severity rules require Data Owner approval.

---

## Reconciliation Results

Complete this section if the data product is migrating from or replacing an existing source.

| Reconciliation Check | Source Value | Target Value | Variance | Threshold | Result |
|----------------------|-------------|--------------|----------|-----------|--------|
| Row count | | | | | Pass / Fail |
| Sum of [metric column] | | | | | Pass / Fail |
| Distinct count of [key column] | | | | | Pass / Fail |
| | | | | | Pass / Fail |

| Reconciliation Metric | Value |
|-----------------------|-------|
| Total checks | |
| Passing | |
| Failing | |
| Reconciliation verdict | Pass / Conditional Pass / Fail |

Notes:
> _Describe any expected variances, timing differences, or known discrepancies between source and target._

---

## Sign-Off

| Role | Name | Decision | Date |
|------|------|----------|------|
| Data Engineer | | Pass / Conditional Pass / Fail | |
| Data Steward | | Pass / Conditional Pass / Fail | |
| Data Owner | | Pass / Conditional Pass / Fail | |
