---
name: consumer-onboarding-guide
description: |
  Create a consumer onboarding guide with prerequisites, datasets, example
  queries, and support contacts. Use when the user asks to "write the onboarding
  guide", "create consumer documentation", "how do consumers access this
  product", or "document the getting started steps".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-6-publish
  dependencies: []
  consumes:
    - data-contract
    - uat-sign-off
    - deployment-record
  shared-components:
    core: []
    platforms: []
---

# Consumer Onboarding Guide

Generate a **Consumer Onboarding Guide** for the data product described in $ARGUMENTS.

Use when the user asks to "write the onboarding guide", "create consumer
documentation", "help users get started with this product", "document how to
access and use this data", or "write the getting-started guide".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 6 — Publish** |
| Precedes | Usage Analytics Report (Phase 8) — onboarding quality affects adoption |
| Depends on | Data Contract (Phase 3), UAT Sign-Off (Phase 5), Deployment Record (Phase 6) |
| Gate | Onboarding guide must be published before consumers are notified of availability |

The consumer onboarding guide is the primary documentation for new consumers. It
covers prerequisites, available datasets and endpoints, example queries, SLA
expectations, access request processes, and support channels.

## Instructions

1. Read the template at `templates/consumer-onboarding-guide.md` to understand the
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
- [ ] Prerequisites list specific tools, permissions, and access groups
- [ ] Example queries are syntactically valid and runnable
- [ ] Dataset descriptions match the data contract schema
- [ ] Support contacts are named with actual channels (not "[Contact]")
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `data-contract` exists in the conversation,
  pull the schema and SLA sections to populate dataset descriptions and
  expectations. If a `consumer-use-case-map` exists, tailor examples to actual
  consumer use cases. If a `deployment-record` exists, use it for endpoint
  URLs and access methods.

If no execution context is available, proceed normally with user-provided
information.
