<div align="center">

<img src="assets/landing-page.svg" alt="AI Catalyst DPLC Skills">

</div>

---

## Getting Started

| | |
|---|---|
| **New to the lifecycle?** | Start with the **concierge** — it interviews you about your situation and routes you to the right phase. New or unsure users get a guided walk-in with an environment check before any handoff. |
| **Not sure you're set up?** | Run **dplc-preflight** — it detects which Databricks workspace you're pointed at (and which others you have), whether you actually have access, and where your product would go. The concierge routes new users here automatically. |
| **Machine not set up yet?** | Run **setup-workspace** to check and install the toolchain (Python, dependencies via cgrepo). `dplc-preflight` routes here when the local toolchain is the blocker. |
| **Know your stage?** | Jump to a group orchestrator: `dplc-design-stage`, `dplc-build-stage`, or `dplc-ship-stage` |
| **Know your phase?** | Jump to a phase orchestrator: `dplc-prereq`, `dplc-triage`, `dplc-discovery`, `dplc-design` |
| **Need one artifact?** | Use a document skill directly — each generates a single lifecycle artifact from its template. |
| **Need one action?** | Use a capability skill directly — e.g., `profile-columns`, `query-table`, `write-dbt-model` |
| **Want to see how they connect?** | Open the [skills graph](../docs/skills-graph/README.md) — every skill in a lifecycle-phase column, wired by its declared dependencies. |

---

## Skill Architecture

Skills are organized in four tiers. Higher tiers compose lower tiers:

```
┌─────────────────────────────────────────────────────┐
│  Orchestrators                                      │
│  Lifecycle stage/phase coordination                 │
│  dplc-concierge → dplc-design-stage → dplc-prereq  │
├─────────────────────────────────────────────────────┤
│  Workflow Skills                                    │
│  Multi-step compound workflows                      │
│  source-aligned, domain-aligned, consumer-aligned   │
├─────────────────────────────────────────────────────┤
│  Document Skills                                    │
│  Single-artifact generation from templates          │
│  data-contract, runbook, feasibility-report, ...    │
├─────────────────────────────────────────────────────┤
│  Capability Skills                                  │
│  Single-responsibility composable actions           │
│  connect-databricks, query-table, profile-columns   │
├─────────────────────────────────────────────────────┤
│  Core Functions + Platform Clients                  │
│  Python libraries (deterministic, no LLM judgment)  │
│  core/profile.py, clients/databricks.py             │
└─────────────────────────────────────────────────────┘
```

All skills live in a flat `skills/{skill-name}/` directory. The tier
(orchestrator, workflow, document, capability) is declared in each skill's
`metadata.tier` field, not in the directory structure.

Each skill is a folder containing `SKILL.md` (required) plus optional
`templates/`, `references/`, and `scripts/` directories.

---

## The Lifecycle

### DESIGN (Phases 0 – 3)

*What are we building and why?*

**Orchestrator:** `dplc-design-stage` (or per-phase: `dplc-prereq`, `dplc-triage`, `dplc-discovery`, `dplc-design`)

**Phase orchestrators:** `dplc-prereq`, `dplc-triage`, `dplc-discovery`, `dplc-design`

**Workflow skills:** `discover-data`, `data-profiling`, `marketplace-search`, `data-modeling`, `column-lineage`, `load-confluence-context`

| Phase | Document Skills | Capability Skills Used |
|-------|----------------|----------------------|
| **0 Prereq** | `phase-zero-checklist` | — |
| **1 Triage** | `demand-tracker-entry`, `consumer-use-case-map` | `marketplace-search` |
| **2 Discovery** | `feasibility-report`, `requirements-acceptance-criteria`, `outcome-kpi-statement`, `effort-estimate`, `business-case`, `privacy-impact-assessment`, `poc-spike-findings`, `product-requirements-document` | `query-catalog`, `profile-columns`, `fetch-confluence` |
| **3 Design** | `data-quality-controls-plan`, `data-contract`, `data-model`, `transformation-spec`, `architecture-diagram`, `dataops-handoff-draft`, `nfr-specification`, `integration-blueprint`, `schedule-backfill-plan`, `security-design` | `parse-lineage`, `data-modeling` |

### BUILD (Phases 4 – 6)

*Build it and prove it works.*

**Orchestrator:** `dplc-build-stage` (or per-phase: `dplc-build` for Phase 4, `dplc-validate` for Phase 5, `dplc-publish` for Phase 6)

**Workflow skills:** `source-aligned`, `domain-aligned`, `consumer-aligned`, `setup-dbt-project`, `setup-databricks-asset-bundle`, `setup-monitoring-and-logging`, `write-dbt-wrapper`, `build-preflight`

