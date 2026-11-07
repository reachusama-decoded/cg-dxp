# RS-DOC: Documentation

rustdoc requirements: errors, panics, examples, module docs.

## RS-DOC-001 — All public items have rustdoc

**Severity:** warning
**Since:** v0.1.0
**Linter:** rustc `missing_docs` (warn at workspace; deny for external crates)

**Decision.** Every public item has a rustdoc comment.

**Why.** Public surface is the contract. The compiler can verify the
warning is present.

## RS-DOC-002 — `///` for items, `//!` for module/crate

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `///` for item docs and `//!` for module/crate-level
docs. Never `/** */` block comments for documentation.

**Why.** Convention. `/** */` is parseable but never used.

## RS-DOC-003 — First line is a third-person summary

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Per API Guidelines C-ITEM-DOC, the first line is a single
sentence in third person. "Returns the..." not "Return the...".

**Examples.**
```rust
/// Returns the column statistics for the given table.
pub fn columns(&self) -> &[ColumnStat] { ... }
```

## RS-DOC-004 — `# Errors` section on `Result`-returning functions

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Document every error variant the caller should expect.

**Why.** A function that returns `Result<T, E>` where E is an enum
should explain which variants are produced and under what conditions.

## RS-DOC-005 — `# Panics` section if the function can panic

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Document panic conditions explicitly. Production code
should not panic, but if a precondition violation panics (index out of
bounds), say so.

## RS-DOC-006 — `# Examples` section on public API entry points

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory (rustdoc tests verify they compile)

**Decision.** Public API functions have at least one example. Use `# `
prefix to hide setup lines from rendered docs.

**Why.** Examples are tested by `cargo test --doc`, so they don't rot.

**Examples.**
```rust
/// Profiles a table's columns.
///
/// # Examples
///
/// ```rust
/// # use catalog_client::{Client, ProfileOptions};
/// # async fn example() -> anyhow::Result<()> {
/// let client = Client::new("https://catalog.internal").await?;
/// let profile = client
///     .profile_table("investments", "curated", "orders", ProfileOptions::default())
///     .await?;
/// # Ok(())
/// # }
/// ```
```

## RS-DOC-007 — Module-level docs on every public module

**Severity:** warning
**Since:** v0.1.0
**Linter:** rustc `missing_docs`

**Decision.** Every `lib.rs` and every public module has a `//!` doc
comment explaining its purpose.

### Testing
