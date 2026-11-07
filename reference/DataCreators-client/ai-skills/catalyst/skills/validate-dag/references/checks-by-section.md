# Checks by section (validator rules)

The per-directive validator logic, organized by RFD 0011 section. Mirrors
`generate-dag/references/compliance-checklist.md` from the auditor side.

## How to read this file

Each rule entry has the shape:

> **PY-AIRFLOW-NNN** — <one-line directive>
>
> **Detect violation:** <exactly how the validator finds it — grep, YAML field assertion, regex, etc.>
> **Severity (production):** `blocker | advisory | ok-if-absent | n-a-per-pattern`
> **Pattern routing:** `[A | C | B-vendored | B-existing]` or `[ALL]`. Notes when the enforcement point shifts to "blueprint source" (B-existing).
> **Remediation hint:** <one short sentence + which generate-dag reference doc to consult>

Severity vocabulary:

- `blocker` — the rule is violated and the DAG cannot be declared compliant.
- `advisory` — the rule's signal is ambiguous or judgment-leaning; the
  finding goes in the report but does not gate the verdict.
- `ok-if-absent` — the field is optional; absence is not a violation.
- `n-a-per-pattern` — enforcement point lives outside the DAG file (e.g.
  inside a team-owned blueprint); the validator checks the *reference*
  instead and emits an `ok` finding when the reference is present.

Mode adjustments live in `references/findings-severity.md`; this file
documents the **production-mode** severity as the canonical baseline.

## Comment-aware grep rule (applies to every grep-based detector below)

Every regex-based detector in this file MUST strip comment-only matches
before flagging a violation. Specifically:

- For YAML carriers, ignore any match whose line begins (after leading
  whitespace) with `#`.
- For Python carriers (`_dag.py`), ignore matches inside `#`-prefixed
  lines AND inside string literals that themselves live inside a `#`
  comment (rare but possible with multi-line constructions).
