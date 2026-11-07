# Findings severity model

Severity matters because the gate's verdict (`DEPLOY_READY` vs `BLOCKED`)
hinges only on `blocker` findings — misclassifying a real failure as
`advisory` silently lets a non-deploy-ready change through the gate and into
the deploy step. Severity is doctrine, not vibes.

## Verdict computation

The gate's stdout `VERDICT:` line (specified in `SKILL.md`'s "Report
contract") computes from the counts as follows:

- `BLOCKER_COUNT > 0` → `VERDICT: BLOCKED`.
- `BLOCKER_COUNT == 0` → `VERDICT: DEPLOY_READY`, regardless of how many
  `advisory`, `ok`, or `n-a` findings the report carries.

That is the entire rule. `advisory` never blocks the verdict; `n-a` never
blocks the verdict; both must still appear in the report so the reviewer can
act on them and so the gaps (e.g. checks skipped in inline mode) are visible.

The four counts are emitted on the same `VERDICT:` line so downstream CI (and
the planned `/deploy-dab` partner) can grep them without parsing Markdown. The
counting unit is fixed so the four counts are deterministic and reconcile with
the Summary table — see SKILL.md "Report contract → Counting" for the
authoritative rule (a finding = one row per gate per distinct rule/column/test;
`ok` is counted per gate; one `n-a` per skipped live step; VERDICT counts ==
Summary column sums).

## The four severity levels

### blocker

- **Definition:** a failure that, if deployed, would break the deploy or the
  deployed relation's contract — the model does not compile, the change drops
  or narrows a column other relations/consumers depend on, or a data test's
  SQL does not compile. `blocker` comes from **deploy-blocking necessity**,
  not from a draft rule ID (see "Sourcing" below).
- **Effect on verdict:** any `blocker` flips the verdict to `BLOCKED`. No
  exceptions.
- **Effect on report:** each blocker generates an item in "Next steps",
  ordered first.

### advisory

- **Definition:** a directive is unmet but the failure mode is judgment-call,
  maturity-dependent, or not deterministically verifiable by the gate — e.g.
  missing PK coverage (SQL-DBSQL-006), a hardcoded catalog/schema
  (SQL-DBSQL-007), an incremental-config suggestion (SQL-DBSQL-003), an
  additive-but-undocumented column, or a new `NOT NULL` whose safety the gate
  cannot confirm without scanning data. The change can still deploy.
- **Effect on verdict:** zero impact. The change can be `DEPLOY_READY` with
  advisories outstanding.
- **Effect on report:** appears under "Advisory — review before merging."
  Surfaced to the human reviewer, not the gate.

### ok

- **Definition:** the check ran and the change satisfies it (compiles, schema
  change is additive, tests compile and PKs are covered).
