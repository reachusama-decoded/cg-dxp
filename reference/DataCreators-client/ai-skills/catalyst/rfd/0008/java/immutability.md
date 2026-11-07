# JV-IMMUTABILITY: Immutability

Defensive copies, final, and unmodifiable factories.

## JV-IMMUTABILITY-001 — Prefer immutable objects

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Default to immutability. Use `final` fields, records, and
unmodifiable collections (`List.of`, `Map.of`, `Set.of`,
`Collections.unmodifiableList`).

**Why.** Effective Java Items 17, 18.

## JV-IMMUTABILITY-002 — Defensive copies of mutable parameters and returns

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs `EI_EXPOSE_REP`, `EI_EXPOSE_REP2`

**Decision.** Public APIs that accept or return mutable types make
defensive copies.

**Why.** Effective Java Item 50. Without copies, the caller can mutate
internal state.

**Examples.**
```java
// ✗ leaks internal state
public List<String> getStages() {
    return stages;  // caller can mutate
}

// ✓ defensive copy
public List<String> getStages() {
    return List.copyOf(stages);
}
```

## JV-IMMUTABILITY-003 — Local variables `final` when not reassigned

**Severity:** advisory
**Since:** v0.1.0
**Linter:** Checkstyle (advisory rule)

**Decision.** Declare local variables `final` when they are not
reassigned.

## JV-IMMUTABILITY-004 — Classes `final` unless designed for extension

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Mark classes `final` by default. Effective Java Item 19.

## JV-IMMUTABILITY-005 — `List.of` / `Map.of` / `Set.of` for unmodifiable factory

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Construct small unmodifiable collections with the
static factory methods.

**Examples.**
```java
List<String> defaults = List.of("extract", "transform", "load");
Map<String, Integer> priorities = Map.of("critical", 1, "high", 2, "low", 3);
Set<String> allowed = Set.of("csv", "parquet", "delta");
```

### Concurrency
