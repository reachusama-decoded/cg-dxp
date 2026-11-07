# JV-SECURITY: Security

PreparedStatement, secrets, deserialization, OWASP scan.

## JV-SECURITY-001 — `PreparedStatement` parameter binding for SQL

**Severity:** error
**Since:** v0.1.0
**Linter:** findsecbugs

**Decision.** Always use `PreparedStatement.setX(...)` for user-supplied
values. Never concatenate or `String.format` user input into SQL.

**Examples.**
```java
// ✓
String sql = "SELECT * FROM users WHERE name = ? AND status = ?";
try (var stmt = connection.prepareStatement(sql)) {
    stmt.setString(1, userName);
    stmt.setString(2, status);
    try (var rs = stmt.executeQuery()) {
        return mapResults(rs);
    }
}

// ✗
String sql = "SELECT * FROM users WHERE name = '" + userName + "'";

// ✗ String.format is not parameterization
String sql = String.format("SELECT * FROM users WHERE name = '%s'", userName);
```

## JV-SECURITY-002 — Never log secrets or PII

**Severity:** error
**Since:** v0.1.0
**Linter:** findsecbugs

**Decision.** Never log:
- Passwords, tokens, API keys
- Social Security numbers, national IDs
- Credit card numbers or financial accounts
- Full email addresses or phone numbers in production logs
- Database connection strings with embedded credentials
- Stack traces containing sensitive input

**Examples.**
```java
// ✗
logger.info("Authenticating user {} with password {}", username, password);
logger.debug("Connection string: {}", connectionString);

// ✓
logger.info("Authenticating user {}", username);
logger.debug("Connected to database at {}", sanitizeConnectionString(connectionString));
```

## JV-SECURITY-003 — Validate identifiers against a safe pattern

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** SQL identifiers and other dynamic names must match an
allowlist pattern.

**Examples.**
```java
private static final Pattern SAFE_IDENTIFIER = Pattern.compile("^[a-zA-Z_][a-zA-Z0-9_]*$");

public static String validateIdentifier(String identifier) {
    if (!SAFE_IDENTIFIER.matcher(identifier).matches()) {
        throw new IllegalArgumentException(
            "Invalid identifier (must be alphanumeric/underscore): " + identifier);
    }
    return identifier;
}
```

## JV-SECURITY-004 — Never deserialize untrusted data with `ObjectInputStream`

**Severity:** error
**Since:** v0.1.0
**Linter:** findsecbugs

**Decision.** Java native serialization is a known RCE vector. Use JSON
(Jackson) or Protocol Buffers across trust boundaries.

**Why.** Effective Java Item 85.

**Exception.** Internal Spark serialization is unavoidable but
constrained. Restrict deserialization to known classes via
`ObjectInputFilter` (Java 9+).

## JV-SECURITY-005 — OWASP Dependency-Check in CI

**Severity:** error
**Since:** v0.1.0
**Linter:** OWASP Dependency-Check (CI)

**Decision.** CI runs OWASP Dependency-Check on every PR. Build fails on
any CVE with CVSS ≥ 7.

```kotlin
plugins {
    id("org.owasp.dependencycheck") version "9.2.0"
}
dependencyCheck {
    failBuildOnCVSS = 7.0f
}
```

## JV-SECURITY-006 — Keep dependencies up to date

**Severity:** warning
**Since:** v0.1.0
**Linter:** Renovate / Dependabot

**Decision.** Run dependency updaters regularly. Don't sit on stale
versions of security-relevant libraries.

### Spark
