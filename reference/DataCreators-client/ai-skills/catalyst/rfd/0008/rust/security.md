# RS-SECURITY: Security

unsafe gates, secret handling, sqlx macros, dependency auditing.

## RS-SECURITY-001 — `unsafe` is denied at workspace level

**Severity:** error
**Since:** v0.1.0
**Linter:** rustc `unsafe_code = "deny"`

**Decision.** No crate in the workspace can use `unsafe` without an
explicit `#[allow(unsafe_code)]`. Every `unsafe` block requires a
`// SAFETY:` comment justifying why the invariants hold.

**Why.** Most production code does not need `unsafe`. The friction is the
point — every use is reviewed.

**Examples.**
```rust
// ✓
#[allow(unsafe_code)]
// SAFETY: ptr is non-null and properly aligned because it was just
// allocated by Vec::as_mut_ptr(). Length is verified within bounds.
// The slice does not outlive the Vec.
unsafe {
    std::slice::from_raw_parts(ptr, len)
}

// ✗
#[allow(unsafe_code)]
unsafe {
    std::slice::from_raw_parts(ptr, len)
}
```

## RS-SECURITY-002 — Every `unsafe` block requires two-engineer review

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory (process gate)

**Decision.** Code review for an `unsafe` block requires approval from
two engineers, one of whom is a designated unsafe reviewer.

## RS-SECURITY-003 — Wrap secrets with the `secrecy` crate

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Sensitive values (passwords, tokens, keys) are typed as
`Secret<String>` (or appropriate secret type). Accessing requires
explicit `expose_secret()`.

**Why.** `Secret<T>` redacts itself in `Debug` output and does not
implement `Display`/`Serialize`, making accidental logging impossible.

**Examples.**
```rust
use secrecy::{ExposeSecret, Secret};

pub struct DatabaseConfig {
    pub host: String,
    pub port: u16,
    pub password: Secret<String>,
}

let conn_string = format!(
    "postgres://user:{}@{}:{}",
    config.password.expose_secret(),
    config.host,
    config.port,
);

tracing::debug!(?config, "connecting to database");
// password = Secret([REDACTED])
```

## RS-SECURITY-004 — Never hardcode secrets

**Severity:** error
**Since:** v0.1.0
**Linter:** `trufflehog` in CI

**Decision.** Load secrets from environment variables or a secret
manager. Never commit a token, password, or key.

## RS-SECURITY-005 — Always use `sqlx::query!` / `sqlx::query_as!`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use sqlx's compile-time-checked macros. Never `format!` or
string concatenation to build SQL.

**Why.** sqlx compile-time-verifies SQL against the database schema and
enforces parameterized queries. SQL injection is impossible at the call
site.

**Examples.**
```rust
// ✓
let profiles = sqlx::query_as!(
    TableProfile,
    "SELECT catalog, schema_name, table_name, row_count
     FROM table_profiles
     WHERE catalog = $1 AND schema_name = $2",
    catalog, schema,
)
.fetch_all(&pool)
.await?;

// ✗
let query = format!("SELECT * FROM table_profiles WHERE catalog = '{}'", catalog);
sqlx::query(&query).fetch_all(&pool).await?;
```

## RS-SECURITY-006 — Validate dynamic identifiers against an allowlist

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** SQL identifiers (column, table names) cannot be
parameterized. Validate user-supplied identifiers against a hard-coded
allowlist before interpolation.

**Examples.**
```rust
const ALLOWED_COLUMNS: &[&str] = &["catalog", "schema_name", "table_name", "row_count"];

fn validate_column(col: &str) -> Result<&str> {
    ALLOWED_COLUMNS
        .iter()
        .find(|&&c| c == col)
        .copied()
        .ok_or_else(|| anyhow::anyhow!("invalid column name: {}", col))
}
```

## RS-SECURITY-007 — `cargo audit` in CI; fail on medium+ severity

**Severity:** error
**Since:** v0.1.0
**Linter:** `cargo audit` job

**Decision.** CI runs `cargo audit` on every PR. Build fails on any
advisory of severity medium or higher.

## RS-SECURITY-008 — Pin `Cargo.lock` for binaries; not for libraries

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Binary crates and services commit `Cargo.lock`. Library
crates do not commit `Cargo.lock`.

**Why.** Binaries need reproducible builds. Libraries need to work with
a range of dependency versions.

## RS-SECURITY-009 — Review new dependencies

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Before adding a new dependency, check: maintenance
activity, download count, transitive dependency size, `unsafe` usage.
Prefer top-1000 crates.io.

### Cargo
