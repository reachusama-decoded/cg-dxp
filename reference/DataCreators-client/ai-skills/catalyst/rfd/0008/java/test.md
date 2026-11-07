# JV-TEST: Testing

JUnit 5, AssertJ, Mockito, JaCoCo coverage.

## JV-TEST-001 — JUnit 5 only

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Tests use JUnit 5 (`org.junit.jupiter`). No JUnit 4
(`org.junit.Test`), no TestNG.

## JV-TEST-002 — AssertJ for all assertions

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use AssertJ (`assertThat(...)`) for assertions. Don't use
JUnit's built-in `assertEquals`/`assertTrue`.

**Why.** AssertJ provides fluent assertions with superior failure messages.

**Examples.**
```java
// ✓
assertThat(result.getName()).isEqualTo("expected");
assertThat(users).hasSize(3);
assertThat(users).extracting(User::getName).containsExactly("Alice", "Bob", "Carol");
assertThat(score).isCloseTo(0.95, within(0.01));

// ✗
assertEquals("expected", result.getName());
assertTrue(users.size() == 3);
```

## JV-TEST-003 — Mockito 5+; never PowerMock

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use Mockito 5 or later. Never PowerMock.

**Why.** PowerMock breaks encapsulation and indicates a design problem
(static dependencies, final classes mocked). The fix is the design, not
PowerMock.

## JV-TEST-004 — 80% line coverage minimum on `src/main/java`

**Severity:** error
**Since:** v0.1.0
**Linter:** JaCoCo coverage gate

**Decision.** JaCoCo enforces ≥ 80% line coverage on `src/main/java`. CI
fails below this threshold.

## JV-TEST-005 — No `@Disabled` without a tracking issue

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** `@Disabled` requires a comment referencing a tracking
issue.

**Examples.**
```java
@Disabled("CATALYST-1234: flaky due to race condition")
@Test
void integration_test_xyz() { ... }
```

## JV-TEST-006 — One thing per test method

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** A test method asserts one behavior. If it has multiple
unrelated assertions, split it.

## JV-TEST-007 — `@Nested` classes for grouping

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `@Nested` classes inside a test class to group related
test cases (per method under test, per scenario family).

**Examples.**
```java
@ExtendWith(MockitoExtension.class)
class TableProfilerTest {
    @Mock private DataSource dataSource;
    @InjectMocks private TableProfiler profiler;

    @Nested
    class Profile {
        @Test void profile_validTable_returnsColumnStats() { ... }
        @Test void profile_missingTable_throwsSchemaNotFound() { ... }
    }

    @Nested
    class Validation {
        @Test void profile_nullSchema_throwsIllegalArgument() { ... }
    }
}
```

### Documentation
