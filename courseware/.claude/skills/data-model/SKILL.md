---
name: data-model
description: |
  Design conceptual, logical, and physical data models with data dictionary.
  Use when the user asks to "create the data model", "design the schema",
  "draw the ER diagram", "define the tables and relationships", or "document
  the physical model".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - data-contract
    - requirements-acceptance-criteria
  shared-components:
    core: []
    platforms: []
---

# Data Model

Generate a **Data Model** for the data product described in $ARGUMENTS.

Use when the user asks to "design the data model", "create an ER diagram",
"define the schema", "document entities and relationships", or "build the
logical and physical model for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Transformation Spec (Phase 3), Build Checklist (Phase 4) |
| Depends on | Data Contract (Phase 3), Requirements & Acceptance Criteria (Phase 2) |
| Gate | Data model approval is part of the Design gate review |

The data model defines the conceptual, logical, and physical structures that
the data product will use. It drives the transformation spec, build
implementation, and serves as a reference for ongoing schema evolution.

## Instructions

1. Read the template at `templates/data-model.md` to understand the
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
- [ ] Every entity has at least a primary key and one business attribute defined
- [ ] Relationships specify cardinality (1:1, 1:N, M:N) and join keys
- [ ] Physical model includes data types, nullable flags, and partitioning strategy
- [ ] Data dictionary covers all columns across all entities
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-contract` exists in the conversation,
  pull schema definitions from it. If a `requirements-acceptance-criteria`
  exists, pull NFRs to guide physical model decisions.
- **Execution results:** If the `data-modeling` execution skill has run, use
  its ER diagram and DDL output directly instead of generating from scratch.
- **Execution results:** If `discover-data` has run, use the real source table
  schemas to ground the logical model in actual source structures.

If no execution context is available, proceed normally with user-provided
information.
