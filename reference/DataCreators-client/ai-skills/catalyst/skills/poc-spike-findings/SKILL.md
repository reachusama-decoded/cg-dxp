---
name: poc-spike-findings
description: |
  Document PoC or spike findings with approach, results, and recommendations.
  Use when the user asks to "document the spike", "write up the PoC results",
  "record what we learned", or "summarize the proof of concept".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes:
    - feasibility-report
  shared-components:
    core: []
    platforms: []
---

# PoC / Spike Findings

Generate a **PoC / Spike Findings** document for the data product described in $ARGUMENTS.

Use when the user asks to "document spike results", "write up PoC findings",
"summarize the proof of concept", "record what we learned from the spike",
or "capture experimental findings for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 2 — Discovery** |
| Precedes | Business Case (Phase 2), Design artifacts (Phase 3) |
| Depends on | Feasibility Report (Phase 2) — spike addresses its unknowns |
| Gate | Findings inform go/no-go decision and design approach |

This artifact is produced when a feasibility report identifies significant
unknowns that require hands-on validation. The PoC/spike is time-boxed and
its findings feed back into the feasibility assessment and business case.

## Instructions

1. Read the template at `templates/poc-spike-findings.md` to understand the
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
- [ ] The hypothesis or question being tested is explicitly stated
- [ ] Approach describes what was actually done, not what was planned
- [ ] Results include concrete data (metrics, timings, counts), not just opinions
- [ ] A clear recommendation is stated (proceed / pivot / abandon)
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `feasibility-report` exists in the
  conversation, reference its uncertain areas to frame what the PoC/spike was
  designed to validate.
- **Execution results:** If `data-profiling` or `discover-data` has run,
  reference their findings as supporting evidence for the PoC results and
  conclusions.

If no execution context is available, proceed normally with user-provided
information.
