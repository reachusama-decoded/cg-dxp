---
name: usage-analytics-report
description: |
  Report usage metrics, consumer breakdown, KPI performance, and improvement
  recommendations. Use when the user asks to "create the usage report", "how
  is this product being used", "analyze adoption", or "report on consumer
  metrics".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-8-evolve
  dependencies: []
  consumes:
    - sla-dashboard-spec
    - outcome-kpi-statement
    - data-contract
  shared-components:
    core: []
    platforms: []
---

# Usage Analytics Report

Generate a **Usage Analytics Report** for the data product described in $ARGUMENTS.

Use when the user asks to "report on usage", "analyze product adoption",
"review KPI performance", "who is using this product", or "create the
usage analytics summary for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 8 — Evolve** |
| Precedes | Downstream Impact Assessment (Phase 8), Deprecation Notice (Phase 8) |
| Depends on | SLA Dashboard Spec (Phase 7), Outcome & KPI Statement (Phase 2), Data Contract (Phase 3) |
| Gate | Usage trends inform decisions to invest, maintain, or deprecate |

The usage analytics report measures how the data product is performing against
its stated outcomes and KPIs. It breaks down usage by consumer, tracks adoption
trends, identifies underperforming areas, and recommends improvements or
deprecation based on the data.

## Instructions

1. Read the template at `templates/usage-analytics-report.md` to understand the
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
- [ ] Usage metrics are specific (query counts, unique consumers, data volume)
- [ ] KPI actuals are compared against the targets from the Outcome & KPI Statement
- [ ] Consumer breakdown includes all known consumers from the data contract
- [ ] Recommendations are actionable with specific next steps, not generic advice
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If an `outcome-kpi-statement` exists in the
  conversation, use its KPI targets as the benchmark for performance evaluation.
  If a `data-contract` exists, use the consumer registry to identify expected
  vs. actual consumers. If an `sla-dashboard-spec` exists, pull operational
  metrics from the dashboard data sources described there.

If no execution context is available, proceed normally with user-provided
information.
