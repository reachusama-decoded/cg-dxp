---
name: build-checklist
description: |
  Generate a build checklist tracking infrastructure, pipeline code, tests, DQ
  rules, and documentation completeness. Use when the user asks to "create the
  build checklist", "track build progress", "what needs to be done before
  we ship", or "check build readiness".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes:
    - data-contract
    - data-model
    - security-design
  shared-components:
    core: []
    platforms: []
---

# Build Checklist

Generate a **Build Checklist** for the data product described in $ARGUMENTS.

Use when the user asks to "track build progress", "create the build checklist",
"check what's left to build", "verify build readiness", or "confirm all
development tasks are complete for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 4 — Build** |
| Precedes | Data Quality Sign-Off (Phase 5), UAT Sign-Off (Phase 5) |
| Depends on | All Design artifacts (Phase 3) — especially Data Contract, Data Model, Security Design |
| Gate | All checklist items must be Done before entering Validate |

The build checklist is the master tracker for all development activities. It
covers source integration, transformation, data quality rules, orchestration,
security, code review, and unit testing. It serves as the pre-Validate gate
document.

## Instructions

1. Read the template at `templates/build-checklist.md` to understand the
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
- [ ] Pre-Build Gates reference actual approved Design artifacts with links or names
- [ ] Each development item has a concrete status (Not Started / In Progress / Done)
- [ ] Notes sections describe actual decisions, not just comment placeholders
- [ ] Code Review and Unit Test sections reference their companion artifacts
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-contract` exists in the conversation,
  use it to pre-fill the DQ rules section. If an `integration-blueprint` or
  `transformation-spec` exists, use them to populate source integration and
  transformation items. If a `security-design` exists, use it for the security
  section.

If no execution context is available, proceed normally with user-provided
information.
