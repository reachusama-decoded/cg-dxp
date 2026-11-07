---
name: validate-dbt
description: |
  Pre-deploy dbt validation gate for a Databricks data product. Runs three
  read-only checks and surfaces actionable errors before a bundle deploy:
  (1) compile check (dbt parse + compile — Jinja, ref()/source(), macros,
  broken SQL, catalog/schema vars), (2) schema diff against the live or a
  provided target schema (breaking column drops/renames/type changes vs.
  additive), and (3) a test-resolution check (data tests compile; declared
  primary keys carry not_null + unique) — without executing tests or
  materializing data. Read-only — never runs, builds, deploys, or modifies
  models. Phase 4 (Build) exit gate, paired with the planned /deploy-dab;
  distinct from /setup-databricks-asset-bundle, which scaffolds the bundle
  this skill validates.
  Trigger phrases: "validate my dbt before deploy", "is this dbt project
  deploy-ready", "run the dbt pre-deploy gate", "check dbt compiles against
  the target", "will this dbt change break the target schema",
  "dry-run my dbt tests".
allowed-tools: Read Bash Grep Glob
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: []                    # read-only gate: invokes no other skill — it runs dbt / databricks directly
  consumes:
    - data-contract                   # ODCS schema is the baseline for the schema-diff gate
    - data-model                      # declared model shape / grain
  cites:
    # References, not runtime prerequisites (matches /validate-dag's cites: treatment —
    # the gate does NOT require any of these to have run first).
    - run-dbt-on-databricks           # reuses its dbt CLI invocation conventions
    - troubleshoot-dbt-on-databricks  # every blocker's remediation hint routes here
    - setup-databricks-asset-bundle   # scaffolds the bundle this gate validates pre-deploy
    # Paired exit-gate partner /deploy-dab is unbuilt (G-01); referenced in prose, not cited, until it lands.
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # RFD 0013 is proposed (in discussion); build authorized by AICAT-166,
    # which implements the A2 validate-dbt follow-up RFD 0013 itself defers.
    # Full SQL-DBSQL-* linting runs in CI, not here —
    # sqlfluff (named in RFD 0013 §"Skills suite", under "Validation and
    # execution") and dbt-project-evaluator (per /dbt-best-practices). This
    # gate asserts only the directives a compile / schema-diff / test
    # resolution can verify deterministically before deploy. The three IDs
    # below are severity:advisory, status:draft in rfd/0008/standards.yaml,
    # so the gate reports them as advisory findings. See references/gates.md.
    - SQL-DBSQL-003   # incremental models use merge strategy + unique_key (surfaced at compile)
    - SQL-DBSQL-006   # not_null + unique on declared PKs (confirmed by the test-resolution check)
    - SQL-DBSQL-007   # catalog/schema set per environment, never hardcoded (surfaced at compile)
---

# /validate-dbt

Run the pre-deploy dbt validation gate for a Databricks data product and
produce a structured report. Read-only — the skill **never runs, builds,
materializes, or deploys, and never modifies models**. It is the Phase 4
(Build) exit gate: it confirms a dbt change is safe to ship *before* the
deploy step pushes the bundle, so creators see actionable compile, schema,
and test errors at the gate instead of in a failed deploy run.

Three gates, in order (full detail in `references/gates.md`):

1. **Compile check** — `dbt parse` (offline manifest build) + `dbt compile`
   against the resolved target. Catches Jinja render errors, unresolved
   `ref()`/`source()`, missing macros, broken model SQL, and catalog/schema
   vars that don't resolve for the target (SQL-DBSQL-007).
2. **Schema diff against target** — compare the columns the compiled models
   will produce against the columns of the live deployed relations (read via
   a `DESCRIBE TABLE` query), when a live target or a pasted snapshot is
   reachable. Additive changes pass; **breaking** changes (dropped/renamed
   columns, narrowing type changes) are flagged before they hit the warehouse.
3. **Test-resolution check** — compile the selected models' data tests so test
   SQL is validated *without executing it or scanning data*, and confirm
   declared primary keys carry `not_null` + `unique` (SQL-DBSQL-006). Full
   test *execution* is deferred to post-deploy `/run-dbt-on-databricks`.