- **Effect on verdict:** zero impact.
- **Effect on report:** counted **per gate** — a gate contributes `ok = 1`
  only when at least one of its checks actually executed (not skipped to
  `n-a`) and none produced a blocker/advisory; a fully-skipped gate is
  `ok = 0`, never a pass. A gate may be `ok = 1` and carry `n-a`s at the same
  time (e.g. inline Gate 1: static pass → `ok = 1`, plus a skipped live compile
  → one `n-a`); `ok` and `n-a` are counted independently. Individual passing
  checks are not enumerated unless `--verbose`. (See SKILL.md "Report contract
  → Counting" for the authoritative rule.)

### n-a

- **Definition:** the check could not run from this subject — typically
  inline mode (no project on disk to `dbt compile`, no live warehouse to
  `DESCRIBE`), an unresolvable target, or an absent companion artifact. The
  gate declines to assert pass OR fail.
- **Effect on verdict:** zero impact, BUT every `n-a` finding MUST carry a
  one-line reason so the gap is visible to the reviewer.
- **Legitimate `n-a` shapes:**
  1. **Inline-mode runtime gap** — the live `dbt compile` / `DESCRIBE TABLE`
     cannot run without a project + warehouse. The gate reports the static
     findings it *can* make and marks the live step `n-a`.
  2. **No live target** — schema diff's breaking-change check needs the live
     relation; without it (inline mode, no snapshot) the check is `n-a`.

  (Note: a relation that does **not exist yet** is *not* `n-a` — it is a first
  deploy, so there is nothing to break and the breaking-change check is `ok`
  / additive. See gates.md Gate 2.)

## Mode-aware severity adjustments

Severity is NOT fixed across modes. This table is the canonical map; every
rule entry in `gates.md` cites it implicitly.

| Finding | production | prototype | lift-and-shift |
|---|---|---|---|
| Compile failure (parse/compile non-zero, unresolved ref/source/macro, Jinja error) | blocker | blocker | blocker |
| Hardcoded catalog/schema (SQL-DBSQL-007, advisory/draft) | advisory | advisory | advisory |
| Incremental missing merge/unique_key (SQL-DBSQL-003, advisory/draft) | advisory | advisory | advisory |
| **Breaking** schema change vs. existing relation | blocker | blocker | blocker |
| Contract-promised column no longer produced | blocker | blocker | blocker |
| New `NOT NULL` on existing table (not data-verifiable) | advisory | advisory | advisory |
| Additive schema change (documented in schema.yml) | ok | ok | ok |
| Additive-but-undocumented schema change | advisory | advisory | advisory |
| Test SQL does not compile | blocker | blocker | blocker |
| Declared PK missing not_null/unique (SQL-DBSQL-006, advisory/draft) | advisory | advisory | advisory |
| Model has no declared tests | advisory | advisory | advisory |
| Naming-convention findings | advisory | advisory | advisory |

The three failures that stay `blocker` in **every** mode are the gate's safety
floor: a change that does not compile, a change that breaks an existing
relation, and a data test that does not compile. These fail open regardless
of maturity, so no mode downgrades them — and none of the three is a draft
`SQL-DBSQL-*` rule; each is a deploy-blocking necessity.

The draft `SQL-DBSQL-*` findings (003 / 006 / 007) are `advisory` in **every**
mode, matching their `severity: advisory` in `rfd/0008/standards.yaml`. The
mode column varies only the framing, not the severity, for these — they do
not gate the verdict in any mode. (Should those rules ratify to a stricter
severity in a future RFD, update this matrix in the same change-set.)

## When mode isn't specified

Default to `production`. If the data product has
`.catalyst-build.yml#mode: prototype` (or `lift-and-shift`), honor that —
the same source of truth `/build-preflight` writes and `/setup-dbt-project`
reads. Otherwise the strictest mode is the safer default: a missed failure
that reaches the deploy step is worse than a spurious advisory, and the gate
is read-only so a spurious finding costs nothing but reviewer time.

## Why we don't have "warning" or "info"

Severity has to be load-bearing on the verdict. A "warning" tier that doesn't
block but also isn't advisory creates ambiguity for the deploy gate: does it
block the deploy or not? Two tiers + `ok` + `n-a` is the minimum coherent
set. Resist adding a fifth.

## Sourcing severity decisions

Every severity in `gates.md` traces back to one of:

1. **Deploy-blocking necessity** — if the change cannot deploy or would break
   a deployed relation, it is a `blocker` *regardless of any rule ID*. This is
   where all of the gate's blockers come from (compile failure, breaking
   schema change, uncompilable test).
2. **`rfd/0008/standards.yaml` severity** — for a finding bound to an
   `SQL-DBSQL-*` rule, the gate reports the severity the standard assigns.
   SQL-DBSQL-003 / -006 / -007 are `severity: advisory, status: draft`, so
   the gate reports them as `advisory` and never escalates them.

The gate does not author rules and does not escalate a standard's severity.
If a finding needs to be a `blocker`, it must be a deploy-blocking necessity
(#1) or the underlying standard must be ratified to a blocking severity in
RFD 0008 / RFD 0013 first — then this file is updated in the same change-set.
