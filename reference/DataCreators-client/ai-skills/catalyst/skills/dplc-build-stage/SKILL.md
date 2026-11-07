---
name: dplc-build-stage
description: >-
  Run the Deliver stage -- build, validate, and publish a data product. Use
  when the design is approved and you're ready to implement. Trigger phrases:
  "run Deliver", "run the Deliver stage", "build the product", "start Build",
  "implement the design", "deploy the product", "publish the product".
allowed-tools: Read Grep Glob
metadata:
  tier: orchestrator
  lifecycle-phase: cross-cutting
  dependencies:
    # Deliver stage = 1-orchestrator-per-phase. Stage orchestrator
    # delegates to phase sub-orchestrators; leaves are owned by those.
    # See docs/superpowers/specs/2026-05-14-dplc-build-skills-design.md
    # and docs/rationalization-pr94-to-pr95.md for the canonical layering.
    - dplc-build       # Phase 4 sub-orchestrator
    - dplc-validate    # Phase 5 sub-orchestrator
    - dplc-publish     # Phase 6 sub-orchestrator
  consumes:
    - data-contract
    - transformation-spec
    - data-model
  shared-components:
    core: []
    platforms: []
---

# Deliver Stage Orchestrator

Run all three phases of the **Deliver** stage in sequence by delegating
to each phase's sub-orchestrator:

| Phase | Sub-orchestrator | Purpose |
|:------|:-----------------|:--------|
| Phase 4 | `/dplc-build` | Build, test, and review the data product code |
| Phase 5 | `/dplc-validate` | Run UAT, DQ sign-off, integration tests |
| Phase 6 | `/dplc-publish` | Deploy to production, onboard consumers |

This stage orchestrator manages the **macro flow and gate transitions
between phases**. Each phase sub-orchestrator owns its detailed
sequencing (which leaf skills to invoke, in what order, with what
conditional gates). The 1-orchestrator-per-phase pattern is consistent
across all DPLC stages (see `dplc-design-stage` for the matching
shape).

---

## Skills Invoked

This orchestrator is a **delegating** stage orchestrator. It does
**not** invoke Phase 4/5/6 leaf skills (`source-aligned`,
`build-checklist`, `deployment-record`, etc.) directly -- those are
owned by the per-phase sub-orchestrators. Invoke each sub-orchestrator
via the `Skill` tool (or by reading `skills/<name>/SKILL.md` if the
harness has not yet registered the skill) -- never duplicate the
phase sub-orchestrator's work in this stage orchestrator. Never invoke
this orchestrator (`dplc-build-stage`) from inside itself; the slash
command names the stage you are already running.

| Sub-orchestrator | Phase | Required? |
|:-----------------|:------|:----------|
| `dplc-build` | Phase 4 -- Build | **Required -- always invoke** |
| `dplc-validate` | Phase 5 -- Validate | **Required -- always invoke** |
| `dplc-publish` | Phase 6 -- Publish | **Required -- always invoke** |

**Delegation rule:** for each phase that applies to this run, route
through the phase sub-orchestrator via the `Skill` tool
(slash-command equivalents: `/dplc-build`, `/dplc-validate`,
`/dplc-publish`). Do **not** invoke leaf skills (`source-aligned`,
`build-checklist`, `unit-test-report`, `code-review-sign-off`,
`integration-test-report`, `data-quality-sign-off`, `uat-sign-off`,
`deployment-record`, `consumer-onboarding-guide`, `release-notes`)
directly from this orchestrator -- they live one layer deeper, owned
by the phase sub-orchestrator. Inline invocation of leaves from the
stage orchestrator bypasses each phase's own conditional gates and
mode-aware logic (e.g., `dplc-build` is mode-aware:
prototype / production / lift-and-shift; skipping it loses that).

