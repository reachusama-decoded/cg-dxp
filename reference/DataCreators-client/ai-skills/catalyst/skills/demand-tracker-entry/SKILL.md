---
name: demand-tracker-entry
description: |
  Create a demand tracker entry capturing requestor, classification, priority,
  and lifecycle state. Use when the user asks to "log new demand", "create a
  demand entry", "register this request", "add to the demand tracker", or
  "triage this data product request".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-1-triage
  dependencies: []
  consumes:
    - phase-zero-checklist
  shared-components:
    core: []
    platforms: []
---

# Demand Tracker Entry

Generate a **Demand Tracker Entry** for the data product described in $ARGUMENTS.

Use when the user asks to "log a new data request", "create a demand entry",
"register a new data product", "add this to the demand tracker", or "triage
a data product request".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 1 — Triage** |
| Precedes | Consumer Use Case Map (Phase 1), all Discovery artifacts (Phase 2) |
| Depends on | Phase Zero Checklist (Phase 0) |
| Gate | Entry must be triaged and prioritized before Discovery begins |

The demand tracker entry is the canonical record for a demand item. It is
created once and updated as the product moves through lifecycle states.

## Instructions

1. Read the template at `templates/demand-tracker-entry.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — no numbering prefixes, no extra words.
   The output **must** contain these six H2 sections in order:
   - `## Identity` — table with columns: Field, Value
   - `## Classification` — table with columns: Field, Value
   - `## Brief Description` — paragraph text
   - `## Lifecycle State` — table with columns: State, Date Entered, Owner, Notes
   - `## Linked Artifacts` — table with columns: Artifact, Location / Reference,
     Status
   - `## Triage Notes` — paragraph text
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] All Identity fields have values (Product Name, Domain, Requestor at minimum)
- [ ] Classification fields have concrete selections, not just the option lists
- [ ] Brief Description is filled with 1-3 sentences, not a comment placeholder
- [ ] Lifecycle State table has at least the "Submitted" row populated with a date
- [ ] Linked Artifacts table references are populated or marked "Not yet created"

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Execution results:** If `data-product-classification` has produced results,
  use its domain, sensitivity, and criticality output to populate the
  Classification section instead of asking the user.
- **Execution results:** If `marketplace-search` has run, reference whether
  similar products were found in the Triage Notes section.

If no execution context is available, proceed normally with user-provided
information.
