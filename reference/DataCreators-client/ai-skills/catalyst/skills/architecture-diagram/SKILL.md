---
name: architecture-diagram
description: |
  Generate architecture diagrams for a data product — data flow, storage layout,
  infrastructure, and failure modes. Use when the user asks to "create the
  architecture diagram", "draw the data flow", "diagram the pipeline",
  "show the system architecture", or "map the infrastructure".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - requirements-acceptance-criteria
    - data-contract
    - data-model
  shared-components:
    core: []
    platforms: []
---

# Architecture Diagram

Generate an **Architecture Diagram** for the data product described in $ARGUMENTS.

Use when the user asks to "draw the architecture", "create a data flow diagram",
"map the infrastructure", "diagram the pipeline", or "show how components
connect for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Build Checklist (Phase 4), Runbook (Phase 7) |
| Depends on | Requirements & Acceptance Criteria (Phase 2), Data Contract, Data Model (Phase 3) |
| Gate | Architecture review must approve before entering Build |

The architecture diagram is a visual companion to the integration blueprint and
data model. It shows how data flows from source to serving layer, identifies
infrastructure components, and documents failure modes at each stage.

## Instructions

1. Read the template at `templates/architecture-diagram.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Include **all** headings and
   subheadings from the template at level H2 or deeper, in the same order and
   with the exact text shown there — numbered prefixes are required, with no
   extra or substituted words. In particular, the output **must** include:
   - `## 1. Overview` — table with columns: Field, Value
   - `### Summary` — required subsection under `## 1. Overview`
   - `## 2. End-to-End Architecture` — Mermaid or ASCII diagram of the full pipeline
   - `## 3. Component Descriptions` — table with columns: Component, Technology / Service, Purpose, Owner
   - `## 4. Infrastructure Requirements` — table with columns: Requirement, Specification, Notes
   - `## 5. Failure Modes & Recovery` — table with columns: Failure Scenario, Impact, Detection Method, Recovery Strategy, RTO
   - `## 6. Deviations from Existing Patterns` — table with columns: Area, Approved Pattern, This Product's Deviation, Justification
   - `## Appendix: Revision History` — table with columns: Version, Date, Author, Summary of Changes
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Every component in the diagram has a named technology or service
- [ ] Data flow directions are explicit (source to target, not ambiguous arrows)
- [ ] Failure modes are documented for each critical component
- [ ] Mermaid or ASCII diagrams render correctly with no syntax errors
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `requirements-acceptance-criteria` exists in
  the conversation, pull NFRs to inform infrastructure sizing. If a
  `data-contract` or `data-model` exists, use them to identify components and
  data flows that must appear in the diagram.

If no execution context is available, proceed normally with user-provided
information.
