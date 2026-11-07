---
name: data-contract
description: |
  Define the producer-consumer contract: schema, SLAs, quality rules, access
  control, and versioning. Use when the user asks to "create the data contract",
  "define the SLAs", "write the schema agreement", "document the quality
  rules", or "set up the contract for this product".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - requirements-acceptance-criteria
    - consumer-use-case-map
  shared-components:
    core: []
    platforms: []
---

# Data Contract

Generate a **Data Contract** for the data product described in $ARGUMENTS.

Use when the user asks to "create a data contract", "define SLAs for this
product", "write a schema agreement", "document the producer-consumer
interface", or "specify data quality rules and access terms".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Build Checklist (Phase 4), Data Quality Sign-Off (Phase 5), Runbook (Phase 7) |
| Depends on | Requirements & Acceptance Criteria (Phase 2), Consumer Use Case Map (Phase 1) |
| Gate | Contract must be approved by producer and consumer representatives before Build |

The data contract is the authoritative agreement between producers and consumers.
It defines what data is provided, at what quality, and under what terms. It is
referenced throughout Build, Validate, and Operate as the source of truth for
schema, SLAs, and quality expectations.

## Instructions

1. Read the template at `templates/data-contract.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — numbered prefixes are required.
   The output **must** contain these H2 sections in order:
   - `## 1. Identity` — Field/Value table with rows: Product Name, Domain
     Catalog, Owner, Steward, Version, Effective Date, Review Cadence,
     Classification
   - `## 2. Schema` — table with columns: Column, Type, Nullable,
     Description, PII, Sensitivity, Criticality, Example
   - `## 3. Service Level Agreements (SLAs)` — two sub-sections:
     - `### 3.1 SLA Targets` (columns: Metric, Target, Measurement Method,
       Measurement Window)
     - `### 3.2 Breach Response` (columns: Severity, Definition, Response
       Time, Resolution Time, Escalation Path)
   - `## 4. Data Quality Rules` — table with columns: Rule ID, Column(s),
     Rule Description, Severity, Action on Failure
   - `## 5. Access & Security` — table with columns: Field, Value
   - `## 6. Change Management` — three sub-sections:
     - `### 6.1 Breaking Changes` (columns: Change Type, Example, Minimum
       Notice Period, Migration Support)
     - `### 6.2 Non-Breaking Changes` (bullet list)
     - `### 6.3 Versioning Policy` (columns: Field, Value)
   - `## 7. Consumer Registry` — table with columns: Consumer, Team,
     Use Case, Access Level, Contact, Onboarded Date
   - `## 8. Approvals` — table with columns: Role, Name, Date, Status
   - `## Appendix: Revision History` — table with columns: Version, Date,
     Author, Summary of Changes (no numbering prefix on this heading)
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave placeholder text.

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Schema table has at least one column defined with type, nullable, and description
- [ ] SLA targets have specific numeric thresholds (not "[X] minutes")
- [ ] Data quality rules reference specific columns and have severity levels
- [ ] Access model specifies concrete roles or groups, not generic descriptions
- [ ] Consumer registry lists at least one known consumer
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `requirements-acceptance-criteria` exists in
  the conversation, pull NFRs and data quality rules from it. If a
  `consumer-use-case-map` exists, pull consumers and SLA requirements from it.
- **Execution results:** If `data-profiling` has run, use real column types and
  statistical profiles to populate the schema section. Refer to the profiling
  checklist at `skills/data-profiling/references/PROFILING_CHECKLIST.md`
  for the quality dimensions that should inform DQ rules.
- **DQ Controls Plan (authoritative home for §4):** If a
  `data-quality-controls-plan` artifact exists in the conversation, §4 is where
  its approved controls are codified as the single source of truth. Carry each
  control's Column(s), rule description (noting the DQ dimension in the text),
  Severity, and Action on Failure into §4 — do not restate the plan as a
  competing table or re-run profiling.
- **Execution results:** If the `data-modeling` execution skill has run, use
  its generated DDL output for the schema definitions. The exemplar model at
  `skills/data-modeling/exemplar.mmd` shows the expected entity
  relationship patterns — the contract's schema should align with it.

If no execution context is available, proceed normally with user-provided
information.
