# RCA — Challenge 02's guide describes data the fixtures do not contain, and its shipped YAML teaches deprecated dbt syntax

| Field | Value |
|---|---|
| **Date** | 2026-08-04 |
| **Status** | Root causes proven; fixes implemented and verified |
| **Severity** | Medium — nothing fails, but a trainee cannot reconcile the guide against what they observe, and is taught syntax dbt has deprecated |
| **Components** | `challenges/02-dbt-pipeline/README.md` · `dbt/models/sources.yml` · `dbt/models/marts/schema.yml` (+ their `stubs/` and `solution/` copies) |
| **Discovered while** | A full beginner-trainee walkthrough of Challenge 02, run after the Phase 2 Challenge 2 blocker was fixed |
| **Related** | `docs/rca/2026-08-04-challenge-02-eager-indirect-selection.md` (the blocker); `docs/rca/2026-08-04-challenge-reset-leaves-authored-files.md` |

---

## 1. Summary

With the Phase 2 Challenge 2 blocker fixed, Challenge 02 runs green end to end
(`dbt seed` 8/8, `dbt run` 11/11, `dbt test` 17/17). **Zero commands fail.** But a full walkthrough
surfaced six defects that a `PASS`-only gate cannot see, in two families:

1. **The guide asserts things about the data that the bundled fixtures contradict.** Most seriously,
   it explains the currency-conversion `coalesce` using a claim that is simply false about the shipped
   CSVs.
2. **The scaffolding that ships complete — `sources.yml` and `marts/schema.yml` — uses YAML shapes dbt
   1.11 has deprecated**, so every command a trainee runs prints a block of deprecation warnings the
   guide never mentions, and the reference YAML they are told to read teaches the old shape.

Both families share a root cause: **the guide's prose and the project's YAML were written against an
earlier state (of the fixtures, and of dbt) and nothing re-checks them, because the only automated
gate asserts exit codes, not claims.**

---

## 2. Impact / who was affected

- **Every trainee.** These are not edge cases; the warnings print on every command and the false
  claims sit in the main explanatory text.
- **The specific harm is loss of trust in the guide.** A beginner told "for a USD fund the base value
  differs from the local value" who then sees every row identical has no way to know whether they
  wrote a bug or the guide is wrong. Debugging correct work is the most expensive failure mode in
  training.
- **Teaching deprecated syntax has a lifetime beyond the challenge.** Trainees copy the reference YAML
  into real projects. `MissingArgumentsPropertyInGenericTestDeprecation` and
  `PropertyMovedToConfigDeprecation` are migration warnings — the old shapes are slated to stop
  working.

---

## 3. The six defects

| # | Where | Guide said | Reality |
|---|---|---|---|
| 1 | Ch1 Concept | "a GBP holding **has no FX row**, so the `coalesce` gives it a rate of 1.0" | `fx_rates_raw.csv` ships `GBP,GBP,…,1.00000000` for both dates. The coalesce **never fires**; GBP converts through a real matched row. |
| 2 | Ch1 How to check | "for a USD fund it is scaled by the FX rate, so the base value differs" | All 8 rows of `holdings_raw.csv` are `ccy_cd=GBP`. No USD holding exists, so this is unobservable. |
| 3 | Ch3 How to check | `exposure_base_ccy` "in the millions" | Actual range 907,120,000 – 1,505,120,000 — high hundreds of millions to low billions. |
| 4 | Ch4 How to check | NAV-per-unit "low tens (for example 10–15)" | `PEF-EM-GROWTH` is 9.07–9.11, below the stated range. |
| 5 | S7 / C7 | `Done. PASS=5 WARN=0 ERROR=0 SKIP=0 TOTAL=5` | dbt 1.11.8 always prints a `NO-OP=0` field the guide omits, in all four quoted summaries. |
| 6 | `sources.yml`, `marts/schema.yml` | (shipped as reference to read) | 8 deprecation warnings on **every** dbt command. |

### 3.1 Defect 1 in detail — the false `coalesce` explanation

