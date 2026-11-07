---
name: build-preflight
description: |
  Run the Phase 4 Build preflight check: confirm build mode, resolve product
  type and catalog placement, inventory DPLC artifacts with agentic backfill,
  scan macro pattern signatures, verify Databricks readiness, and emit a
  build-state report cached in `.catalyst-build.yml`. Use when the user asks
  to start the Build phase or wants to know what mode to build in.
  Trigger phrases: "preflight build", "is everything ready to build",
  "check DPLC artifacts before building", "what mode should I build in".
allowed-tools: Read Bash Write Edit
metadata:
  tier: workflow
  lifecycle-phase: phase-4-build
  dependencies:
    - dbt-best-practices
    - databricks-config
    - databricks-unity-catalog
    - data-contract
    - data-model
    - transformation-spec
    - architecture-diagram
    - schedule-backfill-plan
    - integration-blueprint
    - nfr-specification
    - security-design
  consumes:
    - data-contract
    - data-model
    - transformation-spec
    - architecture-diagram
    - schedule-backfill-plan
    - integration-blueprint
    - nfr-specification
    - security-design
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    # Canonical (RFD 0012 cross-ref)
    - DBX-SEC-001              # SP identity verification during readiness check
    - DBX-SEC-002              # OAuth + SP-PAT detection; refuse user-PAT
    # Cross-ref pending RFD 0008 enumeration
    - DBX-UC-001               # catalog placement decision per env
    - DBX-UC-004               # App vs Domain catalog separation (Build vs Publish)
    # Proposed (PR 94 prose → IDs, awaiting RFD 0008)
    - DBX-COMPUTE-002          # Warehouse channel pinned explicitly (proposed)
    - DBX-COMPUTE-005          # Channel = CURRENT (or PREVIEW + rollback) (proposed)
    - DBX-WORKFLOW-006         # Readiness check: timeout + warehouse availability (proposed)
---

# Build Preflight

Run **before** any Phase 4 Build leaf skill executes. This skill gates the
build by confirming mode, catalog placement, DPLC artifact coverage, macro
pattern bindings, and Databricks platform readiness. The result is cached in
`.catalyst-build.yml` so all downstream skills can read it rather than
repeating these questions.

## When to Run

Run `/build-preflight` at the start of `/dplc-build` (Phase 4) OR whenever
the user says:
- "preflight build"
- "what mode should I build in?"
- "is everything ready to build?"
- "check DPLC artifacts before building"

If a `.catalyst-build.yml` already exists and `build_state` is cached, ask
the user whether to re-run or use the cached state.

---

## Step 1 — Establish Build Mode

Ask the user one direct question:

> **What build mode are you in?**
>
> | Mode | When to use |
> |---|---|
> | `prototype` | Iterating rapidly against a Sandbox catalog; DPLC rigor is optional; strict checks are warnings, not blockers |
> | `production` | Delivering a governed product to App Catalog / Domain Catalog; all DPLC gates must pass |
> | `lift-and-shift` | Wrapping an existing pipeline in Catalyst conventions; partial DPLC coverage is expected |
>
> If uncertain, answer with the context: "I have approved design artifacts"
> (`production`) vs. "I'm exploring" (`prototype`) vs. "I have existing SQL I
> need to wrap" (`lift-and-shift`).

Cache the answer:

```yaml
# .catalyst-build.yml
mode: prototype  # or production | lift-and-shift
```

Propagate to severity rules per
`skills/dbt-best-practices/references/rule-severity-by-mode.md`:
- `prototype` — warnings only for most SQL/DPLC rules
- `production` — blockers for SQL-NAMING-001, SQL-DBSQL-002 (+materialized defaults), SQL-DBSQL-006 (PK tests), DBX-UC-001
- `lift-and-shift` — blockers for security (DBX-SEC-001/002) + UC placement;
  everything else is a warning until migration is complete

---

## Step 2 — Product Type and Catalog Placement

Ask the user the product-type question. This determines the target catalog and
schema-naming convention per the DXP catalog architecture (see
`skills/dbt-best-practices/references/catalog-architecture.md`).

