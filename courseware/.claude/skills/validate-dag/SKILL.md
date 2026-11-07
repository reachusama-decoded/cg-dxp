---
name: validate-dag
description: |
  Validate an existing Airflow DAG against RFD 0011 (DAG Standards) and
  produce a structured compliance report. Read-only — never modifies files.
  Pairs with /generate-dag: same canonical rule set, same pattern detection,
  but applied to DAGs that already exist (hand-written, retrofitted, or
  emitted by /generate-dag).
  Trigger phrases: "validate this DAG", "is this DAG RFD 0011 compliant",
  "check my DAG against the standards", "audit this dag",
  "what's wrong with this DAG", "lint my airflow dag for compliance".
allowed-tools: Read Glob Grep
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  cites:
    # The validator does NOT require /generate-dag to have run first; it
    # only references generate-dag's directive map and remediation docs
    # from its compliance report. cites:, not dependencies:.
    - generate-dag
  consumes:
    - data-contract
  standards:
    # Same canonical rule set as /generate-dag for every directive the
    # validator can detect statically.
    #
    # Provisional-rules caveat (matches /generate-dag's treatment, kept in
    # lock-step so the auditor never enforces a rule the producer doesn't
    # emit to):
    # - RFD 0011 (DAG Standards) currently enumerates PY-AIRFLOW-001..-015
    #   in its ratified body and is in `discussion` state.
    # - PY-AIRFLOW-016..-022 are discussion-state IDs from RFD 0011 PR #87
    #   (tracked in #128) and are treated as provisional until RFD 0011
    #   merges. If the IDs or semantics change at ratification, the
    #   validator's spec MUST be updated in the same change.
    # - DBX-DAB-001 and DBX-DAB-003 are provisional from RFD 0012 (DBX
    #   Asset Bundle composition) and follow the same lock-step rule.
    # This list therefore intentionally exceeds the body of merged RFD 0011
    # today; the surplus is the same surplus /generate-dag already emits to,
    # so the producer/auditor pair stays consistent. See L<anti-goal>:
    # "No new rules" — the validator does not invent rules; the discussion-state
    # IDs above are ratified-in-flight, not validator-authored.
    #
    # Out-of-scope IDs (in /generate-dag's standards but NOT here):
    # DBX-DAB-002, DBX-DAB-004 — bundle-internal composition concerns the
    # static DAG file cannot carry signal for. DBX-SEC-001, DBX-SEC-002 —
    # Databricks workspace SP/OAuth posture, not visible from the DAG.
    #
    # See generate-dag/references/rfd-0011-citations.md for the "what does
    # the rule mean" half; this skill is the "what does an auditor look for
    # to confirm it" half.
    - PY-AIRFLOW-001            # Templated dates; no datetime.now() in DAG body
    - PY-AIRFLOW-002            # Static start_date; no days_ago()
    - PY-AIRFLOW-003            # Retries set on every task
    - PY-AIRFLOW-004            # Exponential backoff with bounded max_retry_delay
    - PY-AIRFLOW-005            # T-shirt cluster sizing / pool assignment
    - PY-AIRFLOW-006            # Explicit schedule + catchup=False
    - PY-AIRFLOW-007            # Required tag set (l1_domain, l1_xmatters_group, lifecycle_phase, data_classification, criticality)
    - PY-AIRFLOW-008            # No DAG-level Datadog/PagerDuty/email on_failure_callback; alerting is platform-side (Astronomer). Routing tags are context for manual escalation
    - PY-AIRFLOW-009            # No module-scope I/O at parse time
    - PY-AIRFLOW-010            # TaskFlow API preferred over PythonOperator for compute
    - PY-AIRFLOW-011            # XCom hygiene (≤1KB)
    - PY-AIRFLOW-012            # DAG ID convention <domain>__<dataset>__<frequency>
    - PY-AIRFLOW-013            # No literal tokens / secrets
    - PY-AIRFLOW-014            # Integrity test stub present
    - PY-AIRFLOW-015            # Data-ready event v2 on success
    - PY-AIRFLOW-016            # Deterministic failures use AirflowFailException (no retry_on_exception API)
    - PY-AIRFLOW-017            # Deferrable operators / mode=reschedule + bounded timeout
    - PY-AIRFLOW-018            # max_active_runs + max_active_tasks bounded
    - PY-AIRFLOW-019            # Asset-driven schedule by default
    - PY-AIRFLOW-020            # No secret values as operator args
    - PY-AIRFLOW-021            # doc_md cites astro dev start
    - PY-AIRFLOW-022            # assert_dag_compliant runs in integrity test
    - DBX-DAB-001               # Reads ${var.databricks_job_prefix} from the bundle
    - DBX-DAB-003               # Airflow failure alerting is platform-side (Astronomer Datadog); DAB owns system-signal notifications
  shared-components:
    core: []
    platforms: [airflow, databricks, astronomer]
