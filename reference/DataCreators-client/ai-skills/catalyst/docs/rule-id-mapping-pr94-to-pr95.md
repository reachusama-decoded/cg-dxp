# Rule-ID Translation Table — PR 94 → PR 95

**Status:** Reference table for the PR 94 → PR 95 donation refactor
**Date:** 2026-05-18
**Companion doc:** [rationalization-pr94-to-pr95.md](./rationalization-pr94-to-pr95.md)

## Background

PR 94 cites a parallel taxonomy of rule IDs (`DBX-DELTA-*`, `DBX-WORKFLOW-*`, `DBX-COMPUTE-*`, `SQL-INCR-*`, `SQL-MODEL-*`, `SQL-TEST-*`, etc.) that aren't enumerated in PR 95's canonical RFDs 0011/0012/0013. PR 95's binding rule families are:

| Family | Canonical home | Enumerated rules |
|---|---|---|
| `PY-AIRFLOW-*` | `rfd/0008/python/airflow.md` (planned; referenced by RFD 0011) | 015 enumerated in RFD 0011 |
| `DBX-BUNDLE-*` | `rfd/0008/databricks/bundles.md` (planned; referenced by RFD 0012) | 010 enumerated in RFD 0012 |
| `SQL-DBSQL-*` | `rfd/0008/sql/dbsql.md` (planned; referenced by RFD 0013) | 009 enumerated in RFD 0013 |
| `SQL-PERF-DBSQL-*` (4-part) | `rfd/0008/sql/perf-dbsql.md` (planned; referenced by RFD 0013) | 005 cited (001..005); not in RFD tables |
| `SQL-PERF-DBT-*` (4-part) | `rfd/0008/sql/perf-dbt.md` (planned; referenced by RFD 0013) | 1 cited (`-005`); others implied |
| `DBX-SEC-*`, `DBX-UC-*`, `DBX-PERF-*`, `DBT-RUN-*`, `DBT-SEC-*`, `DBT-PERF-*`, `PY-NAMING-*` | Cross-referenced by RFD 0011/0012/0013; not yet enumerated | none enumerated |

**RFD 0008 itself does not exist on main or in PR 95.** The three RFDs reference it as "delivered in PR 1" but that PR hasn't landed. This table treats the 34 enumerated rules in RFDs 0011/0012/0013 as the canonical reality, and flags everything else as cross-ref-pending or gap.

Sentinel IDs (`PY-AIRFLOW-000`, `DBX-BUNDLE-000`, `SQL-DBSQL-000`) are validator catch-alls for CLI parse failures — not real rules.

## Three buckets

- **Bucket A — Direct map.** PR 94 rule maps cleanly to a PR 95 enumerated rule. Replace the citation; engineering knowledge is preserved.
- **Bucket B — Cross-ref pending.** PR 94 rule maps to a PR 95 family that exists but isn't enumerated yet. Keep the rule ID, citing the family; flag for RFD 0008 expansion.
- **Bucket C — Gap.** PR 94 rule has no PR 95 equivalent. Keep the prose in the skill body; drop the rule-ID citation; file a follow-up to propose adding to RFD 0008.

---

## Bucket A — Direct map (clean PR 94 → PR 95 substitution)

