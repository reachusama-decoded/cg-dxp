# DPLC Wave 1 (Define) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the Define stage (Phases 0-3) of the DPLC skill package — concierge, 4 phase orchestrators, 7 graduated execution skills, enhanced document skills, platform clients, core functions, and a landing page.

**Architecture:** Phase orchestrators compose atomic skills (execution + document) in lifecycle order. Execution skills run first to gather real data, then document skills produce artifacts grounded in that data. A concierge routes new users via Define/Build/Ship. Everything follows the RFD 0006 layering model: platform clients → core functions → skills → orchestrators.

**Tech Stack:** Python 3.9+, Claude Code skills (SKILL.md), Databricks SDK, Confluence REST API, pytest

---

## File Structure

```
skills/
├── index.html                          # Landing page
├── README.md                           # Plain-text fallback
├── concierge/
│   └── SKILL.md                        # Routes to Define/Build/Ship
├── orchestrators/
│   ├── dplc-prereq/SKILL.md
│   ├── dplc-triage/SKILL.md
│   ├── dplc-discovery/SKILL.md
│   └── dplc-design/SKILL.md
├── execution/
│   ├── discover-data/SKILL.md
│   ├── data-profiling/SKILL.md
│   ├── data-modeling/SKILL.md
│   ├── column-lineage/SKILL.md
│   ├── confluence-fetch/SKILL.md
│   ├── marketplace-search/SKILL.md
│   └── data-product-classification/SKILL.md
├── document/
│   ├── phase-zero-checklist/SKILL.md
│   ├── demand-tracker-entry/SKILL.md
│   ├── consumer-use-case-map/SKILL.md
│   ├── requirements-acceptance-criteria/SKILL.md
│   ├── feasibility-report/SKILL.md
│   ├── business-case/SKILL.md
│   ├── outcome-kpi-statement/SKILL.md
│   ├── effort-estimate/SKILL.md
│   ├── data-contract/SKILL.md
│   ├── data-model/SKILL.md
│   ├── transformation-spec/SKILL.md
│   ├── architecture-diagram/SKILL.md
│   ├── schedule-backfill-plan/SKILL.md
│   ├── integration-blueprint/SKILL.md
│   ├── nfr-specification/SKILL.md
│   ├── security-design/SKILL.md
│   ├── dataops-handoff-draft/SKILL.md
│   └── ... (remaining Phase 4-8 document skills, moved but not enhanced until Wave 2-3)
├── core/
│   ├── __init__.py
│   ├── discover.py                     # discover_tables()
│   ├── profile.py                      # profile_table()
│   ├── lineage.py                      # trace_lineage()
│   ├── confluence.py                   # fetch_confluence_page()
│   ├── marketplace.py                  # search_marketplace()
│   └── classify.py                     # classify_data_product()
├── clients/
│   ├── __init__.py
│   ├── databricks.py                   # DatabricksClient
│   └── confluence.py                   # ConfluenceClient
└── tests/
    ├── __init__.py
    ├── test_discover.py
    ├── test_profile.py
    ├── test_lineage.py
    ├── test_confluence.py
    ├── test_marketplace.py
    ├── test_classify.py
    ├── test_databricks_client.py
    └── test_confluence_client.py
```

Templates stay at `rfd/0002/templates/` — they're part of the RFD spec.

---

### Task 1: Directory Structure and Skill Migration

**Files:**
- Create: `skills/` directory tree (see file structure above)
- Move: `rfd/0002/skills/*/SKILL.md` → `skills/document/*/SKILL.md` (all 35)
- Modify: each moved SKILL.md to update template path references from `rfd/0002/templates/` to `../../rfd/0002/templates/` (or use repo-root-relative paths)

- [ ] **Step 1: Create the skills directory structure**

```bash
mkdir -p skills/{concierge,orchestrators/{dplc-prereq,dplc-triage,dplc-discovery,dplc-design},execution/{discover-data,data-profiling,data-modeling,column-lineage,confluence-fetch,marketplace-search,data-product-classification},document,core,clients,tests}
```

- [ ] **Step 2: Move all 35 document skills**

```bash
# Move each skill directory from rfd/0002/skills/ to skills/document/
for skill in rfd/0002/skills/*/; do
  name=$(basename "$skill")
  cp -r "$skill" "skills/document/$name"
done
```

- [ ] **Step 3: Update template paths in moved skills**

