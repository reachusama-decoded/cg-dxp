---
name: sla-dashboard-spec
description: |
  Specify SLA monitoring dashboard: panels, data sources, alert thresholds, and
  access controls. Use when the user asks to "design the SLA dashboard",
  "create the monitoring spec", "define the alert thresholds", or "specify
  the ops dashboard".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-7-operate
  dependencies: []
  consumes:
    - data-contract
    - nfr-specification
    - outcome-kpi-statement
  shared-components:
    core: []
    platforms: []
---

# SLA Dashboard Specification

Generate an **SLA Dashboard Specification** for the data product described in $ARGUMENTS.

Use when the user asks to "design the monitoring dashboard", "spec the SLA
dashboard", "define what panels we need", "create the observability spec",
or "document how we'll track SLAs for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 7 — Operate** |
| Precedes | Usage Analytics Report (Phase 8) — dashboard data feeds analytics |
| Depends on | Data Contract (Phase 3), NFR Specification (Phase 3), Outcome & KPI Statement (Phase 2) |
| Gate | Dashboard should be operational before the warranty period begins |

The SLA dashboard specification defines the panels, data sources, alert
thresholds, and access controls for the monitoring dashboard. It translates the
data contract SLAs and outcome KPIs into observable, actionable metrics.

## Instructions

1. Read the template at `templates/sla-dashboard-spec.md` to understand the
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
- [ ] Every SLA from the data contract has a corresponding dashboard panel
- [ ] Data sources are specific (table, metric endpoint, log query)
- [ ] Alert thresholds align with the data contract breach definitions
- [ ] Access controls specify who can view and who can edit the dashboard
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-contract` exists in the conversation,
  derive panels from its SLA targets and breach response table. If an
  `outcome-kpi-statement` exists, include business KPI panels alongside
  operational SLA panels. If an `nfr-specification` exists, include performance
  metrics panels.

If no execution context is available, proceed normally with user-provided
information.