The output is a Markdown report keyed by gate, each finding labeled
`blocker | advisory | ok | n-a` with a one-line remediation hint, and a
single machine-greppable `VERDICT:` line that CI (and the planned
`/deploy-dab` partner) can read without parsing Markdown.

## When to invoke

- A creator finishes a dbt change and wants to know whether it is
  deploy-ready — the natural end-of-Build checkpoint before deploy.
- During code review, to surface compile breaks and breaking schema changes
  before a human reviewer (or a failed deploy) finds them.
- After `/setup-databricks-asset-bundle` scaffolds or refreshes the bundle,
  to confirm the dbt project the bundle wraps actually compiles and its tests
  resolve against the target.
- As a CI step that gates promotion: grep the `VERDICT:` line and block the
  deploy when it reads `BLOCKED`.

## When NOT to use this skill

- The user wants the dbt models **fixed**, not validated. This gate is
  read-only; route concrete failures to `/troubleshoot-dbt-on-databricks`
  (every blocker's remediation hint already points there) or to the relevant
  authoring skill (`/write-dbt-model`, `/setup-dbt-project`).
- The user wants to **run** or **deploy** dbt for real (materialize models,
  execute tests against data, push the bundle, trigger a job). That is
  `/run-dbt-on-databricks` and the deploy step. This gate never writes to the
  warehouse — it only reads metadata (compile-time introspection, `DESCRIBE`).
- There is no dbt project (no `dbt_project.yml`) and nothing inlined. The
  gate refuses with a clear message and points at `/setup-dbt-project`.
- Full standards linting (sqlfluff, dbt-project-evaluator, the complete
  `SQL-DBSQL-*` family). Per RFD 0013 that is CI's job; this gate asserts
  only the directives a compile / schema-diff / test-resolution can verify
  deterministically.

## Modes

The mode controls which severity is applied to a non-safety finding (see
`references/findings-severity.md` for the canonical matrix). Default is
`production` unless the user signals otherwise or `.catalyst-build.yml#mode`
is set — the same source of truth `/build-preflight` writes and
`/setup-dbt-project` reads.

### `production` (default)

Every gate failure that would break a production deploy is a `blocker`. The
gate refuses to declare the change deploy-ready while any blocker remains.

### `prototype`

These are at most `advisory` so prototypes iterate without failing the gate
before they are production-bound (both are `advisory` in `production`
already; prototype mode preserves that posture rather than promoting them
to `blocker`):

- Missing PK test coverage (SQL-DBSQL-006) — already advisory by default
- Additive-but-undocumented schema changes

These stay `blocker` in every mode because they fail open regardless of
maturity — the gate's safety floor:

- Compile failures (the deploy cannot succeed)
- **Breaking** schema changes against an existing target relation
- Test SQL that does not compile

### `lift-and-shift`

Same blocker floor as `prototype` (compile + breaking-schema + uncompilable
tests). Naming-convention findings stay at `advisory` here too — lift-and-
shift preserves the original project's shape, so the human reviewer
decides whether to tighten naming.

## Inputs

The skill accepts one of:

1. A **data-product or dbt project directory**:
   `data_products/<product>/` (the skill resolves `dbt_project.yml`,
   `profiles.yml`, and the dataset selector under it) or a path containing a
   `dbt_project.yml`.
2. An **explicit selector + target**: a dbt node selector (e.g.
   `+stg_employee__records+`) and a target name (`dev`/`sqa`/`prd`). The
   target maps to a `profiles.yml` target entry and the bundle's `targets:`
   entry — the same `--target` mapping `/run-dbt-on-databricks` and
   `/setup-databricks-asset-bundle` use. (Deployment-time promotion via
   `promotions.yml` is the deploy step's concern, not this gate's.)
3. **Inline content** pasted into the prompt — typically the model SQL, its
   `_<layer>__models.yml` test config, and (optionally) a snapshot of the
   live target schema, inside fenced code blocks. This mode is used by the
   behavior-test harness (which has no file-setup support) and by anyone
   validating a change before committing.

If none is supplied, the gate asks once. Bulk multi-product sweeps are out of
scope — one data product / one dataset selector at a time.

### Disambiguating inline vs. on-disk mode

**Inline mode takes ABSOLUTE PRIORITY.** Check for it FIRST, before any path
lookup or fallback.

The check is mechanical: scan the prompt for a fenced code block whose body
is a dbt carrier — a ```sql block containing `{{ config(...) }}`, `{{ ref(`,
or `{{ source(`; or a ```yaml block with a top-level `models:` / `sources:`
key (a dbt schema/properties file). **If you find one, that is the subject.
Validate that content. Do NOT look for a project on disk. Do NOT fall back to
any other dbt project under any circumstances.**

Common-mistake guard:

- If the prompt names a path (e.g. `data_products/<product>/`) and ALSO
  contains an inline carrier, **the inline carrier wins**. The path line is
  metadata describing what the inlined content represents — not a fetch
  instruction.
- If a named path does not exist on disk, **do not pivot to a different
  project**. Either validate the inline content if present, or stop and
  report "no dbt project found" — never silently audit a project the user
  did not name.

Priority order (first match wins):

1. **Inline mode** — a fenced dbt carrier is in the prompt. Skip disk
   discovery entirely.
2. **Explicit project/selector mode** — the prompt names a `dbt_project.yml`,
   a data-product dir that exists, or a selector + target, AND no inline
   carrier is present.
3. **No subject found** — stop. Report "no dbt project supplied; inline the
   model(s) or provide a project path." Do NOT pick an arbitrary project from
   the working directory.

## Steps

### Step 0 — Decide inline vs. on-disk mode, resolve the target

Apply the priority order above. The decision is sticky for the whole gate.

- **Inline mode**: treat the inlined content as the authoritative, complete
  subject. Do NOT use Glob/Read/Bash to look for a project on disk; path
  references inside the inline content are data, not fetch instructions.
  Without a project on disk you cannot shell out to `dbt`, so each gate runs
  in **reason-from-source** form (described per-gate below) and any check
  that needs a live `dbt` invocation or a live warehouse emits `n-a` with a
  one-line reason.
- **On-disk mode**: resolve the dbt project (`dbt_project.yml`), the
  `profiles.yml`, the node selector, and the **target** (`dev`/`sqa`/`prd`).
  The target name maps to a `profiles.yml` target entry (and the bundle's
  `targets:` entry); if it cannot be resolved, stop with a `blocker` pointing
  at `/setup-dbt-project`. Confirm the active `dbt` is **dbt-core** (Catalyst
  is core-only; `/build-preflight` pins `dbt-core>=1.8,<1.11`) — the gate's
  exit-code logic assumes core. If the only `dbt` on PATH is the dbt Cloud CLI
  (whose `dbt parse` can exit 0 on a missing-config error and read as a false
  pass), emit `n-a` for the compile gates instead of trusting the exit code.

The pip layer that backs dbt — the install of `dbt-core` / `dbt-databricks`
and any `requirements.txt` the wrapper uses — MUST route through the internal
cgrepo mirror via pip's `--index-url`
(`https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/`), set in
`requirements.txt` / `pip.conf` / `dbt_wrapper.py`. Note `dbt deps` itself
takes **no** `--index-url` flag — it resolves packages from the dbt Package
Hub, not PyPI, so the cgrepo mirror applies to the pip install underneath, not
the `dbt deps` command line. A public-registry 404/timeout from a pip install
is a re-pointing problem, not a missing package — see
`/troubleshoot-dbt-on-databricks`.

### Step 1 — Gate 1: Compile check

**On-disk mode**: run, from the project directory:

```bash
dbt parse                                              # offline: builds the manifest, no warehouse needed
dbt compile --target <target> --select <selector>     # renders SQL; needs OAuth + a running warehouse
```

`dbt parse` builds the manifest and surfaces graph-level errors (unresolved
`ref()`/`source()`, missing macros, malformed YAML) **without a warehouse
connection** — it is the cheap pre-check. `dbt compile` then renders each
selected model's SQL into `target/compiled/` and surfaces Jinja and
`--vars`/catalog-schema resolution errors (SQL-DBSQL-007); on the Databricks
adapter `dbt compile` opens a connection and runs read-only introspective
metadata queries, so it requires OAuth auth and a running warehouse. A
non-zero exit on either is a `blocker` — the deploy cannot succeed. If
`dbt compile` fails on connectivity/auth (e.g. warehouse not running), route
to `/troubleshoot-dbt-on-databricks` rather than reporting a false compile
error. Capture the first actionable error line per failing node for the
report.

**Inline mode**: reason over the inlined SQL/YAML — confirm every `ref()` /
`source()` names a model/source that is present (or note the unresolved name
as a `blocker`), Jinja blocks are balanced, `config()` is well-formed, and
`{{ var(...) }}` catalog/schema references are present rather than hardcoded
(SQL-DBSQL-007). Mark the live `dbt compile` itself `n-a` ("no project on
disk in inline mode") while still reporting the static findings.

### Step 2 — Gate 2: Schema diff against target

**On-disk mode**: for each compiled model, derive the output column set
(name + type) from `target/manifest.json` / the compiled SQL, and read the
live relation's columns from the target. The Databricks CLI has no ad-hoc
`sql query` subcommand; run the statement through the SQL Statement Execution
API (OAuth/SP auth + a running warehouse required), or hand the read off to
`/query-table`:

```bash
# Set a synchronous wait_timeout so the call returns rows inline rather than a
# PENDING statement_id you must poll. (information_schema.columns gives a more
# deterministic row shape than DESCRIBE if you prefer to parse columns.)
databricks api post /api/2.0/sql/statements/ --json '{
  "warehouse_id": "<warehouse_id>",
  "statement": "DESCRIBE TABLE <catalog>.<schema>.<relation>",
  "wait_timeout": "30s",
  "on_wait_timeout": "CONTINUE"
}'
# CONTINUE (not CANCEL) so a query that exceeds wait_timeout returns a pollable
# statement_id rather than being aborted. If the response status is
# PENDING/RUNNING (query exceeded wait_timeout), poll
# GET /api/2.0/sql/statements/<statement_id> — a PENDING envelope has no
# result.data_array and must NOT be read as "no columns".
```

Classify each difference (see `references/gates.md` for the full table):

- **Additive** (new nullable column; relation does not yet exist → first
  deploy) → `ok`.
- **Breaking** (dropped column, renamed column, narrowing/incompatible type
  change) → `blocker` in production.
- **New `NOT NULL` on an existing table** → `advisory`: the gate cannot tell
  whether existing rows are null without scanning data (which it must not do),
  so it flags it for manual verification rather than asserting a breaking
  change it cannot substantiate.

Cross-check the produced schema against the **data-contract** (ODCS) when one
is present: a column the contract promises that the model no longer produces
is a `blocker`.

**Inline mode**: handle each selected model independently. For each model,
find the pasted target-schema snapshot that matches *its* relation
(`catalog.schema.relation`) and diff against that snapshot, classifying as
above. For any model with no matching snapshot, emit `n-a` ("no target
snapshot for this relation in inline mode") for that model's breaking-change
check — do not diff it against another model's snapshot, and do not mark the
whole gate `ok` just because some snapshot was present. The contract (ODCS)
cross-check still runs statically for every model regardless of snapshots.

### Step 3 — Gate 3: Test-resolution check

**On-disk mode**: compile the selected models' data tests and statically
confirm coverage — the gate **never executes tests and never writes to the
warehouse**. `dbt build`/`dbt run --empty` would materialize a zero-row
table over the live relation (a destructive write), so neither is used
here:

```bash
# Gate 1's compile already renders the selected models' attached tests via
# dbt's indirect selection — no extra selector needed. Do NOT append
# test_type:* selectors: a space is a union in dbt's grammar and would pull
# in every singular test in the project, not just the ones under review.
dbt compile --target <target> --select <selector>
# stricter — require all of a test's parents to be selected first:
dbt compile --target <target> --select <selector> --indirect-selection cautious
```

A test whose SQL does not render — a broken custom test macro, a Jinja error,
an unresolved generic test — is a `blocker`. Then read the
`_<layer>__models.yml` (or per-model `.yml`) config and confirm every declared
primary key carries both `not_null` and `unique` tests (SQL-DBSQL-006);
absence is an `advisory`.

Compiling a test renders its SQL but does not prove a referenced column exists
at runtime — that needs execution. Full `dbt test` execution against
materialized inputs is therefore out of scope for this read-only gate; run it
post-deploy via `/run-dbt-on-databricks`, or in a throwaway scratch schema.

**Inline mode**: reason over the inlined test config — confirm each declared
test references a column the model produces, and that declared PKs carry
`not_null` + `unique`. A custom/generic test macro or singular test whose
*definition* is not inlined cannot be verified to render statically: mark that
specific test `n-a` ("test macro/SQL not inlined — cannot verify it renders"),
never a false `ok` or a false `blocker` — only the declared-column-existence
half is statically checkable for it. Mark the live compile `n-a`.

### Step 4 — Emit the report

Render `templates/validation-report.md`. The report carries:

1. **Header** — data product / selector, resolved target, mode, timestamp,
   and which mode (inline vs on-disk) the gate ran in.
2. **Summary** — counts of `blocker | advisory | ok | n-a` and the one-line
   verdict. The verdict is `DEPLOY_READY` only if zero blockers remain.
3. **Findings by gate** — one block per gate (Compile / Schema diff / Test
   resolution) with the rule ID where one applies, severity, location, and a
   one-line remediation hint.
4. **Next steps** — ordered, blockers first; each names the skill to consult
   (`/troubleshoot-dbt-on-databricks` for failures, the authoring skill for
   missing coverage). If `DEPLOY_READY`, the final step notes the change is
   deploy-ready and to proceed with the bundle deploy — the paired
   `/deploy-dab` gate partner is planned (G-01), not yet built.

The gate never edits models. If the user wants the failures fixed, route them
to `/troubleshoot-dbt-on-databricks` or the relevant authoring skill.

## Anti-goals

- **No auto-fix, no deploy.** The gate reads and compiles; it never writes to
  a model file and never pushes a bundle. Remediation is the troubleshooting
  / authoring skills' job; deploying is the deploy step's job.
- **No execution or materialization.** The gate compiles and inspects; it
  never runs `dbt run` / `dbt build`, never uses `--empty` against the target
  (which would overwrite the live relation with a zero-row table), and never
  materializes tables or scans full data.
- **No gate-authored rules.** Every standards finding cites an `SQL-DBSQL-*`
  directive from RFD 0013 (proposed; in discussion) and reports it at the severity
  `rfd/0008/standards.yaml` assigns. The gate does not invent rules or
  escalate a standard's severity, and it does not duplicate CI's full
  sqlfluff / dbt-project-evaluator lint — it asserts only what a compile /
  schema-diff / test-resolution verifies.
- **No silent skips.** If a check cannot run (inline mode, no live warehouse,
  unresolvable target), the gate emits an `n-a` finding with a one-line
  reason — never an unannotated pass.
- **No bulk sweeps.** One data product / one selector at a time.

## Report contract (one-line summary)

The gate's stdout MUST include exactly one line matching:

```
VERDICT: <DEPLOY_READY|BLOCKED> — <blocker_count> blocker, <advisory_count> advisory, <ok_count> ok, <na_count> n-a
```

`DEPLOY_READY` iff `blocker_count == 0`. CI (and the planned `/deploy-dab`
partner) grep this line to decide whether to proceed without parsing the
Markdown body.

**Counting (so the counts are deterministic and self-checking):**

- A *finding* is one row per gate per distinct rule / column / test outcome.
- Count `ok` **per gate**, not per item: a gate contributes `ok = 1` only when
  at least one of its checks actually executed (not skipped to `n-a`) and none
  produced a `blocker` or `advisory` finding; otherwise `ok = 0`. A gate whose
  every check was skipped contributes `ok = 0` and its `n-a` count reflects the
  skipped steps — a fully-skipped gate is never reported as a pass. A gate can
  be **both** `ok = 1` and carry `n-a`s at once: in the common inline run,
  Gate 1's static checks execute-and-pass (`ok = 1`) while its live `dbt
  compile` is skipped (one `n-a`). `ok` (per gate, 0/1) and `n-a` (per skipped
  step) are counted independently and never net against each other — so an
  inline run of three gates that each statically pass with one skipped live
  step is deterministically `3 ok, 3 n-a`. (Passing
  individual checks are not enumerated unless `--verbose`.) Emit **exactly
  one** `n-a` per skipped live step (e.g. the inline live-compile; or, in
  Gate 2 inline, one per model whose breaking-change check could not run).
- The four counts on the `VERDICT:` line MUST equal the column sums of the
  Summary table — the two surfaces are self-checking and must reconcile.
- Only the verdict *token* gates CI; a matcher SHOULD accept any dash
  (`—`, `–`, or `-`) as the separator so a generated en-dash/hyphen still
  matches. The canonical form uses an em-dash.
