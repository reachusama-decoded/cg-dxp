# third-party/

This folder exists because Catalyst vendors and forks content from
`databricks-solutions/ai-dev-kit` under a Databricks custom license, and that
license places obligations on us that persist regardless of whether we
redistribute the code.

## What's in here

- **`LICENSE-databricks.md`** — full text of the Databricks custom license
  covering the vendored ai-dev-kit content. Includes a **Wipe runbook** at the
  bottom that we are obligated to execute if the upstream Databricks MCSA or
  this license terminates.
- **`NOTICE.md`** — attribution for the ai-dev-kit upstream plus the
  transitive third-party components that came with the vendored
  `databricks_tools_core` Python module.

## Why we keep it (and what we don't keep)

The Databricks license places obligations on **use**, not just on
distribution: the Scope of Use clause, the wipe runbook on termination, and
the requirement to preserve attribution. Those obligations apply to us as an
internal consumer, so the license text and attribution stay in the repo.

Apache 2.0 forks (e.g. `dbt-labs/dbt-agent-skills`) are intentionally **not**
tracked here. Apache §4 redistribution clauses only fire when the work is
distributed outside the organization; internal-only use doesn't trigger them.
The upstream commit hash is recorded in each forked skill's frontmatter
(`upstream-commit`, `upstream-repo`) for provenance, which is documentation,
not legal compliance.

If we ever externalize Catalyst (publish a skill bundle, share with a partner,
open-source any of this), the Apache-side attribution work would need to be
redone before that happens.

## When forking more Databricks-licensed content

1. Add the forked path to the **list of forked skill directories** in
   `NOTICE.md` (under the ai-dev-kit section).
2. Confirm the same path is covered by the `git rm` commands in the
   `LICENSE-databricks.md` Wipe runbook. Update the runbook if not.
3. Record `upstream-repo`, `upstream-commit`, and `catalyst-modifications`
   in the new skill's frontmatter.

## When forking from a new upstream (not Databricks)

If the new upstream is under a copyleft or use-restricted license (anything
beyond Apache / MIT / BSD), add a license file to this folder and a section
to `NOTICE.md`, and extend `tests/ci/test_license_files.py` so the file is
required to exist.
