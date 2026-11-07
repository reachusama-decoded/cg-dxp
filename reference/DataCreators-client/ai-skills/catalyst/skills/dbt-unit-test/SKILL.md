---
name: dbt-unit-test
description: |
  Generate unit tests for a DBT model. Use this skill when the user says "generate tests for <model>",
  "run dbt-unit-test on <model>", "create unit tests for my DBT model", "test the <model> model",
  "write test cases for <model>", "generate test coverage for <model>",
  or any request to produce, run, or review generated DBT unit tests.
  Also triggered by "dbt-unit-test <model>", "test <model> with dbt-unit-test",
  or "analyse <model> and generate test cases".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: phase-4-build
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - SQL-TEST-005
    - SQL-TEST-006
  upstream-source: cg-edo/edo-ai-skills/plugins/data-platform/skills/dbt-unit-test
  upstream-commit: 74edeb7575038e7b5134ce9f12b6b60ac229c245
  upstream-license: Internal (Capital Group — cg-edo/edo-ai-skills; no external license, internal transfer)
  catalyst-modifications: |
    Migrated from edo-ai-skills by Capital Group on 2026-06-24:
    - updated frontmatter to Catalyst metadata schema
    - fixed sys.path bootstrap in run_from_json.py: uses `_SCRIPTS_DIR = Path(__file__).resolve().parent` to make the bundled `engine/` package importable in the Catalyst repo layout
    - removed edo-ai-skills-specific shared.config dependency (graceful fallback retained)
    - added stdlib-only `load_dotenv()` to run_from_json.py (Catalyst convention; shell/CI env vars win)
    - run_from_json.py: analyzer cache now regenerates on JSONDecodeError instead of raising
    - runner.py: default execution backend switched from pyspark to pandas; ambiguous bare
      column names appearing in more than one source are skipped when building the rename map
    - script_generator.py: added Python-identifier validation on `model_name` / `test_id`
      (prompt-injection guard — these are interpolated into generated class names)
    - script_generator.py / spark_executor.py: pip install hints re-pointed at the cgrepo
      index URL (no public PyPI on the corporate network)
    - pytest_test.py.j2: method-call names (e.g. `.notna()`) excluded from missing-column detection
    - upstream `evals/trigger_eval_set.json` not migrated
---

> _Modified from `cg-edo/edo-ai-skills/plugins/data-platform/skills/dbt-unit-test` @ `74edeb7` by Capital Group on 2026-06-24. See `metadata.catalyst-modifications` for the change set._

# dbt-unit-test — DBT Unit Test Generator

Analyse a DBT integration model's SQL and YAML, generate comprehensive unit
test cases with synthetic seed data, execute them against the real SQL transformation
using pandas (default) or PySpark, and produce a Markdown test report.

## When to Use

- User wants unit tests for a specific DBT model
- User says "generate tests", "run dbt-unit-test", "create test cases", or "test coverage" for a DBT model
- User wants to validate a DBT SQL transformation produces correct output given synthetic inputs
- User wants a test report for a model before or after code review

## Decision Rule

| User Context | Recommended Skill |
|---|---|
| Has a specific DBT model name, wants test cases generated | **dbt-unit-test (this skill)** |
| Already has a `_test_cases.json` file and just wants to re-run | Use `run_from_json.py` directly: `python "${SKILL_DIR}/scripts/run_from_json.py" --json <path> --executor pandas` |

---

## Outputs

All outputs are written to `workspace/dbt-unit-test/<model_name>/`:

```
workspace/dbt-unit-test/<model_name>/
├── <model_name>_test_cases.json          # Agent-generated test cases (seed for re-runs)
├── test_<model_name>_ai_generated.py     # Generated pytest script
├── <model_name>_results.xml              # JUnit XML test results
└── <model_name>_report.md                # Markdown test report
```

---

## Configuration

| Input | Source | Required |
|---|---|---|
| `model_name` | User message | Yes |
| `project_root` | Workspace root (auto-detected) | Auto |
| `executor` | User preference or default | No — default: `pandas` |
| `jira_issue` | User message (e.g. "PROJ-1234") | No |
| `JIRA_URL` | `.env` or environment variable | Required only when fetching Jira AC |
| `JIRA_USERNAME` | `.env` or environment variable | Required only when fetching Jira AC |
| `JIRA_API_TOKEN` | `.env` or environment variable | Required only when fetching Jira AC |

