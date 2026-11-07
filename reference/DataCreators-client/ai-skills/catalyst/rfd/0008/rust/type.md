# RS-TYPE: Types

Standard derive macros and trait selection.

## RS-TYPE-001 — `Debug` is required on every public type

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Every public struct, enum, or trait object derives `Debug`.

**Why.** Logging, panics, and error reports rely on `Debug`. A type
without it is unloggable.

**Exception.** Types containing secrets — wrap secret fields with the
`secrecy` crate (RS-SECURITY-003), then derive `Debug`.

## RS-TYPE-002 — `Clone` unless the type manages a unique resource

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Default to deriving `Clone`. Skip when the type owns a
unique resource (file handle, connection pool, mutex guard) where
cloning would be incorrect.

**Why.** Most value types are clonable; explicit `Clone` lets callers
decide.

## RS-TYPE-003 — `PartialEq` and `Eq` on value types

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Value types derive `PartialEq` and `Eq` together. `Eq`
requires `PartialEq`.

**Why.** Tests and assertions need equality. `Eq` documents that the
relation is reflexive.

**Exception.** Types containing `f32`/`f64` cannot derive `Eq` (NaN).

## RS-TYPE-004 — `Hash` on map-key types

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Types used as `HashMap` keys or `HashSet` members derive
`Hash`. Requires `Eq`.

## RS-TYPE-005 — `Serialize`/`Deserialize` only on boundary-crossing types

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Derive `Serialize`/`Deserialize` only on types that cross
API or persistence boundaries. Internal-only types should not derive
serde.

**Why.** Serde derive is non-trivial in compile time. Adding it to types
that don't need it bloats build time and locks the type's wire format
unnecessarily.

## RS-TYPE-006 — Derive ordering: std first, then third-party

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Order derives: standard traits first, then third-party
traits, alphabetized within each group.

**Examples.**
```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct TableId {
    pub catalog: String,
    pub schema: String,
    pub table: String,
}
```

### Error Handling