> **What type of data product is this?**
>
> | Type | Target catalog | Schema naming |
> |---|---|---|
> | **SAP** — Source Aligned Product | Source Aligned Catalog | `raw_<source>` + `stnd_<source>` per source system |
> | **DAP** — Domain Aligned Product | L0 Domain Catalog (ask which business group) | Product-named schema |
> | **CAP** — Consumer Aligned Product | L0 Domain Catalog (ask which business group) | Product-named schema |
> | **Sandbox** | Shared Sandbox Catalog | Project-named schema (**120-day TTL — data is deleted after 120 days**) |

If mode is `prototype`, **default to Sandbox** and emit the TTL warning:

> ⚠️  Prototype mode defaults to the Shared Sandbox Catalog. All datasets in
> the Sandbox Catalog are subject to a **120-day TTL** and will be
> automatically deleted. Do not publish consumer-facing data to Sandbox.

For DAP or CAP, ask the follow-up:

> Which business group owns this product? (e.g., `investments`, `retail`,
> `institutional`, `operations`) — this determines which L0 Domain Catalog
> you will write to.

Cache the results:

```yaml
# .catalyst-build.yml  (append)
product_type: SAP          # SAP | DAP | CAP | Sandbox
business_group: ""         # only for DAP / CAP; blank for SAP / Sandbox
target_catalog:
  app_catalog: "<team>-app-<env>"        # Phase 4 writes here
  domain_catalog: "<bg>-domain-<env>"   # Phase 6 publishes here
  caspian_catalog: "caspian-<env>"      # for prototype / legacy reference
sandbox_ttl_warning: false              # true when product_type == Sandbox
```

**Phase 4 build skills write to `app_catalog` only.** The `domain_catalog`
entry is pre-populated so `/setup-dbt-project` can emit it in `dbt_project.yml`
vars; it is not written to until Phase 6 (`/dplc-publish`).

---

## Step 3 — DPLC Artifact Inventory

List the `.dplc/` directory (search precedence: `$DPLC_DIR`, `./.dplc/`,
`./docs/.dplc/`). For each artifact in the Phase 1–3 inventory matrix below,
report whether the file exists:

| Phase | Artifact | Filename | Required for production? |
|---|---|---|---|
| Phase 1 | Demand Tracker Entry | `demand-tracker-entry.md` | Optional |
| Phase 1 | Business Case | `business-case.md` | Optional |
| Phase 2 | Consumer Use Case Map | `consumer-use-case-map.md` | Yes |
| Phase 2 | Feasibility Report | `feasibility-report.md` | Yes |
| Phase 2 | Requirements & AC | `requirements-acceptance-criteria.md` | Yes |
| Phase 3 | Data Contract | `data-contract.md` | **Required** |
| Phase 3 | Data Model | `data-model.md` | **Required** |
| Phase 3 | Transformation Spec | `transformation-spec.md` | **Required** |
| Phase 3 | Architecture Diagram | `architecture-diagram.md` | Recommended |
| Phase 3 | Schedule & Backfill Plan | `schedule-backfill-plan.md` | Recommended |
| Phase 3 | Integration Blueprint | `integration-blueprint.md` | Recommended |
| Phase 3 | NFR Specification | `nfr-specification.md` | Recommended |
| Phase 3 | Security Design | `security-design.md` | Yes (Restricted products) |

Format the output as a table:

```
DPLC Artifact Inventory
───────────────────────────────────────────────────────────────
 Phase 3 | data-contract          ✓  .dplc/data-contract.md
 Phase 3 | data-model             ✓  .dplc/data-model.md
 Phase 3 | transformation-spec    ✗  NOT FOUND — invoke /transformation-spec to create now? (y/n)
 Phase 3 | security-design        ✗  NOT FOUND — invoke /security-design to create now? (y/n)
 ...
───────────────────────────────────────────────────────────────
```

### Agentic backfill

For each `✗` artifact the user marks `y` on, invoke the upstream skill
in-line using its slash command. After the skill completes, re-check the file
and update the inventory entry to `✓`.

In `production` mode, the three **required** Phase 3 artifacts (data-contract,
data-model, transformation-spec) are **blockers**: if any are absent and the
user does not backfill, halt and emit:

