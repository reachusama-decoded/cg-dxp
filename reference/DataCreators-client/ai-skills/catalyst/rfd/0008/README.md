---
authors: RBLW
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/139
labels: coding-standards, python, rust, typescript, java, sql, ci, composability
---

# RFD 0008 Coding Standards

## Introduction

As the platform grows across multiple languages — Python for data engineering
and AI skills, Rust for backend services, TypeScript for frontend applications,
Java for Spark workloads on Azul Zulu OpenJDK, and SQL for dbt models — we need
a shared set of coding standards that ensure consistency, security, and
maintainability.

This RFD establishes language-specific standards rooted in the authoritative
style guides for each language. Rather than inventing conventions, we adopt
community standards and document only the deviations or additions specific to
our platform. Standards are enforced automatically through linters, formatters,
and GitHub Copilot code review in CI.

Each language guide is **rule-based**: every requirement is a numbered rule
with a stable ID, a severity, a linter binding, and concrete examples. Rules
are addressable from outside the document — by future engineering skills, by
CI gates, by dashboards. See *Rule Format* below.

## Layout

Each language/platform has its own subdirectory. The directory's `README.md`
covers the intro, governing authority, and tooling. Rules are split into
**per-category files** so a single file holds one cohesive group of rules
(e.g., `python/error.md` holds all `PY-ERROR-*` rules). Each category file
is short enough to read in one sitting.

```
rfd/0008/
├── README.md                  # this file: overview, format, governance, Copilot
├── standards.yaml             # machine-readable index of every rule
├── common/
│   ├── README.md
│   └── bi-temporal.md         # bi-temporal table design reference
├── python/
│   ├── README.md              # intro, governing authority, tooling
│   ├── version.md             # PY-VERSION-* rules
│   ├── import.md              # PY-IMPORT-* rules
│   ├── naming.md              # PY-NAMING-* rules
│   ├── type.md                # PY-TYPE-* rules
│   ├── doc.md                 # PY-DOC-* rules
│   ├── error.md               # PY-ERROR-* rules
│   ├── idiom.md               # PY-IDIOM-* rules
│   ├── test.md                # PY-TEST-* rules
│   └── security.md            # PY-SECURITY-* rules
├── rust/                      # same shape; 13 category files
├── java/                      # 14 category files
├── typescript/                # 10 category files
├── sql/                       # 11 category files
├── databricks/                # 5 category files
└── containerization/          # 5 category files
```

## Language Guides

| Language / Platform | Guide | Governing Authority | Formatter | Linter | Type Checker |
|---------------------|-------|---------------------|-----------|--------|--------------|
| Python | [`python/`](python/README.md) | PEP 8, Google Python Style Guide | `ruff format` | `ruff check` | `pyright` |
| Rust | [`rust/`](rust/README.md) | Rust API Guidelines, Clippy | `cargo fmt` | `cargo clippy` | compiler |
| TypeScript | [`typescript/`](typescript/README.md) | Airbnb JS Guide, TypeScript Handbook | `prettier` | `eslint` | `tsc --noEmit` |
| Java | [`java/`](java/README.md) | Google Java Style Guide, Effective Java (Azul Zulu OpenJDK) | Spotless (`google-java-format`) | `checkstyle` | compiler |
| SQL (dbt) | [`sql/`](sql/README.md) | dbt Style Guide, sqlfluff | — | `sqlfluff lint` | — |
| Databricks / UC | [`databricks/`](databricks/README.md) | Databricks docs, UC, Delta Lake | — | Terraform validate, cluster policies | — |
| Containerization | [`containerization/`](containerization/README.md) | OCI image guidance, Development Containers Spec, Google Shell Style Guide | — | shellcheck, CI | — |

### Rule Index

[`standards.yaml`](standards.yaml) — the machine-readable index of every
rule. Each entry has a stable ID, severity, linter binding, and a `source`
pointing to the markdown anchor (e.g., `python/error.md#py-error-001`).
Used by future engineering skills (via `metadata.standards`), CI gates, and
compliance dashboards.

### Supporting References

| Document | Description |
|----------|-------------|
| [`common/bi-temporal.md`](common/bi-temporal.md) | Bi-temporal table design patterns for foundation data models. |

When working in a specific language, start with that language's `README.md`
and pick the category file relevant to your change.

## Rule Format

Every rule in every language guide has the same shape:

