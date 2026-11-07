---
name: integration-blueprint
description: |
  Document source systems, integration patterns, error handling, and downstream
  targets. Use when the user asks to "create the integration blueprint", "map
  the source systems", "document the integration pattern", or "design the
  data flow".
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

# Integration Blueprint

Generate an **Integration Blueprint** for the data product described in $ARGUMENTS.

Use when the user asks to "design the integration", "map source systems",
"document how data flows in", "define ingestion patterns", or "specify
error handling and retry logic for this pipeline".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Build Checklist (Phase 4), Schedule & Backfill Plan (Phase 3) |
| Depends on | Data Contract (Phase 3), Requirements & Acceptance Criteria (Phase 2) |
| Gate | Integration design review is part of the Design gate |

The integration blueprint documents how data enters and leaves the product.
It identifies source systems, integration patterns (batch, streaming, CDC),
error handling strategies, and downstream delivery targets.

## Instructions

1. Read the template at `templates/integration-blueprint.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — numbered prefixes are required.
   The output **must** contain these H2 sections in order:
   - `## 1. Overview` — Field/Value table with rows: Product Name,
     Integration Complexity, Total Source Integrations, Total Consumer
     Integrations, Classification
   - `## 2. Integration Inventory` — two sub-sections:
     - `### 2.1 Source Integrations (Inbound)` (columns: Source, Direction,
       Protocol, Auth Method, Frequency, Format, Owner, SLA Dependency)
     - `### 2.2 Consumer Integrations (Outbound)` (columns: Consumer,
       Direction, Protocol, Auth Method, Frequency, Format, Owner, SLA
       Commitment)
   - `## 3. Data Flow Description` — two sub-sections:
     - `### 3.1 Inbound Flows` — descriptive bullet points per source
       covering trigger, extraction method, landing zone, preprocessing,
       idempotency, and volume
     - `### 3.2 Outbound Flows` — descriptive bullet points per consumer
       covering delivery method, trigger, format, and access control
   - `## 4. Error Handling` — two sub-sections:
     - `### 4.1 Inbound Error Handling` (columns: Error Type, Detection,
       Response, Recovery)
     - `### 4.2 Outbound Error Handling` (columns: Error Type, Detection,
       Response, Recovery)
   - `## 5. SLA Dependencies` — table with columns: This Product's SLA,
     Depends On, Upstream SLA, Gap / Risk
   - `## 6. End-to-End Sequence Diagram` — Mermaid `sequenceDiagram` block
     showing source-to-consumer data flow
   - `## 7. Integration Testing Plan` — table with columns: Test Scenario,
     Description, Frequency, Owner
   - `## Appendix: Revision History` — table with columns: Version, Date,
     Author, Summary of Changes (no numbering prefix on this heading)
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Every source system has a named owner and connectivity method
- [ ] Integration patterns are specific (batch/CDC/API/streaming), not "TBD"
- [ ] Error handling specifies retry counts, dead-letter queues, or alerting
- [ ] Downstream targets list actual table/API/file paths, not placeholders
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-contract` exists in the conversation,
  use it to populate downstream targets and interface definitions. If a
  `requirements-acceptance-criteria` exists, use its NFRs to set error handling
  and retry requirements.

If no execution context is available, proceed normally with user-provided
information.
