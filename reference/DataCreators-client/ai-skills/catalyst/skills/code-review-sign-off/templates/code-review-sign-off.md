---
phase: "3 - Build"
artifact: "Code Review Sign-Off"
data_product: "[Data Product Name]"
date: "YYYY-MM-DD"
author: "[Author]"
status: "Draft | In Review | Approved | Approved with Conditions"
---

# Code Review Sign-Off

## Review Scope

| Component | Description | Reviewer | Status |
|-----------|-------------|----------|--------|
| Source integration | Ingestion logic, connection handling | | Not Started / In Review / Approved |
| Transformation models | Business logic, staging, and output models | | Not Started / In Review / Approved |
| Data quality rules | DQ tests and validation logic | | Not Started / In Review / Approved |
| Orchestration | DAG/pipeline definition, scheduling, retries | | Not Started / In Review / Approved |
| Security configuration | Grants, masking, encryption settings | | Not Started / In Review / Approved |
| Infrastructure / config | Environment config, deployment scripts | | Not Started / In Review / Approved |

---

## Review Criteria

### Correctness

| Criterion | Met? | Notes |
|-----------|------|-------|
| Transformation logic matches the approved specification | Yes / No / N/A | |
| Edge cases handled (nulls, empty sets, late-arriving data, duplicates) | Yes / No / N/A | |
| Output schema matches the physical data model | Yes / No / N/A | |
| Joins and filters produce expected cardinality | Yes / No / N/A | |
| Incremental logic is correct and complete | Yes / No / N/A | |

### Security and Compliance

| Criterion | Met? | Notes |
|-----------|------|-------|
| No hardcoded credentials, tokens, or secrets in code or config | Yes / No / N/A | |
| Grants and role assignments match the access control design | Yes / No / N/A | |
| Sensitivity and criticality classifications reflected in controls | Yes / No / N/A | |
| Column masking / row-level security applied where required | Yes / No / N/A | |
| PII and restricted data handled per policy | Yes / No / N/A | |

### Code Quality

| Criterion | Met? | Notes |
|-----------|------|-------|
| Naming conventions followed (models, columns, variables) | Yes / No / N/A | |
| Code is readable and self-documenting | Yes / No / N/A | |
| No dead code, commented-out blocks, or debug artifacts | Yes / No / N/A | |
| Configuration separated from logic | Yes / No / N/A | |
| Documentation (inline comments, model descriptions) adequate | Yes / No / N/A | |

### Operability

| Criterion | Met? | Notes |
|-----------|------|-------|
| Pipeline is idempotent (safe to re-run without side effects) | Yes / No / N/A | |
| Handles upstream schema evolution gracefully | Yes / No / N/A | |
| Retry and failure behavior is well-defined | Yes / No / N/A | |
| Logging is sufficient for debugging | Yes / No / N/A | |
| Resource usage is reasonable (no unnecessary full scans, etc.) | Yes / No / N/A | |

### Testing

| Criterion | Met? | Notes |
|-----------|------|-------|
| Unit tests exist for all transformation models | Yes / No / N/A | |
| Unit tests cover key business logic paths | Yes / No / N/A | |
| Data quality rules have corresponding test cases | Yes / No / N/A | |
| All tests pass at time of review | Yes / No / N/A | |

---

## Outstanding Issues

| ID | Severity | Description | Owner | Resolution | Status | Closure Confirmed |
|----|----------|-------------|-------|------------|--------|-------------------|
| 1 | Critical / High / Medium / Low | | | | Open / Resolved / Accepted | [ ] Yes — reviewer name, date / N/A |
| 2 | Critical / High / Medium / Low | | | | Open / Resolved / Accepted | [ ] Yes — reviewer name, date / N/A |

> All **Critical** and **High** severity issues must be resolved before approval. Medium and Low issues may be accepted with documented rationale.

---

## Condition Closure

If the final decision is 'Approved with conditions', the original reviewer must confirm all conditions are closed before the build checklist gate can be marked complete.

| Condition | Original Reviewer | Closure Confirmed | Date |
|---|---|---|---|
| | | [ ] Yes  [ ] Outstanding | |

> **Note:** The build gate cannot pass while any condition is marked Outstanding.

---

## Final Decision

| Decision | Selected |
|----------|----------|
| Approved | [ ] |
| Approved with conditions | [ ] |
| Changes required --- re-review needed | [ ] |

**Conditions (if applicable):**
> _List any conditions that must be met before merge or before proceeding to Validate._

| Role | Reviewer | Decision | Date |
|------|----------|----------|------|
| Primary Reviewer | | Approved / Conditional / Changes Required | |
| Secondary Reviewer (if applicable) | | Approved / Conditional / Changes Required | |