```
### LANG-CATEGORY-NNN — one-line directive

**Severity:** error | warning | advisory
**Since:** v0.1.0
**Linter:** linter rule codes, or "advisory"

**Decision.** What to do, in 1–3 sentences.
**Why.** Rationale.
**Exception.** When the rule does not apply, or "None."
**Examples.** ✓ good / ✗ bad code.
```

### Rule ID scheme

```
{LANG}-{CATEGORY}-{NNN}

PY-NAMING-001       Python naming
PY-TYPE-014         Python typing
PY-ERROR-008        Python error handling
RS-LIFETIME-003     Rust lifetimes
TS-ASYNC-007        TypeScript async
JV-NULL-002         Java null safety
SQL-MODEL-005       SQL/dbt modeling
CONT-PATH-001       Containerized environment paths
COMMON-LOG-001      cross-language logging shape
```

Language prefixes:

- `PY` — Python
- `RS` — Rust
- `JV` — Java
- `TS` — TypeScript
- `SQL` — SQL/dbt
- `CONT` — containerization and containerized development environments
- `COMMON` — cross-language rules (logging shape, secret handling, etc.)

### Rule categories per language

Each language uses a fixed set of categories so contributors know exactly where
new rules belong:

| Language | Categories |
|----------|-----------|
| Python | VERSION, IMPORT, NAMING, TYPE, DOC, ERROR, IDIOM, TEST, SECURITY |
| Rust | VERSION, IMPORT, NAMING, TYPE, ERROR, IDIOM, ASYNC, LOG, DOC, TEST, SECURITY, CARGO, PERF |
| Java | VERSION, IMPORT, NAMING, TYPE, NULL, ERROR, IDIOM, LOG, DOC, TEST, IMMUTABILITY, CONCURRENCY, SECURITY, SPARK |
| TypeScript | VERSION, IMPORT, NAMING, TYPE, REACT, IDIOM, ASYNC, ERROR, TEST, SECURITY |
| SQL/dbt | VERSION, FMT, NAMING, CTE, MODEL, INCR, TEST, JINJA, IDIOM, PERF, SECURITY |
| Databricks/UC | DELTA, UC, COMPUTE, WORKFLOW, SEC |
| Containerization | BASE, PATH, ENV, SETUP, PORT |

### Severity

- **error** — must be fixed; CI fails
- **warning** — must be fixed unless suppressed with justification
- **advisory** — recommended; not enforced by linters today

### Linter binding

Each rule lists the linter rule codes that enforce it. A rule with `linter:
[advisory]` is policy-only; humans enforce it in code review until it's
encoded in a tool.

## Composability with Engineering Skills

The rule-based structure exists so that future **engineering skills** —
"write a Python module," "design a Rust async service," "review a TypeScript
PR" — can compose against the standard rather than duplicating it.

### Skills bind to rule IDs

A future engineering skill declares which rules it expects in its frontmatter:

```yaml
---
name: write-python-module
description: Approach for designing and writing a new Python module.
metadata:
  tier: document
  standards:
    - PY-NAMING-*           # all Python naming rules
    - PY-TYPE-001..015      # range
    - PY-ERROR-008          # specific rule
    - PY-TEST-*
    - COMMON-LOG-001
---
```

At skill invocation, the loader resolves the wildcards and ranges from
`standards.yaml` and inlines the matching rule bodies into the skill's
context. The skill itself stays short — it describes *approach* (when to
break out a module, how to organize public API, how to think about coupling)
— while the *rules* stay in this RFD as the single source of truth.

### Why this matters

This pattern separates **policy** from **practice**:

- **Standards (this RFD)** = policy — what is correct
- **Skills** = practice — how to apply policy in a workflow

A skill that wants to teach "write a new Python module" doesn't repeat
naming rules. It binds to `PY-NAMING-*` and lets the standard speak. When
the standard updates, every skill that bound to it inherits the update
automatically.

### Concrete consequences

- A future `engineering/write-python-data-product` skill is ~150 lines of
  approach plus a frontmatter declaration of which standards bind. Without
  this pattern it would be ~1500 lines of rules and approach tangled
  together.
- A `engineering/refactor-error-handling` skill binds to `PY-ERROR-*` +
  `RS-ERROR-*` + `COMMON-LOG-001` — works across languages because the skill
  is about *the workflow*, not the rules.
