---
authors: RBLW
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/3
labels: architecture, repository, governance
---

# RFD 0003 Repository Strategy

## Introduction

Capital Group's Enterprise Data Office (EDO) operates Caspian, an enterprise
data lake platform on Databricks with Unity Catalog. With domain-aligned
data engineering teams plus a platform team, we need a repository strategy that
enables domain team autonomy while facilitating shared component reuse and
cross-team collaboration.

This RFD defines the repository strategy for **domain data repositories** --
the repos where domain teams build and maintain their data products. It covers
directory structure, dbt project configuration, cross-domain access patterns,
testing, and governance. Platform infrastructure (Terraform, shared libraries,
CI/CD templates) is maintained separately by the platform team and consumed
by domain repos via versioned packages; the platform repo strategy is out of
scope for this RFD.

A key governance constraint: domain teams consume shared packages (e.g.,
`caspian-core`) via version pinning and must stay within one major version of
the latest release. Versions older than 12 months are unsupported. See
[Platform Package: caspian-core](#platform-package-caspian-core) for the full
versioning and supply chain policy.

## Background

With many domain teams working with dbt, Airflow, Spark, and Terraform, we
need a repository structure that balances autonomy with consistency. Teams
need to own their code and deploy independently, but shared components --
dbt packages, CI/CD templates -- must be reusable across teams without
duplication. Security and access control boundaries must align with
organizational structure, and the strategy must scale as new domain teams
are added.

## Proposal

### Delivery Independence

A repository is scoped to the smallest unit that needs to **deliver
independently**. The goal is that a team can build, test, and deploy without
coordinating with other teams. What determines that boundary varies -- it may
be an entire domain, a sub-domain, or a team's product set. The right grain
depends on the team's situation, and it will change over time as teams grow
and products mature.

This is not a one-size-fits-all decision. A new domain with one team and a
handful of models should start with a single repo. A large domain with
multiple teams, different deployment cadences, and distinct on-call rotations
should split. The strategy supports both and provides a path between them.

### Repository Grain

Three grains are supported. Teams choose based on their delivery needs:

| Grain | When to use | Example |
|---|---|---|
| **Domain** | Small domain, one team, shared deployment pipeline. The default starting point. | `investments-data` |
| **Sub-domain** | Large domain with distinct product groups that need independent delivery (different release cadences, different SLAs, different on-call). | `investments-positions-data`, `investments-attribution-data` |
| **Product set** | Team-scoped set of products that delivers together, regardless of where they sit in the domain hierarchy. | `pricing-valuation-data` |

**When to split.** Split a repo when the cost of coordination exceeds the
benefit of co-location. Signals that a split is overdue:

- Two teams in the same repo routinely block each other's deployments.
- CI takes too long because unrelated code is tested together.
- On-call rotation is ambiguous because the repo spans multiple support
  boundaries.
- Astronomer or another orchestrator requires a separate deployment that the
  shared repo cannot accommodate (Astronomer maps 1:1 between Git repos and
  Airflow deployments).

**When to merge.** Merge repos when the overhead of cross-repo coordination
exceeds the benefit of independence. Signals:

- Two repos share most of their dbt macros and source definitions.
- Changes routinely require synchronized PRs across both repos.
- The team is small enough that a single repo simplifies their workflow.

Splitting and merging are **team-level decisions**, not architecture review
gates. The team that owns the repos decides when the grain is wrong and
adjusts. The exception is repos that write to **multiple domains** (see
Multi-Domain below) -- those require platform team review because they
affect cross-domain governance.

### Multi-Domain Repositories

A single repository that writes to **multiple domain catalogs** is the most
complex pattern. It occurs when closely related domains share significant
data lineage or when a shared pipeline produces outputs consumed by multiple
domains. The repository must clearly delineate which models belong to which
domain (e.g., via directory structure or dbt project configuration).

Multi-domain repos **require architecture review and written approval from
the platform team** before adoption. The approval must include a documented
access control plan covering CI/CD scoping, CODEOWNERS configuration, and
deployment coordination.

### Invariants

Regardless of grain, the following always hold:

- Every repository has exactly **one owning team**.
- Every Unity Catalog object has exactly **one owning domain**.
- CI/CD pipelines are scoped **per repository**, not per domain.
- Cross-domain data access is always through the **domain catalogs** only.
- The repository name starts with the registered domain name (see Naming
  Convention below).

### Domain Repositories

Domain repositories are organized around data products. Each product lives
under `data-products/{domain}/datasets/{product}/` and contains its own
platform-specific code -- dbt models, Airflow DAG definition, Databricks
bundle, contract, and specs -- co-located within the product boundary.
Domain-level concerns (a single dbt project, shared macros, environment
variables) live at the domain level. Repo-level configuration (devcontainer,
CI/CD pipeline definition, tooling) lives at the root.

`{domain}` must match the registered domain name in the enterprise data domain
registry (e.g., `investments`, `client-services`, `pricing`). This name is
also used as the Unity Catalog catalog prefix and the repository name prefix.
Teams must not invent domain names — use the registered name exactly.
Regardless of repo grain (domain, sub-domain, or product set), the directory
structure inside the repo uses the same `{domain}` value.

```
[domain-data-repo]/
├── data-products/
│   └── {domain}/
│       ├── dbt_project.yml           # One dbt project for the whole domain
│       ├── packages.yml              # dbt package dependencies
│       ├── dbt_profiles/
│       │   └── profiles.yml          # .gitignored — template only, not committed
│       ├── datasets/
│       │   ├── {product-name}/
│       │   │   ├── contract/         # Human-readable data contract (see below)
│       │   │   ├── dbt/
│       │   │   │   ├── raw/          # Source definitions (_sources.yml only)
│       │   │   │   ├── staging/      # Cleaned, typed, renamed columns
│       │   │   │   ├── intermediate/ # Business logic, joins, aggregations
│       │   │   │   └── curated/      # Published interface (facts & dims)
│       │   │   ├── airflow/          # DAG definition
│       │   │   ├── bundle/           # Databricks Asset Bundle (see below)
│       │   │   ├── spark/            # Optional -- only if PySpark needed
│       │   │   └── specs/            # Requirements & source-to-target mappings
│       │   └── {product-name-2}/
│       │       ├── contract/
│       │       ├── dbt/
│       │       ├── airflow/
│       │       ├── bundle/
│       │       └── specs/
│       ├── shared/                   # Domain-shared dbt assets
│       │   ├── macros/
│       │   ├── seeds/
│       │   ├── snapshots/
│       │   ├── analyses/
│       │   ├── tests/                # Singular (bespoke) SQL tests
│       │   └── sources/              # Cross-domain source definitions
│       ├── airflow/                  # Astronomer dags_folder
│       │   ├── dags_loader.py        # Discovers product DAGs for Airflow
│       │   ├── plugins/
│       │   └── tests/
│       │       └── test_dags.py
│       └── variables/                # Environment-specific variable files
│           ├── variables.yml
│           ├── variables_dev.yml
│           ├── variables_qa.yml
│           └── variables_prod.yml
├── .astro/
│   └── config.yaml
├── .devcontainer/
│   └── devcontainer.json
├── .github/
│   └── copilot-instructions.md
├── .harness/
│   └── pipeline.yaml
└── mise.toml
```

The dbt project is scoped to the domain, not the product. The `dbt_project.yml`
sets `model-paths: ["datasets"]` so all product models are discovered under a
single project. This allows models to reference each other across products
within the domain and supports running the full domain with a single
`dbt run`. Domain-shared macros, seeds, and snapshots live in `shared/`
rather than being duplicated per product.

Products are self-contained below the dataset boundary: all the code needed
to understand, run, and test a product lives in one directory. A product can
be extracted to its own repository by moving its directory and promoting the
domain-level dbt project, variables, and shared assets alongside it.

Not every product needs every directory. The minimum viable product directory
contains only `dbt/` and optionally `contract/`:

```
{product-name}/
├── contract/              # Required for curated models with consumers
└── dbt/
    ├── raw/               # _sources.yml only
    ├── staging/           # stg_ models
    └── curated/           # Published interface
```

The following directories are optional and should only be created when needed:

| Directory | When to include |
|---|---|
| `dbt/intermediate/` | When business logic requires joins, aggregations, or multi-step transforms |
| `airflow/` | When using Airflow for orchestration (see Choosing Orchestrator) |
| `bundle/` | When using Databricks Workflows for orchestration |
| `spark/` | When PySpark code is needed alongside dbt models |
| `specs/` | When product-specific requirements or mapping documents exist |

Do not create empty directories as placeholders.

The intended development workflow is local-first: engineers develop and test
on their own machines, then move to Databricks compute when work is ready for a
pull request. The `.devcontainer/` and `mise.toml` entries support this by
providing a consistent local environment and pinned tool versions across the
team. The specifics of the local development setup will be defined in a planned
Local Development Environment RFD.

For 1:many repos that write to multiple domains, each domain gets its own
subdirectory under `data-products/`, preserving the domain boundary at the
directory level:

```
data-products/
├── domain-a/
│   ├── dbt_project.yml
│   ├── datasets/
│   │   ├── product-1/
│   │   └── product-2/
│   ├── shared/
│   └── variables/
└── domain-b/
    ├── dbt_project.yml
    ├── datasets/
    │   └── product-1/
    ├── shared/
    └── variables/
```

Each domain's dbt project, variables, and shared assets are fully independent.
Domain repositories consume shared dbt packages via `dbt deps` and reference
Harness pipeline templates for CI/CD.

For 1:many repos, each domain has its own independent dbt project. CI/CD
pipelines run each project separately — the Harness pipeline uses path-based
triggers to detect which domain(s) changed and runs only the affected
project(s). A `dbt run` in CI always targets a single domain; there is no
"run all domains" command. If a change touches shared infrastructure (e.g.,
`.harness/pipeline.yaml`), all domain projects are built and tested.

### Variable Loading

The `variables/` directory contains environment-specific dbt variable files.
dbt does not natively load variables from YAML files — the Harness pipeline
template and the local development wrapper script are responsible for merging
base + environment variables and passing the result to dbt.

The merge strategy is **shallow key-level replace**: `variables.yml` provides
defaults; `variables_{env}.yml` overrides any key present in both. The merge
is performed by a Python helper script (provided in the Harness pipeline
template and the local `mise` task) that produces a safe JSON string for
`--vars`. Raw shell expansion (`$(cat ...)`) must not be used — it is
vulnerable to injection via special characters in YAML values and the
`ENVIRONMENT` variable itself.

```bash
# Harness pipeline template (simplified — actual implementation in template)
MERGED_VARS=$(python3 merge_vars.py variables/variables.yml variables/variables_${ENVIRONMENT}.yml)
dbt run --vars "${MERGED_VARS}"

# Local development wrapper (provided by mise task)
mise run dbt -- run   # merges variables.yml + variables_dev.yml by default
```

The `ENVIRONMENT` variable is validated against an allowlist (`dev`, `qa`,
`prod`) before use. The `merge_vars.py` script is provided by `caspian-core`
and handles escaping, multi-line values, and special characters safely.

The `variables.yml` (no environment suffix) contains defaults shared across
all environments. Variable files must not contain secrets — all credentials
must be referenced via Databricks secret scopes or `env_var()` in dbt Jinja
(see Secret Management below). The `caspian-core` package documents the
required variable names (e.g., catalog names for cross-domain references) so
domain teams know what to populate.

### Ownership Model

Repositories are owned by the **team that delivers them**. That team has
write access, owns the deployment pipeline, runs on-call, and approves PRs.
The grain of the repo determines the grain of ownership:

- A domain-level repo is owned by the domain team.
- A sub-domain repo is owned by the sub-domain team.
- A product-set repo is owned by the team that builds those products.

| Role | Access |
|------|--------|
| Owning team | Write |
| Platform team | Read + Review |
| Other teams | Read |

Ownership is enforced technically, not just by convention:

- Every repo must have a `CODEOWNERS` file mapping `*` to the owning
  team's GitHub team (e.g., `* @org/investments-positions`).
- Branch protection on `main` requires CODEOWNERS approval for all merges.

For multi-domain repos, the owning team is responsible for all domains the
repo writes to. If ownership becomes ambiguous, that is a signal to split.

### dbt Project Configuration

The `dbt_project.yml` at the domain level sets `model-paths: ["datasets"]` so
dbt discovers all product models under a single project. The domain-level
config sets the target catalog and default materialization; layer-specific
schema routing is set per-model in each product's `schema.yml` files.

Directory-based config keys in `dbt_project.yml` (e.g., `raw:`, `staging:`)
only match models whose path is directly under `datasets/raw/`. Because
product models live at `datasets/{product}/dbt/raw/`, those keys do not
apply at the expected depth. Per-model config in `schema.yml` is the reliable
mechanism for this structure.

```yaml
# data-products/{domain}/dbt_project.yml
name: '{domain}'
profile: '{domain}'
require-dbt-version: [">=1.8.0", "<2.0.0"]   # pinned to match caspian-core

model-paths: ["datasets"]
analysis-paths: ["shared/analyses"]
test-paths: ["shared/tests"]
seed-paths: ["shared/seeds"]
macro-paths: ["shared/macros"]
snapshot-paths: ["shared/snapshots"]

models:
  {domain}:
    +database: "{{ target.database }}"
```

The `require-dbt-version` range must be compatible with the version declared
by `caspian-core`. The `mise.toml` at the repo root pins the same dbt version
for local development. Domains must stay within one minor version of the
`caspian-core`-declared minimum to receive platform team support.

Because `model-paths` points at `datasets/`, dbt will walk the entire product
directory tree looking for `.sql` files — including `contract/`, `airflow/`,
`bundle/`, `spark/`, and `specs/`. To prevent dbt from attempting to compile
non-model SQL files (Spark SQL scripts, Airflow SQL templates, spec examples),
the `dbt_project.yml` excludes non-dbt directories explicitly:

```yaml
# Exclude non-dbt directories from model discovery
model-paths: ["datasets"]
# ... other paths ...

# Prevent dbt from scanning non-model directories
clean-targets: ["target", "dbt_packages"]
```

Non-dbt directories (`contract/`, `airflow/`, `bundle/`, `spark/`, `specs/`)
must not contain `.sql` files at their root level. If a product requires SQL
files in these directories (e.g., Spark SQL scripts), they should use a
different extension (`.sparksql`, `.sql.j2`) or be nested in a subdirectory
that dbt ignores. The `caspian-core` package includes a CI check that fails
if `.sql` files are found outside of `dbt/` directories under `datasets/`.

Per-product schema routing is defined in each product's `schema.yml`:

```yaml
# datasets/{product}/dbt/schema.yml
version: 2

models:
  - name: stg_investments_positions
    config:
      schema: staging
      materialized: view

  - name: fct_investments_daily_positions
    config:
      schema: curated
      materialized: table
      contract:
        enforced: true
      access: public
```

dbt projects map directly to the Unity Catalog namespace:

| dbt Concept | Unity Catalog | Example |
|---|---|---|
| `target.database` | Catalog | `investments_dev`, `investments_prod` |
| `schema` config | Schema | `raw`, `staging`, `intermediate`, `curated` |
| Model | Table or View | `fct_investments_daily_positions` |

The `profiles.yml` is `.gitignore`d and not committed. The `dbt_profiles/`
directory contains a `.gitkeep` and optionally a `profiles.yml.example` showing
the expected structure. Actual profiles are managed locally by developers
(populated from the devcontainer setup or manually) and injected by Harness
during CI/CD execution via environment variables and `DBT_PROFILES_DIR`.

### Layers

Each product's `dbt/` directory follows a four-layer model:

| Layer | Schema | Materialization | Access | Purpose |
|---|---|---|---|---|
| raw | `raw` | — | Domain only | Source definitions only; no SQL models |
| staging | `staging` | view | Domain only | Clean, type-cast, and rename columns |
| intermediate | `intermediate` | ephemeral | Domain only | Business logic, joins, aggregations |
| curated | `curated` | table | Domain + Cross-domain | Published facts and dimensions |

**Raw** contains only `_sources.yml` definitions pointing at ingested data. No
SQL model files exist at this layer. Source definitions provide schema
documentation, freshness checks, and a single place to update if the underlying
table location changes.

**Staging** models clean, type-cast, and rename columns from raw sources. Each
staging model maps to exactly one source. The `stg_` prefix is the only prefix
used at this layer.

**Intermediate** models contain business logic: joins, aggregations, case
statements, window functions. They default to ephemeral materialization and
compile into CTEs within downstream models. Teams may override to `view` or
`table` when a model is referenced by many downstream nodes and repeated CTE
compilation is a performance problem.

**Curated** models are the product's published interface and the only models
accessible to other domains. Every curated model must have an enforced contract
(see Schema Stability below).

### Databricks Asset Bundles

Each product's `bundle/` directory contains a
[Databricks Asset Bundle](https://docs.databricks.com/en/dev-tools/bundles/index.html)
configuration (`databricks.yml`) that defines the Databricks Workflow job for
that product. The bundle is the deployment unit — it declares the job cluster
configuration, task sequence (typically: `dbt deps` → `dbt run` → `dbt test`),
schedule, alerts, and permissions.

Bundles are deployed by the Harness pipeline and are the bridge between the
dbt project (which defines *what* to run) and Databricks (which defines *where*
and *when* to run it). A product that uses only the domain-level Airflow
orchestration (see `airflow/`) may leave `bundle/` empty or omit it. Products
that use Databricks Workflows as their orchestrator define their job here.

The `bundle/` directory is not scanned by dbt (see Model Path Exclusion above).

**Choosing between Airflow and Databricks Workflows:**

| Use Case | Recommended Orchestrator |
|---|---|
| Single-product dbt job (build → test → notify) | Databricks Workflows via `bundle/` |
| Multi-product orchestration within a domain | Airflow (domain-level `airflow/`) |
| Cross-system tasks (non-dbt, API calls, file transfers) | Airflow |
| Event-driven or streaming triggers | Databricks Workflows |

Products that use Airflow may leave `bundle/` empty or omit it. Products that
use Databricks Workflows may omit the product-level `airflow/` directory. The
domain-level `airflow/` directory and `dags_loader.py` must exist if any
product in the domain uses Airflow.

### Testing

Each product's `dbt/` directory contains tests at multiple levels:

- **Generic tests** (defined in `schema.yml`) — `not_null`, `unique`,
  `accepted_values`, `relationships`, plus custom generic tests from
  `caspian-core`. These are the primary testing mechanism and run as part
  of every `dbt test` invocation.

- **Singular tests** (`shared/tests/`) — bespoke SQL queries that assert
  domain-specific business rules spanning multiple models. These return rows
  that violate the assertion; an empty result set means the test passes.

- **Unit tests** (dbt 1.8+, defined in `schema.yml`) — test individual model
  logic with mocked inputs. Recommended for models with complex
  transformation logic (intermediate and curated layers). Not required for
  staging models that perform only renaming and type casting.

Tests run in two contexts:
1. **CI (pull request):** `dbt build` in the PR isolation schema runs all
   models and tests. Generic and unit tests must pass for the PR to merge.
2. **Production:** `dbt test` runs after `dbt run` in the scheduled job.
   Failures trigger alerts per the DataOps handoff configuration.

Test coverage expectations: every curated model must have at least `not_null`
and `unique` tests on its primary key columns. Products with enforced data
contracts (all curated models) get column-type validation automatically.

### Platform Package: caspian-core

`caspian-core` is a dbt package maintained by the platform team and consumed
by all domain projects:

```yaml
# packages.yml
packages:
  - git: "https://github.com/<org>/caspian-core.git"  # canonical URL in platform repo template
    revision: v1.2.0
  - package: dbt-labs/dbt_utils
    version: 1.1.1
```

The package provides shared macros, generic tests, and the schema routing
logic that all domains depend on:

- **Schema routing macros** — override dbt's default schema and database
  naming behavior so models land in the correct Unity Catalog namespace.
  Without these macros, dbt's default behavior produces schema names like
  `default_curated` instead of `curated`. The macro implementations and
  their configuration are maintained in the `caspian-core` repository.

- **Generic tests** — shared data quality tests (`valid_date_range`,
  `non_negative`, `referential_integrity`) available to all domain projects.

Domain projects pin to a specific version and upgrade on their own schedule.
The platform team follows semantic versioning and maintains backward
compatibility within a major version. A change to a schema routing macro
that alters catalog or schema placement is a major version bump. Domains
must stay within one major version of the latest release; versions older
than 12 months are unsupported by the platform team.

**Supply chain controls for `caspian-core`:**

- Merges to `main` require two approvals from platform team members.
- Releases are published only from signed Git tags.
- Domain repos should pin to both a version tag and a commit SHA:
  ```yaml
  - git: "https://github.com/<org>/caspian-core.git"
    revision: v1.2.0  # also verify: commit SHA abc1234
  ```
- The Harness pipeline template caches `dbt deps` output to avoid
  re-cloning on every CI run and to provide resilience against Git host
  outages.
- A pre-commit hook runs `gitleaks` to prevent accidental secret commits.

### Cross-Domain References

Cross-domain data access is limited to the curated layer. Domains reference
another domain's curated tables using `source()`, not `ref()`. dbt Core does
not support lightweight cross-project `ref()` — the `dependencies.yml`
`projects:` mechanism is exclusive to dbt Cloud Enterprise. Installing an
upstream domain as a package pulls all its source code into the downstream
project and adds every model to the DAG, which is fragile and defeats the
purpose of independent domain projects.

Cross-domain sources are a domain-level concern, not a product-level one:
they are defined in `shared/sources/_cross_domain__sources.yml` so they are
not conflated with a product's own ingestion sources in `dbt/raw/`. dbt
discovers source definitions anywhere under `model-paths`, so placing the
file under `shared/` is sufficient — no additional configuration is needed:

```yaml
# shared/sources/_cross_domain__sources.yml
version: 2

sources:
  - name: client_services_curated
    # Owner: client-services domain
    database: "{{ var('client_services_catalog', 'client_services_' ~ target.name) }}"
    schema: curated
    tables:
      - name: dim_clients
        loaded_at_field: _dbt_loaded_ts
        freshness:
          warn_after: { count: 24, period: hour }
          error_after: { count: 48, period: hour }
```

Every cross-domain source entry must include a `# Owner: {domain} domain`
comment identifying the owning domain. This makes cross-domain dependencies
visible at a glance when scanning the YAML file.

The `client_services_catalog` variable is defined in the domain's
`variables/variables_{env}.yml` or passed as a CLI argument during CI/CD,
and defaults to `client_services_{target.name}` if not set. Unity Catalog
grants control actual access to the curated schema. The source definition
provides freshness checks and documents the cross-domain dependency. dbt does
not track this dependency in its DAG — lineage terminates at the source
definition. This is primarily a documentation and lineage gap; the reliability
risk (upstream schema drift undetected at compile time) is mitigated by
enforced contracts on curated models and freshness checks on cross-domain
sources, though not fully eliminated (see Risks). If dbt Core
gains native lightweight cross-project references in the future, the migration
path is to replace `source()` calls with two-argument `ref()` calls.

### Schema Stability

Every curated model must have `contract: {enforced: true}` and `access: public`
configured. Enforced contracts and the `access` property require dbt 1.5 or
later.

```yaml
# curated/_curated__models.yml
version: 2

models:
  - name: fct_investments_daily_positions
    config:
      contract:
        enforced: true
      access: public
    columns:
      - name: position_id
        data_type: string
        tests: [not_null, unique]
      - name: client_id
        data_type: string
        tests: [not_null]
```

When dbt builds a model with an enforced contract, it generates DDL with
explicit column definitions. If the SQL output does not match the contract,
Delta Lake rejects the DDL and the build fails. A developer who removes or
renames a column must update the contract YAML to match, making the breaking
change visible in the pull request diff and subject to review.

Contracts make breaking changes deliberate and reviewable, not impossible.
They achieve the same goal as semantic versioning with less process overhead:
enforcement is automatic at build time, with nothing to track, bump, or
coordinate.

### Data Contracts: `contract/` Directory vs. dbt Contracts

Each product has a `contract/` directory and dbt `contract: {enforced: true}`
in its curated model YAML. These serve different purposes:

- **`contract/` directory** — contains the human-readable data contract
  document (as defined in [RFD 0002](../0002/README.md)): SLAs, quality
  thresholds, consumer expectations, ownership, versioning policy, and
  support contacts. This is the artifact that consumers and data owners
  review and approve. It may be a Markdown file, a YAML file, or both.

- **dbt `contract: {enforced: true}`** — the machine-enforceable subset:
  column names, data types, and not-null constraints. dbt enforces this at
  build time against the SQL output. It is the technical implementation of
  the schema portion of the broader data contract.

The `contract/` document is the source of truth for what the product promises.
The dbt contract YAML is the enforcement mechanism for the schema portion of
that promise. When the data contract changes, the dbt contract YAML must be
updated to match. The code review process (PR diff) is the mechanism that
keeps them in sync — both files live in the same product directory and are
changed in the same PR.

### PR Isolation Schemas

CI pipelines create an isolated schema per pull request to allow dbt models
to be built and tested without affecting the shared development catalog:

```
pr_{number}_{username}
```

These schemas are scoped to the domain's dev catalog only. Each PR schema
is granted access only to the service principal running that PR's CI job —
other developers cannot read or write another PR's isolation schema. Schemas
are destroyed when the pull request is merged or closed.

A scheduled Databricks workflow (owned by the platform team, running daily
at 02:00 UTC) cleans up orphaned PR schemas:

1. Queries `information_schema.schemata` for schemas matching `pr_*`.
2. Compares against the GitHub API to identify closed or stale PRs.
3. Drops schemas where the corresponding PR has been closed for > 24 hours
   or has had no activity for > 7 days.
4. On GitHub API failure: retries 3× with exponential backoff; if still
   unreachable, skips the run and alerts the platform team.
5. On partial failure (some schemas dropped, others fail): logs and
   continues; alerts if orphaned schema count exceeds 50.
6. A manual cleanup command (`mise run cleanup-pr-schemas`) is available
   for ad-hoc use.

### Specs

Each data product includes a `specs/` directory co-located within the product
boundary at `data-products/{domain}/datasets/{product-name}/specs/`. A spec combines what would
traditionally be a product requirements document (PRD) with the technical
mapping detail that engineers need to implement it, kept together so they stay
in sync and travel with the product if it is moved to a different repository.

Specs follow a flat numbering convention: `NNN-{feature-name}.md`, where `NNN`
is a zero-padded sequence number and `{feature-name}` is a descriptive slug
(e.g., `001-trade-settlement-ingest.md`). If a spec requires supporting files
-- diagrams, sample data, mapping spreadsheets -- it is promoted to a directory
with a `README.md`: `specs/NNN-{feature-name}/README.md`.

Each spec carries minimal front matter:

```yaml
---
author: jdoe
status: draft        # draft | accepted | implemented
domain: settlements
---
```

Acceptance criteria live inside the spec itself, not in a separate tracking
system. There is no branch-per-spec workflow; specs are proposed and reviewed
through normal feature branches and PRs.

Specs are product-local.
Platform-wide decisions are captured as RFDs in catalyst; product-specific
requirements and design context live alongside the product code they describe.

### Agent Instructions

Each domain repository includes context files for AI coding agents. These are
distillations of the relevant platform-wide RFDs — naming conventions, model
layering, testing expectations, branching rules — into the specific guidance
an agent needs to generate correct code for that domain.

The following agent context files are supported:

| File | Agent | Purpose |
|---|---|---|
| `.github/copilot-instructions.md` | GitHub Copilot | Repository-level coding instructions |
| `CLAUDE.md` (repo root) | Claude Code | Project-level instructions, conventions, slash commands |
| `.cursor/rules` | Cursor | Repository-level rules and context |

The platform team maintains reference versions of these files in the
`catalyst-domain-template` repository. Domain teams may extend them with
domain-specific context (e.g., naming conventions for their catalogs, common
data sources, team-specific review expectations) but must not remove
platform-level guidance. The Harness CI pipeline includes a check that
verifies platform-required sections are present in agent instruction files
(comparing against a checksum of required sections from the template). This
prevents accidental or intentional removal of security-relevant instructions.

When a platform-wide RFD changes conventions, the platform team updates the
reference files and domain teams pull the changes on their own schedule.

## Repository Naming Convention

Repository names **must start with the registered domain name** so they are
discoverable and groupable. The suffix indicates the scope:

| Grain | Pattern | Example |
|---|---|---|
| Domain | `{domain}-data` | `investments-data` |
| Sub-domain | `{domain}-{subdomain}-data` | `investments-positions-data` |
| Product set | `{domain}-{scope}-data` | `pricing-valuation-data` |

Shared packages use the pattern `caspian-{package}` (e.g., `caspian-core`,
`caspian-dq`).

The domain prefix is enforced by the GitHub organization's repository creation
policy. Teams must not create repos that omit the domain prefix -- it is how
tooling, CI, and catalog integrations discover which domain a repo belongs to.

## Onboarding and Migration

### New teams

1. Decide the repo grain: domain, sub-domain, or product set. Start with
   the broadest grain that lets the team deliver independently — you can
   always split later.
2. Create a new repo from the
   [`catalyst-domain-template`](https://github.com/RBLW_capgroup/catalyst-domain-template)
   GitHub template. This provides the full directory structure, CODEOWNERS,
   Harness pipeline, devcontainer, mise config, gitleaks hooks, and agent
   instruction files.
3. Name the repo per the naming convention: `{domain}-data`,
   `{domain}-{subdomain}-data`, or `{domain}-{scope}-data`.
4. Rename `data-products/{template-domain}/` to the domain name.
5. Update `dbt_project.yml` with the domain name and catalog.
6. Add the first product under `datasets/`.
7. Run `dbt deps` to pull `caspian-core` and verify the schema routing
   macros work against the dev catalog.

### Migrating an existing repository

1. Create the target directory structure per this RFD.
2. Move existing dbt models into `datasets/{product}/dbt/{layer}/`.
3. Move existing source definitions into `dbt/raw/`.
4. Add `caspian-core` to `packages.yml` and remove duplicated macros
   that are now provided by the package.
5. Add `contract: {enforced: true}` to curated models (this may require
   adding column definitions — plan for this effort).
6. Set up the Harness pipeline from the template.
7. Verify in a PR isolation schema before merging to main.

The platform team provides hands-on onboarding support during the adoption
pilot (April 2026). After the pilot, onboarding is self-service via the
template repo with platform team office hours for questions.

## Alternatives Considered

### Monorepo (All Domains in One Repo)

A single repository containing all domain code. Consistency is enforced
by default, dependency management is simplified, and cross-domain changes can
happen in a single PR. However, merge conflicts increase as teams grow, CI/CD
must be scoped to avoid running everything on every change, access control is
coarse-grained, and a single team's broken build can block everyone else.

### Unstructured Polyrepo (No Shared Conventions)

Each team creates repos with no shared structure, naming, or tooling.
Access control is clean and teams deploy independently. The tradeoff is
shared components (macros, tests, CI/CD templates) end up duplicated
across repositories and standards drift without a central enforcement
point. This proposal allows flexible repo grain but requires the shared
conventions (directory structure, caspian-core, naming prefix, CI template)
that an unstructured polyrepo does not.

### Single dbt Project (All Domains)

Placing all domain models in a single dbt project produces complete lineage and
simplifies dependency management. At scale this becomes untenable: merge
conflicts increase, ownership boundaries blur, deployments are all-or-nothing,
and parse times grow with the number of models across all teams.

### Fully Independent dbt Projects (No Shared Package)

Maximum domain autonomy with no shared package. Teams choose their own macros
and schema routing logic. This leads to duplicated utility code, inconsistent
schema routing (each team writes their own `generate_schema_name`), and
divergent testing patterns. Without a shared package, platform-wide changes
must be made independently in every domain project.

### dbt Mesh via dbt Cloud Enterprise

dbt Cloud Enterprise provides a metadata service that resolves cross-project
`ref()` calls, eliminates the lineage gap, and provides compile-time validation
of cross-project dependencies. It is architecturally superior for cross-domain
references. However, it requires a dbt Cloud Enterprise subscription. Adopting
dbt Cloud solely for cross-project references would introduce a significant
platform dependency for a problem adequately mitigated by `source()` definitions
with enforced contracts.

## Impact

- **Economic**: The domain-per-repo model front-loads investment in shared
  packages and templates, but reduces ongoing cost by eliminating duplication
  across teams. New domain teams can be onboarded using the
  `catalyst-domain-template`. The `caspian-core` package centralizes shared
  logic, reducing duplication without creating deployment coupling.
- **Customer/User**: Domain teams retain autonomy over their assets and can
  deploy independently without blocking on other teams.
- **Performance**: Ephemeral intermediate models avoid materializing objects
  that exist only as intermediate computation steps. Each domain's dbt parse
  and compile operates only on its own models plus the lightweight
  `caspian-core` package, keeping build times proportional to domain size.
  CI/CD pipelines are scoped per repository.
- **Security**: Unity Catalog grants are the sole mechanism for cross-domain
  access. A domain team cannot read another domain's staging or intermediate
  data even if they know the table names. PR isolation schemas ensure
  in-progress work cannot leak into shared environments.

## Risks and Open Questions

- **caspian-core as a bottleneck.** If the platform team is slow to release
  package updates, domain teams are blocked on fixes or new capabilities. The
  mitigation is that domains pin their own version and upgrade independently,
  but this only works if the platform team maintains backward compatibility
  within major versions.
- **Cross-domain lineage gap.** The `source()` pattern means dbt docs do not
  show full data lineage across domains. Teams must rely on Unity Catalog's
  own lineage tracking or external tools for a platform-wide view.
  Additionally, `source()` definitions do not fail at compile time when an
  upstream schema changes — a renamed or removed column is only detected at
  runtime. Freshness checks on cross-domain sources mitigate staleness but
  do not catch schema drift. The platform team will ship a **cross-domain
  contract validation job** as part of the initial rollout of this strategy.
  The job runs nightly, compares each domain's `_cross_domain__sources.yml`
  column definitions against the actual upstream schema in Unity Catalog,
  and posts drift alerts to the affected domain's channel. This provides
  runtime schema drift detection as an interim measure until dbt Core
  supports lightweight cross-project references.
- **Cross-domain change notification.** There is no mechanism to notify
  downstream domains when an upstream data contract is about to change.
  Enforced contracts prevent silent breakage within a domain, but a domain
  that changes its curated schema has no way to discover or alert affected
  downstream consumers. Unity Catalog lineage tracking can identify
  dependencies, but there is no automated notification workflow. This should
  be addressed in a follow-on RFD.
- **Contract adoption.** Existing curated models that lack contracts must be
  retroactively fitted with column definitions and data types. For domains with
  many curated models this is a non-trivial migration effort.
- **Schema routing correctness.** The schema routing macros in `caspian-core`
  are a single point of failure — a defective release affects every domain's
  catalog placement. The platform team's integration tests against a reference
  domain project mitigate this risk.
- **Cross-repository changes** (e.g., updating a shared dbt package) require
  coordination across teams. Package versioning discipline is essential.
- **Many:many mapping pattern** is the hardest to reason about for CI/CD,
  ownership, and access control. The general criterion — "if ownership becomes
  ambiguous, split the repo" — applies, but specific guidance on acceptable
  vs. restructure-required scenarios is an open question.
- **Many:1 deployment coordination.** Repos that must deploy consistently (e.g.,
  a dbt repo and a PySpark repo both writing to the same catalog) need a defined
  coordination process. This is not addressed by the current CI/CD strategy and
  should be an explicit topic in the CI/CD pipeline standards RFD.
- **Secret management.** A comprehensive secret management strategy spanning
  Databricks, Harness, and AWS is deferred to the Security & Secrets RFD.
  Until that RFD is published, the following interim rules apply:
  - **No credentials in `variables/*.yml` or any committed file.** Variable
    files are committed to Git and must contain only non-sensitive values
    (catalog names, schema names, feature flags).
  - **dbt models** must reference secrets via `{{ env_var('SECRET_NAME') }}`
    in Jinja, never as hardcoded values or dbt vars.
  - **CI/CD pipelines** must reference secrets via Harness secret manager
    and mask all secret-containing environment variables in logs.
  - **Every domain repo** must include `gitleaks` as a pre-commit hook and
    as a CI gate in the Harness pipeline. The platform repo template
    includes both by default.

## References

- [RFD 0001: Requests for Discussion](../0001/README.md)
- [RFD 0004: Branching Strategy](../0004/README.md) — branch naming conventions and PR workflow for domain repos
- [RFD 0002: Data Product Lifecycle](../0002/README.md) — lifecycle phases that spec status values (`draft`, `accepted`, `implemented`) map to
- RFD NNNN: Orchestration Patterns *(planned)* — Airflow deployment model and dbt execution within Astronomer
- RFD NNNN: Local Development Environment *(planned)* — mise, dev containers, and local dbt/Airflow setup
- [catalyst-domain-template](https://github.com/RBLW_capgroup/catalyst-domain-template) — reference implementation of the domain repository structure defined in this RFD
- [dbt model contracts](https://docs.getdbt.com/docs/mesh/govern/model-contracts)
- [dbt model access](https://docs.getdbt.com/docs/mesh/govern/model-access)
- [Unity Catalog documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
