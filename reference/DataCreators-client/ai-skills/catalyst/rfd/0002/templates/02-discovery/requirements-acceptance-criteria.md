---
phase: "Intake & Discovery"
artifact: "Requirements & Acceptance Criteria"
data_product: "[Product Name]"
date_created: "YYYY-MM-DD"
last_updated: "YYYY-MM-DD"
---

# Requirements & Acceptance Criteria

The Data Product Manager (DPM) owns this document. It captures functional and
non-functional requirements, data quality rules, and testable acceptance criteria.

> **Note:** This is a living document. Initial requirements are captured during
> Intake & Discovery and refined throughout Design, Build, and Validate phases.

---

## Functional Requirements

| ID     | Requirement                              | Priority        | Source             | Status   |
|--------|------------------------------------------|-----------------|--------------------|----------|
| FR-001 |                                          | _Must / Should / Could / Won't_ |      |          |
| FR-002 |                                          |                 |                    |          |
| FR-003 |                                          |                 |                    |          |

## Non-Functional Requirements

| ID     | Category       | Requirement                              | Target               | Measurement Method   |
|--------|----------------|------------------------------------------|-----------------------|----------------------|
| NFR-001| Freshness      |                                          |                       |                      |
| NFR-002| Completeness   |                                          |                       |                      |
| NFR-003| Availability   |                                          |                       |                      |
| NFR-004| Latency        |                                          |                       |                      |
| NFR-005| Volume         |                                          |                       |                      |
| NFR-006| Sensitivity    |                                          |                       |                      |
| NFR-007| Criticality    |                                          |                       |                      |

## Data Quality Rules

| ID     | Field / Entity  | Rule Description                         | Severity        | Enforcement Point    |
|--------|-----------------|------------------------------------------|-----------------|-----------------------|
| DQ-001 |                 |                                          | _Block / Warn / Log_ |                  |
| DQ-002 |                 |                                          |                 |                       |
| DQ-003 |                 |                                          |                 |                       |

## Acceptance Criteria

Each criterion must be **testable** and **agreed upon before build begins**.

| ID     | Linked Req(s)  | Criterion (Given / When / Then)          | Verification Method  | Agreed? |
|--------|----------------|------------------------------------------|----------------------|---------|
| AC-001 |                |                                          |                      | _Y / N_ |
| AC-002 |                |                                          |                      | _Y / N_ |
| AC-003 |                |                                          |                      | _Y / N_ |

## Out of Scope

Explicitly list what is **not** included in this product or iteration.

| #  | Item                                            | Rationale              |
|----|-------------------------------------------------|------------------------|
| 1  |                                                 |                        |
| 2  |                                                 |                        |

## Open Questions

| #  | Question                                        | Owner          | Status   | Resolution |
|----|-------------------------------------------------|----------------|----------|------------|
| 1  |                                                 |                |          |            |
| 2  |                                                 |                |          |            |

---

## Completeness Check

All items below must be checked before this document is considered complete.

- [ ] Every functional requirement has a stated priority (Must Have / Should Have / Nice to Have)
- [ ] Every acceptance criterion is testable (has a concrete pass/fail condition, not just a description)
- [ ] Every acceptance criterion has a linked verification method (how it will be tested)
- [ ] All NFRs have numeric targets (not "fast" or "reliable" — specific thresholds)
- [ ] All DQ rules have a severity level and an action on breach
- [ ] Out-of-scope items are explicitly listed (not left blank)
- [ ] All open questions have an assigned owner and a decision-needed-by date

---

## Revision History

| Date       | Author         | Changes                                  |
|------------|----------------|------------------------------------------|
|            |                |                                          |
