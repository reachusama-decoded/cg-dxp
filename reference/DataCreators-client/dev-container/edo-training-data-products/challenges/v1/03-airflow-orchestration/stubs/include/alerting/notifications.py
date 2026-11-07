"""Chat/escalation transport for the portfolio-analytics DAG.

`send_alert` posts a message to the team's Microsoft Teams chat webhook via an
Airflow HTTP connection. Teams is the chat / escalation surface, NOT an
automated alert sink — automatic alerts route to Datadog (see callbacks.py),
and support pages the on-call via xMatters. This is the single transport
boundary the P2 notifications go through, kept behind the `alert_webhook`
connection so the webhook URL is the only thing that changes.

Connection requirement: an HTTP connection named `alert_webhook`
(conn-type http) configured in the Airflow UI (Admin > Connections), holding
the Microsoft Teams incoming-webhook URL. When that connection is missing or
unreachable (local parse, preflight load, no Teams), `send_alert` logs and
returns — it must not fail the DAG task solely because chat is unconfigured.
"""
from __future__ import annotations

import logging

from airflow.providers.http.hooks.http import HttpHook

log = logging.getLogger(__name__)


def send_alert(text: str, channel: str | None = None,
               conn_id: str = "alert_webhook") -> None:
    """Post a P2 message to the Microsoft Teams chat webhook.

    Args:
        text: The formatted message body.
        channel: Optional channel handle (e.g. "portfolio-analytics").
            When None, the webhook's default channel is used.
        conn_id: Airflow HTTP connection holding the Teams webhook URL.
    """
    payload: dict[str, str] = {"text": text}
    if channel is not None:
        payload["channel"] = channel
    try:
        hook = HttpHook(method="POST", http_conn_id=conn_id)
        hook.run(endpoint="", json=payload)
    except Exception as exc:
        # Mirror Datadog/ticket offline stubs in callbacks.py: missing chat
        # transport must not turn a successful dbt run into a task failure.
        log.warning(
            "send_alert skipped (conn_id=%s unavailable or post failed): %s | text=%s",
            conn_id,
            exc,
            text[:200],
        )
