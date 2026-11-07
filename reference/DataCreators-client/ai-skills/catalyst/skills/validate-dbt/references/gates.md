# The three gates (validator rules)

The per-gate validator logic for `/validate-dbt`, in the order the gate runs
them. RFD 0013 is proposed (in discussion; build authorized by AICAT-166): this
gate asserts only the directives a compile /
schema-diff / test-resolution can verify deterministically before a deploy.
The full `SQL-DBSQL-*` lint runs from CI — `sqlfluff` (named in RFD 0013
§"Skills suite", under the "Validation and execution" list) and
`dbt-project-evaluator` (per `/dbt-best-practices`) — and is explicitly **not**
duplicated here.

The three standards IDs this gate touches (SQL-DBSQL-003 / -006 / -007) are
all `severity: advisory, status: draft` in `rfd/0008/standards.yaml`, so the
gate reports them as **advisory** findings. The gate does not escalate a
standard's severity. The `blocker` severities below come instead from
**deploy-blocking necessity** — a change that cannot compile, or that breaks
an existing deployed relation — which is independent of any draft rule ID.

Each gate runs in one of two forms depending on the mode resolved in Step 0:

- **On-disk form** — a real dbt project is present; the gate shells out to
  `dbt` / `databricks` and reads the result.
- **Reason-from-source form** — inline mode; no project on disk. The gate
  reasons over the inlined SQL/YAML and emits `n-a` (with a one-line reason)
  for any check that genuinely needs a live `dbt` invocation or a live
  warehouse.

Severity vocabulary is the same four levels as the report
(`blocker | advisory | ok | n-a`); the canonical severity-by-mode matrix
lives in `references/findings-severity.md`. This file documents the
**production-mode** baseline.

---

## Gate 1 — Compile check

**Goal:** prove the selected models *parse and compile* against the target
before a deploy tries to. This is the gate that most often turns a failed
deploy run into a one-line message at the checkpoint.

**On-disk form** — from the project directory:

```bash
dbt parse                                            # offline: builds the manifest, no warehouse needed
dbt compile --target <target> --select <selector>   # renders SQL; needs OAuth + a running warehouse
```

- `dbt parse` builds the manifest and surfaces graph-level errors —
  unresolved `ref()` / `source()`, missing macros, malformed YAML properties
  files — **without connecting to a warehouse**. It is the cheap pre-check.
  (`dbt parse` is metadata-only; it takes no per-target catalog/schema into
  account, so the catalog/schema resolution check below belongs to `compile`,
  not `parse`.)
- `dbt compile` renders each selected model's SQL into `target/compiled/` and
  surfaces Jinja render errors and `--vars` / catalog-schema resolution
  failures. On the Databricks adapter `dbt compile` opens a connection and
  runs read-only introspective metadata queries, so it requires OAuth auth
  and a running warehouse — a stopped warehouse or an auth failure here is a
  connectivity problem to route to `/troubleshoot-dbt-on-databricks`, not a
  false compile error.

**What it catches → severity (production):**

| Symptom | Rule | Severity | Source of severity |
|---|---|---|---|
| `dbt parse`/`dbt compile` non-zero exit | — | `blocker` | deploy-blocking |
| Unresolved `ref()` / `source()` | — | `blocker` | deploy-blocking |
| Missing / unparseable macro | — | `blocker` | deploy-blocking |
| Jinja render error | — | `blocker` | deploy-blocking |
| Catalog/schema hardcoded instead of `{{ var(...) }}` / per-env target | SQL-DBSQL-007 | `advisory` | standards.yaml (advisory/draft) |
| Incremental model missing `incremental_strategy='merge'` or `unique_key` | SQL-DBSQL-003 | `advisory` | standards.yaml (advisory/draft) |

Capture the first actionable error line per failing node — that line is the
report's remediation hint, prefixed with a pointer to
`/troubleshoot-dbt-on-databricks` where the failure has a known fix (SSL/CA,
auth, warehouse-not-running, `bitemporal_load_v2` macro, public-PyPI 404).

