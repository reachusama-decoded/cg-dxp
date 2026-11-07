# DXP-aligned catalog architecture

Authoritative sources (Confluence):

- **Technical Data Catalog Organization aligned to DXP** — page 351410409 (PARTIALLY APPROVED Apr 14 2026)
- **Domain Data Catalog Taxonomy Design** — page 55220055 (APPROVED Feb 11 2025)
- **Data Product Publish Pattern in Unity Catalog: App Catalog → Domain Catalog** — page 391231086

## Three catalog types

| Catalog | Count | Hosts | Schema naming |
|---|---|---|---|
| **Source Aligned Catalog** | 1 centralized | SAP (Source Aligned Products) | `raw_<source>` + `stnd_<source>` per source system |
| **L0 Domain Catalog** | ~7-8 (one per business group) | DAP + CAP as schemas | Product-named schemas |
| **Shared Sandbox Catalog** | 1 centralized | Exploratory/intermediate datasets (120-day TTL) | Project-name schemas |

SAP → invoke `/source-aligned`. DAP → `/domain-aligned`. CAP → `/consumer-aligned`. Sandbox / prototype → any leaf with TTL warning.

## Two-catalog publishing model

- **App Catalog** — team-owned. ALL transformation logic (CDC, SCD, upsert, append, partition-replace), quality gates resolved here. dbt run writes here.
- **Domain Catalog** — governed, consumer-facing. Validated/approved outputs only.

**Publish step = `CREATE TABLE <domain_catalog>.<schema>.<table> DEEP CLONE <app_catalog>.<schema>.<table>`.** Codified in `DBX-DELTA-009`.

Phase 4 build skills write to App Catalog. The deep-clone step that lands tables in Domain Catalog is *separate* from the marketplace-listing work `/dplc-publish` orchestrates (deployment record, onboarding guide, release notes, marketplace listing — all governance / docs, no physical data move). See "Deep-clone publish pattern (suggested)" below for the recommended shape.

## Deep-clone publish pattern (suggested; pending live reference)

> **Status — 2026-05-29.** The publish step from App Catalog → Domain
> Catalog is documented as the org standard (`DBX-DELTA-009`) but **not
> yet operationalized** in any production reference. `edo-ig-data-products`
> at `origin/main` (51708bc) declares `domain_catalog` in
> `dbt_project.yml` and plumbs the var through to dbt via job `--vars`,
> but the value is empty (`""`) and no model, post-hook, or task
> executes the clone. The pattern below is Catalyst's *suggested shape*
> — designed to fit the existing var plumbing and dbt-native idioms.
> Re-validate and update this section when the platform team
> operationalizes the publish step in the production exemplar.

### Suggested shape: separate `publish_to_domain` Databricks task

After the `dbt run` task in the product's job, add a sibling
`publish_to_domain` task that runs a small Python script. The script
reads the dbt manifest (already uploaded to the `dbt_artifacts/` UC
Volume by the wrapper — see `/setup-monitoring-and-logging`,
AICAT-136), iterates over prepared-layer nodes, and runs
`CREATE OR REPLACE TABLE <domain_catalog>.<schema>.<table> DEEP CLONE <app_catalog>.<schema>.<table>`
for each. Gate the task on the bundle target so the clone only fires
on production deploys.

```yaml
# data_products/<product>/datasets/<dataset>/bundle/<dataset>.job.yml (excerpt)
resources:
  jobs:
    <dataset>_job:
      tasks:
        - task_key: dbt_run
          spark_python_task:
            python_file: ${workspace.root_path}/files/dbt_wrapper.py
            parameters: ["run", "--project-dir", "${workspace.root_path}/files/data_products/${var.data_product_name}", ...]

        - task_key: publish_to_domain
          depends_on: [{ task_key: dbt_run }]
          # Only run on production deploys; absent from dev/qa/sqa bundles.
          run_if: NONE_FAILED
          spark_python_task:
            python_file: ${workspace.root_path}/files/publish_to_domain.py
            parameters:
              - --manifest-path
              - /Volumes/${var.app_catalog}/${var.target_schema}/dbt_artifacts/${job.run_id}/dbt_run/manifest.json
              - --app-catalog
              - ${var.app_catalog}
              - --domain-catalog
              - ${var.domain_catalog}
              - --target-schema
              - ${var.target_schema}
              - --layer
              - prepared      # which tag/path identifies models to publish
```