```
❌  Build blocked: required DPLC artifact(s) missing.
    Cannot proceed without: data-contract.md, data-model.md, transformation-spec.md
    Run /data-contract, /data-model, /transformation-spec to create them, or
    switch to prototype mode (/build-preflight --mode=prototype) to proceed with warnings.
```

In `prototype` and `lift-and-shift` modes, missing required artifacts are
**warnings**, not blockers. Emit:

```
⚠️  Missing DPLC artifacts (prototype mode — non-blocking):
    - data-contract.md  [warn]
    - data-model.md     [warn]
    Build will proceed without DPLC validation. Backfill before promoting to production.
```

Cache the inventory result:

```yaml
# .catalyst-build.yml  (append)
dplc_inventory:
  data-contract: present        # present | absent
  data-model: present
  transformation-spec: absent
  # ... one entry per artifact
```

---

## Step 4 — Pattern Signature Scan

Scan `macros/` for macro names that match the Catalyst pattern signatures.
Use the reference files in `skills/dbt-best-practices/references/pattern-*.md`
for the canonical macro name for each pattern:

| Pattern | Macro name signature | Reference |
|---|---|---|
| Source wrapper | `source_wrapper` or `stg_source_` prefix | `pattern-source-wrapper.md` |
| Bitemporal incremental | `bitemporal_load_v2` or `load_bitemporal` | `pattern-bitemporal-incremental.md` |
| Audit columns | `add_audit_columns` or `audit_columns` | `pattern-audit-columns.md` |
| Audit column injection | `inject_audit_columns` | `pattern-audit-column-injection.md` |
| Checkpoint table | `checkpoint_insert` or `checkpoint_table` | `pattern-checkpoint-table.md` |
| Surrogate key | `generate_surrogate_key` or `surrogate_key` | `pattern-surrogate-key.md` |

Check with:

```bash
find macros/ -name "*.sql" | xargs grep -l "macro " 2>/dev/null
```

Report which patterns are bound (macro found) vs. unbound (macro absent):

```
Pattern Signature Scan
───────────────────────────────────────────────────────────────
 source-wrapper           ✓  macros/stg_source_wrapper.sql
 bitemporal-incremental   ✗  not found
 audit-columns            ✓  macros/add_audit_columns.sql
 checkpoint-table         ✗  not found
 surrogate-key            ✗  not found
───────────────────────────────────────────────────────────────
```

For unbound patterns, ask: "Is the `<pattern>` macro present under a different
name?" If the user provides a name, bind it.

Cache pattern bindings:

```yaml
# .catalyst-build.yml  (append)
patterns:
  source-wrapper:
    bound: true
    macro: "stg_source_wrapper"
  bitemporal-incremental:
    bound: false
    macro: null
  audit-columns:
    bound: true
    macro: "add_audit_columns"
  checkpoint-table:
    bound: false
    macro: null
  surrogate-key:
    bound: false
    macro: null
```

Downstream skills (`/source-aligned`, `/domain-aligned`, `/consumer-aligned`)
read `.catalyst-build.yml#patterns` to decide which macros to invoke rather
than asking the user again.

---

## Step 5 — Databricks Readiness Check

### Tool-version drift check (both modes)

Catalyst's skill templates are tested against specific version ranges of
`dbt-core`, `dbt-databricks`, `databricks-cli`, and `databricks-sdk`. When
the user's installed version drifts outside that range, the templates still
*emit* fine — but the emitted artifacts may exercise CLI flag orders or SDK
shapes that haven't been validated (the AICAT-138 Bug 4 failure mode).

The tested-against ranges live in `skills/requirements.txt` — there's no
per-skill duplication. Read those lines, parse the installed versions, and
emit a **warning** (not a blocker) for any mismatch.

The four tools to check (and the `requirements.txt` lines to read):

| Tool | Requirements.txt entry shape | How to read the installed version |
|---|---|---|
| `dbt-core` | `dbt-core>=<min>,<<max>` | Python dist metadata |
| `dbt-databricks` | `dbt-databricks>=<min>,<<max>` | Python dist metadata |
| `databricks-cli` | `databricks-cli>=<min>,<<max>` (a **comment** — see note below) | `databricks --version` (Go binary, **not** pip) |
| `databricks-sdk` | `databricks-sdk>=<min>,<<max>` | Python dist metadata |

