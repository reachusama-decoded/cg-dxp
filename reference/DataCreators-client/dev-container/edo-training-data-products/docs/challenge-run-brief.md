# Challenge Run Brief (template)

Copy the block below into a background agent to run a challenge as a beginner trainee.
Replace `<NN>`, `<WORKING_PATH>`, `<CONTAINER_ID>` and `<HOST_REPO_PATH>`.

Record the outcome in `docs/challenge-runs.md` afterwards.

## Per-challenge values

| `<NN>` | `<WORKING_PATH>` (the only path the agent may edit) |
|---|---|
| `02` | `challenges/v1/02-dbt-pipeline/dbt` |
| `03` | `data_products/portfolio_analytics` |
| `04` | `data_products/atlas_elt` |

Find `<CONTAINER_ID>` with `docker ps` (image `vsc-edo-training-data-products-*`).

---

## The brief

> You are role-playing a BEGINNER TRAINEE working through a hands-on training challenge.
> Follow the guide **literally** and report exactly what happens — including failures. You
> are a test subject, NOT a fixer.
>
> ### Absolute rules
>
> 1. **You may ONLY create or edit files under `<WORKING_PATH>`**, and only where the guide
>    tells the trainee to author something. Do NOT touch `challenges/`, `.mise.toml`,
>    `tests/`, `docs/`, `.devcontainer/`, or any other data product. If you notice changes
>    elsewhere in the repo, ignore them — do not revert or comment on them.
> 2. **When a documented command fails, do NOT work around it, do NOT change the command, do
>    NOT debug the repo.** Record it verbatim and continue if later steps still can. If truly
>    blocked, stop and report.
> 3. Run every command **exactly as the guide prints it**. Never add flags the guide does not
>    show. If you believe a command needs an extra flag to work, that is a BUG TO REPORT, not
>    something to silently fix.
> 4. **If you run the same command more than once, say so and explain why.** The tools' own
>    logs are audited; unexplained repeats are treated as concealed failures.
> 5. Report documentation mismatches **even when the exit code is 0** — wrong row counts,
>    wrong column or file names, output that differs from what the guide describes, or guide
>    text contradicted by what the repo ships.
> 6. You may read the guide's `<details><summary>Solution</summary>` blocks and use that code;
>    trainees are explicitly invited to.
>
> ### Environment
>
> The toolchain exists ONLY inside the running devcontainer. The repo is bind-mounted, so
> files you edit on the host appear in the container instantly.
>
> - Host repo path (edit files here): `<HOST_REPO_PATH>`
> - Container ID: `<CONTAINER_ID>`
> - Container repo path: `/workspaces/edo-training-data-products`
>
> Use this exact wrapper for every command:
>
> ```bash
> docker exec <CONTAINER_ID> bash -lc 'export PATH="$PATH:/root/.local/bin:/root/.local/share/mise/shims"; cd /workspaces/edo-training-data-products/<WORKING_PATH> && mise exec -- dbt <ARGS> 2>&1 | tail -40'
> ```
>
> - `mise exec --` is required: a `docker exec` shell is non-interactive and non-login, so it
>   does not load the Databricks settings. This is still raw `dbt` — the guides teach raw dbt,
>   never the `mise run challenge:dbt` wrapper.
> - For `mise run <task>` (verify and reset only), `cd` to the repo root and drop
>   `mise exec --`.
> - Use a generous `initial_wait` (300–900s). Databricks builds are slow.
> - **Never run a blocking command** (`dbt docs serve`, any foreground server). Skip it and
>   say so.
> - **Never run two `dbt` commands concurrently in the same project.** They share project
>   state, and a parallel invocation has returned a *false empty result* — headers with no
>   rows, which reads exactly like a genuine data bug. Run them one at a time.
>
> ### Task
>
> 1. Start clean: `mise run challenge:reset <NN>`.
> 2. Read `challenges/<NN>-*/README.md` **in full**.
> 3. Work **every** section in order, running **every** command the guide prints, including
>    each `mise run challenge:verify <NN>` gate.
> 4. Compare every observed output against what the guide claims.
>
> ### Report back
>
> - A table of every section/step: PASS or FAIL.
> - For every FAIL: the exact command, verbatim error output (10–30 relevant lines), and what
>   the guide claimed would happen instead.
> - Documentation mismatches, even at exit 0.
> - Every repeated command, with the reason.
> - The final `mise run challenge:verify <NN>` output, verbatim.
> - The container architecture (`uname -sm` inside the devcontainer), so the ledger row can
>   record which host/arch combination this run covers.
>
> Quote real output; never paraphrase. An unreported mismatch is a missed bug.

---

## Before the run

**Run one challenge at a time.** Never start a second while one is in flight. A challenge 03
run adds five Airflow containers *inside* the devcontainer (Docker-in-Docker) on top of a
devcontainer already using ~4 GiB; on Windows all of it shares one memory-capped WSL2 VM, and
two concurrent runs have taken the Docker daemon down. Challenge 04 writes to disjoint
relation names so it cannot corrupt 02/03 data — but that is a data argument, not a resource
one, so it still runs alone.

Before starting, and periodically during a long run, check headroom on the host:

```bash
docker stats --no-stream --format "{{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}"
```

If the devcontainer is near its limit, stop the Airflow stack between challenges
(`astro dev stop`) instead of leaving it running. If the daemon crashes mid-run, treat the
run as void: re-run it rather than recording partial results.

## Auditing the run (do this, do not skip it)

An agent that "helpfully" fixes a broken command and reports `PASS` looks identical to a
genuine pass. Prompt rules are not verification. Each check below caught something real:

**1. Scope — did it edit anything it should not have?**

```bash
git status --porcelain | grep -v '^ M <WORKING_PATH>/'
```

Take a checksum baseline first if you want certainty:

```bash
git ls-files | grep -v '^<WORKING_PATH>/' | xargs shasum -a 256 > /tmp/baseline.txt
# after the run
shasum -a 256 -c /tmp/baseline.txt | grep -v ': OK$'
```

**2. Commands — what did it actually run?** dbt records the literal command line of every
invocation, including flags, and the agent cannot edit that:

```bash
grep -o "'invocation_command': '[^']*'" <WORKING_PATH>/**/logs/dbt.log | sed "s/.*: '//;s/'$//" | cat -n
```

Watch for flags the guide does not show — that is a worked-around failure. **Caveat:
`logs/dbt.log` is not session-scoped**; it is not cleared by `challenge:reset` and contains
invocations from earlier sessions, so check timestamps before calling something a repeat.

**3. Airflow runs (challenge 03) — did tasks really run?** Query the metadata database
rather than trusting the report:

```sql
SELECT dr.run_id, dr.state, count(ti.task_id)
FROM dag_run dr LEFT JOIN task_instance ti
  ON ti.dag_id = dr.dag_id AND ti.run_id = dr.run_id
WHERE dr.dag_id = 'portfolio_analytics_daily'
GROUP BY dr.run_id, dr.state, dr.start_date ORDER BY dr.start_date DESC;
```

**4. Independently re-run anything you intend to act on.** A run of challenge 03 on
2026-08-04 reported a confident root cause that failed to reproduce under three separate
conditions. Treat reported causes as hypotheses, not findings.

## After the run

1. Append a row to `docs/challenge-runs.md`.
2. Paste the raw report into the PR or leave it in the session workspace — do not commit it.
3. Write an RCA in `docs/rca/` **only** if you found a root cause and fixed it.
4. Reset the working tree: `mise run challenge:reset <NN>`.