- A reviewer skill (`engineering/review-pr`) binds to *all* rules for the
  languages in the diff and checks the PR against the explicit list, citing
  rule IDs in its output.

### Validation

- Skill metadata referencing a non-existent rule ID fails skill validation
  in CI.
- Skill bindings to deprecated rules surface as warnings, with an automated
  hint pointing at the replacement rule.

## `standards.yaml` Index

`standards.yaml` is the machine-readable index of every rule. Each entry:

```yaml
- id: PY-NAMING-001
  title: Identifier casing per PEP 8
  language: python
  category: NAMING
  severity: error
  since: 0.1.0
  linter: ["ruff:N"]
  source: python/naming.md#py-naming-001
```

Used by:

- **Engineering skills** — resolve `metadata.standards` bindings.
- **CI gates** — map rule IDs to linter configurations.
- **Dashboards** — aggregate compliance and exception trends.
- **Tooling** — `catalyst standards list --tag python --category error`.

## Rule Governance

### Stability

Rule IDs are **stable**. They are never renumbered or reused. When a rule is
replaced, the old ID stays in `standards.yaml` with `status: deprecated` and
a `replaced_by` pointer.

### Adding a new rule

1. Pick the next free `NNN` in the appropriate `LANG-CATEGORY-` namespace.
2. Add the rule to the language's markdown file in the right section.
3. Append to `standards.yaml` with all metadata fields populated.
4. If the rule has a linter binding, update the corresponding linter
   configuration so the rule actually fires.
5. Open a PR; tag the language owner.

### Deprecating a rule

1. In the language's markdown file, mark the rule heading with
   `(DEPRECATED — see {NEW-ID})` and leave the body in place.
2. In `standards.yaml`, set `status: deprecated` and `replaced_by: NEW-ID`.
3. Skills binding to the deprecated rule surface a warning at validation
   time pointing at the replacement.

### Language ownership

| Language / Platform | Owner |
|---------------------|-------|
| Python | Platform — Data Engineering |
| Rust | Platform — Backend |
| Java | Platform — Spark / Compute |
| TypeScript | Platform — Frontend |
| SQL | Platform — Data Engineering |
| Databricks / UC | Platform — Data Platform |
| COMMON | Platform — Architecture |

The owning team approves additions, deprecations, and severity changes for
their language. Cross-cutting changes (severity, ID schema) require RFD
amendment.

## Task Automation: mise

