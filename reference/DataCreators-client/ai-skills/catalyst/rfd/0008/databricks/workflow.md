# DBX-WORKFLOW: Workflows (Jobs and Orchestration)

Databricks Workflows: timeouts, retries, notifications, declarative DAGs.

## DBX-WORKFLOW-001 — Use Databricks Workflows for orchestration

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Production data pipelines run on Databricks Workflows
(Jobs). Cross-system orchestration may use Airflow/Astronomer (per the
existing platform) calling Databricks Jobs as a task.

**Why.** Workflows are first-class on Databricks: native UC integration,
serverless task execution, declarative dependencies. Airflow on
Databricks (running on a long-lived cluster) is an antipattern.

## DBX-WORKFLOW-002 — Job timeouts set explicitly per task

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform validation

**Decision.** Every task in a Workflow declares `timeout_seconds`. The
default is unbounded — that's the wrong default.

**Why.** A hung task without a timeout consumes cluster resources
indefinitely until manually killed.

## DBX-WORKFLOW-003 — Retries with exponential backoff

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Tasks declare `max_retries` (typically 2-3) and
`min_retry_interval_millis` for backoff. Retry on transient infra
failures only — don't retry on data-quality errors.

## DBX-WORKFLOW-004 — Failure notifications go to a team channel

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform validation

**Decision.** Job failure notifications are routed to a team Slack/Teams
channel or a shared on-call rotation. Never to an individual user's
email.

**Why.** Bus factor: when the named individual is on PTO, the alert is
silently lost.

## DBX-WORKFLOW-005 — Job parameters via job-level params, not hardcoded

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use job-level parameters (`{{job.parameters.<name>}}`) for
environment-specific values. Never hardcode catalog names, dates, or
config values in the notebook/wheel.

**Why.** Hardcoded values fork the artifact across environments.
Parameters keep one artifact and many invocations.

## DBX-WORKFLOW-006 — Task dependencies expressed declaratively

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Express task dependencies in Workflow YAML / Terraform
(`depends_on`), not procedurally inside tasks (e.g., one task triggering
another via the API).

**Why.** Declarative DAGs are visible, monitorable, and rerunnable.
Procedural triggers hide the dependency graph.

### Security
