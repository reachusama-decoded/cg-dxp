"""Scrub secret env-var values from anything the runner is about to persist.

When the agent runs `env | grep CONFLUENCE` and then `curl -u user:$TOKEN`,
the token lands verbatim in the captured Bash command. From there it flows
into the cache JSON, the per-case markdown, the live-report HTML, and the
benchmark.json — all on the user's local disk in plaintext, with no
chance of redaction at the consumer end.

The fix: at the runner's output boundary, take the *values* of known
sensitive env vars and replace them with `<redacted:VAR_NAME>` everywhere
they appear in tool-call args, tool-call results, and the output text.

We redact by value (not pattern) so we don't get false positives — only
strings that match an actual secret in the environment get scrubbed,
which keeps test output readable. False negatives (a secret we didn't
know about) are still possible; the right defense for those is to keep
DEFAULT_SENSITIVE_VARS in sync with the `.env.example` and to fail loud
if a tool-call result re-fetches a credential from somewhere new.

Used by claude_agent._state_to_result. Applies once, at the boundary —
not per-tool-call — so detect_sub_skill etc. can still see real values
during the live drive loop.
"""
from __future__ import annotations
import os
from typing import Any, Callable

# Env vars whose values should never appear in test artifacts. Add to this
# set when wiring a new credential into the test harness; the cost of a
# false positive (overzealous redaction) is much lower than a leak.
DEFAULT_SENSITIVE_VARS: tuple[str, ...] = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CONFLUENCE_API_TOKEN",
    "JIRA_API_TOKEN",
    "DATABRICKS_TOKEN",
    "TEST_DATABRICKS_TOKEN",
)


def collect_secrets(
    var_names: tuple[str, ...] = DEFAULT_SENSITIVE_VARS,
    extra_env_var: str = "BEHAVIOR_TESTS_REDACT_VARS",
) -> dict[str, str]:
    """Look up the live values of each sensitive var.

    `extra_env_var` lets a user add to the list without changing code:
    `BEHAVIOR_TESTS_REDACT_VARS=MY_SECRET,OTHER_SECRET`.

    Returns {var_name: value} only for vars that are actually set and
    non-empty — empty/unset vars can't be redacted (the empty-string
    replacement would scrub everything).
    """
    names = list(var_names)
    if extra := os.getenv(extra_env_var):
        names.extend(n.strip() for n in extra.split(",") if n.strip())
    out: dict[str, str] = {}
    for name in names:
        val = os.environ.get(name) or ""
        if val and len(val) >= 8:  # too-short values risk false positives
            out[name] = val
    return out


def build_redactor(secrets: dict[str, str]) -> Callable[[Any], Any]:
    """Return a function that walks a JSON-shaped value and replaces every
    occurrence of any secret value with `<redacted:VAR_NAME>`.

    The returned function is recursive over dict/list/tuple/str. Other
    scalar types (int, float, bool, None) pass through. Iteration order
    is preserved so cache files stay diffable.

    Empty `secrets` produces an identity function — fast path for tests
    that have no creds in env.
    """
    if not secrets:
        return lambda x: x
    # Sort by descending length so the longest secret wins when one is
    # a prefix of another (rare but possible with model-scoped tokens).
    items = sorted(secrets.items(), key=lambda kv: -len(kv[1]))

    def redact_str(s: str) -> str:
        out = s
        for name, value in items:
            if value in out:
                out = out.replace(value, f"<redacted:{name}>")
        return out

    def walk(x: Any) -> Any:
        if isinstance(x, str):
            return redact_str(x)
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items()}
        if isinstance(x, list):
            return [walk(v) for v in x]
        if isinstance(x, tuple):
            return tuple(walk(v) for v in x)
        return x

    return walk
