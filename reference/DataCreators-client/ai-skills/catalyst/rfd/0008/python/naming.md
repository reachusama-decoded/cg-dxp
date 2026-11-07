# PY-NAMING: Naming

Identifier casing and naming conventions per PEP 8.

## PY-NAMING-001 — Identifier casing per PEP 8

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `N`

**Decision.** Use the conventions in this table:

| Item | Convention | Example |
|------|-----------|---------|
| Modules | `snake_case` | `table_profile.py` |
| Packages | `snake_case` | `core/lineage/` |
| Classes | `UpperCamelCase` | `TableProfile` |
| Exceptions | `UpperCamelCase` + `Error` suffix | `DataProfilingError` |
| Functions | `snake_case` | `fetch_table_profile` |
| Methods | `snake_case` | `get_columns` |
| Module-level constants | `SCREAMING_SNAKE_CASE` | `MAX_BATCH_SIZE` |
| Variables | `snake_case` | `row_count` |
| Type variables | `UpperCamelCase` | `T`, `ResponseT` |
| Private | Leading double underscore | `__internal_cache` |
| Protected | Leading underscore | `_internal_cache` |
| Dunder | Double underscore | `__init__`, `__repr__` |

**Why.** PEP 8. Consistent across CG codebases reduces cognitive load.

**Exception.** Existing public APIs may keep historical casing — flag with
`# noqa: N802 (legacy public API)`.

## PY-NAMING-002 — No ambiguous single-character names

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `E741`

**Decision.** Never use `l` (lowercase L), `O` (uppercase O), or `I`
(uppercase I) as variable, parameter, or attribute names.

**Why.** PEP 8. Visually ambiguous with digits and other letters.

**Exception.** None.

## PY-NAMING-003 — No generic names for variables

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Avoid `data`, `info`, `temp`, `result`, `stuff`, `thing` as
variable names. Name what the variable contains.

**Why.** Generic names hide intent. `holdings` reads better than `data`;
`profile` reads better than `result`.

**Exception.** Throwaway names in narrow scopes.

### Typing
