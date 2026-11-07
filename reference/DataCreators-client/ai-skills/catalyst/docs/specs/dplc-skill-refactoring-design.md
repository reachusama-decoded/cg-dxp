# DPLC Skill Refactoring Design

**Date:** 2026-04-22
**RFD:** 0006 (Skill Contribution Strategy)
**Goal:** Refactor skills from edo-ai-skills and AI Catalyst into a layered,
composable skill package that accelerates the Data Product Lifecycle.

## Approach

Phase orchestrators compose atomic skills (document + execution) in the right
order, feeding execution results into document generation so artifacts are
grounded in real data instead of prose estimates. A concierge routes new users
to the right phase.

## User Experience

```
"I'm working on a data product"
         │
    ┌────▼─────┐
    │ Concierge │──── "Are you defining, building, or shipping?"
    └────┬─────┘
         │
    ┌────┼──────────────────┐
    ▼    ▼                  ▼
 Define  Build              Ship
 Ph 0-3  Ph 4-5            Ph 6-8
```

Experienced users skip the concierge and invoke phase orchestrators directly.
Power users invoke atomic skills individually.

## Sequencing

Not everything ships at once. The stages have different readiness levels.

### Wave 1: Define (Phases 0-3)

Ship first. The execution skills here are discovery and profiling — the
code is solid (well-structured platform clients, clean function interfaces).
The document skills are already proven (98.3% eval pass rate). The main work
is composing them via phase orchestrators so artifacts get real data instead
of guesses.

**What ships:**
- `dplc-concierge` (routes to phases)
- `dplc-prereq` orchestrator
- `dplc-triage` orchestrator
- `dplc-discovery` orchestrator
- `dplc-design` orchestrator
- Graduated execution skills: discover-data, data-profiling, data-modeling,
  column-lineage, confluence-fetch, marketplace-search,
  data-product-classification
- Enhanced document skills: all Phase 0-3 document skills updated to accept
  execution context as input
- Platform clients: databricks_client, confluence_client
- Core functions: discover_tables, profile_table, fetch_confluence_page,
  trace_lineage, classify_data_product, search_marketplace

### Wave 2: Ship (Phases 6-8)

Ship second. These are mostly document skills plus impact-assessment and
column-lineage (already graduated in Wave 1). The code for impact assessment
needs targeted fixes (subprocess coupling to sibling skill directory) but
the core logic is sound.

**What ships:**
- `dplc-publish` orchestrator
- `dplc-operate` orchestrator
- `dplc-evolve` orchestrator
- Graduated execution skills: impact-assessment, foundation-review
- Enhanced document skills: all Phase 6-8 document skills updated
- Core functions: assess_downstream_impact (extracted from impact-assessment),
  run_foundation_review

### Wave 3: Build (Phases 4-5)

Ship last. This is where the pipeline scaffolding lives — source-aligned,
domain-aligned, deequ-rules, dag generation. The code quality is decent but
these skills need more hardening before we stand behind them for the
enterprise:

- source-aligned is 800+ lines and needs decomposition
- dbt model generation involves judgment calls (materialization, patterns)
  that make it a skill, not just a function
- DQ rule generation needs to produce executable output, not descriptions
- Pipeline scaffolding conventions need to align with our RFD standards,
  not carry over platform-specific assumptions

**What ships (after hardening):**
- `dplc-build` orchestrator
- `dplc-validate` orchestrator
- Graduated execution skills: source-aligned, domain-aligned, deequ-rules
- Jira integration: jira-create-epics-stories (deferred until Wave 2 or 3
  depending on demand)
- Platform clients: dbt_executor, jira_client
- Core functions: generate_ddl, create_epic, create_story, search_issues
- Skills (requiring LLM judgment): generate-dbt-model, scaffold-pipeline,
  generate-dq-rules, review-code

## Layering

Per RFD 0006:

```
                        ┌──────────────┐
          ┌────────────►│  Templates   │
          │  references │              │
          │             └──────────────┘
          │
┌─────────┴───────────────────────────────────┐
│              Skills (SKILL.md)               │
│  Prompt + orchestration + judgment           │◄──── can invoke
│                                              │      other skills
├─────────────────────────────────────────────┤
│         Skill Scripts (optional)             │
│  Deterministic workflows, no LLM judgment    │
├─────────────────────────────────────────────┤
│              Core Functions                   │
│  Reusable, deterministic, one thing well     │
├─────────────────────────────────────────────┤
│              Platform Clients                 │
│  API wrappers, no business logic             │
└─────────────────────────────────────────────┘
```

