# JV-IDIOM: Idioms

Streams, method references, immutable collectors.

## JV-IDIOM-001 — Streams not for side effects

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** Don't use streams to mutate external state. Use a `for`
loop instead.

**Examples.**
```java
// ✗
users.stream().forEach(u -> u.setProcessed(true));

// ✓
for (User user : users) {
    user.setProcessed(true);
}
```

## JV-IDIOM-002 — Method references over lambdas when clear

**Severity:** warning
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Prefer `User::getName` over `u -> u.getName()`.

**Examples.**
```java
// ✓
List<String> names = users.stream().map(User::getName).toList();

// ✗
List<String> names = users.stream().map(u -> u.getName()).toList();
```

## JV-IDIOM-003 — Limit stream pipelines to ~3-4 operations

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Beyond 3-4 intermediate operations, extract named methods
for readability.

**Examples.**
```java
// ✓ extracted
List<Report> reports = data.stream()
    .filter(this::isRecentAndComplete)
    .map(this::toReport)
    .filter(r -> r.getScore() > threshold)
    .sorted(Comparator.comparing(Report::getScore).reversed())
    .limit(100)
    .toList();

// ✗ inline complexity
List<Report> reports = data.stream()
    .filter(d -> d.getDate().isAfter(cutoff))
    .filter(d -> d.getStatus() == Status.COMPLETE)
    .map(d -> new Report(d.getId(), d.getMetrics()))
    .filter(r -> r.getMetrics().getScore() > threshold)
    .sorted(Comparator.comparing(Report::getScore).reversed())
    .limit(100)
    .toList();
```

## JV-IDIOM-004 — Use `Stream.toList()` or `Collectors.toUnmodifiableList()`

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Default to immutable collections. Use `.toList()` (Java
16+) or `Collectors.toUnmodifiableList()` (Java 10+) unless mutability is
needed.

**Why.** Immutable defaults prevent accidental downstream mutation.

### Logging