---

# /validate-dag

Audit an existing Airflow DAG against RFD 0011 and produce a structured
compliance report. Read-only — the skill **never modifies files**. Same
DAG-file-scoped rule set as `/generate-dag` (the bundle-internal
`DBX-DAB-002/-004` and Databricks-posture `DBX-SEC-001/-002` IDs are
explicitly out of scope — see frontmatter `standards:` comment for why);
same pattern detection; flipped polarity (check, don't emit).

The output is a Markdown report keyed by RFD 0011 section, with each
finding labeled `blocker | advisory | ok | n-a` and a one-line
remediation hint pointing at the relevant `/generate-dag` step or
reference doc.

## When to invoke

- A team hands you an existing DAG (hand-written, copied from another repo,
  or emitted by an older version of `/generate-dag`) and asks whether it
  meets the standards.
- During code review, to surface RFD 0011 violations before a human
  reviewer has to find them.
- After `/generate-dag` runs, as a second pair of eyes on the emission —
  confirms the structural test would pass and the integrity test would
  load the DAG.
- Before a `lift-and-shift` retrofit: validate the original to scope the
  proposal under `workspace/dag-proposals/`.

## When NOT to use this skill

- The DAG isn't Catalyst-shaped (not under
  `data_products/<product>/datasets/<dataset>/airflow/`). The validator
  refuses with a clear message and points at `/scaffold-repo-structure`.
- The orchestrator isn't Airflow (Prefect, Dagster, Argo). Out of scope.
- The user wants the DAG **fixed**, not audited. Route to
  `/generate-dag` in `lift-and-shift` mode instead — that skill emits a
  proposal under `workspace/dag-proposals/` the user can diff and merge.

## Modes

Inherits the same three modes as `/generate-dag`. The mode controls
which severity is applied to each finding (see
`references/findings-severity.md`):

The canonical, authoritative severity-by-mode matrix lives in
`references/findings-severity.md` — consult that for any cross-cluster
question. This section is the human summary.

### `production` (default)

All RFD 0011 directives are `blocker` when violated. Validator refuses
to declare the DAG compliant if any blocker remains.

### `prototype`

The following clusters downgrade to `advisory` so prototypes don't
fail the gate before they're production-bound:

- PY-AIRFLOW-007 — required MDS tag set
- PY-AIRFLOW-008 — no DAG-level alerting callback (platform-side Datadog)
- PY-AIRFLOW-017 — bounded waits / deferrable
- PY-AIRFLOW-018 — bounded parallelism
- PY-AIRFLOW-012 — DAG ID convention
- PY-AIRFLOW-014 / -022 — integrity-test existence

These stay `blocker` in every mode because they fail open regardless
of maturity:

- PY-AIRFLOW-001 / -002 — idempotency
- PY-AIRFLOW-013 / -020 — secrets
- PY-AIRFLOW-016 — `retry_on_exception` ban

