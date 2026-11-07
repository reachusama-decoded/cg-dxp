# RS-IMPORT: Imports

Import grouping per workspace rustfmt.

## RS-IMPORT-001 — Group imports per workspace `rustfmt.toml`

**Severity:** error
**Since:** v0.1.0
**Linter:** rustfmt (`group_imports = "StdExternalCrate"`)

**Decision.** Three groups, separated by blank lines, alphabetized:

1. `std` / `core` / `alloc`
2. External crates (`serde`, `tokio`, `anyhow`)
3. Workspace and local crate (`use crate::...`)

**Why.** Matches the import-ordering convention across all language
standards. rustfmt enforces automatically.

**Examples.**
```rust
use std::collections::HashMap;
use std::sync::Arc;

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use tokio::sync::Semaphore;

use catalog_client::Client;

use crate::errors::CatalogError;
use crate::models::TableProfile;
```

## RS-IMPORT-002 — Crate-level import granularity

**Severity:** error
**Since:** v0.1.0
**Linter:** rustfmt (`imports_granularity = "Crate"`)

**Decision.** Imports from the same crate collapse into one `use` statement.

**Why.** Reduces visual noise. `use std::collections::{HashMap, HashSet};`
is clearer than two separate lines.

**Examples.**
```rust
// ✓
use std::collections::{HashMap, HashSet};

// ✗
use std::collections::HashMap;
use std::collections::HashSet;
```

## RS-IMPORT-003 — `use super::*` only in `#[cfg(test)]`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** `use super::*` is allowed only inside `#[cfg(test)]` test
modules.

**Why.** In production code, glob imports hide the dependency surface.
In test modules under the file they test, the convention is universal
and harmless.

### Naming
