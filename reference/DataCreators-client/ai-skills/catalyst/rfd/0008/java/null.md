# JV-NULL: Null and Optional

Optional usage, null discipline, requireNonNull at API boundaries.

## JV-NULL-001 — `Optional` only as return type when absence is normal

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** `Optional<T>` is a return type for methods where "no value"
is a valid normal result. Not a general-purpose null replacement.

**Why.** Effective Java Item 55. `Optional` allocates and complicates the
type — use it only where it earns its keep.

## JV-NULL-002 — Never `Optional.get()` without `isPresent()` (use combinators)

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs `OPTIONAL_RETURN_NULL`

**Decision.** Use `map`, `flatMap`, `orElse`, `orElseThrow`, or
`ifPresent`. Never `.get()` without first checking — and prefer the
combinators even then.

**Examples.**
```java
// ✓ map + orElse
String name = findUser(id).map(User::getName).orElse("unknown");

// ✓ orElseThrow with specific exception
User user = findUser(id)
    .orElseThrow(() -> new UserNotFoundException("User not found: " + id));

// ✓ flatMap chains
String city = findUser(id)
    .flatMap(User::getAddress)
    .map(Address::getCity)
    .orElse("unknown");

// ✓ or() for fallback Optional (Java 9+)
User user = findInCache(id)
    .or(() -> findInDatabase(id))
    .orElseThrow(() -> new UserNotFoundException(id));

// ✗ get() without check — throws NoSuchElementException
String name = findUser(id).get();

// ✗ verbose imperative
Optional<User> opt = findUser(id);
if (opt.isPresent()) {
    return opt.get().getName();
} else {
    return "unknown";
}
```

## JV-NULL-003 — Never `Optional` as a method parameter

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't take `Optional<T>` as a parameter. Use method
overloading or `@Nullable`.

**Examples.**
```java
// ✗
public void process(Optional<String> filter) { ... }

// ✓
public void process() { process(null); }
public void process(@Nullable String filter) { ... }
```

## JV-NULL-004 — Never `Optional` as a field type

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** Don't declare a field as `Optional<T>`. Use `@Nullable` or a
sentinel value.

## JV-NULL-005 — Never `Optional<Collection<T>>`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Return an empty collection rather than `Optional<Collection<T>>`.

**Why.** Empty collection is the natural "no values" representation. An
empty `Optional` adds a wrapper without semantic gain.

## JV-NULL-006 — Never return `null` from a collection-returning method

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** Effective Java Item 54. Return an empty `List`, `Set`, or
`Map` (e.g., `List.of()`).

## JV-NULL-007 — `Objects.requireNonNull` and blank checks at API boundaries

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Public methods validate parameters with
`Objects.requireNonNull(arg, "message")` and explicit blank checks where
applicable.

**Examples.**
```java
public TableProfile profile(String catalog, String schema, String table) {
    Objects.requireNonNull(catalog, "catalog must not be null");
    Objects.requireNonNull(schema, "schema must not be null");
    Objects.requireNonNull(table, "table must not be null");
    if (catalog.isBlank()) {
        throw new IllegalArgumentException("catalog must not be blank");
    }
    if (schema.isBlank()) {
        throw new IllegalArgumentException("schema must not be blank");
    }
    if (table.isBlank()) {
        throw new IllegalArgumentException("table must not be blank");
    }
    // ...
}
```

### Error Handling