### `lift-and-shift`

The following downgrade to `advisory` because lift-and-shift preserves
the original carrier:

- PY-AIRFLOW-012 — DAG ID convention
- PY-AIRFLOW-014 / -022 — integrity-test existence

Tag set, the alerting-callback ban (PY-AIRFLOW-008), bounded waits,
bounded parallelism, and all secret rules remain `blocker`.

### Mode source of truth

Default is `production` unless the user signals otherwise or
`.catalyst-build.yml#mode` is set.

## Inputs

The skill accepts one of:

1. A **dataset directory** path:
   `data_products/<product>/datasets/<dataset>/`. The validator resolves
   the carrier file under `airflow/` and runs from there.
2. An **explicit DAG file** path (`.dag.yml`, `.dag-factory.yml`, or
   `_dag.py`). The validator locates the dataset's contract and bundle by
   walking up the path.
3. **Inline carrier content** pasted directly into the prompt — typically
   inside a fenced code block (```yaml ... ``` or ```python ... ```).
   When the user inlines the carrier, the validator audits the inlined
   content as the authoritative carrier; it does NOT search disk for
   a file matching the inlined `dag_id` or any path the inlined content
   references. This mode is used by the behavior-test harness (which
   has no `setup.files:` support) and by anyone who wants to validate
   a DAG snippet before committing.

If none of the three is supplied, the validator asks once. Bulk repo
sweeps are out of scope (see `/generate-dag` OQ-4 —
single-dataset-at-a-time).

### Disambiguating inline vs. on-disk mode

**Inline mode takes ABSOLUTE PRIORITY.** Check for it FIRST, before
considering any path reference, file lookup, or fallback to a canonical
fixture.

The check is mechanical: scan the user's prompt for a fenced code
block (```yaml, ```yml, or ```python) whose body contains a DAG
carrier signal — top-level `dag_id:` for YAML, or a `@dag(...)`
decorator / `DAG(...)` constructor for Python. **If you find one,
that is the carrier. Audit that content. Do NOT look for a file. Do
NOT fall back to any other DAG on disk under any circumstances.**

Common-mistake guard:

- If the prompt says "Carrier file: data_products/<some/path>.yml"
  and ALSO contains an inline code block, **the inline code block
  wins**. The "Carrier file:" line is metadata describing what the
  inlined content represents — it is NOT an instruction to fetch.
- If the path in the prompt doesn't exist on disk, **do not fall back
  to a different DAG file** (e.g., a fixture under `tests/`,
  `examples/`, or anywhere else). Either audit the inline content if
  present, or stop and report "no carrier found" — never silently
  pivot to a DAG the user did not name.

Priority order (first match wins):

1. **Inline mode**: the prompt contains a fenced code block whose body
   is a DAG carrier (see signals above). Skip disk discovery entirely.
2. **Explicit file mode**: the prompt names a path ending in
   `.dag.yml`, `.dag.yaml`, `.dag-factory.yml`, or `_dag.py`, AND that
   file exists on disk, AND no inline carrier is present.
3. **Dataset directory mode**: the prompt names a
   `data_products/<product>/datasets/<dataset>/` path that exists, AND
   no inline carrier is present.
4. **No carrier found**: stop. Report "no carrier supplied; please
   inline the DAG content or provide a path to one." Do NOT pick an
   arbitrary DAG from the working directory.

## Steps

### Step 0 — Decide inline vs. on-disk mode

Apply the priority order from "Disambiguating inline vs. on-disk mode"
above:

- **Inline mode** (fenced code block with carrier content in the prompt):
  treat the inlined content as the authoritative, complete carrier.
  Do NOT use Glob, Read, or any other tool to look for the carrier or
  its companion artifacts on disk — even if the inline content
  references a `data_products/...` path. Path references inside the
  inline carrier are data, not fetch instructions. The carrier filename
  (used for pattern detection in Step 1) is inferred from the code-fence
  language tag and the body shape, NOT from a disk lookup.
- **Disk mode** (explicit DAG file path or dataset directory path):
  proceed to Step 1's disk-discovery flow.

This decision is sticky for the rest of the audit. In inline mode,
Steps 2 and 4 below run with reduced inputs (no contract, no bundle,
no test files) and the report's "Companion artifacts" section reads
"not provided in inline mode" for each absent artifact.

### Step 1 — Detect the emission pattern

**Inline mode**: detect the pattern from the inline content directly.
- Fenced as ```yaml or ```yml AND body has top-level `steps:` with
  `blueprint:` references → `astro-blueprints (existing)`.
- Fenced as ```yaml or ```yml AND body has top-level `tasks:` with
  inline `operator:` configs → `dag-factory` (assume Pattern A unless
  the user explicitly says Pattern B vendored).
- Fenced as ```python AND body has `@dag(...)` decorator or
  `DAG(...)` constructor → `python` (Pattern C).
- If the prompt contains MULTIPLE inline carriers in the same dataset
  (e.g. both a `.dag.yml` and a `.dag-factory.yml` block), the
  multi-carrier short-circuit fires as a `blocker` — see
  `references/pattern-detection.md`. Do not arbitrarily pick one.

**Disk mode**: same disambiguation as `/generate-dag` Step 1 —
file-extension-driven, sticky to the existing carrier. See
`references/pattern-detection.md` for the full decision tree and the
validator's no-op fallbacks (the validator never emits, so unresolved
carriers become a `blocker` finding instead of a prompt to emit).

