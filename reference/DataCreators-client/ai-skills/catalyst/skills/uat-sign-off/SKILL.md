---
name: uat-sign-off
description: |
  Document UAT test scope, results, sign-off, and conditions for production
  deployment. Use when the user asks to "create the UAT sign-off", "document
  user acceptance testing", "sign off on UAT", or "record acceptance test
  results".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-5-validate
  dependencies: []
  consumes:
    - data-quality-sign-off
    - build-checklist
  shared-components:
    core: []
    platforms: []
---

# UAT Sign-Off

Generate a **UAT Sign-Off** for the data product described in $ARGUMENTS.

Use when the user asks to "run UAT", "document user acceptance testing",
"get sign-off for production", "record UAT results", or "confirm the product
is ready for release".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 5 — Validate** |
| Precedes | Deployment Record (Phase 6), Release Notes (Phase 6) |
| Depends on | Data Quality Sign-Off (Phase 5), Build Checklist (Phase 4) |
| Gate | UAT approval is required before production deployment |

The UAT sign-off records that the data product meets business expectations from
the consumer perspective. It covers test scenarios, business logic validation,
data completeness, consumer access verification, and formal approval. Critical
issues must be resolved before sign-off.

## Instructions

1. Read the template at `templates/uat-sign-off.md` to understand the
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
- [ ] Test scenarios have actual results, not empty columns
- [ ] Pass rate is calculated and stated explicitly
- [ ] Consumer access verification names real consumers and access methods
- [ ] Known issues have severity ratings and accepted-by names for each risk
- [ ] Formal sign-off section has actual names and decisions, not blanks

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `consumer-use-case-map` exists in the
  conversation, use it to derive UAT test scenarios. If a `data-contract`
  exists, use its SLA targets as business logic validation criteria. If a
  `data-quality-sign-off` exists, reference its results in the completeness
  check.

If no execution context is available, proceed normally with user-provided
information.
