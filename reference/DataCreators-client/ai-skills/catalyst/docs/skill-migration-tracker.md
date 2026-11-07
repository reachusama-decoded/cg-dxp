# Skill Migration Tracker

**Living document** tracking the migration of skills from edo-ai-skills (develop) through Jess's DPLC bundle (PR #79) to AI Catalyst production.

**Last updated:** 2026-04-30

---

## Legend

| Status | Meaning |
|--------|---------|
| **Ported** | Fully brought to AI Catalyst and working |
| **Rewritten** | Reimplemented in AI Catalyst (not a copy) |
| **Partial** | Some logic brought over, significant gaps remain |
| **Promoted** | Promoted to skills/document/, enriched with triggers and templates |
| **Missing** | Not in AI Catalyst at all |
| **Not Needed** | Intentionally excluded (Hourglass-specific, redundant, etc.) |

---

## 1. Platform Knowledge

The domain knowledge that skills depend on to produce correct output.

| Content | edo-ai-skills (develop) | Jess's bundle (PR #79) | AI Catalyst | Status | Wave | Notes |
|---------|------------------------|----------------------|----------|--------|------|-------|
| Platform concepts (medallion, bi-temporal SCD2, surrogate keys, DAG patterns, EAV pivoting, union patterns, prototype-to-foundation, asset mapping, source systems, IM vs MSS patterns) | `docs/wiki/platform/concepts/` (11 files) | Not included | — | **Missing** | 1 | Critical — skills produce generic output without this |
| Platform ADRs (dbt-spark-sql, bitemporal-scd2, delta-parquet, deequ-quality, caspian-orchestration, sha-change-detection) | `docs/wiki/platform/decisions/` (6 files) | Not included | — | **Missing** | 1 | Critical — defines why patterns exist |
| IM Foundation domains (18 files), entities (12 files), schema, index | `docs/wiki/im-foundation/` | Not included | — | **Missing** | 1 | Critical — includes index-constituent-position |
| MSS Foundation domains (9 files), entities (13 files), pipelines (8 files), schema, index | `docs/wiki/mss-foundation/` | Not included | — | **Missing** | 2 | Important for MSS data products |
| Casper data catalog (42+ domain READMEs) | `discover-data/references/casper-data-catalog/` | Not included | — | **Missing** | 1 | Critical — offline catalog context for discover-data |
| Client data catalog (33 files) | `discover-data/references/client-data-catalog/` | Not included | — | **Missing** | 2 | Important for MSS |
| Data product classification domain map | `data-product-classification/assets/dc_tag_domain_map.json` | Not included | — | **Dropped** | — | Classification skill removed |
| Profiling checklist | `data-profiling/references/PROFILING_CHECKLIST.md` | Not included | `skills/execution/data-profiling/references/PROFILING_CHECKLIST.md` | **Ported** | 1 | |
| Deequ examples | `deequ-rules/references/deequ_examples.md` | Not included | — | **Missing** | 3 | Needed for DQ rule generation |
| Foundation review naming conventions + checklist | `foundation-review/references/` (2 files) | Not included | — | **Missing** | 2 | Needed for code review automation |
| DAG YAML examples + template catalog | `dag-yaml/references/` (2 files) | Not included | — | **Missing** | 3 | Needed for DAG generation |
| Entity scaffold model examples | `entity-scaffold/references/model_examples.md` | Not included | — | **Missing** | 3 | |
| Brand guidelines | `cg-brand-guidelines/references/` (2 files) | Not included | — | **Missing** | Nice-to-have | |

---

## 2. Skills (SKILL.md files)

### Orchestrators & Concierge (new in AI Catalyst)

