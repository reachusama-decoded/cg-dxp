---
name: consumer-use-case-map
description: |
  Map downstream consumers, their use cases, access patterns, and SLA
  requirements. Use when the user asks to "map the consumers", "who uses this
  data", "document the use cases", or "create the consumer map".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-1-triage
  dependencies: []
  consumes:
    - demand-tracker-entry
  shared-components:
    core: []
    platforms: []
---

# Consumer Use Case Map

Generate a **Consumer Use Case Map** for the data product described in $ARGUMENTS.

Use when the user asks to "map consumers", "identify downstream users",
"document use cases for this data product", "list who needs this data",
or "define consumer SLA requirements".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 1 — Triage** |
| Precedes | All Discovery artifacts (Phase 2), especially Requirements & Acceptance Criteria |
| Depends on | Demand Tracker Entry (Phase 1) |
| Gate | Consumer map feeds into priority and feasibility decisions |

The consumer use case map captures who will consume the data product, how they
will use it, and what service levels they require. It is a key input to the
data contract and SLA design in Phase 3.

## Instructions

1. Read the template at `templates/consumer-use-case-map.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — no numbering prefixes, no extra words.
   The output **must** contain these four H2 sections in order:
   - `## Consumer Summary` — table with columns: #, Consumer / Team,
     Primary Use Case, Access Pattern, Freshness Need, Priority
   - `## Detailed Use Cases` — repeatable subsections (### UC-1, ### UC-2, etc.)
     each with table (columns: Field, Details) and Notes paragraph
   - `## Overlapping Needs` — table with columns: Need / Pattern,
     Consumers Sharing It, Design Implication
   - `## Open Questions` — table with columns: #, Question, Owner, Status
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] At least one consumer is identified with team and contact information
- [ ] Each consumer has at least one use case with a concrete description
- [ ] Access patterns specify method (SQL, API, dashboard, file) not just "read"
- [ ] SLA requirements have numeric targets, not qualitative descriptions
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `demand-tracker-entry` exists in the
  conversation, pull the product name, domain, and requestor from it instead
  of asking the user.
- **Execution results:** If `discover-data` has run, use the discovered tables
  and schemas to inform access patterns and volume estimates.

If no execution context is available, proceed normally with user-provided
information.
