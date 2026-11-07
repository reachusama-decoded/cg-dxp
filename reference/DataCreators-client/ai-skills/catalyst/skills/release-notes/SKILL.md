---
name: release-notes
description: |
  Write release notes: summary, what is new, known limitations, and migration
  notes. Use when the user asks to "write the release notes", "document what
  changed", "create the changelog", or "summarize this release".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-6-publish
  dependencies: []
  consumes:
    - deployment-record
    - uat-sign-off
  shared-components:
    core: []
    platforms: []
---

# Release Notes

Generate **Release Notes** for the data product described in $ARGUMENTS.

Use when the user asks to "write release notes", "document what changed",
"create the changelog for this release", "summarize the new version", or
"notify consumers about the update to this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 6 — Publish** |
| Precedes | Consumer Onboarding Guide updates, Downstream Impact Assessment (Phase 8) |
| Depends on | Deployment Record (Phase 6), UAT Sign-Off (Phase 5) |
| Gate | Release notes should be published before or alongside consumer notification |

Release notes communicate what changed between versions of a data product. They
are especially important for versioned products with breaking changes that
require consumer migration. Optional for initial releases.

## Instructions

1. Read the template at `templates/release-notes.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document with the following required H2 headings in
   this order (exact text, no numbering prefixes, no extra words):
   - `## Version Information` — table with columns: Field, Detail
   - `## Summary of Changes` — bullet list
   - `## Breaking Changes` — table with columns: Change, Impact, Consumer Action Required
   - `## Migration Steps` — table with columns: Step, Action, Deadline
   - `## Known Issues` — table with columns: Issue, Severity, Workaround, Expected Fix
   - `## Contact` — table with columns: Role, Name / Team, Channel

   Preserve the required format for each section: `Summary of Changes` must be
   a bullet list, and `Version Information` must use the `Field | Detail`
   table. For the list-table sections (`Breaking Changes`, `Migration Steps`,
   `Known Issues`, and `Contact`), always render the full table structure. Even
   when there are no items, include the table header row followed by a single
   row whose cells state "None" or "No items". Do not replace a required table
   with a prose note.
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Version number follows semantic versioning and matches the deployment record
- [ ] Breaking changes section is explicit (list changes or state "None")
- [ ] Migration steps have specific deadlines for consumer action
- [ ] Known issues have severity and workaround information
- [ ] Contact information lists actual names and channels

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `deployment-record` exists in the conversation,
  pull version and component details from it. If a `data-contract` exists, check
  for schema changes that constitute breaking changes. If a `uat-sign-off`
  exists, reference known issues documented during testing.

If no execution context is available, proceed normally with user-provided
information.
