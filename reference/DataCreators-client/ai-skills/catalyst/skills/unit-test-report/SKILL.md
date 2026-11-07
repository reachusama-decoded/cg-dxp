---
name: unit-test-report
description: |
  Summarize unit test coverage, categories, and notable findings. Use when the
  user asks to "write the test report", "document unit test results", "create
  the test summary", or "record test coverage".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes:
    - build-checklist
  shared-components:
    core: []
    platforms: []
---

# Unit Test Report

Generate a **Unit Test Report** for the data product described in $ARGUMENTS.

Use when the user asks to "summarize unit tests", "document test coverage",
"create the unit test report", "what tests did we write", or "report on test
results for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 4 — Build** |
| Precedes | Integration Test Report (Phase 4), Validate gate |
| Depends on | Build Checklist (Phase 4) — tests are written during Build |
| Gate | Unit test pass rate and coverage must meet minimum thresholds |

The unit test report summarizes test coverage across transformation logic, data
quality rules, and business rule validation. It is referenced by the build
checklist as a gate criterion for entering Validate.

## Instructions

1. Read the template at `templates/unit-test-report.md` to understand the
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
- [ ] Coverage percentage is stated for each test category
- [ ] Test categories align with the build checklist sections (transformation, DQ, etc.)
- [ ] Notable findings describe actual issues found, not generic statements
- [ ] Pass/fail counts and overall pass rate are calculated
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `transformation-spec` exists in the
  conversation, verify that unit tests cover all documented business rules. If
  a `data-contract` exists, verify that DQ rule tests align with the contract's
  quality rules.

If no execution context is available, proceed normally with user-provided
information.
