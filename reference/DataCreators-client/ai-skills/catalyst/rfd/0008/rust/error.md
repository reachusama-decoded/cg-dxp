# RS-ERROR: Error Handling

thiserror, anyhow, and the `?` propagation pattern.

## RS-ERROR-001 — Never `.unwrap()` or `.expect()` outside tests

**Severity:** error
**Since:** v0.1.0
**Linter:** Clippy `unwrap_used`, `expect_used`

**Decision.** Both are denied at the workspace level. Every `Option` and
`Result` is handled explicitly. No `#[allow]` overrides without a senior
review and a `// SAFETY:` comment justifying the invariant.

**Why.** A panic in production tears down the request, the task, or in
async code potentially the runtime.

**Exception.** Tests are exempt via per-crate Clippy configuration.

**Examples.**
```rust
// ✓
let user = users
    .get(&user_id)
    .ok_or_else(|| CatalogError::TableNotFound { schema: schema.into(), table: table.into() })?;

// ✗
let user = users.get(&user_id).unwrap();
```

## RS-ERROR-002 — Library crates use `thiserror`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Public library error types derive `thiserror::Error`.

**Why.** Compiler-verified `Display`, `Error`, and `From`
implementations. Consistent across the workspace.

**Examples.**
```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum CatalogError {
    #[error("table '{schema}.{table}' not found")]
    TableNotFound { schema: String, table: String },

    #[error("connection to catalog '{catalog}' failed")]
    ConnectionFailed {
        catalog: String,
        #[source]
        source: sqlx::Error,
    },

    #[error("query timed out after {timeout_secs}s")]
    QueryTimeout { timeout_secs: u64 },
}
```

## RS-ERROR-003 — Application crates use `anyhow`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Binaries, CLI tools, and services use `anyhow::Result` for
`main()`, request handlers, and top-level orchestration.

**Why.** `anyhow::Error` provides backtraces, context chaining, and
downcasting without hand-rolling an aggregate error type.

## RS-ERROR-004 — Never `Box<dyn Error>`; use `anyhow::Error`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't return `Box<dyn Error>` from a function. Use
`anyhow::Error` (or `anyhow::Result<T>`).

**Why.** `anyhow::Error` is strictly more capable: backtraces, chained
context, downcasting.

## RS-ERROR-005 — Use `?` for propagation; don't match-and-rewrap

**Severity:** error
**Since:** v0.1.0
**Linter:** Clippy `question_mark`

**Decision.** Use `?` to propagate errors. Don't `match` on `Result`
just to re-wrap and return.

**Why.** That's exactly what `?` and `From` impls are for.

**Examples.**
```rust
// ✓
let content = tokio::fs::read_to_string(path).await?;

// ✗
let content = match tokio::fs::read_to_string(path).await {
    Ok(c) => c,
    Err(e) => return Err(anyhow::anyhow!("failed to read: {}", e)),
};
```

## RS-ERROR-006 — Add context at domain boundaries

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `anyhow::Context::context` or `with_context` to add
domain-meaningful context when crossing module or service boundaries.

**Why.** Bare error messages from low-level crates ("file not found")
don't tell the operator which file, in which subsystem.

**Examples.**
```rust
let content = tokio::fs::read_to_string(path)
    .await
    .with_context(|| format!("failed to read config from {}", path.display()))?;

let config: AppConfig = toml::from_str(&content)
    .with_context(|| format!("invalid TOML in {}", path.display()))?;
```

## RS-ERROR-007 — Domain error types are enums, not structs

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Each variant represents a distinct failure mode the caller
may want to match on.

**Why.** Pattern matching on a struct only checks one shape. An enum
encodes "this can fail in N specific ways" into the type.

## RS-ERROR-008 — Convert error types via `#[from]` on enum variants

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `thiserror`'s `#[from]` to derive `From`
implementations between error types so `?` works without manual mapping.

**Examples.**
```rust
#[derive(Debug, Error)]
pub enum ServiceError {
    #[error(transparent)]
    Catalog(#[from] CatalogError),

    #[error(transparent)]
    Auth(#[from] AuthError),

    #[error("internal error")]
    Internal(#[from] anyhow::Error),
}

async fn handle_request(req: Request) -> Result<Response, ServiceError> {
    let table = catalog.lookup(&req.table_name)?;  // CatalogError -> ServiceError
    let token = auth.validate(&req.token)?;         // AuthError -> ServiceError
    Ok(build_response(table))
}
```

### Idioms
