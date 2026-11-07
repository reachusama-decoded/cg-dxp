---
name: deprecation-notice
description: |
  Create a deprecation notice with scope, timeline, migration checklist, and
  rollback plan. Use when the user asks to "deprecate this product", "write
  the deprecation notice", "plan the sunset", or "notify consumers of
  retirement".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-8-evolve
  dependencies: []
  consumes:
    - downstream-impact-assessment
    - usage-analytics-report
  shared-components:
    core: []
    platforms: []
---

# Deprecation Notice

Generate a **Deprecation Notice** for the data product described in $ARGUMENTS.

Use when the user asks to "deprecate this product", "create a sunset notice",
"notify consumers about decommission", "write the deprecation plan", or
"document the end-of-life for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 8 — Evolve** |
| Precedes | Product decommission — no further lifecycle artifacts |
| Depends on | Downstream Impact Assessment (Phase 8), Usage Analytics Report (Phase 8) |
| Gate | Deprecation notice must be approved and communicated before decommission begins |

The deprecation notice formally communicates that a data product is being
retired. It includes the reason, timeline, affected consumers, migration path,
data archival plan, and support window. All consumers must be notified and given
adequate time to migrate before decommission.

## Instructions

1. Read the template at `templates/deprecation-notice.md` to understand the
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
- [ ] Timeline has specific dates for each milestone (announcement, freeze, decommission)
- [ ] Every known consumer is listed with migration status and contact info
- [ ] Migration path is concrete (replacement product named, or "no replacement" stated)
- [ ] Data archival plan specifies retention period, format, and location
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `downstream-impact-assessment` exists in the
  conversation, pull the consumer list and impact ratings from it. If a
  `data-contract` exists, reference the consumer registry for the affected
  consumer list. If a `usage-analytics-report` exists, use declining usage
  as supporting rationale for deprecation.

If no execution context is available, proceed normally with user-provided
information.
