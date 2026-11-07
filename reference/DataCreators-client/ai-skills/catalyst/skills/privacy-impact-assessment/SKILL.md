---
name: privacy-impact-assessment
description: |
  Assess data classification, PII inventory, privacy risks, and required
  controls. Use when the user asks to "assess privacy impact", "does this have
  PII", "create the PIA", "evaluate data sensitivity", or "check privacy
  requirements".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes:
    - demand-tracker-entry
  shared-components:
    core: []
    platforms: []
---

# Privacy Impact Assessment

Generate a **Privacy Impact Assessment** for the data product described in $ARGUMENTS.

Use when the user asks to "assess privacy impact", "identify PII risks",
"do a PIA for this product", "evaluate data sensitivity", or "document
privacy controls needed for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 2 — Discovery** |
| Precedes | Security Design (Phase 3), Data Contract (Phase 3) |
| Depends on | Demand Tracker Entry (Phase 1) — sensitivity classification |
| Gate | Required for products classified Restricted or above; recommended for all |

The privacy impact assessment identifies personal and sensitive data elements,
evaluates privacy risks, and prescribes controls. It is a mandatory input to
the security design in Phase 3 for restricted or regulated data products.

## Instructions

1. Read the template at `templates/privacy-impact-assessment.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — numbered prefixes are required, no extra
   words. The output **must** contain these seven H2 sections in order:
   - `## 1. Personal Data Inventory` — table with columns: Data Element, Category,
     Data Subjects, Source System, Sensitivity, Criticality
   - `## 2. Purpose & Legal Basis` — table with columns: Purpose of Processing,
     Legal Basis, Retention Period
   - `## 3. Data Subject Rights` — table with columns: Right, How Supported, Notes
   - `## 4. Cross-Border Transfer` — table with columns: Factor, Details
   - `## 5. Technical & Organizational Controls` — table with columns:
     Control Category, Control Description, Status
   - `## 6. Risks & Mitigations` — table with columns: #, Risk, Likelihood,
     Impact, Mitigation
   - `## 7. Sign-Off` — table with columns: Role, Name, Date, Decision
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Every PII column is identified with its sensitivity level and legal basis
- [ ] Risk ratings have both likelihood and impact, not just a single score
- [ ] Required controls are specific (masking method, encryption type) not generic
- [ ] Regulatory references cite specific regulations, not just "applicable law"
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `demand-tracker-entry` exists in the
  conversation, pull the sensitivity classification from it to seed the data
  classification section.
- **Execution results:** If `data-profiling` has run, scan the column names and
  sample values for PII-pattern columns (e.g. names, emails, IDs) and flag them
  in the PII inventory.

If no execution context is available, proceed normally with user-provided
information.
