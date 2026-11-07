# PR 94 → PR 95 Donation Brainstorm

**Status:** Draft — analysis before donation work begins
**Date:** 2026-05-18
**Branches compared:** `feat/databricks-build-skills` (PR 94, Martin + Rob) vs `feat/engineering-skills-foundations` (PR 95, Robert Walsh / RBLW)

## Context

PR 94 (113 commits, 198 files, +42,762 / -113) and PR 95 (3 commits, 158 files, +17,386 / -864) both target `main` and both build large skill suites for the same DPLC Build phase problem space. They were authored in parallel, by different people, with different taxonomies and design choices.

The strategic decision is to **donate PR 94's contributions into PR 95** rather than the reverse — PR 95's taxonomy is cleaner, fresher, and brings a coherent lifecycle pattern (`connect-* / scaffold-* / write-* / validate-* / run-* / deploy-* / optimize-*`).

This document maps where the two PRs overlap, where they're complementary, and what a merged version looks like for each pair.

## Topology summary

- **Zero literal name collisions.** Both PRs add exactly 22 net-new skills; no two have the same name.
- **5 same-job pairs** with different sophistication levels (different names, overlapping responsibility).
- **1 deleted-from-main:** PR 95 deletes main's stub `/generate-dag`; PR 94 rewrites it. Real conflict on the same file.
- **3 cross-cutting conflicts** that must be resolved repo-wide before any skill donates (paths, RFD numbering, auth model).
- **1 new architectural pattern** in PR 95 (validate-pass marker gating) that PR 94's deploy-shaped skills need to adopt.

---

## Same-job pair findings

### Pair 1 — `/generate-dag` (PR 94) vs `/write-astro-dag` (PR 95)

**What each brings:**

| PR 94 `/generate-dag` brings | PR 95 `/write-astro-dag` brings |
|---|---|
| Compose contract with `/setup-databricks-asset-bundle` (reads emitted `job_name`) | Cluster-profile templates (xs/s/m/l/xl T-shirt sizing) |
| Two emission patterns: dag-factory + astro-blueprints with auto-detection | TaskFlow vs PythonOperator switch with `--operator-style` |
| Three modes: prototype / production / lift-and-shift (different output paths) | Integrity test stub (PY-AIRFLOW-014) |
| MDS tag collection (owner / business_function / data_domain / data_classification / app_id) | Explicit PY-AIRFLOW-001..015 rule-ID coverage in emitted file |
| Anchored on RFD 0011 §N citations on every emitted line | Static `start_date`, exponential backoff retries, secrets via `Variable.get` |
| 5 vendored Airflow Python templates (`assets.py`, two callbacks, `databricks_dbt.py`, `asset_signal.py`) | DAG ID convention `<domain>__<dataset>__<frequency>` |
| Asset-driven cross-DAG triggers (per Astro pattern + RFD 0007) | OAuth secret pattern (no PATs) |
| Compose-regression integration test (caught a real `databricks_job_prefix` drift bug) | TaskFlow API default |
| Anti-goals enumerated (no PagerDuty, DLT, dbt Cloud, MCP, S3 handoff, watermark idempotency) | |

**Recommended merge: layered.** Both skills survive at different abstraction tiers.

- **`/write-astro-dag`** — leaf renderer: produces the DAG `.py` file with PY-AIRFLOW-001..015 enforced. Adopts PR 94's vendored callbacks + assets as inline emit if `--callbacks=datadog`. RBLW's templates win.
- **`/generate-dag`** — composer: reads `databricks.yml`/`job.yml`, collects MDS tags, picks mode, picks pattern, then *invokes* `/write-astro-dag` with resolved args. Survives as the Catalyst-specific orchestration entry point.

Net result: `/generate-dag` becomes a thin orchestrator. Its 5 vendored templates move to `/write-astro-dag/templates/`.

---

