---
name: dplc-build
description: |
  Run the Build phase (Phase 4) of the Data Product Lifecycle. Single
  orchestrator with branching steps: preflight → (if fresh) infra setup
  leaves → (per model) authoring leaves + artifact skills → gate. Mode
  aware (prototype / production / lift-and-shift). Mirrors the
  1-orchestrator-per-phase pattern of every other DPLC phase.
  Use when the design is approved and the user is ready to build, or
  when iterating on a prototype dbt project against a sandbox warehouse,
  or when wrapping an existing dbt project in Catalyst conventions.
  Trigger phrases: "build the data product", "Phase 4", "build phase",
  "scaffold dbt project", "set up Databricks bundle", "prototype dbt
  against Databricks".
allowed-tools: Read Grep
metadata:
  tier: orchestrator
  lifecycle-phase: phase-4-build
  dependencies:
    # --- Phase 4 Build skills (new, authored in this PR) ---
    - build-preflight                 # phase-4-build, orchestrator — preflight gating
    - setup-dbt-project               # phase-4-build, workflow — dbt project scaffolding
    - configure-sql-warehouse         # phase-4-build, capability — serverless warehouse + compute DAB
    - write-dbt-wrapper               # phase-4-build, capability — dbt_wrapper.py authoring
    - setup-databricks-asset-bundle   # phase-4-build, workflow — pipeline DAB + job YAMLs
    - setup-monitoring-and-logging    # phase-4-build, capability — cluster log + runbook
    - run-dbt-on-databricks           # phase-4-build, capability — smoke run executor
    - dbt-best-practices              # phase-4-build, capability — rule loader (vendored)
    - troubleshoot-dbt-on-databricks  # phase-4-build, capability — debug guide (vendored)
    # --- Phase 4 Build skills (pre-existing, composed in from earlier PRs) ---
    - source-aligned                  # phase-4-build, workflow — source-layer model authoring
    - domain-aligned                  # phase-4-build, workflow — integration-layer model authoring
    - consumer-aligned                # phase-4-build, workflow — consumer-layer model authoring
    - unit-test-report                # phase-4-build, document — unit test artifact
    - integration-test-report         # phase-4-build, document — integration test artifact
    - code-review-sign-off            # phase-4-build, document — code review gate artifact
    - build-checklist                 # phase-4-build, document — build completion checklist
  consumes:
    - data-contract
    - data-model
    - transformation-spec
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # Canonical (RFD 0012 cross-ref) — orchestrator inherits coverage from invoked leaves
    - DBX-SEC-002              # SP ownership of created objects (delegated to leaves)
    # Proposed (PR 94 prose → IDs; awaiting RFD 0008)
    - DBX-WORKFLOW-001         # Pipeline DAB and compute DAB are separate bundles (load-bearing)
    - DBX-WORKFLOW-002         # Airflow owns DAG-level alerting; DAB owns system signals
    - DBX-COMPUTE-004          # Auto-stop on every warehouse (delegated to /configure-sql-warehouse)
    - DBX-COMPUTE-007          # Pipeline DAB tasks use serverless Python compute
---

# Phase 4 Build Orchestrator

Run Phase 4 of the Data Product Lifecycle. Branching driven by `/build-preflight`'s state report.

## Delegation rule

This orchestrator is a **delegating** sub-orchestrator. Each sub-skill listed below is a separate, purpose-built skill: invoke it via the `Skill` tool (or by reading `skills/<name>/SKILL.md` if the runtime registry hasn't picked it up). Never invoke this orchestrator (`dplc-build`) from inside itself; the slash command names the phase you are already running.

**Acknowledge and advance — don't inline-execute.** When you invoke a sub-skill (`Skill(build-preflight)`, `Skill(source-aligned)`, etc.) and it returns successfully, treat the step as complete and advance. When the `Skill` tool returns "Unknown skill" (Catalyst skills aren't always in the runtime registry), READ the sub-skill's SKILL.md **once** as your acknowledgment of delegation -- that read IS the delegation in this harness (the behavior-test runner counts a `Read(skills/<name>/SKILL.md)` as a sub-skill invocation, equivalent to a successful `Skill` call). Then advance to the next step.

