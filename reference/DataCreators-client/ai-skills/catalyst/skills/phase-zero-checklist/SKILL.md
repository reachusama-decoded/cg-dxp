---
name: phase-zero-checklist
description: |
  Verify organizational prerequisites before entering Triage — roles,
  infrastructure, demand tracker readiness. Use when the user asks to "run the
  prereq check", "are we ready to start", "check phase zero", or "verify
  organizational readiness".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-0-prereq
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: []
---

# Phase Zero Checklist

Generate a **Phase Zero Checklist** for the data product described in $ARGUMENTS.

Use when the user asks to "check prerequisites", "verify we're ready for triage",
"confirm Phase 0 gates", "run the readiness checklist", or "validate org
readiness for a new data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 0 — Pre-requisite** |
| Precedes | Phase 1 (Triage): Demand Tracker Entry, Consumer Use Case Map |
| Depends on | None — this is the entry point |
| Gate | All conditions must be met before entering Triage |

This artifact is not per-product — it confirms organizational readiness each
time a new product request is raised. If it was recently completed and nothing
has changed, reference the prior checklist rather than regenerating.

## Instructions

1. Read the template at `templates/phase-zero-checklist.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — no numbering prefixes, no extra words.
   The output **must** contain these three H2 sections in order:
   - `## Roles` — table with columns: #, Condition, Met, Name / Reference,
     Notes. Covers Data Owner, Data Product Creator, Data Product Manager,
     Data Stewards.
   - `## Organizational Infrastructure` — table with columns: #, Condition,
     Met, Reference, Notes. Covers demand tracker, approved pattern registry,
     Catalyst repo access.
   - `## Determination` — table with columns: Field, Value. Includes
     "All conditions met?", "If No — blocker(s)", "Next action",
     "Confirmed by", "Date".
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] All conditions in the Roles table have a clear Met/Not Met status
- [ ] All conditions in the Organizational Infrastructure table have a clear status
- [ ] The Determination section states a concrete next action
- [ ] Every "Not Met" condition has an owner and remediation path in Notes

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If the user has already provided team information
  in a prior message, use it to pre-fill the Roles section instead of asking.

If no execution context is available, proceed normally with user-provided
information.
