# RS-LOG: Logging

tracing crate usage, structured fields, and instrumentation.

## RS-LOG-001 — Use the `tracing` crate

**Severity:** error
**Since:** v0.1.0
**Linter:** Clippy `print_stdout`, `print_stderr`

**Decision.** All logging uses `tracing`. Never `log`, `println!`, or
`eprintln!` in production code.

**Why.** `tracing` supports structured fields, spans, and log levels. It
integrates with log aggregation. `println!` does not.

**Exception.** CLI tools that intentionally print to stdout for piping.

## RS-LOG-002 — Structured fields, not interpolation

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Pass values as structured fields, not interpolated into
the message string.

**Examples.**
```rust
// ✓
info!(table = %table_name, rows = row_count, "profiling complete");

// ✗
info!("profiling complete for {} ({} rows)", table_name, row_count);
```

## RS-LOG-003 — `#[instrument]` on functions for span creation

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Annotate non-trivial async functions with
`#[tracing::instrument]` to create spans automatically.

**Examples.**
```rust
#[instrument(skip(client), fields(table = %table_name))]
async fn profile_table(client: &Client, table_name: &str) -> Result<Profile> {
    debug!("starting profiling");
    let result = client.query(table_name).await?;
    info!(columns = result.len(), "profiling complete");
    Ok(result)
}
```

### Documentation
