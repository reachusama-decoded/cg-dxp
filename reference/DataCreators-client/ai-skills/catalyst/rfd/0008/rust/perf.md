# RS-PERF: Performance

Allocation, cloning, async sharing, and benchmark discipline.

## RS-PERF-001 — Prefer `&str` over `String` in parameters

**Severity:** warning
**Since:** v0.1.0
**Linter:** Clippy `needless_pass_by_value`

**Decision.** Accept borrowed data when ownership is not needed. Use
`impl AsRef<str>` for maximum flexibility.

## RS-PERF-002 — Avoid unnecessary cloning

**Severity:** warning
**Since:** v0.1.0
**Linter:** Clippy `implicit_clone`, `redundant_clone`

**Decision.** If a function needs owned data, take it by value and let
the caller decide whether to clone.

## RS-PERF-003 — `Vec::with_capacity` when size is known

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Pre-allocate when the final size is known or estimable.

## RS-PERF-004 — `Arc<T>` over `Clone` for large shared data in async

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When the same large value is read by multiple async
tasks, share via `Arc<T>` rather than cloning the data.

## RS-PERF-005 — Profile before optimizing

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `cargo flamegraph` or `criterion` benchmarks before
introducing complexity for performance. Do not introduce `unsafe` for
performance without benchmark evidence of meaningful improvement.
