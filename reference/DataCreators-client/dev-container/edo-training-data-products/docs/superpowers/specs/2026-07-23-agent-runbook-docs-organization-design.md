# Agent-First Docs Organization Design

## Context

Recent debugging showed repeated confusion from split runtime contexts (host Astro vs devcontainer Astro) and drift between Databricks Asset Bundle (DAB) job naming and Airflow job lookup naming. Agents need deterministic defaults so users do not need to configure internal wiring manually.

The current docs spread critical setup/debug steps across multiple files (`README.md`, `GETTING_STARTED.md`, `.devcontainer/README.md`) with overlapping guidance. This increases the chance that an agent follows a partial or stale path.

## Goal

Create an agent-first documentation structure that:

1. Gives agents one canonical starting point.
2. Makes prefix/auth/deploy order deterministic.
3. Keeps the human path short and low-friction.

## Non-Goals

1. Full rewrite of all technical docs in one pass.
2. Replacing existing deep-reference docs.
3. Changing DAG business logic in this design step.

## Proposed Information Architecture

### 1. Canonical agent entrypoint

Add `docs/agent-runbook.md` as the single required entrypoint for agent operational workflows.

This file owns the **default execution order** for setup and DAG/dbt troubleshooting:

1. Verify execution context is the devcontainer Astro environment.
2. Verify DAB deployment status before Airflow task execution.
3. Resolve and sync Databricks job prefix in Airflow from Databricks identity.
4. Refresh Databricks OAuth-backed Airflow connections.
5. Trigger and classify failures by stage.
6. Apply stage-specific remediation and re-verify.

### 2. Human-first quick path

Keep `GETTING_STARTED.md` as short quickstart for humans, with minimal branching and one explicit link to `docs/agent-runbook.md` for agent operations.

### 3. Deep reference remains in place

Keep `.devcontainer/README.md` as detailed reference/troubleshooting source and reduce duplication by linking to canonical runbook steps.

## Agent Guardrails (Hard Defaults)

Update `.github/copilot-instructions.md` so agents must:

1. Read `docs/agent-runbook.md` before setup/debug actions.
2. Confirm active runtime context before using Airflow UI findings.
3. Follow strict operation order:
   1. Deploy DAB jobs.
   2. Start/restart Astro.
   3. Verify prefix + job existence.
4. Auto-remediate prefix/auth drift instead of asking users to configure prefix manually.

### Why this guardrail is required

The error `Job ID for job name clients_job can not be found` happens when Airflow resolves the unprefixed name while DAB jobs are created with prefixed names (for example `[dev gqp] clients_job`). If the agent does not enforce order and prefix sync, troubleshooting can misdiagnose runtime failures as code issues.

## Runtime Contract for Prefix + Job Lookup

Agents should treat the following as required runtime contract:

1. Job prefix is derived from Databricks identity, not manually entered by users.
2. Airflow variable `databricks_job_prefix` must be set from that derived identity.
3. DAB deployment must be complete before Airflow DAG task execution.
4. Airflow job lookup must validate the target job exists before task trigger.

If validation fails, agent remediation path is:

1. Refresh OAuth setup and connection state.
2. Recompute + update prefix.
3. Re-verify job exists in Databricks.
4. Retry task.

## Failure Classification Model

To reduce noisy debugging, the runbook will classify failures into three stages:

1. **Job lookup stage** (prefix/deploy mismatch, missing job).
2. **Auth stage** (invalid/stale token, connection drift).
3. **Runtime stage** (dbt/Databricks execution errors after job launch).

This sequencing matters because lookup/auth failures must be fixed before runtime analysis is meaningful.

## Rollout Plan (Docs + Guardrails)

1. Create `docs/agent-runbook.md` with explicit start-here and deterministic decision tree.
2. Update `.github/copilot-instructions.md` to enforce runbook-first behavior.
3. Trim `GETTING_STARTED.md` to human quick path and link to runbook/deep reference.
4. Update `.devcontainer/README.md` to reference runbook for agent workflows and keep deep details.
5. Add a short “source of truth” matrix showing which file owns which guidance.

## Success Criteria

1. Agent can execute a full DAG/dbt triage path without asking user to set prefix manually.
2. Agent can identify environment mismatch vs genuine runtime error within first 5 minutes.
3. Docs have one canonical agent flow and no conflicting setup order.
4. Human onboarding remains concise with progressive links to details.

## Risks and Mitigations

1. **Risk:** Duplicate instructions reappear across docs over time.  
   **Mitigation:** Add “source of truth ownership” section and link-first editing rule.

2. **Risk:** Guardrails are added but not followed in practice.  
   **Mitigation:** Make runbook-first check explicit and mandatory in copilot instructions.

3. **Risk:** Prefix logic changes in DAB naming conventions.  
   **Mitigation:** Keep runbook prefix derivation tied to Databricks identity and validate against live job names.

## Open Questions Resolved

1. Should users manually configure prefix? **No** — agent/runtime should derive and apply it.
2. Should docs optimize for agents or humans first? **Agents operationally, humans for onboarding quickstart.**
3. Should deploy order be explicit? **Yes** — DAB deploy precedes Astro runtime launch for reliable job lookup.
