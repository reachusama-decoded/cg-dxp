# Python Coding Standards

## Governing Authority

These standards are derived from and comply with:

- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 / 526 — Type Hints](https://peps.python.org/pep-0484/)
- [PEP 585 — Type Hinting Generics in Standard Collections](https://peps.python.org/pep-0585/)
- [PEP 604 — Allow writing union types as `X | Y`](https://peps.python.org/pep-0604/)
- [PEP 612 — Parameter Specification Variables](https://peps.python.org/pep-0612/)
- [PEP 695 — Type Parameter Syntax](https://peps.python.org/pep-0695/) (3.12+)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

Where this document is silent, the Google Python Style Guide applies.

## Rule Format

Every rule below has the same shape:

```
### PY-{CATEGORY}-{NNN} — one-line directive

**Severity:** error | warning | advisory
**Since:** v0.1.0
**Linter:** linter rule codes, or "advisory" if not auto-enforced

**Decision.** What to do.
**Why.** Rationale.
**Exception.** When the rule does not apply, or "None."
**Examples.** good / bad code.
```

Rule IDs are stable and never reused. Categories: `VERSION`, `IMPORT`,
`NAMING`, `TYPE`, `DOC`, `ERROR`, `IDIOM`, `TEST`, `SECURITY`, `AIRFLOW`.

## Tooling

### Formatter and Linter: Ruff

Ruff is the **only** formatter and linter. Do not use Black, autopep8, yapf,
flake8, pylint, isort, pyflakes, bandit, or pyupgrade.

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors (PEP 8)
    "W",      # pycodestyle warnings (PEP 8)
    "F",      # pyflakes (undefined names, unused imports)
    "I",      # isort (import ordering per PEP 8)
    "N",      # pep8-naming (function, class, variable naming)
    "UP",     # pyupgrade (modernize to latest Python syntax)
    "B",      # flake8-bugbear (common bugs and design problems)
    "S",      # flake8-bandit (security vulnerabilities)
    "T20",    # flake8-print (no print() in production code)
    "SIM",    # flake8-simplify (simplifiable expressions)
    "TCH",    # flake8-type-checking (move imports to TYPE_CHECKING)
    "RUF",    # ruff-specific rules
    "ANN",    # flake8-annotations (enforce type annotations)
    "C4",     # flake8-comprehensions (unnecessary list/dict calls)
    "DTZ",    # flake8-datetimez (require timezone-aware datetimes)
    "PIE",    # flake8-pie (misc. lints)
    "PT",     # flake8-pytest-style (pytest best practices)
    "RET",    # flake8-return (unnecessary else after return)
    "ARG",    # flake8-unused-arguments
    "ERA",    # eradicate (commented-out code)
]
ignore = [
    "E501",   # line length — handled by formatter
    "ANN101", # missing type annotation for self
    "ANN102", # missing type annotation for cls
    "ANN401", # allow Any — challenge case-by-case in review
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",   # allow assert in tests
    "ANN",    # don't require annotations in tests
    "ARG",    # allow unused arguments in test fixtures
]
```

### Type Checker: pyright

```toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "basic"
reportMissingTypeStubs = false
reportUnknownMemberType = false
```

Projects may opt into `strict` mode. New projects are encouraged to start
strict.

---

## Rule index

Rules are split by category. Each category file has the rules in numeric order.

- [`airflow.md`](airflow.md) — **Airflow on Astronomer** (24 rules). Idempotency, retries, resourcing, scheduling, tagging, secrets, task atomicity, code organization, and the `assert_dag_compliant` structural test for paved-path DAGs (RFD 0011).
- [`doc.md`](doc.md) — **Documentation** (5 rules). Docstring requirements and Google docstring format.
- [`error.md`](error.md) — **Error Handling** (7 rules). Exception handling, propagation, and domain error types.
- [`idiom.md`](idiom.md) — **Idioms** (19 rules). Idiomatic patterns: iteration, formatting, paths, context managers, logging, datetimes.
- [`import.md`](import.md) — **Imports** (3 rules). Import grouping, ordering, and type-only import rules.
- [`naming.md`](naming.md) — **Naming** (3 rules). Identifier casing and naming conventions per PEP 8.
- [`security.md`](security.md) — **Security** (7 rules). Untrusted input, SQL injection, secret handling, deserialization.
- [`test.md`](test.md) — **Testing** (7 rules). pytest framework, naming, coverage, fixtures, and mocking discipline.
- [`type.md`](type.md) — **Types** (8 rules). Type annotations, modern syntax, and structural typing.
- [`version.md`](version.md) — **Version** (3 rules). Python version policy and runtime expectations.
