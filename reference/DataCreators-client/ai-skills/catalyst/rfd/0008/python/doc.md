# PY-DOC: Documentation

Docstring requirements and Google docstring format.

## PY-DOC-001 — All public symbols have docstrings

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `D`

**Decision.** All public modules, classes, functions, and methods must have
a docstring.

**Why.** Public API needs explanation. The type signature shows shape; the
docstring shows behavior, edge cases, and intent.

**Exception.** Trivial property accessors and dunder methods that match
the standard contract.

## PY-DOC-002 — Google docstring format only

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `D` (Google convention)
**url:** https://google.github.io/styleguide/pyguide.html

**Decision.** Use the Google docstring format. Not Sphinx rST. Not NumPy.

**Why.** Google's Python style guide extends PEP 8 with more prescriptive
standards for documentation, typing, and consistency across teams.
Organizations often prefer it because clear, enforceable conventions reduce
review friction and improve long-term maintainability. Tooling (Sphinx,
mkdocs, IDE hovercards) expects one format per project.

**Exception.** None.

## PY-DOC-003 — First line is one imperative sentence

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `D`

**Decision.** The first line of a docstring is a single imperative sentence
ending with a period. Fits on one line.

**Why.** Tooling and IDEs use the first line as the summary.

**Exception.** None.

**Example:**
```python
def load_config(path: Path) -> dict[str, Any]:
    """Load application configuration from a YAML file."""
    ...
```

## PY-DOC-004 — Include Args / Returns / Raises sections when applicable

**Severity:** warning
**Since:** v0.1.0
**Linter:** Ruff `D`

**Decision.** Document parameters, return values, and raised exceptions
using Google-format sections. Omit sections that don't apply.

**Why.** Standardized sections make docstrings parseable by tooling.

**Exception.** Trivial functions where the signature is fully self-describing.

**Example:**
```python
def connect_to_next_port(self, minimum: int) -> int:
    """Connect to the next available port.

    Args:
      minimum: A port value greater or equal to 1024.

    Returns:
      The new minimum port.

    Raises:
      ConnectionError: If no available port is found.
    """
    ...
```

## PY-DOC-005 — No redundant docstrings

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't repeat what the signature already says. Add context
the signature doesn't convey.

**Why.** Redundant docstrings rot — when the signature changes, the docstring
gets stale.

### Error Handling
