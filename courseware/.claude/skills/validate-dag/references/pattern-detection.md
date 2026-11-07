# Pattern detection (validator side)

How `/validate-dag` decides which carrier a dataset uses, and what to do when
the answer is "none" or "more than one." Same disambiguation as
`/generate-dag` Step 1, with one polarity flip: the validator never emits.
Unresolved or ambiguous carriers become `blocker` findings, not prompts.

## Why this matters

The carrier determines where each RFD 0011 directive is *enforced*, which
in turn determines what the validator has to inspect:

- **Pattern A (dag-factory)** and **Pattern B vendored** — almost every
  directive is a YAML field on the carrier. The validator reads keys and
  values.
- **Pattern B existing** — retries, callbacks, deferrability, fail-fast
  behaviour live inside `data_products/.blueprints/*.py` source. The YAML
  only names the blueprint. The validator has to confirm the *right
  blueprint is used*, then trust (or separately inspect) the blueprint
  source. Asserting these rules against the YAML alone produces false
  negatives.
- **Pattern C (python)** — every directive is a Python literal in the
  `@dag(...)` kwargs and operator constructors. The validator greps and
  parses the AST.

Get the pattern wrong and the entire compliance report is wrong. Hence:
detection is Step 1, and it's strict.

## The three patterns

| Pattern | Filename on disk | Recognizable signal |
|---|---|---|
| `dag-factory` | `<dataset>.dag-factory.yml` | Top-level keys `dag_id`, `tasks:` (dict of task name -> operator config). Loaded by `data_products/dags_loader.py`. |
| `astro-blueprints` | `<dataset>.dag.yml` or `<dataset>.dag.yaml` | Top-level keys `dag_id`, `steps:` (dict of step name -> `blueprint:` ref) OR a dag-factory-shaped body (vendored sub-mode). Loaded by `data_products/blueprints_loader.py`. |
| `python` | `<dataset>_dag.py` | A `@dag(...)` decorator on a module-level function, with a trailing call to instantiate it. |

Both YAML loaders run in the same Airflow process. The file extension is
the disambiguator, not "which loader is installed."

## Decision tree (per dataset)

**Run the multi-carrier check FIRST**, then the order below. First match
wins among the singletons. Sticky to whatever the dataset already uses.

### Multi-carrier short-circuit

Before classifying, list every carrier-shaped file in
`data_products/<product>/datasets/<dataset>/airflow/`. If MORE THAN ONE
of the following is present, emit a `blocker` finding and stop — the
file presence itself is the violation:

- `*.dag-factory.yml`
- `*.dag.yml` or `*.dag.yaml`
- `*_dag.py`

All three pairwise combinations are violations: `dag-factory.yml +
dag.yml`, `dag-factory.yml + _dag.py`, `dag.yml + _dag.py`. Both YAML
loaders run in the same Airflow process and `_dag.py` is picked up by
the DagBag scan, so any pair registers ≥ 2 DAGs (or two competing
definitions of the same DAG ID).

- rule id: `PY-AIRFLOW-012` (DAG ID uniqueness — multiple carriers
  register colliding DAGs)
- remediation: "Multiple carrier files found: `<list>`. Delete the
  non-canonical carrier(s), then re-run `/validate-dag`."

### Single-carrier classification

1. **`<dataset>.dag.yml` OR `<dataset>.dag.yaml` exists** →
   `astro-blueprints`. Sub-detect:
   - Open the file. If the top-level has a `steps:` key where each child
     has a `blueprint:` reference, this is `astro-blueprints (existing)`.
     Skip YAML-field assertions for PY-AIRFLOW-003/004/008/016/017 — they
     are enforced in the blueprint source, not here. See
     `references/checks-by-section.md` "Pattern routing."
   - Else (the body uses `tasks:` with inline operator config, dag-factory
     shape) → `astro-blueprints (vendored)`. YAML-field assertions apply
     in full because the vendored helpers expose retries / callbacks /
     timeouts as configurable fields.
   - Edge case: if the body mixes `steps:` AND `tasks:` keys, emit a
     `blocker` finding ("ambiguous body shape") and stop; the human
     must reconcile to one shape before the audit can continue.
2. **Else if `<dataset>.dag-factory.yml` exists** → `dag-factory`.
3. **Else if `<dataset>_dag.py` exists** → `python`. Then guard against
   non-DAG Python files:
   - Parse the file (string-read or `ast.parse`). If neither a
     `@dag(...)` decorator nor a `DAG(...)` constructor call appears at
     module scope, the `_dag.py` suffix is misleading — there is no
     DAG to audit. Emit a `blocker` finding:
     - rule id: `PY-AIRFLOW-014` (no DAG to integrity-test)
     - remediation: "`<file>` matches `*_dag.py` but defines no DAG.
       Rename the helper module or add a `@dag(...)` decorator. Then
       re-run `/validate-dag`."
   - This guard also catches `__init__.py`-style shared helpers that
     accidentally match the `_dag.py` glob.