**Jira credentials:** Resolved from environment variables or `.env` file (environment variables take precedence; `.env` is loaded as a fallback):
```
JIRA_URL         — Jira instance URL (e.g. https://capitalgroup.atlassian.net)
JIRA_USERNAME    — your Atlassian email address
JIRA_API_TOKEN   — your Atlassian API token (plain text, not base64-encoded)
```

**Auto-detection:** The skill locates model SQL at:
1. `models/**/<model_name>.sql` — search from workspace root
2. Try with `int_` prefix if not found (e.g., `int_<model_name>.sql`)

---

## Order of Operations

```
Step 0: [ENV CHECK] If JIRA_API_TOKEN unset → jira_ac_context=null, skip Step 1.5 silently
    ↓
Step 1: Locate model files — cache check (offer reuse if _test_cases.json is fresh)
    ↓
Step 1.5: [JIRA — only if JIRA_API_TOKEN is set] Ask for Jira story / AC
    ↓
Step 2: [MERGED] Analyse SQL + Generate test cases in one LLM pass
    ↓
Step 3: [CHECKPOINT] Show brief summary + TC table — ask executor choice — confirm before saving
    ↓
Step 4: Save JSON to workspace/dbt-unit-test/<model_name>/
    ↓
Step 5: Execute pipeline (seed fixing → pytest script → parallel run → report) with chosen executor
    ↓
Step 6: Show result summary and report path
```

---

## How to Execute

### Step 0 — Environment Check (Jira Token)

Check **silently** whether `JIRA_API_TOKEN` **and** `JIRA_USERNAME` are both set in the user's environment or `.env` file.

- If **both are set**: `jira_ac_context` will be populated in Step 1.5.
- If **either is not set**: set `jira_ac_context = null` and **skip Step 1.5 entirely**. Do **not** prompt the user about Jira unless they explicitly mention a Jira issue ID.

**Only show the setup guide below if the user's request contains a Jira issue ID but `JIRA_API_TOKEN` is missing:**

