---
name: integration-test-report
description: |
  Document integration test scenarios, performance results, and pass/fail
  status. Use when the user asks to "write the integration test report",
  "document end-to-end test results", "create the test report", or "record
  integration testing".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes:
    - build-checklist
    - unit-test-report
  shared-components:
    core: []
    platforms: []
---

# Integration Test Report

Generate an **Integration Test Report** for the data product described in $ARGUMENTS.

Use when the user asks to "document integration tests", "report end-to-end test
results", "create the integration test summary", "record pipeline test outcomes",
or "verify the full pipeline works for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 4 — Build** |
| Precedes | Data Quality Sign-Off (Phase 5), UAT Sign-Off (Phase 5) |
| Depends on | Build Checklist (Phase 4), Unit Test Report (Phase 4) |
| Gate | Integration tests must pass before entering Validate |

The integration test report documents end-to-end pipeline testing — from source
ingestion through transformation to serving layer output. It validates that
components work together and performance meets NFR thresholds.

## Instructions

1. Read the template at `templates/integration-test-report.md` to understand the
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
- [ ] Test scenarios cover the full pipeline path (source to serving layer)
- [ ] Performance results include specific metrics (duration, row counts, throughput)
- [ ] Each test has a clear Pass/Fail result with actual vs. expected values
- [ ] Failed tests have documented root cause and resolution or accepted risk
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `build-checklist` exists in the conversation,
  use it to identify the pipeline components that need integration testing. If
  an `nfr-specification` exists, use its performance thresholds as the pass/fail
  criteria. If a `schedule-backfill-plan` exists, verify backfill scenarios
  were tested.

If no execution context is available, proceed normally with user-provided
information.
