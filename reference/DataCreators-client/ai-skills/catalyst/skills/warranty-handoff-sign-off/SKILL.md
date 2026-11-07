---
name: warranty-handoff-sign-off
description: |
  Document warranty period criteria, actuals, and sign-off for transition to
  BAU operations. Use when the user asks to "sign off on warranty", "complete
  the handoff", "transition to BAU", or "close the warranty period".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-7-operate
  dependencies: []
  consumes:
    - runbook
    - incident-log
    - sla-dashboard-spec
  shared-components:
    core: []
    platforms: []
---

# Warranty Handoff Sign-Off

Generate a **Warranty Handoff Sign-Off** for the data product described in $ARGUMENTS.

Use when the user asks to "close the warranty period", "hand off to BAU ops",
"create the warranty sign-off", "transition from project to operations", or
"confirm the product is stable enough for steady-state support".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 7 — Operate** |
| Precedes | Evolve phase artifacts (Phase 8) — product enters steady-state |
| Depends on | Runbook (Phase 7), Incident Log (Phase 7), SLA Dashboard Spec (Phase 7) |
| Gate | Warranty sign-off is the final gate before the dev team steps back |

The warranty handoff sign-off documents the criteria for a successful warranty
period, actual performance during that period, and formal approval to transition
from project-mode support to BAU operations. The development team's on-call
obligations end upon sign-off.

## Instructions

1. Read the template at `templates/warranty-handoff-sign-off.md` to understand the
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
- [ ] Warranty period start and end dates are specific
- [ ] Success criteria have actual measured values, not just targets
- [ ] Incident summary references the incident log with counts and severity breakdown
- [ ] Sign-off includes actual names and decisions from both dev and ops leads
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If an `incident-log` exists in the conversation,
  summarize incident counts and trends during the warranty period. If a
  `data-contract` exists, compare actual SLA performance against contracted
  targets. If a `runbook` exists, confirm it was updated with lessons learned
  during warranty.

If no execution context is available, proceed normally with user-provided
information.
