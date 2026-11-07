---
name: deployment-record
description: |
  Log deployment metadata, components deployed, verification steps, and issues
  encountered. Use when the user asks to "document the deployment", "create the
  deployment record", "log what was deployed", or "record the release".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-6-publish
  dependencies: []
  consumes:
    - uat-sign-off
    - build-checklist
  shared-components:
    core: []
    platforms: []
---

# Deployment Record

Generate a **Deployment Record** for the data product described in $ARGUMENTS.

Use when the user asks to "document the deployment", "create a deployment
record", "log what was deployed", "record the release to production", or
"capture deployment details for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 6 — Publish** |
| Precedes | Consumer Onboarding Guide (Phase 6), Runbook (Phase 7) |
| Depends on | UAT Sign-Off (Phase 5), Build Checklist (Phase 4) |
| Gate | Deployment record must be completed before consumer notification |

The deployment record captures what was deployed, when, by whom, and what
verification steps were performed. It serves as the audit trail for the
production release and is referenced by the runbook for rollback procedures.

## Instructions

1. Read the template at `templates/deployment-record.md` to understand the
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
- [ ] Deployment timestamp and environment are specific (not "production")
- [ ] Component list matches what was actually deployed with version numbers
- [ ] Verification steps document actual results, not just planned checks
- [ ] Issues encountered section is populated (or explicitly states "None")
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `build-checklist` exists in the conversation,
  use it to enumerate the components that were deployed. If a `uat-sign-off`
  exists, reference any conditions that were attached to the deployment
  approval.

If no execution context is available, proceed normally with user-provided
information.
