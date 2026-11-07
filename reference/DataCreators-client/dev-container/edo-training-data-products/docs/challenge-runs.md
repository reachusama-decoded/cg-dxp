# Challenge Run Ledger

One row per agent run of a challenge. **Append only — never rewrite history**, because the
value of this file is the comparison between rows, not any single row.

## Why this file exists (and why there is no per-run document)

A finished run produces a long report: every step, verbatim errors, documentation
mismatches. That report is the right thing to *read* while deciding what to fix, and the
wrong thing to *keep*. It is long, it goes stale the moment the bug is fixed, and it can be
confidently wrong — a run of challenge 03 on 2026-08-04 reported a root cause for its
Section 4 failure that did not survive testing under three separate conditions.

So reports are treated as leads with a lifespan of hours, and only two things are kept:

| Artifact | Lives | Written when |
|---|---|---|
| Raw agent report | PR comment or session workspace — **not committed** | every run |
| **A row in this file** | forever, one line | every run |
| RCA in `docs/rca/` | forever | only when a root cause is found **and** fixed |

Fixed columns are the point. They let you answer questions prose cannot:
*did challenge 03 regress after the dbt upgrade?* · *has anyone run 04 since the YAML
change?* · *which commit made 03 start passing?* Rows 2 and 3 below answer that last one.

## How to record a run

1. Run the challenge using the brief in `docs/challenge-run-brief.md` (it carries the audit
   rules — without them an agent can report `PASS` for a step it quietly worked around).
2. Paste the agent's report into the PR, or leave it in the session workspace. Do not commit it.
3. Append one row here.
4. Write an RCA **only** if you found a root cause and fixed it, then link it in the row.

**Result** is `steps passed / steps attempted`, or `blocked at <step>` if the run could not
continue. **Blockers** names the cause in a few words, not the symptom.

**Host OS** is the machine Docker Desktop runs on — `Windows 11 (WSL2)`, `macOS 26.5 (arm64)`,
`Ubuntu 24.04` — **not** the devcontainer, which is always Linux (`linuxkit`) whatever the
host. The host is where the differences actually bite, and this repo has been bitten
repeatedly:

- `docs/rca/2026-08-03-profiles-symlink-windows.md` — a tracked symlink broke Windows clones.
- Concurrent runs have crashed the Docker daemon on Windows, where everything shares one
  memory-capped WSL2 VM; the same load is survivable elsewhere.
- Line endings, path separators and case-sensitivity all diverge by host.

Recording it also lets you **disprove** an OS theory, which is the more common outcome. The
Phase 2 Challenge 2 failure that started this work was reported as "failing on my Windows
machine"; it reproduced first try on macOS and was entirely platform-independent. With rows
from more than one host you can see that in the ledger instead of chasing it.

## Runs

