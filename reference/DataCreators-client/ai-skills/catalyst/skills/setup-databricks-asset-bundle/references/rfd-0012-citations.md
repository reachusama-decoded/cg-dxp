# RFD 0012 directive map — what we emit, what we defer

The skill currently emits DABs that match `edo-ig-data-products`'s
production layout. RFD 0012 (state: prediscussion) enumerates an
aspirational standard that the real repo hasn't fully adopted. Rather
than emit DABs that pass standards but fail to deploy in the team's
environment, the skill emits the **working shape** and flags the
remaining gaps as inline `# TODO DBX-…` comments.

This file is the authoritative map. When the team migrates toward the
aspirational shape, update the corresponding row's status and the
emission template in parallel.

## Where each rule is enforced (emission grep / structural test / review)

For each directive the skill currently *enforces*, the check happens in
one of three places: an emission-time grep run by the skill itself, a
structural pytest emitted alongside the bundle, or human review. This
table is the single answer to "what catches the failure if the bundle
drifts."

| Rule | Status | Where it's caught |
|---|---|---|
| **DBX-BUNDLE-001** `bundle: name + targets` | emitted | Skill writes `bundle.name = <product>` + `targets:`; structural test `test_bundle_name_and_targets`; `databricks bundle validate` parses it |
| **DBX-BUNDLE-002** One bundle per data product | emitted | Skill writes one `databricks.yml` per `data_products/<product>/`; structural test `test_exactly_one_databricks_yml_at_product_root` |
| **DBX-BUNDLE-003** Workspace host from promotions.yml | deferred | Hosts inlined per target; review only (TODO comment in `databricks.yml`) |
| **DBX-BUNDLE-004** T-shirt clusters, no inline node_type_id | deferred (partial) | Cluster shapes are vars (good — structural test `test_no_inline_node_type_id_in_job_yml`); shape internals still inline `node_type_id`; review |
| **DBX-BUNDLE-005** OAuth M2M only | n/a (deploy-side) | `connect-databricks` enforces; this skill doesn't write auth |
| **DBX-BUNDLE-006** Notifications via standard alert sink | deferred | Human-facing `email_notifications` omitted from templates; system-sink `webhook_notifications` still deferred |
| **DBX-BUNDLE-007** `tags:` block (data_product / owner / cost_center) | deferred | No `tags:` emitted today; structural test `test_main_job_tags_include_required_keys_if_present` is a placeholder that skips until `tags:` lands |
| **DBX-BUNDLE-008** `permissions:` block | deferred | No `permissions:` emitted today; review |
| **DBX-BUNDLE-009** LTS DBR | emitted | `clusters.yml` pins `15.4.x-scala2.12`; structural test `test_dbr_lts_pin_on_complex_clusters` |
| **DBX-BUNDLE-010** External tables only | n/a (data-side) | Enforced by dbt model conventions, not bundle YAML |
| **DBX-DAB-001** `databricks_job_prefix` var | deferred | Literal job names today; TODO comment + review |
| **DBX-DAB-002** Separate pipeline / compute DABs | deferred | One DAB per product covers both; comment in `databricks.yml` flags the split |
| **DBX-DAB-003** Platform-side Datadog alerts humans; DAB alerts systems | emitted | Templates omit `email_notifications.on_failure` and annotate platform-side (Astronomer Datadog) alerting ownership — no DAG callback |
| **DBX-DAB-005** Persistent compute by var | emitted | `existing_cluster_id: ${var.cluster_id}` only; structural test `test_main_job_existing_cluster_id_is_var_reference` greps for literal IDs |
| **DBX-DAB-004** `databricks_job_prefix` (compose contract) | deferred | Paired with DBX-DAB-001 |
| **DBX-DAB-006** Serverless Python | deferred | Using `existing_cluster_id`; review |
| **DBX-DAB-007** Ephemeral job_cluster allowed | emitted | DQ template declares `job_clusters` keyed by `${var.dqf_cluster}`; structural test `test_dq_job_uses_ephemeral_job_cluster` |
| **DBX-SEC-002** SP-owned objects | n/a (deploy-side) | `connect-databricks` |
| **DBX-DAB-008** cgrepo Nexus mirror | deferred (until serverless) | No `environments[]` block today; when DBX-DAB-006 lands, the dependencies list must route through cgrepo per the project CLAUDE.md |
| **Variable-declaration canary** | emitted | Structural test `test_all_referenced_variables_are_declared` catches `${var.NAME}` references with no declaration |

**Pre-emit checks (skill-side, not test-side):**

- Bundle name resolves (user input or `data_products/<product>` dir name).
- All required variables in `variables.yml` are declared (compared against a known set).
- Per-env files exist for at least one of {dev, sqa, prd}; warn if not.
- `cluster_id` is set in at least one env file; refuse to emit a job that references `${var.cluster_id}` if no env declares it.
- `databricks_runtime_spark_version` is an LTS string (regex match).
- `runtime/dq_verify.py` exists for each dataset whose DQ job YAML is emitted (warn + TODO comment if missing).

**Not checked (out of scope for emission):**

- Whether the cluster ID actually exists in the workspace — `databricks bundle deploy --validate-only` territory.
- Whether the dbt models referenced by `--select +<dataset>+` resolve — `dbt deps && dbt compile` territory.
- Whether the Deequ JAR at `${var.deequ_jar_path}` exists in the UC Volume — UC ACL check, not bundle validate.

## Status legend