For the three Python distributions, get the installed version with `python -c
"from importlib.metadata import version; print(version('<dist-name>'))"` (or
`pip show <name> | awk '/^Version: /{print $2}'` as a fallback). Compare against
the pinned range from `skills/requirements.txt`.

For `databricks-cli`, read the version from the binary instead:

```bash
databricks --version    # -> "Databricks CLI v0.287.0"
```

`pip show databricks-cli` reports the deprecated legacy Python package (≤ 0.18.0)
if it is installed at all, which is a different artifact on a different version
scheme and will produce a spurious drift warning every time.

Emit one line per tool:

```
Tool-version drift
 dbt-core         ✓  1.9.2   tested 1.8.0–1.10.x
 dbt-databricks   ✓  1.9.0   tested 1.8.0–1.10.x
 databricks-cli   ⚠  1.5.0   tested 0.218.0–0.99.x  (installed is past upper bound)
 databricks-sdk   ✓  0.42.0  tested 0.30.0–0.99.x
```

When any line is `⚠`, append a one-line guidance block naming the specific
tool, installed version, tested range, and a suggested pin:

```
[build-preflight] WARNING: installed databricks CLI is 0.287.0; skills were
tested against 0.218.0–0.99.x. Emitted bundle artifacts may exercise CLI
behavior outside that range. Verify generated bundles against your version.
```

> **`databricks-cli` is not a pip install.** The `databricks-cli>=0.218.0,<1.0.0`
> range above refers to the **Go** CLI (`databricks --version` → `v0.2xx`),
> distributed outside PyPI and installed per `docs/install.md`. The PyPI package
> of that name is the *deprecated legacy* Python CLI, which stops at **0.18.0** —
> so `pip install 'databricks-cli<1.0.0'` can never resolve the version this
> table checks against. Read the installed version from the binary
> (`databricks --version`), not from `pip show`. The range lives in
> `skills/requirements.txt` as a **comment** for exactly this reason; do not
> re-add it as an active requirement (it aborts the whole pip transaction).

Drift is **never** a blocker — proceed to the workspace checks below.
Warnings are advisory because skills work in most drift scenarios; the
warning exists to short-circuit the AICAT-138 Bug 4 debug loop when they
don't.

Cache the drift result:

```yaml
# .catalyst-build.yml  (append; sibling of databricks_readiness)
tool_version_drift:
  dbt-core:        { installed: "1.9.2", tested: ">=1.8.0,<1.11.0", ok: true }
  dbt-databricks:  { installed: "1.9.0", tested: ">=1.8.0,<1.11.0", ok: true }
  databricks-cli:  { installed: "1.5.0", tested: ">=0.218.0,<1.0.0", ok: false }
  databricks-sdk:  { installed: "0.42.0", tested: ">=0.30.0,<1.0.0", ok: true }
```

### Prototype mode (lite check)

Verify only:
1. Sandbox catalog exists and user has `USE CATALOG` on it
2. A SQL warehouse is reachable (`databricks sql list-warehouses` or
   `databricks_tools_core/sql/list_warehouses()`)

Use `skills/clients/databricks_tools_core/`:

```python
from skills.clients.databricks_tools_core.sql import list_warehouses
from skills.clients.databricks_tools_core.unity_catalog import check_catalog_access

warehouses = list_warehouses()
sandbox_ok = check_catalog_access("sandbox_catalog")
```

Emit:

```
Databricks Readiness (prototype / lite)
 SQL warehouse      ✓  <warehouse-id> (serverless, auto-stop 10 min)
 Sandbox catalog    ✓  sandbox accessible
```

### Production mode (strict check)

Verify all of:
1. **App Catalog access** — `USE CATALOG` on `app_catalog` (from Step 2)
2. **Domain Catalog access** — `USE CATALOG` on `domain_catalog`
3. **UC Volume** — `/Volumes/<catalog>/<schema>/dbt_logs/` exists or user has
   `CREATE VOLUME` on the target schema
