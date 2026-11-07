---
name: downstream-impact-assessment
description: |
  Assess downstream consumer impact from proposed changes, with risk ratings
  and communication plan. Use when the user asks to "assess the impact",
  "who will be affected by this change", "create the impact assessment", or
  "evaluate downstream risk".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-8-evolve
  dependencies: []
  consumes:
    - data-contract
    - usage-analytics-report
  shared-components:
    core: []
    platforms: []
---

# Downstream Impact Assessment

Generate a **Downstream Impact Assessment** for the data product described in $ARGUMENTS.

Use when the user asks to "assess downstream impact", "evaluate change impact",
"what consumers are affected by this change", "run an impact analysis", or
"document who breaks if we change this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 8 — Evolve** |
| Precedes | Deprecation Notice (Phase 8), Release Notes for major changes (Phase 6) |
| Depends on | Data Contract (Phase 3) — consumer registry and schema, Usage Analytics Report (Phase 8) |
| Gate | Impact assessment must be reviewed before any breaking change is deployed |

The downstream impact assessment evaluates how a proposed change (schema
modification, deprecation, SLA change, or decommission) affects consumers. It
assigns risk ratings per consumer, defines a communication plan, and identifies
migration requirements.

## Instructions

1. Read the template at `templates/downstream-impact-assessment.md` to understand the
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
- [ ] The proposed change is described in specific, unambiguous terms
- [ ] Every consumer from the data contract registry is assessed
- [ ] Risk ratings have both likelihood and severity, not just a single score
- [ ] Communication plan has specific dates and channels for each consumer
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-contract` exists in the conversation,
  pull the consumer registry and change management rules from it. If a
  `usage-analytics-report` exists, use actual usage patterns to assess which
  consumers are most affected. If a `consumer-use-case-map` exists, understand
  how each consumer uses the data to evaluate impact severity.

If no execution context is available, proceed normally with user-provided
information.