- For grep-style detection (e.g. PY-AIRFLOW-001's `datetime.now(`,
  PY-AIRFLOW-016's `retry_on_exception`), the rule is: a match counts
  ONLY if it sits in code that would actually execute or be parsed by
  Airflow at DAG-load time. Pedagogical comments documenting "do not
  emit this key" are not violations.

The safe implementation is a two-pass detector: (1) strip comment-only
lines from the carrier text, then (2) apply the regex set. Inline
comments (`<code> # explanatory text`) are kept — strip only the
comment fragment past `#`.

The structural test (`test_dag_structural.py`) doesn't need this guard
because it parses the YAML/AST and walks the resulting dict — comments
disappear in parsing. The validator runs against raw text for cheap
detection, which is why the explicit guard matters here.

## Pattern routing — the existing-vs-vendored split

In `astro-blueprints (existing)` mode (the carrier shape used by
`edo-ig-data-products`), the team's `.blueprints/dag_args.py` defines a
`ProjectDagArgsConfig` that types `default_args` as `dict[str, str]` and
exposes only a small set of top-level fields: `schedule`, `description`,
`start_date`, `catchup`, `tags`, `default_args`. Fields like
`max_active_runs`, `max_active_tasks`, `render_template_as_native_obj`,
`retries`, `retry_exponential_backoff`, `max_retry_delay`,
`execution_timeout`, and `on_failure_callback` are NOT addressable from
the `.dag.yml` — they're enforced inside the blueprint's Python
`render()` method (e.g. `dag_exec_check.py` hardcodes `retries=5`,
`mode="reschedule"`; `databricks_run_now.py` hardcodes
`deferrable=True` and a failure callback that harvests Databricks run
logs locally — alerting itself is platform-side, not blueprint-emitted).

The validator MUST NOT flag absence of these YAML fields as a `blocker`
in B-existing. Instead it emits `n-a-per-pattern` and verifies that the
right blueprint name appears in `steps[*].blueprint`. The rubric matches
the "What's enforced where" table in
`generate-dag/references/pattern-astro-blueprints.md`. The validator
detects existing mode with the same `_is_existing_blueprints_mode`
heuristic as `test_dag_structural.py`: `PATTERN == "astro-blueprints"`
AND `steps` is a mapping AND at least one step has a `blueprint:` key.

Pattern A (`dag-factory`) and Pattern B-vendored expose the full YAML
field surface and are checked identically. Pattern C (pure Python) is
parsed via `ast` for the same logical assertions; the validator
de-indents the module body and walks AST nodes instead of dict keys.

## §1 — Idempotency

> **PY-AIRFLOW-001** — No wall-clock calls in DAG body; partitions reference templated dates.
>
> **Detect violation:** Grep the carrier file (`.dag.yml`,
> `.dag-factory.yml`, `_dag.py`) for these regexes, scanning module
> scope AND task body literals. *Apply the comment-aware grep rule from
> the top of this file — `#`-prefixed lines never count as violations:*
> - `r"\bdatetime\.now\("`
> - `r"\bdate\.today\("`
> - `r"\bpendulum\.now\("`
> - `r"\btime\.time\("`
>
> Any match is a violation. Jinja templates `{{ ds }}`,
> `{{ data_interval_start }}`, `{{ data_interval_end }}`, and
> `{{ logical_date }}` are the expected partition keys and never flagged.
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Replace with `{{ ds }}` or `{{ data_interval_start }}`. See `generate-dag/references/rfd-0011-citations.md` §1.

## §2 — Retries

> **PY-AIRFLOW-003** — Every task has `retries >= 1`; default is 3.
>
> **Detect violation:** A/C/B-vendored — load YAML (or AST-walk for C),
> assert `default_args.retries` is an int and `>= 3` (matches the
> structural test's `>= 3` threshold). B-existing — confirm any step
> using compute references the `databricks_run_now` blueprint, OR
> waits use `dag_exec_check` (hardcodes `retries=5`).
> **Severity (production):** `blocker` for A/C/B-vendored; `n-a-per-pattern` for B-existing (emit `ok` if blueprint reference is present, `blocker` if a compute step is using an unknown blueprint).
> **Pattern routing:** `[A | C | B-vendored | B-existing]`
> **Remediation hint:** Set `default_args.retries: 3` per `generate-dag/references/compliance-checklist.md` §2.

> **PY-AIRFLOW-004** — Exponential backoff is bounded.
>
> **Detect violation:** A/C/B-vendored — assert
> `default_args.retry_exponential_backoff is True` AND at least one of
> `default_args.max_retry_delay_seconds`,
> `default_args.max_retry_delay_minutes`, or
> `default_args.max_retry_delay` (as a `timedelta` literal in Python /
> ISO 8601 duration string in YAML) is present and positive.
> B-existing — verify the `dag_exec_check` / `databricks_run_now`
> blueprint reference (both pin
> `retry_exponential_backoff=True`, `retry_delay=60s` in `render()`).
> **Severity (production):** `blocker` for A/C/B-vendored; `n-a-per-pattern` for B-existing.
> **Pattern routing:** `[A | C | B-vendored | B-existing]`
> **Remediation hint:** See `generate-dag/references/rfd-0011-citations.md` §2.

> **PY-AIRFLOW-016** — `retry_on_exception` is NOT a real Airflow API; never emit it.
>
> **Detect violation:** Grep for `retry_on_exception` anywhere in the
> carrier file. Match = violation. Airflow's scheduler hardcodes
> "no retry on `AirflowFailException`" — there is no per-operator
> retry filter API on `BaseOperator`, so emitting one is dead code
> at best and a misleading signal to reviewers at worst. *Apply the
> comment-aware grep rule from the top of this file — pedagogical
> comments like `# do not emit retry_on_exception` do not count as
> violations.*
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Remove the key; deterministic failures should raise `AirflowFailException` from task code. See `generate-dag/references/rfd-0011-citations.md` PY-AIRFLOW-016.

## §3 — Deferrability

> **PY-AIRFLOW-017** — Deferrable operators; sensors use `mode: reschedule`; DAG-level `execution_timeout` set.
>
> **Detect violation:** A/C/B-vendored — walk `tasks:` (or AST-walk
> operator instantiations in C):
> - Any task whose `operator` string contains
>   `DatabricksRunNowOperator` MUST set `deferrable: true`. Missing
>   or `false` = blocker.
> - Any task whose `operator` string contains `Sensor` MUST set
>   `mode: reschedule` AND a positive `timeout`. Missing either =
>   blocker.
> - DAG-level `default_args.execution_timeout` MUST be present and
>   positive. Any of these accepted forms count: a YAML mapping like
>   `execution_timeout: {hours: N}` / `{minutes: N}` / `{seconds: N}`
>   (resolves to a `timedelta`), OR the explicit
>   `execution_timeout_seconds: N` / `execution_timeout_minutes: N` /
>   `execution_timeout_hours: N` scalar, OR a Python `timedelta(...)`
>   literal for Pattern C. Missing all of these = blocker.
>
> B-existing — confirm the carrier references `databricks_run_now`
> for compute steps (hardcodes `deferrable=True`) and `dag_exec_check`
> for waits (hardcodes `mode="reschedule"` and a timeout). Absence of
> either reference where a compute / wait step is needed = `blocker`.
> **Severity (production):** `blocker` for A/C/B-vendored; `n-a-per-pattern` for B-existing.
> **Pattern routing:** `[A | C | B-vendored | B-existing]`
> **Remediation hint:** See `generate-dag/references/rfd-0011-citations.md` PY-AIRFLOW-017.

## §4 — Resourcing

> **PY-AIRFLOW-005** — Every task declares a `pool` (T-shirt cluster tier).
>
> **Detect violation:** A/C/B-vendored — assert each task in `tasks:`
> sets `pool: databricks_<tier>` where `<tier> ∈ {xs, sm, md, lg}`,
> OR `default_args.pool` is set and the per-task entry doesn't
> override with an empty value. Missing pool on any task = blocker.
> B-existing — `n-a-per-pattern`; pool selection is encoded in the
> blueprint config schema (e.g. `databricks_run_now.pool_tier`); the
> validator verifies the field is set on the blueprint step.
> **Severity (production):** `blocker` for A/C/B-vendored; `n-a-per-pattern` for B-existing.
> **Pattern routing:** `[A | C | B-vendored | B-existing]`
> **Remediation hint:** See `generate-dag/references/rfd-0011-citations.md` §3 and `skills/dbt-best-practices/references/sql-warehouse-sizing.md` for the tier choice.

> **PY-AIRFLOW-018** — Bounded parallelism at the DAG level.
>
> **Detect violation:** A/C/B-vendored — assert `max_active_runs` and
> `max_active_tasks` at the DAG top level are both positive ints.
> Missing either = blocker. If `catchup: true` is set, also assert
> `max_active_runs == 1` (backfill thundering-herd guard).
> B-existing — `ProjectDagArgsConfig` does not yet expose
> `max_active_runs` / `max_active_tasks`; emit an `advisory` finding
> tagged "platform-team task" (the structural test does the same
> with a `pytest.skip`).
> **Severity (production):** `blocker` for A/C/B-vendored; `advisory` for B-existing.
> **Pattern routing:** `[A | C | B-vendored | B-existing]`
> **Remediation hint:** Add `max_active_runs: 1` and `max_active_tasks: 4` (or justified higher) per `generate-dag/references/rfd-0011-citations.md` PY-AIRFLOW-018.

## §5 — Scheduling

> **PY-AIRFLOW-002** — Static `start_date`; no `days_ago()`.
>
> **Detect violation:** Grep `r"\bdays_ago\("` anywhere in the carrier.
> Match = blocker. Then assert `start_date` is one of:
> - A YAML string parseable as ISO 8601 with a timezone suffix (e.g.
>   `2024-01-01T00:00:00+00:00` or `2024-01-01 00:00:00+00:00`).
> - A Python `datetime(...)` literal with an explicit `tzinfo` kwarg
>   (AST inspection for Pattern C).
>
> Naive datetimes (no tz) = blocker. Missing `start_date` = blocker.
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** See `generate-dag/references/rfd-0011-citations.md` §4.

> **PY-AIRFLOW-006** — `catchup` is explicit; cron carries a reason comment.
>
> **Detect violation:** Assert top-level `catchup` field is present and
> explicitly `false` (the structural test asserts `is False`).
> Absence = blocker. If `catchup: true`, grep the file (within 5 lines
> of the `catchup:` line) for an `# RFD 0011 §5 — reason:` comment;
> if absent AND `schedule` is a cron string, that's a blocker (the
> combination is the thundering-herd trap).
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Set `catchup: false`. See `generate-dag/references/rfd-0011-citations.md` §4.

> **PY-AIRFLOW-019** — Asset-driven schedule by default; cron and `None` require a reason.
>
> **Detect violation:** Inspect the `schedule` field:
> - `schedule: - dataset: "..."` (or `schedule=[Asset(...)]` in C) = `ok`.
> - `schedule: "<cron>"` — search within 5 lines for
>   `# RFD 0011 §5 — reason:`. Absent = advisory.
> - `schedule: null` / `schedule=None` — same reason-comment rule.
> - `schedule` field absent — defaults to `@daily` in Airflow; flag
>   as advisory (ambiguous intent).
> **Severity (production):** `advisory`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Prefer Asset-driven `schedule: - dataset: "<upstream>_ready"`; if cron is intentional, add the reason comment. See `generate-dag/references/rfd-0011-citations.md` PY-AIRFLOW-019.

> **PY-AIRFLOW-015** — Producer DAGs emit a data-ready event on success.
>
> **Detect violation:** Heuristic — a DAG is a "producer" if the
> Databricks job it triggers writes to Unity Catalog or S3 (the
> validator cannot prove this from the DAG alone). Apply this
> review-leaning check: if the DAG has no task with `outlets:`
> containing an `Asset(...)` AND no step references the
> `kafka_notify` blueprint (B-existing) or
> `include/shared/asset_signal.py` (B-vendored), emit `advisory`.
> Do NOT emit a blocker — the false-positive rate is too high for
> consumer-only DAGs.
> **Severity (production):** `advisory`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Add `outlets: [Asset("<dataset>_ready")]` on the last task, or chain the `kafka_notify` blueprint. See `generate-dag/references/rfd-0011-citations.md` PY-AIRFLOW-015.

> **RENDER-TEMPLATE-AS-NATIVE-OBJ** — `render_template_as_native_obj: true` at DAG level.
>
> **Detect violation:** A/C/B-vendored — assert top-level
> `render_template_as_native_obj` is `true`. The structural test
> (`test_render_template_as_native_obj_true`) enforces the same.
> RFD 0011 §4 lists this as "Always" emitted by `/generate-dag`.
> B-existing — `n-a-per-pattern`; `ProjectDagArgsConfig` does not
> expose this field. Emit `n-a` with reason "platform-team task to
> extend `dag_args.py`," matching the structural test's
> `pytest.skip`.
> **Severity (production):** `blocker` for A/C/B-vendored; `n-a-per-pattern` for B-existing.
> **Pattern routing:** `[A | C | B-vendored | B-existing]`
> **Remediation hint:** Add `render_template_as_native_obj: true` at the DAG top level. See `generate-dag/references/rfd-0011-citations.md` §4.

## §6 — Observability + alerting

> **PY-AIRFLOW-007** — Required MDS tag set is present with valid values.
>
> **Detect violation:** Read `tags:` from the carrier. Apply the same
> shape-agnostic key extraction as `test_dag_structural.py` —
> `_tag_keys` accepts `list[str]` of `"key:value"` (canonical),
> `list[dict]` (legacy dag-factory), or `dict` (legacy blueprint).
> Required keys (each missing key = one finding):
> - `l1_domain`
> - `l1_xmatters_group`
> - `lifecycle_phase` — value MUST be in `{build, operate, decom}`
> - `data_classification` — value MUST be in `{public, internal, confidential, restricted}`
> - `criticality` — value MUST be in `{critical, high, standard}`
>
> Invalid value (key present, value out of range) = blocker.
> **Severity (production):** `blocker` per missing key / invalid value (production); `advisory` (prototype); `blocker` (lift-and-shift). See `references/findings-severity.md` mode matrix.
> **Pattern routing:** `[ALL]`
> **Remediation hint:** See `generate-dag/references/mds-tags.md` for the canonical key set and discovery rules.

> **DEFAULT-ARGS-OWNER** — `default_args.owner` is a non-empty string.
>
> **Detect violation:** Assert `default_args.owner` is present and a
> non-empty string. The structural test (`test_owner_present`) enforces
> the same shape. For B-existing, `owner` is allowed under
> `ProjectDagArgsConfig.default_args` (typed `dict[str, str]`), so the
> check applies there too.
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Set `default_args.owner: <team-or-AD-group>`. See `generate-dag/SKILL.md` Step 3 (owner is one of the prompt-derived MDS values).

> **PY-AIRFLOW-008** — No DAG-level alerting callback; Datadog alerting is platform-side (Astronomer). No PagerDuty.
>
> **Detect violation:** A/C/B-vendored — a `default_args.on_failure_callback`
> whose lowercase form contains `datadog` or `pagerduty` = blocker
> (failure alerting is provided by Astronomer at the platform level, not
> wired as a DAG callback). Then grep the whole carrier (case-insensitive)
> for `pagerduty`; any match = blocker. No callback present = `ok`.
> B-existing — verify the `databricks_run_now` blueprint's failure callback
> does Databricks log harvesting only and emits no Datadog event. If the
> blueprint reference is present and emits no DAG-level Datadog/PagerDuty
> alert, emit `ok`.
> **Severity (production):** `blocker` (production); `advisory` (prototype).
> **Pattern routing:** `[A | C | B-vendored | B-existing]`
> **Remediation hint:** Remove any DAG-level Datadog/PagerDuty `on_failure_callback`; failure alerting is platform-side (Astronomer). See `generate-dag/references/rfd-0011-citations.md` §6 / PY-AIRFLOW-008.

## §7 — Task design

> **PY-AIRFLOW-009** — No module-scope I/O at parse time.
>
> **Detect violation:** Module-scope only (NOT inside `def` / `@task`
> / class bodies). For Pattern C, use `ast.parse` and walk
> `Module.body` directly. For YAML carriers, inspect any
> `python_callable` literals and any `!!python` tags. Regexes
> (applied to de-indented module-scope lines):
> - `r"\bVariable\.get\("`
> - `r"\bConnection\.get\("`
> - `r"\brequests\.(get|post|put|delete)\("`
> - `r"\bboto3\.(client|resource)\("`
> - `r"\burllib\.request\."`
> - `r"\bopen\([\"']" ` (file I/O at module scope)
>
> Match = blocker. AST-based detection is preferred when feasible;
> a robust regex over de-indented lines is the fallback.
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Move the call into a task callable or use Jinja templating. See `generate-dag/references/rfd-0011-citations.md` §6.

> **PY-AIRFLOW-010** — TaskFlow `@task` preferred over `PythonOperator` for compute.
>
> **Detect violation:** Grep `tasks:` (or AST-walk operator
> instantiations) for `operator:` values containing
> `PythonOperator` whose `python_callable` is NOT one of the
> known orchestration helpers (sensor polling, branching,
> XCom plumbing). Heuristic — too noisy to auto-blocker.
> The structural test also enforces a stricter
> "no `PythonOperator` at all" check; the validator mirrors
> that as `advisory` (the structural test will hard-fail).
> **Severity (production):** `advisory`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Refactor to `@task` or `DatabricksRunNowOperator`. See `generate-dag/references/rfd-0011-citations.md` §6.

> **PY-AIRFLOW-011** — XCom payload size ≤ 1KB.
>
> **Detect violation:** Cannot be validated statically. Emit an `n-a`
> finding with reason "runtime XCom size check — covered by
> integrity test if the platform's `assert_dag_compliant(dag)`
> implementation includes the runtime probe."
> **Severity (production):** `n-a` (with reason).
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Run `pytest tests/dags/test_<dataset>_dag_integrity.py` to invoke `assert_dag_compliant(dag)`.

## §8 — Code organization

> **PY-AIRFLOW-012** — DAG ID convention.
>
> **Detect violation:** Read `.catalyst-build.yml#dag_id_style` if
> the file exists. Resolve to one of:
> - `rfd` (or absent / not set) — assert `dag_id` matches
>   `r"^[a-z][a-z0-9_]*__[a-z0-9_]+__[a-z0-9_]+$"`. Failure = blocker
>   in production, `advisory` in `lift-and-shift` mode.
> - `legacy` — downgrade to `advisory` regardless of mode.
>
> The validator NEVER asks; absence of `.catalyst-build.yml` means
> the default `rfd` style applies (matches the generator's behavior).
> **Severity (production):** `blocker` (rfd style); `advisory` (legacy style or lift-and-shift mode).
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Rename to `<l1_domain>__<dataset>__<frequency>` or pin `dag_id_style: legacy` in `.catalyst-build.yml`. See `generate-dag/references/rfd-0011-citations.md` §7.

## §9 — Secrets

> **PY-AIRFLOW-013** — Credentials via `conn_id` only; secrets via `Variable.get` inside task callables.
>
> **Detect violation:** Grep the whole carrier for any of (apply the
> comment-aware grep rule from the top of this file):
> - `r"\bpassword\s*=\s*[\"']"` (literal password kwarg)
> - `r"\btoken\s*=\s*[\"']"`
> - `r"\bapi_key\s*=\s*[\"']"`
> - `r"\baws_access_key_id\s*=\s*[\"']"`
> - `r"\baws_secret_access_key\s*=\s*[\"']"`
> - `r"\bAKIA[0-9A-Z]{16}\b"` (raw AWS access key ID pattern)
> - `r"\bxox[baprs]-[A-Za-z0-9-]{10,}"` (Slack token pattern — even though Slack is anti-goal)
> - `Variable.get(` at MODULE scope (overlap with PY-AIRFLOW-009)
>
> Match = blocker. The validator MUST NOT print the matched value
> back in the report — emit only the file path, line number, and
> rule ID.
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Replace literals with `conn_id` references or runtime `Variable.get(...)` inside the task body. See `generate-dag/references/rfd-0011-citations.md` §8.

> **PY-AIRFLOW-020** — No secret values as operator args.
>
> **Detect violation:** Apply the PY-AIRFLOW-013 regex set
> specifically to operator argument literals (subject to the same
> comment-aware grep rule from the top of this file). For YAML
> carriers, walk `tasks[*]` and inspect every scalar value. For
> Pattern C, AST-walk `Call.keywords` on every operator instantiation.
> Match = blocker. Also flag any operator arg whose value resolves
> to `Variable.get(...)` at module scope (the deferred evaluation
> happens at parse time, not task runtime — `PY-AIRFLOW-009`
> overlap).
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Use `conn_id` instead, or fetch the secret inside the task body. See `generate-dag/references/rfd-0011-citations.md` PY-AIRFLOW-020.

## §10 — Testing

> **PY-AIRFLOW-014** — Integrity test stub present and imports `DagBag`.
>
> **Detect violation:** Confirm
> `tests/dags/test_<dataset>_dag_integrity.py` exists. If absent =
> blocker. If present, grep for `from airflow.models import DagBag`
> OR `pytest.importorskip("airflow")` followed by `airflow.models.DagBag`
> (the generator template's shape). Absence of DagBag use = blocker.
> The actual `dag.test()` runtime check is `n-a` here — see
> "Checks that cannot run statically" below.
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Re-run `/generate-dag` to emit `templates/tests/test_dag_integrity.py`. See `generate-dag/references/compliance-checklist.md` §10.

> **PY-AIRFLOW-021** — `doc_md` references `astro dev start`.
>
> **Detect violation:** Locate the `doc_md` field (YAML scalar or
> Python triple-quoted string assigned to `doc_md=...`). Grep its
> contents (case-insensitive) for `astro dev start`. Absence =
> advisory.
> **Severity (production):** `advisory`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Add a "Local dev" section to `doc_md` with the canonical `astro dev start` invocation. See `generate-dag/references/rfd-0011-citations.md` PY-AIRFLOW-021.

> **PY-AIRFLOW-022** — Integrity test imports `assert_dag_compliant`.
>
> **Detect violation:** In `tests/dags/test_<dataset>_dag_integrity.py`,
> grep for
> `from edo_airflow_lib.compliance import assert_dag_compliant`.
> Absence (or import present only inside a comment) = blocker.
> The runtime invocation (`assert_dag_compliant(dag)` inside a test
> body) is `n-a` here — see "Checks that cannot run statically".
> **Severity (production):** `blocker`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Re-run `/generate-dag` to refresh the integrity test template. See `generate-dag/references/compliance-checklist.md` §10.

## Compose-with-bundle (DBX-DAB-001)

> **DBX-DAB-001** — DAG's `job_name` literal composes the bundle prefix and resource key.
>
> **Detect violation:** Locate
> `data_products/<product>/datasets/<dataset>/bundle/databricks.yml`.
> If absent: production = `blocker`, prototype = `advisory`, with a
> hint to run `/setup-databricks-asset-bundle`.
>
> If present, parse the bundle and enumerate resource keys under
> `resources.jobs.*`. Find the DAG task's `job_name` argument (YAML
> field for A/B; AST `Call.keywords` for C). Assert the literal
> string contains EITHER:
> - `${var.databricks_job_prefix}` (Databricks bundle var syntax), OR
> - `{{ var.value.databricks_job_prefix }}` (Airflow Variable Jinja).
>
> AND contains the resource key from the bundle. Mismatch =
> `blocker` (production), `advisory` (prototype). Missing
> `job_name` entirely = blocker.
> **Severity (production):** `blocker` (production); `advisory` (prototype).
> **Pattern routing:** `[ALL]`
> **Remediation hint:** See `generate-dag/references/compose-with-bundle.md` for the prefix contract.

## DBX-DAB-003 — alerting ownership split

> **DBX-DAB-003** — Airflow owns DAG-level alerting; DAB owns system-signal notifications.
>
> **Detect violation:** Two-step. The Astronomer-recommended owner-contact
> shape — `default_args.email: [...]` paired with `email_on_failure: false`
> (failure alerting is platform-side Datadog) — is legitimate and must NOT be flagged.
>
> Step 1: grep the carrier for an alerting-enabled marker. ANY match
> here qualifies:
> - `r"\bemail_on_failure\s*[:=]\s*[Tt]rue\b"` — explicit opt-in
> - `r"\bemail_on_retry\s*[:=]\s*[Tt]rue\b"` — explicit opt-in
>
> Step 2: ALSO flag the "implicit opt-in" case — `email:` set as a YAML
> key (`r"^\s*email\s*:"`) or Python kwarg (`r"\bemail\s*=\s*\["`) WHEN
> `email_on_failure` is NOT explicitly set in the same DAG (Airflow's
> default for `email_on_failure` is `True`, so absent + present `email:`
> = paging is on).
>
> An `email:` key paired with an explicit `email_on_failure: false`
> (case-insensitive) is the contact-info-only shape — do NOT flag it.
>
> When a real violation is matched per the above, search within 5 lines
> for a `# DBX-DAB-003 reason:` comment justifying the override. Absence
> = advisory (the DAB is the canonical owner of email alerts; the DAG
> should not carry an email-paging callback — failure alerting is
> platform-side Datadog).
> **Severity (production):** `advisory`
> **Pattern routing:** `[ALL]`
> **Remediation hint:** Move email alerting into the bundle's notifications block; the DAG carries no alerting callback (alerting is platform-side Astronomer Datadog). See `generate-dag/references/compose-with-bundle.md`.

## Checks that cannot run statically

The validator marks the following as `n-a` with a clear reason —
they require an Airflow runtime to evaluate:

- `dag.test()` execution (PY-AIRFLOW-014 secondary signal). The
  integrity test renders Jinja and runs each task in-process; the
  validator cannot replicate this without Airflow installed.
- `assert_dag_compliant(dag)` runtime invocation (PY-AIRFLOW-022
  secondary signal). The shared helper is the org-wide source of
  truth for §1–§9 against the loaded DAG object; the static
  validator only confirms the *import* is wired up.
- XCom payload size at task runtime (PY-AIRFLOW-011). No static
  signal exists; the payload size is only knowable after a real
  task execution.
- Platform-side Datadog alert routing (PY-AIRFLOW-008). The DAG emits
  no Datadog callback — alerting is built into Astronomer — so there is
  no DAG-emitted event payload to inspect. Routing-tag *presence* is
  checked statically under PY-AIRFLOW-007; whether support escalates to
  Teams/xMatters is an out-of-band manual decision the validator cannot
  see.

Direct the user to run
`pytest tests/dags/test_<dataset>_dag_integrity.py` (which itself
guards with `pytest.importorskip("airflow")`) to cover these. The
validator's report MUST list these as `n-a` findings with the
runtime-test pointer, never as silent passes.
