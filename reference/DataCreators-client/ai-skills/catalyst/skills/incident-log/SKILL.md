---
name: incident-log
description: |
  Record production incidents with severity, resolution, duration, trends, and
  action items. Use when the user asks to "log an incident", "document what
  happened", "create the incident report", or "record the outage".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-7-operate
  dependencies: []
  consumes:
    - runbook
    - sla-dashboard-spec
  shared-components:
    core: []
    platforms: []
---

# Incident Log

Generate an **Incident Log** for the data product described in $ARGUMENTS.

Use when the user asks to "log an incident", "record a production issue",
"document what went wrong", "create the incident report", or "track incidents
for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 7 — Operate** |
| Precedes | Warranty Handoff Sign-Off (Phase 7), Usage Analytics Report (Phase 8) |
| Depends on | Runbook (Phase 7), SLA Dashboard Spec (Phase 7) |
| Gate | Incident trends inform warranty handoff and evolve decisions |

The incident log is a living document that tracks all production incidents for
a data product. It captures severity, root cause, resolution, duration, and
follow-up actions. Patterns in the incident log inform runbook updates,
warranty period assessments, and deprecation decisions.

## Instructions

1. Read the template at `templates/incident-log.md` to understand the
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
- [ ] Each incident has a unique ID, timestamp, and severity classification
- [ ] Root cause analysis is specific (not just "unknown" or "infrastructure issue")
- [ ] Resolution includes what was done and time-to-resolution
- [ ] Action items have owners and due dates
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-contract` exists in the conversation,
  reference its SLA breach definitions to classify incident severity. If a
  `runbook` exists, reference the procedures that were followed (or should have
  been followed) during resolution.

If no execution context is available, proceed normally with user-provided
information.