4. **SQL warehouse** — reachable and channel is `CURRENT` (not `PREVIEW`) per
   DBX-COMPUTE-005 (proposed)
5. **Grants** — the service principal (resolved via `/connect-databricks`) has
   `CREATE TABLE` on the target schema in the App Catalog. Per DBX-SEC-002,
   readiness is verified against the SP's identity — never against a developer's
   user account.

Use strict checks:

```python
from skills.clients.databricks_tools_core.unity_catalog import (
    check_catalog_access,
    check_schema_grants,
    check_volume_exists,
)

app_ok    = check_catalog_access(app_catalog)
domain_ok = check_catalog_access(domain_catalog)
volume_ok = check_volume_exists(f"/Volumes/{app_catalog}/{schema}/dbt_logs/")
grants_ok = check_schema_grants(app_catalog, schema, privilege="CREATE TABLE")
```

Emit a readiness table:

```
Databricks Readiness (production / strict)
 SQL warehouse            ✓  abc123 (serverless, CURRENT channel)
 App Catalog              ✓  investments-app-dev — USE CATALOG OK
 Domain Catalog           ✓  investments-domain-dev — USE CATALOG OK
 UC Volume (logs)         ✗  /Volumes/investments-app-dev/hr/dbt_logs/ NOT FOUND
                              → Run: CREATE VOLUME investments-app-dev.hr.dbt_logs
 Schema grants            ✓  CREATE TABLE on investments-app-dev.hr
```

Any `✗` in production mode is a **blocker** unless the user explicitly
overrides with a documented reason. Provide the exact remediation command for
each failure.

Cache readiness:

```yaml
# .catalyst-build.yml  (append)
databricks_readiness:
  mode: production
  sql_warehouse_id: "abc123"
  app_catalog_ok: true
  domain_catalog_ok: true
  uc_volume_ok: false
  uc_volume_path: "/Volumes/investments-app-dev/hr/dbt_logs/"
  grants_ok: true
```

---

## Step 6 — Build-State Report

Inspect the dbt project directory (default: current directory; also check
`data_products/` and `dbt/` subdirectories) to determine the build state:

| State | Condition | Meaning |
|---|---|---|
| `fresh` | No `dbt_project.yml` found | Project has not been scaffolded — run `/setup-dbt-project` |
| `infra-only` | `dbt_project.yml` exists but `models/` is empty or absent | Infrastructure scaffolded; model authoring not started |
| `models-exist` | `models/` contains `.sql` files | Model authoring is underway or complete |

Emit:

```
Build State: infra-only
  dbt_project.yml    ✓  found
  models/            ✗  empty
  Next step: run /source-aligned or /domain-aligned to author models
```

Cache the state:

```yaml
# .catalyst-build.yml  (append)
build_state: infra-only   # fresh | infra-only | models-exist
dbt_project_root: "."     # relative path to dbt_project.yml
```

### Routing guidance

Based on build state, emit the recommended next step:

- `fresh` → "Run `/setup-dbt-project` to scaffold `dbt_project.yml`, profiles,
  and config files, then run this preflight again."
- `infra-only` → "Infrastructure is ready. Run `/source-aligned`,
  `/domain-aligned`, or `/consumer-aligned` to author models based on your
  product type."
- `models-exist` → "Model authoring is underway. Check
  `.catalyst-build.yml#patterns` for bound macros and run
  `/write-dbt-model` for individual dataset models."

---

## Final Summary

Print a single-page preflight summary:

```
╔══════════════════════════════════════════════════════════╗
║  /build-preflight — Summary                              ║
╠══════════════════════════════════════════════════════════╣
║  Mode           prototype                                ║
║  Product type   DAP — investments domain                 ║
║  App catalog    investments-app-dev                      ║
║  Domain catalog investments-domain-dev                   ║
╠══════════════════════════════════════════════════════════╣
║  DPLC artifacts  8/11 present (3 optional absent)        ║
║  Pattern scan    2/6 bound (source-wrapper, audit-cols)  ║
║  Tool versions   ⚠ 1 drift (databricks-cli 1.5.0)        ║
║  Databricks      ✓ lite check passed                     ║
║  Build state     infra-only                              ║
╠══════════════════════════════════════════════════════════╣
║  Next step: /source-aligned — author source-aligned      ║
║             models for the investments domain product.   ║
╚══════════════════════════════════════════════════════════╝
```

