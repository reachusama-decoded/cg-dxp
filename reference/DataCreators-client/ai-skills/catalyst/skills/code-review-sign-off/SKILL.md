---
name: code-review-sign-off
description: |
  Record code review findings, resolutions, and sign-off. Use when the user asks
  to "document the code review", "create the review sign-off", "record review
  findings", or "sign off on the code review".
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

# Code Review Sign-Off

Generate a **Code Review Sign-Off** for the data product described in $ARGUMENTS.

Use when the user asks to "document the code review", "record review findings",
"create the code review sign-off", "summarize PR feedback", or "sign off on the
code review for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 4 — Build** |
| Precedes | Integration Test Report (Phase 4), Validate gate |
| Depends on | Build Checklist (Phase 4) — code must be written before review |
| Gate | Code review approval is required before merging and proceeding to Validate |

The code review sign-off records what was reviewed, findings by severity,
how each finding was resolved, and who approved the merge. It is referenced
by the build checklist as a gate criterion.

## Instructions

1. Read the template at `templates/code-review-sign-off.md` to understand the
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
- [ ] Every finding has a severity level and resolution status
- [ ] Critical and high-severity findings are resolved, not just acknowledged
- [ ] Reviewer names and dates are recorded
- [ ] The sign-off decision is explicit (Approved / Approved with Conditions / Rejected)
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `build-checklist` exists in the conversation,
  reference the specific code components that were reviewed. If a
  `transformation-spec` or `security-design` exists, verify the review covered
  alignment with those specifications.

If no execution context is available, proceed normally with user-provided
information.
