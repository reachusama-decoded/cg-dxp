---
name: dplc-validate
description: >-
  Phase 5 Validate -- sub-orchestrator of dplc-build-stage. Drives data-quality
  sign-off, UAT sign-off, and DataOps handoff finalization, then reports the
  Phase 5 gate decision. Use once Phase 4 Build is complete (CI green, code
  reviewed, integration tests passing). Trigger phrases: "validate the data
  product", "Phase 5", "run UAT", "data quality sign-off", "ready to publish".
allowed-tools: Read Grep
metadata:
  lifecycle-phase: phase-5-validate
  dependencies:
    - integration-test-report
    - data-quality-sign-off
    - uat-sign-off
    - dataops-handoff-draft
  consumes:
    - build-checklist
    - unit-test-report
    - code-review-sign-off
    - data-contract
    - product-requirements-document
  shared-components:
    core: []
    platforms: []
  standards: [DBX-SEC-002]
---

# Phase 5: Validate Orchestrator

This orchestrator guides you through **Phase 5 -- Validate** of the Data Product
Lifecycle (see `rfd/0002/README.md` for the full definition).

**Phase 5 purpose:** Confirm the data product meets business requirements,
governance standards, and operational readiness before go-live. The Data
Steward and Data Owner formally sign off on data quality and acceptance; the
DataOps team accepts the operational handoff.

**Who this is for:** A Data Product Creator or Data Product Manager whose
product has cleared Phase 4 Build (CI green, code reviewed, integration tests
passing) and now needs business and governance acceptance before publishing.

**Phase 5 gate:** *UAT Passed & Accepted?*
- Data Steward has tested against real-world scenarios and signed off
- Data quality validated against contract thresholds
- Governance and compliance checks complete (classification, access, retention)
- DataOps handoff package reviewed and accepted (when DataOps will own)
- Non-functional requirements verified
- Yes -> Publish (Phase 6)
- No -> Rework (return to Build or Design to address issues)

---

## Progress Reporting

As you work through each step, report progress clearly so the user can
follow along. For each sub-skill or action:

1. **Announce** what you're about to do before doing it
2. **Report** what you found or produced after each step
3. **Show counts and specifics** -- not "ran DQ checks" but "Validated 12 DQ
   rules from data-contract; 11 passed, 1 conditional pass with waiver"
4. **Use a checklist** format so the user can see what's done and what's left:

Example:
```
- [x] Read Phase 4 artifacts (integration-test-report, build-checklist,
      unit-test-report, code-review-sign-off found)
- [x] Read data contract -- 12 DQ rules, 4 SLA thresholds
- [x] integration-test-report: confirmed end-to-end pass in pre-prod
- [x] data-quality-sign-off: 11/12 rules pass, 1 waived (Data Owner approval)
- [ ] uat-sign-off: collecting Data Steward sign-off...
- [ ] dataops-handoff-draft: finalize
- [ ] gate determination
```

Never run silently. The user should always know where you are.

---

## Sub-Skills Invoked

| Skill | Type | Purpose | Required? |
|:------|:-----|:--------|:----------|
| `integration-test-report` | document | End-to-end pipeline test results in pre-prod / staging | Required if not already produced in Phase 4 |
| `data-quality-sign-off` | document | Formal DQ validation against data contract thresholds | Required |
| `uat-sign-off` | document | Data Steward / Data Owner business acceptance | Required |
| `dataops-handoff-draft` | document | Final operational handoff package | Required if DataOps will own; otherwise Optional |

This orchestrator is **artifact-driven**, not data-driven. The actual UAT
testing, DQ probe execution, and integration test runs are performed by the
delivery team in their UAT/staging environment **outside this skill**. The
orchestrator collects evidence, drives the sign-off documents, and renders
the gate decision.