This is the most damaging because it teaches an incorrect mental model of the join.

`fx_rates_raw.csv` ships six rows: `GBP→GBP` at `1.0`, `USD→GBP` at `0.78`, `EUR→GBP` at `0.85`, for
each of two dates. `stg_fx_rates` keeps all rows where `to_ccy = 'GBP'`, so the GBP→GBP row survives
into the model. Every bundled holding is GBP, so **every** holding finds a matching FX row and gets
its rate from the join.

The guide's claim inverts this: it tells the trainee the GBP rows are the ones that *miss* the join.
A trainee who believes it will misread the entire left-join/`coalesce` pattern — which is the single
most important idea in Challenge 1.

### 3.2 Defect 6 in detail — the deprecations

`dbt parse --no-partial-parse --show-all-deprecations` reports exactly eight:

```
PropertyMovedToConfigDeprecation: 6 occurrences
  `freshness` / `loaded_at_field` are top-level properties of sources[0..2] in models/sources.yml;
  they should be moved into the `config` of the source.
MissingArgumentsPropertyInGenericTestDeprecation: 2 occurrences
  Top-level arguments to test `relationships` on 'fct_portfolio_returns' and
  `accepted_values` on 'agg_fund_exposure' should be nested under `arguments`.
```

Both files **ship complete** — the trainee is told to read them, not write them — so the trainee has
no way to silence the noise and no reason to suspect the repo rather than themselves.

---

## 4. Root cause

### 4.1 Why the data claims drifted

The fixtures are small hand-written CSVs; the prose describes an idealised multi-currency book. There
is no check that ties one to the other, so any fixture edit (or an original mismatch) is invisible.
The `PASS`/`FAIL` gate cannot help: `mv_base_ccy` is computed correctly whether or not a USD row
exists, so the pipeline is green while the explanation is wrong.

### 4.2 Why the deprecations accumulated

The YAML was valid when written. dbt 1.11 moved source `freshness`/`loaded_at_field` under `config:`
and generic-test arguments under `arguments:`. Nothing in CI treats a new deprecation as a signal, so
a toolchain upgrade silently added warnings to every trainee's console.

### 4.3 The common root cause

**The only automated gate is `mise run challenge:verify 02`, which asserts that the pipeline builds
and tests pass.** Every defect here is invisible to that gate by construction: five are claims in
prose, and the sixth is a warning, not an error. Nothing validates the guide *as a document* against
the repo it describes.

---

## 5. How to reproduce

```bash
# Defects 1 & 2 — inspect the fixtures the guide describes
cat challenges/02-dbt-pipeline/dbt/seeds/holdings_raw.csv   # every ccy_cd is GBP
cat challenges/02-dbt-pipeline/dbt/seeds/fx_rates_raw.csv   # a GBP,GBP,...,1.0 row exists

# Defect 6 — count the deprecations on a clean parse
cd challenges/02-dbt-pipeline/dbt
dbt parse --no-partial-parse --show-all-deprecations
```

| | Before fix | After fix |
|---|---|---|
| Deprecation lines from `dbt parse` | 8 | **0** |

---

## 6. The fixes

### 6.1 Data claims (defects 1–5) — correct the prose to the fixtures

Defects 3, 4 and 5 are corrected to the observed values. Defects 1 and 2 are corrected *and* the lost
teaching is restored:

- **Defect 1** now states what actually happens: the FX feed ships a `GBP → GBP` rate of `1.0`, so a
  GBP holding converts through a real matched row, and the `coalesce` is the safety net for the other
  case — a left join that finds no rate returns `null`, and multiplying by `null` would silently wipe
  the value out. That is the real reason the `coalesce` is there, and it is a better lesson than the
  original.
