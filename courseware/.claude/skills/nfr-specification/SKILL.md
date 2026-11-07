---
name: nfr-specification
description: |
  Specify non-functional requirements: performance, scalability, reliability,
  observability, and cost constraints. Use when the user asks to "define the
  NFRs", "specify performance requirements", "document non-functional
  requirements", or "set the SLOs".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - requirements-acceptance-criteria
    - data-contract
  shared-components:
    core: []
    platforms: []
---

# NFR Specification

Generate an **NFR Specification** for the data product described in $ARGUMENTS.

Use when the user asks to "define non-functional requirements", "specify
performance targets", "document scalability needs", "set reliability SLOs",
or "write the NFR spec for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | DataOps Handoff Draft (Phase 3), Build Checklist (Phase 4) |
| Depends on | Requirements & Acceptance Criteria (Phase 2), Data Contract (Phase 3) |
| Gate | NFR approval is part of the Design gate review |

The NFR specification expands the non-functional requirements from Discovery
into formal, measurable thresholds. It drives infrastructure sizing,
monitoring configuration, and SLA commitments.

## Instructions

1. Read the template at `templates/nfr-specification.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — numbered prefixes are required.
   The output **must** contain these H2 sections in order:
   - `## 1. Overview` — Field/Value table with rows: Product Name,
     Classification, Justification for NFR Spec
   - `## 2. Performance Targets` — table with columns: Metric, Platform
     Default, This Product's Requirement, Justification
   - `## 3. Scalability` — main table with columns: Dimension, Current
     State, 12-Month Projection, Scaling Strategy; followed by:
     - `### Scaling Triggers` (columns: Trigger, Threshold, Action)
   - `## 4. Reliability & Availability` — main table with columns: Metric,
     Platform Default, This Product's Requirement; followed by:
     - `### Redundancy & Failover` (columns: Component, Redundancy Strategy,
       Failover Method)
   - `## 5. Observability Requirements` — main table with columns: Signal,
     Metric, Alert Threshold, Alert Channel; followed by:
     - `### Dashboards & Reporting` (columns: Dashboard, Purpose, Audience,
       Refresh Cadence)
   - `## 6. Cost Constraints` — table with columns: Cost Category, Monthly
     Budget, Current Estimate, Notes; followed by:
     - `### Cost Optimization Levers` (bullet list)
   - `## 7. Compliance & Auditability` — table with columns: Requirement,
     Details
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
- [ ] Every NFR has a measurable threshold (e.g., "p99 latency < 500ms")
- [ ] Performance targets align with the data contract SLA commitments
- [ ] Scalability section addresses growth projections with specific numbers
- [ ] Observability requirements name specific metrics, logs, and traces
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `requirements-acceptance-criteria` exists in
  the conversation, use it as the baseline and expand each NFR with formal
  measurable thresholds. If a `data-contract` exists, align SLA targets with
  the contract's freshness and uptime commitments.

If no execution context is available, proceed normally with user-provided
information.