See [Notes -> Environment connectivity](#notes) for why live UAT/staging
probes are not invoked here.

---

## Sequencing

### Step 1 -- Read prior-phase artifacts

Before asking the user anything, check the conversation for prior phase
artifacts. The Validate orchestrator is heavily dependent on Phase 3 and
Phase 4 outputs; surface what is and is not in context:

**From Phase 3 Design (required):**
- `data-contract` -- DQ rules, SLA thresholds, schema. **This is the source
  of truth for validation. DQ sign-off must reference contract thresholds,
  not ad hoc checks.**
- `dataops-handoff-draft` -- the in-progress operational package, finalized
  in this phase

**From Phase 4 Build (required):**
- `build-checklist` -- confirms build tasks are complete
- `unit-test-report` -- confirms component-level testing passed
- `code-review-sign-off` -- confirms peer review accepted the implementation
- `integration-test-report` -- if already produced in Phase 4; otherwise
  produce it in Step 2

**From Phase 2 Discovery (recommended):**
- `product-requirements-document` -- acceptance criteria the UAT must verify

If any of these are missing, ask the user where they live (path or filename)
or whether the prior phase was skipped. Do not fabricate artifact content.
Note skipped artifacts so they appear in the gate report.

Also ask (if not already known): which UAT / pre-production environment was
used for the testing being signed off on (e.g., catalog name, workspace
host)? This is recorded in the sign-off documents but **the orchestrator
does not connect to it**.

### Step 2 -- Invoke `integration-test-report` (if not already produced)

If a Phase 4 `integration-test-report` already exists in context, skip this
step and carry it forward. If not, invoke `integration-test-report` to
capture the end-to-end pipeline test outcomes the team ran in pre-prod /
staging. Pass as context:

- The data contract from Step 1 (defines expected pipeline behavior)
- NFR thresholds from Phase 3 (`nfr-specification`, if available)
- The user-described UAT environment

Confirm the report records: pass/fail by scenario, performance against NFR
thresholds, defect status. Any failed scenarios block this orchestrator --
return to Build to address them.

### Step 3 -- Invoke `data-quality-sign-off` (Required)

Call `data-quality-sign-off` with the product context. Pass as context:

- The data contract from Step 1 (DQ rules, severity, thresholds)
- `unit-test-report` and `integration-test-report` from prior steps
- The team's recorded DQ probe results from the UAT environment

The artifact must record, for each DQ rule in the contract:
- Rule definition + threshold
- Actual measured value from UAT
- Pass / fail / conditional-pass-with-waiver
- For waivers: who approved, scope, expiry

The Data Owner and engineering lead are the named sign-off parties. Do not
finalize the document until both names are recorded.

### Step 4 -- Invoke `uat-sign-off` (Required)

Call `uat-sign-off` with the product context. Pass as context:

- The PRD acceptance criteria from Phase 2 (if available)
- The `data-quality-sign-off` from Step 3
- The `consumer-use-case-map` from Phase 1 (the use cases UAT must exercise)
- The team's recorded UAT scenario results

The artifact must record:
- UAT scope (which use cases / acceptance criteria were tested)
- Scenario-by-scenario pass / fail
- Defects logged + disposition (fixed, deferred-with-waiver, blocking)
- Data Steward sign-off with date
- Conditions for production deployment (if any)

Critical (blocking) defects must be resolved before sign-off. Conditional
sign-offs with deferrable defects are acceptable provided each defect has
an owner and target resolution date.

### Step 5 -- Finalize `dataops-handoff-draft` (Required if DataOps will own)

Ask the user: "Will DataOps assume ownership of this product after Publish?"

- **Yes:** Invoke `dataops-handoff-draft` to finalize the package authored
  in Phase 3. Pass as context: the runbook outline from Phase 3 (if any),
  the integration test report, the DQ sign-off, NFR thresholds. Confirm
  the package is reviewed and accepted by the named DataOps lead before
  marking complete.
- **No (team will self-operate):** Skip this step. Record in the gate
  determination that DataOps handoff is N/A.

### Step 6 -- Gate determination + report

Assess the Phase 5 gate (*UAT Passed & Accepted?*) by checking each
condition:

1. Integration tests pass in pre-prod / staging
2. Data Owner + engineering lead signed `data-quality-sign-off`
3. Data Steward signed `uat-sign-off` (or conditional sign-off with
   tracked defects)
4. Governance / compliance verifications recorded (classification,
   access controls, retention)
5. NFRs verified against thresholds
6. DataOps handoff accepted (when applicable)

**If all conditions met:**
> "Phase 5 Validate complete.
> - Integration tests: passed in [env]
> - Data quality: [N/M rules passed, waivers noted]
> - UAT: signed off by [Data Steward], [date]
> - DataOps handoff: [accepted by ... | N/A self-operate]
> - NFRs: verified
>
> You are ready for Phase 6 Publish. Run `/dplc-publish [product-name]`
> to continue."

**If conditional sign-off with deferred defects:**
> Record the open defects, owners, and target dates. State that the
> product may proceed to Publish only if the Data Owner accepts the
> conditional sign-off in writing. Do not declare the gate unconditionally
> passed.

**If UAT or DQ failed:**
> State the specific failures from the sign-off documents. Recommend
> returning to Phase 4 Build to address. List what must change for
> re-validation. Do not proceed to Publish.

**If governance / compliance check fails:**
> State the specific control gap (e.g., access not yet provisioned,
> classification mismatch, retention not configured). Recommend
> returning to Phase 3 Design or to the relevant data steward.

### Step 7 -- Invite feedback

After the gate determination, append this one-line prompt as the final line
of your response:

> "Anything to flag about this run? Hit enter to skip, or tell me what
> worked / what didn't."

Then:
- **If the user replies with anything substantive** -- a sentence, a
  reaction, a problem description, even a short "worked great": invoke
  the `catalyst-feedback` skill with `$ARGUMENTS = "dplc-validate
  reply=<their reply verbatim>"`. The skill extracts session context
  (sub-skills that ran, current phase, any errors), composes a draft
  issue, **shows the user the full draft for review**, and files after
  they confirm.
- **If the user hits enter / moves on / gives a non-substantive reply**
  (e.g. just "k", "ok", an emoji alone): do nothing. No file, no
  re-prompt. Silence means satisfied.

---

## Notes

### Environment connectivity

This orchestrator is intentionally **artifact-driven**. It does not connect
to dev / staging / UAT environments to re-run DQ probes or integration tests.
Reasons:

- Per `rfd/0002/README.md` Phase 5 exit criteria, the required outputs are
  **records of testing** -- `data-quality-sign-off`, `uat-sign-off`,
  finalized `dataops-handoff-draft` -- not live re-tests.
- `skills/connect-databricks` resolves a single workspace via
  `DATABRICKS_HOST` / `DATABRICKS_CLIENT_ID` / `DATABRICKS_CLIENT_SECRET`
  (OAuth M2M credentials per DBX-SEC-002). There is no dev / staging / UAT /
  prod profile model today, so the orchestrator cannot reliably target a
  specific UAT workspace without ambiguity.
- Live re-validation belongs to a future skill that depends on
  multi-environment connection profiles.

The team performs DQ probes and integration runs in their UAT environment
**outside this skill**, then this orchestrator collects, structures, and
formalizes the evidence into the sign-off documents.

### Iteration

Phase 5 is iterative with Phase 4. If UAT or DQ uncovers a defect, it is
correct to return to Build, fix, and re-enter Validate. Do not push partial
sign-offs forward to satisfy a calendar. The Phase 5 gate exists to keep
broken products out of production.

### Reuse the contract

The data contract from Phase 3 is the single source of truth for
validation. DQ sign-off must reference contract rule IDs and thresholds
verbatim. If a check the team wants to run is not in the contract, that
is a contract gap -- update the contract (back to Phase 3) rather than
sign off on an undocumented threshold.

### Feature-level vs. product-level Validate

For feature work on an existing live product, scope sign-offs to the
delta:
- DQ sign-off covers rules added or changed by the feature
- UAT sign-off covers the new acceptance criteria
- Carry over prior sign-offs by reference; do not re-sign unchanged scope

The gate decision still applies at the feature level.
