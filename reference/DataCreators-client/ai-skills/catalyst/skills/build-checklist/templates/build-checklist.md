---
phase: "3 - Build"
artifact: "Build Checklist"
data_product: "[Data Product Name]"
date: "YYYY-MM-DD"
author: "[Author]"
status: "Draft | In Progress | Complete"
---

# Build Checklist

## 1. Pre-Build Gates

Before development begins, confirm the following Design-phase artifacts have been approved and are accessible to the build team.

| Gate | Artifact | Approved By | Date | Status |
|------|----------|-------------|------|--------|
| Data contract finalized | Data contract specification | | | Pending / Done |
| Logical model approved | Logical data model | | | Pending / Done |
| Physical model approved | Physical data model | | | Pending / Done |
| Lineage documented | Data lineage diagram | | | Pending / Done |
| Security design approved | Access control and sensitivity/criticality classification | | | Pending / Done |
| DataOps handoff reviewed | Operational handoff plan (draft) | | | Pending / Done |

**Gate decision:** All items above must be marked **Done** before proceeding.

- [ ] Pre-build gate passed
- Approved by: _______________
- Date: _______________

---

## 2. Development

### 2.1 Source Integration

| Item | Details | Status |
|------|---------|--------|
| Source system(s) connected | | Not Started / In Progress / Done |
| Connection credentials stored in secrets manager | | Not Started / In Progress / Done |
| Ingestion method defined (batch, streaming, CDC, API) | | Not Started / In Progress / Done |
| Raw/landing zone write confirmed | | Not Started / In Progress / Done |
| Schema detection or explicit schema applied | | Not Started / In Progress / Done |
| Incremental load strategy implemented (if applicable) | | Not Started / In Progress / Done |

Notes:
> _Describe any source integration decisions, trade-offs, or deviations from the design._

### 2.2 Transformation

| Item | Details | Status |
|------|---------|--------|
| Transformation framework selected (e.g., dbt, Spark) | | Not Started / In Progress / Done |
| Staging/intermediate models implemented | | Not Started / In Progress / Done |
| Business logic matches approved specification | | Not Started / In Progress / Done |
| Naming conventions followed per team standards | | Not Started / In Progress / Done |
| Slowly changing dimensions handled (if applicable) | | Not Started / In Progress / Done |
| Output schema matches physical data model | | Not Started / In Progress / Done |
| Materialization strategy configured (view, table, incremental) | | Not Started / In Progress / Done |

Notes:
> _Describe any transformation decisions, trade-offs, or deviations from the design._

### 2.3 Data Quality

| Item | Details | Status |
|------|---------|--------|
| DQ rules from the data contract implemented | | Not Started / In Progress / Done |
| Null/not-null constraints applied | | Not Started / In Progress / Done |
| Uniqueness constraints applied | | Not Started / In Progress / Done |
| Referential integrity checks applied | | Not Started / In Progress / Done |
| Range/format/pattern validations applied | | Not Started / In Progress / Done |
| Freshness checks configured | | Not Started / In Progress / Done |
| DQ failure handling defined (warn, error, block) | | Not Started / In Progress / Done |

Notes:
> _Describe any data quality decisions, trade-offs, or deviations from the contract._

### 2.4 Orchestration

| Item | Details | Status |
|------|---------|--------|
| Pipeline/DAG defined | | Not Started / In Progress / Done |
| Schedule configured per SLA requirements | | Not Started / In Progress / Done |
| Dependency ordering validated | | Not Started / In Progress / Done |
| Retry and timeout policies set | | Not Started / In Progress / Done |
| Failure alerting configured | | Not Started / In Progress / Done |
| Idempotency verified (safe to re-run) | | Not Started / In Progress / Done |

Notes:
> _Describe orchestration platform, schedule details, and any operational considerations._

### 2.5 Security

| Item | Details | Status |
|------|---------|--------|
| Data sensitivity and criticality classification applied | | Not Started / In Progress / Done |
| Column-level masking or redaction implemented (if required) | | Not Started / In Progress / Done |
| Row-level security implemented (if required) | | Not Started / In Progress / Done |
| Role/group grants match access control design | | Not Started / In Progress / Done |
| No hardcoded credentials in code or configuration | | Not Started / In Progress / Done |
| Encryption at rest and in transit confirmed | | Not Started / In Progress / Done |
| Audit logging enabled | | Not Started / In Progress / Done |

Notes:
> _Describe any security decisions, trade-offs, or deviations from the design._

---

## 3. Code Review

| Item | Status |
|------|--------|
| Code review completed (see Code Review Sign-Off) | Pending / Done |
| All critical and high-severity findings resolved | Pending / Done |
| Reviewer(s) approved merge | Pending / Done |

- Code Review Sign-Off reference: _[link or path to completed code-review-sign-off]_

---

## 4. Unit Testing

| Item | Status |
|------|--------|
| Unit tests written for all transformation models | Pending / Done |
| Unit tests written for DQ rules | Pending / Done |
| All tests passing | Pending / Done |
| Test coverage meets minimum threshold | Pending / Done |
| Unit Test Report completed (see Unit Test Report) | Pending / Done |

- Unit Test Report reference: _[link or path to completed unit-test-report]_

---

## 5. Ready for Validate Gate

All of the following must be complete before the data product moves to Phase 5 (Validate).

| Gate Criterion | Status |
|----------------|--------|
| All development sections above marked Done | Pending / Done |
| Code review approved | Pending / Done |
| Unit tests passing | Pending / Done |
| Pipeline deployed to pre-production environment | Pending / Done |
| Pipeline executed successfully end-to-end in pre-production | Pending / Done |
| Data contract obligations met in pre-production output | Pending / Done |

**Ready for Validate decision:**

- [ ] Build phase complete --- data product is approved to proceed to Validate.

| Role | Name | Date |
|------|------|------|
| Build Lead | | |
| Data Engineer | | |
| Data Owner (or delegate) | | |