### What's a core function vs. what's a skill

If the LLM needs to make decisions, it's a skill. If it's a deterministic
operation that always does the same thing given the same input, it's a core
function.

| Operation | Judgment needed? | Layer |
|---|---|---|
| Connect to Databricks, run SQL | No | Platform client |
| Profile a table's columns and stats | No | Core function |
| Discover tables matching keywords | No | Core function |
| Fetch a Confluence page | No | Core function |
| Create a Jira epic | No | Core function |
| Trace column lineage through SQL | No | Core function |
| Generate a dbt model for an entity | Yes — materialization, patterns | Skill |
| Scaffold a full pipeline | Yes — which pattern, what to include | Skill |
| Assess downstream impact | Yes — severity, relevance | Skill |
| Generate DQ rules from a contract | Yes — which rules, what severity | Skill |
| Review code against conventions | Yes — judgment on violations | Skill |

## Skill Inventory

### Platform Clients

| Client | Source | Used By |
|---|---|---|
| `databricks_client` | edo: scripts/shared/databricks_client.py | discover_tables, profile_table, generate_ddl, run_foundation_review |
| `dbt_executor` | edo: scripts/shared/dbt_executor.py | generate-dbt-model, trace_lineage |
| `jira_client` | edo: scripts/jira_client.py | create_epic, create_story, search_issues |
| `confluence_client` | edo: confluence-fetch scripts | fetch_confluence_page |

Code quality: solid. DatabricksClient and JiraClient are proper classes with
typed signatures, retry logic, and explicit error handling. Salvageable as-is
with minor cleanup.

### Core Functions

| Function | Source | Used By (Skills) |
|---|---|---|
| `discover_tables()` | edo: discover-data | discover-data, dplc-discovery, dplc-triage |
| `profile_table()` | edo: data-profiling | data-profiling, dplc-discovery, dplc-build, dplc-validate |
| `fetch_confluence_page()` | edo: confluence-fetch | confluence-fetch, dplc-discovery |
| `trace_lineage()` | edo: column-lineage | column-lineage, impact-assessment, dplc-design, dplc-evolve |
| `search_marketplace()` | edo: marketplace-search | marketplace-search, dplc-triage |
| `classify_data_product()` | edo: data-product-classification | data-product-classification, dplc-triage |
| `create_epic()` | edo: jira-create-epics-stories | jira-create-epics-stories, dplc-discovery |
| `create_story()` | edo: jira-create-epics-stories | jira-create-epics-stories, dplc-discovery |
| `search_issues()` | edo: jira-create-epics-stories | jira-create-epics-stories, dplc-triage |
| `generate_ddl()` | edo: data-modeling | data-modeling, source-aligned, domain-aligned, dplc-build |

### Execution Skills (graduated from edo-ai-skills)

| Skill | Source | Phase | Wave | Notes |
|---|---|---|---|---|
| discover-data | edo: data-platform | 2 | 1 | Extract discover_tables as core function |
| data-profiling | edo: data-platform | 2 | 1 | Extract profile_table as core function |
| data-modeling | edo: data-platform | 3 | 1 | Judgment on model design, stays a skill |
| column-lineage | edo: data-platform | 3, 8 | 1 | Extract trace_lineage; fix end_to_end path coupling |
| confluence-fetch | edo: integrations | cross-phase | 1 | Extract fetch_confluence_page |
| marketplace-search | edo: integrations | 1 | 1 | Extract search_marketplace |
| data-product-classification | edo: data-platform | 1 | 1 | Extract classify_data_product |
| impact-assessment | edo: data-platform | 8 | 2 | Fix subprocess coupling to column-lineage |
| foundation-review | edo: data-platform | 5 | 2 | Automated code review checks |
| source-aligned | edo: data-platform | 4 | 3 | 800-line monolith, needs decomposition |
| domain-aligned | edo: data-platform | 4 | 3 | Similar decomposition as source-aligned |
| deequ-rules | edo: data-platform | 4 | 3 | Needs to produce executable output |
| jira-create-epics-stories | edo: integrations | 2 | 2-3 | Extract Jira core functions |
| entity-scaffold | edo: data-platform | 4 | 3 | Overlaps with source/domain-aligned |
| generate-dbt-model | new (from source-aligned decomp) | 4 | 3 | Skill, not function — requires judgment |

