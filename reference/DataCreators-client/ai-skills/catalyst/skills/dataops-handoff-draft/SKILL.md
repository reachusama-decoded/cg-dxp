---
name: dataops-handoff-draft
description: |
  Draft the operational handoff package: compute, orchestration, monitoring,
  alerting, and on-call contacts. Use when the user asks to "create the
  handoff document", "draft the ops handoff", "document operational
  requirements", or "prepare the DataOps package".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - nfr-specification
    - data-contract
    - requirements-acceptance-criteria
  shared-components:
    core: []
    platforms: []
---

# DataOps Handoff Draft

Generate a **DataOps Handoff Draft** for the data product described in $ARGUMENTS.

Use when the user asks to "prepare the ops handoff", "draft the operational
handoff", "document what DataOps needs to run this", "create the handoff
package", or "define monitoring and alerting for this pipeline".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Runbook (Phase 7), Warranty Handoff Sign-Off (Phase 7) |
| Depends on | NFR Specification (Phase 3), Data Contract (Phase 3), Requirements (Phase 2) |
| Gate | DataOps handoff review is part of the Design gate |

The DataOps handoff draft captures everything the operations team needs to run
the data product in production. It is a draft during Design, finalized during
Build, and serves as the foundation for the Runbook in Phase 7.

## Instructions

1. Read the template at `templates/dataops-handoff-draft.md` to understand the
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
- [ ] Compute and infrastructure details specify actual services (not "cloud platform")
- [ ] Monitoring thresholds are numeric and aligned with the data contract SLAs
- [ ] Alerting channels and escalation contacts are named, not generic
- [ ] On-call rotation and escalation paths are documented
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `requirements-acceptance-criteria` or
  `nfr-specification` exists in the conversation, use the NFRs to populate
  monitoring thresholds and alerting targets. If a `data-contract` exists, use
  its SLAs to define operational expectations in the handoff.

If no execution context is available, proceed normally with user-provided
information.