**Reason-from-source form (inline):** confirm every `ref()`/`source()` names
a present model/source (unresolved → `blocker`), Jinja blocks balance,
`config()` is well-formed, and catalog/schema come from `{{ var(...) }}`
rather than literals (SQL-DBSQL-007 advisory). Mark the live `dbt compile`
`n-a` ("no project on disk in inline mode") while still reporting static
findings.

---

## Gate 2 — Schema diff against target

**Goal:** catch a change that compiles cleanly but would **break the deployed
relation** — the failure mode a compile check cannot see.

**On-disk form** — for each compiled model, derive the produced column set
(name + type) from `target/manifest.json` / the compiled SQL, then read the
live relation's columns. The unified `databricks` CLI has **no** ad-hoc
`sql query` subcommand; run the read through the SQL Statement Execution API
(`databricks api`), or hand it off to `/query-table` (which wraps
`DESCRIBE TABLE`). OAuth/SP auth and a running warehouse are prerequisites.

```bash
# Set a synchronous wait_timeout so the statement returns rows inline rather
# than a PENDING statement_id that must be polled.
databricks api post /api/2.0/sql/statements/ --json '{
  "warehouse_id": "<warehouse_id>",
  "statement": "DESCRIBE TABLE <catalog>.<schema>.<relation>",
  "wait_timeout": "30s",
  "on_wait_timeout": "CONTINUE"
}'
# CONTINUE (not CANCEL): a query exceeding wait_timeout returns a pollable
# statement_id instead of being aborted, so the PENDING poll path below is valid.
# More deterministic row shape:
#   SELECT column_name, full_data_type, is_nullable
#   FROM <catalog>.information_schema.columns
#   WHERE table_schema = '<schema>' AND table_name = '<relation>'
# If status is PENDING/RUNNING (exceeded wait_timeout), poll
# GET /api/2.0/sql/statements/<statement_id>; a PENDING envelope carries no
# result.data_array and must NOT be read as "no columns".
```

Classify each difference:

| Difference | Classification | Severity (production) | Source of severity |
|---|---|---|---|
| Relation does not exist yet (first deploy) | additive | `ok` | — |
| New nullable column | additive | `ok` | — |
| New column, widening type change (e.g. `int`→`bigint`) | additive | `ok` | — |
| Dropped column | **breaking** | `blocker` | deploy-blocking |
| Renamed column (drop + add of a new name) | **breaking** | `blocker` | deploy-blocking |
| Narrowing / incompatible type change (e.g. `string`→`int`) | **breaking** | `blocker` | deploy-blocking |
| New `NOT NULL` on an existing table | conditional | `advisory` | not data-verifiable |
| Column promised by the data-contract (ODCS) no longer produced | **breaking** | `blocker` | deploy-blocking |

`NOT NULL` is `advisory`, not `blocker`: whether adding it breaks depends on
whether existing rows contain nulls, which the gate cannot determine from
`DESCRIBE` / compiled columns without scanning data (which it must not do).
It is flagged for manual verification rather than asserted as breaking.

The contract cross-check uses the ODCS contract under
`data_products/<product>/datasets/<dataset>/contract/` when present — a
column the contract promises consumers but the model no longer emits is a
`blocker` regardless of the live relation.

