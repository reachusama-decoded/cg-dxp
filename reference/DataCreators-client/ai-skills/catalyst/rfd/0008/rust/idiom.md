# RS-IDIOM: Idioms

Combinators, iterator chains, builders, and ownership patterns.

## RS-IDIOM-001 — Combinators over match for simple transforms

**Severity:** warning
**Since:** v0.1.0
**Linter:** Clippy `manual_map`, `manual_let_else`, `map_unwrap_or`

**Decision.** Use `Option`/`Result` combinators (`map`, `and_then`,
`unwrap_or_else`, `ok_or_else`, `filter_map`) for single-expression
transforms. Reserve `match` for multi-statement arms.

**Examples.**
```rust
// ✓
let upper: Option<String> = name.map(|n| n.to_uppercase());
let port: Option<u16> = config.get("port").and_then(|v| v.parse::<u16>().ok());
let timeout = config.timeout.unwrap_or_else(|| Duration::from_secs(30));

// ✗
let upper = match name {
    Some(n) => Some(n.to_uppercase()),
    None => None,
};
```

## RS-IDIOM-002 — Iterator chains over manual loops for transforms

**Severity:** warning
**Since:** v0.1.0
**Linter:** Clippy `needless_collect`, `manual_filter`

**Decision.** Use iterator chains (`map`, `filter`, `filter_map`,
`collect`, `fold`, `sum`) for transforms and aggregations. Use for-loops
when the body has side effects.

**Examples.**
```rust
// ✓
let valid_ports: Vec<u16> = raw_ports
    .iter()
    .filter_map(|s| s.parse::<u16>().ok())
    .filter(|&p| p > 1024)
    .collect();

let total_rows: u64 = tables.iter().map(|t| t.row_count).sum();
```

## RS-IDIOM-003 — For-loops for side effects; never iterator chains

**Severity:** warning
**Since:** v0.1.0
**Linter:** Clippy `needless_for_each`

**Decision.** When the loop body performs I/O, logging, or external
mutation, use a `for` loop, not `.for_each()` or a `[]`-collected
comprehension equivalent.

**Why.** Iterator chains read as if they produce a value. Side-effecting
chains hide intent and ignore Results from each iteration.

**Examples.**
```rust
// ✓
for table in &tables {
    tracing::info!(table = %table.name, "processing");
    processor.ingest(table).await?;
}

// ✗
tables.iter().for_each(|t| {
    println!("processing {}", t.name);  // bypasses tracing
    processor.ingest(t);                 // ignores Result
});
```

## RS-IDIOM-004 — Field init shorthand

**Severity:** warning
**Since:** v0.1.0
**Linter:** Clippy `redundant_field_names`

**Decision.** When the variable name matches the field, use shorthand.

**Examples.**
```rust
// ✓
let profile = TableProfile { catalog, schema, table, row_count, columns: vec![] };

// ✗
let profile = TableProfile {
    catalog: catalog,
    schema: schema,
    table: table,
    row_count: row_count,
    columns: vec![],
};
```

## RS-IDIOM-005 — Builder pattern for >4 fields with optionals

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When a struct has more than 4 fields and some are
optional, use a builder. Prefer the `bon` crate; `typed-builder` is
acceptable.

**Why.** Builders document required vs optional and provide stable
construction across version changes.

**Exception.** Plain data structs with all required fields don't need a
builder.

**Examples.**
```rust
use bon::Builder;

#[derive(Debug, Builder)]
pub struct PipelineConfig {
    catalog: String,
    schema: String,
    #[builder(default = "default".into())]
    environment: String,
    #[builder(default = 3)]
    retries: u32,
    #[builder(default = Duration::from_secs(3600))]
    timeout: Duration,
}

let config = PipelineConfig::builder()
    .catalog("investments_dev".into())
    .schema("curated".into())
    .retries(5)
    .build();
```

## RS-IDIOM-006 — `From` for infallible, `TryFrom` for fallible

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Implement `From<T>` for lossless infallible conversions.
Implement `TryFrom<T>` when conversion can fail. Callers get `Into`/`TryInto` for free.

**Examples.**
```rust
impl From<DbRow> for TableProfile {
    fn from(row: DbRow) -> Self {
        Self { catalog: row.catalog, schema: row.schema, table: row.table, row_count: row.row_count as u64, columns: vec![] }
    }
}

impl TryFrom<&str> for Severity {
    type Error = ParseSeverityError;
    fn try_from(value: &str) -> Result<Self, Self::Error> {
        match value {
            "high" => Ok(Self::High),
            "medium" => Ok(Self::Medium),
            "low" => Ok(Self::Low),
            other => Err(ParseSeverityError(other.to_string())),
        }
    }
}
```

## RS-IDIOM-007 — Accept `impl Into<T>` in public function signatures

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Public APIs accept `impl Into<T>` (or `impl AsRef<T>`)
where ergonomic. Callers don't have to convert manually.

**Examples.**
```rust
// ✓
pub fn set_catalog(&mut self, catalog: impl Into<String>) {
    self.catalog = catalog.into();
}

// caller: config.set_catalog("investments");

// ✗
pub fn set_catalog(&mut self, catalog: String) { self.catalog = catalog; }
// caller: config.set_catalog("investments".to_string());
```

## RS-IDIOM-008 — `Cow<'_, str>` for borrowed-or-owned

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When a function sometimes allocates and sometimes does
not, return `Cow<'_, str>` rather than always allocating.

**Examples.**
```rust
use std::borrow::Cow;

fn normalize_name(name: &str) -> Cow<'_, str> {
    if name.contains(' ') {
        Cow::Owned(name.replace(' ', "_"))
    } else {
        Cow::Borrowed(name)
    }
}
```

### Async (Tokio)
