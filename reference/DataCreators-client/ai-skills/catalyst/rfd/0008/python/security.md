# PY-SECURITY: Security

Untrusted input, SQL injection, secret handling, deserialization.

## PY-SECURITY-001 — Never run dynamic code from untrusted input

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `S102`, `S307`

**Decision.** Never use Python's dynamic-code APIs on strings derived from
user input or external data. Reach for these built-ins only with
hard-coded, trusted inputs and explicit review.

**Why.** Code injection. Catastrophic.

**Exception.** None for untrusted input.

## PY-SECURITY-002 — Parameterized SQL only

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `S608`

**Decision.** Build SQL with the database driver's parameter binding.
Never construct SQL with f-strings, `.format()`, or `%`-formatting.

**Why.** SQL injection. Industry-standard catastrophe.

## PY-SECURITY-003 — No hardcoded secrets

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `S105`, `S106`, `S107`

**Decision.** Read secrets from environment variables, Databricks secret
scopes, or a vault client. Never commit a token, password, or key.

**Why.** Hardcoded secrets leak via git history, public repos, and
build artifacts.

**Exception.** Test-only sentinel values that don't grant access.

## PY-SECURITY-004 — Safe YAML loading only

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `S506`

**Decision.** Use `yaml.safe_load()`. Never `yaml.load()` without an
explicit `SafeLoader`.

**Why.** Default YAML loading can construct arbitrary Python objects,
which is code execution.

## PY-SECURITY-005 — No unsafe binary deserializers with untrusted data

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `S301`

**Decision.** Don't use unsafe binary deserializers (Python's standard
serialization library) on data crossing a trust boundary. Use JSON or
protobuf instead.

**Why.** The unsafe deserializer can execute arbitrary code on load.

**Exception.** Internal cache files written and read by the same trusted
process within a single deployment boundary.

## PY-SECURITY-006 — No shell-mode subprocess with variable input

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `S602`, `S603`, `S605`

**Decision.** Use `subprocess.run([...])` with a list of arguments. Never
the shell-mode invocation when input includes user-supplied or external
data.

**Why.** Shell injection.

## PY-SECURITY-007 — Validate external input at API boundaries

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** All input from outside the process — HTTP requests, message
broker payloads, file uploads, environment-derived strings — must be
validated at the boundary using pydantic models, FastAPI request models,
or explicit checks.

**Why.** Validation at the boundary lets internal code assume well-formed
data.