If any blockers exist (production mode, missing required artifacts, failed
Databricks checks), substitute:

```
╠══════════════════════════════════════════════════════════╣
║  ❌  BUILD BLOCKED — resolve the above before proceeding ║
╚══════════════════════════════════════════════════════════╝
```

---

## `.catalyst-build.yml` Schema Reference

The complete schema emitted by this skill:

```yaml
# Written by /build-preflight

mode: prototype                   # prototype | production | lift-and-shift

product_type: DAP                 # SAP | DAP | CAP | Sandbox
business_group: investments       # only for DAP / CAP
target_catalog:
  app_catalog: "investments-app-dev"
  domain_catalog: "investments-domain-dev"
  caspian_catalog: "caspian-dev"
sandbox_ttl_warning: false

dplc_inventory:
  data-contract: present
  data-model: present
  transformation-spec: present
  architecture-diagram: absent
  schedule-backfill-plan: absent
  integration-blueprint: absent
  nfr-specification: absent
  security-design: absent
  consumer-use-case-map: present
  feasibility-report: present
  requirements-acceptance-criteria: present

patterns:
  source-wrapper:
    bound: true
    macro: "stg_source_wrapper"
  bitemporal-incremental:
    bound: false
    macro: null
  audit-columns:
    bound: true
    macro: "add_audit_columns"
  audit-column-injection:
    bound: false
    macro: null
  checkpoint-table:
    bound: false
    macro: null
  surrogate-key:
    bound: false
    macro: null

tool_version_drift:
  dbt-core:        { installed: "1.9.2", tested: ">=1.8.0,<1.11.0", ok: true }
  dbt-databricks:  { installed: "1.9.0", tested: ">=1.8.0,<1.11.0", ok: true }
  databricks-cli:  { installed: "0.230.0", tested: ">=0.218.0,<1.0.0", ok: true }
  databricks-sdk:  { installed: "0.42.0", tested: ">=0.30.0,<1.0.0", ok: true }

databricks_readiness:
  mode: prototype
  sql_warehouse_id: "abc123"
  app_catalog_ok: true
  domain_catalog_ok: true
  uc_volume_ok: true
  uc_volume_path: ""
  grants_ok: true

build_state: infra-only           # fresh | infra-only | models-exist
dbt_project_root: "."
```

This file is read by all Phase 4 Build leaf skills. Do not modify it manually
between skill invocations unless instructed.

---

## Standards

### Canonical (RFD 0012 cross-ref)

| Standard | Where applied |
|---|---|
| **DBX-SEC-001** | Step 5 readiness — verifies identity is a service principal, not a human user |
| **DBX-SEC-002** | Step 5 readiness — refuses user-PAT auth; accepts OAuth or SP-PAT |

### Cross-ref pending RFD 0008 enumeration

| Standard | Where applied |
|---|---|
| **DBX-UC-001** | Step 2 catalog placement decision per environment |
| **DBX-UC-004** | Step 2 separates App Catalog (Build phase) from Domain Catalog (Publish phase) |

### Proposed (PR 94 prose → IDs; awaiting RFD 0008)

| Standard | Where applied |
|---|---|
| **DBX-COMPUTE-002** | Step 5 — warehouse channel pinned explicitly |
| **DBX-COMPUTE-005** | Step 5 — channel is `CURRENT` (or `PREVIEW` with rollback plan) |
| **DBX-WORKFLOW-006** | Step 5 — readiness check timeout + warehouse availability validation |

---

## References

- Catalog architecture: `skills/dbt-best-practices/references/catalog-architecture.md`
- Mode-aware severity: `skills/dbt-best-practices/references/rule-severity-by-mode.md`
- Pattern signatures: `skills/dbt-best-practices/references/pattern-*.md`
- Databricks client: `skills/clients/databricks_tools_core/`