- **Defect 2** replaces an unobservable claim with an observable exercise. Rather than change the
  fixtures — which would cascade into the exposure figures, the NAV values, the custodian NAV seed and
  the reconciliation test's tolerance — the guide keeps the data and adds an optional variation that
  makes a non-`1.0` rate visible with no file edits:

  ```bash
  dbt show --inline "select mv_local_ccy, mv_local_ccy * (select fx_rate from {{ ref('stg_fx_rates') }} where from_ccy = 'USD' and rate_date = '2026-05-20') as mv_if_usd from {{ ref('stg_holdings') }} where position_date = '2026-05-20'" --limit 5
  ```

  Verified: `911,070,000 → 710,634,600`, exactly 78%.

**Why not add a USD holding instead?** It is the tempting fix, but one new row changes
`stg_holdings`'s row count, every `agg_fund_exposure` figure, every `calc_nav_per_unit`, and therefore
the `seed_custodian_nav` fixture and the tolerance in `assert_nav_within_tolerance`. That is a large,
high-risk change to make a sentence true. Correcting the sentence and adding a read-only demonstration
achieves the same teaching at a fraction of the blast radius.

### 6.2 Deprecated YAML (defect 6) — adopt the current shapes

`sources.yml` moves `loaded_at_field` and `freshness` under each source's `config:`:

```yaml
  - name: custodian
    config:
      loaded_at_field: _extracted_at
      freshness:
        warn_after:  {count: 4, period: hour}
        error_after: {count: 6, period: hour}
```

`marts/schema.yml` nests generic-test arguments under `arguments:`:

```yaml
          - relationships:
              arguments:
                to: ref('int_fund_attributes')
                field: fund_id
```

Applied consistently to all copies — `dbt/`, `stubs/`, `solution/` — and to the YAML quoted in the
guide, plus the Section 8 variation, which now shows the `arguments:` shape so a trainee who follows
it writes current syntax.

---

## 7. Verification (evidence)

| Check | Result |
|---|---|
| `dbt parse --no-partial-parse --show-all-deprecations` | **0** deprecation lines (was 8) |
| `dbt source freshness` after moving to `config:` | 5 of 5 `PASS` — freshness still evaluated |
| `dbt ls --resource-type test` after nesting `arguments:` | Test names **unchanged** (`accepted_values_agg_fund_exposure_strategy_code__EQ_LC__…`, `relationships_fct_portfolio_returns_fund_id__…`) — proving the restructure is behaviour-preserving, not just parse-clean |
| New USD variation query | `911,070,000 → 710,634,600` (×0.78) |
| Offline suite | 89 passed |
| Full trainee walkthrough before these fixes | seed 8/8, run 11/11, test 17/17, `challenge:verify 02` PASS |

The test-name check matters: generic test names are derived from their arguments, so unchanged names
prove dbt is reading the arguments from the new location rather than silently ignoring them.

---

## 8. Lessons

1. **A green pipeline says nothing about a correct guide.** Every defect here coexisted with a fully
   passing `challenge:verify 02`. Exit codes validate the code; only reading validates the claims.
2. **Prose that describes data is a fixture assertion, and it rots.** "All holdings are GBP" is
   testable. Statements about the shipped data should be checked against the shipped data.
3. **Treat new deprecation warnings as a build signal.** These arrived through a toolchain upgrade, not
   a code change, so no diff review would ever have caught them.
4. **Scaffolding that ships complete is teaching material.** Files the trainee is told to *read* carry
   the same authority as the solutions, and must be held to the same standard.
5. **When prose and fixtures disagree, prefer changing the prose.** The fixtures are load-bearing for
   the reconciliation test's tolerances; the sentence is not load-bearing for anything.

---

## 9. Follow-ups

- Apply the same `config:` / `arguments:` migration to challenges 03 and 04, which ship copies of the
  same `sources.yml` and `marts/schema.yml` shapes. Deferred here only to avoid editing those trees
  while their trainee walkthroughs were mid-run.
- Consider an offline test that asserts the guide's numeric claims against the seed CSVs (for example,
  that every `ccy_cd` in `holdings_raw.csv` is GBP if the guide says so), so fixture edits and prose
  cannot drift apart again.
- Consider failing CI on any **new** dbt deprecation, which would have caught defect 6 at upgrade time.
