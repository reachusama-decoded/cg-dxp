# JV-TYPE: Types

Records, sealed classes, switch expressions, text blocks, var.

## JV-TYPE-001 — Records for immutable data carriers

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use a `record` for any immutable data class. Don't write a
hand-rolled POJO with constructor, getters, `equals`, `hashCode`, and
`toString` when a record fits.

**Why.** Records implement `equals`/`hashCode`/`toString` correctly by
default. No bugs from forgetting a field.

**Exception.** Class needs mutable state, participates in inheritance
(records are implicitly final), or requires a builder pattern.

**Examples.**
```java
// ✓ basic record
public record ColumnStat(
    String name,
    String dataType,
    long nullCount,
    long distinctCount,
    double nullRate
) {}

// ✓ compact constructor with validation
public record BatchConfig(int batchSize, int maxRetries) {
    public BatchConfig {
        if (batchSize <= 0) {
            throw new IllegalArgumentException("batchSize must be positive: " + batchSize);
        }
        if (maxRetries < 0) {
            throw new IllegalArgumentException("maxRetries must be non-negative: " + maxRetries);
        }
    }
}

// ✓ derived accessor
public record TableRef(String catalog, String schema, String table) {
    public String fullyQualified() {
        return catalog + "." + schema + "." + table;
    }
}
```

## JV-TYPE-002 — Sealed classes for closed type hierarchies

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When a type has a known fixed set of subtypes, declare it
`sealed` with explicit `permits`. Pair with switch expressions for
exhaustive handling.

**Why.** The compiler verifies exhaustiveness — adding a variant forces
every switch to be updated.

**Examples.**
```java
public sealed interface PipelineResult
    permits PipelineResult.Success, PipelineResult.Failure, PipelineResult.Skipped {

    record Success(long rowsProcessed, Duration elapsed) implements PipelineResult {}
    record Failure(String reason, Throwable cause) implements PipelineResult {}
    record Skipped(String reason) implements PipelineResult {}
}

String summary = switch (result) {
    case PipelineResult.Success s -> "Processed %d rows in %s".formatted(s.rowsProcessed(), s.elapsed());
    case PipelineResult.Failure f -> "Failed: " + f.reason();
    case PipelineResult.Skipped sk -> "Skipped: " + sk.reason();
};
```

## JV-TYPE-003 — Switch expressions over switch statements

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Use `->` arrow switch expressions, not `case ... :` switch
statements with `break`.

**Why.** Arrow switches don't fall through, are exhaustive on enums and
sealed types, and are expression-form.

**Examples.**
```java
// ✓
String label = switch (status) {
    case PENDING -> "Pending";
    case RUNNING -> "Running";
    case COMPLETE -> "Complete";
    case FAILED -> "Failed";
};

// ✗
String label;
switch (status) {
    case PENDING:
        label = "Pending";
        break;
    case RUNNING:
        label = "Running";
        break;
    default:
        label = "Unknown";
}
```

## JV-TYPE-004 — Text blocks for multi-line strings

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `"""` text blocks for multi-line SQL, JSON, XML, and log
templates. Never concatenate multi-line strings with `+`.

**Examples.**
```java
// ✓
String sql = """
    SELECT column_name,
           data_type,
           COUNT(*) FILTER (WHERE value IS NULL) AS null_count
    FROM %s.%s.%s
    GROUP BY column_name, data_type
    """.formatted(catalog, schema, table);

// ✗
String sql = "SELECT column_name, data_type, " +
    "COUNT(*) FILTER (WHERE value IS NULL) AS null_count " +
    "FROM " + catalog + "." + schema + "." + table + " " +
    "GROUP BY column_name, data_type";
```

**Note.** `formatted()` for structural placeholders (table names) is fine;
user-supplied values must use `PreparedStatement` (JV-SECURITY-001).

## JV-TYPE-005 — `var` permitted when type is obvious

**Severity:** warning
**Since:** v0.1.0
**Linter:** Checkstyle (advisory rule)

**Decision.** Use `var` for local variables when the type is obvious from
the right-hand side. Never use `var` when the type is not immediately
clear from the code on the same line.

**Examples.**
```java
// ✓
var users = new ArrayList<User>();
var config = BatchConfig.load("pipeline.yml");
try (var reader = Files.newBufferedReader(path)) { ... }

// ✗
var result = process(input);   // type unclear
var x = getData();              // meaningless name and unclear type
var list = new ArrayList<>();   // erased: ArrayList<Object>
```

**Rule of thumb.** If a reviewer reading a diff (no IDE) cannot determine
the type, don't use `var`.

### Null and Optional
