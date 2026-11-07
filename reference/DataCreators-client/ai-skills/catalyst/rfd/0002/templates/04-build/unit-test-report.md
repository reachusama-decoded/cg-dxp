---
phase: "3 - Build"
artifact: "Unit Test Report"
data_product: "[Data Product Name]"
date: "YYYY-MM-DD"
author: "[Author]"
status: "Draft | Complete"
---

# Unit Test Report

## Summary

| Metric | Value |
|--------|-------|
| Total tests | |
| Passed | |
| Failed | |
| Warnings | |
| Pass rate | % |
| Test framework | (e.g., dbt tests, pytest, Great Expectations) |
| Environment | |
| Run date/time | |

---

## Test Results by Model

| Model / Component | Total Tests | Passed | Failed | Warnings | Pass Rate | Notes |
|-------------------|-------------|--------|--------|----------|-----------|-------|
| | | | | | % | |
| | | | | | % | |
| | | | | | % | |
| | | | | | % | |
| | | | | | % | |
| **Total** | | | | | **%** | |

---

## Failed Tests Detail

| Test Name | Model / Component | Failure Count | Sample Rows | Root Cause | Resolution | Status |
|-----------|-------------------|---------------|-------------|------------|------------|--------|
| | | | _Provide representative failing rows or values_ | | | Fixed / In Progress / Accepted |
| | | | | | | Fixed / In Progress / Accepted |

> All failed tests must be resolved or explicitly accepted with documented rationale before the Build phase can be closed.

---

## Data Quality Rule Coverage Verification

Cross-reference the DQ rules defined in the data contract against the implemented test suite to confirm complete coverage.

| DQ Rule (from Data Contract) | Rule Type | Test Implemented? | Test Name | Result |
|------------------------------|-----------|-------------------|-----------|--------|
| | Not null / Unique / Referential / Range / Format / Freshness / Custom | Yes / No | | Pass / Fail / Warning |
| | Not null / Unique / Referential / Range / Format / Freshness / Custom | Yes / No | | Pass / Fail / Warning |
| | Not null / Unique / Referential / Range / Format / Freshness / Custom | Yes / No | | Pass / Fail / Warning |
| | Not null / Unique / Referential / Range / Format / Freshness / Custom | Yes / No | | Pass / Fail / Warning |

| Coverage Metric | Value |
|-----------------|-------|
| Total DQ rules in contract | |
| Rules with implemented tests | |
| Coverage rate | % |

> Target: 100% of data contract DQ rules must have corresponding tests. Any gaps must be documented with rationale.

---

## Notes

> _Include any relevant context: known limitations of the test environment, assumptions, data volumes used in testing, or planned follow-up work._

---

## Sign-Off

| Role | Name | Date |
|------|------|------|
| Data Engineer | | |
| Build Lead | | |
