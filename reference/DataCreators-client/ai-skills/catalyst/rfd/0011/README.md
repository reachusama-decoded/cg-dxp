---
authors: MRQL
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/87
---

# RFD 0011 DAG Standards

## Problem

EDO is building the paved path for data product creation, with Astronomer
as the orchestration layer. At full scale the paved path will host
thousands of Airflow DAGs across domain teams, writing to Databricks
(Unity Catalog), Dremio, and S3. To manage and scale that footprint, every
DAG on the paved path needs to meet a consistent quality bar from day one.

Without shared DAG standards, the risks at thousands-of-DAGs scale are:

* **Reruns become unsafe.** A DAG that is not idempotent can double-insert
  rows, advance an external checkpoint, or leave Unity Catalog and S3 out
  of sync when re-run for the same logical date. At scale, operators cannot
  rely on tribal knowledge to know which DAGs are safe to rerun.
* **Intermittent cloud failures create operational overhead.** Transient
  failures (network blips, cluster cold-starts, throttled APIs) are a
  routine fact of cloud workloads, and a simple rerun of a failed task is
  usually all that's needed. Without a shared retry policy, those failures
  land on operators instead of self-healing, and the overhead scales
  linearly with DAG count.
* **Resourcing becomes implicit.** Tasks submitted to whichever pool, queue,
  or cluster the author copied from a neighbor produce noisy neighbors and
  oversized clusters that scale poorly.
* **Incident response can't scale.** Owner, alerting, and SLA fields only
  help operations if they're set consistently on every DAG. Leave it to
  author discretion and a 3am failure sits unrouted; ownership is
  ambiguous; there's no shared bar for what counts as late.
* **Skill-generated DAGs encode whatever defaults we ship.** As more of the
  paved path is authored through Catalyst skills (`generate-dag` and
  successors), whatever those skills emit becomes the de facto standard.
  The skill defaults must encode this RFD, not the other way around.

The cost of getting this wrong would show up at scale: oncall pages for
problems that a retry policy would have absorbed, backfills that take days
because DAGs cannot be safely replayed, and platform spend that scales with
carelessness rather than workload.

We need a shared, enforceable definition of what a "good" paved-path DAG
looks like so authors, reviewers, and the skills that generate DAGs all
aim at the same bar.

## Background

We've had operational issues in the past with DAGs that were not properly
configured: missing retries, missing owners, non-idempotent writes that
broke on rerun. The pain is not limited to the DAG definition itself. A
single DAG task often hands work off to a Databricks job, a dbt run on a
SQL warehouse, or a Kubernetes pod the task spins up, and a
misconfiguration at any of those layers produces the same operational
drag. The standard this RFD proposes has to cover the entire compute
envelope a DAG triggers, not just the DAG file.

This standard binds to several other RFDs:

* **RFD 0008** — the `PY-AIRFLOW-*` rule bodies live in
  [`rfd/0008/python/airflow.md`](../0008/python/airflow.md) (ID-keyed, with a
  `Since:` field), matching how every other RFD 0008 language category works;
  this RFD reads as the decision record explaining *why* the rules exist and
  links to that home. This PR performs that physical split — the rule bodies now
  live in the RFD 0008 category file and this RFD links to them.
* **RFD 0009 (ODCS)** — asset-driven triggers (PY-AIRFLOW-019) depend on the
  upstream data contract; it is the subscription point.
* **RFD 0007** — the data-ready event v2 contract that PY-AIRFLOW-015 emits and
  asset subscriptions consume.
* **RFD 0002 (DPLC)** — this standard governs the **Build** phase; the
  `lifecycle_phase` tag is anchored to the DPLC phases.
* **RFD 0004 (`promotions.yml`)** — the trunk-based promotion mechanism behind
  "Astronomer deploy gated on green CI." Partial development stays in
  non-production: author in `prototype` mode, then promote to `production` through
  `promotions.yml`, with the `lifecycle_phase` tag as the in-DAG signal. This RFD
  deliberately does **not** define a separate feature-flag or branch scheme —
  gated release lives in RFD 0004 (promotion) and RFD 0002 (DPLC phases).

