---
name: data-quality-sign-off
description: |
  Record DQ validation results and sign-off from data owner and engineering
  leads. Use when the user asks to "sign off on data quality", "document the
  DQ results", "create the quality sign-off", or "record validation results".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-5-validate
  dependencies: []
  consumes:
    - data-contract
    - build-checklist
    - unit-test-report
  shared-components:
    core: []
    platforms: []
---

# Data Quality Sign-Off

Generate a **Data Quality Sign-Off** for the data product described in $ARGUMENTS.

Use when the user asks to "sign off on data quality", "validate DQ results",
"create the DQ sign-off", "confirm data quality meets the contract", or
"get approval on data quality for this product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 5 — Validate** |
| Precedes | UAT Sign-Off (Phase 5), Deployment Record (Phase 6) |
| Depends on | Data Contract (Phase 3), Build Checklist (Phase 4), Unit Test Report (Phase 4) |
| Gate | DQ sign-off is required before UAT and production deployment |

The data quality sign-off formally records that DQ rules from the data contract
have been validated against actual data output, with results meeting the agreed
thresholds. It requires sign-off from the data owner and engineering lead.

## Instructions

1. Read the template at `templates/data-quality-sign-off.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names.
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Every DQ rule from the data contract has a corresponding validation result
- [ ] Results include actual metric values, not just Pass/Fail
- [ ] Any failures have documented root cause, impact, and remediation plan
- [ ] Sign-off roles and names are filled in with actual people
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-contract` exists in the conversation,
  pull the DQ rules table to verify every rule has a validation result. If a
  `unit-test-report` or `integration-test-report` exists, reference their DQ
  test results as evidence.

If no execution context is available, proceed normally with user-provided
information.
