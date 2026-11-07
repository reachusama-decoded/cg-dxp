# CONT-SETUP: Setup Tasks and Scripts

How the container bootstraps itself: committed scripts as the unit of vending,
idempotent and guarded tasks, and clean (emoji-free) output.

## CONT-SETUP-001 — Scripts are the unit of vending; tasks call scripts

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Setup logic lives in committed container setup scripts (for
example `.devcontainer/utils/normalize-env.sh`, `scripts/container/setup.sh`, or
`utils/setup-databricks-config.sh`). Task-runner tasks (`.mise.toml`,
`pyproject.toml` poe tasks) only invoke those scripts — a task body is a single
script call, not an inline shell block of setup logic.

**Why.** Scripts are what the vending process ships and updates centrally. When a
repo inlines the logic into a task body, two failure modes follow: (1) the
vended `.mise.toml` references `utils/*.sh` scripts that were never shipped, and
the container breaks on first run; (2) the inline copy drifts from canonical and
can no longer be re-vended. Keeping scripts as the unit of vending makes every
repo patchable from one place.

**Exception.** Trivial one-liners that call a single already-vended tool (for
example `run = "pytest"`).

**Examples.**
```toml
# ✗ — setup logic inlined into the task; cannot be re-vended, drifts from canonical
[tasks."setup:normalize-env"]
run = """
for key in DATABRICKS_HOST DATABRICKS_TOKEN; do
  val=$(printenv "$key"); export "$key=$(printf '%s' "$val" | sed 's/^"//;s/"$//')"
done
"""

# ✓ — task is a thin wrapper around a committed, vendable script
[tasks."setup:normalize-env"]
run = ".devcontainer/utils/normalize-env.sh"
```

## CONT-SETUP-002 — Setup scripts are idempotent and guard on missing inputs

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + shellcheck

**Decision.** Every setup script can run repeatedly with the same result and
skips gracefully — with a clear message — when a required input is absent. A
missing credential or optional template must not abort the whole setup.

**Why.** `postCreateCommand` re-runs on rebuild, and developers re-run setup
manually. A script that fails on a second run, or hard-fails when an optional
secret is unset, makes the container fragile. Guarding inputs lets a developer
get a working container before all credentials are filled in.

**Exception.** None.

**Examples.**
```sh
# ✓ — skip with guidance instead of failing the whole setup
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "Skipping ~/.databrickscfg generation (DATABRICKS_HOST or DATABRICKS_TOKEN unset)."
    exit 0
fi
```

## CONT-SETUP-003 — No emojis in container scripts or their output

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Container setup scripts, log lines, and generated messages use
plain text only — no emojis or decorative glyphs (checkmarks, crosses, warning
signs) in `echo` output or comments.

**Why.** This mirrors the platform-wide no-emoji standard. Decorative glyphs
render inconsistently across terminals and CI log viewers, and they are noise in
machine-parsed setup output. Plain status words ("Wrote", "Skipping", "Warning:")
are unambiguous everywhere.

**Exception.** None.

**Examples.**
```sh
# ✗
echo "✓ Databricks environment variables normalized"

# ✓
echo "Databricks environment variables normalized (surrounding quotes removed)."
```
