---
name: runbook
description: |
  Generate an operational runbook — health checks, alert responses, escalation
  paths, maintenance schedules. Use when the user asks to "create the runbook",
  "document operational procedures", "write the ops guide", "define health
  checks and alert responses", or "prepare the operations handbook".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-7-operate
  dependencies: []
  consumes:
    - dataops-handoff-draft
    - deployment-record
    - data-contract
  shared-components:
    core: []
    platforms: []
---

# Runbook

Generate a **Runbook** for the data product described in $ARGUMENTS.

Use when the user asks to "create the runbook", "document operational
procedures", "write the ops guide", "define health checks and alert responses",
or "prepare the operations handbook for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 7 — Operate** |
| Precedes | Incident Log (Phase 7), Warranty Handoff Sign-Off (Phase 7) |
| Depends on | DataOps Handoff Draft (Phase 3), Deployment Record (Phase 6), Data Contract (Phase 3) |
| Gate | Runbook must be complete before the warranty period begins |

The runbook is the primary operational reference for DataOps. It is a living
document that covers schedule, health checks, alert responses, procedures for
common failure scenarios, escalation paths, and maintenance tasks. It is updated
after each significant incident.

## Instructions

1. Read the template at `templates/runbook.md` to understand the
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
- [ ] Health checks have specific commands or queries to run, not just descriptions
- [ ] Alert responses include concrete first-response steps, not just "check logs"
- [ ] Escalation paths name actual teams and contacts with SLA timeframes
- [ ] Procedures include runnable commands (trigger, pause, re-enable)
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `dataops-handoff-draft` exists in the
  conversation, use it as the foundation and expand with production-specific
  details. If a `data-contract` exists, align alert thresholds with the
  contract's SLA breach definitions. If a `deployment-record` exists, pull
  pipeline locations and orchestration details from it.

If no execution context is available, proceed normally with user-provided
information.