All projects use [mise](https://mise.jdx.dev/) for task automation and tool
version management. Every repository includes a `mise.toml` at the root:

```toml
# mise.toml
[tools]
python = "3.12"
java = "zulu-21"
node = "20"

[tasks.fmt]
description = "Format all code"
run = [
    "ruff format .",
    "cargo fmt",
    "npx prettier --write .",
    "./gradlew spotlessApply",
]

[tasks.lint]
description = "Lint all code"
run = [
    "ruff check .",
    "cargo clippy -- -D warnings",
    "npx eslint . --max-warnings 0",
    "./gradlew checkstyleMain",
]

[tasks.check]
description = "Run all quality checks (format + lint + type check)"
depends = ["fmt", "lint"]
run = [
    "pyright",
    "npx tsc --noEmit",
]

[tasks.test]
description = "Run all tests"
run = [
    "pytest",
    "cargo test",
    "npx vitest run",
    "./gradlew test",
]
```

Not every repo has every language — tasks for absent languages are skipped.

| Command | What it does |
|---------|-------------|
| `mise run fmt` | Format all code |
| `mise run lint` | Lint all code |
| `mise run check` | Full quality gate (format + lint + type check) |
| `mise run test` | Run all tests |

mise replaces Makefiles, shell scripts, and npm scripts as the task runner.
It pins tool versions (Python, Java/Azul Zulu, Node) so every developer and
CI environment uses the same versions.

## Principles

These apply across all languages:

1. **Adopt the community standard.** Don't invent conventions when an
   authoritative one exists.
2. **Automate enforcement.** Every rule that can be checked by a tool must
   be checked by a tool. Code review focuses on design and logic.
3. **Explicit over implicit.** Type annotations, explicit error handling,
   named constants over magic numbers.
4. **Secure by default.** No secrets in code, no SQL injection, no
   unvalidated input at system boundaries. OWASP Top 10 awareness for all
   web-facing code.
5. **Test what matters.** Test behavior, not implementation. Prefer
   integration tests at system boundaries, unit tests for complex logic.

## Cross-Language Rules

These principles apply to **all** code regardless of language. Each
language's rules implement them concretely; future `COMMON-*` rules will
encode the cross-cutting versions explicitly.

### Secrets

- **NEVER** commit secrets, API keys, passwords, or tokens to source
  control.
- Use environment variables, Databricks secret scopes, or Harness secret
  manager.
- `gitleaks` runs in CI on every PR. A detected secret fails the pipeline.

### Dead Code

- **NEVER** commit commented-out code. Git history preserves it.
- **NEVER** leave TODO comments without a ticket reference:
  `// TODO(JIRA-1234): description`
- Ruff `ERA` (Python), Clippy (Rust), and ESLint `no-warning-comments`
  (TypeScript) enforce this.

### SQL Safety

- **ALWAYS** use parameterized queries.
- Python: parameter binding (`cursor.execute(sql, params)`) — `PY-SECURITY-002`
- Rust: `sqlx::query!` / `sqlx::query_as!` — `RS-SECURITY-005`
- TypeScript: query builder or parameterized statements
- Java: `PreparedStatement` with `?` placeholders — `JV-SECURITY-001`

### Error Handling

- **NEVER** swallow exceptions silently.
- **ALWAYS** catch the most specific exception type, not a broad base.
- **ALWAYS** preserve the original exception when wrapping (Python: `from
  e`, Rust: `#[from]`, Java: chained constructor, TypeScript: `cause`).

### Logging

- **NEVER** log sensitive data (credentials, PII, tokens, full request
  bodies with auth headers).
- Use structured logging with lazy evaluation:
  - Python: `logger.info("msg %s", var)` — `PY-IDIOM-015`
  - Rust: `tracing::info!(table = %name, "processing")` — `RS-LOG-002`
  - Java: `log.info("msg {}", var)` (SLF4J) — `JV-LOG-002`
  - TypeScript: structured logger with object args

## CI Enforcement

### Pipeline Architecture

Coding standards checks run as a **Quality Gate** stage in the Harness
pipeline. This stage runs on every PR and every merge to `main`. It is a
hard gate — if any check fails, the PR cannot merge.

```
┌─────────────────────────────────────────────────────┐
│ Stage 1: Quality Gate                               │
│                                                     │
│  Step 1: Detect Languages (path-based)              │
│    *.py → Python  *.rs → Rust  *.ts/*.tsx → TS      │
│    *.java → Java  *.sql → SQL                       │
│                                                     │
│  Step 2: Format Check (parallel per language)       │
│    ruff format --check | cargo fmt --check          │
│    prettier --check | spotlessCheck                 │
│                                                     │
│  Step 3: Lint (parallel per language)               │
│    ruff check | cargo clippy -D warnings            │
│    eslint --max-warnings 0 | checkstyle             │
│    sqlfluff lint                                    │
│                                                     │
│  Step 4: Type Check (parallel)                      │
│    pyright | tsc --noEmit                           │
│                                                     │
│  Step 5: Security Scan                              │
│    gitleaks detect                                  │
│    ruff check --select S (bandit rules)             │
│    findsecbugs (Java) | cargo audit (Rust)          │
│                                                     │
│  Step 6: Copilot Review (async, non-blocking)       │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Stage 2: Build (only if Quality Gate passes)        │
├─────────────────────────────────────────────────────┤
│ Stage 3: Deploy (only if Build passes)              │
└─────────────────────────────────────────────────────┘
```

### Harness Pipeline Template

The Quality Gate is a Harness pipeline template maintained in
`catalyst-domain-template`. Domain repos reference it:

```yaml
# .harness/pipeline.yaml (in each domain repo)
pipeline:
  name: Domain CI/CD
  stages:
    - stage:
        name: Quality Gate
        type: CI
        template:
          templateRef: quality_gate
          versionLabel: v1
    - stage:
        name: Build
    - stage:
        name: Deploy
```

The template is versioned. When coding standards change, the platform team
updates the template and bumps the version. Domain repos upgrade on their
own schedule.

### Language Detection

The pipeline inspects changed files to determine which checks to run. A PR
that only touches `.py` files skips Rust/TS/Java checks. This keeps CI fast
for focused changes.

```yaml
# Step 1 in the template
- step:
    name: Detect Languages
    type: Run
    spec:
      shell: Bash
      command: |
        CHANGED=$(git diff --name-only origin/main...HEAD)
        echo "$CHANGED" | grep -q '\.py$'     && echo "PYTHON=true"     >> $HARNESS_ENV
        echo "$CHANGED" | grep -qE '\.tsx?$'  && echo "TYPESCRIPT=true" >> $HARNESS_ENV
        echo "$CHANGED" | grep -q '\.rs$'     && echo "RUST=true"       >> $HARNESS_ENV
        echo "$CHANGED" | grep -q '\.java$'   && echo "JAVA=true"       >> $HARNESS_ENV
        echo "$CHANGED" | grep -q '\.sql$'    && echo "SQL=true"        >> $HARNESS_ENV
```

Each subsequent step runs conditionally:
```yaml
when:
  condition: <+stage.variables.PYTHON> == "true"
```

### Failure Behavior

| Check | On Failure | Developer Action |
|-------|-----------|-----------------|
| Format | Pipeline fails | Run `ruff format` / `cargo fmt` / `prettier --write` locally, push |
| Lint | Pipeline fails | Fix the violation or add inline suppression with justification comment |
| Type check | Pipeline fails | Fix the type error or add a narrowing assertion |
| Secret scan | Pipeline fails | Remove the secret, rotate it, push |
| Copilot review | Pipeline continues | Address or dismiss the comment on the PR |

The pipeline does **not** auto-fix. Developers run formatters locally and
push the fix. This keeps git history clean.

### Pre-commit Hooks (Recommended)

To catch issues before pushing:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-added-large-files
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.0
    hooks:
      - id: gitleaks
```

Pre-commit is recommended, not required. CI is the authoritative gate.

### GitHub Copilot Code Review

Copilot reviews every PR automatically. The instructions file
[`.github/copilot-instructions.md`](../../.github/copilot-instructions.md)
points Copilot at this RFD, sets review priorities by severity, and tells
Copilot to cite rule IDs in every suggestion.

Copilot review is **advisory** — it does not block merges. Linters are the
hard gate. Copilot's value is what linters cannot catch: unclear naming,
missing context in error messages, architectural concerns, missing tests
on new business logic, and design intent.

#### Why rule citations matter

Without rule IDs, Copilot says:
> Consider using `pathlib` here instead of string concatenation.

With rule IDs, Copilot says:
> **PY-IDIOM-010** — `pathlib` only; never string concatenation or `os.path`.
> The path on line 47 is built with `+`, which is OS-fragile and breaks on
> filenames with special characters. Use `Path(base_dir) / filename`.
> ([rule](python/idiom.md#py-idiom-010))

The second is **navigable** (click to the rule), **citable** (the author
can argue against the specific rule), and **measurable** (you can grep PR
comments for rule IDs and see which rules fire most).

#### Repository setup

1. Enable "Copilot code review" in repo settings → Code review → Copilot.
2. Add `.github/copilot-instructions.md` to the repo (provided by domain
   template).
3. Copilot reviews PRs automatically using the instructions.

#### Path-scoped instructions for VS Code

For developers using VS Code's Copilot Chat, add path-scoped instructions
so each language's full rule file loads only when working in that
language. Add to `.vscode/settings.json`:

```jsonc
{
  "github.copilot.chat.codeGeneration.instructions": [
    { "file": ".github/copilot-instructions.md" },
    { "file": "rfd/0008/python/", "applyTo": "**/*.py" },
    { "file": "rfd/0008/rust/", "applyTo": "**/*.rs" },
    { "file": "rfd/0008/typescript/", "applyTo": "**/*.{ts,tsx}" },
    { "file": "rfd/0008/java/", "applyTo": "**/*.java" },
    { "file": "rfd/0008/sql/", "applyTo": "**/*.sql" },
    { "file": "rfd/0008/databricks/", "applyTo": "**/{cluster,workflow,terraform}*.{tf,yaml,yml,json}" }
  ]
}
```

The github.com PR-review surface only reads the repo-wide
`.github/copilot-instructions.md`; path-scoped instructions are a VS Code
enhancement.

#### Validation

The standards are only useful if Copilot actually uses them. Track:

1. **Citations per rule.** Weekly:
   ```bash
   gh pr list --state merged --limit 100 --json comments \
     | jq -r '.[].comments[].body' \
     | grep -oE '(PY|RS|JV|TS|SQL|DBX)-[A-Z]+-[0-9]+' \
     | sort | uniq -c | sort -rn
   ```
   Tells you which rules Copilot cites most. Surprises here often surface
   rules that should be promoted to `error` severity, or rules that are
   too aggressive and produce false positives.

2. **Sample failure modes.** Pick 10 random Copilot comments per week.
   Score each:
   - Useful (caught a real issue)
   - Restated linter (CI already caught it)
   - Wrong (didn't apply or misread the code)
   - Hallucinated (invented a rule ID)

   If "restated linter" or "hallucinated" exceed 30%, refine the
   instructions. Hallucinated IDs in particular indicate the instructions
   need stronger "verify the ID exists in standards.yaml" guidance.

3. **Rules that never fire.** Compare the citation log against
   `standards.yaml`. Rules that go 90 days without a citation may be:
   - Genuinely never violated (kept in)
   - Too vague for Copilot to recognize (rewrite the rule)
   - Subsumed by a linter (mark as `linter: ...` and stop expecting Copilot)

4. **Author engagement.** Sample 20 PRs with Copilot comments. Did
   authors address or dismiss the comments? Pattern of dismissal
   signals rules that aren't earning their keep.

## Alternatives Considered

### No shared standard — each team decides

Maximum autonomy but leads to inconsistency. New contributors face different
conventions in every project. Code review becomes a style debate.

### Strict standard with no per-project flexibility

A single rigid configuration for all projects. Rejected because different
project types have different needs. The standard defines the baseline; teams
can add stricter rules but not weaken it.

### Custom style guide from scratch

Rejected because authoritative guides already exist (PEP 8, Rust API
Guidelines, Google Java Style Guide, Airbnb JS Guide) and are maintained by
communities with more experience than any single team. We adopt and document
deviations, not reinvent.

### Section-based prose vs rule-based numbered structure

The previous draft of this RFD organized standards by topic ("Naming
Conventions", "Error Handling") with prose under each. Rejected in favor of
rule-based numbered structure (Google C++ style guide model) because:

- Rules need to be addressable from outside the document — by skills, by CI,
  by code review references. A heading is not a stable address; an ID is.
- Mechanical authoring shape (Decision / Why / Exception / Examples) keeps
  contributions consistent and reviewable.
- A `standards.yaml` index becomes derivable from the rule shape.
- Skills can bind to ranges and wildcards (`PY-NAMING-*`,
  `PY-TYPE-001..015`), which is impossible against prose sections.

The cost is more visual repetition than prose; the benefit is a standard
that other systems can compose against.

## Impact

- **Economic:** Reduced code review time — reviewers cite rule IDs and move
  on. Faster onboarding for new contributors who already know the community
  standards.
- **Quality:** Automated linting catches bugs (bandit security checks,
  Clippy correctness lints, type-checked ESLint rules) that manual review
  misses.
- **Velocity:** Formatters eliminate style debates.
- **Security:** Language-specific security lints catch common
  vulnerabilities before code review.
- **Composability:** Future engineering skills inherit the standard via
  `metadata.standards` bindings instead of duplicating rules. Updates
  propagate automatically.

## Risks

- **Ruff adoption.** Teams using Black + flake8 + isort need to migrate.
  Mechanical but requires CI pipeline updates.
- **Clippy pedantic noise.** May need additional allows for legitimate
  false positives.
- **Copilot review quality.** Advisory only; may produce false positives.
  Linters are the hard gate.
- **Java version migration.** Teams on Java 8/11 need effort to reach 17,
  then 21. Java 11 is accepted as transitional. Azul Zulu replaces Oracle
  JDK; toolchain migration is a one-time CI change.
- **Rule-ID drift.** A rule renamed or restructured without preserving its
  ID breaks every skill binding. Governance section above codifies the
  stability contract.

## References

- [PEP 8](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ruff](https://docs.astral.sh/ruff/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Clippy](https://rust-lang.github.io/rust-clippy/master/)
- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Effective Java, 3rd Edition](https://www.oreilly.com/library/view/effective-java/9780134686097/)
- [Azul Zulu OpenJDK](https://www.azul.com/downloads/?package=jdk)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [dbt Style Guide](https://docs.getdbt.com/best-practices/how-we-style/0-how-we-style-our-dbt-projects)
- [sqlfluff](https://docs.sqlfluff.com/en/stable/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Copilot Code Review](https://docs.github.com/en/copilot/using-github-copilot/code-review/using-copilot-code-review)
- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) — reference for the rule-based document structure
