# Rust Coding Standards

## Governing Authority

These standards are derived from and comply with:

- [The Rust Programming Language (The Book)](https://doc.rust-lang.org/book/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Clippy Lint Reference](https://rust-lang.github.io/rust-clippy/master/)
- [RFC 430 — Naming Conventions](https://github.com/rust-lang/rfcs/blob/master/text/0430-finalizing-naming-conventions.md)
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) (unsafe code reference)
- [Rust Reference](https://doc.rust-lang.org/reference/)

Where this document is silent, the Rust API Guidelines apply.

## Rule Format

Same shape as the rest of RFD 0008:

```
### RS-{CATEGORY}-{NNN} — one-line directive

**Severity:** error | warning | advisory
**Since:** v0.1.0
**Linter:** clippy/rustc rules, or "advisory" if not auto-enforced

**Decision.** What to do.
**Why.** Rationale.
**Exception.** When the rule does not apply, or "None."
**Examples.** ✓ good / ✗ bad code.
```

Categories: `VERSION`, `IMPORT`, `NAMING`, `TYPE`, `ERROR`, `IDIOM`, `ASYNC`,
`LOG`, `DOC`, `TEST`, `SECURITY`, `CARGO`, `PERF`.

## Tooling

### Formatter: rustfmt

Every repository MUST contain a `rustfmt.toml` at the repo root:

```toml
# rustfmt.toml
edition = "2021"
max_width = 100
tab_spaces = 4
use_small_heuristics = "Max"
imports_granularity = "Crate"
group_imports = "StdExternalCrate"
reorder_imports = true
reorder_modules = true
newline_style = "Unix"
format_code_in_doc_comments = true
```

### Linter: Clippy

Clippy is mandatory on every commit. CI MUST fail on Clippy warnings.

```toml
# Cargo.toml (workspace root)
[workspace.lints.clippy]
unwrap_used = "deny"
expect_used = "deny"
panic = "deny"
todo = "deny"
unimplemented = "deny"
dbg_macro = "deny"
print_stdout = "deny"
print_stderr = "deny"
large_futures = "warn"

needless_pass_by_value = "warn"
cloned_instead_of_copied = "warn"
flat_map_option = "warn"
implicit_clone = "warn"
inconsistent_struct_constructor = "warn"
inefficient_to_string = "warn"
manual_let_else = "warn"
map_unwrap_or = "warn"
redundant_closure_for_method_calls = "warn"
semicolon_if_nothing_returned = "warn"
str_to_string = "warn"
trivially_copy_pass_by_ref = "warn"
unnested_or_patterns = "warn"
unused_self = "warn"
used_underscore_binding = "warn"

[workspace.lints.rust]
unsafe_code = "deny"
unused_must_use = "deny"
missing_docs = "warn"
```

### Dependency Auditing: cargo-deny

Every workspace MUST include a `deny.toml`:

```toml
[advisories]
vulnerability = "deny"
unmaintained = "warn"

[licenses]
unlicensed = "deny"
allow = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unicode-3.0"]

[bans]
multiple-versions = "warn"
wildcards = "deny"

[sources]
unknown-registry = "deny"
unknown-git = "deny"
```

CI MUST run `cargo deny check` on every PR.

---

## Rule index

Rules are split by category. Each category file has the rules in numeric order.

- [`async.md`](async.md) — **Async** (6 rules). tokio runtime, structured concurrency, and async-safety rules.
- [`cargo.md`](cargo.md) — **Cargo** (3 rules). Cargo.toml conventions and workspace inheritance.
- [`doc.md`](doc.md) — **Documentation** (7 rules). rustdoc requirements: errors, panics, examples, module docs.
- [`error.md`](error.md) — **Error Handling** (8 rules). thiserror, anyhow, and the `?` propagation pattern.
- [`idiom.md`](idiom.md) — **Idioms** (8 rules). Combinators, iterator chains, builders, and ownership patterns.
- [`import.md`](import.md) — **Imports** (3 rules). Import grouping per workspace rustfmt.
- [`log.md`](log.md) — **Logging** (3 rules). tracing crate usage, structured fields, and instrumentation.
- [`naming.md`](naming.md) — **Naming** (5 rules). Identifier casing per RFC 430 and API Guidelines.
- [`perf.md`](perf.md) — **Performance** (5 rules). Allocation, cloning, async sharing, and benchmark discipline.
- [`security.md`](security.md) — **Security** (9 rules). unsafe gates, secret handling, sqlx macros, dependency auditing.
- [`test.md`](test.md) — **Testing** (8 rules). Unit/integration tests, sqlx::test, snapshot testing.
- [`type.md`](type.md) — **Types** (6 rules). Standard derive macros and trait selection.
- [`version.md`](version.md) — **Version** (3 rules). Toolchain pinning and MSRV policy.