| Skill | edo-ai-skills | Jess's bundle | AI Catalyst | Status | Wave |
|-------|--------------|---------------|----------|--------|------|
| dplc-concierge | — | — | `skills/dplc-concierge/SKILL.md` | **New** | 1 |
| dplc-prereq | — | `catalyst-prereq-check-docs` | `skills/dplc-prereq/SKILL.md` | **New** | 1 |
| dplc-triage | — | `catalyst-triage-docs` | `skills/dplc-triage/SKILL.md` | **New** | 1 |
| dplc-discovery | — | `catalyst-discovery-docs` | `skills/dplc-discovery/SKILL.md` | **New** | 1 |
| dplc-design | — | `catalyst-design-docs` | `skills/dplc-design/SKILL.md` | **New** | 1 |
| dplc-build | — | — | — | **Missing** | 3 |
| dplc-validate | — | `catalyst-validate-docs` | — | **Missing** | 3 |
| dplc-publish | — | `catalyst-publish-docs` | — | **Missing** | 2 |
| dplc-operate | — | `catalyst-operate-docs` | — | **Missing** | 2 |
| dplc-evolve | — | `catalyst-evolve-docs` | — | **Missing** | 2 |

### Execution Skills

| Skill | edo-ai-skills | Jess's bundle | AI Catalyst | Status | Wave | Gap detail |
|-------|--------------|---------------|----------|--------|------|------------|
| source-aligned | Full skill: SKILL.md + 14 prompts + 11 scripts + dbt templates | `catalyst-source-aligned` (full copy) | `skills/execution/source-aligned/` (full: SKILL.md + 15 prompts + 11 scripts + 8 dbt templates) | **Ported** | 3 | Brought from Jess's bundle with path updates |
| domain-aligned | Full skill: SKILL.md + 11 prompts + 2 scripts + dbt templates | `catalyst-domain-aligned` (full copy) | `skills/execution/domain-aligned/` (full: SKILL.md + 11 prompts + 2 scripts + 2 dbt templates) | **Ported** | 3 | Brought from Jess's bundle with path updates |
| consumer-aligned | — | `catalyst-consumer-aligned` (new) | `skills/execution/consumer-aligned/SKILL.md` | **Ported** | 3 | SKILL.md only — no prompts/scripts yet |
| discover-data | SKILL.md + 2 scripts + 75+ catalog references | — | `skills/execution/discover-data/SKILL.md` (thin) + `skills/core/discover.py` | **Partial** | 1 | Missing: catalog references, data_access_roles.py, export_uc_sources.py |
| data-profiling | SKILL.md + profiling checklist reference | — | `skills/execution/data-profiling/` (SKILL.md + references/PROFILING_CHECKLIST.md) + `skills/core/profile.py` | **Ported** | 1 | Full skill with profiling checklist |
| data-modeling | SKILL.md + exemplar.mmd + prompt.md | — | `skills/execution/data-modeling/` (SKILL.md + exemplar.mmd + references/prompt.md) | **Ported** | 1 | Full skill with exemplar and prompt reference |
| column-lineage | SKILL.md + 2 scripts + evals | — | `skills/execution/column-lineage/SKILL.md` (thin) + `skills/core/lineage.py` | **Partial** | 1 | Missing: end_to_end_lineage.py |
| data-product-classification | SKILL.md + 12 scripts + domain map JSON | — | — | **Dropped** | — | User knows their own product's classification better than a keyword matcher |
| confluence-fetch | SKILL.md + script | — | `skills/execution/confluence-fetch/SKILL.md` + core + client | **Rewritten** | 1 | Working with v2 API |
| marketplace-search | SKILL.md + Playwright script | — | `skills/execution/marketplace-search/SKILL.md` + `skills/core/marketplace.py` (stub) | **Partial** | 1 | No Playwright, HTTP stub only |
| impact-assessment | SKILL.md + script | — | — | **Missing** | 2 | |
| foundation-review | SKILL.md + 4 prompts + 2 references | — | — | **Missing** | 2 | |
| deequ-rules | SKILL.md + 2 prompts + 1 reference | — | — | **Missing** | 3 | |
| dag-yaml | SKILL.md + 3 prompts + 2 references | — | — | **Missing** | 3 | |
| generate-dag | SKILL.md | — | — | **Missing** | 3 | |
| entity-scaffold | SKILL.md + 6 prompts + 1 reference | — | — | **Missing** | 3 | |
| domain-wiki | SKILL.md | — | — | **Missing** | 1 | Generates wiki docs for domains |
| extract-code-patterns | SKILL.md | — | — | **Missing** | Nice-to-have | |
| dremio-query | SKILL.md + scripts + references | — | — | **Missing** | Nice-to-have | |
| kedro-to-dbt | SKILL.md + 4 prompts + 2 references | — | — | **Missing** | Nice-to-have | |