### Pair 2 — `/setup-databricks-asset-bundle` (PR 94, 395 lines) vs `/write-dab-resource` (PR 95, 113 lines)

| PR 94 brings | PR 95 brings |
|---|---|
| **Lifecycle separation rule** (load-bearing): pipeline DAB ≠ compute DAB | Resource-type generality (`job` / `pipeline` / `schema` / `table`) |
| Serverless Python compute defaults (`environment_key: default_python`, `client: "1"`) | T-shirt cluster sizing via `templates/cluster_profiles.yaml` |
| 4-task dbt layout (deps → seed → run → test) | DBX-BUNDLE-001..010 rule citations |
| cgrepo `--index-url` injection in environment dependencies | Managed-table waiver gate (`meta.managed_table_waiver` in product.yaml; exits 7 without) |
| Per-env variable files (`variables_dev.yml`, etc.) | OAuth service principal run-as (DBX-BUNDLE-005) |
| `databricks_job_prefix` variable (load-bearing compose contract with `/generate-dag`) | External-table storage-location requirement (DBX-BUNDLE-010) |
| Refuses `email_notifications.on_failure` at job level (Airflow owns alerting) | Workspace host via `${var.workspace_host}` from promotions.yml (DBX-BUNDLE-003) |
| Reads `.dplc/data-model.md`, `.dplc/schedule-backfill-plan.md`, `.catalyst-build.yml` | Composes with `register-data-contract` |
| Multi-dataset glob pattern (`datasets/**/bundle/*.yml`) | |
| Handoff sequence to other Phase 4 skills | |

**Recommended merge: layered.** Two skills, different roles.

