---
name: challenge-trainee-runs
description: Use when validating that the training challenges (02 dbt, 03 Airflow, 04 Atlas capstone) still work for a trainee - runs a challenge end to end as a beginner via a subagent, audits the result against artifacts rather than the agent's own report, and records it in the run ledger. Admin/maintainer workflow, not for trainees working through a challenge.
---

# Running the Challenges as a Trainee (maintainer workflow)

Validates that a challenge still works end to end for a beginner, by having a subagent work
through it literally and reporting what actually happened.

**This is not for helping someone through a challenge.** If a trainee is stuck, help them in
place — never reset their working tree.

## The Iron Law

```
NEVER `challenge:reset` UNLESS YOU ARE STARTING A VALIDATION RUN THE USER ASKED FOR
```

`mise run challenge:reset <NN>` deletes the trainee's authored files, including the ones they
created from scratch. "Help me run challenge 02" is a request for help, not a validation run.
When in doubt, ask.

## Before you start

Run **one challenge at a time. Never two concurrently.**

- **Resource exhaustion is the binding constraint.** A challenge 03 run starts five Airflow
  containers *inside* the devcontainer via Docker-in-Docker, on top of a devcontainer measured
  at ~4.2 GiB. On Windows all of it shares one memory-capped WSL2 VM, and concurrent runs have
  **taken the Docker daemon down** in practice.
- Challenges 02 and 03 also build identical relation names (`stg_*`, `int_*`,
  `fct_portfolio_returns`, `agg_fund_exposure`) into the same schema and would corrupt each
  other. Challenge 04 uses disjoint names and a separate `atlas_seeds` schema — that removes
  the *data* conflict but not the resource one, so it still runs alone.

Check headroom before starting and periodically during a long run:

```bash
docker stats --no-stream --format "{{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}"
```

Stop the Airflow stack between challenges (`astro dev stop`) rather than leaving it up. **If
the daemon crashes mid-run the run is void** — re-run it rather than recording partial results,
or you will log a false regression.

## Steps

1. **Dispatch the subagent** using the brief in `docs/challenge-run-brief.md`. Do not improvise
   a prompt — the brief carries the scope limits and the audit rules, and an agent without them
   will report `PASS` for steps it quietly worked around.
2. **Audit the finished run against artifacts** (next section). Do this before believing
   anything in the report.
3. **Append one row** to `docs/challenge-runs.md`, including the **host OS**. Capture it
   before you forget which machine ran it:

   ```bash
   # macOS
   sw_vers | tr '\n' ' '; uname -m
   # Windows (PowerShell)
   (Get-ComputerInfo).OsName; $env:PROCESSOR_ARCHITECTURE
   # Linux
   . /etc/os-release && echo "$PRETTY_NAME $(uname -m)"
   ```

   Record the **host** — the machine Docker Desktop runs on — not the devcontainer, which is
   always Linux (`linuxkit`) whatever the host. The host is where behaviour actually diverges:
   a tracked symlink once broke Windows clones
   (`docs/rca/2026-08-03-profiles-symlink-windows.md`), concurrent runs have crashed the Docker
   daemon on Windows where everything shares one memory-capped WSL2 VM, and line endings, path
   separators and case-sensitivity all differ. It also lets you *disprove* an OS theory, which
   is the more common outcome — the failure that started this work was reported as
   Windows-specific and reproduced immediately on macOS.
4. **Write an RCA** in `docs/rca/` only if you found a root cause *and* fixed it.
5. **Reset the working tree** so the next run starts clean.

## Auditing — do not skip

An agent that "helpfully" fixes a broken command and reports `PASS` is indistinguishable from
a real pass. Prompt rules are not verification. Every check below has caught something real:

| Check | Command |
|---|---|
| Scope — edited anything it shouldn't? | `git status --porcelain` |
| Actual commands run, with flags | `grep -o "'invocation_command': '[^']*'" <project>/logs/dbt.log` |
| Airflow tasks really ran (ch03) | query `dag_run` / `task_instance` in the metadata DB |

Full commands are in `docs/challenge-run-brief.md`.

Two traps, both hit in practice:

- **`logs/dbt.log` is not session-scoped.** It survives `challenge:reset` and contains
  invocations from earlier sessions. Check timestamps before calling something a repeat.
- **A reported root cause is a hypothesis, not a finding.** A challenge 03 run confidently
  reported a cause for a Section 4 failure; it failed to reproduce under three separate
  conditions and would have been written into the guide as fiction.

## Recording the result

Only two things are kept, because a per-run document is mostly "everything passed" and scales
with the number of runs:

| Artifact | Lives | When |
|---|---|---|
| Raw agent report | PR comment / session workspace — **not committed** | every run |
| Row in `docs/challenge-runs.md` (incl. host OS) | forever, one line | every run |
| RCA in `docs/rca/` | forever | only a verified, fixed root cause |

The ledger's value is that fixed columns make runs comparable — *did 03 regress after the dbt
upgrade? which commit made it pass?* Prose reports cannot answer that.
