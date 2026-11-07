# Agent-First Docs Organization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish one canonical agent runbook and enforce agent defaults so users never need to manually configure Databricks job prefix behavior.

**Architecture:** Add a single source-of-truth agent operations doc (`docs/agent-runbook.md`), then wire existing docs to it by role: human quickstart (`GETTING_STARTED.md`) and deep technical reference (`.devcontainer/README.md`). Enforce runbook-first behavior and strict remediation order in `.github/copilot-instructions.md`.

**Tech Stack:** Markdown docs, repo policy docs, ripgrep (`rg`), git.

## Global Constraints

- Canonical agent entrypoint must be `docs/agent-runbook.md`.
- Agents must not ask users to set `databricks_job_prefix` manually.
- Agent flow must enforce order: deploy DAB jobs first, then start/restart Astro, then verify prefix + job existence.
- Agent troubleshooting must classify failures by stage: job lookup, auth, runtime.
- Human onboarding docs must remain short and link out to deep reference docs.

---

### Task 1: Create Canonical Agent Runbook

**Files:**
- Create: `docs/agent-runbook.md`
- Reference: `docs/superpowers/specs/2026-07-23-agent-runbook-docs-organization-design.md`
- Test: `rg` checks from repo root

**Interfaces:**
- Consumes: Design requirements from `docs/superpowers/specs/2026-07-23-agent-runbook-docs-organization-design.md`
- Produces: Canonical operational flow section names used by follow-up docs:
  - `## Start Here (Required)`
  - `## Deterministic Execution Order`
  - `## Failure Classification`
  - `## Auto-Remediation Playbook`

- [ ] **Step 1: Write the failing verification checks (before file exists)**

```bash
rg -n "^## Start Here \\(Required\\)$" docs/agent-runbook.md
```

Expected: no matches / non-zero exit because file does not exist yet.

- [ ] **Step 2: Create `docs/agent-runbook.md` with required sections**

```markdown
# Agent Runbook

## Start Here (Required)
- Confirm you are operating in the devcontainer-backed Astro environment.
- Verify active scheduler container name matches `edo-training.*-scheduler-1`.

## Deterministic Execution Order
1. Deploy DAB jobs first.
2. Start/restart Astro after deployment.
3. Verify `databricks_job_prefix` resolves from Databricks identity and is present in Airflow.
4. Verify target Databricks job exists with prefixed name.
5. Trigger DAG/task.

## Failure Classification
1. Job lookup stage (missing or mismatched prefixed job name).
2. Auth stage (invalid/stale OAuth token or connection drift).
3. Runtime stage (dbt/Databricks run-time failures after launch).

## Auto-Remediation Playbook
- Never ask user to manually configure prefix.
- Recompute prefix from Databricks identity.
- Refresh OAuth-backed Airflow Databricks connections.
- Re-verify job existence and retry task.
```

- [ ] **Step 3: Run verification checks for required runbook sections**

```bash
rg -n "^## Start Here \\(Required\\)$|^## Deterministic Execution Order$|^## Failure Classification$|^## Auto-Remediation Playbook$" docs/agent-runbook.md
```

Expected: 4 matches, one per required section.

- [ ] **Step 4: Commit Task 1**

```bash
git add docs/agent-runbook.md
git commit -m "docs: add canonical agent runbook for airflow/databricks triage"
```

---

### Task 2: Enforce Agent Guardrails in Copilot Instructions

**Files:**
- Modify: `.github/copilot-instructions.md`
- Test: `rg` checks from repo root

**Interfaces:**
- Consumes: `docs/agent-runbook.md` section names and deterministic order
- Produces: Hard guardrail section in `.github/copilot-instructions.md` that later tasks can reference by title:
  - `## Agent Runbook Enforcement`

- [ ] **Step 1: Write failing verification check for new guardrail section**

```bash
rg -n "^## Agent Runbook Enforcement$" .github/copilot-instructions.md
```

Expected: no matches / non-zero exit before update.

- [ ] **Step 2: Add required enforcement block to `.github/copilot-instructions.md`**

```markdown
## Agent Runbook Enforcement

- Agents must read `docs/agent-runbook.md` before setup/debugging work.
- Agents must verify execution context is the devcontainer Astro scheduler before trusting localhost Airflow UI observations.
- Agents must enforce this sequence for job-triggered DAGs:
  1. Deploy DAB jobs.
  2. Start/restart Astro.
  3. Verify prefixed Databricks job exists.
- Agents must auto-remediate prefix/auth drift and must not ask users to manually set `databricks_job_prefix`.
```

- [ ] **Step 3: Verify enforcement text exists and includes sequence**

```bash
rg -n "Agent Runbook Enforcement|Deploy DAB jobs|Start/restart Astro|must not ask users to manually set `databricks_job_prefix`" .github/copilot-instructions.md
```

Expected: matches for section and all three guardrail checks.

- [ ] **Step 4: Commit Task 2**

```bash
git add .github/copilot-instructions.md
git commit -m "docs: enforce agent runbook-first workflow and prefix auto-remediation"
```

---

### Task 3: Reorganize Human Quick Start to Link Agent Path

