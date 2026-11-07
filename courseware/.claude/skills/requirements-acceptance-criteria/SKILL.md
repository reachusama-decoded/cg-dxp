---
name: requirements-acceptance-criteria
description: |
  Define functional and non-functional requirements with testable acceptance
  criteria. Use when the user asks to "define the requirements", "write the
  acceptance criteria", "what are the ACs", or "specify what needs to be true
  for this to pass".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes:
    - consumer-use-case-map
    - demand-tracker-entry
  shared-components:
    core: []
    platforms: []
---

# Requirements & Acceptance Criteria

Generate **Requirements & Acceptance Criteria** for the data product described in $ARGUMENTS.

Use when the user asks to "define requirements", "write acceptance criteria",
"document what this product must do", "set the definition of done", or
"specify functional and non-functional requirements".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 2 — Discovery** |
| Precedes | Data Contract (Phase 3), NFR Specification (Phase 3), Build Checklist (Phase 4) |
| Depends on | Consumer Use Case Map (Phase 1), Demand Tracker Entry (Phase 1) |
| Gate | Requirements approval is required before entering Design |

Requirements and acceptance criteria bridge what consumers need (use case map)
with what engineers will build (design artifacts). Each requirement must have
testable acceptance criteria that can be verified during the Validate phase.

## Instructions

1. Read the template at `templates/requirements-acceptance-criteria.md` to understand the
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
- [ ] Each requirement has a unique ID and is categorized (functional / non-functional)
- [ ] Every requirement has at least one testable acceptance criterion
- [ ] Acceptance criteria use measurable language ("at least 99.5%") not vague ("high")
- [ ] Priority is assigned to each requirement (Must / Should / Could / Won't)
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `consumer-use-case-map` exists in the
  conversation, pull consumers and use cases from it instead of asking the user.
- **Execution results:** If `data-profiling` has run, use real column names and
  data types to inform NFR definitions.
- **Execution results:** If `discover-data` has run, use the actual schema
  information to populate data quality rules.

If no execution context is available, proceed normally with user-provided
information.