### Document Skills (existing AI Catalyst, enhanced)

All 35 existing RFD 0002 document skills stay as atomic skills. Enhanced in
each wave to accept execution context as input so they produce artifacts
grounded in real data.

### Orchestrators and Concierge (new)

| Skill | Stage | Wave | Composes |
|---|---|---|---|
| `dplc-concierge` | — | 1 | Routes to phase orchestrators via Define/Build/Ship |
| `dplc-prereq` | Define | 1 | phase-zero-checklist |
| `dplc-triage` | Define | 1 | marketplace-search, data-product-classification, demand-tracker-entry, consumer-use-case-map |
| `dplc-discovery` | Define | 1 | discover-data, data-profiling, confluence-fetch, feasibility-report, requirements-acceptance-criteria, business-case, outcome-kpi-statement, effort-estimate |
| `dplc-design` | Define | 1 | data-modeling, column-lineage, data-contract, data-model, transformation-spec, architecture-diagram, schedule-backfill-plan, integration-blueprint |
| `dplc-build` | Build | 3 | source-aligned, domain-aligned, deequ-rules, build-checklist |
| `dplc-validate` | Build | 3 | data-profiling, foundation-review, uat-sign-off, data-quality-sign-off, code-review-sign-off |
| `dplc-publish` | Ship | 2 | deployment-record, consumer-onboarding-guide, release-notes |
| `dplc-operate` | Ship | 2 | runbook, incident-log, sla-dashboard-spec, warranty-handoff-sign-off |
| `dplc-evolve` | Ship | 2 | column-lineage, impact-assessment, downstream-impact-assessment, usage-analytics-report |

## Phase Orchestrator Pattern (Discovery example)

1. **Read prior artifacts.** Check for Phase 1 demand-tracker-entry and
   consumer-use-case-map. Pull product name, consumers, classification.
   Don't re-ask what's already captured.

2. **Run execution skills.** Invoke discover-data to query Unity Catalog.
   Invoke data-profiling on candidate sources to get real row counts, date
   ranges, null rates. Optionally invoke confluence-fetch for design docs.

3. **Feed results to document skills.** Call feasibility-report with profiling
   data — "Data Availability" gets real numbers. Call requirements with
   discovered schema — NFRs reference real columns and volumes. Call remaining
   document skills with accumulated context.

4. **Cross-reference.** Effort-estimate references feasibility findings.
   Requirements reference Phase 1 consumer use cases. No re-derivation.

Output: same 5 artifacts, grounded in real data instead of prose estimates.

## Code Quality Assessment

Most of the edo-ai-skills Python code is salvageable:

**Solid (minor cleanup):** databricks_client, jira_client, dremio_sql,
column_lineage, data_access_roles, generate_coi_artifacts

**Targeted fixes needed:**
- `impact_assessment.py` — subprocess call to sibling skill directory needs
  to become an import
- `end_to_end_lineage.py` — path coupling to one dbt project layout needs
  parameterization
- `config.py` — quoted-value parsing bug, side-effectful path resolution
- `dbt_executor.py` — schema swap needs context manager for safe cleanup

**Needs decomposition (Wave 3):**
- source-aligned scripts — 800+ lines, extract core functions
- domain-aligned scripts — similar decomposition

## Gaps the Refactoring Addresses

From the Index Data Product simulation gap analysis:

1. **Prose where there should be code** → execution skills produce real
   artifacts (DDL, dbt models, DQ rules) alongside the documents
2. **Self-acknowledged gaps** → orchestrators invoke execution skills so
   documents don't need "Execution Skill Opportunities" sections
3. **Cross-artifact redundancy** → orchestrators read prior phase artifacts
   and pass context forward instead of re-deriving
4. **Generic estimates** → profiling and discovery produce real numbers that
   feed into documents