**Files:**
- Modify: `GETTING_STARTED.md`
- Test: `rg` checks from repo root

**Interfaces:**
- Consumes: Canonical runbook path `docs/agent-runbook.md`
- Produces: Human quickstart pointer to agent runbook and shortened troubleshooting ownership notes

- [ ] **Step 1: Write failing check for explicit agent runbook pointer**

```bash
rg -n "docs/agent-runbook.md" GETTING_STARTED.md
```

Expected: no matches before update.

- [ ] **Step 2: Add concise “Agent operations” pointer in Airflow section**

```markdown
### Agent operations

For agent-driven setup/debug flows, use the canonical runbook:

`docs/agent-runbook.md`
```

- [ ] **Step 3: Keep quickstart concise by replacing duplicated troubleshooting paragraphs with one link**

```markdown
For detailed Airflow troubleshooting and environment internals, see:
`.devcontainer/README.md#working-with-airflow-dags`
```

- [ ] **Step 4: Verify quickstart now has both human-first flow and agent pointer**

```bash
rg -n "Agent operations|docs/agent-runbook.md|Working with Airflow DAGs" GETTING_STARTED.md
```

Expected: all 3 patterns matched.

- [ ] **Step 5: Commit Task 3**

```bash
git add GETTING_STARTED.md
git commit -m "docs: keep getting started human-first and link canonical agent runbook"
```

---

### Task 4: Align Devcontainer Reference + Source-of-Truth Matrix

**Files:**
- Modify: `.devcontainer/README.md`
- Modify: `README.md`
- Test: `rg` checks from repo root

**Interfaces:**
- Consumes: Canonical paths:
  - `docs/agent-runbook.md`
  - `GETTING_STARTED.md`
  - `.devcontainer/README.md`
- Produces: Source-of-truth matrix defining ownership:
  - human onboarding
  - agent operations
  - deep technical troubleshooting

- [ ] **Step 1: Write failing check for source-of-truth matrix heading**

```bash
rg -n "^## Documentation Ownership Matrix$" .devcontainer/README.md
```

Expected: no matches before update.

- [ ] **Step 2: Add ownership matrix in `.devcontainer/README.md`**

```markdown
## Documentation Ownership Matrix

| Need | Source of truth |
|---|---|
| Human onboarding quick path | `GETTING_STARTED.md` |
| Agent operational defaults and remediation order | `docs/agent-runbook.md` |
| Deep devcontainer/Astro implementation details | `.devcontainer/README.md` |
```

- [ ] **Step 3: Add a short pointer in `README.md` to the matrix and runbook**

```markdown
For operational defaults:
- Agent workflows: `docs/agent-runbook.md`
- Human quickstart: `GETTING_STARTED.md`
```

- [ ] **Step 4: Verify ownership links and canonical paths are present**

```bash
rg -n "Documentation Ownership Matrix|docs/agent-runbook.md|GETTING_STARTED.md" .devcontainer/README.md README.md
```

Expected: matches in both files.

- [ ] **Step 5: Final consistency check across all docs**

```bash
rg -n "clients_job can not be found|databricks_job_prefix|Deploy DAB jobs|Start/restart Astro" docs/agent-runbook.md .github/copilot-instructions.md GETTING_STARTED.md .devcontainer/README.md
```

Expected: all patterns found with no conflicting instructions.

- [ ] **Step 6: Commit Task 4**

```bash
git add .devcontainer/README.md README.md
git commit -m "docs: add ownership matrix and unify agent/human doc entrypoints"
```

---

### Task 5: Validation Pass and Handoff

**Files:**
- Modify (if needed): `docs/agent-runbook.md`, `.github/copilot-instructions.md`, `GETTING_STARTED.md`, `.devcontainer/README.md`, `README.md`
- Test: repo-wide `rg` consistency checks

**Interfaces:**
- Consumes: All prior task outputs
- Produces: Final validated docs set ready for agent execution defaults

- [ ] **Step 1: Run consolidated consistency checks**

```bash
rg -n "docs/agent-runbook.md|Agent Runbook Enforcement|Documentation Ownership Matrix" README.md GETTING_STARTED.md .devcontainer/README.md .github/copilot-instructions.md
```

Expected: canonical references present across docs.

- [ ] **Step 2: Run contradiction scan for startup order and prefix guidance**

```bash
rg -n "astro dev start|astro dev restart|databricks_job_prefix|Deploy DAB jobs" README.md GETTING_STARTED.md .devcontainer/README.md docs/agent-runbook.md .github/copilot-instructions.md
```

Expected: no contradictory order statements (DAB deploy precedes Astro restart in agent workflow docs).

- [ ] **Step 3: Commit final cleanup if any edits were required**

```bash
git add README.md GETTING_STARTED.md .devcontainer/README.md .github/copilot-instructions.md docs/agent-runbook.md
git commit -m "docs: finalize agent-first documentation consistency checks"
```

- [ ] **Step 4: Prepare PR summary**

```markdown
- Added canonical agent runbook and guardrail enforcement.
- Reorganized human quickstart to stay concise.
- Added documentation ownership matrix to prevent future drift.
- Standardized remediation flow for `clients_job` prefix lookup failures.
```
