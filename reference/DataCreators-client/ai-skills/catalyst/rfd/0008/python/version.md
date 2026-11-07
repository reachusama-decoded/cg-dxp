# PY-VERSION: Version

Python version policy and runtime expectations.

## PY-VERSION-001 — New projects use Python 3.12+

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory (enforced via `pyproject.toml` `requires-python`)

**Decision.** Set `requires-python = ">=3.12"` for all new projects.

**Why.** 3.12 brings PEP 695 type parameter syntax, faster startup, better
error messages, and is the floor for current dependency support.

**Exception.** None for new projects.

## PY-VERSION-002 — Existing projects target 3.12 on next major update

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Existing projects on 3.10 or 3.11 are acceptable but must
target 3.12 on their next major release.

**Why.** Keeps the platform on a single supported runtime over time without
forcing immediate migration.

**Exception.** Projects deprecated or sunsetting before their next major
release.

## PY-VERSION-003 — No Python 2 syntax

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `UP` rules

**Decision.** No Python 2 syntax. No `__future__` imports for `print` or
`division`. No `u""` string prefixes. No `xrange`, `iteritems`, etc.

**Why.** Python 2 reached end-of-life in 2020. Modernization is non-negotiable.

**Exception.** None.

### Imports
