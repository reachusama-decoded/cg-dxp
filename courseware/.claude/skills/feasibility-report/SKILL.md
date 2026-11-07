---
name: feasibility-report
description: |
  Assess technical, data availability, and regulatory feasibility for a proposed
  data product. Use when the user asks to "assess feasibility", "can we build
  this", "write the feasibility report", "evaluate technical readiness", or
  "check if this is doable".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes:
    - demand-tracker-entry
    - consumer-use-case-map
  shared-components:
    core: []
    platforms: []
---

# Feasibility Report

Generate a **Feasibility Report** for the data product described in $ARGUMENTS.

Use when the user asks to "assess feasibility", "can we build this",
"evaluate technical readiness", "check data availability", or "run a
feasibility assessment for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 2 — Discovery** |
| Precedes | Effort Estimate, Business Case, PoC/Spike Findings (Phase 2) |
| Depends on | Demand Tracker Entry (Phase 1), Consumer Use Case Map (Phase 1) |
| Gate | Feasibility must be confirmed before committing resources to Build |

The feasibility report evaluates whether the data product can be built with
available data, technology, and skills. A "not feasible" finding may redirect
the request to a PoC/Spike or cancel it entirely.

## Instructions

1. Read the template at `templates/feasibility-report.md` to understand the
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
- [ ] Each feasibility dimension (technical, data, regulatory) has a clear verdict
- [ ] Data availability assessment references specific source systems
- [ ] Risks and blockers have severity ratings and mitigation strategies
- [ ] A clear overall recommendation is stated (feasible / not feasible / conditional)
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `demand-tracker-entry` exists in the
  conversation, pull product name and classification from it. If a
  `consumer-use-case-map` exists, pull the consumer list from it.
- **Execution results:** If `discover-data` has run, use actual table names and
  access status to populate the Data Availability section.
- **Execution results:** If `data-profiling` has run, use real row counts, date
  ranges, and null rates for the data quality assessment.

If no execution context is available, proceed normally with user-provided
information.