The publish script (single shared file, lives next to `dbt_wrapper.py`
at the repo root, sync'd into each bundle via `sync.paths`):

```python
#!/usr/bin/env python3
"""publish_to_domain.py — copy prepared-layer tables from App to Domain Catalog.

Idempotent. Reads the dbt manifest produced by the prior dbt_run task,
filters to prepared-layer models, runs CREATE OR REPLACE TABLE ... DEEP CLONE
for each. Re-running is safe; CREATE OR REPLACE makes every clone idempotent.
"""
import argparse, json, sys
from databricks.sdk.runtime import sql  # ambient-auth SQL execution

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-path", required=True)
    parser.add_argument("--app-catalog", required=True)
    parser.add_argument("--domain-catalog", required=True)
    parser.add_argument("--target-schema", required=True)
    parser.add_argument("--layer", default="prepared")
    args = parser.parse_args()

    if not args.domain_catalog:
        print(f"[publish_to_domain] domain_catalog empty; skipping (likely dev/qa). exit 0.")
        return 0

    manifest = json.load(open(args.manifest_path))
    nodes = [
        n for n in manifest["nodes"].values()
        if n.get("resource_type") == "model"
        and args.layer in (n.get("tags") or [])
    ]

    failed = []
    for n in nodes:
        name = n["alias"] or n["name"]
        src = f"{args.app_catalog}.{args.target_schema}.{name}"
        dst = f"{args.domain_catalog}.{args.target_schema}.{name}"
        try:
            sql(f"CREATE OR REPLACE TABLE {dst} DEEP CLONE {src}")
            print(f"[publish_to_domain] ok: {src} -> {dst}")
        except Exception as exc:  # noqa: BLE001
            print(f"[publish_to_domain] FAILED: {src} -> {dst} :: {exc}", file=sys.stderr)
            failed.append((src, dst, str(exc)))

    if failed:
        print(f"[publish_to_domain] {len(failed)} clone(s) failed; task will exit non-zero.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Why a separate task (and not a `+post-hook`)

The earlier draft of this section recommended a dbt `+post-hook` per
model. That collapses two concerns and weakens idempotency in the
partial-failure case. A separate task is cleaner:

- **Single failure surface.** A clone failure shows up as
  `publish_to_domain` FAILED, not as a dbt model error. Governance /
  ops can distinguish "data didn't transform correctly" from "data
  transformed but wasn't promoted."
- **Atomic-ish retry.** If the publish task fails mid-run (3 of 5
  clones land, 2 fail), Domain Catalog is in a mixed state — same
  failure mode as a post-hook. **But** retry is just "rerun the
  publish task." No need to figure out which dbt models need
  re-selecting; the script re-clones everything from the same
  manifest. Each clone is individually idempotent via
  `CREATE OR REPLACE`; the whole task converges to "Domain == App for
  this manifest's prepared models."
- **No dependency on dbt's run-state tracking.** Post-hook retry
  behavior depends on materialization (table → always re-runs;
  incremental → re-runs body, hooks fire after; ephemeral → no hook).
  A separate task sidesteps that entirely.
- **Manifest-driven scope.** Reads `dbt_artifacts/<run_id>/dbt_run/manifest.json`
  — already captured to UC Volume by the wrapper. The publish task
  doesn't need its own list of tables; it inherits the dbt model
  graph automatically. New prepared models appear in the next
  publish run with no config change.
- **Different identity later, if needed.** If the platform team
  decides publish should run as a dedicated SP (separate from the dbt
  SP that owns App Catalog), this task takes a different `run_as`
  with no rewrites.
- **Same job, not a second job.** The publish task is a sibling of
  `dbt_run` inside the same DAB job. No second bundle, no second
  schedule, no cross-job coordination.

### Trade-offs to revisit

- **Gate condition.** This pattern fires on every successful `dbt_run`
  in the production bundle target. If promotion follows a different
  gate (manual approval in Marketplace, governance sign-off webhook,
  SQA→PRD env hop), pull the publish task into a *separate* bundle /
  workflow that's only deployed to the promotion environment, instead
  of conditioning inside the same job.
- **Layer scope.** Script defaults to the `prepared` tag (Phase 4
  output). If Domain Catalog should also publish integration- or
  staging-level tables, pass `--layer` accordingly or extend the
  script to accept a tag list.
- **`CREATE OR REPLACE` vs incremental clone.** The script fully
  rebuilds the Domain Catalog table on each run. For very large
  tables this is wasteful; switch to an incremental clone pattern
  once Databricks ships one stable enough to standardize on.
- **Partial-failure visibility.** The script exits non-zero on any
  clone failure, which surfaces the whole task as FAILED — but the
  per-table breakdown is only in stdout/stderr. If publish telemetry
  needs to be queryable (which Domain tables are stale vs current?),
  add a side-effect: write a JSON Lines audit file to
  `dbt_logs/<run_id>/publish_to_domain.jsonl` with one line per
  attempted clone + status. Same UC Volume scheme as the wrapper logs.
- **Auth in the script.** Above uses `databricks.sdk.runtime.sql`
  (ambient identity, same trust model the wrapper uses). For non-job
  contexts (manual catch-up runs), the script needs the same
  `DATABRICKS_HOST` / `DATABRICKS_TOKEN` short-circuit the wrapper
  has — implement when the script lands.

### Table properties — preserved automatically

`DEEP CLONE` carries the source table's `TBLPROPERTIES` to the
destination. The Catalyst default `+tblproperties:` block (UniForm,
column-mapping mode, deletion vectors, auto-optimize, file-size
tuning, the 35-day time-travel retention pair — see
`delta-table-standards.md`) is set on the App Catalog table by
`/setup-dbt-project`, and Domain Catalog inherits it via the clone.
No reapplication needed in the publish script.

`CREATE OR REPLACE TABLE ... DEEP CLONE` semantics: the existing
Domain table is fully replaced, so properties always converge to
whatever's currently on the App table. If a property is removed at
the App layer, Domain catches up automatically on the next publish.
Likewise, bumping a property at App (e.g. retention 35→90 days for a
specific product) propagates to Domain without needing a separate
Domain-side change.

**If Domain ever needs to differ from App** — e.g. governance wants
longer time-travel on Domain than App for compliance, or stricter
column-level masking — extend the publish script with explicit
overrides after the clone:

```python
# In publish_to_domain.py, after the successful clone:
overrides = domain_specific_properties(node)  # e.g. {"delta.logRetentionDuration": "interval 90 days"}
if overrides:
    props = ", ".join(f"'{k}' = '{v}'" for k, v in overrides.items())
    sql(f"ALTER TABLE {dst} SET TBLPROPERTIES ({props})")
```

No Domain-specific overrides are needed *today* — Catalyst's table
standards apply equally to App and Domain. Add the override branch
when the first divergence is decided, not before.

### TODO when a live reference exists

- Open the production exemplar (edo-ig or successor) and confirm:
  post-hook vs separate task; per-model vs per-product clone; identity
  used; gate condition; whether `CREATE OR REPLACE` or incremental.
- If the production shape diverges from this suggestion, update this
  section to match. `catalog-architecture.md` records the *current
  recommended pattern*; intentional divergences belong in
  `docs/design-divergences-from-edo-ig.md`.

## Layer tagging

Tables/schemas tagged with one of four layers:

- **Ingestion** — minimally governed
- **Integration** — semi-governed (basic DQ, ACL, SLA)
- **Publish** — fully governed (column descriptions, functional tags, DQ, SLA, ACL, classification)
- **Vendor** — minimally governed

## Environments and Data Domain hierarchy

- Environments: `dev` / `qa` / `sqa` / `prd`
- Data Domain hierarchy: Business Function → Data Domain → Data Family → Data Sub-Family. Each product gets a primary domain assigned by governance.

## How build skills consume this

- `/build-preflight` asks the product-type question (SAP / DAP / CAP / Sandbox) to determine catalog placement. Prototype mode defaults to Sandbox.
- `/setup-dbt-project` emits `dbt_project.yml` vars: `app_catalog` (Phase 4 target), `domain_catalog` (Phase 6 publish target), `caspian_catalog` (per prototype convention). Schema naming follows the table above per product type.
- `/setup-databricks-asset-bundle` passes catalog vars to the wrapper via job.yml `--vars`.

## Cross-repo dependency management

When upstream models live in another team's repo:

- **dbt Mesh** (`dependencies.yml`) — covered by Catalyst's `/working-with-dbt-mesh` skill (forked from dbt-labs).
- **dbt Loom** (`manifest.json` sharing to artifact store) — alternative not currently in Catalyst's scope. Tracked as OQ-13.