**Reason-from-source form (inline):** handle each selected model
independently. For each model, find the pasted target-schema snapshot matching
*its* relation (`catalog.schema.relation`) and diff against that; classify as
above. For any model with no matching snapshot, emit `n-a` ("no target
snapshot for this relation in inline mode") for that model's breaking-change
check — never diff a model against another model's snapshot, and never mark
the whole gate `ok` just because some snapshot was present. The contract (ODCS)
cross-check still runs statically for every model regardless of snapshots.

---

## Gate 3 — Test-resolution check

**Goal:** prove the data tests *compile and resolve* — and that the declared
primary keys are actually tested — without executing tests or writing to the
warehouse.

**On-disk form** — Gate 1's `dbt compile --select <selector>` already renders
the selected models' attached generic + singular tests into `target/compiled/`
(dbt's default `eager` indirect selection pulls a model's tests in with the
model), so no second command is strictly needed — confirm those tests
rendered. Do **not** append `test_type:generic test_type:singular` as extra
selectors: in dbt's selection grammar a comma is intersection and a space is
union, so `<selector>,test_type:generic test_type:singular` resolves to
`(<selector> AND generic) OR (every singular test in the project)` and leaks
tests unrelated to the change. If you want to require that a test's parents
are all selected before it is included, use cautious indirect selection:

```bash
dbt compile --target <target> --select <selector>                                # attached tests render via indirect selection
dbt compile --target <target> --select <selector> --indirect-selection cautious  # stricter: all parents must be selected
```

> **Why not `dbt build --empty`?** `--empty` *executes model SQL against the
> warehouse*, overwriting the existing relation with a zero-row table — a
> destructive write (`adding-dbt-unit-test/SKILL.md`: "`--empty` overwrites
> existing models with schema-only (zero-row) versions … it will wipe that
> data"). `dbt build --empty` still runs the attached data tests, but
> against the empty result, so the tests are not meaningful for pre-deploy
> validation either. A read-only pre-deploy gate must never run it against
> the target.

**What it catches → severity (production):**

| Symptom | Rule | Severity | Source of severity |
|---|---|---|---|
| A data test's SQL does not render (broken custom test macro, Jinja error, unresolved generic test) | — | `blocker` | deploy-blocking |
| A declared primary key lacks `not_null` | SQL-DBSQL-006 | `advisory` | standards.yaml (advisory/draft) |
| A declared primary key lacks `unique` | SQL-DBSQL-006 | `advisory` | standards.yaml (advisory/draft) |
| A model has no declared tests at all | SQL-DBSQL-006 | `advisory` | standards.yaml (advisory/draft) |

Read the `_<layer>__models.yml` (or per-model `.yml`) config to find declared
PKs and their tests; the model's `config(unique_key=...)` and the contract's
key columns both count as "declared primary key".

**Scope limit (stated, not hidden):** compiling a test renders its SQL but
does not prove a referenced column exists at *runtime* — that needs
execution. Full `dbt test` execution against materialized inputs is out of
scope for this read-only gate; run it post-deploy via
`/run-dbt-on-databricks`, or in a throwaway scratch schema.

**Reason-from-source form (inline):** reason over the inlined test config —
each declared test must reference a column the model produces, and declared
PKs must carry `not_null` + `unique`. A custom/generic test macro or singular
test whose *definition* is not inlined cannot be verified to render: mark that
specific test `n-a` ("test macro/SQL not inlined") — never a false `ok` or a
false `blocker`; only the declared-column-existence half is statically
checkable for it. Mark the live compile `n-a`.

---

## Why these three and not more

The gate's job is to be the cheap, deterministic checkpoint that stands
between "I think this is done" and the deploy. Three gates is the minimum
coherent set:

- **Compile** is the necessary condition for any deploy to succeed.
- **Schema diff** is the one failure a compile cannot see — a clean-compiling
  change that breaks downstream consumers of the deployed relation.
- **Test resolution** confirms the project's own quality bar (RFD 0013's
  PK-coverage rule) holds and the tests themselves are not broken.

Anything broader — style, performance, full standards coverage, test
*execution* — is CI's job (sqlfluff, dbt-project-evaluator) per RFD 0013, an
advisory skill (`/optimize-dbsql-query`, `/dbt-best-practices`), or
post-deploy execution (`/run-dbt-on-databricks`). Adding it here would make
the gate slow, duplicate the RFD's stated division of labor, or break
the read-only guarantee. If a new gate seems necessary, add the rule to
RFD 0008 / RFD 0013 first, then to this file — do not author a gate the RFD
does not back.