4. **Else** → no DAG carrier present for this dataset. **The validator
   does NOT emit a scaffold.** Produce a `blocker` finding:
   - rule id: `PY-AIRFLOW-014` (no DAG to integrity-test)
   - location: `data_products/<product>/datasets/<dataset>/airflow/`
   - remediation: "Run `/generate-dag` to scaffold a carrier, then re-run
     `/validate-dag`."
   Stop the validation pass for this dataset — there is nothing to audit.

The single-carrier order mirrors `/generate-dag` Step 1's sticky lookup
(dag.yml before dag-factory.yml before _dag.py) so the two skills
classify the same file identically.

## Discovery (Glob + Read only — no shell)

The validator's `allowed-tools` is `Read Glob Grep` — Bash is
deliberately excluded so the read-only invariant rests on the tool
surface, not on prompt discipline. All discovery is Glob patterns;
content inspection is Read (for whole-file parsing) plus Grep (for
regex-based detectors in `checks-by-section.md`). None of these tools
can write, mutate, or shell out.

```text
# Repo-level loaders + blueprints (informational; does not change the per-dataset answer)
Glob:  data_products/.blueprints/*.py
Glob:  data_products/blueprints_loader.py
Glob:  data_products/dags_loader.py

# Per-dataset carrier — this is the authoritative signal. One Glob per
# candidate carrier shape; a non-empty result for any of these decides
# the pattern per the single-carrier classification rules above. If
# more than one returns a non-empty result, the multi-carrier
# short-circuit fires.
Glob:  data_products/<product>/datasets/<dataset>/airflow/*.dag-factory.yml
Glob:  data_products/<product>/datasets/<dataset>/airflow/*.dag.yml
Glob:  data_products/<product>/datasets/<dataset>/airflow/*.dag.yaml
Glob:  data_products/<product>/datasets/<dataset>/airflow/*_dag.py
```

Read is used after Glob to inspect a carrier's body shape (existing vs
vendored disambiguation below, and per-section checks in
`checks-by-section.md`). At no point does the validator invoke a shell;
the framing flip from `/generate-dag`'s `test -f` / `ls` discovery is
"ready to inspect?" with read-only tools, never "ready to emit?".

## Existing vs vendored — how to tell

Open the `.dag.yml`. The shape of the body is the signal.

**Existing-mode (`blueprint:` references):**

```yaml
dag_id: currency
schedule: "@daily"
steps:
  run_currency_dbt:
    blueprint: databricks_run_now
    job_name: "{{ var.value.databricks_job_prefix }}currency_job"
```

If `steps:` is present and each entry has `blueprint:`, it's existing.
The validator looks up each blueprint name in
`data_products/.blueprints/*.py` to learn what's enforced where.

**Vendored / dag-factory shape (`tasks:` with inline operator):**

```yaml
dag_id: currency
schedule: "@daily"
tasks:
  run_databricks_job:
    operator: airflow.providers.databricks.operators.databricks.DatabricksRunNowOperator
    job_name: "..."
```

If `tasks:` is present with `operator:` configs (no `blueprint:`), the
YAML carries the full operator config and every YAML-field assertion
applies.

## What changes downstream

Four bullets. The authoritative split lives in
`references/checks-by-section.md` "Pattern routing":

- **dag-factory** → all PY-AIRFLOW directives asserted as YAML fields.
- **astro-blueprints (vendored)** → same as dag-factory.
- **astro-blueprints (existing)** → PY-AIRFLOW-003/004/008/016/017
  asserted at the blueprint reference (right blueprint used?) and
  inspected in `data_products/.blueprints/<blueprint>.py` source.
  PY-AIRFLOW-018 downgrades to `advisory` (the platform-team task to
  extend `ProjectDagArgsConfig` is tracked separately).
- **python** → all directives asserted as Python literals via grep / AST.

## When detection is ambiguous

The validator is an audit, not an interactive emission. It does **not**
prompt the user mid-run. If two carriers are present, or if the `.dag.yml`
body shape doesn't match either existing or vendored cleanly (e.g. mixes
`steps:` and `tasks:`), the validator emits a `blocker` finding listing
the candidate carriers and the body-shape evidence, then stops the pass.

To resume, the user re-invokes `/validate-dag` with an explicit file path
(see `SKILL.md` "Inputs" option 2), which overrides detection and forces
the validator to treat the named file as the authoritative carrier.
