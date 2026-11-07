# RS-TEST: Testing

Unit/integration tests, sqlx::test, snapshot testing.

## RS-TEST-001 — Unit tests in `#[cfg(test)]`; integration in `tests/`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Unit tests live in the same source file under
`#[cfg(test)] mod tests`. Cross-module or end-to-end tests live in
`tests/`.

## RS-TEST-002 — Test naming `test_<scenario>_<expected>`

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Test functions describe behavior, not sequence number.

**Examples.**
```rust
// ✓
#[test]
fn parse_severity_from_valid_string_returns_variant() { ... }

#[test]
fn parse_severity_from_invalid_string_returns_error() { ... }

// ✗
#[test]
fn test_1() { ... }
```

## RS-TEST-003 — `#[tokio::test]` for async tests

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Async tests use `#[tokio::test]`. Never manually build a
runtime in tests.

## RS-TEST-004 — `#[sqlx::test]` for database tests

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Database tests use `#[sqlx::test]`, which provides a
transactional test database that rolls back after each test.

**Why.** No cleanup logic needed; tests are isolated by construction.

## RS-TEST-005 — Tests may use `.unwrap()`/`.expect()`

**Severity:** advisory
**Since:** v0.1.0
**Linter:** Clippy per-crate allow

**Decision.** Tests are exempt from RS-ERROR-001 via per-crate Clippy
configuration or module-level `#[allow]`.

**Examples.**
```rust
#[cfg(test)]
#[allow(clippy::unwrap_used, clippy::expect_used)]
mod tests {
    use super::*;
    // ...
}
```

## RS-TEST-006 — No `#[ignore]` without a tracking issue

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Every `#[ignore]` has a comment linking to a tracking issue.

**Examples.**
```rust
#[ignore = "https://github.com/org/repo/issues/123 — flaky on Windows CI"]
#[test]
fn integration_test_xyz() { ... }
```

## RS-TEST-007 — `assert_eq!`/`assert_ne!` over raw `assert!`

**Severity:** warning
**Since:** v0.1.0
**Linter:** Clippy `bool_assert_comparison`

**Decision.** Use `assert_eq!` and `assert_ne!` for equality. They print
both values on failure. Use `assert!(matches!(...))` for enum variant
matching.

**Examples.**
```rust
// ✓
assert_eq!(severity, Severity::High);
assert!(matches!(result, Err(CatalogError::TableNotFound { .. })));

// ✗
assert!(severity == Severity::High);
```

## RS-TEST-008 — Snapshot tests use `insta`

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** For complex output (rendered templates, JSON, SQL), use
`insta::assert_snapshot!` or `insta::assert_json_snapshot!`.

### Security
