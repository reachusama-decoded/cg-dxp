# RCA — Challenge 02 Phase 2 Challenge 2 fails for every trainee, because dbt eagerly runs a test whose other input is still a stub

| Field | Value |
|---|---|
| **Date** | 2026-08-04 |
| **Status** | Root cause proven; fix implemented and verified live |
| **Severity** | High — a hard, deterministic blocker on a guided training step, on every OS |
| **Components** | `challenges/02-dbt-pipeline/README.md` (Phase 2, Challenge 2) · `challenges/02-dbt-pipeline/dbt/models/marts/schema.yml` · dbt node selection (`--indirect-selection`) |
| **Discovered while** | Reproducing a trainee report that Challenge 02 "fails in Phase 2 step 2 on my Windows machine" |
| **Related** | `docs/rca/2026-08-03-challenge-02-raw-dbt-walkthrough.md` (introduced the raw-`dbt` walkthrough commands this RCA repairs) |

---

## 1. Summary

Phase 2, Challenge 2 tells the trainee to build two intermediate models and check them:

```bash
dbt build --select int_fund_attributes int_positions_dated
dbt show --select int_fund_attributes --limit 10
```

**Both commands fail**, with an error that names neither the cause nor the fix:

```
[UNRESOLVED_COLUMN.WITH_SUGGESTION] A column, variable, or function parameter with name
`fund_id` cannot be resolved. Did you mean one of the following? [`placeholder`].
```

The two models the trainee wrote are correct and build fine. What fails is a **third node the
trainee never selected and has not yet written**: the `relationships` test that
`models/marts/schema.yml` declares between `fct_portfolio_returns.fund_id` and
`int_fund_attributes.fund_id`.

> **Root cause: that test has two inputs, and dbt's default indirect selection (`eager`) runs a
> test as soon as *any one* of its inputs is selected. Selecting `int_fund_attributes` is
> therefore enough to run it — but its other input, `fct_portfolio_returns`, is still the
> untouched `select 1 as placeholder` stub until Challenge 4, two challenges later.**

The reported "Windows" framing was a red herring. The failure is deterministic and
platform-independent; it was reproduced on macOS in the Linux devcontainer on the first attempt.

---

## 2. Impact / who was affected

- **Every trainee, on every OS, every time.** Nothing about this is environmental, timing-based, or
  flaky — the guide's own commands cannot succeed at that point in the guide.
- Both "How to check" commands for the step fail, so the trainee has **no** way to verify their work
  as written.
- The error is actively misleading. It points at `fund_id` on a mart the trainee has not been asked
  to write yet, and its only hint (`Did you mean [placeholder]`) describes scaffolding the guide told
  them to ignore. A beginner has no way to connect this to node selection.
- Highest-cost failure mode for training: the trainee's own SQL was correct, so the error teaches
  them to distrust correct work.

---

## 3. Symptoms

| What you see | What it actually means |
|---|---|
| `ERROR relationships_fct_portfolio_returns_fund_id__fund_id__ref_int_fund_attributes_` | dbt ran a test you did not select |
| `Did you mean one of the following? [`placeholder`]` | The test queried a model that is still a stub |
| `Done. PASS=2 WARN=0 ERROR=1 SKIP=0 TOTAL=3` | Your **2 models built fine**; the 3rd node is the uninvited test |
| `dbt show --select int_fund_attributes --limit 10` fails with the *same* error | `show` uses the same indirect selection, so it previews the test node too |
| Challenge 1 (`int_holdings_enriched`) worked a minute earlier | No test references that model, so nothing extra was pulled in |

`TOTAL=3` from a two-model selection is the signature of this bug.

---

## 4. Root cause

### 4.1 The test that gets pulled in

`challenges/02-dbt-pipeline/dbt/models/marts/schema.yml` ships complete — by design, so Challenge 5
can be "read it and run it" rather than "write it". It contains:

```yaml
models:
  - name: fct_portfolio_returns
    columns:
      - name: fund_id
        tests:
          - not_null
          - relationships:
              to: ref('int_fund_attributes')
              field: fund_id
```

A `relationships` test is the only generic test in this project with **two** model inputs: the model
it is attached to (`fct_portfolio_returns`) and the model it points `to` (`int_fund_attributes`).

### 4.2 Why selecting one model runs it

dbt does not require you to name tests; it infers them from the models you select. That inference is
called **indirect selection**, and its default mode is `eager`:

| Mode | A test runs when… |
|---|---|
| `eager` (default) | **any one** of the test's inputs is selected |
| `cautious` | **all** of the test's inputs are selected |
| `buildable` | all inputs are selected, or are ancestors of the selection |

Challenge 2 selects `int_fund_attributes`. Under `eager`, that single input is sufficient, so dbt
adds the relationships test to the run. Measured directly:

```
$ dbt ls --select int_fund_attributes int_positions_dated
portfolio_analytics_challenge.intermediate.int_fund_attributes
portfolio_analytics_challenge.intermediate.int_positions_dated
portfolio_analytics_challenge.marts.relationships_fct_portfolio_returns_fund_id__fund_id__ref_int_fund_attributes_
```

Two models selected, **three** nodes returned.

### 4.3 Why the test cannot pass yet

The trainee does not author `fct_portfolio_returns` until **Challenge 4**. At Challenge 2 it is still
the shipped stub:

```sql
-- fct_portfolio_returns — TODO(Challenge 02 · fact): publish the daily portfolio fact
select 1 as placeholder
```

So the compiled test reads a column that does not exist:

```sql
with child as (
    select fund_id as from_field
    from `training_dev`.`training_gqp`.`fct_portfolio_returns`   -- only column: placeholder
    where fund_id is not null
), ...
```

