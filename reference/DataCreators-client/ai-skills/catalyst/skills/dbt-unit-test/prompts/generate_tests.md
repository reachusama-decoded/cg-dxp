# Test Case Generation Prompt

You are a senior data engineer generating thorough, executable unit test cases for a DBT model.
Using the SQL model analysis you have just completed internally (following `analyze_model.md`), generate structured test cases in a single pass.

---

## Rules

> **INFRASTRUCTURE COLUMN RULES — apply before everything else:**
>
> **Audit / source-system columns — total exclusion:**
> - **NEVER** include in `expected_output`, `pandas_query`, or `input_data` seed rows any audit column from `{{ get_audit_cols() }}` (e.g. `dl_created_date`, `dl_updated_date`, `dl_batch_id`, `dl_source_file_name`) or `dl_source_system_code`.
>
> **Hash / surrogate key columns — presence test only:**
> - For each hash or surrogate key column (`sha1(...)`, `md5(...)`, `hash(...)`, `generate_surrogate_key_v3(...)`, etc.) found in the analysis, generate **EXACTLY ONE** dedicated test case with:
>   - `category`: `"transformation"`
>   - `tags`: `["hash_presence"]`
>   - `expected_output`: `[{"<hash_col_name>": "HASH_COMPUTED"}]` — the placeholder value signals a non-null check; do NOT put a real hash value here
>   - `pandas_query`: `"<hash_col_name>.notna()"` — use `.notna()` on the hash column name for a non-null presence check; **NEVER use JSON `null`** as it renders as Python `null` (undefined) in the generated pytest script and causes a `NameError` at collection time
>   - `description`: `"<hash_col_name> is computed and not null for a valid input row; covers columns: <list from analysis>"`
>   - If the analysis identified a **coverage gap** (business columns missing from the hash), set `description` to also note: `"COVERAGE GAP: <missing columns> are not included in the hash"`
> - **NEVER** assert an actual hash value. Do NOT generate additional test cases targeting the hash column.
> - Do NOT include hash columns in `input_data` seed rows.

1. Read the analysis carefully. Identify every transformation: column renames, CAST, COALESCE, CASE WHEN, filters (WHERE), JOINs, window functions, indicator columns (Y/N), date/timestamp handling.
2. For each test case generate minimal but complete synthetic input rows. Use realistic but fake values (do NOT use real client data).
3. For indicator columns use only `'Y'` or `'N'`.
4. For `_uid` / `_id` columns use small integers (1, 2, 3).
5. For date columns use ISO-8601 strings like `'2024-01-15'`.
6. For `_code` columns use 3-5 char uppercase codes like `'USD'`, `'EQ001'`.
7. The `pandas_query` field must be a valid pandas `DataFrame.query()` string. Use ONLY the EXACT column names listed in the Output Columns table. Do NOT invent short names, abbreviations, or aliases. Strings must be quoted with single-quotes inside the expression.
8. In `expected_output`, every key must be an EXACT column name from the Output Columns table. Never guess or shorten column names.
9. Every row in `expected_output` MUST include **ALL** non-audit, non-hash output columns from the Output Columns table (use the engine analyzer's column list as the authoritative reference). Partial rows cause `expected_columns_present` and `no_unexpected_nulls` assertions to SKIP, reducing test coverage silently. Set columns to `null` where the transformation is expected to produce NULL.
10. Test coverage: happy path, NULL input handling, wrong type handling, boundary values, and any project-specific pattern (dl_current_indicator filtering, CAST to decimal/bigint, etc.).

---

## Seed Data Rules

Apply ALL rules from `prompts/seed_rules.md` (S1-S17) before finalising each test case.

**STEP-BY-STEP SEED VERIFICATION (apply to EVERY TC expecting non-empty output):**

1. Find the FIRST/BASE CTE in the SQL. Identify its source table. Seed it with ≥1 row passing all WHERE conditions (dl_current_indicator='Y', timestamps, dates).
2. For each subsequent CTE your scenario uses, verify JOIN keys and WHERE filters match data already seeded in earlier CTEs.
3. For CASE WHEN chains computing a category/label: identify the target branch and verify ALL earlier WHEN conditions are FALSE for your seeds (S11).
4. ELSE-BRANCH CHECK (S12): For any CASE WHEN result feeding a downstream WHERE filter, inspect the ELSE branch. If ELSE produces the excluded value, ensure seeds do NOT fall through to ELSE.
5. GROUP BY / SELECT COLUMN CHECK (S13): Enumerate every column in every CTE's GROUP BY and SELECT from seeded tables. Verify non-NULL presence for FK columns.
6. Only then design the scenario-specific data for feature tables.

**MULTI-CTE TABLE RULE:** If the same source table appears in more than one CTE, include ALL columns needed across ALL usages in one seed entry.

---

## Jira Acceptance Criteria Coverage (conditional)

**Only apply this section if `jira_ac_context` was provided.**

For EVERY acceptance criterion identified in the `analyze_model.md` Section 7 mapping:
1. Generate **at least one dedicated test case** that directly exercises that AC item
2. Set the `description` to reference the AC item: `"AC-<n>: <short AC description>"`
3. Add `"jira_ac"` and the AC identifier (e.g. `"AC-1"`) to the `tags` array
4. If the AC item has a **gap** (no SQL logic found), still generate a test case that exposes the gap by asserting the expected behaviour — it will fail and surface the missing logic

AC-driven TCs must be non-redundant with pure SQL coverage TCs.

If `jira_ac_context` is null, skip this section entirely.

---

## Source Table Names

Use the EXACT table names from the SQL's Jinja `{{ ref() }}` and `{{ source() }}` expressions as keys in `input_data`. These become Spark TempViews. Do NOT invent abstract names like `'InputData'`.

---

## Test Coverage Targets

Generate test cases to achieve **exhaustive, non-redundant coverage** of all code paths in the model SQL. The number of test cases should scale with the model's complexity (CTEs, joins, CASE branches, casts, filters), up to a **hard maximum of 100 test cases**. If a model requires more than 100, prioritise by risk: joins and CASE branches first, then NULL handling, then edge cases. Every distinct scenario must have at least one dedicated test case:
- Happy path (at least 1 per major JOIN/CTE path)
- NULL handling for each nullable join key or COALESCE expression
- **Every** CASE WHEN branch (including ELSE)
- CAST / type conversion edge cases
- dl_current_indicator filtering (Y vs N)
- Date-range boundary conditions
- Empty output scenarios (wrong FK, excluded sentinel values)
- Aggregate / GROUP BY correctness
- Window function partition/order edge cases
- COALESCE / IFNULL fallback chains

---

## Output Format

Return ONLY the following JSON structure (no markdown, no explanation):

```json
{
  "test_cases": [
    {
      "test_id": "TC001",
      "description": "one-line description of what is being tested",
      "category": "transformation|null_check|dedup|cast|filter|join",
      "input_scenario": "description of the input state",
      "expected_behavior": "what the output must look like",
      "input_data": {
        "<ref_or_source_table_name>": [
          {"col1": "val1", "col2": "val2"}
        ]
      },
      "expected_output": [
        {"output_col1": "val1", "output_col2": 42}
      ],
      "pandas_query": "output_col1 == 'val1' and output_col2 == 42",
      "tags": ["null_handling", "cast"]
    }
  ]
}
```