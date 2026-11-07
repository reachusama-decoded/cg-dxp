---
name: business-case
description: |
  Build a business case with cost/benefit analysis, alternatives, and strategic
  alignment. Use when the user asks to "write the business case", "justify this
  project", "build the cost-benefit analysis", or "make the case for this
  data product".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes:
    - demand-tracker-entry
    - feasibility-report
    - effort-estimate
  shared-components:
    core: []
    platforms: []
---

# Business Case

Generate a **Business Case** for the data product described in $ARGUMENTS.

Use when the user asks to "build a business case", "justify this data product",
"write a cost-benefit analysis", "make the case for funding", or "show the ROI
for this initiative".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 2 — Discovery** |
| Precedes | Design artifacts (Phase 3) — used to secure approval to proceed |
| Depends on | Demand Tracker Entry (Phase 1), Feasibility Report, Effort Estimate |
| Gate | Business case approval is required before entering Design |

The business case consolidates feasibility, effort, and strategic alignment into
a decision document. It is typically the last Discovery artifact produced before
the gate review.

## Instructions

1. Read the template at `templates/business-case.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — numbered prefixes are required for headings
   1–6, no extra words. The output **must** contain these eight H2 sections in order:
   - `## Executive Summary` — paragraph text
   - `## 1. Problem Statement` — subsections: Current State, Future State
   - `## 2. Value` — subsections with tables: Quantitative Value (columns:
     Value Driver, Current Cost / Loss, Projected Improvement, Timeframe),
     Qualitative Value (bullet list)
   - `## 3. Cost to Build` — table with columns: Cost Category, Estimate, Notes
   - `## 4. Alternatives Considered` — table with columns: Alternative, Pros,
     Cons, Why Not Selected
   - `## 5. Strategic Alignment` — paragraph text
   - `## 6. Recommendation` — paragraph text
   - `## Approvals` — table with columns: Role, Name, Date, Decision
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending AAAS/BLLS decision
   (per proposal)" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Cost estimates include specific dollar amounts or ranges, not "TBD"
- [ ] Benefit projections are quantified with measurable outcomes
- [ ] At least two alternatives are evaluated (including "do nothing")
- [ ] Strategic alignment references specific initiatives or OKRs
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `demand-tracker-entry` exists in the
  conversation, pull classification and priority from it to anchor the
  strategic alignment section. If a `feasibility-report` exists, use its
  feasibility assessment to support the options analysis.

If no execution context is available, proceed normally with user-provided
information.
