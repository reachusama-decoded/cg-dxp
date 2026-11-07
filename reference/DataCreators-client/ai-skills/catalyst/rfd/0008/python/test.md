# PY-TEST: Testing

pytest framework, naming, coverage, fixtures, and mocking discipline.

## PY-TEST-001 — pytest only

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Tests use pytest. No `unittest.TestCase` subclasses.

**Why.** Single test framework across the platform. pytest fixtures and
parametrize are strictly more capable than `unittest`.

**Exception.** Migration from existing `unittest` suites — convert
incrementally, but no new `TestCase` classes.

## PY-TEST-002 — Test file naming `test_{module}.py`

**Severity:** error
**Since:** v0.1.0
**Linter:** pytest discovery

**Decision.** Test files are named `test_<module>.py` and live in
`tests/` mirroring the source layout, or alongside source as
`test_<module>.py`.

**Why.** pytest collection convention.

## PY-TEST-003 — Test function naming describes the scenario

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Test functions are named `test_<scenario>` where the
scenario is a behavior, not a sequence number. Use snake_case sentence
fragments.

**Why.** Test names appear in failure output. `test_profile_raises_on_missing_table`
tells the reviewer what broke; `test_1` does not.

## PY-TEST-004 — 80% coverage on `core/` and `clients/`

**Severity:** warning
**Since:** v0.1.0
**Linter:** coverage gate in CI

**Decision.** Branch coverage greater than or equal to 80% on `core/` and
`clients/` packages.

**Why.** These are the libraries other code depends on. Skills and
scripts are evaluated by eval, not unit tests, so they have no fixed
threshold.

**Exception.** Documented exclusions in `.coveragerc`.

## PY-TEST-005 — No `assert True` or `assert False`

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `B011`

**Decision.** Assert specific values. `assert True` always passes; `assert
False` always fails — neither tests anything.

**Why.** A test that asserts a tautology has no signal.

## PY-TEST-006 — Fixtures over setup/teardown

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use pytest fixtures in `conftest.py` for shared setup. Don't
use `setUp`/`tearDown`-style classes.

**Why.** Fixtures are composable, scoped, and lazy.

## PY-TEST-007 — Mock at boundaries only

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Mock external clients (HTTP, database, message broker) and
filesystem. Don't mock internal functions or methods within the package
under test.

**Why.** Internal mocks test the mock, not the code. They lock the
implementation in place and break on legitimate refactors.

### Security