Each SKILL.md references its template like `rfd/0002/templates/02-discovery/business-case.md`. These paths need to work from the new location. Update all 35 to use repo-root-relative paths (skills are invoked from repo root by Claude Code, so the existing paths should still work — verify this).

- [ ] **Step 4: Verify a moved skill still works**

Run one skill from its new location to confirm template resolution:
```bash
# Test that the skill can still read its template
claude -p "Using the skill at skills/document/demand-tracker-entry/SKILL.md, create a demand tracker entry for a test data product called Widget Analytics"
```
Verify the output matches the template structure.

- [ ] **Step 5: Remove old skill location**

```bash
rm -rf rfd/0002/skills/
```

- [ ] **Step 6: Commit**

```bash
git add skills/ rfd/0002/
git commit -m "feat: move skills to top-level directory structure

Move 35 document skills from rfd/0002/skills/ to skills/document/.
Create directory structure for execution skills, orchestrators,
concierge, core functions, and platform clients per RFD 0006."
```

---

### Task 2: Landing Page

**Files:**
- Create: `skills/index.html`
- Create: `skills/README.md`

- [ ] **Step 1: Create the HTML landing page**

Create `skills/index.html` — a single-file HTML page (inline CSS, no external deps) that uses the AI Catalyst design language (clean, blue accents, card-based layout). Should include:

- Header with AI Catalyst branding
- Three stage cards: **Define** (Phases 0-3), **Build** (Phases 4-5), **Ship** (Phases 6-8)
- Each card lists the available skills in that stage
- A "Getting Started" section explaining the concierge entry point
- Skills marked as "Coming Soon" for Wave 2-3

Use the AI Catalyst app screenshot as design reference: clean white background, blue accent color, card layout with counts, Define/Build/Ship stage grouping.

- [ ] **Step 2: Create the README.md fallback**

Plain markdown version of the same content for GitHub rendering.

- [ ] **Step 3: Commit**

```bash
git add skills/index.html skills/README.md
git commit -m "feat: add DPLC skills landing page

HTML landing page with Define/Build/Ship stage grouping and skill
inventory. Matches AI Catalyst app design language."
```

---

### Task 3: Platform Clients

**Files:**
- Create: `skills/clients/databricks.py`
- Create: `skills/clients/confluence.py`
- Create: `skills/clients/__init__.py`
- Create: `skills/tests/test_databricks_client.py`
- Create: `skills/tests/test_confluence_client.py`

Source: `cg-edo/edo-ai-skills` develop branch. Fetch with:
```bash
gh api "repos/cg-edo/edo-ai-skills/contents/scripts/shared/databricks_client.py?ref=develop" --jq '.content' | base64 -d
```

- [ ] **Step 1: Write failing tests for DatabricksClient**

```python
# skills/tests/test_databricks_client.py
import pytest
from skills.clients.databricks import DatabricksClient

def test_init_requires_host_and_token():
    with pytest.raises(TypeError):
        DatabricksClient()

def test_init_stores_config():
    client = DatabricksClient(host="https://test.cloud.databricks.com", token="test-token")
    assert client.host == "https://test.cloud.databricks.com"

def test_execute_sql_requires_warehouse_id():
    client = DatabricksClient(host="https://test.cloud.databricks.com", token="test-token")
    with pytest.raises(ValueError, match="warehouse_id"):
        client.execute_sql("SELECT 1")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/rbap/code/catalyst
python -m pytest skills/tests/test_databricks_client.py -v
```
Expected: FAIL (module not found)

- [ ] **Step 3: Port DatabricksClient from edo-ai-skills**

