# JV-IMPORT: Imports

Group order and wildcard policy per Google Java Style.

## JV-IMPORT-001 — Group order per Google Java Style

**Severity:** error
**Since:** v0.1.0
**Linter:** google-java-format, Checkstyle

**Decision.** Three groups, separated by blank lines:

1. `com.catalyst.*` (project imports)
2. Third-party (`org.apache`, `com.google`, etc.)
3. `java.*` and `javax.*`

## JV-IMPORT-002 — No wildcard imports

**Severity:** error
**Since:** v0.1.0
**Linter:** Checkstyle `AvoidStarImport`

**Decision.** Never `import java.util.*`. Always import specific classes.

**Why.** Wildcards hide which classes are used, break when packages export
the same name, and complicate code review.

**Examples.**
```java
// ✓
import java.util.List;
import java.util.Map;

// ✗
import java.util.*;
```

## JV-IMPORT-003 — Static imports limited and explicit

**Severity:** warning
**Since:** v0.1.0
**Linter:** Checkstyle

**Decision.** Static imports are allowed for AssertJ assertions, Mockito,
and `org.apache.spark.sql.functions.*`. Never `import static java.util.Arrays.*`
or other broad utility statics.

### Naming