| Phase | Document Skills | Capability Skills Used |
|-------|----------------|----------------------|
| **4 Build** | `build-checklist`, `unit-test-report`, `integration-test-report`, `code-review-sign-off` | `write-dbt-model`, `write-dbt-source`, `generate-dag`, `validate-dag`, `connect-databricks`, `query-table`, `run-dbt-on-databricks`, `troubleshoot-dbt-on-databricks`, `adding-dbt-unit-test`, `dbt-unit-test`, `configure-sql-warehouse`, `scaffold-repo-structure`, `dbt-best-practices`, `fetching-dbt-docs`, `working-with-dbt-mesh` |
| **5 Validate** | `data-quality-sign-off`, `uat-sign-off` | `profile-columns`, `query-table` |
| **6 Publish** | `deployment-record`, `consumer-onboarding-guide`, `release-notes` | — |


### SHIP (Phases 7 – 8)

*Get it live and keep it healthy.*

**Orchestrator:** `dplc-ship-stage`

| Phase | Document Skills | Capability Skills Used |
|-------|----------------|----------------------|
| **7 Operate** | `runbook`, `incident-log`, `sla-dashboard-spec`, `warranty-handoff-sign-off` | `query-table`, `profile-columns` |
| **8 Evolve** | `usage-analytics-report`, `downstream-impact-assessment`, `deprecation-notice` | `parse-lineage` |

---

## Capability Skills (23)

Single-responsibility, composable actions and platform-reference skills. Each works standalone or as part of a workflow.

### Data-product actions

| Skill | What it does |
|-------|-------------|
| `connect-databricks` | Authenticate and validate a Databricks session |
| `query-table` | Run SQL against a Databricks workspace |
| `profile-columns` | Compute column-level statistics for a table |
| `query-catalog` | Discover catalogs, schemas, and tables in Unity Catalog |
| `parse-lineage` | Trace column-level lineage from SQL |
| `fetch-confluence` | Fetch and parse Confluence pages as Markdown |
| `configure-sql-warehouse` | Provision and wire a serverless SQL warehouse for dbt |
| `generate-dag` | Generate an Airflow DAG entry for a pipeline |
| `validate-dag` | Audit an existing Airflow DAG against RFD 0011 and emit a compliance report (read-only) |
| `run-dbt-on-databricks` | Execute dbt phases against Databricks via the wrapper |
| `troubleshoot-dbt-on-databricks` | Diagnose dbt-on-Databricks job failures |
| `adding-dbt-unit-test` | Author a dbt unit test for an existing model |
| `dbt-unit-test` | Analyse a dbt model's SQL, generate synthetic test cases, execute via pandas/PySpark, and report |
| `dbt-best-practices` | Apply dbt-Labs conventions to model authoring decisions |
| `fetching-dbt-docs` | Pull dbt documentation snippets on demand |
| `working-with-dbt-mesh` | Patterns for cross-project dbt references and groups |
| `scaffold-repo-structure` | Lay down the Catalyst data-product repository layout |
| `astronomer-update-base-deployment` | Refresh a vended Astro/IAC deployment repo against the `template-copier-astro-infra-bundle` main branch (Airflow 2/3 auto-detect, overwrite/merge/preserve strategies) |

### Platform references — Databricks API surface

Loaded on demand by other skills that need the underlying Databricks behavior.

| Skill | What it documents |
|-------|------------------|
| `databricks-bundles` | Databricks Asset Bundles (DAB) schema and patterns |
| `databricks-config` | Workspace configuration, profiles, and `databricks.yml` shape |
| `databricks-dbsql` | Databricks SQL (DBSQL) endpoints, warehouses, and clients |
| `databricks-docs` | Index of authoritative Databricks doc references |
| `databricks-execution-compute` | Job clusters, serverless compute, and execution semantics |
| `databricks-jobs` | Jobs API, task types, retry/timeout, and run pages |
| `databricks-python-sdk` | `databricks-sdk` for Python — usage patterns |
| `databricks-unity-catalog` | Unity Catalog model, grants, volumes, and lineage |

---

## Skill Folder Structure

Every skill follows the same layout:

```
skill-name/
├── SKILL.md              # Required — instructions + frontmatter
├── templates/            # Optional — output templates (e.g., data-contract.md)
├── references/           # Optional — docs loaded on demand (progressive disclosure)
├── scripts/              # Optional — executable code (Python, Bash)
└── assets/               # Optional — icons, images, fonts
```

**Templates travel with the skill.** Each document skill has its template in
`templates/` — the template and the skill are versioned together.

**References are Level 3 content.** Claude loads them only when needed during
execution. Use for checklists, conventions, detailed specs.