| Date | Ch | Host OS | Model | Result | Blockers | RCA | Commit |
|---|---|---|---|---|---|---|---|
| 2026-08-04 | 02 | macOS 26.5 (arm64) | claude-sonnet-5 | 18/18 (after fix) | Phase 2 Challenge 2: dbt's eager indirect selection ran a `relationships` test whose other input was still a stub | `2026-08-04-challenge-02-eager-indirect-selection.md` | c4acb62 |
| 2026-08-04 | 03 | macOS 26.5 (arm64) | claude-sonnet-5 | **blocked at Prerequisites** | Airflow booted with blank `DBT_CATALOG`; DAG never imported. Guide's own documented fix did not work | `2026-08-04-databricks-env-not-propagated-to-shells.md` | — |
| 2026-08-04 | 03 | macOS 26.5 (arm64) | claude-sonnet-5 | 21/21 | none — re-run confirming the env fix; cold-booted Airflow itself | — | c4acb62 |
| 2026-08-04 | 04 | macOS 26.5 (arm64) | claude-sonnet-5 | 24/24 | none blocking; `verify 04` PASS and full build `PASS=46 ERROR=0` | — | c4acb62 |
| 2026-08-05 | 02 | Windows 11 Enterprise (WSL2, x86_64) | claude-sonnet-5 | 18/18 | none blocking; two doc-vs-code mismatches — README claimed every source carries freshness (`product_ref` carries none, so freshness covers 5 of 6 tables), and `bloomberg.prices_raw` had no `columns:` block so the trainee could not discover `quote_ccy` and guessed `ccy_cd` | — | b9380b0 |
| 2026-08-05 | 03 | Windows 11 Enterprise (WSL2, x86_64) | claude-sonnet-5 | 21/21 | none blocking; Section 10's Solution block ran `tasks clear … --yes` unscoped, re-executing all 9 historical DAG runs (~20 min unrequested compute); also 3rd mart `agg_fund_daily_exposure` undocumented, `Marking task as SUCCESS` wording is Airflow 2.x, and two "author this" callbacks ship complete | `2026-08-05-challenge-03-unscoped-tasks-clear.md` | b9380b0 |
| 2026-08-05 | 04 | Windows 11 Enterprise (WSL2, x86_64) | claude-sonnet-5 | 30/32 | `verify 04` rewrote tracked `package-lock.yml` to a machine-specific absolute path; Challenge 7's printed `dbt test` hit the same eager-indirect-selection trap as challenge 02 (closes that RCA's follow-up); plus wrong sample row, `tag:domain-aligned` builds 13 not 9, and a false "throwaway copy" claim | `2026-08-05-challenge-04-verify-rewrites-package-lock.md` | b9380b0 |
| 2026-08-05 | 02 | macOS 26.5 (arm64) | claude-sonnet-5 | 20/20 | none; confirmed the Windows fixes — `bloomberg.prices_raw`'s `quote_ccy` is now discoverable from `sources.yml` alone (authored `stg_prices` without opening the CSV or Solution), and `dbt source freshness` reports exactly the 5 sources the README claims. Only nit: S3's optional variation had nothing left to add | — | 180d33e |
| 2026-08-05 | 03 | macOS 26.5 (arm64) | claude-sonnet-5 | 20/21 | none blocking. Section 10's CLI clear was declined per stop-condition: `-s`/`-e` scope a calendar **day**, so it still matched 34 tasks across 2 runs (improved from 9 runs, but not run-scoped — UI is). Agent also reported the dependency chain was unenforced; **disproved** — DagBag structure and real run timings both show correct `start -> gate -> group -> publish -> end` ordering | — | 180d33e |
| 2026-08-05 | 04 | macOS 26.5 (arm64) | claude-sonnet-5 | 31/31 | none; all three Windows fixes confirmed — `verify 04` left `package-lock.yml` byte-identical (checked before/after, twice), Challenge 7's printed command avoids the eager-indirect-selection trap (agent proved the trap still exists by contrast-running it without the flag), and Quick Start's `PASS=35 ERROR=5` matched exactly. Full build `PASS=46 ERROR=0` | — | 180d33e |
| 2026-08-06 | 02 | Windows 11 Enterprise (WSL2, x86_64) | claude-sonnet-5 | 20/20 | none — regression run after the macOS edits; report audited against `dbt.log` (the one non-guide-looking flag, `--no-partial-parse`, is the guide's own at line 755) | — | 40be1bc |
| 2026-08-06 | 03 | Windows 11 Enterprise (WSL2, x86_64) | claude-sonnet-5 | 26/26 | none blocking; the macOS Section 10 rewrite validated itself — the trainee independently hit the documented limitation that `-s`/`-e` cannot select a `dags trigger` run. Found Section 4's "no scheduler, no DB record" false on Airflow 3: `tasks test` leaves a real DagRun (confirmed in the metadata DB at `logical_date=2026-05-04`, `try_number=3`) | — | 40be1bc |
| 2026-08-06 | 04 | Windows 11 Enterprise (WSL2, x86_64) | claude-sonnet-5 | 30/32 | `package-lock.yml` stayed clean across all 3 gates, confirming the Windows fix holds. Challenge 10's `grep target/run/...` cannot work: `dbt_project.yml` sets `target-path` to a Unity Catalog Volume, and the incremental filter lives in `compiled/`, not `run/` | — | 40be1bc |
| 2026-08-31 | 04 | macOS (arm64; version unavailable in container) | GitHub Copilot | 67/67 (twice) | none after fix; full live gate built 28 models and passed 8 tests, all 11 Atlas DAGs loaded, and reset restored starter state after both runs | `2026-08-31-challenge-04-from-scratch-gaps.md` | 42430fc |

## Reading the seed rows

Rows 2 and 3 are the same challenge on the same day — blocked, then clean. That contrast is
the whole record of the largest fix in `c4acb62`, in two lines.

Row 1 is the case for auditing rather than trusting: that run reported every step green
*after* the fix, but its own `dbt.log` showed a command repeated three times at Challenge 6.
The explanation held up, but nothing in the narrative report would have prompted the question.