### Document Skills (DPLC artifacts)

| Skill | edo-ai-skills | Jess's bundle | AI Catalyst | Status | Wave |
|-------|--------------|---------------|----------|--------|------|
| phase-zero-checklist | — | In prereq-check-docs | `skills/document/` | **Ported** | 1 |
| demand-tracker-entry | — | In triage-docs | `skills/document/` | **Ported** | 1 |
| consumer-use-case-map | — | In triage-docs | `skills/document/` | **Ported** | 1 |
| product-requirements-document | — | — | `skills/document/` | **New** (from Mark Walker's branch) | 1 |
| feasibility-report | — | In discovery-docs | `skills/document/` | **Ported** | 1 |
| requirements-acceptance-criteria | — | In discovery-docs | `skills/document/` | **Ported** | 1 |
| business-case | — | In discovery-docs | `skills/document/` | **Ported** | 1 |
| outcome-kpi-statement | — | In discovery-docs | `skills/document/` | **Ported** | 1 |
| effort-estimate | — | In discovery-docs | `skills/document/` | **Ported** | 1 |
| privacy-impact-assessment | — | In discovery-docs | `skills/document/` | **Ported** | 1 |
| poc-spike-findings | — | In discovery-docs | `skills/document/` | **Ported** | 1 |
| data-contract | — | In design-docs | `skills/document/` | **Ported** | 1 |
| data-model | — | In design-docs | `skills/document/` | **Ported** | 1 |
| transformation-spec | — | In design-docs | `skills/document/` | **Ported** | 1 |
| architecture-diagram | — | In design-docs | `skills/document/` | **Ported** | 1 |
| integration-blueprint | — | In design-docs | `skills/document/` | **Ported** | 1 |
| schedule-backfill-plan | — | In design-docs | `skills/document/` | **Ported** | 1 |
| nfr-specification | — | In design-docs | `skills/document/` | **Ported** | 1 |
| security-design | — | In design-docs | `skills/document/` | **Ported** | 1 |
| dataops-handoff-draft | — | In design-docs | `skills/document/` | **Ported** | 1 |
| build-checklist | — | In build-docs (implied) | `skills/document/` | **Promoted** | 3 |
| unit-test-report | — | — | `skills/document/` | **Promoted** | 3 |
| integration-test-report | — | — | `skills/document/` | **Promoted** | 3 |
| code-review-sign-off | — | — | `skills/document/` | **Promoted** | 3 |
| uat-sign-off | — | In validate-docs | `skills/document/` | **Promoted** | 3 |
| data-quality-sign-off | — | In validate-docs | `skills/document/` | **Promoted** | 3 |
| deployment-record | — | In publish-docs | `skills/document/` | **Promoted** | 2 |
| consumer-onboarding-guide | — | In publish-docs | `skills/document/` | **Promoted** | 2 |
| release-notes | — | In publish-docs | `skills/document/` | **Promoted** | 2 |
| runbook | — | In operate-docs | `skills/document/` | **Promoted** | 2 |
| incident-log | — | In operate-docs | `skills/document/` | **Promoted** | 2 |
| warranty-handoff-sign-off | — | In operate-docs | `skills/document/` | **Promoted** | 2 |
| sla-dashboard-spec | — | In operate-docs | `skills/document/` | **Promoted** | 2 |
| usage-analytics-report | — | In evolve-docs | `skills/document/` | **Promoted** | 2 |
| deprecation-notice | — | In evolve-docs | `skills/document/` | **Promoted** | 2 |
| downstream-impact-assessment | — | In evolve-docs | `skills/document/` | **Promoted** | 2 |

### Planning Skills

| Skill | edo-ai-skills | Jess's bundle | AI Catalyst | Status | Wave |
|-------|--------------|---------------|----------|--------|------|
| discovery-process | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| discovery-interview-prep | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| prd-development | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| epic-breakdown-advisor | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| epic-hypothesis | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| roadmap-planning | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| user-story-mapping | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| user-story-mapping-workshop | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| user-story-splitting | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| user-story | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| feature-investment-advisor | `plugins/planning/` | — | — | **Missing** | Nice-to-have |
| executive-onboarding-playbook | `plugins/planning/` | — | — | **Missing** | Nice-to-have |

### Document Generation Skills

| Skill | edo-ai-skills | Jess's bundle | AI Catalyst | Status | Wave |
|-------|--------------|---------------|----------|--------|------|
| cg-brand-guidelines | `plugins/documents/` | — | — | **Missing** | Nice-to-have |
| cg-word-document | `plugins/documents/` | — | — | **Missing** | Nice-to-have |
| create-powerpoint | `plugins/documents/` | — | — | **Missing** | Nice-to-have |
| collect-markdown | `plugins/documents/` | — | — | **Missing** | Nice-to-have |
| markdown-to-docx | `plugins/documents/` | — | — | **Missing** | Nice-to-have |

### Utility Skills (new in AI Catalyst)

Plugin-meta skills for feedback, telemetry, config, etc. Not migrated from edo-ai-skills — born in AI Catalyst.

| Skill | edo-ai-skills | AI Catalyst | Status | Wave | Notes |
|-------|--------------|----------|--------|------|-------|
| catalyst-feedback | — | `skills/catalyst-feedback/SKILL.md` | **New** | 1 | v1.1.0. Files GitHub issues on cg-open-itg/catalyst with auto-captured session context + mandatory preview-before-file. Zero user config (piggybacks on gh auth). See PR #16 and `docs/feedback.md`. |

### Hourglass Skills

| Skill | edo-ai-skills | AI Catalyst | Status | Wave | Notes |
|-------|--------------|----------|--------|------|-------|
| hourglass (main) | `plugins/hourglass/` | — | **Not Needed** | — | Separate framework per RFD 0006 |
| databricks / databricks-api / databricks-sdk | `plugins/hourglass/` | `skills/clients/databricks.py` covers basic SQL | **Not Needed** | — | Platform client covers our needs |
| dbt-writing / hourglass-dbt-model | `plugins/hourglass/` | — | **Not Needed** | — | Build standards come from RFDs |
| 15 other hourglass-* skills | `plugins/hourglass/` | — | **Not Needed** | — | Hourglass-specific |
| skill-creator | `plugins/hourglass/` | — | **Missing** | Nice-to-have | Eval framework is useful |

---

## 3. Scripts & Core Functions

| Component | edo-ai-skills | AI Catalyst | Status | Wave | Notes |
|-----------|--------------|----------|--------|------|-------|
| `scripts/shared/databricks_client.py` | Yes | `skills/clients/databricks.py` (rewritten) | **Rewritten** | 1 | |
| `scripts/shared/dbt_executor.py` | Yes | — | **Missing** | 3 | Needed for build phase |
| `scripts/shared/config.py` | Yes | — | **Missing** | 1 | Env var loading, workspace path |
| `scripts/jira_client.py` | Yes | — | **Missing** | 2 | |
| `scripts/dremio_sql.py` | Yes | — | **Missing** | Nice-to-have | |
| `scripts/dbx_sql.py` | Yes | — | **Missing** | Nice-to-have | |
| `scripts/data_access_roles.py` | Yes | — | **Missing** | 1 | Used by discover-data |
| `scripts/generate_catalog.py` | Yes | — | **Missing** | Nice-to-have | |
| `scripts/validate_skills.py` | Yes | — | **Missing** | Important | CI validation |
| `scripts/new_skill.py` | Yes | — | **Missing** | Nice-to-have | |
| `scripts/run_eval.py` | Yes | — | **Missing** | Important | |
| Source-aligned scripts (11 files) | Yes | — | **Missing** | 3 | Pipeline scaffolding |
| Domain-aligned scripts (2 files) | Yes | — | **Missing** | 3 | |
| Column-lineage end_to_end_lineage.py | Yes | — | **Missing** | 1 | |
| Impact assessment script | Yes | — | **Missing** | 2 | |
| Classification scripts (12 files) | Yes | `skills/core/classify.py` (simplified) | **Partial** | 1 | |
| Confluence recursive fetch | Yes | `skills/core/confluence.py` (rewritten) | **Rewritten** | 1 | |
| Jira scripts (5 files) | Yes | — | **Missing** | 2 | |
| Document generation scripts (cg_slides.py, cg_docx.py, md_to_docx.py) | Yes | — | **Missing** | Nice-to-have | |

### New in AI Catalyst (not from edo-ai-skills)

| Component | Location | Notes |
|-----------|----------|-------|
| `skills/core/discover.py` | discover_tables() | New implementation |
| `skills/core/profile.py` | profile_table() | New implementation |
| `skills/core/lineage.py` | trace_lineage() | Based on column_lineage.py concepts |
| `skills/core/confluence.py` | fetch_confluence_page() | New implementation |
| `skills/core/marketplace.py` | search_marketplace() | HTTP stub |
| `skills/core/classify.py` | classify_data_product() | Simplified keyword matcher |
| `skills/clients/databricks.py` | DatabricksClient | New implementation |
| `skills/clients/confluence.py` | ConfluenceClient | New implementation |

---

## 4. dbt Templates & Macros

| Template | edo-ai-skills | Jess's bundle | AI Catalyst | Status | Wave |
|----------|--------------|---------------|----------|--------|------|
| surrogate_key_v3.sql | source-aligned + domain-aligned | Both catalyst- variants | — | **Missing** | 3 |
| get_custom_schema.sql | source-aligned + domain-aligned | Both | — | **Missing** | 3 |
| incremental_materialization.sql | source-aligned | catalyst-source-aligned | — | **Missing** | 3 |
| dbt_spark_get_incremental_sql.sql | source-aligned | catalyst-source-aligned | — | **Missing** | 3 |
| cspn_commit_checkpoints.sql | source-aligned | catalyst-source-aligned | — | **Missing** | 3 |
| cspn_utils.sql | source-aligned | catalyst-source-aligned | — | **Missing** | 3 |
| add_default_metric.sql | source-aligned | catalyst-source-aligned | — | **Missing** | 3 |
| create_schema.sql | source-aligned | catalyst-source-aligned | — | **Missing** | 3 |
| generate_surrogate_key_v3.sql | domain-aligned | catalyst-domain-aligned | — | **Missing** | 3 |
| data-modeling exemplar.mmd | data-platform | — | `skills/execution/data-modeling/exemplar.mmd` | **Ported** | 1 |

---

## 5. Evals & Testing

| Item | edo-ai-skills | AI Catalyst | Status | Wave |
|------|--------------|----------|--------|------|
| 11 evals.json files (top-level) | Yes | — | **Missing** | Important |
| ~25 trigger_eval_set.json files (per-skill) | Yes | — | **Missing** | Important |
| source-aligned grading_results.json | Yes | — | **Missing** | 3 |
| 14 test files in tests/ | Yes | 3 test files in skills/tests/ (79 tests passing) | **Partial** | Ongoing |

---

## 6. Infrastructure & Config

| Item | edo-ai-skills | AI Catalyst | Status | Wave |
|------|--------------|----------|--------|------|
| pyproject.toml | Yes | — | **Missing** | Important |
| .devcontainer/ (3 files) | Yes | — | **Missing** | Nice-to-have |
| .github/hooks/ (5 files) | Yes | — | **Missing** | Nice-to-have |
| CONTRIBUTING.md | Yes | — | **Missing** | Important |
| skills.graph.json | Yes | — | **Missing** | Important |
| marketplace.json + plugin.json files | Yes | `.vscode/settings.json` (different approach) | **Different** | — |
| .env.example | Yes | Yes (ported) | **Ported** | — |
| validate_skills.py | Yes | — | **Missing** | Important |
| setup.sh | Yes | — | **Missing** | Nice-to-have |
| sample_workspace_output/ | Yes | `data-product-workspace/` (live output) | **Different** | — |

---

## Critical Path: What Must Be Done

### Wave 1 (Define) — gaps to close NOW

1. ~~Bring over data-modeling exemplar and detailed prompt~~ DONE
2. ~~Bring over profiling checklist reference~~ DONE
3. ~~Bring over dc_tag_domain_map.json for classification~~ DROPPED (classification skill removed)
4. ~~Fix discover_tables() core function~~ DONE (row_count removed, table types fixed)
5. ~~Add orchestrator verbosity (progress reporting)~~ DONE
6. Add end_to_end_lineage.py to lineage support
7. Re-run integration test with fixed skills

### Wave 2 (Ship) — gaps to close

1. MSS Foundation docs (30 files)
2. Client data catalog (33 files)
3. Foundation review skill + prompts + references
4. Impact assessment skill + script
5. Jira integration (client + scripts)
6. Wave 2 orchestrators (publish, operate, evolve)
7. Unstage Wave 2 document skills

### Wave 3 (Build) — gaps to close

1. ~~Full source-aligned skill (14 prompts + 11 scripts + dbt templates)~~ PORTED
2. ~~Full domain-aligned skill (11 prompts + 2 scripts + dbt templates)~~ PORTED
3. ~~Consumer-aligned skill (new)~~ PORTED (SKILL.md only, no prompts/scripts yet)
4. Deequ rules skill + prompts + references
5. DAG YAML skill + prompts + references
6. Entity scaffold skill + prompts
7. dbt_executor shared script
8. Wave 3 orchestrators (build, validate)
9. Unstage Wave 3 document skills
10. All dbt macro templates (10 files)

---

## 5. Removed in PR #95 (RFD 0011/0012/0013 reconciliation with PR #98)

PR #95 deletes 17 skills that were either superseded by the more mature suite in PR #98 or replaced by enumerated rule sets + CI lints.

| Removed | Successor | Reason |
|---------|-----------|--------|
| `generate-dbt-model` | `write-dbt-model` | New skill binds to `SQL-DBSQL-*` / `PY-NAMING-*` rule IDs and emits RFD 0003-compliant paths |
| `validate-sql` | CI `sqlfluff` + `optimize-dbsql-query` (advisory) | Validation moves to CI; advisory findings via the optimizer |
| `write-astro-dag` | `generate-dag` (PR #98) | PR #98's composer is mode-aware (prototype / production / lift-and-shift) and richer |
| `write-dab-resource` | `setup-databricks-asset-bundle` (PR #98) | PR #98 ships full bundle authoring with `DBX-BUNDLE-*` coverage |
| `write-dbt-test` | `write-dbt-model` (column-test stubs) | Column test stubs are now emitted alongside the model file |
| `scaffold-dbt-project` | `setup-dbt-project` (PR #98) | PR #98's version writes the full Delta `+tblproperties:` block |
| `scaffold-domain-repo` | `scaffold-data-product` + `scaffold-repo-structure` (PR #98) | Layout knowledge centralized in `scaffold-repo-structure` |
| `run-dbt` | `run-dbt-on-databricks` (PR #98) | PR #98 supports 3 invocation modes (local / bundle-deploy / bundle-run) |
| `validate-astro-dag` | CI lints; follow-up A2 | Validation runs from CI; skill-form deferred until `promotions.yml` resolver settles |
| `validate-dab` | CI `databricks bundle validate`; follow-up A2 | Same — CI-side, skill-form deferred |
| `validate-dbt` | CI `dbt parse` + `sqlfluff`; follow-up A2 | Same |
| `deploy-astro` | CI `astro deploy`; follow-up A1 | Deploy runs from CI; skill-form deferred |
| `deploy-dab` | CI `databricks bundle deploy`; follow-up A1 | Same |
| `optimize-dbt-model` | follow-up A3 | `SQL-PERF-DBT-*` rule category lands in PR1; skill comes after |
| `authoring-airflow-on-astronomer` | RFD 0011 (document-tier) | Standards moved to the RFD; skill collapsed |
| `authoring-databricks-bundles` | RFD 0012 (document-tier) | Same |
| `authoring-dbt-on-dbsql` | RFD 0013 (document-tier) | Same |
