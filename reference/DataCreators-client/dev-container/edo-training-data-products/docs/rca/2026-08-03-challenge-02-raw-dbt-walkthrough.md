# RCA — Challenge 02 raw-dbt walkthrough: four defects found by a beginner trainee

| Field | Value |
|---|---|
| **Date** | 2026-08-03 |
| **Status** | Resolved on `feature/improvements` |
| **Severity** | High — one blocker plus three "the guide says X, reality is Y" defects, all on the happy path |
| **Components** | `challenges/02-dbt-pipeline/stubs/` + `dbt/models/` · `challenges/02-dbt-pipeline/README.md` · `tests/challenges/offline/test_ch02.py` |
| **Discovered while** | Running a beginner trainee agent end-to-end through Challenge 02 on a Windows host + devcontainer, after the raw-dbt conversion |
| **Related** | `docs/rca/2026-08-03-profiles-symlink-windows.md` · `docs/rca/2026-08-03-dbt-databricks-auth-hang.md` |

---

## 1. Summary

A trainee walked Challenge 02 from top to bottom. They finished, and
`mise run challenge:verify 02` passed (`PASS=17 WARN=0 ERROR=0`). But along the way they hit four
defects that a first-timer cannot distinguish from their own mistakes:

1. **Two stub files ship with stray SQL** left over from a botched find-replace, so a fresh clone
   fails `dbt build` with a Databricks syntax error pointing at a file the guide calls a placeholder.
2. **`dbt docs serve --port 8080` cannot run in this devcontainer** — two independent causes.
3. **`dbt show --select holdings_raw --limit 5` silently re-seeds the table** and returns 8 rows, not
   the 5 the guide promises.
4. **The `OPTIMIZE … ZORDER` post-hook never appears on the console**, yet the guide's entire "how to
   check" for that section is "watch it run".

All four are fixed, with regression tests for 1 and a rescoped test for 3.

---

## 2. Defect 1 — corrupt stubs (BLOCKER)

### Symptom

`challenges/02-dbt-pipeline/stubs/models/intermediate/int_holdings_enriched.sql` as committed:

```sql
-- int_holdings_enriched — TODO(Challenge 02 · intermediate): join holdings to prices and FX
select 1 as placeholder
        and p.price_date = h.position_date
    left join fx f
        on f.from_ccy = h.local_ccy
        and f.to_ccy = 'GBP'
        and f.rate_date = h.position_date
)

select * from joined
```

`fct_portfolio_returns.sql` had the same shape with 18 stray lines. Reproduced from pristine stubs:

```console
$ dbt build --select int_holdings_enriched
  select 1 as placeholder
          and p.price_date = h.position_date
  --------^^^
Done. PASS=0 WARN=0 ERROR=1 SKIP=0 NO-OP=0 TOTAL=1
```

### Root cause

A find-replace that swapped each solution body for `select 1 as placeholder` anchored on the
*beginning* of the SQL but not its end, so the tail of the original query survived. It affected
exactly the two longest models — the ones whose bodies contained a CTE close paren plus a final
`select`, which is what the replacement pattern failed to consume.

It slipped through for three reasons:

- **`dbt parse` does not catch it.** dbt parses Jinja, not SQL. `dbt parse` and `dbt ls` both succeed
  on the corrupt stubs; only a real `dbt build` sends the text to Databricks, which rejects it.
- **The corruption is invisible in the normal flow.** The guide has the trainee *author* these two
  files, overwriting the corruption before ever building them. It only bites someone who builds
  early, runs the verify gate before finishing, or resets mid-challenge.
- **No test asserted stub shape.** The existing tests checked that stubs *contain* a placeholder, never
  that they contain *nothing else*.

The guide meanwhile promises the opposite:

> each model file is a stub with a `TODO` comment naming its challenge and a `select 1 as placeholder`
> **so the project still parses**

### Fix

Both files, in `stubs/` and `dbt/`, reduced to their intended two lines. New regression test
`test_stubs_contain_no_stray_sql_after_the_placeholder` asserts that no line follows the placeholder in
any ch02 stub. Verified the guard fails on reintroduced corruption
(`assert not [')', 'select * from joined']`) and passes on the fixed tree.

`mise run challenge:reset 02` was confirmed to propagate the clean stubs into `dbt/`.

---

## 3. Defect 2 — `dbt docs serve --port 8080` cannot run (MAJOR)

### Symptom

```console
$ dbt docs serve --port 8080
socket.gaierror: [Errno -2] Name or service not known
```

and, once that is worked around:

```console
OSError: [Errno 98] Address already in use
```

### Root cause — two independent problems stacked

**(a) `DBT_HOST` is overloaded.** dbt-core defines `--host` for `docs serve` with
`envvar="DBT_HOST"` (`dbt/cli/params.py:309`), defaulting to `127.0.0.1`. This repo uses the same
name for something completely different — the Databricks workspace URL, set in `.mise/env.sh:102` and
consumed by every `profiles.yml` as `env_var('DBT_HOST', …)`. So `dbt docs serve` tries to bind a
local socket to `https://cg-db-…cloud.databricks.com` and the DNS lookup fails.

This is a genuine namespace collision, not a misconfiguration: both uses of `DBT_HOST` are reasonable
in isolation. `DBT_HOST` is load-bearing across `profiles.yml`, `setup-databricks-dbt.sh`,
`normalize-env.sh`, `dbt_wrapper.py`, and the Databricks job cluster definitions in
`atlas_elt/variables/clusters.yml`, so renaming it is a much larger change than this defect warrants.