**Acknowledge and advance — don't inline-execute.** When you invoke a
phase sub-orchestrator (`Skill(dplc-build)`, `Skill(dplc-validate)`,
`Skill(dplc-publish)`) and it returns successfully, treat the phase as
complete and advance. When the `Skill` tool returns "Unknown skill"
(Catalyst skills aren't always in the runtime registry), READ the
phase sub-orchestrator's SKILL.md **once** as your acknowledgment of
delegation -- that read IS the delegation in this harness (the
behavior-test runner counts a `Read(skills/<name>/SKILL.md)` as a
sub-skill invocation, equivalent to a successful `Skill` call). Then
advance to the next phase.

Do **not** follow the sub-orchestrator's instructions inline by
reading its leaf SKILL.md files or its leaf templates. Each phase
sub-orchestrator owns its own phase; this stage orchestrator's job is
to invoke phases in order and present gate determinations, NOT to
execute the phase's body inline. Inline-execution cascades through
every leaf in every phase and exhausts the turn budget before reaching
the last phase.

Process exactly one phase per delegation step: invoke (or
acknowledge-via-Read), present the gate, advance. Trust the
sub-orchestrator with its leaves.

---

## Phase Gates

### Gate 4 -- Build Complete?

- All pipeline code implemented and passing unit tests
- Code review completed and signed off
- Build checklist items all resolved
- **Pass** -> Phase 5 | **Fail** -> Fix build issues

### Gate 5 -- Validated?

- Integration tests passing in pre-production environment
- Data quality metrics meet thresholds defined in the data contract
- UAT completed and signed off by the Data Owner or delegate
- **Pass** -> Phase 6 | **Fail** -> Fix defects and retest

### Gate 6 -- Published?

- Deployment record completed with environment details and rollback plan
- Consumer onboarding guide available
- Release notes published
- At least one consumer confirmed access and validated the product
- **Pass** -> Sustain stage | **Fail** -> Address deployment issues

---

## Sequencing

### Step 1 -- Verify Define stage is complete

The Deliver stage requires three Design-stage artifacts as inputs:
`data-contract.md`, `transformation-spec.md`, and `data-model.md`.

Determine whether the Define stage is complete using this order:

1. **First, check `$ARGUMENTS` and the conversation.** If the user
   explicitly states the design is approved (phrasings like "Design
   artifacts approved", "Define stage complete", "design is signed
   off", "design approved"), treat that as the authoritative signal.
   The user is the source of truth -- do **not** override their
   assertion with a filesystem check. Capture the assertion in
   `build-checklist` so reviewers can verify it later, and proceed
   to Step 2.
2. **Otherwise, check the workspace** for the three artifacts via
   `Glob`/`Read`. If all three are present, proceed to Step 2.
3. **Only if neither signal is present** (no user assertion **and**
   the artifacts are missing from the workspace), do not proceed.
   Direct the user to complete the Define stage first: "The data
   contract, transformation spec, and data model are required inputs
   for Build. Run `/dplc-design-stage [product-name]` to complete the
   Define stage."

The filesystem check is a fallback, not a gate. Skill behavior tests
and real engagements both rely on conversational context as primary
input -- artifacts on disk are confirmation, not a precondition.

### Step 2 -- Phase 4: Build

**Delegate to the `dplc-build` sub-orchestrator.** Use the `Skill` tool
with `skill: dplc-build` (slash-command equivalent: `/dplc-build`). Do
not invoke `source-aligned` / `domain-aligned` / `consumer-aligned` /
`build-checklist` / `unit-test-report` / `code-review-sign-off`
directly -- those are leaves owned by `/dplc-build`, which decides
which pipeline type applies (based on user context: raw files vs UC
tables vs consumer mart) and runs the appropriate sub-skills in
order. `/dplc-build` is mode-aware (prototype / production /
lift-and-shift) and skipping it loses that branching.

Carry forward to `/dplc-build`:
- The user's product name and the location of the design artifacts
  (`data-contract.md`, `transformation-spec.md`, `data-model.md`).
- Any user assertion about the pipeline type (raw feed vs canonical
  vs consumer-facing) so `/dplc-build` can route without re-asking.

Present `/dplc-build`'s Gate 4 ("Built and Reviewed?") determination
to the user. Pause for confirmation before advancing to Phase 5.

### Step 3 -- Phase 5: Validate

**Delegate to the `dplc-validate` sub-orchestrator.** Use the `Skill`
tool with `skill: dplc-validate` (slash-command equivalent:
`/dplc-validate`). Do not invoke `integration-test-report` /
`data-quality-sign-off` / `uat-sign-off` / `dataops-handoff-draft`
directly -- those are leaves owned by `/dplc-validate`, which
sequences them and references the data contract for DQ thresholds.

Carry forward to `/dplc-validate`:
- `build-checklist`, `unit-test-report`, `code-review-sign-off`
  outputs from Phase 4.
- The data contract (for DQ threshold comparison) and the PRD (for
  UAT scenario derivation).

Present `/dplc-validate`'s Gate 5 ("UAT Passed & Accepted?")
determination to the user. Pause for confirmation before advancing
to Phase 6.

### Step 4 -- Phase 6: Publish

**Delegate to the `dplc-publish` sub-orchestrator.** Use the `Skill`
tool with `skill: dplc-publish` (slash-command equivalent:
`/dplc-publish`). Do not invoke `deployment-record` /
`consumer-onboarding-guide` / `release-notes` /
`marketplace-search` directly -- those are leaves owned by
`/dplc-publish`, which sequences them and verifies the marketplace
listing.

Carry forward to `/dplc-publish`:
- `uat-sign-off` and the data contract from Phase 5.
- The consumer use case map (for onboarding-guide scoping).

Present `/dplc-publish`'s Gate 6 ("Published?") determination to
the user.

### Step 5 -- Summarize Deliver stage

> "Deliver stage complete.
> - Phase 4: Build complete, code reviewed, tests passing
> - Phase 5: Integration tests, DQ, and UAT all signed off
> - Phase 6: Deployed, consumers onboarded, release notes published
>
> The product is live. Run `/dplc-ship-stage [product-name]` to set up
> operational monitoring and support."

---

## Notes

- The data contract from Phase 3 is the source of truth for validation.
  Data quality sign-off must reference contract thresholds, not ad hoc
  criteria.
- Pipeline-type routing (source-aligned / domain-aligned / consumer-aligned)
  is the responsibility of `/dplc-build`, not this stage orchestrator. See
  that skill's notes for routing cues and the per-pipeline-type leaf chain.
- For feature-level work, the Build phase may be lighter -- updating an
  existing pipeline rather than generating from scratch. `/dplc-build` checks
  for existing pipeline artifacts before generating new ones.
- Do not skip UAT. The Data Owner must confirm the product works as specified
  before it goes to production.
