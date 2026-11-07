# Challenge 03 Redundant Command Cleanup Design

## Objective
Remove the redundant `astro dev start` and `mise run setup:databricks` re-run
instructions scattered through later steps of
`challenges/03-airflow-orchestration/README.md`. Both commands are already
established once, correctly, in that challenge's **Prerequisites**; the later
repeats make trainees re-run one-time / already-running steps and waste time.
After this change each command appears as a prerequisite (where needed) and not
as a mid-challenge re-run.

## Root Cause
Challenge 03 establishes both commands up front in Prerequisites — `mise run
setup:databricks` (`challenges/03-airflow-orchestration/README.md:120`) and
`astro dev start` (`:157`). Individual sections were later authored to be
self-contained and re-issued the same commands, even though the OAuth setup is
one-time and the astro stack is explicitly told to "leave it running" for the
rest of the challenge (`:143`). The result is duplicate instructions in
sections 3, 5, 8, and 9 that repeat work already done in Prerequisites.

## Scope
In scope: only the redundant re-runs in
`challenges/03-airflow-orchestration/README.md`.

Out of scope (confirmed with user): the conditional / troubleshooting mentions
elsewhere, which appear once and are guarded by "if you haven't already" or "if
expired" wording — `challenges/README.md:5` (top-level prerequisite),
`challenges/00-environment-check/README.md:32`,
`challenges/02-dbt-pipeline/README.md:16`,
`challenges/04-atlas-capstone/README.md:288` and `:1593`, and the self-contained
quickstart runbook `challenges/03-airflow-orchestration/solution/README.md:36,39`.
`CHANGES.md` and the DAG source comments are changelog/code context, not trainee
steps, and are also untouched.

## Approved Design
Approach A — delete the redundant command and lightly reword only the immediate
surrounding sentence so each step still reads correctly. Five edits, all in
`challenges/03-airflow-orchestration/README.md`:

1. **Section 3 "Connect to Databricks" (~:277)** — remove the `mise run
   setup:databricks` code block. Reword the "Challenge (authoring)" sentence so
   it states setup was already completed in the Prerequisites (keeping the
   `training_dev` / `training_$(whoami)` catalog+schema detail), leaving the
   section focused on its actual teaching point: proving the connection with
   `dbt debug`. The following Hint about the profile's env vars is unchanged.
2. **Section 5 optional variation (~:461)** — remove `astro dev start` from
   "Open the Graph view in the Airflow UI (`astro dev start`, then the DAG →
   Graph)", leaving "(the DAG → Graph)". The stack is already up from
   Prerequisites.
3. **Section 8 "How to check" (~:650)** — delete the `astro dev start` line from
   the code block; keep the `astro dev run dags test …` command.
4. **Section 9 "Challenge (authoring)" (~:703)** — delete `astro dev start` from
   the code block and reword "Boot the local stack and trigger it:" to "Unpause
   and trigger it:".
5. **Section 9 Solution block (~:733)** — delete the `astro dev start` line from
   the code block.

## Deliberate Keeps
These reference the Prerequisites rather than instructing a re-run, so they stay:

- `:257` — "With the stack up from the Prerequisites (`astro dev start`), prefix
  Airflow commands with `astro dev run`". This teaches the `astro dev run`
  prefix and cites the prerequisite; it is not a re-run instruction.
- `:147–150` — the Prerequisites note explaining *why* to start the stack only
  after `mise run setup:databricks` finishes. This is prerequisite context, not
  a duplicate step.

## Verification Design
- `git --no-pager diff` shows only the five intended edits in
  `challenges/03-airflow-orchestration/README.md` and no other files changed.
- A grep for `astro dev start` in that README returns only the Prerequisites
  occurrence (`:157`) and the section-2 back-reference (`:257`).
- A grep for `mise run setup:databricks` in that README returns only the
  Prerequisites occurrences (`:120`, `:150`).
- Manual read of sections 3, 5, 8, 9 confirms each step still reads coherently
  (no dangling "then", no orphaned code fences) and that no command required to
  complete the step (`dbt debug`, `dags test`, `unpause`, `trigger`) was
  removed.

## Constraints
- Do not remove any command that is the actual deliverable of a step (only the
  redundant environment-bootstrap commands are removed).
- Do not alter Prerequisites, other challenges, the solution quickstart, or
  changelog/code files.
- Preserve existing Markdown structure, headings, and the collapsible Solution
  blocks.