1. Generate an Atlassian API token at [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Add to `.env` in the project root (preferred):
   ```
   JIRA_URL=https://capitalgroup.atlassian.net
   JIRA_USERNAME=your.email@capgroup.com
   JIRA_API_TOKEN=your-api-token
   ```
   Or export in shell (add to `~/.zshrc` for permanence):
   ```bash
   export JIRA_URL="https://capitalgroup.atlassian.net"
   export JIRA_USERNAME="your.email@capgroup.com"
   export JIRA_API_TOKEN="your-api-token"
   ```
3. Verify: `echo $JIRA_API_TOKEN && echo $JIRA_USERNAME`

**Security:** Never commit `.env` to source control — ensure it is in `.gitignore`.

**Corporate network note:** All Jira API calls use the `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE` environment variable to trust the corporate CA bundle (standard on CG machines). Do **not** disable TLS verification — credentials are in flight.

---

### Step 1 — Locate Model Files

Search the workspace for the model SQL file:
- Look in `models/` recursively for `<model_name>.sql`
- Also look for the companion `<model_name>.yml` YAML file
- Also find `database/dbt_tables/<model_name>.sql` (DDL schema, if present)

Read both files completely. Note:
- All `{{ ref('...') }}` and `{{ source('...', '...') }}` table references
- All CTE names
- All output columns in the final SELECT

#### Schema Context (Engine Analyzer)

Run the engine's `DBTModelAnalyzer` against the model to extract:
- All output columns with data types
- Type casts (CAST expressions)
- Checksum column coverage
- Source table DDL schemas

**Path resolution:** The `scripts/` directory is co-located with this SKILL.md file. Derive `SKILL_DIR` from the absolute path used by `read_file` to load this SKILL.md — it is the parent directory of this file (e.g. `.../skills/dbt-unit-test`). Do **not** search for it.

Execute from the engine's scripts directory:
```bash
# SKILL_DIR = parent directory of this SKILL.md file
# e.g. /path/to/catalyst/skills/dbt-unit-test
# Write to a temp file to avoid zsh quoting issues with mixed quotes (per Step 1.5 note)
cat > /tmp/dbt_analyzer_run.py << 'PYEOF'
import sys, json
sys.path.insert(0, '<SKILL_DIR>/scripts')
from engine.analysis.model_analyzer import DBTModelAnalyzer
analyzer = DBTModelAnalyzer(project_root='<workspace_root>')
ctx = analyzer.analyze('<model_name>')
print(json.dumps({
    'schema_columns': [{'name': c.output_name, 'type': c.data_type, 'src': c.source_expr} for c in ctx.schema_columns],
    'type_casts': ctx.type_casts,
    'checksum_columns': ctx.checksum_columns,
    'source_tables': ctx.source_tables,
    'source_table_schemas': ctx.source_table_schemas,
}, indent=2))
PYEOF
python3 /tmp/dbt_analyzer_run.py
```

Use this output as the **authoritative column reference** for Step 2. Every `expected_output` row in generated test cases must include ALL non-audit, non-hash columns from this schema.

#### Cache Check

After locating the SQL file, check whether `workspace/dbt-unit-test/<model_name>/<model_name>_test_cases.json` already exists.

- If it **exists**: inform the user — "Cached test cases found from a previous run. Reply `reuse` to skip analysis and run with the existing JSON, or `regenerate` to redo full analysis."
  - **reuse** → skip Steps 1.5–2 and jump to Step 3 (checkpoint) using the existing JSON
  - **regenerate** → continue normally
- If it **does not exist**: continue normally.

### Step 1.5 — Jira Acceptance Criteria (Conditional)

**SKIP this step entirely if `JIRA_API_TOKEN` or `JIRA_USERNAME` is not set** — set `jira_ac_context = null` and proceed silently to Step 2.

**Only execute if both `JIRA_API_TOKEN` and `JIRA_USERNAME` are present in the environment.** Ask the user:

> "Do you have a Jira story for this model? If so, paste the issue ID (e.g. `PROJ-1234`) or paste the acceptance criteria directly. This helps generate test cases that cover your story's Definition of Done."
> *(Press Enter to skip and generate tests from SQL analysis only.)*

**If the user provides a Jira issue ID:**

Resolve the credentials and make the Jira REST API call using `skills/clients/jira.py` (Catalyst's shared Jira client — handles retries, rate limiting, and TLS via `REQUESTS_CA_BUNDLE`):

```python
import os, sys, json
from pathlib import Path

# Locate skills/ root relative to SKILL_DIR (parent of this SKILL.md)
skill_dir = Path("<SKILL_DIR>")          # substitute the actual SKILL_DIR path
repo_root = skill_dir.parents[1]         # skills/dbt-unit-test -> skills -> repo root
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from skills.clients.jira import JiraClient

base_url  = os.environ.get("JIRA_URL", "https://capitalgroup.atlassian.net")
username  = os.environ.get("JIRA_USERNAME", "")
api_token = os.environ.get("JIRA_API_TOKEN", "")

if not api_token:
    raise EnvironmentError("JIRA_API_TOKEN not set — see Step 0 to configure")
if not username:
    raise EnvironmentError("JIRA_USERNAME not set — see Step 0 to configure")

client = JiraClient(base_url=base_url, username=username, api_token=api_token)

# Fetch issue; customfield_10170 is the dedicated AC field in Capital Group Jira.
# Falls back to description if the AC field is absent or is a placeholder.
ac_field = os.environ.get("JIRA_ACCEPTANCE_CRITERIA_FIELD_ID", "customfield_10170")
issue = client.get_issue("<ISSUE_ID>", fields=["description", "summary", "comment", ac_field])
# Extract AC from customfield_10170, falling back to description
```

**Execution note:** Always write this script to a temp file and execute it with
`python3 /tmp/dbt_test_jira_fetch.py` rather than using `python3 -c "..."` inline.
Multi-line inline Python with mixed quotes causes shell quoting errors on macOS zsh.

1. Extract all `Given / When / Then` or bullet-point AC items from `customfield_10170`
   (the dedicated AC field in Capital Group Jira). Fall back to `description` if
   `customfield_10170` is absent or contains only a placeholder like
   `'See Acceptance Criteria for details'`.
2. Store the extracted AC text as `jira_ac_context` — pass it to Step 2

**If `JIRA_API_TOKEN` or `JIRA_USERNAME` is missing when the user provides a Jira ID:**
- Do not attempt the API call
- Tell the user: "`JIRA_API_TOKEN` or `JIRA_USERNAME` is not set. Please follow Step 0 to add both, then retry — or paste your acceptance criteria directly."

**If the user pastes AC text directly:**
- Use it as-is as `jira_ac_context` (no token needed)

**If the user skips:**
- Set `jira_ac_context = null` and proceed — test generation will be SQL-analysis-only

---

### Step 2 — Analyse + Generate (Single LLM Pass)

Combine SQL analysis and test-case generation in **one response** to eliminate the token round-trip of outputting a full analysis and then re-reading it as input.

0. **Read** `prompts/analyze_model.md`, `prompts/generate_tests.md`, and `prompts/seed_rules.md` using `read_file`. These files contain the authoritative rules for analysis and test-case generation — do NOT proceed without reading them first.
1. **Internally** apply `prompts/analyze_model.md` as chain-of-thought — work through all 7 sections in reasoning but do **not** output the full analysis to the user. Use the engine analyzer output from Step 1 as the authoritative column reference.
2. **Immediately** apply `prompts/generate_tests.md` (with seed rules from `prompts/seed_rules.md`) to produce the test cases JSON.
3. **Output to the user:**
   - A brief model summary (≤5 bullet points: key CTEs, join types, output column count, notable business logic, Jira AC coverage if applicable)
   - The complete JSON `test_cases` array

Target 8–25 test cases with non-redundant coverage:
- Happy path (≥1 per major CTE/JOIN path)
- NULL handling per nullable join key or COALESCE expression
- Each major CASE WHEN branch
- CAST / type conversion edge cases
- dl_current_indicator filtering (Y vs N)
- Date-range boundary conditions
- Empty output scenarios
- Aggregate / GROUP BY correctness
- ≥1 dedicated TC per Jira AC item (if `jira_ac_context` available), tagged `jira_ac`

```json
{
  "test_cases": [
    {
      "test_id": "TC001",
      "description": "...",
      "category": "transformation|null_check|dedup|cast|filter|join",
      "input_scenario": "...",
      "expected_behavior": "...",
      "input_data": { "<table_name>": [{"col": "val"}] },
      "expected_output": [{"output_col": "val"}],
      "pandas_query": "output_col == 'val'",
      "tags": ["null_handling"]
    }
  ]
}
```

### Step 3 — Checkpoint

**PAUSE and present a summary table before proceeding:**

```
Model:    <model_name>
TCs:      <count> test cases

| ID    | Category       | Description                        |
|-------|----------------|------------------------------------|
| TC001 | transformation | Happy path — full join, USD output |
| TC002 | null_check     | NULL listing_uid — LEFT JOIN miss  |
| ...   | ...            | ...                                |
```

Ask the user two questions in a single message:

1. **Executor choice** — which executor should be used to run the tests?
   - `pandas` — fast structural check (no JVM required). Validates seed-data wiring and column presence but **does not execute SQL transforms** (CAST, COALESCE, CASE WHEN assertions are skipped). Use for rename-only models or a quick smoke test.
   - `pyspark` — full SQL fidelity; evaluates every transform, CAST, and CASE WHEN. Required for integration models with business logic. Requires standalone `pyspark>=3.4.0` (not `databricks-connect`).

2. **Proceed confirmation** — confirm whether to proceed with the `<count>` generated test cases, adjust them, or cancel.

Wait for the user's reply. Store the executor answer as `chosen_executor` (default: `pandas` if the user does not specify).

- **proceed / yes** → continue to Step 4 using `chosen_executor`
- **adjust** → user can edit individual test cases or change the executor choice, then re-confirm
- **cancel** → stop; JSON is not saved

### Step 4 — Save Test Cases JSON

Save the JSON produced in Step 2 to:

```
workspace/dbt-unit-test/<model_name>/<model_name>_test_cases.json
```

Create the directory if it does not exist.

### Step 5 — Execute Pipeline

Run the helper script to trigger seed fixing, pytest script generation, test execution, and report generation:

**Path resolution:** Use `SKILL_DIR` derived from this SKILL.md's absolute path (see Step 1). Do not use relative paths or search for the script.

```bash
# SKILL_DIR = parent directory of this SKILL.md file (e.g. /path/to/catalyst/skills/dbt-unit-test)
# chosen_executor = value selected by user at Step 3 ("pandas" or "pyspark")
python "${SKILL_DIR}/scripts/run_from_json.py" \
    --json workspace/dbt-unit-test/<model_name>/<model_name>_test_cases.json \
    --executor <chosen_executor> \
    --project-root <workspace_root>
```

This script:
1. Applies deterministic seed post-processing fixes (10+ seed rules)
2. Renders the Jinja2 pytest script
3. Executes pytest with the chosen executor (parallel via pytest-xdist if installed)
4. Generates `<model_name>_results.xml` and `<model_name>_report.md`

> **PySpark environment note:** PySpark requires a standalone `pyspark` installation (not `databricks-connect`). If PySpark fails with `RuntimeError: Only remote Spark sessions … Databricks Connect`, re-run with `--executor pandas` instead.

### Step 6 — Show Results

After execution, report the outcome:

```
✅ ALL TESTS PASSED  / ❌ SOME TESTS FAILED  / ⚠️ PARTIAL  / ⏭ SKIPPED

Passed:   <n> / <total>
Skipped:  <n> / <total>   ← ⚠️ PARTIAL = some passed + some skipped; ⏭ SKIPPED = all skipped
Failed:   <n> / <total>
Report:   workspace/dbt-unit-test/<model_name>/<model_name>_report.md
Script:   workspace/dbt-unit-test/<model_name>/test_<model_name>_ai_generated.py
JSON:     workspace/dbt-unit-test/<model_name>/<model_name>_test_cases.json
```

If `Skipped > 0` and the executor was `pandas`, note: *"Transform assertions were skipped — re-run with `--executor pyspark` to validate CAST / COALESCE / CASE WHEN logic."*

If tests fail, read `<model_name>_report.md` and summarise the failing assertions
with the most likely root cause (seed data gap, wrong expected value, CASE WHEN
branch mismatch, etc.) and suggest a fix.

---

## Error Handling

| Error | Resolution |
|---|---|
| Model SQL not found | Ask user to confirm model name and project root |
| PySpark not installed | Re-run with `--executor pandas` (default) or install PySpark |
| PySpark raises `RuntimeError: Only remote Spark sessions … Databricks Connect` | The venv contains `databricks-connect` instead of standalone PySpark. Re-run with `--executor pandas` — do not attempt to install pyspark on top of databricks-connect |
| All TCs produce 0 rows | Apply S8 (CTE transitive dependency) — trace chain and re-seed base CTE |
| AMBIGUOUS_REFERENCE in Spark | Multi-table column name clash — check seed column uniqueness |
| JSON parse error from agent output | Re-generate Step 2 output in strict JSON mode |
| JUnit XML missing | pytest did not run; check Python environment and dbt-unit-test install |
| `JIRA_API_TOKEN` not set | Step 1.5 is silently skipped; tests generated from SQL only. If user mentions a Jira ID, show the setup guide from Step 0. |
| `JIRA_USERNAME` not set | Same as above — Step 1.5 is silently skipped. If user mentions a Jira ID, prompt them to set `JIRA_USERNAME` alongside `JIRA_API_TOKEN`. |
| Jira API returns 401 Unauthorized | Token is incorrect or expired — re-generate at id.atlassian.com and re-export |
| Jira API returns 403 Forbidden | User lacks permission for the issue — ask them to paste AC directly |
| Jira API returns 404 Not Found | Issue ID does not exist — ask user to verify the issue key |

---

## Next Steps

After a successful run:
- Review `<model_name>_report.md` for assertion-level detail
- Add failing TCs to Jira acceptance criteria for the model's ticket
- Re-run with `python "${SKILL_DIR}/scripts/run_from_json.py" --json <path> --executor pandas` after model SQL changes to regression-test