Fetch `scripts/shared/databricks_client.py` from edo-ai-skills. Adapt to `skills/clients/databricks.py`:
- Keep the class structure (it's solid)
- Remove any edo-ai-skills-specific imports
- Ensure host/token are explicit constructor params (not env-var magic)
- Move warehouse_id validation to `__init__` (fix the lazy validation issue from code review)

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest skills/tests/test_databricks_client.py -v
```
Expected: PASS

- [ ] **Step 5: Write failing tests for ConfluenceClient**

```python
# skills/tests/test_confluence_client.py
import pytest
from skills.clients.confluence import ConfluenceClient

def test_init_requires_base_url_and_credentials():
    with pytest.raises(TypeError):
        ConfluenceClient()

def test_init_stores_config():
    client = ConfluenceClient(base_url="https://wiki.example.com", email="test@example.com", token="test-token")
    assert client.base_url == "https://wiki.example.com"
```

- [ ] **Step 6: Implement ConfluenceClient**

Extract from edo-ai-skills `confluence-fetch` skill scripts. Create `skills/clients/confluence.py` with:
- `ConfluenceClient(base_url, email, token)`
- `get_page(page_id) → dict`
- `get_page_tree(page_id) → list[dict]`

- [ ] **Step 7: Run tests, verify pass**

```bash
python -m pytest skills/tests/test_confluence_client.py -v
```

- [ ] **Step 8: Create __init__.py**

```python
# skills/clients/__init__.py
from .databricks import DatabricksClient
from .confluence import ConfluenceClient
```

- [ ] **Step 9: Commit**

```bash
git add skills/clients/ skills/tests/test_databricks_client.py skills/tests/test_confluence_client.py
git commit -m "feat: add platform clients (DatabricksClient, ConfluenceClient)

Ported from edo-ai-skills with minor fixes:
- DatabricksClient: warehouse_id validated at init, not lazily
- ConfluenceClient: extracted from confluence-fetch skill scripts"
```

---

### Task 4: Core Functions

**Files:**
- Create: `skills/core/discover.py`
- Create: `skills/core/profile.py`
- Create: `skills/core/lineage.py`
- Create: `skills/core/confluence.py`
- Create: `skills/core/marketplace.py`
- Create: `skills/core/classify.py`
- Create: `skills/core/__init__.py`
- Create: `skills/tests/test_discover.py`
- Create: `skills/tests/test_profile.py`
- Create: `skills/tests/test_lineage.py`
- Create: `skills/tests/test_confluence.py`
- Create: `skills/tests/test_marketplace.py`
- Create: `skills/tests/test_classify.py`

Each core function is extracted from an edo-ai-skills skill. Follow the same TDD pattern for each: write failing test → implement → verify pass.

- [ ] **Step 1: Write tests for discover_tables()**

```python
# skills/tests/test_discover.py
import pytest
from skills.core.discover import discover_tables

def test_discover_tables_returns_list():
    # With a mock client, verify the function returns a list of table metadata
    result = discover_tables(client=mock_client, catalog="test", keywords=["index"])
    assert isinstance(result, list)

def test_discover_tables_filters_by_keywords():
    result = discover_tables(client=mock_client, catalog="test", keywords=["index"])
    assert all("index" in t["name"].lower() for t in result)
```

- [ ] **Step 2: Implement discover_tables()**

Extract from edo-ai-skills `discover-data` skill. Create `skills/core/discover.py`:
- `discover_tables(client: DatabricksClient, catalog: str, keywords: list[str]) → list[dict]`
- Pure function: takes a client, returns structured results
- No side effects, no file I/O

- [ ] **Step 3: Run tests, verify pass**

- [ ] **Step 4: Repeat for profile_table()**

Extract from `data-profiling` skill. `skills/core/profile.py`:
- `profile_table(client: DatabricksClient, catalog: str, schema: str, table: str) → dict`
- Returns: row_count, date_range, column_stats (nulls, distinct counts, types)

- [ ] **Step 5: Repeat for trace_lineage()**

Extract from `column-lineage` skill. `skills/core/lineage.py`:
- `trace_lineage(sql: str) → dict`
- Pure function — parses SQL, returns column-level lineage mapping
- Fix: parameterize project root (don't hardcode path assumptions)

- [ ] **Step 6: Repeat for fetch_confluence_page()**

Extract from `confluence-fetch` skill. `skills/core/confluence.py`:
- `fetch_confluence_page(client: ConfluenceClient, page_id: str) → str`
- Returns markdown content

- [ ] **Step 7: Repeat for search_marketplace() and classify_data_product()**

Extract from `marketplace-search` and `data-product-classification` skills:
- `skills/core/marketplace.py`: `search_marketplace(query: str) → list[dict]`
- `skills/core/classify.py`: `classify_data_product(description: str) → dict`

- [ ] **Step 8: Create __init__.py**

```python
# skills/core/__init__.py
from .discover import discover_tables
from .profile import profile_table
from .lineage import trace_lineage
from .confluence import fetch_confluence_page
from .marketplace import search_marketplace
from .classify import classify_data_product
```

- [ ] **Step 9: Run full test suite**

```bash
python -m pytest skills/tests/ -v
```
Expected: all pass

- [ ] **Step 10: Commit**

```bash
git add skills/core/ skills/tests/
git commit -m "feat: add core functions extracted from edo-ai-skills

Six core functions: discover_tables, profile_table, trace_lineage,
fetch_confluence_page, search_marketplace, classify_data_product.
Each is a pure function with explicit inputs/outputs and unit tests."
```

---

### Task 5: Execution Skills (7 graduated from edo-ai-skills)

**Files:**
- Create: `skills/execution/discover-data/SKILL.md`
- Create: `skills/execution/data-profiling/SKILL.md`
- Create: `skills/execution/data-modeling/SKILL.md`
- Create: `skills/execution/column-lineage/SKILL.md`
- Create: `skills/execution/confluence-fetch/SKILL.md`
- Create: `skills/execution/marketplace-search/SKILL.md`
- Create: `skills/execution/data-product-classification/SKILL.md`

Each skill is a SKILL.md that uses the core functions. These are not copy-pastes from edo-ai-skills — they're rewritten for AI Catalyst conventions with lifecycle context.

- [ ] **Step 1: Write discover-data SKILL.md**

```yaml
---
name: discover-data
description: "Explore data catalogs to find tables relevant to a data product. Use during Phase 2 Discovery to inventory available sources before writing the feasibility report."
argument-hint: "[catalog-or-keywords]"
allowed-tools: Read Grep Bash
---
```

Body should:
- Explain this is a Phase 2 (Discovery) execution skill
- Instruct the model to use `skills/core/discover.py` to query Unity Catalog
- Instruct the model to use `skills/core/profile.py` to profile discovered tables
- Define the output format: structured markdown table of discovered tables with row counts, date ranges, column summaries
- Note that this output feeds into the feasibility-report and requirements-acceptance-criteria document skills

- [ ] **Step 2: Write data-profiling SKILL.md**

Same pattern — Phase 2 execution skill that calls `profile_table()` and produces a structured profiling report.

- [ ] **Step 3: Write data-modeling SKILL.md**

Phase 3 execution skill. This one requires LLM judgment (materialization strategy, SCD type, naming conventions). It calls `generate_ddl()` from core but makes design decisions.

- [ ] **Step 4: Write column-lineage SKILL.md**

Phase 3/8 execution skill. Calls `trace_lineage()` core function. Produces OpenLineage JSON and Mermaid diagrams.

- [ ] **Step 5: Write confluence-fetch SKILL.md**

Cross-phase utility. Calls `fetch_confluence_page()` core function. Converts to markdown.

- [ ] **Step 6: Write marketplace-search and data-product-classification SKILL.md files**

Phase 1 execution skills. marketplace-search checks if a data product already exists. data-product-classification assigns domain and type.

- [ ] **Step 7: Eval test each skill**

For each skill, run against a realistic test prompt and verify output is useful:
```bash
# Example for discover-data
claude -p "Using the skill at skills/execution/discover-data/SKILL.md, find all index-related tables in the caspian catalog"
```

- [ ] **Step 8: Commit**

```bash
git add skills/execution/
git commit -m "feat: add 7 execution skills graduated from edo-ai-skills

discover-data, data-profiling, data-modeling, column-lineage,
confluence-fetch, marketplace-search, data-product-classification.
Each calls core functions and produces structured output for
consumption by document skills and orchestrators."
```

---

### Task 6: Enhance Document Skills (Phase 0-3)

**Files:**
- Modify: `skills/document/feasibility-report/SKILL.md`
- Modify: `skills/document/requirements-acceptance-criteria/SKILL.md`
- Modify: `skills/document/data-contract/SKILL.md`
- Modify: `skills/document/data-model/SKILL.md`
- Modify: `skills/document/transformation-spec/SKILL.md`
- Modify: remaining Phase 0-3 document skills (17 total)

The enhancement: teach document skills to accept execution context as optional input. If profiling data, discovered tables, or prior phase artifacts are provided, use them instead of guessing.

- [ ] **Step 1: Update feasibility-report skill**

Add to the SKILL.md instructions:

```markdown
## Execution Context (optional)

If the following data is available in the conversation context, use it
to populate the corresponding sections with real data instead of estimates:

- **Profiling results** from data-profiling skill → populate Data Availability
  section with actual row counts, date ranges, null rates, completeness
- **Discovery results** from discover-data skill → populate source system
  inventory with actual table names, schemas, metadata
- **Prior artifacts** from Phase 1 (demand-tracker-entry, consumer-use-case-map)
  → reference product name, consumers, classification instead of re-asking

If execution context is not available, proceed with user-provided information
as before.
```

- [ ] **Step 2: Update requirements-acceptance-criteria skill**

Same pattern — if discovered schema info is available, use real column names and volumes for NFRs.

- [ ] **Step 3: Update data-contract, data-model, transformation-spec skills**

If data-modeling execution skill has produced DDL or ER diagrams, reference them. If profiling data exists for source tables, use real statistics.

- [ ] **Step 4: Update remaining Phase 0-3 document skills**

Light touch for skills that don't benefit from execution context (e.g., phase-zero-checklist, business-case). Add the "Prior artifacts" reference pattern so they pull from earlier phases instead of re-asking.

- [ ] **Step 5: Eval test enhanced skills**

Re-run the eval framework from the Index Data Product simulation. Compare outputs with and without execution context to verify the enhancement produces better artifacts.

- [ ] **Step 6: Commit**

```bash
git add skills/document/
git commit -m "feat: enhance Phase 0-3 document skills with execution context

Document skills now accept profiling data, discovery results, and prior
phase artifacts as optional input. When available, artifacts are grounded
in real data instead of prose estimates."
```

---

### Task 7: Phase Orchestrators

**Files:**
- Create: `skills/orchestrators/dplc-prereq/SKILL.md`
- Create: `skills/orchestrators/dplc-triage/SKILL.md`
- Create: `skills/orchestrators/dplc-discovery/SKILL.md`
- Create: `skills/orchestrators/dplc-design/SKILL.md`

- [ ] **Step 1: Write dplc-prereq orchestrator**

Simplest orchestrator — just calls phase-zero-checklist. Exists for consistency so the concierge can route to it.

```yaml
---
name: dplc-prereq
description: "Guide a data product creator through Phase 0 Pre-requisites. Verifies roles, infrastructure, and organizational readiness before starting the lifecycle."
allowed-tools: Read Grep
---
```

- [ ] **Step 2: Write dplc-triage orchestrator**

```yaml
---
name: dplc-triage
description: "Guide a data product creator through Phase 1 Triage. Checks if the data product already exists, classifies it, creates demand tracker entry and consumer use case map."
allowed-tools: Read Grep Bash
---
```

Orchestration sequence:
1. Invoke marketplace-search to check if product already exists
2. Invoke data-product-classification to assign domain and type
3. Invoke demand-tracker-entry document skill with classification context
4. Invoke consumer-use-case-map document skill

- [ ] **Step 3: Write dplc-discovery orchestrator**

The most complex Phase 0-3 orchestrator. Sequence:
1. Read Phase 1 artifacts (demand-tracker-entry, consumer-use-case-map)
2. Invoke discover-data to query Unity Catalog
3. Invoke data-profiling on discovered sources
4. Optionally invoke confluence-fetch for design docs
5. Invoke feasibility-report with profiling data
6. Invoke requirements-acceptance-criteria with schema info
7. Invoke business-case, outcome-kpi-statement, effort-estimate with accumulated context
8. Cross-reference: effort-estimate references feasibility, requirements reference Phase 1 consumers

- [ ] **Step 4: Write dplc-design orchestrator**

Sequence:
1. Read Phase 2 artifacts (requirements, feasibility, data contract from effort-estimate)
2. Invoke data-modeling to produce ER diagrams and DDL
3. Invoke column-lineage if transformation sources are known
4. Invoke data-contract, data-model, transformation-spec, architecture-diagram, schedule-backfill-plan, integration-blueprint with design context
5. Cross-reference: all design artifacts reference requirements and feasibility findings

- [ ] **Step 5: Eval test each orchestrator**

Run dplc-discovery against the Index Data Product scenario (without live Databricks access, use the Confluence proposal as input) and verify:
- It reads Phase 1 artifacts if present
- It calls execution skills before document skills
- Document artifacts contain execution context, not just prose
- Cross-references work (no re-derived information)

- [ ] **Step 6: Commit**

```bash
git add skills/orchestrators/
git commit -m "feat: add Phase 0-3 orchestrators

dplc-prereq, dplc-triage, dplc-discovery, dplc-design.
Each composes execution and document skills in lifecycle order,
feeding real data into artifact generation."
```

---

### Task 8: Concierge

**Files:**
- Create: `skills/concierge/SKILL.md`

- [ ] **Step 1: Write the concierge skill**

```yaml
---
name: dplc-concierge
description: "Guide a data product creator through the Data Product Lifecycle. Start here if you're new to the process or unsure which phase you need. Routes to the right phase based on where you are: Define (Phases 0-3), Build (Phases 4-5), or Ship (Phases 6-8)."
allowed-tools: Read Grep
---
```

Body should:
- Ask "Are you **defining** a data product, **building** it, or **shipping/operating** it?"
- Define: "What are we building and why?" → routes to dplc-prereq, dplc-triage, dplc-discovery, or dplc-design based on what's already done
- Build: "Coming soon — Build phase skills are being hardened for production"
- Ship: "Coming soon — Ship phase skills arriving in Wave 2"
- Check for existing artifacts to determine where the user is in the lifecycle
- If artifacts from prior phases exist, skip ahead to the right phase

- [ ] **Step 2: Eval test the concierge**

Test with different entry points:
- "I'm starting a new data product" → should route to dplc-prereq
- "I have a demand tracker entry and need to do discovery" → should route to dplc-discovery
- "I need to deploy my data product" → should say Wave 2 coming soon

- [ ] **Step 3: Commit**

```bash
git add skills/concierge/
git commit -m "feat: add DPLC concierge skill

Routes data product creators to the right lifecycle phase via
Define/Build/Ship stage grouping. Checks for existing artifacts
to determine where to pick up."
```

---

### Task 9: Integration Test — Full Discovery Flow

**Files:**
- No new files — this is an end-to-end verification

- [ ] **Step 1: Run the full discovery flow via orchestrator**

Start from dplc-discovery with the Index Data Product Confluence proposal as input (same scenario as our simulation). Verify:

1. Orchestrator reads Phase 1 artifacts if they exist in the workspace
2. Execution skills are invoked (discover-data, data-profiling, confluence-fetch)
3. Document skills receive execution context
4. Output artifacts have real data where execution skills ran, and clearly marked unknowns where they couldn't (no bare TBDs)
5. Cross-references work between artifacts

- [ ] **Step 2: Compare output to the simulation artifacts**

Read the simulation artifacts from the `test/rfd-0002-skills-eval` branch and compare. The new artifacts should be strictly better:
- Feasibility report has profiling data where the simulation had adjectives
- Requirements have real column names where the simulation had guesses
- No "Execution Skill Opportunities" sections (the orchestrator filled them)
- No cross-artifact redundancy (information referenced, not re-derived)

- [ ] **Step 3: Run eval framework**

Execute the eval assertions from `data-product-workspace/evals/evals.json` against the new outputs. Pass rate should be >= 98.3% (the simulation baseline).

- [ ] **Step 4: Document results and commit**

```bash
git add skills/
git commit -m "test: verify full Discovery flow via orchestrator

End-to-end test of dplc-discovery against Index Data Product scenario.
Compared to document-only simulation: artifacts now grounded in
execution context with real data and cross-references."
```

---

### Task 10: Final Cleanup and PR

- [ ] **Step 1: Run full test suite**

```bash
python -m pytest skills/tests/ -v
```
All tests pass.

- [ ] **Step 2: Verify all skills have valid frontmatter**

```bash
# Check every SKILL.md has name and description in frontmatter
for f in skills/*/SKILL.md skills/*/*/SKILL.md; do
  echo "=== $f ==="
  head -5 "$f"
done
```

- [ ] **Step 3: Update the landing page with final skill counts**

Update `skills/index.html` and `skills/README.md` with actual counts:
- Define stage: 4 orchestrators + 7 execution + 17 document skills
- Build stage: "Coming in Wave 3"
- Ship stage: "Coming in Wave 2"

- [ ] **Step 4: Commit and create PR**

```bash
git add -A
git commit -m "feat: DPLC Wave 1 complete — Define stage skills

Concierge, 4 phase orchestrators, 7 execution skills, 17 enhanced
document skills, 6 core functions, 2 platform clients, landing page.
Skills are layered per RFD 0006: clients → core → skills → orchestrators."
```

Create PR targeting main.