| Status | Meaning |
|---|---|
| **emitted** | Skill writes the directive's required shape. CI / review can enforce. |
| **deferred** | Real repo doesn't yet conform. Skill emits the working shape with a `# TODO DBX-NNN: …` comment so the gap is visible. |
| **n/a (deploy-side)** | Directive is about deploy / runtime auth, not bundle YAML content. Out of scope for emission. |
| **n/a (data-side)** | Directive is a content constraint enforced at the dbt-model layer (table type, naming, etc.), not bundle YAML. Out of scope for emission. |

## RFD 0012 enumerated rules (001–010)

| ID | Rule | Status | Where it lives |
|---|---|---|---|
| **DBX-BUNDLE-001** | `bundle:` declares `name` + target set | **emitted** | `templates/databricks.yml` — `bundle.name: {{PRODUCT}}` + `targets:` block |
| **DBX-BUNDLE-002** | One bundle per data product | **emitted** | One `databricks.yml` per `data_products/<product>/` |
| **DBX-BUNDLE-003** | Workspace host per target from `promotions.yml` | **deferred** | `databricks.yml` inlines `workspace.host:` per target today. Move to promotions.yml resolver when `deploy-dab` lands. |
| **DBX-BUNDLE-004** | T-shirt clusters via shared `compute.yml`; no inline `node_type_id` | **deferred** | `templates/variables/clusters.yml` defines `small_cluster` + `dqf_cluster` as complex vars with inline `node_type_id: m7gd.large`. Migration: extract to a shared `compute.yml` at the org level. |
| **DBX-BUNDLE-005** | OAuth M2M only; no PATs | **n/a (deploy-side)** | Enforced by `connect-databricks` / deploy step, not bundle YAML. |
| **DBX-BUNDLE-006** | Notifications wired to standard alert sink | **deferred** | Job templates intentionally omit `email_notifications.on_failure` so Airflow remains the human-alert owner. Migration: add `webhook_notifications` to the Datadog workspace webhook for system signals once configured. |
| **DBX-BUNDLE-007** | Tags include `data_product`, `owner`, `cost_center` | **deferred** | Job templates don't emit a `tags:` block today. Migration: add when the team registers cost-attribution conventions across products. |
| **DBX-BUNDLE-008** | `permissions:` block declares run-as + reviewer groups | **deferred** | Job templates don't emit `permissions:` today. Migration: add when run-as SP names + reviewer groups are catalogued per product. |
| **DBX-BUNDLE-009** | DBR LTS runtime; no preview channels in prod | **emitted** | `clusters.yml` pins `15.4.x-scala2.12`; bump synchronously across products. |
| **DBX-BUNDLE-010** | External tables only; no managed tables | **n/a (data-side)** | Data-side constraint enforced by dbt model conventions, not bundle YAML. |

## Cross-RFD / proposed (012+, workflow / compute / sec)

These IDs appear in the existing skill's frontmatter as "proposed" pending RFD extension. Treated here the same way: emit what works today, defer the rest.

| ID | Rule | Status | Where it lives |
|---|---|---|---|
| **DBX-DAB-001** | Bundle exposes `databricks_job_prefix` var (compose with `/generate-dag`) | **deferred** | Job templates use literal `<dataset>_job` names with a TODO pointing at `${var.databricks_job_prefix}<dataset>_job`. Migration: enable when `/generate-dag`'s compose contract is wired across products. |
| **DBX-DAB-002** | Pipeline DAB and compute DAB are separate bundles | **deferred** | edo-ig-data-products ships one bundle per product covering both. Migration: extract long-lived compute (`cluster_id`, `sql_warehouse_id`) into a per-product compute DAB once `/configure-sql-warehouse` is in steady state. |
| **DBX-DAB-003** | Failure alerting is platform-side (Astronomer Datadog); DAB owns system signals | **emitted** | Job templates omit `email_notifications.on_failure`; human-facing failure alerting is provided platform-side by Astronomer's Datadog integration, not a DAG `on_failure_callback`. |
| **DBX-DAB-005** | Pipeline DAB references persistent compute by var only | **emitted** | Main job uses `existing_cluster_id: ${var.cluster_id}`; DQ job uses an ephemeral `job_cluster` keyed by `${var.dqf_cluster}`. No inline cluster IDs. |
| **DBX-DAB-004** | Bundle exposes `databricks_job_prefix` (compose contract) | **deferred** | Same as DBX-DAB-001 — paired migration. |
| **DBX-DAB-006** | Pipeline DAB tasks use serverless Python | **deferred** | Real repo runs dbt on `existing_cluster_id`, not serverless. Migration: opt-in `compute=serverless` flag once the team validates serverless against their init-script + custom-JAR needs. |
| **DBX-DAB-007** | Ephemeral per-job `job_cluster` allowed | **emitted** | DQ jobs declare `job_clusters:` with `new_cluster: ${var.dqf_cluster}`. |
| **DBX-SEC-002** | SP-owned objects; OAuth preferred | **n/a (deploy-side)** | Enforced by `connect-databricks`, not bundle YAML. |
| **DBX-DAB-008** | cgrepo Nexus mirror for environment dependencies | **deferred** | No `environments` block today (since not serverless). Migration: when `DBX-DAB-006` adopts serverless, the `environments[].spec.dependencies` list must route through cgrepo. |

## Why "deferred" instead of "violated"

Some of these directives describe a future state. Calling them violations
in CI today would mean every existing deploy fails. The skill takes the
pragmatic line: emit what passes the team's actual `databricks bundle
validate --target <env>` while marking the gap inline.

When the team is ready to adopt one of the deferred directives:

1. Update its row in this table to `emitted`.
2. Update the corresponding emission template (`templates/...`) to write
   the new shape and remove the `# TODO DBX-…` comment.
3. Bump the `Catalyst-version: N` header at the top of the emitted file
   so deployed bundles can be audited for compliance era.