Hence `UNRESOLVED_COLUMN ... Did you mean [placeholder]`.

### 4.4 Blast radius — Challenge 2 only

Every other Phase 2 command was checked with `dbt ls` to see which nodes it pulls in:

| Guide step | Extra nodes selected | Outcome |
|---|---|---|
| C1 `--select int_holdings_enriched` | none | ✅ no test references this model |
| **C2 `--select int_fund_attributes int_positions_dated`** | **the relationships test** | ❌ **its other input is a stub** |
| C3 `--select agg_fund_exposure` | that mart's own 3 tests | ✅ single-input tests, model is built by the same command |
| C4 `--select fct_portfolio_returns` | its 4 not_null tests + the relationships test | ✅ by now **both** inputs are real |

`int_fund_attributes` is the only *intermediate* model that any mart test names, which is exactly why
Challenge 2 is the only step that breaks.

### 4.5 Why existing testing did not catch it

The offline suite (`tests/challenges/offline/test_ch02.py`) asserts guide *content* — that stubs are
stubs, that `marts/schema.yml` ships without the capstone, that the guide uses raw `dbt`. It never
executes the guide's commands. The live gate runs `mise run challenge:verify 02`, which builds the
**whole** project, so `fct_portfolio_returns` is real by the time any test runs and the failure is
structurally invisible to it.

**The gap: nothing tested the guide the way a trainee reads it — one step at a time, with everything
after that step still a stub.**

---

## 5. How to reproduce

From a clean start, complete Phase 1 and Phase 2 Challenge 1 normally, then author the two Challenge
2 models and run the guide's commands:

```bash
mise run challenge:reset 02
cd challenges/02-dbt-pipeline/dbt
# ... author staging + int_holdings_enriched per the guide ...
# ... author int_fund_attributes + int_positions_dated per the guide ...
dbt build --select int_fund_attributes int_positions_dated
```

| Guide version | Result |
|---|---|
| **Before fix** | `Done. PASS=2 WARN=0 ERROR=1 SKIP=0 TOTAL=3` |
| **After fix** | `Done. PASS=2 WARN=0 ERROR=0 SKIP=0 TOTAL=2` |

---

## 6. The fix

Add `--indirect-selection=cautious` to both of Challenge 2's commands, and explain it — the flag is
not incidental plumbing, it is a genuine dbt concept the trainee benefits from meeting here:

```bash
dbt build --select int_fund_attributes int_positions_dated --indirect-selection=cautious
dbt show --select int_fund_attributes --limit 10 --indirect-selection=cautious
```

The guide now carries a **"Why `--indirect-selection=cautious` here"** paragraph defining indirect
selection, contrasting `eager` with `cautious`, naming the specific test and the specific stub
involved, and telling the trainee to drop the flag after Challenge 4 — at which point both inputs are
real and the test passes on its own.

### 6.1 Alternatives considered and rejected

| Option | Why not |
|---|---|
| Move the `relationships` test out of the shipped `schema.yml` so the trainee adds it in C5 | Contradicts the file's stated design ("ships complete: read it and run it") and the offline test `test_marts_schema_ships_without_capstone` that encodes it. Fixes one step by degrading another. |
| Change C2's check to `dbt run` (which never runs tests) | Hides the concept instead of teaching it, and breaks the guide's consistent use of `dbt build` at every other step. |
| Reorder the challenges so `fct_portfolio_returns` comes first | Large structural change to a guide whose ordering (intermediate → marts) is pedagogically deliberate. |

---

## 7. Verification (evidence)

| Check | Result |
|---|---|
| `dbt build --select int_fund_attributes int_positions_dated` (as guide read before) | `PASS=2 ERROR=1 TOTAL=3` |
| `dbt show --select int_fund_attributes --limit 10` (as guide read before) | Same `UNRESOLVED_COLUMN` error |
| `dbt ls --select int_fund_attributes int_positions_dated` | 3 nodes — proves the test is indirectly selected |
| Both commands **with `--indirect-selection=cautious`** | `PASS=2 WARN=0 ERROR=0 TOTAL=2`; `dbt show` previews all 4 active funds |
| Phase 1 end-to-end before the failing step | `PASS=10 WARN=0 ERROR=0 TOTAL=10` |
| Phase 2 Challenge 1 | `PASS=1 WARN=0 ERROR=0 TOTAL=1` |
| Offline suite after the guide edit | 89 passed |

---

## 8. Lessons

1. **A guide that ships a complete `schema.yml` has coupled every later model into every earlier
   step.** Cross-model tests (`relationships`) are the sharp edge: they make a step depend on a model
   the trainee has not written yet, invisibly, through selection rather than through SQL.
2. **`--select <model>` does not mean "only this model".** Indirect selection is the default and it is
   `eager`. Any guide that pins exact expected output (`PASS=2`) must be checked against `dbt ls`,
   not assumed.
3. **A full-project verify gate cannot validate a step-by-step guide.** Building everything erases the
   exact condition — later models still stubbed — under which each documented step actually runs.
4. **"It fails on Windows" deserves reproduction before it is believed.** The platform detail was
   incidental; the bug was 100% reproducible on the first try on another OS. Chasing the reported
   environment first would have wasted the investigation.

---

## 9. Follow-ups

- Consider a live test that walks the guide **incrementally** — author step N, run step N's commands,
  assert success while steps N+1… remain stubs. That is the only shape of test that would have caught
  this, and it would cover the whole guide, not just this step.
- Audit challenges 03 and 04 for the same pattern: any shipped `relationships` test (or other
  multi-input test) whose second input is authored in a later step.