- **`/write-dab-resource`** stays as RBLW designed — generic resource emitter, one CLI call per file. **Add from PR 94:** lifecycle-separation refusal (won't emit `sql_warehouse_definition` inside a `job` resource — route to `/configure-sql-warehouse`), cgrepo `--index-url` injection on environment deps, `databricks_job_prefix` variable declaration (compose contract with `/generate-dag`), `--task-layout dbt-4task` option emitting the deps/seed/run/test pattern.
- **`/setup-databricks-asset-bundle`** survives as the **dbt-pipeline composer** — reads DPLC artifacts, iterates datasets, calls `/write-dab-resource --resource-type job --task-layout dbt-4task` per dataset, writes per-env `variables_<env>.yml` files. Retains the lifecycle-separation rule callout.

---

### Pair 3 — `/setup-dbt-project` (PR 94, 395 lines) vs `/scaffold-dbt-project` (PR 95, 75 lines)

Same skill at very different completeness levels. PR 95's covers the basics; PR 94's has every CG-specific opinion baked in.

**Donate into `/scaffold-dbt-project`** (PR 95's taxonomy wins):

| From PR 94 → PR 95 | Why |
|---|---|
| 4 more output files: `.sqlfluff`, `.pre-commit-config.yaml`, `.dbtignore`, `models/sources.yml` stub | Production-ready scaffold; not just dbt_project.yml |
| UC Volume `target-path` (DBX-UC-002) | Avoids ephemeral cluster storage; volumes persist across restarts |
| Full Delta `+tblproperties:` block (UniForm, deletion vectors, 35-day retention) | CG backup standard alignment; matches `/dbt-best-practices` references |
| Product-type-aware schema naming (SAP / DAP / CAP / Sandbox) | Catalog architecture from DXP |
| Four environment targets in `profiles.yml` (dev/qa/sqa/prd) | RBLW only has dev/qa/prod; `sqa` is real at CG |
| RFD 0008 `.sqlfluff` rules (SQL-NAMING-001 lowercase, sparksql, jinja templater) | Linting at author time |
| Read from `.catalyst-build.yml` (from `/build-preflight`) + `.dplc/data-contract.md` + `.dplc/data-model.md` | Plugs into DPLC artifact chain |
| Pattern bindings support (source-wrapper, audit-columns) | Loads from `/dbt-best-practices` |
| Setup checklist + next-step routing | UX |
| Comment rejecting `dbt-project-evaluator` runtime dep | Catalyst enforces those rules at gen time |

**Keep from PR 95:**

- OAuth-only `profiles.yml` (SQL-DBSQL-001) — PR 94's uses PAT (`DATABRICKS_TOKEN`), which violates DBX-SEC-002. Win for PR 95.
- Project name = `<domain>_<product>` snake_case (PR 94 uses kebab-case `product_name`; needs to switch)
- Catalog resolution chain: `--catalog` → `meta.uc_catalog` → domain fallback
- `loaded_by: authoring-dbt-on-dbsql` document-tier wiring

---

### Pair 4 — `/run-dbt-on-databricks` (PR 94, 270 lines) vs `/run-dbt` (PR 95, 80 lines)

**Different lifecycle phases, not duplicates.**

- **`/run-dbt`** = deploy-stage gated executor. Marker-gated (refuses without `validate-dbt` pass), OAuth-only, structured exit codes (0/2/3/4/5), token redaction. CI-friendly.
- **`/run-dbt-on-databricks`** = build-stage developer cookbook. Three modes (local CLI / bundle-deploy / bundle-run), `--python-params` JSON args, recipes for selectors / full-refresh / debug.

**Decision (2026-05-18): collapse into a single `/run-dbt` skill.**

- `/run-dbt` (PR 95's name + marker-gating shape) survives as the only "run dbt" skill.
- Body stays terse — RBLW's design intent preserved.
- PR 94's mode 1-3 cookbook content moves to reference files loaded by `/run-dbt`:
  - `/run-dbt/references/local-iteration.md` — `dbt run --target local --select`, `--full-refresh`, `--debug`, `dbt compile`
  - `/run-dbt/references/bundle-deploy.md` — `databricks bundle deploy --target dev`, dry-run via `bundle validate`, resource-specific deploys
  - `/run-dbt/references/bundle-run.md` — `databricks bundle run` with `--python-params` JSON args for dbt CLI passthrough, async `--no-wait`, target mapping
  - `/run-dbt/references/selectors-and-full-refresh.md` — dbt node-selection grammar recipes
- Body gets a "Developer iteration" callout linking the references. Marker gating only applies when `--target` is `qa` or `prod`; local iteration is unconstrained.
- `/run-dbt-on-databricks` is dropped as a standalone skill.
- `/troubleshoot-dbt-on-databricks` routing pointer moves into `/run-dbt`'s body (or its own reference file).

---

### Pair 5 — `/dbt-best-practices` (PR 94) vs `/authoring-dbt-on-dbsql` (PR 95)

PR 95's is a thin **document-tier loader** (other skills `loaded_by` it). PR 94's is a fat **capability skill** with mode-aware decision logic in the body.

**Recommended merge:** Keep PR 95's document-tier shape. Donate PR 94's content as additional reference files under `/authoring-dbt-on-dbsql/references/`:

- `references/patterns/source-wrapper.md` ← PR 94's source-wrapper pattern
- `references/patterns/bitemporal-incremental.md` ← PR 94's bitemporal-incremental pattern
- `references/patterns/audit-columns.md`
- `references/patterns/checkpoint-table.md`
- `references/patterns/surrogate-key.md`
- `references/rule-severity-by-mode.md` ← mode-aware enforcement (prototype/production/lift-and-shift)
- `references/dpe-categorical-rules.md` ← dbt-project-evaluator categorical rules
- `references/absorbed-*.md` ← absorbed dbt-labs analytics-engineering content (Apache 2.0)
- `references/catalog-architecture.md` ← DXP catalog architecture (SAP/DAP/CAP/Sandbox)
- `references/delta-table-standards.md` ← Catalyst Delta tblproperties block + rationale

PR 95's `/authoring-dbt-on-dbsql/SKILL.md` body gets a new section linking these references and a callout about mode-aware severity.

**Drop `/dbt-best-practices` as a standalone skill.** PR 94's body is reduced to reference files under PR 95's authoring doc.

---

### Pair 6 — `/scaffold-repo-structure` (PR 94) vs `/scaffold-domain-repo` + `/scaffold-data-product` (PR 95)

PR 95 splits the scaffolding work by lifecycle scope (once-per-repo + once-per-product). PR 94 has ONE skill that's both a directory emitter and a path-lookup reference for other skills.

**Path convention conflict — load-bearing:**

| PR 94 path | PR 95 path |
|---|---|
| `data_products/<product>/datasets/<dataset>/` | `data-products/<domain>/datasets/<product>/` |
| Underscore separator | Hyphen separator |
| No domain layer | Domain layer required |

PR 95's path is RFD 0003 compliant. PR 94's was the operational prototype layout from `edo-ig-data-products` and pre-dated RFD 0003.

**Recommended merge:**

1. Adopt PR 95's path convention everywhere (`data-products/<domain>/datasets/<product>/`).
2. Keep PR 95's two-skill split (`/scaffold-domain-repo` + `/scaffold-data-product`).
3. Donate PR 94's contributions:
   - Add `.catalyst-build.yml` stub to `/scaffold-domain-repo`'s output (drives `/build-preflight`)
   - Add `airflow/`, `runtime/`, `init_scripts/`, `python/<pkg>/` subdirs to `/scaffold-data-product`'s output (from PR 94's canonical layout)
4. **Drop `/scaffold-repo-structure` as a standalone skill.** Its `references/repo-structure.md` content moves to `/authoring-databricks-bundles/references/repo-layout.md` (and/or `/authoring-airflow-on-astronomer/references/repo-layout.md`) — cited by leaves the same way RBLW's references are.
5. **Cross-cutting:** every PR 94 leaf skill that emits a path needs a search-and-replace from `data_products/<product>/` → `data-products/<domain>/datasets/<product>/`. This affects `/setup-databricks-asset-bundle`, `/generate-dag`, `/setup-dbt-project`, `/configure-sql-warehouse`, `/setup-monitoring-and-logging`, `/write-dbt-wrapper`.

---

### Pair 7 — `/dplc-build-stage` (main, both PRs inherit) vs `/dplc-build` (PR 94 net-new)

**Not duplicates** — different scope:

- `/dplc-build-stage` (main) = full **Build STAGE** = Phases 4 (Build) + 5 (Validate) + 6 (Publish)
- `/dplc-build` (PR 94) = **Phase 4 only** (Build)

**Recommended merge:** Donate `/dplc-build` as-is into PR 95. The naming is consistent with PR 95's `/dplc-validate` (Phase 5) — main already has both `dplc-validate` and `dplc-build-stage`. The hierarchy becomes:

- `/dplc-build-stage` invokes `/dplc-build` (Phase 4) → `/dplc-validate` (Phase 5) → `/dplc-ship-stage` (Phase 6, on main)

Mode-awareness (prototype/production/lift-and-shift) from PR 94's `/dplc-build` survives intact.

---

## PR 94's unique skills (pure donation, no merge needed)

| Skill | Donates as | Notes |
|---|---|---|
| `/build-preflight` | new in PR 95 | Writes `.catalyst-build.yml` consumed by every other Phase 4 skill. Net-new infrastructure. |
| `/configure-sql-warehouse` | new in PR 95 | Owns the **compute** DAB (vs PR 94/95's pipeline DAB). Load-bearing lifecycle-separation rule. |
| `/write-dbt-wrapper` | new in PR 95 | `dbt_wrapper.py` with cgrepo CA cert handling on `dbt deps`. |
| `/setup-monitoring-and-logging` | new in PR 95 | `cluster_log_conf` → UC Volume + per-product `runbook.md`. |
| `/troubleshoot-dbt-on-databricks` | new in PR 95 | Failure-mode table with cgrepo-specific entries. |
| **8 ai-dev-kit forks** + **3 dbt-labs forks** | new in PR 95 | Vendored upstream content; live alongside PR 95's `authoring-*` docs as upstream reference. RBLW's `authoring-*` distills; PR 94's forks preserve. Both can coexist. |
| `skills/clients/databricks_tools_core/` (41 Python files) | new in PR 95 | Vendored upstream client; lives alongside PR 95's existing `skills/clients/databricks.py`. |

---

## PR 95's unique skills (PR 94 doesn't have equivalents — PR 95 just brings them)

| Skill | What it does | PR 94 missed it because |
|---|---|---|
| `/validate-astro-dag`, `/validate-dab`, `/validate-dbt` | Static + CLI-driven validation; emit `.claude/markers/<system>/<name>.pass` | PR 94's checks are inline in each skill body; no cross-skill gating |
| `/deploy-astro`, `/deploy-dab` | Marker-gated deploy via `promotions.yml` | PR 94 has no deploy skill — `/run-dbt-on-databricks` mode 2 is the closest |
| `/connect-astro` | Astronomer OAuth | PR 94 only covers Databricks |
| `/optimize-databricks-job`, `/optimize-dbsql-query`, `/optimize-dbt-model` | Performance findings against rule IDs (advisory; never mutate) | PR 94 has no optimize trio |
| `/register-data-contract` | ODCS contract registration | PR 94 documents the gap (`docs/todos/dq-skills-coverage.md`) |
| `/write-dbt-{model,source,test}` | Three separate leaf scaffolders | PR 94 has no model-authoring skills — defers to `/source-aligned`, `/domain-aligned`, `/consumer-aligned` (on main) |

---

## Cross-cutting conflicts (must be resolved before any donation)

### 1. Path convention — `data_products/` vs `data-products/<domain>/datasets/`

**Decision:** Adopt PR 95's (RFD 0003 compliant). Every PR 94 emitter needs path rewrites.

**Cosmetic rename, not a structural conflict (resolved 2026-05-19):** I initially flagged this as a deep architectural conflict; on review with Rob it's purely a directory renaming. Both models agree: **one product comprises multiple tables**. PR 94's inner `<dataset>` is a table-folder inside a product, not a separate product. The translation:

| PR 94 path component | RFD 0003 equivalent |
|---|---|
| `data_products/` | `data-products/` |
| `<product>/` (outer) | `<domain>/datasets/<product>/` (the product is the deliverable) |
| `datasets/<dataset>/` (inner, table-folder grouping) | Collapses into the product's `dbt/{raw,staging,intermediate,curated}/` subfolders + the product's single `bundle/` + single `airflow/` |

Concretely for edo-ig-data-products: today's `data_products/employee_directory/datasets/cg_employee_v4/dbt/` is the same product as today's `data_products/employee_directory/datasets/employee_history/dbt/` — both are tables/models within the `employee_directory` product. Under RFD 0003 they live under `data-products/investments/datasets/employee_directory/dbt/{layer}/cg_employee.sql` and `.../employee_history.sql` — same product, multiple models.

The one Airflow-side inconsistency to settle with RBLW remains: `/scaffold-domain-repo` writes `airflow/dags/` at repo root, while `/write-astro-dag` emits to `<product>/airflow/<dag_id>.py`. RBLW needs to pick one.

### 2. RFD numbering (0011 / 0012 / 0013)

**Decision (2026-05-18):** Use PR 95's RFD numbering. RBLW's RFDs 0011/0012/0013 are newer than the planning the team had on hand. Drop PR 94's `docs/rfd-drafts/2026-05-15-rfd-0011-v2-proposal.md` or fold its content into RBLW's RFD 0011 as a section update. Skill citations on PR 94's side update accordingly.

### 3. Auth model — object ownership, not credential format

| Skill | PR 94 | PR 95 |
|---|---|---|
| `connect-databricks` | inherits main (older PAT-tolerant) | rewrites to OAuth-only (DBX-SEC-002), refuses PAT |
| `profiles.yml` in dbt setup | `token: {{ env_var('DATABRICKS_TOKEN') }}` | `auth_type: oauth` with `client_id`/`client_secret` env_vars |

**Decision (refined 2026-05-18):** the binding principle is **service-principal ownership of production database objects**, not the credential format. PR 95's current framing ("no PATs") is right in spirit but conflates PAT-the-credential-type with PAT-issued-to-a-user — a service principal can also hold a PAT, and that's an acceptable transitional state while OAuth is being set up.

Three legitimate auth shapes, ranked:

| Auth | Identity | Object ownership | Status |
|---|---|---|---|
| **OAuth M2M (client credentials)** | Service principal | SP-owned | Preferred — short-lived rotating tokens, full SP audit trail |
| **PAT for service principal** | Service principal | SP-owned | Acceptable fallback — static credential but ownership semantics are correct |
| **PAT for human user** | Developer | Human-owned | **Forbidden** — creates orphaned objects when devs leave, mixes audit trails, breaks lifecycle management |

Refactor consequences:

- `profiles.yml` emission: primary block is OAuth; commented fallback shows SP-PAT (never user-PAT). Inline warning explains *why* user-PAT is forbidden (ownership semantics).
- `/connect-databricks` refusal logic loosens: refuse user-PAT (detect via SP identity check on the token); accept SP-PAT as warning-level fallback; prefer OAuth.
- Skill prose anchors on ownership ("objects created by this skill will be owned by the service principal identified by `DBX_CLIENT_ID`"), not on credential format.

To discuss with RBLW: PR 95's `profiles-yml.md` says *"PATs are user-scoped, do not rotate, and bypass the SP-level audit trail"* — accurate for user-PATs, imprecise for SP-PATs. Worth refining `DBX-SEC-002`'s wording during donation. Proposed rewording: *"Production database objects must be created by a service principal identity. OAuth M2M is the standard auth mechanism; PAT issued to a service principal is an acceptable fallback. PAT issued to a human user is forbidden in any path that creates database objects."*

### 4. Validate-pass marker pattern adoption

PR 95 introduces `.claude/markers/<system>/<name>.pass` as a cross-skill gating mechanism. PR 94 has no equivalent.

**Decision:** PR 94's deploy-shaped skills adopt it.

- `/run-dbt-on-databricks` mode 2/3 (`bundle-deploy`/`bundle-run`) → refuse without `/validate-dbt` marker
- `/setup-databricks-asset-bundle` → write a hint at the end recommending `/validate-dab` before deploy

### 5. Standards / rule-ID convention

PR 95 uses tight rule IDs (`PY-AIRFLOW-001..015`, `DBX-BUNDLE-001..010`, `SQL-DBSQL-001..009`) cited inline in emitted artifacts. PR 94 cites broader categories (`DBX-WORKFLOW-001`, `DBX-COMPUTE-004`, `DBX-UC-001..003`) and RFD section numbers.

**Decision:** Adopt PR 95's rule-ID granularity. Where PR 94 cites a category (e.g., `DBX-WORKFLOW-001`), map to the specific PR 95 rule ID(s) in the merged version.

### 6. Tests directory layout

PR 94: `skills/tests/` + `tests/behavior/`. PR 95: `tests/skills/` + `tests/behavior/` + `tests/integration/` + `tests/baselines/` + `tests/ci/`.

**Decision:** PR 95's layout wins. PR 94's ~700 cross-cutting tests move to `tests/skills/` and `tests/integration/` accordingly.

---

## Proposed donation sequence

Six chunks, each a focused PR against `feat/engineering-skills-foundations` (or against main after PR 95 merges, depending on timing):

| # | Chunk | Risk | Why this position |
|---|---|---|---|
| **1** | Cross-cutting reconciliation: path convention + OAuth-only + rule-ID mapping in PR 94's skills | High | Gates everything else; precondition discussion with RBLW |
| **2** | Pure donations with no PR 95 collision: `/build-preflight`, `/configure-sql-warehouse`, `/write-dbt-wrapper`, `/setup-monitoring-and-logging`, `/troubleshoot-dbt-on-databricks`, vendored forks, `databricks_tools_core/` | Low | No naming conflict; proves donation mechanism |
| **3** | `/dplc-build` Phase 4 orchestrator + `/setup-databricks-asset-bundle` composer | Medium | Lifecycle-separation rule is the load-bearing addition |
| **4** | Merge content into PR 95's existing skills: `/scaffold-dbt-project`, `/write-dab-resource`, `/run-dbt-on-databricks` (companion to `/run-dbt`), `/authoring-dbt-on-dbsql` (with 10+ new reference files), `/scaffold-data-product` + `/scaffold-domain-repo` | High | RBLW will want to review each carefully |
| **5** | `/generate-dag` + `/write-astro-dag` layering | Medium | Restores main's deleted `/generate-dag` (with PR 94's depth); RBLW's `/write-astro-dag` becomes the leaf renderer |
| **6** | Test infrastructure migration: PR 94's `skills/tests/` → PR 95's `tests/skills/` + `tests/integration/` | Medium | After all skills land |

---

## Skills to drop (after donation completes)

- `/scaffold-repo-structure` — content folds into `/scaffold-data-product` + `/authoring-databricks-bundles/references/repo-layout.md`
- `/dbt-best-practices` — content folds into `/authoring-dbt-on-dbsql/references/`
- PR 94's `/setup-dbt-project` — content merges into PR 95's `/scaffold-dbt-project`
- `/run-dbt-on-databricks` — content folds into `/run-dbt/references/*.md`

## Skills that survive both PRs as-is

PR 94 keeps: `/dplc-build`, `/build-preflight`, `/configure-sql-warehouse`, `/setup-databricks-asset-bundle`, `/write-dbt-wrapper`, `/setup-monitoring-and-logging`, `/troubleshoot-dbt-on-databricks`, `/generate-dag`, 11 vendored forks.

PR 95 keeps everything (it's the donation target).

---

## Open questions

All three load-bearing questions are settled (paths → PR 95; RFD numbers → PR 95; run-dbt → collapse into PR 95's). Remaining open detail to confirm with RBLW during donation:

- **Validate-pass marker behavior in collapsed `/run-dbt`** — does `--target qa` or `--target prod` hard-fail without a marker (RBLW's current shape), or warn-and-prompt? Default: hard-fail (per RBLW's design).

---

## Conflict findings — PR 94 emissions vs PR 95 / RFD 0011-0013 standards

Conflicts identified after reading RFDs 0011 (Airflow), 0012 (DAB), 0013 (dbt on DBSQL) and grepping PR 94's emissions.

### Hard conflicts (must fix in PR 94 before donation)

| # | Conflict | Affected PR 94 files | RFD/Rule violated |
|---|---|---|---|
| 1 | **PAT auth (`DATABRICKS_TOKEN`)** in 10+ files | `clients/databricks_tools_core/auth.py`, `clients/databricks_tools_core/client.py`, `configure-sql-warehouse/SKILL.md`, `connect-databricks/SKILL.md` (inherited from main, predates PR 95's rewrite), `databricks-python-sdk/SKILL.md` + examples, `data-profiling/`, `discover-data/`, `domain-aligned/` (inherited); `setup-dbt-project/SKILL.md` profiles.yml uses `DATABRICKS_TOKEN` | DBX-SEC-002, SQL-DBSQL-001, SQL-DBSQL-008 |
| 2 | **Hardcoded workspace host placeholders** (`<workspace>.azuredatabricks.net`) instead of reading from `promotions.yml` | `setup-dbt-project` profiles.yml (4 environments) | DBX-BUNDLE-003, SQL-DBSQL-007, RFD 0004 |
| 3 | **No `promotions.yml` integration** — PR 94 has zero references to it | All PR 94 emitters (path resolution, deployment IDs, workspace hosts) | RFD 0004 |
| 4 | **DAB tags missing** — no `data_product` / `owner` / `cost_center` on emitted jobs | `setup-databricks-asset-bundle/SKILL.md` job.yml template | DBX-BUNDLE-007 |
| 5 | **DAB permissions block missing** | `setup-databricks-asset-bundle/SKILL.md` job.yml template | DBX-BUNDLE-008 |
| 6 | **`standards:` declarations cite rule families that don't exist** in RFD 0008/0011/0012/0013 — PR 94 cites `DBX-WORKFLOW-*`, `DBX-COMPUTE-*`, `DBX-UC-*` (not in enumerated rules) | Every PR 94 skill's frontmatter | RFD 0008 enumeration |
| 7 | **`lifecycle-phase` schema mismatch** — PR 94 uses `phase-4-build`; PR 95's new skills use bare `build`, `scaffold`, `deploy`, `optimize`, `validate` | All net-new PR 94 skill frontmatter | RBLW's metadata migration in progress |

### Soft conflicts (need clarification with RBLW)

| # | Question | Detail |
|---|---|---|
| 8 | What is "the standard alert sink" in DBX-BUNDLE-006? | PR 94 emits **no notifications block** in DAB job.yml (says "Airflow owns alerting"). RFD 0012 DBX-BUNDLE-006 requires "Notifications block wired to the standard alert sink." Reconcilable if standard sink = Datadog webhook in DAB **and** Airflow keeps `on_failure_callback`. |
| 9 | Is SQL-DBSQL-009 (`VACUUM RETAIN 168 HOURS`) a **minimum** or an **exact** value? | PR 94 sets `deletedFileRetentionDuration: interval 35 days` (840 hours) per CG backup standard. If 168 is minimum, PR 94 is compliant; if exact, conflict. |
| 10 | Is the DAG ID convention `<domain>__<dataset>__<frequency>` (PY-AIRFLOW-012) enforced in `/generate-dag`? | grep finds no evidence — needs update |
| 11 | Does PR 94's `asset_signal.py` template emit the RFD 0007 data-ready event **v2** exactly? | PY-AIRFLOW-015 binds to RFD 0007 v2; needs verification |

### Non-conflicts (looked like conflicts but aren't)

- `node_type_id` in `databricks_tools_core/compute/*.py` — that's a Python helper for programmatic cluster creation, not DAB YAML emission. DBX-BUNDLE-004 applies to bundle YAML, not to imperative cluster-creation code.
- `tier:` values — both PRs use `workflow`, `capability`, `document`, `orchestrator`. Compatible.
- `allowed-tools:` field — PR 95 doesn't ban it, just doesn't always use it. PR 94's skills can keep theirs.
- VACUUM 35-day retention is **stricter** than DBX-DELTA-003's "≥ 7 days" — PR 94's own rule is the more binding one.

### Refactor sequence implication

The hard conflicts cluster around one architectural seam: **PR 94 doesn't know about `promotions.yml`**. Fixing #1 (PAT → OAuth), #2 (hardcoded hosts), and #3 (promotions.yml integration) together makes sense — they're the same refactor at different leaves. #4-5 are isolated YAML emission additions. #6-7 are mechanical frontmatter rewrites.

**Recommended canary skill: `/setup-dbt-project`.** It touches the heaviest emissions (profiles.yml with 4 envs, hardcoded hosts, PAT, `standards:` declarations) so refactoring it end-to-end validates the pattern for every other skill.
