---
name: schedule-backfill-plan
description: |
  Design the ingestion schedule, historical backfill strategy, and rollback
  plan. Use when the user asks to "plan the schedule", "design the backfill",
  "how do we load historical data", or "create the scheduling plan".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - integration-blueprint
    - data-model
    - requirements-acceptance-criteria
  shared-components:
    core: []
    platforms: []
---

# Schedule & Backfill Plan

Generate a **Schedule & Backfill Plan** for the data product described in $ARGUMENTS.

Use when the user asks to "plan the ingestion schedule", "design the backfill
strategy", "define the load cadence", "how do we handle historical data",
or "plan the rollback approach for this pipeline".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Build Checklist (Phase 4), Runbook (Phase 7) |
| Depends on | Integration Blueprint (Phase 3), Data Model (Phase 3), Requirements (Phase 2) |
| Gate | Schedule and backfill strategy must be reviewed before Build |

The schedule & backfill plan defines when data is ingested, how historical data
is loaded, and what happens if a load fails. It is a key input to the runbook
and is validated during integration testing in Phase 4.

## Instructions

1. Read the template at `templates/schedule-backfill-plan.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — numbered prefixes are required.
   The output **must** contain these H2 sections in order:
   - `## 1. Overview` — Field/Value table with rows: Product Name, Owner,
     Classification
   - `## 2. Production Schedule` — three sub-sections:
     - `### 2.1 Primary Schedule` (Field/Value table: Trigger Type,
       Schedule, Processing Window, SLA Deadline, Time Zone)
     - `### 2.2 Detailed Job Schedule` (columns: Job / Model, Trigger,
       Schedule / Dependency, Expected Duration, SLA Deadline, Retry Policy)
     - `### 2.3 Schedule Visualization` (Mermaid gantt chart)
   - `## 3. Dependencies` — two sub-sections:
     - `### 3.1 Upstream Dependencies` (columns: Dependency, Type, Expected
       Availability, Impact if Late, Mitigation)
     - `### 3.2 Downstream Commitments` (columns: Consumer, Expected
       Availability, Notification Method, Fallback if Delayed)
   - `## 4. Backfill Plan` — four sub-sections:
     - `### 4.1 Initial Historical Load` (Field/Value table)
     - `### 4.2 Backfill Execution Steps` (columns: Step, Action, Duration,
       Validation)
     - `### 4.3 Re-Run / Replay Strategy` (columns: Scenario, Approach,
       Scope, Impact on Consumers)
     - `### 4.4 Re-Run Command / Process` (code block with exact
       command/process)
   - `## 5. Maintenance Windows` — table with columns: Window, Schedule,
     Duration, Impact, Communication; followed by:
     - `### Maintenance Checklist` (checkboxes)
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
- [ ] Schedule frequency is specific (cron expression or exact cadence)
- [ ] Backfill window specifies exact date range and expected duration
- [ ] Rollback plan describes concrete steps, not just "roll back if needed"
- [ ] Dependencies on source system availability windows are documented
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `requirements-acceptance-criteria` exists in
  the conversation, pull freshness and latency NFRs to set the ingestion
  schedule. If a `data-model` exists, use its partitioning strategy to inform
  the backfill approach.

If no execution context is available, proceed normally with user-provided
information.