The detected pattern drives which rules are enforced in YAML vs.
deferred to blueprint source (see "Pattern routing" in
`references/checks-by-section.md`).

### Step 2 — Locate companion artifacts

**Inline mode**: skip disk lookups entirely. The Companion Artifacts
section of the report reads `not provided in inline mode` for contract,
bundle, structural test, integrity test, and callback module. Any rule
that depends on a companion artifact (e.g. DBX-DAB-001's bundle
compose check, PY-AIRFLOW-014/-022's integrity test presence) emits
`n-a` with reason `"companion artifact not provided in inline mode"`
instead of `blocker`. The user can re-invoke in disk mode to cover
those checks.

**Disk mode**: read whatever is present and use it to enrich the
report:

- `data_products/<product>/datasets/<dataset>/contract/<dataset>.odcs.yaml`
  — used to cross-check `data_classification`, `l1_domain`, and SLA tags.
- `data_products/<product>/datasets/<dataset>/bundle/databricks.yml`
  — used to verify `job_name` composition with `databricks_job_prefix`
  (DBX-DAB-001).
- `tests/dags/test_<dataset>_dag.py` and
  `tests/dags/test_<dataset>_dag_integrity.py` — note whether the
  generated tests exist; their absence is a PY-AIRFLOW-014/-022 finding.
- Failure alerting is platform-side (Astronomer Datadog) — there is no
  DAG-level callback module to look for. PY-AIRFLOW-008 instead flags a
  DAG-level Datadog/PagerDuty/email `on_failure_callback` as a violation.

Missing companion artifacts (in disk mode) are findings, not hard
stops. The validator still produces a report.

### Step 3 — Run the per-section checks

Walk the DAG file once and apply every check in
`references/checks-by-section.md`. The checks are organized by RFD 0011
section (§1 through §10) and are pattern-aware: each rule's enforcement
point is one of:

- **YAML field** — assert presence/value (Pattern A, Pattern C, Pattern
  B vendored).
- **Blueprint reference** — assert the right blueprint is named in
  `steps[*].blueprint` (Pattern B existing).
- **Grep** — reject forbidden literals (`datetime.now()`, `days_ago(`,
  `password=`, `token=`, PagerDuty references) in any pattern.
- **Companion file** — confirm the integrity test file exists and
  imports `assert_dag_compliant` (all patterns).

Each finding carries:

- The rule ID (`PY-AIRFLOW-NNN` or `DBX-DAB-NNN`).
- A severity in `{blocker, advisory, ok, n-a}` per
  `references/findings-severity.md`.
- The file and (where applicable) line/key path.
- A one-line remediation hint that names the `/generate-dag` step or
  reference doc that explains the fix.

### Step 4 — Cross-reference the bundle (DBX-DAB-001)

**Inline mode**: emit `n-a` for DBX-DAB-001 with reason
`"bundle not provided in inline mode"` — the validator cannot verify
the compose contract without a bundle to read. The user can re-invoke
in disk mode to cover this check.

**Disk mode**: compare the DAG's `job_name` literal to the bundle's
`${var.databricks_job_prefix}<resource_key>` rendered pattern. A
mismatch is a `blocker` in production mode: the DAG would target a job
the bundle didn't deploy. See
`generate-dag/references/compose-with-bundle.md` for the contract.

If `databricks.yml` is absent (disk mode only): production mode emits a
`blocker` finding pointing at `/setup-databricks-asset-bundle`;
prototype mode downgrades to `advisory`.

### Step 5 — Emit the report

Render `templates/compliance-report.md` to stdout (and to
`workspace/dag-reports/<dataset>-compliance.md` if the user has the
`workspace/` directory). The report has:

1. **Header** — DAG ID, dataset path, detected pattern, validation mode,
   timestamp.
2. **Summary** — counts of `blocker | advisory | ok | n-a`. The
   one-line verdict at the top is `COMPLIANT` only if zero blockers
   remain.
3. **Findings by section** — one block per RFD 0011 section that has
   findings, with the rule ID, severity, location, and remediation
   hint.
4. **Next steps** — ordered list, blocker fixes first. Each step
   names the `/generate-dag` mode (`lift-and-shift` for retrofits)
   or reference doc the team should consult.

The validator does not edit the DAG. If the user wants the violations
fixed, point them at `/generate-dag` in `lift-and-shift` mode, which
emits a proposal under `workspace/dag-proposals/` the user can diff
against the runtime original.

## Anti-goals

- **No auto-fix.** The validator reads files; it never writes to the
  runtime DAG location. Remediation is `/generate-dag`'s job.
- **No bulk repo sweeps.** Single dataset at a time, same as
  `/generate-dag` (OQ-4).
- **No validator-authored rules.** Every check cites a directive in
  `generate-dag/references/rfd-0011-citations.md`, and every enforced
  directive is one the producer (`/generate-dag`) already emits to —
  the producer/auditor pair stays in lock-step. Where RFD 0011 / RFD 0012
  is still in discussion state (PY-AIRFLOW-016..-022, DBX-DAB-001/-003),
  the validator carries them as **provisional** in its `standards:` block
  (see frontmatter comment). When the RFDs ratify, the validator's spec
  is updated in the same change-set so it never enforces a stricter rule
  than the ratified RFD.
- **No silent skips.** If a check can't run (e.g. Airflow not installed
  to load the DAG), the validator emits an `n-a` finding with a clear
  reason, never an unannotated pass.
- **No DAG-level alerting callbacks.** Datadog alerting is provided by
  Astronomer at the platform level, not emitted by the DAG — a DAG-level
  Datadog/PagerDuty/email `on_failure_callback` is a PY-AIRFLOW-008 violation.
  No PagerDuty, no Slack. From the Datadog alert, Teams (Datadog→Teams) and
  xMatters paging are both manual by support; routing tags are the context
  they read.

## Report contract (one-line summary)

The validator's stdout MUST include exactly one line matching:

```
VERDICT: <COMPLIANT|NON_COMPLIANT> — <blocker_count> blocker, <advisory_count> advisory, <ok_count> ok, <na_count> n-a
```

So CI and other skills can grep the result without parsing Markdown.
