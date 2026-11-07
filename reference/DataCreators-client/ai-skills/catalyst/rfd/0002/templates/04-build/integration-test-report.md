---
phase: "4 - Build"
artifact: "Integration Test Report"
data_product: "[Data Product Name]"
date: "YYYY-MM-DD"
author: "[Author]"
status: "Draft | Complete"
---

# Integration Test Report

Integration tests verify end-to-end pipeline behavior across real or
representative source connections, transformations, and consumer outputs. They
complement unit tests by exercising component interactions that unit tests
cannot cover.

---

## Summary

| Metric | Value |
|--------|-------|
| Total integration tests | |
| Passed | |
| Failed | |
| Skipped | |
| Pass rate | % |
| Environment | *(e.g., dev, staging)* |
| Source data | *(prod copy / synthetic / anonymized)* |
| Run date/time | |
| CI run reference | |

---

## Test Coverage by Concern

| Concern | Tests Defined | Tests Passed | Notes |
|---------|--------------|--------------|-------|
| Source connectivity (all source systems reachable) | | | |
| Schema conformance (output matches data contract) | | | |
| Transformation correctness (key business rules validated end-to-end) | | | |
| Idempotency (re-run produces identical output) | | | |
| Incremental / full-load behavior | | | |
| Backfill scenario (if applicable) | | | |
| Consumer output format and delivery | | | |
| SLA / freshness (pipeline completes within defined window) | | | |
| Volume / scale (test data representative of expected load) | | | |
| Error handling and recovery (bad input, source unavailability) | | | |

---

## Failed Tests Detail

| Test Name | Concern Area | Failure Description | Root Cause | Resolution | Status |
|-----------|-------------|---------------------|------------|------------|--------|
| | | | | | Fixed / In Progress / Accepted |
| | | | | | Fixed / In Progress / Accepted |

> All failed tests must be resolved or explicitly accepted with documented
> rationale before the Build phase can be closed.

---

## Data Contract Conformance

Verify that pipeline output satisfies the contract defined in `data-contract.md`.

| Contract Field | Expected | Observed | Pass / Fail |
|----------------|----------|----------|-------------|
| Schema version | | | |
| Row counts within tolerance | | | |
| Null rates within thresholds | | | |
| Freshness SLA met | | | |
| No undocumented columns in output | | | |

---

## Notes

> _Include environment caveats, data volume used in testing, assumptions about
> source availability, or planned follow-up work._

---

## Sign-Off

| Role | Name | Date |
|------|------|------|
| Data Engineer | | |
| Build Lead | | |
