---
name: outcome-kpi-statement
description: |
  Define measurable business outcomes, KPIs, and success criteria. Use when the
  user asks to "define the KPIs", "what does success look like", "create the
  outcome statement", or "set the metrics for this product".
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

# Outcome & KPI Statement

Generate an **Outcome & KPI Statement** for the data product described in $ARGUMENTS.

Use when the user asks to "define success metrics", "set KPIs for this product",
"write outcome criteria", "how will we measure success", or "define what good
looks like for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 2 — Discovery** |
| Precedes | Business Case (Phase 2), SLA Dashboard Spec (Phase 7) |
| Depends on | Demand Tracker Entry (Phase 1), Consumer Use Case Map (Phase 1) |
| Gate | KPIs are referenced in the business case and validated during Operate |

The outcome & KPI statement ties the data product to measurable business value.
KPIs defined here are later tracked in the SLA dashboard and usage analytics
during the Operate and Evolve phases.

## Instructions

1. Read the template at `templates/outcome-kpi-statement.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — no numbering prefixes, no extra words.
   The output **must** contain these seven H2 sections in order:
   - `## Summary` — paragraph text (1-3 sentences)
   - `## Outcome 1: [Outcome Name]` — Description paragraph + KPIs table
     (columns: Metric, Baseline (Current), Target, Measurement Cadence,
     Data Source for Metric)
   - `## Outcome 2: [Outcome Name]` — same structure as Outcome 1. Add
     further `## Outcome N:` sections for each additional outcome.
   - `## Accountable Team` — table with columns: Role, Name / Team
   - `## Success Criteria for Launch` — table with columns: #, Criterion,
     How Verified
   - `## Anti-Goals` — bullet list
   - `## Stakeholder Alignment` — table with columns: Stakeholder, Role,
     Date Agreed, Notes
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Each KPI has a specific numeric target, not a qualitative goal
- [ ] Measurement methods are concrete (specific tool, query, or process)
- [ ] Baseline values are stated or have a plan to establish them
- [ ] Review cadence and responsible owner are specified for each KPI
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `demand-tracker-entry` exists in the
  conversation, pull classification and priority from it to frame the business
  context. If a `feasibility-report` exists, use its feasibility assessment to
  calibrate ambition of KPI targets.

If no execution context is available, proceed normally with user-provided
information.
