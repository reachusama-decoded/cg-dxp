# Challenge 03 Redundant Command Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the redundant `astro dev start` and `mise run setup:databricks` re-run instructions from later sections of Challenge 03's README so each command appears only as a prerequisite.

**Architecture:** Pure documentation edit to a single Markdown file. Five surgical string replacements delete the duplicated environment-bootstrap commands and lightly reword the immediately surrounding sentence so each step still reads correctly. The Prerequisites section remains the single source of truth for both commands.

**Tech Stack:** Markdown. Verification via `grep` and manual read (no code test framework applies to this doc change).

## Global Constraints

- Edit only `challenges/03-airflow-orchestration/README.md`. No other files change.
- Do not remove any command that is a step's actual deliverable (`dbt debug`, `dags test`, `unpause`, `trigger`, `challenge:dbt … show`).
- Do not alter Prerequisites (lines ~120, ~157), the section-2 back-reference (~257), or the Prerequisites note (~147–150).
- Preserve Markdown structure, headings, code fences, and the collapsible `<details>` Solution blocks.
- Reference spec: `docs/superpowers/specs/2026-07-31-challenge-03-redundant-command-cleanup-design.md`.

---

### Task 1: Remove redundant re-runs from Challenge 03 README

**Files:**
- Modify: `challenges/03-airflow-orchestration/README.md` (sections 3, 5, 8, 9)

**Interfaces:**
- Consumes: nothing (self-contained doc edit).
- Produces: nothing consumed by later tasks (single-task plan).

- [ ] **Step 1: Edit Section 3 — drop the `mise run setup:databricks` re-run**

Replace this block (the "Challenge (authoring)" sentence, the fenced command, and the catalog/schema line):

```
**Challenge (authoring).** Run the setup script (first time only) and accept
the training defaults:

```bash
mise run setup:databricks
```

Take catalog `training_dev` and schema `training_$(whoami)`.
```

with:

```
**Challenge (authoring).** You already ran `mise run setup:databricks` in the
Prerequisites — it took catalog `training_dev` and schema `training_$(whoami)`.
Nothing to re-run here; the task is to prove the connection with `dbt debug`.
```

The following **Hint** paragraph (about the in-repo profile env vars) is unchanged.

- [ ] **Step 2: Edit Section 5 — drop `astro dev start` from the optional variation**

Replace:

```
**Try a variation (optional).** Open the Graph view in the Airflow UI
(`astro dev start`, then the DAG → Graph) and expand the `dbt_pipeline` group
```

with:

```
**Try a variation (optional).** Open the Graph view in the Airflow UI
(the DAG → Graph) and expand the `dbt_pipeline` group
```

- [ ] **Step 3: Edit Section 8 — drop `astro dev start` from the how-to-check block**

Replace:

```bash
astro dev start
astro dev run dags test portfolio_analytics_daily 2026-05-04 2>&1 | grep -iE "retry|attempt"
```

with:

```bash
astro dev run dags test portfolio_analytics_daily 2026-05-04 2>&1 | grep -iE "retry|attempt"
```

- [ ] **Step 4: Edit Section 9 "Challenge (authoring)" — drop `astro dev start` and reword the sentence**

Replace (the sentence plus its fenced block; the "Boot the local stack" wording makes this occurrence unique):

```
read the result. Boot the local stack and trigger it:

```bash
astro dev start
astro dev run dags unpause portfolio_analytics_daily
astro dev run dags trigger portfolio_analytics_daily
```
```

with:

```
read the result. Unpause and trigger it:

```bash
astro dev run dags unpause portfolio_analytics_daily
astro dev run dags trigger portfolio_analytics_daily
```
```

- [ ] **Step 5: Edit Section 9 Solution block — drop `astro dev start`**

Replace (the trailing `# after success:` line makes this occurrence unique):

```bash
astro dev start
astro dev run dags unpause portfolio_analytics_daily
astro dev run dags trigger portfolio_analytics_daily
# after success:
```

with:

```bash
astro dev run dags unpause portfolio_analytics_daily
astro dev run dags trigger portfolio_analytics_daily
# after success:
```

- [ ] **Step 6: Verify `astro dev start` now appears only in the two allowed places**

Run: `grep -n "astro dev start" challenges/03-airflow-orchestration/README.md`
Expected: exactly two lines — the Prerequisites boot command (~line 157) and the section-2 back-reference `> the Prerequisites (\`astro dev start\`), prefix Airflow commands with` (~line 257). No occurrences in sections 5, 8, or 9.

- [ ] **Step 7: Verify `mise run setup:databricks` now appears only in the Prerequisites**

Run: `grep -n "setup:databricks" challenges/03-airflow-orchestration/README.md`
Expected: exactly two lines, both in Prerequisites — the boot command (~line 120) and the explanatory note "written by `mise run setup:databricks`" (~line 150). No occurrence in section 3.

- [ ] **Step 8: Confirm the diff is scoped and each step still reads coherently**

Run: `git --no-pager diff --stat`
Expected: only `challenges/03-airflow-orchestration/README.md` changed.

Run: `git --no-pager diff challenges/03-airflow-orchestration/README.md`
Expected: five hunks matching Steps 1–5. Manually confirm no dangling "then", no orphaned or unbalanced code fences, and that `dbt debug`, `dags test`, `unpause`, `trigger`, and `challenge:dbt … show` commands are all still present.

- [ ] **Step 9: Commit**

```bash
git add challenges/03-airflow-orchestration/README.md
git commit -m "docs(challenge-03): drop redundant astro dev start / setup:databricks re-runs

Both commands are already established in Prerequisites; remove the duplicate
re-runs from sections 3, 5, 8, and 9 so they appear as prerequisites only.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Self-Review

**1. Spec coverage:** All five spec edits map to Steps 1–5; both spec "Deliberate Keeps" are protected by Global Constraints and asserted in Steps 6–7; the spec "Verification Design" maps to Steps 6–8. No gaps.

**2. Placeholder scan:** No TBD/TODO/placeholder steps; every edit shows exact before/after text.

**3. Type consistency:** N/A (documentation change, no code symbols). Command names referenced in verification (`astro dev run`, `dbt debug`, `challenge:dbt`) match the README verbatim.
