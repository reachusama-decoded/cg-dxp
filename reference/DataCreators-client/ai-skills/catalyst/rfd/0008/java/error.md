# JV-ERROR: Error Handling

Exception handling, try-with-resources, exception chaining.

## JV-ERROR-001 — Never `catch (Exception e)` as silent catch-all

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs `REC_CATCH_EXCEPTION`

**Decision.** Catching `Exception` is allowed only when the catch block
re-throws or wraps and re-throws.

**Why.** Catching `Exception` hides `NullPointerException`,
`ClassCastException`, `ArrayIndexOutOfBoundsException` — bugs that should
crash loudly during development.

## JV-ERROR-002 — Never catch `Throwable`

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** Don't catch `Throwable`. It includes `Error` subclasses
(`OutOfMemoryError`, `StackOverflowError`) the JVM cannot recover from.

## JV-ERROR-003 — Never empty catch block

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle `EmptyCatchBlock`

**Decision.** Every catch block must re-throw, wrap-and-throw, log at
ERROR/WARN level, or contain an explicit comment justifying the swallow.

**Examples.**
```java
// ✓ intentional ignore with required justification
try {
    Thread.sleep(100);
} catch (InterruptedException e) {
    // Restore interrupted status — this thread is about to terminate
    Thread.currentThread().interrupt();
}

// ✗
try {
    parseConfig(input);
} catch (ConfigException e) {
    // silently swallowed
}
```

## JV-ERROR-004 — Always try-with-resources for `AutoCloseable`

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs `OS_OPEN_STREAM`, Checkstyle

**Decision.** Every `AutoCloseable` is acquired in a try-with-resources.
No manual `close()` in `finally`. Effective Java Item 9.

**Examples.**
```java
// ✓ multiple resources in one try-with-resources
try (var input = Files.newBufferedReader(path);
     var output = Files.newBufferedWriter(outputPath)) {
    String line;
    while ((line = input.readLine()) != null) {
        output.write(transform(line));
        output.newLine();
    }
}

// ✗
Connection conn = null;
try {
    conn = dataSource.getConnection();
    // ...
} finally {
    if (conn != null) conn.close();
}
```

## JV-ERROR-005 — Checked vs unchecked exceptions

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use checked exceptions for recoverable conditions the caller
can handle (e.g., `FileNotFoundException`, `SQLException`). Use unchecked
exceptions (`RuntimeException` subclasses) for programming errors:
illegal arguments, illegal state, broken invariants.

**Why.** Effective Java Items 70-72.

## JV-ERROR-006 — Never `throws Exception` or `throws Throwable`

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Declare specific exception types in method signatures.

**Why.** `throws Exception` tells the caller nothing useful and prevents
the compiler from helping them.

## JV-ERROR-007 — Always chain exceptions with the cause

**Severity:** error
**Since:** v0.1.0
**Linter:** SpotBugs

**Decision.** When wrapping an exception, pass the original as the
`cause` parameter. Never discard the original stack trace.

**Examples.**
```java
// ✓
try (var connection = dataSource.getConnection();
     var statement = connection.prepareStatement(sql)) {
    statement.setString(1, schemaName);
    try (var rs = statement.executeQuery()) {
        return mapResultSet(rs);
    }
} catch (SQLException e) {
    throw new DataProfilingException(
        "Failed to profile " + schemaName + "." + tableName, e);
}

// ✗ — original cause discarded
} catch (SQLException e) {
    throw new RuntimeException(e.getMessage());
}
```

## JV-ERROR-008 — Domain exceptions in a dedicated package

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Define a per-package `*Exception` hierarchy with a base
exception class.

**Examples.**
```java
public class CatalystException extends RuntimeException {
    public CatalystException(String message) { super(message); }
    public CatalystException(String message, Throwable cause) { super(message, cause); }
}

public class DataProfilingException extends CatalystException { ... }

public class SchemaNotFoundException extends CatalystException {
    public SchemaNotFoundException(String schema) {
        super("Schema not found: " + schema);
    }
}
```

### Idioms
