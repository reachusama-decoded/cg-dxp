# Atlas Reliability Guardrails Design

## Context

Atlas training DAG reliability degraded due to three independent operational failure modes:

1. Duplicate Databricks jobs with identical names under one user prefix caused Airflow name-based job lookup failures.
2. Missing or unprepared DQ dependency volume (`<catalog>.<schema>.dqf_libs`) blocked DQ runtime setup.
3. Databricks artifact allowlist policy blocked loading the Deequ JAR from `/Volumes/.../dqf_libs/...`.

These failures are high-impact for training because they appear as random DAG breaks to new users, even when repo code is valid.

## Goal

Make Atlas local training runs predictably green by adding deterministic preflight guardrails with remediation, not just documentation.

## Non-Goals

1. Full redesign of Atlas DAG business logic.
2. Full replacement of current Airflow/Databricks operator stack in one step.
3. Solving organization-wide Databricks governance policy in this repo alone.

## Decision

Adopt a **hybrid guardrail model**:

1. Agent/runbook guidance for known failure modes.
2. Automated preflight checks with remediation before deploy/run.
3. Keep DAG runtime logic mostly unchanged in phase 1 to minimize rollout risk.

## Why this approach

1. Documentation-only does not prevent failures during execution.
2. Full hard enforcement everywhere increases onboarding friction and change risk.
3. Preflight-first catches and fixes most training blockers early with clear, reproducible actions.

## Architecture

Add a single entrypoint: `mise run atlas:preflight`.

This preflight runs before Atlas deploy validation and before Atlas DAG validation runs. It performs:

1. **Job uniqueness check/remediation** in Databricks for Atlas `*_job` and `*_dq_job` resources under the current user prefix.
2. **DQ volume readiness check/remediation** for `<catalog>.<schema>.dqf_libs` and required artifacts (Deequ JAR + wheels as needed).
3. **Artifact allowlist readiness check** and explicit block with actionable request template when policy is missing.

## Remediation Model

### 1. Duplicate job handling

1. Discover duplicate job names for Atlas scope and current user prefix.
2. Default to **dry-run report** showing keep/delete decisions.
3. Apply mode deletes older duplicates and keeps the most recent job ID per name.

Rationale: this preserves the newest deployment while making Airflow name-based lookup unambiguous.

### 2. Volume readiness handling

1. If `dqf_libs` volume is missing, create it in the active user schema.
2. If Deequ JAR is missing, stage it to expected volume path.
3. Keep cluster init scripts as **verification/install-from-volume** only, not volume creators.

Rationale: preflight is earlier, clearer, and typically runs with better privileges than cluster startup init scripts.

### 3. Allowlist handling

1. Detect allowlist failure signatures from Databricks run errors.
2. Stop DQ run attempts when allowlist is missing.
3. Emit exact admin request payload (workspace, training-compute scope, path pattern, business justification, expected principal scope).

Rationale: this policy is platform-governed and cannot be reliably auto-fixed from repo code.

### 4. Training workspace allowlist policy

For this repository's training environment, prefer a **workspace-scoped broad trainee allowlist** instead of per-user allowlist entries:

1. Scope policy to the dedicated training workspace and training compute policies only.
2. Permit artifact loading for approved training dependency locations (shared training DQ libs path pattern).
3. Avoid enterprise-wide/global allow-all settings outside the training workspace boundary.

Rationale: this removes per-trainee onboarding friction while keeping blast radius limited to the training environment.

## Operational Flow

1. Run `atlas:preflight` (check + remediation).
2. Deploy bundle to `local`.
3. Trigger Atlas DAG validation sequence.
4. On failure, classify into:
   1. uniqueness drift,
   2. volume/dependency readiness,
   3. policy/allowlist,
   4. true runtime logic failure.

## Testing Strategy

1. Unit tests for:
   1. duplicate detection and keep/delete selection,
   2. volume existence and artifact readiness parsing,
   3. allowlist error signature classification.
2. Integration smoke path:
   1. preflight executes,
   2. bundle deploy executes,
   3. Atlas DAG subset run verifies preflight effect on known blockers.

## Rollout Plan

1. Add preflight command and docs.
2. Add deterministic tests for check + remediation logic.
3. Update training runbook and agent instructions to require preflight before Atlas DAG validation.
4. Phase 2 (optional): add deterministic job ID mapping for runtime execution if name-based ambiguity remains a recurring issue.

## Success Criteria

1. Atlas training users no longer hit name-collision failures after running the documented preflight path.
2. Volume-missing failures are remediated before first DQ run attempt.
3. Allowlist blockers are surfaced as explicit policy gaps with exact next action, not opaque task failures.
4. Training users do not require per-user allowlist onboarding to run Atlas DQ flows.
4. Repeated local runs in the same user namespace remain stable without manual Databricks job cleanup.

## Risks and Mitigations

1. **Risk:** Over-aggressive duplicate cleanup deletes intended jobs.  
   **Mitigation:** dry-run default + scope-limited cleanup (current prefix + Atlas patterns only).

2. **Risk:** Volume creation privileges differ by user/workspace.  
   **Mitigation:** fail with explicit SQL command and privilege guidance when auto-create is denied.

3. **Risk:** Broad allowlist may over-permit artifacts if scope is not bounded.  
   **Mitigation:** restrict policy to training workspace + approved training compute + approved training artifact path pattern.

## Evidence and External References

1. Databricks deployment mode behavior (development prefixing and target behaviors):  
   https://docs.databricks.com/aws/en/dev-tools/bundles/deployment-modes
2. Databricks CLI issue history showing duplicate workflow creation patterns under state drift/CI conditions:  
   https://github.com/databricks/cli/issues/986  
   https://github.com/databricks/cli/issues/893
