---
name: transformation-spec
description: |
  Specify model topology, materialization decisions, and backfill strategy for
  a data product. Use when the user asks to "document the transformations",
  "write the transformation spec", "specify data lineage", or "map the model
  topology for this data product".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - data-model
    - data-contract
  shared-components:
    core: []
    platforms: []
---

# Transformation Spec

Generate a **Transformation Spec** for the data product described in $ARGUMENTS.

Use when the user asks to "define the transformations", "document the
transformation spec", "specify data lineage", or "map the model topology
for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Build Checklist (Phase 4), Unit Test Report (Phase 4) |
| Depends on | Data Model (Phase 3), Data Contract (Phase 3) |
| Gate | Transformation spec review is part of the Design gate |

The transformation spec defines how source data is converted into the target
data model. It documents model topology, materialization decisions, and the
backfill strategy. Per-column quality rules and business rules live in the
data contract (`contract/contract.yaml`, RFD 0009); transformation logic
lives in dbt SQL.

## Instructions

1. Read the template at `templates/transformation-spec.md` to understand the
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
- [ ] Every model in the Model Map has a corresponding Model Details section
- [ ] Materialization choice is specified for each model
- [ ] Incremental models have an Incremental Strategy, Unique Key, and Partition/Cluster entry
- [ ] Backfill Strategy is complete with a historical range and rollback plan
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-model` exists in the conversation, pull
  target entities and model names from it to populate the Model Map and Model
  Details sections. If a `data-contract` exists, use it to confirm model grain
  and source references.
- **Execution results:** If `column-lineage` has run, use its lineage mapping
  to fill in Source Model(s) fields in the Model Details section.
- **Execution results:** If `discover-data` has run, use the real source schemas
  to confirm source model references and materialization choices.

If no execution context is available, proceed normally with user-provided
information.
