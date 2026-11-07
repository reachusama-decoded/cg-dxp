# Findings severity model

Severity matters because the validator's verdict (`COMPLIANT` vs
`NON_COMPLIANT`) hinges only on `blocker` findings — misclassifying a
real violation as `advisory` silently lets non-compliant DAGs through
the gate. Severity is doctrine, not vibes.

## Verdict computation

The validator's stdout `VERDICT:` line (specified in `SKILL.md`'s
"Report contract") computes from the counts as follows:

- `BLOCKER_COUNT > 0` → `VERDICT: NON_COMPLIANT`.
- `BLOCKER_COUNT == 0` → `VERDICT: COMPLIANT`, regardless of how many
  `advisory`, `ok`, or `n-a` findings the report carries.

That's the entire rule. `advisory` never blocks the verdict; `n-a`
never blocks the verdict; both must still appear in the report so the
reviewer can act on them and so the runtime-only gaps are visible.

The four counts (`blocker | advisory | ok | n-a`) are emitted on the
same `VERDICT:` line so downstream CI can grep them without parsing
Markdown. Treat the count semantics as additive: a single rule that
fails as both a missing companion artifact AND an unverifiable field
contributes one `blocker` AND one `n-a` (see n-a shape #3 below) —
this is intentional, not double-counting.

## The four severity levels

### blocker

- **Definition:** violates a directive that, if shipped to production,
  would break the RFD 0011 contract for production DAGs — alerting
  routes broken, secrets leaked, deterministic-fail semantics broken,
  idempotency gone, bundle composition mismatched, etc.
- **Effect on verdict:** any `blocker` flips the verdict to
  `NON_COMPLIANT`. No exceptions.
- **Effect on report:** each blocker generates an item in the
  "Next steps" list, ordered first.

### advisory

- **Definition:** a directive is unmet, but the failure mode is
  judgment-call or context-dependent (e.g. cron vs Asset trigger when
  the dataset legitimately has temporal semantics; PythonOperator
  usage for orchestration glue that doesn't fit TaskFlow).
- **Effect on verdict:** zero impact. The DAG can still be
  `COMPLIANT` with advisories outstanding.
- **Effect on report:** appears under "Advisory — review before
  merging." Surfaced to the human reviewer, not the gate.

### ok

- **Definition:** the rule was checked and the DAG satisfies it.
- **Effect on verdict:** zero impact.
- **Effect on report:** counted in the summary line; not enumerated
  individually unless `--verbose`.

### n-a

- **Definition:** the rule cannot be checked from this carrier / this
  artifact / without Airflow runtime. The auditor declines to assert
  pass OR fail.
- **Effect on verdict:** zero impact, BUT every `n-a` finding MUST
  carry a one-line reason so the gap is visible to the reviewer.
- **Three legitimate `n-a` shapes:**
  1. **Pattern-deferred:** rule is enforced in blueprint source for
     `astro-blueprints` with `blueprints-source: existing` (see
     `generate-dag/references/pattern-astro-blueprints.md` "What's
     enforced where"). The validator confirms the right blueprint is
     referenced and marks the YAML-field check `n-a`.
  2. **Runtime-only:** rule requires Airflow to be installed and the
     DAG to load (e.g. `dag.test()`, `assert_dag_compliant(dag)`,
     XCom size at execution). Validator points the user at the
     integrity test (`tests/dags/test_<dataset>_dag_integrity.py`).
  3. **Companion-artifact missing:** the validator can't check a
     contract-derived field because the contract file isn't there.
     Emits `n-a` for that field AND a `blocker` finding for the
     missing artifact. These are two distinct findings tracking two
     distinct RFD 0011 directives — the missing-artifact directive
     fails (blocker), and the field-level directive cannot be
     evaluated (n-a). Do not dedupe them; the verdict line counts
     both, and that's intentional (see "Verdict computation" above).

## Mode-aware severity adjustments

Severity is NOT fixed across modes. Use this table as the canonical
map; every rule entry in `checks-by-section.md` cites it implicitly.

| Rule cluster | production | prototype | lift-and-shift |
|---|---|---|---|
| Required MDS tag set (PY-AIRFLOW-007) | blocker | advisory* | blocker |
| No DAG-level alerting callback (PY-AIRFLOW-008) | blocker | advisory | blocker |
| Bounded waits / deferrable (PY-AIRFLOW-017) | blocker | advisory | blocker |
| Bounded parallelism (PY-AIRFLOW-018) | blocker | advisory | blocker |
| Asset-driven schedule (PY-AIRFLOW-019) | advisory | advisory | advisory |
| DAG ID convention (PY-AIRFLOW-012) | blocker | advisory | advisory** |
| Idempotency (PY-AIRFLOW-001/002) | blocker | blocker | blocker |
| Secrets (PY-AIRFLOW-013/020) | blocker | blocker | blocker |
| retry_on_exception emitted (PY-AIRFLOW-016) | blocker | blocker | blocker |
| Integrity test exists (PY-AIRFLOW-014/022) | blocker | advisory | advisory |

*In prototype mode, the validator still reports
`# TODO PY-AIRFLOW-007: <tag>` comment markers as known-gaps rather
than violations — they're the generator's intentional placeholder
shape (see `generate-dag` Step 3 prototype branch). Their absence
when the tag is also absent is the actual advisory.

**Lift-and-shift preserves existing DAG IDs by definition (see
`/generate-dag` Step 7 + `generate-dag/references/rfd-0011-citations.md`
§7 tie-breaker). Downgrade to advisory; the human reviewer decides
whether to rename and break downstream references.

The cluster names above reference the rule IDs from
`checks-by-section.md` exactly. Do not invent new IDs.

## When mode isn't specified

Default to `production`. The skill's SKILL.md says so. If the user
supplies a dataset that has `.catalyst-build.yml#mode: prototype`,
honor that. Otherwise the strictest mode is the safer default — a
missed violation is worse than a spurious one, and the auditor is
read-only so spurious findings cost nothing but reviewer time.

## Why we don't have "warning" or "info"

Severity has to be load-bearing on the verdict. A "warning" tier that
doesn't block but also isn't advisory creates ambiguity for downstream
CI: does this fail the gate or not? Two tiers + `ok` + `n-a` is the
minimum coherent set. Resist adding a fifth.

## Sourcing severity decisions

Every severity in `checks-by-section.md` traces back to one of:

1. **RFD 0011's own language** about whether the directive is
   mandatory ("MUST" → blocker; "SHOULD" → advisory). See
   `generate-dag/references/rfd-0011-citations.md`.
2. **The `/generate-dag` skill's behavior** — if `/generate-dag`
   REFUSES to emit without this directive resolved (Step 3
   production-mode prompt-and-stop, Step 2 missing-bundle stop),
   the validator treats absence as `blocker`.
3. **The compliance-checklist `Enforcement point` field** —
   review-only rules are advisory because the auditor can't
   deterministically verify them from the carrier alone.

If you ever need to invent a new severity, you're making a new rule.
Don't. Add the rule to RFD 0011 first, then to
`generate-dag/references/rfd-0011-citations.md`, then to
`checks-by-section.md` here.