| PR 94 rule | PR 94 meaning | PR 95 canonical | Notes |
|---|---|---|---|
| `DBX-SEC-001` | Service principal auth | `DBX-SEC-001` | Both PRs cite identically |
| `DBX-SEC-002` | OAuth M2M only; no PATs (PR 94 + PR 95 wording) | `DBX-SEC-002` (proposed refinement: SP ownership; OAuth preferred, SP-PAT acceptable fallback, user-PAT forbidden) | Both PRs cite identically; refined wording proposed during donation — see Auth model section in rationalization doc |
| `DBX-DELTA-003` | VACUUM retention ≥ 7 days | `SQL-DBSQL-009` (VACUUM RETAIN 168 HOURS) | PR 94's "≥ 7 days" is compatible with PR 95's "168 hours" (= 7 days); PR 94's *actual setting* (35 days) is stricter |
| `SQL-INCR-002` | merge strategy required on Databricks | `SQL-DBSQL-003` (Incrementals use merge strategy with `unique_key`) | Same rule, broader scope |
| `SQL-INCR-006` | Incremental works on `--full-refresh` | `SQL-DBSQL-003` | Subsumed |
| `SQL-MODEL-002` | No hard-coded references (dbt-project-evaluator) | `SQL-DBSQL-007` (Catalog and schema set per environment) | Partial overlap; PR 95's rule is narrower (catalog/schema), PR 94's is broader (any hardcoded ref) — recommend keeping prose for the broader claim |
| `SQL-MODEL-004` | Incremental materialization default for marts; primary-key tests | `SQL-DBSQL-002` (+materialized default per layer) + `SQL-DBSQL-006` (test coverage on PKs) | Splits into two PR 95 rules |
| `SQL-TEST-001` | not_null test on PKs | `SQL-DBSQL-006` (test coverage minimum: not_null and unique on declared PKs) | Subsumed |
| `SQL-TEST-002` | unique test on PKs | `SQL-DBSQL-006` | Subsumed |
| `DBX-UC-003` (PR 94: caspian_catalog var for lift-and-shift) | External tables only (PR 95) | `DBX-UC-003` (external tables only, cross-ref'd by `DBX-BUNDLE-010` + `SQL-DBSQL-005`) | Same ID, different meanings — **conflict.** PR 95's semantics win; PR 94's lift-and-shift caspian_catalog rule is unrelated engineering knowledge and should move to a different ID or drop |

---

## Bucket B — Cross-ref pending (PR 94 rule maps to a PR 95 family that exists but isn't enumerated)

Keep the family prefix; cite the ID; flag for RFD 0008 expansion.

| PR 94 rule | PR 94 meaning | PR 95 family | Status |
|---|---|---|---|
| `DBX-UC-001` | app_catalog / domain_catalog vars per environment | `DBX-UC-*` | Cross-ref'd by RFDs 0012/0013; awaiting `rfd/0008/databricks/unity-catalog.md` |
| `DBX-UC-002` | Volume target-path for dbt artifacts | `DBX-UC-*` | Same |
| `SQL-NAMING-001` | lowercase identifiers; schema naming per product type | `SQL-NAMING-*` | Cross-ref'd by `scaffold-*` skills via `PY-NAMING-*`; awaiting `rfd/0008/sql/naming.md` |
| `SQL-NAMING-002` | (semantics unclear in PR 94; likely another naming convention rule) | `SQL-NAMING-*` | Same |
| `DBX-COMPUTE-001` | Serverless or PRO warehouse type; no CLASSIC | `DBX-COMPUTE-*` | No PR 95 enumeration; family doesn't exist yet — propose `rfd/0008/databricks/compute.md` |
| `DBX-COMPUTE-002` | Pin channel explicitly | `DBX-COMPUTE-*` | Same |
| `DBX-COMPUTE-004` | Auto-stop configured on every warehouse | `DBX-COMPUTE-*` | Same |
| `DBX-COMPUTE-005` | Channel pinned to CURRENT (or PREVIEW + rollback) | `DBX-COMPUTE-*` | Same |
| `DBX-COMPUTE-006` | Cluster policy applied via `compute_policy_id` | `DBX-COMPUTE-*` | Same |

---

## Bucket C — Gap (no PR 95 equivalent; needs new RFD section or accepted prose)

These rules represent real engineering knowledge with no PR 95 home. During refactor: keep the prose in the skill body, drop the inline rule-ID citation, mark the skill body content as candidate for RFD 0008 expansion follow-up.

### DBX-DELTA family — Delta table standards (8 rules without PR 95 equivalent)

PR 94 enumerates 9 Delta rules; only DBX-DELTA-003 maps to PR 95 (VACUUM). The other 8 are PR 94 inventions covering real Delta engineering knowledge.

| PR 94 rule | Meaning | Proposal |
|---|---|---|
| `DBX-DELTA-001` | Curated tables use Delta format (`file_format='delta'`) | Propose for `rfd/0008/databricks/delta.md` |
| `DBX-DELTA-002` | Liquid clustering preferred; Z-ORDER on legacy | Propose for `rfd/0008/databricks/delta.md` |
| `DBX-DELTA-004` | `OPTIMIZE` via predictive optimization (UC managed) | Propose for `rfd/0008/databricks/delta.md` |
| `DBX-DELTA-005` | Change Data Feed when downstream needs it | Propose for `rfd/0008/databricks/delta.md` |
| `DBX-DELTA-006` | Explicit schema evolution (`ALTER TABLE`) | Propose for `rfd/0008/databricks/delta.md` |
| `DBX-DELTA-007` | `CHECK` constraints for invariants; PK is advisory in Delta | Propose for `rfd/0008/databricks/delta.md` |
| `DBX-DELTA-008` | Time-travel readers pin to version/timestamp | Propose for `rfd/0008/databricks/delta.md` |
| `DBX-DELTA-009` | DEEP CLONE for backups; SHALLOW CLONE for tests only | Propose for `rfd/0008/databricks/delta.md` |

Engineering knowledge in PR 94's `setup-dbt-project` + `dbt-best-practices` prose (UniForm, deletion vectors, autoOptimize, tune file sizes, log retention, column mapping mode) survives as **prose** in the merged skills' bodies, without rule-ID citations until the family is enumerated.

### DBX-WORKFLOW family — workflow/pipeline structure (4 rules)

| PR 94 rule | Meaning | Proposal |
|---|---|---|
| `DBX-WORKFLOW-001` | Pipeline DAB separate from compute DAB | Cross-ref `DBX-BUNDLE-002` (one bundle per data product) — but the lifecycle-separation rule is novel; propose extending RFD 0012 |
| `DBX-WORKFLOW-002` | Airflow owns orchestration, DAB owns compute | Cross-cuts RFD 0011 + 0012 — propose a section in either, or new `rfd/0008/databricks/workflow.md` |
| `DBX-WORKFLOW-005` | Log retention on UC Volume follows catalog's retention | Operational/monitoring — propose for a new ops RFD or accept as prose |
| `DBX-WORKFLOW-006` | Step 5 readiness check — timeout + warehouse availability validation | Operational — accept as prose |

### Other gaps

| PR 94 rule | Meaning | Proposal |
|---|---|---|
| `SQL-TEST-003` | Documentation coverage (model description) | Propose for `rfd/0008/sql/dbsql.md` extension (SQL-DBSQL-010?) or accept as prose |
| `SQL-TEST-005` | (semantics unclear; investigate) | TBD |
| `SQL-TEST-006` | (semantics unclear; investigate) | TBD |

---

## Vendored upstream code policy

`skills/clients/databricks_tools_core/` (41 files vendored from `databricks-solutions/ai-dev-kit`) and `skills/databricks-python-sdk/` (vendored fork) carry upstream code that supports both PAT and OAuth auth paths. Catalyst's policy:

- **Do not patch the vendored client to remove PAT code paths.** Diverging from upstream makes future re-syncs painful.
- **Enforce DBX-SEC-002 at the use site instead.** `/connect-databricks` (PR 95's OAuth-only rewrite) refuses user-PAT and is the auth gateway for every other skill. Skills that call the vendored client always go through `/connect-databricks` first.
- **Catalyst-pass on vendored skill docs is allowed.** Updating SKILL.md prose to recommend OAuth, add cgrepo `--index-url` to pip commands, and replace MCP refs with `databricks_tools_core/` Python is standard Catalyst-pass work; the Python source files stay close to upstream.

## Refactor protocol

When refactoring a PR 94 skill's frontmatter `standards: [...]`:

1. **Look up each rule in this table.**
2. **Bucket A:** replace the citation with the PR 95 canonical rule.
3. **Bucket B:** keep the family prefix (e.g., `DBX-UC-001`); add a `# cross-ref pending RFD 0008` comment if useful.
4. **Bucket C:** drop the rule from the `standards:` declaration; preserve the engineering prose in the skill body; file a follow-up issue: "Propose rule X for RFD 0008 expansion."
5. When emitting artifacts (databricks.yml, dbt_project.yml, DAG.py):
   - **Bucket A:** keep the inline `# DBX-BUNDLE-007` style comment (citing the PR 95 ID).
   - **Bucket B:** keep the comment with the family ID; reader should know it's a pending enumeration.
   - **Bucket C:** drop the inline comment; the prose in the SKILL.md is the only reference.

### Example application — `/setup-dbt-project`

Current declaration:
```yaml
standards:
  - SQL-MODEL-004
  - SQL-NAMING-001
  - DBX-UC-001
  - DBX-UC-002
  - DBX-UC-003
```

Translated:
```yaml
standards:
  - SQL-DBSQL-001    # OAuth-only profiles.yml (was implicit; now explicit)
  - SQL-DBSQL-002    # +materialized default per layer (was SQL-MODEL-004 part 1)
  - SQL-DBSQL-005    # External tables only (was DBX-UC-003)
  - SQL-DBSQL-006    # PK tests required (was SQL-MODEL-004 part 2)
  - SQL-DBSQL-007    # Catalog/schema set per environment (was DBX-UC-001 partial)
  - DBX-SEC-002      # OAuth M2M only
  - DBX-UC-001       # cross-ref pending RFD 0008 (catalog vars per env)
  - DBX-UC-002       # cross-ref pending RFD 0008 (UC Volume target-path)
  - SQL-NAMING-001   # cross-ref pending RFD 0008 (schema naming per product type)
```

Engineering knowledge that loses a rule ID but stays as prose:
- Full Delta `+tblproperties:` block (DBX-DELTA-001..009 minus 003): UniForm, deletion vectors, autoOptimize, tune file sizes, column mapping mode, log retention — body explains *why* each property is set, without citing IDs that don't exist canonically.

---

## PR 94 prose engineering knowledge — proposed rule IDs

PR 94 carries substantive engineering knowledge that lives only as prose today (Delta tblproperties, dbt patterns, catalog architecture, lifecycle separation, MDS tags, cgrepo policy). Per the rule-ID-inventory pattern, every piece of binding guidance should have an ID so it's auditable, citable, and testable.

Below are the proposed new IDs grouped by canonical RFD 0008 home. These are **proposals** — they need RBLW + RFD review to land. Until then, refactored PR 94 skills cite them as cross-ref pending (Bucket B style), and the prose stays in the skill body.

### Proposed: `rfd/0008/databricks/delta.md` — extend `DBX-DELTA-*`

Current PR 94 enumeration: 001..009. Extend with the tblproperties block sub-rules:

| Proposed ID | Rule |
|---|---|
| `DBX-DELTA-010` | UniForm Iceberg compat enabled on curated tables (`delta.universalFormat.enabledFormats='iceberg'` + `delta.enableIcebergCompatV2='true'`) |
| `DBX-DELTA-011` | Column mapping mode = `'name'` (enables rename/drop/widen for schema evolution) |
| `DBX-DELTA-012` | Deletion vectors enabled (`delta.enableDeletionVectors='true'`) — ~10x faster DELETE/UPDATE/MERGE |
| `DBX-DELTA-013` | autoOptimize.optimizeWrite enabled — small-file management at write time |
| `DBX-DELTA-014` | tuneFileSizesForRewrites enabled — MERGE-friendly file sizing |
| `DBX-DELTA-015` | `delta.logRetentionDuration` MUST equal `delta.deletedFileRetentionDuration` (footgun: VACUUM honors deletedFileRetention; mismatched values break time-travel silently) |

Note: `DBX-DELTA-003` already cross-maps to `SQL-DBSQL-009` (VACUUM RETAIN). The new 010-015 are tblproperties-block-specific.

### Proposed: `rfd/0008/databricks/compute.md` — `DBX-COMPUTE-*`

Currently cross-ref'd by PR 94; PR 95 has no enumeration. PR 94's prose covers:

| Proposed ID | Rule |
|---|---|
| `DBX-COMPUTE-001` | Serverless or PRO warehouse type; no CLASSIC for new products |
| `DBX-COMPUTE-002` | Warehouse channel pinned explicitly (CURRENT default; PREVIEW requires rollback plan) |
| `DBX-COMPUTE-003` | (reserved) |
| `DBX-COMPUTE-004` | Auto-stop configured on every warehouse; never disabled |
| `DBX-COMPUTE-005` | Channel pinned to CURRENT (or PREVIEW with documented rollback) |
| `DBX-COMPUTE-006` | Cluster policy applied via `compute_policy_id`; platform-team guardrails enforced |
| `DBX-COMPUTE-007` | Pipeline DAB tasks use serverless Python compute (`environment_key` + `client: "1"`); no inline cluster definitions in pipeline DAB |
| `DBX-COMPUTE-008` | Ephemeral per-job `job_cluster` allowed in pipeline DAB; persistent shared clusters live in the compute DAB |

### Proposed: `rfd/0008/databricks/workflow.md` — `DBX-WORKFLOW-*`

PR 94's lifecycle-separation rule is novel and load-bearing. Propose:

| Proposed ID | Rule |
|---|---|
| `DBX-WORKFLOW-001` | Pipeline DAB and compute DAB are separate bundles. Pipeline DAB owns job layout, schedule, task graph, ephemeral compute. Compute DAB owns SQL warehouses, persistent clusters. |
| `DBX-WORKFLOW-002` | Airflow owns DAG-level orchestration and alerting (`on_failure_callback`). DAB owns job-level compute and system-signal notifications (Datadog webhook). No duplicate alerting paths. |
| `DBX-WORKFLOW-003` | Pipeline DAB references persistent compute by variable only (`${var.warehouse_id}`, `${var.cluster_id}`); never declares it inline |
| `DBX-WORKFLOW-004` | Bundle exposes `databricks_job_prefix` variable for downstream skills (e.g., `/generate-dag`) to reference; never rename without coordinating with consumers |
| `DBX-WORKFLOW-005` | Log retention on UC Volume follows the catalog's retention policy |
| `DBX-WORKFLOW-006` | Step 5 readiness check — timeout + warehouse availability validation before promoting |

### Proposed: `rfd/0008/databricks/unity-catalog.md` — `DBX-UC-*`

Currently 001/002/003 are cross-ref'd. Extend with catalog architecture rules:

| Proposed ID | Rule |
|---|---|
| `DBX-UC-001` | `app_catalog` / `domain_catalog` vars declared per environment (dev/qa/sqa/prd); never hard-code prod catalog in dev profile |
| `DBX-UC-002` | dbt `target-path` set to `/Volumes/<catalog>/<schema>/dbt_artifacts` (UC Volume, not ephemeral cluster storage) |
| `DBX-UC-003` | External tables only; managed tables require explicit `meta.managed_table_waiver` in `product.yaml` |
| `DBX-UC-004` | App catalog (`<team>-app-<env>`) for Build phase; Domain catalog (`<bg>-domain-<env>`) for Publish phase; DEEP CLONE from App→Domain (catalog architecture) |
| `DBX-UC-005` | SAP schema naming: `raw_<source>` (ingestion) + `stnd_<source>` (integration) |
| `DBX-UC-006` | DAP/CAP schema naming: product-named (`<product_name>`); one schema per layer optional |
| `DBX-UC-007` | Sandbox schema naming: `<project_name>_proto` |

### Proposed: `rfd/0008/sql/dbt-patterns.md` — `DBT-PATTERN-*` (new family)

PR 94's 5 Capital Group pattern implementations deserve enumeration:

| Proposed ID | Rule |
|---|---|
| `DBT-PATTERN-001` | source-wrapper — every source goes through `stg_source_wrapper.sql` macro before downstream use |
| `DBT-PATTERN-002` | bitemporal-incremental — slowly-changing datasets use the bitemporal_load_v2 pattern (valid-time + transaction-time columns) |
| `DBT-PATTERN-003` | audit-columns — every mart model carries `_loaded_at`, `_loaded_by`, `_source_system` via `add_audit_columns()` post-hook |
| `DBT-PATTERN-004` | checkpoint-table — long-running pipelines emit a checkpoint table per run for crash-recovery and observability |
| `DBT-PATTERN-005` | surrogate-key — generated keys use `dbt_utils.generate_surrogate_key()` with explicit column ordering documented per model |

### Proposed: `rfd/0008/databricks/security.md` — extend `DBX-SEC-*`

Currently `DBX-SEC-001`/`DBX-SEC-002` are cross-ref'd. Add:

| Proposed ID | Rule |
|---|---|
| `DBX-SEC-003` | All package installs route through cgrepo Nexus mirror (`https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/`); public PyPI is blocked on the CG corporate network. Same applies to npm (cgnpm), Maven (cgmaven), Docker (cgregistry-aws), conda (conda-proxy). |
| `DBX-SEC-004` | Docker images source from `cgregistry-aws.capgroup.com`; never use public Docker Hub `FROM` directives |
| `DBX-SEC-005` | `dbt deps` includes the cgrepo CA certificate path (avoids SSL errors on internal package fetch) |

These are CG-specific but binding firm-wide.

### Proposed: extend `PY-AIRFLOW-*` for MDS tags

| Proposed ID | Rule |
|---|---|
| `PY-AIRFLOW-016` | DAG metadata tags include MDS taxonomy: `owner`, `business_function`, `data_domain`, `data_classification`, `app_id`. Distinct from DAB-level cost-attribution tags (`data_product`, `owner`, `cost_center`). |

### Proposed: extend `DBX-BUNDLE-*` for compose contract

| Proposed ID | Rule |
|---|---|
| `DBX-BUNDLE-011` | Pipeline DAB exposes `databricks_job_prefix` variable; `/generate-dag` reads it to template DAG `job_name` for cross-skill compose |

### Summary — proposed new IDs from PR 94 prose

| Family | New IDs | Total |
|---|---|---|
| `DBX-DELTA-*` | 010..015 | 6 |
| `DBX-COMPUTE-*` | 001..008 (enumerates existing cross-refs) | 8 |
| `DBX-WORKFLOW-*` | 001..006 | 6 |
| `DBX-UC-*` | 001..007 (enumerates existing cross-refs + extensions) | 7 |
| `DBT-PATTERN-*` | 001..005 (new family) | 5 |
| `DBX-SEC-*` | 003..005 (extend existing family) | 3 |
| `PY-AIRFLOW-*` | 016 (extend) | 1 |
| `DBX-BUNDLE-*` | 011 (extend) | 1 |
| **Total new IDs proposed** | | **37** |

Once these land in RFD 0008, every PR 94 skill that currently has prose-only knowledge gets a citable rule ID. The donation refactor cites them now as "Bucket B — cross-ref pending" so the IDs are in place when RFD 0008 catches up.

---

## Follow-up RFD 0008 expansion proposals

Tracking issues to file after the donation completes:

1. `rfd/0008/databricks/delta.md` — enumerate `DBX-DELTA-001..015` (15 rules)
2. `rfd/0008/databricks/compute.md` — enumerate `DBX-COMPUTE-001..008` (8 rules)
3. `rfd/0008/databricks/unity-catalog.md` — enumerate `DBX-UC-001..007` (7 rules)
4. `rfd/0008/databricks/workflow.md` — enumerate `DBX-WORKFLOW-001..006` (6 rules)
5. `rfd/0008/databricks/security.md` — extend `DBX-SEC-*` with cgrepo rules (3 new)
6. `rfd/0008/sql/dbt-patterns.md` — enumerate `DBT-PATTERN-001..005` (5 rules; new family)
7. `rfd/0008/sql/naming.md` — enumerate `SQL-NAMING-001/002`
8. `rfd/0008/sql/testing.md` — extend `SQL-TEST-*` beyond `SQL-DBSQL-006`
9. RFD 0011 extension — add `PY-AIRFLOW-016` (MDS tags)
10. RFD 0012 extension — add `DBX-BUNDLE-011` (compose contract `databricks_job_prefix`)
11. RFD 0013 extension — add doc-coverage rule (currently `SQL-TEST-003` gap)
