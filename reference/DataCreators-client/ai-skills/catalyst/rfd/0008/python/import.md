# PY-IMPORT: Imports

Import grouping, ordering, and type-only import rules.

## PY-IMPORT-001 — Group imports per PEP 8

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `I` rules

**Decision.** Three groups, separated by one blank line:

1. Standard library (`os`, `sys`, `pathlib`, `datetime`)
2. Third-party packages (`pydantic`, `sqlalchemy`, `httpx`)
3. Local application (`from core.profile import profile_table`)

Alphabetized within each group.

**Why.** PEP 8. Ruff isort enforces this automatically.

**Exception.** None.

## PY-IMPORT-002 — Absolute imports only

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `TID252`

**Decision.** Use absolute imports. No relative imports (`from . import x`,
`from ..models import Y`).

**Why.** Absolute imports are stable across module moves and unambiguous
when grepping. Relative imports break when files are renamed or moved.

**Exception.** None.

## PY-IMPORT-003 — Move type-only imports under TYPE_CHECKING

**Severity:** warning
**Since:** v0.1.0
**Linter:** Ruff `TCH`

**Decision.** Imports used only in type annotations belong under
`if TYPE_CHECKING:`.

**Why.** Avoids circular imports and reduces import-time cost for runtime.

**Exception.** Forward references inside generic types may need runtime imports.

## PY-IMPORT-004 — Never use wildcard imports

**Severity:** error
**Since:** v0.1.0
**Linter:** Ruff `F403`, `F405`

**Decision.** Never use `from module import *`.

**Why.** Wildcard imports hide symbol origin, pollute namespaces, and
increase collision risk during refactors.

**Exception.** None.

## PY-IMPORT-005 — Import from defining modules, not transitive re-exports

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** In data pipelines, import models, transforms, validators, and
DQ checks from their defining module, not via package `__init__` transitive
re-exports, unless the package explicitly marks a stable public API.

**Why.** Direct imports reduce coupling to package internals and prevent
breakage when re-export layouts change.

**Exception.** Public API packages may expose stable facades intentionally.
For PY-IMPORT-005, public API means the package's documented, versioned
import surface intended for external consumers (typically explicit exports
in `__init__.py` and/or `__all__`).

**Example:**
```python
# Bad — transitive re-export import from package facade
from pipelines import orders_silver_model

# Good — import from the defining module
from pipelines.orders.silver import orders_silver_model

# Also good — package explicitly defines a stable public API facade
from pipelines.public_api import orders_silver_model
```

### Naming