**(b) Port 8080 is the Airflow UI.** Challenge 03 runs Airflow there; inside the devcontainer the
astro api-server holds `127.0.0.1:8080` via docker-proxy. Any trainee who does 02 and 03 in the same
session — or in either order without tearing down — collides.

### Fix

The guide now uses explicit flags and explains both reasons:

```bash
dbt docs generate
dbt docs serve --host 127.0.0.1 --port 8081
```

It also states that `docs serve` holds the terminal until **Ctrl-C**, which the guide never mentioned.
Port `8081` added to `forwardPorts` in `devcontainer.json` with a `dbt docs` label so VS Code surfaces
it. Verified: `HTTP 200` from `http://127.0.0.1:8081/`.

---

## 4. Defect 3 — the "peek" command mutates data and ignores `--limit` (MAJOR)

### Symptom

The guide's Section 1 "How to check":

```bash
dbt show --select holdings_raw --limit 5
```

> You should see five real holding rows

Reality:

```console
1 of 1 START seed file training_gqp.holdings_raw ... [RUN]
1 of 1 OK loaded seed file training_gqp.holdings_raw ... [INSERT 8 in 5.02s]
Previewing node 'holdings_raw':
 ... 8 rows ...
```

### Root cause

`--select holdings_raw` selects the **seed node**, and `dbt show` *builds* the node it selects. So the
"peek" re-runs the seed — a write — and then previews the whole loaded relation, where `--limit` does
not clip the output. A beginner reasonably reads `show` as a read-only operation; nothing in the guide
suggests it writes.

### Fix

Switch to a genuinely read-only query that also happens to teach the section's actual subject
(`source()`):

```bash
dbt show --inline "select * from {{ source('custodian', 'holdings_raw') }}" --limit 5
```

Verified: exactly 5 rows, no seed re-run. The guide now also contrasts the two forms explicitly
("selecting a node builds it; `--inline` just reads"), and the optional "try a variation" step — which
previously told trainees to run `dbt show` against `source('product_ref', 'fund_master_raw')` without
ever showing the syntax — is now actionable.

### Test fallout: an obsolete ban on `--inline`

`test_ch02.py::test_guide_avoids_inline_sql` asserted `"--inline" not in README.md`. Its rationale was
sound **for the mise wrapper**: `mise run challenge:dbt 02 -- show --inline "<SQL>"` pushes the SQL
through a mise variadic that word-splits on spaces. Confirmed still true:

```console
$ mise run challenge:dbt 02 -- show --inline "select 1 as a, 2 as b" --limit 1
dbt wrapper caught exception type=UsageError: UsageError("Got unexpected extra arguments (1 as a, 2 as b')")

$ dbt show --inline "select 1 as a, 2 as b" --limit 1     # raw dbt, same shell
Previewing inline node:
| a | b |
| 1 | 2 |
```

The raw-dbt conversion removed the wrapper from the guide, which made the blanket ban obsolete — but
the test was not updated with it, so it silently blocked the correct fix. Rescoped to
`test_guide_never_pairs_inline_sql_with_the_mise_wrapper`, which bans `--inline` only on lines that
also invoke `challenge:dbt`. The real constraint is preserved; the stale one is gone.

---

## 5. Defect 4 — the `OPTIMIZE` post-hook is invisible (MAJOR)

### Symptom

Guide, Challenge 9 "How to check":

> after the `OK created sql table model … agg_fund_exposure` line you should see the post-hook execute
> the `OPTIMIZE … ZORDER BY (fund_id, position_date)` statement

No such line ever appears on the console.

### Root cause

dbt does not echo hook SQL at the default log level; hooks are recorded only in the debug log. The
hook *does* run — proven two ways. First, it shows up 13 times in `logs/dbt.log`. Second, building an
unfinished stub fails *inside the hook*:

```console
Database Error in model fct_portfolio_returns
  [DELTA_ZORDERING_COLUMN_DOES_NOT_EXIST] Z-Ordering column fund_id does not exist in data schema.
```

which is only reachable if the post-hook executed. So the mechanism is correct and only the
instruction was wrong — the worst kind of doc bug, because the trainee's environment is fine and they
have no way to know that.

### Fix

The guide now states that dbt does not print hook SQL, and gives two commands that actually work:

```bash
grep "ZORDER BY" logs/dbt.log | tail -1
dbt --debug build --select agg_fund_exposure 2>&1 | grep "ZORDER BY"
```

Verified output:
`OPTIMIZE `training_dev`.`training_gqp`.`fct_portfolio_returns` ZORDER BY (fund_id, position_date)`

---

## 6. Lessons

1. **A passing verify gate is not a working challenge.** `challenge:verify 02` passed the whole time.
   It builds the *finished* pipeline, so it never touches the corrupt stubs, never runs `docs serve`,
   never runs a `show` peek, and never reads a hook log. Everything the trainee actually types is
   outside the gate.
2. **"Still parses" is not "still builds".** `dbt parse` validates Jinja, not SQL. Any claim that a
   skeleton is safe needs a `dbt build`/`compile` to back it, not a parse.
3. **Assert what a stub must NOT contain.** Tests checked stubs *contain* a placeholder; the bug was
   everything after it.
4. **When you delete a wrapper, revisit the tests written to work around it.** The `--inline` ban was
   correct for the mise path and became a trap the moment the guide moved to raw dbt. Conversions
   should sweep for tests whose stated rationale names the thing being removed.
5. **Doc claims about observable output need to be executed, not reasoned about.** Three of these four
   defects are "the guide says you will see X". Each needed one real run to disprove.
