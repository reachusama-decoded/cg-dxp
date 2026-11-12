"""Tiered alert callbacks for the price sheet DAG.

Three severities mapped to the CG escalation model — no Slack, no PagerDuty:

  - P1 (auto page) -> Datadog. `on_failure_callback` emits a Datadog event
                   carrying the MDS routing tags. Datadog is the sole
                   AUTOMATIC alert sink; from that payload support MANUALLY
                   pages the on-call via xMatters (the group in
                   `l1_xmatters_group`). Reserved for a task that fails after
                   exhausting its retries: the pipeline is down and the
                   07:30 UK SLA is at risk.
  - P2 (notify) -> Microsoft Teams via `send_alert` (the vendor-neutral webhook
                   transport in include/alerting/notifications.py). Teams is the
                   chat / escalation surface, NOT an automated alert sink: a
                   retry fired, or an SLA was missed but the DAG still completed.
  - P3 (ticket) -> a tracking ticket via `open_ticket`. No human is paged or
                   pinged; the work is logged for the next working day.

Both external transports degrade to a structured log line when their
credential env var is unset, so the callbacks import and run offline (in the
DAG-load check and in `airflow tasks test`) with no secrets configured and no
network call at parse time.

PagerDuty is an explicit CG anti-goal — the paved path forbids it, so it is not
wired here; email-on-failure is forbidden too (DBX-WORKFLOW-002, alert fatigue).
Set `DD_API_KEY` / `TICKET_WEBHOOK_URL` to wire the real transports.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import Any

from notifications import send_alert

log = logging.getLogger(__name__)

# Datadog Events API. Datadog is the sole automatic alert sink; support pages
# the on-call via xMatters from the Datadog payload (PagerDuty is not used).
DATADOG_EVENTS_URL = "https://api.datadoghq.com/api/v1/events"

# MDS routing tags make an alert actionable: owning domain, the xMatters group
# support pages, lifecycle phase, classification, and criticality. Realistic
# placeholders; real values come from the MDS.
MDS_ROUTING_TAGS = {
    "l1_domain": "pricing-data",
    "l1_xmatters_group": "price-sheet-oncall",
    "lifecycle_phase": "operate",
    "data_classification": "internal",
    "criticality": "p2",
}


def _emit_datadog(summary: str, severity: str, detail: dict[str, Any]) -> None:
    """P1: emit a Datadog event carrying the MDS routing tags.

    Datadog is the automatic sink; support pages the on-call via xMatters from
    this payload (the `l1_xmatters_group` tag names the group). Falls back to a
    WARNING log when DD_API_KEY is unset, so the callback is safe to import and
    exercise offline with no network call.
    """
    tags = [f"{key}:{value}" for key, value in MDS_ROUTING_TAGS.items()]
    api_key = os.environ.get("DD_API_KEY")
    if not api_key:
        log.warning("[datadog stub] severity=%s summary=%s tags=%s detail=%s",
                    severity, summary, tags, detail)
        return
    payload = {
        "title": summary,
        "text": json.dumps(detail),
        "alert_type": "error" if severity == "error" else "warning",
        "source_type_name": "airflow",
        "tags": tags,
    }
    req = urllib.request.Request(
        DATADOG_EVENTS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "DD-API-KEY": api_key},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)  # noqa: S310 (trusted endpoint)
        log.info("[datadog] event emitted: %s", summary)
    except Exception as exc:  # noqa: BLE001 — never let alerting fail the task
        log.error("[datadog] emit failed: %s (summary=%s)", exc, summary)


def open_ticket(summary: str, detail: dict[str, Any]) -> None:
    """P3: open a tracking ticket via a generic ticket webhook.

    Falls back to an INFO log when TICKET_WEBHOOK_URL is unset.
    """
    url = os.environ.get("TICKET_WEBHOOK_URL")
    if not url:
        log.info("[ticket stub] summary=%s detail=%s", summary, detail)
        return
    req = urllib.request.Request(
        url,
        data=json.dumps({"summary": summary, "detail": detail}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)  # noqa: S310
        log.info("[ticket] opened: %s", summary)
    except Exception as exc:  # noqa: BLE001
        log.error("[ticket] open failed: %s (summary=%s)", exc, summary)


def on_failure_callback(context: dict[str, Any]) -> None:
    """P1 + P2: a task failed after all retries — Datadog event AND Teams notify.

    Wired into `default_args`, so it fires for any task in the DAG. The price sheet is
    at risk of missing the SLA, so this is the event that emits to Datadog (the
    auto sink); support then pages the on-call via xMatters from the payload.
    """
    ti = context["task_instance"]
    dag_run = context.get("dag_run")
    detail = {
        "dag_id": ti.dag_id,
        "task_id": ti.task_id,
        "run_id": dag_run.run_id if dag_run else None,
        "log_url": ti.log_url,
        "exception": str(context.get("exception")),
    }
    summary = f"DAG failure: {ti.dag_id}.{ti.task_id}"
    _emit_datadog(summary=summary, severity="error", detail=detail)
    send_alert(
        text=(
            f"*DAG failure (Datadog alerted, xMatters paged)*\n"
            f"*DAG:* {ti.dag_id}\n"
            f"*Task:* {ti.task_id}\n"
            f"*Log:* {ti.log_url}\n"
            f"*Runbook:* https://wiki.internal/runbooks/{ti.dag_id}"
        ),
    )


def on_retry_callback(context: dict[str, Any]) -> None:
    """P3: a task is about to retry — log a ticket, no page, no chat noise.

    Retries are expected (transient warehouse blips); we record them so a
    flaky task shows up in the ticket history, but nobody is paged or pinged.
    """
    ti = context["task_instance"]
    try_number = getattr(ti, "try_number", "?")
    open_ticket(
        summary=f"Retry: {ti.dag_id}.{ti.task_id} (attempt {try_number})",
        detail={"task_id": ti.task_id, "log_url": ti.log_url},
    )


def on_sla_miss_callback(dag, task_list, blocking_task_list, slas,
                         blocking_tis) -> None:
    """P2: an SLA was missed but the DAG still ran — notify, don't page.

    Wired as the DAG's `sla_miss_callback`. A miss means the pipeline was slow,
    not down: it emits a Datadog warning event and posts to Teams for visibility
    and escalation, but does not trigger an xMatters page.
    """
    missed = ", ".join(t.task_id for t in task_list) or "(none)"
    _emit_datadog(
        summary=f"SLA miss on {dag.dag_id}",
        severity="warning",
        detail={"tasks_past_sla": missed},
    )
    send_alert(
        text=(
            f"*SLA miss on {dag.dag_id}*\n"
            f"*Tasks past SLA:* {missed}\n"
            f"The DAG is still running or completed late — check the run and "
            f"warn downstream consumers if the 07:30 UK price sheet is at risk.\n"
            f"*Runbook:* https://wiki.internal/runbooks/{dag.dag_id}"
        ),
    )


def on_success_callback(context: dict[str, Any]) -> None:
    """P2 (informational): the publish task completed — one chat confirmation.

    Wired on the final task only, so it fires once per successful DAG run, not
    once per task.
    """
    ti = context["task_instance"]
    send_alert(text=f"*{ti.dag_id}* completed successfully — price sheet published.")
