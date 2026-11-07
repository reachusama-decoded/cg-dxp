---
name: dplc-ship-stage
description: >-
  Run the Ship stage -- operate, monitor, and evolve. Use when the product
  is in production. Trigger phrases: "set up monitoring", "create a runbook",
  "product is live", "run Sustain", "operate the product", "deprecate",
  "evolve the product", "handle an incident".
allowed-tools: Read Grep
metadata:
  tier: orchestrator
  lifecycle-phase: cross-cutting
  dependencies:
    - runbook
    - incident-log
    - sla-dashboard-spec
    - warranty-handoff-sign-off
    - usage-analytics-report
    - downstream-impact-assessment
    - deprecation-notice
    - dplc-design-stage
  consumes:
    - data-contract
    - architecture-diagram
    - dataops-handoff-draft
  shared-components:
    core: []
    platforms: []
---

# Sustain Stage Orchestrator

Run both phases of the **Sustain** stage:

| Phase | Name | Purpose |
|:------|:-----|:--------|
| Phase 7 | Operate | Establish operational support, monitoring, and incident response |
| Phase 8 | Evolve | Assess usage, plan changes, deprecate when appropriate |

Phase 7 runs once after go-live to establish the operational baseline.
Phase 8 is ongoing -- it triggers whenever the product needs to change.

---

## Skills Invoked

### Phase 7 -- Operate

| Skill | Type | Purpose |
|:------|:-----|:--------|
| `runbook` | document | Operational procedures, troubleshooting, escalation paths |
| `incident-log` | document | Record and track production incidents |
| `sla-dashboard-spec` | document | Define monitoring dashboards and SLA alerting |
| `warranty-handoff-sign-off` | document | Formal handoff from build team to operations |

### Phase 8 -- Evolve

| Skill | Type | Purpose |
|:------|:-----|:--------|
| `usage-analytics-report` | document | Analyze adoption, consumption patterns, and ROI |
| `downstream-impact-assessment` | document | Assess impact of proposed changes on consumers |
| `deprecation-notice` | document | Formal notice when retiring or replacing a product |

---

## Phase Gates

### Gate 7 -- Operational?

- Runbook published and reviewed by the operations team
- SLA dashboard spec defined and monitoring configured
- Warranty handoff signed by both build team and operations team
- Incident response process established
- **Pass** -> Product is fully operational | **Fail** -> Address ops gaps

### Gate 8 -- Evolution Decision

Phase 8 does not have a single pass/fail gate. Instead, each evolution
trigger results in a routing decision:

| Change Type | Action |
|:------------|:-------|
| Minor update (new column, threshold change, bug fix) | Handle in Sustain -- update contract, run impact assessment, deploy |
| Major change (new source, redesigned model, new consumers) | Loop back to Define stage (`dplc-design-stage`) for the change |
| Deprecation (product retired, replaced, or sunset) | Invoke `deprecation-notice` and `downstream-impact-assessment` |
| No change needed (healthy, well-adopted) | Continue monitoring; revisit on next review cycle |

---

## Sequencing

### Step 1 -- Determine entry point

Check conversation and $ARGUMENTS for context:

- **Just deployed (coming from Deliver):** Start with Phase 7 to establish
  operational baseline.
- **Product already operational:** Skip Phase 7 setup, go directly to the
  specific Operate or Evolve task the user needs (e.g., "log an incident",
  "assess a change", "deprecate").
- **Reviewing an existing product:** Start with `usage-analytics-report` to
  understand current state before making decisions.

### Step 2 -- Phase 7: Operate (first-time setup)

Execute in order:

1. Invoke `runbook` -- pull operational context from the design artifacts
   (data contract SLAs, architecture diagram, dataops-handoff-draft if it
   exists from Phase 3)
2. Invoke `sla-dashboard-spec` -- reference the data contract SLA thresholds
   to define monitoring and alerting
3. Invoke `warranty-handoff-sign-off` -- formal handoff from the build team
   to the operations team

Present Gate 7 determination. The product is now fully operational.

For ongoing incidents, invoke `incident-log` as needed -- this is not a
one-time setup but a recurring operational activity.

### Step 3 -- Phase 8: Evolve (ongoing)

When the user triggers an evolution activity:

**For usage review:**
1. Invoke `usage-analytics-report` to analyze adoption and consumption
2. Based on findings, recommend: continue as-is, optimize, or deprecate

**For proposed changes:**
1. Invoke `downstream-impact-assessment` to evaluate consumer impact
2. Based on severity:
   - Minor -> update the data contract version, deploy the change
   - Major -> route back to `dplc-design-stage` for a full lifecycle pass

**For deprecation:**
1. Invoke `downstream-impact-assessment` first -- understand who is affected
2. Invoke `deprecation-notice` with timeline, migration path, and consumer
   communication plan
3. Coordinate with consumers for migration before decommissioning

### Step 4 -- Summarize

For Phase 7 completion:
> "Operate setup complete. Runbook published, SLA monitoring defined,
> warranty handoff signed. The product is in steady-state operations."

For Phase 8 activities, summarize the specific action taken and its outcome.

---

## Loopback Guidance

The lifecycle is circular. Sustain feeds back into Define when products need
significant change. Use these rules:

| Indicator | Route |
|:----------|:------|
| Schema-breaking change or new source system | `dplc-design-stage` (full Define pass) |
| New consumer type with different SLA requirements | `dplc-design-stage` (at least Discovery + Design) |
| Performance optimization without schema change | Handle in Sustain |
| Bug fix or data quality remediation | Handle in Sustain |
| Product no longer needed | Deprecation flow in Phase 8 |

When looping back to Define, carry forward all existing artifacts. The
Define stage should detect existing artifacts and update them rather than
recreating from scratch.

---

## Notes

- Phase 7 artifacts should reference the data contract as the source of
  truth for SLAs. Do not define SLA thresholds in the runbook that differ
  from the contract.
- The warranty handoff is a formal gate. The build team is not done until
  operations has accepted the handoff. Do not let this become a formality --
  operations must confirm they have the runbook, access, and understanding
  to support the product.
- Usage analytics should be reviewed periodically (quarterly recommended).
  Products with zero consumption for two consecutive review cycles should
  be candidates for deprecation.
- Deprecation is not deletion. The deprecation notice defines a sunset
  timeline that gives consumers time to migrate. Minimum notice period
  should align with the organization's data product deprecation policy.
