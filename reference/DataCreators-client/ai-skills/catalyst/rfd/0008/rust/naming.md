# RS-NAMING: Naming

Identifier casing per RFC 430 and API Guidelines.

## RS-NAMING-001 — Identifier casing per RFC 430

**Severity:** error
**Since:** v0.1.0
**Linter:** rustc warnings + Clippy

**Decision.** Use the casing in this table:

| Item | Convention | Example |
|------|-----------|---------|
| Crates | `snake_case` | `catalog_client` |
| Modules | `snake_case` | `table_profile.rs` |
| Types (struct, enum, trait) | `UpperCamelCase` | `TableProfile` |
| Type parameters | `T`, `ResponseBody` | single uppercase or UpperCamelCase |
| Lifetimes | short lowercase, descriptive | `'a`, `'conn` |
| Functions | `snake_case` | `fetch_table_profile` |
| Methods | `snake_case` | `get_columns` |
| Local variables | `snake_case` | `row_count` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_BATCH_SIZE` |
| Statics | `SCREAMING_SNAKE_CASE` | `DEFAULT_TIMEOUT` |
| Enum variants | `UpperCamelCase` | `NotFound` |
| Feature flags | `kebab-case` | `serde-support` |
| Macros | `snake_case!` | `vec!`, `ensure!` |

**Why.** RFC 430. The compiler warns; Clippy reinforces.

**Exception.** None.

## RS-NAMING-002 — No `get_` prefix on getters

**Severity:** warning
**Since:** v0.1.0
**Linter:** Clippy `wrong_self_convention`

**Decision.** Per API Guidelines C-GETTER, getters use the bare field
name: `fn name(&self) -> &str`, not `fn get_name(&self) -> &str`.

**Why.** Idiomatic Rust. The `get_` prefix is reserved for `HashMap::get`-style
returns of `Option<&V>`.

**Examples.**
```rust
// ✓
impl Profile {
    fn name(&self) -> &str { &self.name }
}

// ✗
impl Profile {
    fn get_name(&self) -> &str { &self.name }
}
```

## RS-NAMING-003 — `set_` prefix on setters; `is_`/`has_` on boolean getters

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Setters use `set_`. Boolean accessors use `is_` or `has_`.

**Why.** API Guidelines. Predictable, scannable.

**Examples.**
```rust
fn set_name(&mut self, name: String) { self.name = name; }
fn is_active(&self) -> bool { self.status == Status::Active }
fn has_columns(&self) -> bool { !self.columns.is_empty() }
```

## RS-NAMING-004 — Conversion prefixes per API Guidelines

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use the canonical conversion prefixes:

- `as_` — cheap, borrowed (e.g., `String::as_str`)
- `to_` — expensive or different type (e.g., `&str::to_string`)
- `into_` — ownership transfer (e.g., `String::into_bytes`)

**Why.** API Guidelines C-CONV. Sets caller expectations about cost.

## RS-NAMING-005 — No ambiguous or generic variable names

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Avoid `data`, `info`, `temp`, `result`, `val`, `foo`, `bar`,
`baz`. Single-character names are acceptable in closures (`|x|`),
iterator chains, and single-character generics (`T`, `E`).

**Why.** Generic names hide intent. Test code is included in this rule.

### Types and Derives