Do **not** follow the sub-skill's instructions inline by reading its templates, exploring the workspace yourself, or executing its underlying scripts. Each sub-skill owns its own scope (preflight does state-detection; source-aligned authors models; etc.); this orchestrator's job is to invoke them in order and report the gate, NOT to execute their bodies inline. Inline-execution of even one sub-skill (e.g., build-preflight's repo exploration) burns the wall-clock budget before the chain finishes.

**Do NOT fabricate sub-skill outputs.** When you acknowledge a sub-skill via Read (because `Skill` returned Unknown), the sub-skill did **not** actually run — there is no output to consume. **Never invent preflight reports, profiling results, mode determinations, or any other sub-skill output.** Doing so silently overrides what the user actually told you. For every downstream decision (mode selection, pipeline type, build state), use:

1. The USER'S INPUT (`$ARGUMENTS`) — this is the authoritative source. If the user said "production mode", the mode is production. If the user said "build a canonical model from existing UC tables", the pipeline type is `domain-aligned`. Take their words at face value.
2. Design artifacts already in conversation or workspace context.
3. Explicit signals the user provided in this session.

If you need information the sub-skill would have produced and the user didn't provide it, **ASK the user** — never assume defaults.

Process exactly one sub-skill per delegation step: invoke (or acknowledge-via-Read), use the user's actual input for downstream decisions, advance. Trust each sub-skill with its own work; trust the user with the framing.

## Phase 4 gate

**Code Review & CI Passed?** — only checked in production mode at Step 4.

- Yes → Phase 5 Validate
- No → Rework (fix failures and resubmit)

## Sub-skills invoked

| Phase | Skill | When |
|---|---|---|
| 1 — Preflight | `/build-preflight` | Always |
| 2 — Infra setup | `/setup-dbt-project`, `/configure-sql-warehouse`, `/write-dbt-wrapper`, `/setup-databricks-asset-bundle`, `/setup-monitoring-and-logging` | Only when preflight reports `fresh` or `infra-only` |
| 3 — Per model | `/dbt-best-practices`, `/source-aligned` OR `/domain-aligned` OR `/consumer-aligned` (existing), `/run-dbt-on-databricks` | Production: every model. Prototype: file-driven, single model. |
| 3 — Artifacts | `/unit-test-report`, `/integration-test-report`, `/code-review-sign-off`, `/build-checklist` (existing) | Production only |
| 4 — Gate | (inline gate check) | Production only |
| Debug | `/troubleshoot-dbt-on-databricks` | On demand |

## Steps

### Step 1: Preflight

Invoke `/build-preflight`. Capture mode + DPLC-artifact-status-report + Databricks-readiness + build-state from its output.

If `/build-preflight` reports any blocking issue (e.g., production-mode required artifact absent and the user declined backfill), STOP and report the blocker.

### Step 2: Infrastructure setup (conditional)

If build-state is `fresh` or `infra-only`, invoke in order:

1. `/setup-dbt-project` — scaffold the dbt project (dbt_project.yml, profiles.yml, .sqlfluff, .pre-commit-config.yaml, .dbtignore, packages.yml)
2. `/configure-sql-warehouse` — provision or select the serverless SQL warehouse; wire profiles.yml
3. `/write-dbt-wrapper` — author dbt_wrapper.py
4. `/setup-databricks-asset-bundle` — write databricks.yml + per-dataset *.job.yml
5. `/setup-monitoring-and-logging` — cluster_log_conf + runbook

If build-state is `models-exist` already, skip Step 2.

### Step 3: Model authoring (per model)

For each model the user wants to build:

1. Delegate to **`/dbt-best-practices`** via the `Skill` tool — load rule set; severity adapts to mode from preflight.
2. **STOP and decide the pipeline type before invoking anything.** Read the user's input + design artifacts and pick exactly **one** of the three pipeline-build sub-skills below based on the cues. Do not invoke more than one. Do not invoke them in list order — branch on the cues:

   - **IF the user describes raw inbound data arriving at a schema** (cue words: *"sources land"*, *"data lands"*, *"landing zone"*, raw CSV/DAT/.out.gz files, *"ingest a feed"*, *"first hop from raw"*, named vendor feeds like Bloomberg/RDM/Moody's/FactSet/Refinitiv/MSCI) → delegate to **`/source-aligned`** via the `Skill` tool.
   - **ELSE IF the user describes building a canonical model from existing UC tables** (cue words: *"canonical model"*, *"UNION sources"*, *"consolidate tables"*, multiple existing UC tables already populated, *"domain-aligned product on top of X and Y"*, *"cross-source integration"*) → delegate to **`/domain-aligned`** via the `Skill` tool.
   - **ELSE IF the user describes a consumer-facing outbound layer** (cue words: *"consumer-facing layer"*, *"outbound mart"*, *"publish a curated view for downstream"*, *"consumer-aligned"*, building on top of an existing domain-aligned product) → delegate to **`/consumer-aligned`** via the `Skill` tool.
   - **ELSE** the cues are ambiguous: ask the user which pipeline type applies before delegating.

   In data-engineering idiom, *"sources land in [schema]"* specifically means raw inbound data is arriving at a landing zone -- that is `source-aligned`, **not** `domain-aligned`. Announce your routing decision in one line ("Pipeline type: source-aligned because the user said 'sources land in cspn_dev1'") before invoking, so the choice is visible in the trace.
3. After authoring, delegate to **`/run-dbt-on-databricks`** via the `Skill` tool for a smoke (local or bundle, depending on mode).

**After Step 3's per-model work completes in production mode, you MUST run the artifact chain.** Do not stop after `/run-dbt-on-databricks`. Delegate to each of the following in order via the `Skill` tool:

1. **`/unit-test-report`** — record unit test results for the model(s) just authored.
2. **`/integration-test-report`** — record integration test results.
3. **`/code-review-sign-off`** — record the code review approval.
4. **`/build-checklist`** — tick remaining items and confirm Phase 4 completion.

The artifact chain is non-optional in production mode -- skipping it means Phase 4's gate ("Code Review & CI Passed?") has no evidence and the orchestrator cannot determine the gate verdict. Invoke all four even when only a single model was authored; "all models authored" is true the moment the per-model loop exits, including for single-model runs.

In prototype mode, skip artifact skills; emit the promote-to-production checklist instead.

### Step 4: Gate check (production only)

Verify "Code Review & CI Passed?" — confirm each artifact from Step 3's production list is present and signed off.

- Yes → Phase 4 complete; route to `/dplc-validate`.
- No → Surface the failing artifacts and stop.

### Promote-to-production checklist (prototype mode only)

End of prototype run, print:

> You're at prototype-mode quality. To promote:
> 1. Run `/dplc-triage` to author marketplace-search + demand-tracker-entry + consumer-use-case-map
> 2. Run `/dplc-discovery` to author discovery artifacts
> 3. Run `/dplc-design` to author data-contract + data-model + transformation-spec
> 4. Re-run `/dplc-build` in production mode — same models will be tightened, artifact skills will run.
