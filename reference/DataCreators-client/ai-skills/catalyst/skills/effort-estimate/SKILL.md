---
name: effort-estimate
description: |
  Estimate effort with work breakdown, assumptions, and risks. Use when the
  user asks to "estimate the effort", "how long will this take", "create the
  work breakdown", "size this project", or "estimate person-days".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes:
    - demand-tracker-entry
    - feasibility-report
  shared-components:
    core: []
    platforms: []
---

# Effort Estimate

Generate an **Effort Estimate** for the data product described in $ARGUMENTS.

Use when the user asks to "estimate the effort", "size this work", "create a
work breakdown", "how long will this take", or "what resources do we need for
this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 2 — Discovery** |
| Precedes | Business Case (Phase 2), Design artifacts (Phase 3) |
| Depends on | Demand Tracker Entry (Phase 1), Feasibility Report (Phase 2) |
| Gate | Effort estimate feeds into business case and funding decisions |

The effort estimate provides a structured breakdown of work, assumptions, and
risks. It is a key input to the business case and is used to set expectations
with stakeholders on timeline and resource needs.

## Instructions

1. Read the template at `templates/effort-estimate.md` to understand the
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
- [ ] Work breakdown has specific tasks with hour or day estimates
- [ ] Assumptions are listed and each has an owner who can validate it
- [ ] Risks include probability and impact ratings, not just descriptions
- [ ] Total effort is summed and a confidence range is stated
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `demand-tracker-entry` exists in the
  conversation, pull classification and priority from it to scope the effort.
  If a `feasibility-report` exists, use its feasibility assessment to surface
  relevant risks and assumptions in the estimate.

If no execution context is available, proceed normally with user-provided
information.