## Proposal

A paved-path DAG MUST satisfy the `PY-AIRFLOW-*` standards. The canonical,
ID-keyed rule bodies — decision, rationale, mechanism, and examples — live in
[`rfd/0008/python/airflow.md`](../0008/python/airflow.md), in the same house
format as every other RFD 0008 language category. **RFD 0011 is the decision
record**: it explains *why* the rules exist; the rule home says *what to do* and
how. CI checks (`assert_dag_compliant`, ruff, secret-scan) enforce the
machine-checkable rules; the rest are PR-review checklist items.

Three principles run through the set:

* **Worker slots are the scarce resource** at thousands-of-DAGs scale, so long
  waits must release them and parallelism is bounded.
* **Every run is idempotent against its processing window** — a rerun produces the
  same end state, never a double-write.
* **DAGs default to asset-driven triggering** — react to data, not the clock.

The rules, by ID:

| ID | Rule | Severity |
|---|---|---|
| [PY-AIRFLOW-001](../0008/python/airflow.md#py-airflow-001--derive-partitions-and-paths-from-the-processing-window) | Derive partitions and paths from the processing window | error |
| [PY-AIRFLOW-002](../0008/python/airflow.md#py-airflow-002--pin-start_date-to-a-static-utc-datetime) | Pin `start_date` to a static UTC datetime | error |
| [PY-AIRFLOW-003](../0008/python/airflow.md#py-airflow-003--declare-a-retry-policy-on-every-task) | Declare a retry policy on every task | error |
| [PY-AIRFLOW-004](../0008/python/airflow.md#py-airflow-004--use-exponential-backoff-for-retries) | Use exponential backoff for retries | warning |
| [PY-AIRFLOW-005](../0008/python/airflow.md#py-airflow-005--declare-compute-via-approved-t-shirt-tiers) | Declare compute via approved T-shirt tiers | error |
| [PY-AIRFLOW-006](../0008/python/airflow.md#py-airflow-006--declare-the-schedule-explicitly-and-set-catchup-to-intent) | Declare the schedule explicitly and set `catchup` to intent | warning |
| [PY-AIRFLOW-007](../0008/python/airflow.md#py-airflow-007--tag-every-dag-with-the-required-tag-set) | Tag every DAG with the required tag set | error |
| [PY-AIRFLOW-008](../0008/python/airflow.md#py-airflow-008--rely-on-platform-datadog-alerting-not-a-per-dag-callback) | Rely on platform Datadog alerting, not a per-DAG callback | warning |
| [PY-AIRFLOW-009](../0008/python/airflow.md#py-airflow-009--no-io-at-module-scope) | No I/O at module scope; keep DAG parsing cheap | error |
| [PY-AIRFLOW-010](../0008/python/airflow.md#py-airflow-010--prefer-the-taskflow-api-for-new-code) | Prefer the TaskFlow API for new code | advisory |
| [PY-AIRFLOW-011](../0008/python/airflow.md#py-airflow-011--keep-xcom-to-metadata-not-row-data) | Keep XCom to metadata, not row data | warning |
| [PY-AIRFLOW-012](../0008/python/airflow.md#py-airflow-012--follow-the-dag-id-naming-convention) | Follow the DAG ID naming convention | warning |
| [PY-AIRFLOW-013](../0008/python/airflow.md#py-airflow-013--resolve-secrets-through-connections-and-variables) | Resolve secrets through Connections and Variables | error |
| [PY-AIRFLOW-014](../0008/python/airflow.md#py-airflow-014--cover-every-dag-with-a-pytest-integrity-test) | Cover every DAG with a pytest integrity test | error |
| [PY-AIRFLOW-015](../0008/python/airflow.md#py-airflow-015--emit-the-data-ready-event-only-on-success) | Emit the data-ready event only on success | error |
| [PY-AIRFLOW-016](../0008/python/airflow.md#py-airflow-016--fail-fast-on-deterministic-errors) | Fail fast on deterministic errors | warning |
| [PY-AIRFLOW-017](../0008/python/airflow.md#py-airflow-017--release-the-worker-slot-on-long-waits-and-bound-the-timeout) | Release the worker slot on long waits and bound the timeout | error |
| [PY-AIRFLOW-018](../0008/python/airflow.md#py-airflow-018--bound-dag-parallelism) | Bound DAG parallelism (`max_active_runs` / `max_active_tasks`) | warning |
| [PY-AIRFLOW-019](../0008/python/airflow.md#py-airflow-019--default-to-asset-driven-scheduling) | Default to asset-driven scheduling | warning |
| [PY-AIRFLOW-020](../0008/python/airflow.md#py-airflow-020--never-pass-secrets-as-operator-arguments) | Never pass secrets as operator arguments | error |
| [PY-AIRFLOW-021](../0008/python/airflow.md#py-airflow-021--develop-and-test-dags-locally-before-pushing) | Develop and test DAGs locally before pushing | advisory |
| [PY-AIRFLOW-022](../0008/python/airflow.md#py-airflow-022--enforce-the-standard-with-a-value-bounded-structural-test) | Enforce the standard with a value-bounded structural test | error |
| [PY-AIRFLOW-023](../0008/python/airflow.md#py-airflow-023--one-task-is-one-logical-step) | One task is one logical step | warning |
| [PY-AIRFLOW-024](../0008/python/airflow.md#py-airflow-024--keep-dag-files-thin-shared-logic-in-a-versioned-library) | Keep DAG files thin; shared logic in a versioned library | warning |

### Skills suite

Four production-tier skills deliver the rules above. Together they form
the authoring and deploy loop for paved-path DAGs:

* **`connect-astro`** — Astronomer workspace and deployment auth via
  the Astro CLI. No personal access tokens (PATs); auth flows through
  the same identity layer used everywhere else.
* **`generate-dag`** — composes a TaskFlow DAG that conforms to the
  `PY-AIRFLOW-*` rules above. Supports dag-factory (default) and
  astro-blueprints emission patterns. Mode-aware: prototype,
  production, lift-and-shift. Carries the rule IDs it implements in
  its metadata block so reviewers can audit which rules a generated
  DAG covers. Composes with `setup-databricks-asset-bundle` so the
  emitted DAG resolves cluster sizing and job IDs from the bundle.
* **`dplc-build`** — orchestrator that drives `generate-dag`
  end-to-end for a data product, wiring in scaffold, contract, and
  bundle skills.
* **Deploy path** — `databricks bundle deploy` and `astro deploy` are
  invoked by CI from the deploy manifest; there is no dedicated deploy
  skill in scope. A `deploy-astro` skill is tracked as a follow-up if
  the deploy step grows beyond mechanical invocation.

The skills compose. `connect-astro` is a prerequisite for any deploy
flow; `generate-dag` is followed by CI validation before deploy.

### Authoring vs. deploying

`generate-dag` is **adaptive** — it makes judgments about how to model
the DAG given the source contract and the author's intent. Validate
and deploy steps are **deterministic**: given the same inputs they
take the same actions. Adaptive work belongs in skills; deterministic
work belongs in scripts. This split keeps review cadences appropriate
to each (skills evolve with new patterns; scripts only change when the
mechanism does).

## Alternatives

### Alternative A: Per-team standards, no shared bar

Each domain team writes its own DAG conventions, enforced in its own repo.
We rejected this because Asset-driven triggers and shared operational
tooling (oncall, lineage, runbooks) only work if every DAG behaves
consistently across domains. Per-team standards also undermine the
skill-driven authoring model.

### Alternative B: Adopt Astronomer's defaults as-is

Astronomer publishes opinionated defaults via `astro-runtime` and reference
DAGs. We considered adopting those wholesale. Rejected because the defaults
don't cover idempotency against Unity Catalog writes, don't encode our
Asset URI conventions, and don't speak to our T-shirt-size cluster
profiles. We will adopt Astronomer defaults where they apply and extend
rather than replace them.

### Alternative C: Enforce via review checklist only, no CI

The cheapest path is a markdown checklist that reviewers paste into PRs.
Rejected because review fatigue lets issues slip through, and skill-generated
DAGs would still need a programmatic check before submission. CI enforcement
also lets us measure the standard's adoption over time.

## Impact

### Affected audiences

* **Domain DAG authors** get a written standard plus CI feedback. Net
  reduction in review cycles, but a short-term cost to learn the conventions.
* **Platform team** owns `edo_airflow_lib` (helpers, cluster profiles,
  callbacks) and the `assert_dag_compliant` checker.
* **Catalyst skill authors** update `generate-dag` and downstream skills to
  emit compliant DAGs by default.
* **Oncall** benefits from consistent ownership tags, SLAs, and on-failure
  routing.
* **Existing DAGs.** The full rule set applies at authoring time going
  forward, and existing DAGs are retrofitted as they're touched — but
  "retrofitted opportunistically" is not a strategy for the incident-response
  basics, so two policies bound it:
  * **Compliance floor.** Every existing DAG must carry the minimum
    incident-response bar — `owner`, `l1_xmatters_group`, and `criticality`
    tags, so the platform's Datadog alert routes to a named team — regardless
    of whether it is otherwise touched. The
    per-team remediation schedule is set by the Platform team; a hard
    cross-team calendar deadline is not fixed in this RFD without that buy-in
    (an unbacked deadline is worse than an honest schedule).
  * **Migration cutover.** Teams moving from Composer / MWAA / self-hosted
    Airflow onto Astronomer comply **at cutover**, not opportunistically — the
    migration is the cheapest moment to bring a DAG up to standard. The
    `generate-dag` lift-and-shift mode supports this.

### Operational changes

* Astronomer deploy pipelines add the compliance check as a required gate.
* The runbook template is updated to reference the standard sections
  that map to runbook entries.
* Oncall pulls `owner` and `tags` directly from the DAG; teams that change
  ownership update the DAG, not a side document.

### Governance

* **Owners.** The Data Platform team (Airflow track) owns the rule set
  and the shared `edo_airflow_lib` helpers. The Skills team owns
  `generate-dag`, `dplc-build`, and the rest of the skills suite. New
  rules or rule changes go through this RFD's PR workflow.
* **Review cadence.** Quarterly. Each review checks whether new
  Airflow / Astronomer features warrant new rules, whether existing
  rules are still pulling their weight, and whether the skill defaults
  still match the rule set.
* **Waivers.** A DAG that can't meet a rule for a documented reason records
  the waiver inline in `doc_md` with the rule ID, the rationale, an approver,
  and an expiry.
  * **Approval:** MUST-level rules require Platform-team sign-off; SHOULD-level
    rules can be approved by the domain team lead.
  * **Default expiry:** one quarter — long enough to plan a fix, short enough
    to force a recheck.
  * **On expiry:** CI **blocks** the deploy for an expired MUST-level waiver
    (with a 30-day pre-expiry warning) and **warns** for an expired SHOULD-level
    waiver. A waiver whose expiry isn't enforced is a permanent exemption, not
    a waiver.
  * CI surfaces all waivers in a per-repo dashboard so they don't accumulate
    silently.
* **Tracked follow-ups.** Named here so they don't drift into "future work";
  each gets a ticket with a Platform-team owner. (The physical split of the rule
  bodies into `rfd/0008/python/airflow.md` is **completed by this PR**.)
  (1) the out-of-Airflow / Ops
  monitor that enforces delivery SLAs from the `deliver_by_*` tags (Airflow's
  native SLA is not used); (2) the periodic resource-usage audit against
  declared T-shirt size; (3) the weekly post-deploy drift-reconciliation job;
  (4) keeping the `xmatters_groups` allowlist current against the live directory
  / sourcing it from MDS; (5) publishing `edo_airflow_lib` to the cgpypi mirror
  and migrating vendored consumers.

### Out of scope

* dbt model standards (covered separately).
* DAG-level data contract validation (covered by the data contract RFD).
* Cross-DAG dependency design beyond Asset usage.
