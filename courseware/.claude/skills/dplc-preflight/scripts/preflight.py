#!/usr/bin/env python3
"""preflight.py — answer the zero-to-one questions before a user starts
building a data product:

    1. Am I set up to run Catalyst at all?
    2. Which Databricks workspace am I pointed at, and what else is available?
    3. Do I actually have access?
    4. Where would my data product go?
    5. Is usage reporting on, and set safely -- for Copilot Chat and, when
       running under Claude Code, for this harness too?

Design constraint that shapes everything here: **this script must produce a
useful answer on a machine where nothing is installed yet.** That is the whole
point of a pre-flight. So the toolchain probe uses the standard library only,
and every Databricks import is attempted lazily inside a guard. A missing
`databricks-sdk` is a finding to report, never a traceback.

Subcommands:

  check       Full readiness report + machine-readable cache. Exit code is the
              top-priority blocker (see EXIT CODES).
  workspaces  List the Databricks profiles configured in ~/.databrickscfg,
              marking which one is active. Answers "which workspaces do I have?"
              without needing the SDK.
  otel        Report usage-reporting config on its own, and optionally probe the
              collector endpoint (--probe-endpoint).
  background  A quiet once-a-session advisory pass -- telemetry, credential
              liveness, tool versions, identity coherence. Silent when clean,
              never changes an exit code, never blocks.

Question 5 is advisory and never changes the exit code: telemetry is not a
prerequisite for building a data product. Applying the settings is deliberately
*not* here -- this script is read-only by contract. /setup-workspace owns the
write.

Network calls, stated precisely because this script's contract is read-only and
mostly-local:

  * `check` and `background` each make one short localhost connect (1s timeout) to
    see whether a local OTLP collector exists, since "enabled with no endpoint"
    silently discards data. Loopback is not egress.
  * `background` also shells out to `keeper-env doctor` and `gh auth status`, and
    those DO leave the machine -- unavoidably, since credential liveness is the
    question being asked. Both are bounded by `_run` timeouts.
  * `otel --probe-endpoint` is the only call that contacts a collector, and only
    when asked.

EXIT CODES (check):
  0  ready to build
  2  local toolchain not ready        -> /setup-workspace
  3  no Databricks connection at all  -> /databricks-config
  4  connected, but no catalog access -> entitlement request, not self-serve
  5  connected, but no SQL warehouse reachable
  6  a lookup failed, so access is undetermined -> read the error and re-run
     (deliberately outranks 4 and 5: a failed call is not evidence of a
     missing entitlement, and sending users to file an access ticket they do
     not need wastes their time and their platform team's)

EXIT CODES (workspaces):
  0  at least one profile found
  3  no profiles configured -> /databricks-config

Cache: writes `.catalyst-env.yml` in the working directory so downstream skills
read the answers instead of re-asking. Mirrors how /build-preflight uses
`.catalyst-build.yml`.
"""
from __future__ import annotations

import argparse
import configparser
import json
import os
import shutil
import subprocess
import sys
import time
from itertools import islice
from pathlib import Path
from typing import Any, Dict, List, Optional

MIN_PYTHON = (3, 10)
RECOMMENDED_PYTHON = (3, 13)
DATABRICKS_CFG = Path.home() / ".databrickscfg"
CACHE_FILE = Path(".catalyst-env.yml")

# Probed by import name; these are the deps a Databricks-touching skill needs.
CORE_IMPORTS = ("yaml", "requests", "databricks.sdk")


# --- Question 1: can I run Catalyst at all? (stdlib only) --------------------
def probe_toolchain() -> Dict[str, Any]:
    """Report the local Python toolchain without importing anything optional."""
    version = sys.version_info[:2]
    missing = []
    for name in CORE_IMPORTS:
        try:
            __import__(name)
        except Exception:
            missing.append(name)

    return {
        "python_version": ".".join(map(str, version)),
        "python_ok": version >= MIN_PYTHON,
        "python_too_new": version > RECOMMENDED_PYTHON,
        "missing_imports": missing,
        "deps_ok": not missing,
        "databricks_cli": bool(shutil.which("databricks")),
    }


# --- Question 5: is usage reporting on? (JSONC parse, no network by default) --
#
# Deliberately last, and deliberately advisory: telemetry is not a prerequisite
# for building a data product, so nothing here changes the exit code. The one
# finding that must be loud is captureContent=true, and even that is a
# compliance escalation rather than a reason to stop the user working.

OTEL_EXPECTED: Dict[str, Any] = {
    "github.copilot.chat.otel.enabled": True,
    "github.copilot.chat.otel.exporterType": "otlp-http",
    "github.copilot.chat.otel.otlpEndpoint": "https://catalyst-otel.datalake.aws.capgroup.com",
    "github.copilot.chat.otel.captureContent": False,
}
OTEL_CAPTURE_KEY = "github.copilot.chat.otel.captureContent"
OTEL_ENDPOINT_KEY = "github.copilot.chat.otel.otlpEndpoint"

# Both Catalyst collectors are valid endpoints, not just the default.
#
# The Claude Code side has named these two since AICAT-337 and picks between them
# deliberately -- prd is not routable from an oz-dev Coder workspace. Checking the
# Copilot side against prd alone meant someone pointed at dev, on purpose, was told
# MISCONFIGURED directly above `Reachable: yes` against that same endpoint. A check
# that contradicts itself in adjacent lines teaches people to ignore it.
#
# So dev is accepted rather than flagged, and named in the report instead: choosing
# it is a legitimate override, but a silent one is how a laptop ends up reporting
# into dev for a month. Anything that is neither collector is still a problem.
OTEL_COLLECTORS = {
    "dev": "https://catalyst-otel.datalakefoundation.aws-dev.capgroup.com",
    "prd": "https://catalyst-otel.datalake.aws.capgroup.com",
}
OTEL_DEFAULT_COLLECTOR = "prd"

# The fifth setting, and the one whose absence is invisible.
#
# Copilot Chat 0.63.0 does not emit `user.id` of its own accord -- RBLW verified
# that against 693 production payloads, none of which carried it (PR #434). So
# without this attribute every report is anonymous: the data arrives, the
# dashboards populate, and nothing can be attributed to a person. Checking the
# other four and calling it ON would have been a false pass.
#
# Deliberately the settings key rather than OTEL_RESOURCE_ATTRIBUTES: the env var
# outranks it but never reaches a VS Code launched from the Dock, which is how
# this audience starts it.
OTEL_RESOURCE_ATTRS_KEY = "github.copilot.chat.otel.resourceAttributes"
OTEL_IDENTITY_ATTR = "user.id"

# Verdicts. Strings rather than an enum so the cache stays greppable.
OTEL_NOT_CONFIGURED = "NOT_CONFIGURED"
OTEL_OK = "ON"
OTEL_PENDING_RESTART = "ON_PENDING_RESTART"
OTEL_MISCONFIGURED = "MISCONFIGURED"
OTEL_CAPTURE_CONTENT = "CAPTURE_CONTENT_ENABLED"
OTEL_DISABLED = "EXPLICITLY_OFF"
OTEL_UNREADABLE = "SETTINGS_UNREADABLE"

# A settings.json touched this recently probably has not been followed by the
# full quit-and-reopen the exporter needs. We cannot observe a VS Code restart
# from a script, so this is a heuristic and is reported as one.
OTEL_RECENT_EDIT_SECONDS = 600

OTEL_REMEDIATION = {
    OTEL_NOT_CONFIGURED: "Usage reporting is off. Run /setup-workspace otel to turn it on "
                         "(see docs/catalyst-otel-getting-started.md). If that does not "
                         "work, raise it with /catalyst-feedback.",
    OTEL_OK: "Usage reporting is configured.",
    OTEL_PENDING_RESTART: "Settings look right but were edited moments ago. Run Developer: "
                          "Reload Window -- that is enough to start the exporter. A full "
                          "quit also works but is not required.",
    OTEL_MISCONFIGURED: "Usage reporting is configured incorrectly. Fix the keys named, "
                        "then run Developer: Reload Window.",
    OTEL_CAPTURE_CONTENT: "captureContent is true, which sends conversation text. That requires "
                          "a Governance, Risk and Compliance review -- do not leave it on. Set "
                          "it back to false and raise it with the EDO team if it was deliberate.",
    OTEL_DISABLED: "Usage reporting is explicitly disabled (enabled=false). Nothing is sent.",
    OTEL_UNREADABLE: "Found a settings file but could not parse it. Fix the JSON (usually a "
                     "comma) and re-run.",
}


def vscode_settings_candidates() -> List[Path]:
    """Every plausible User settings.json, most-likely first.

    Deliberately User scope only. Workspace and folder settings do not enable the
    exporter, and writing there would look like it worked while silently doing
    nothing outside that folder.
    """
    home = Path.home()
    if sys.platform == "darwin":
        roots = [home / "Library" / "Application Support"]
    elif os.name == "nt":
        appdata = os.environ.get("APPDATA")
        roots = [Path(appdata)] if appdata else [home / "AppData" / "Roaming"]
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        roots = [Path(xdg)] if xdg else [home / ".config"]

    products = ("Code", "Code - Insiders", "VSCodium")
    return [root / product / "User" / "settings.json"
            for root in roots for product in products]


def _strip_jsonc(text: str) -> str:
    """Drop // and /* */ comments and trailing commas.

    settings.json is JSONC, so `json.loads` rejects the file VS Code itself
    writes. Character-walked rather than regexed because a `//` inside a string
    value -- every https:// URL in the file -- must survive.
    """
    out = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1

    stripped = "".join(out)
    # Trailing commas. This pass has to track strings for the same reason the
    # comment pass does: a comma inside a string value can be followed by `}`,
    # as in {"x": "a,}"} -- and removing it silently rewrites the parsed data,
    # which then gets diagnosed as a different configuration than the one on disk.
    result = []
    in_string = False
    escaped = False
    for idx, ch in enumerate(stripped):
        if escaped:
            escaped = False
            result.append(ch)
            continue
        if ch == "\\" and in_string:
            escaped = True
            result.append(ch)
            continue
        if ch == '"':
            in_string = not in_string
            result.append(ch)
            continue
        if ch == "," and not in_string:
            rest = stripped[idx + 1:].lstrip()
            if rest[:1] in ("}", "]"):
                continue
        result.append(ch)
    return "".join(result)


def read_user_settings(path: Path) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Parse a JSONC settings file. Returns (settings, error) -- never raises."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"could not read {path}: {exc}"
    try:
        parsed = json.loads(_strip_jsonc(raw) or "{}")
    except ValueError as exc:
        return None, f"{path} is not valid JSON ({exc})"
    if not isinstance(parsed, dict):
        return None, f"{path} does not contain a JSON object"
    return parsed, None


def collector_name(url: Any) -> Optional[str]:
    """`dev`, `prd`, or None for anything that is not a Catalyst collector.

    Trailing slashes only, deliberately: this decides whether a value is accepted,
    so it stays a lookup against the two known URLs rather than anything that could
    be talked into matching a lookalike host.

    That rules out `.strip()`, which an earlier revision had. Whitespace is not
    cosmetic here: the exporter uses the settings value verbatim, so a padded URL is
    a value nothing can be reached at. Accepting it made preflight print
    `collector: prd` and a green `ON` directly above `Reachable: no`, with nothing
    naming the padding as the cause -- a confidently wrong verdict, which is the one
    thing this check must never produce. A padded value is now correctly "not one of
    the two known URLs".
    """
    if not isinstance(url, str):
        return None
    trimmed = url.rstrip("/")
    for name, known in OTEL_COLLECTORS.items():
        if trimmed == known.rstrip("/"):
            return name
    return None


def probe_otel(now: Optional[float] = None) -> Dict[str, Any]:
    """Report whether Copilot Chat usage reporting is on, and correctly."""
    import time

    now = time.time() if now is None else now
    candidates = vscode_settings_candidates()
    found = [p for p in candidates if p.exists()]
    if not found:
        return {
            "verdict": OTEL_NOT_CONFIGURED,
            "settings_path": None,
            "searched": [str(p) for p in candidates],
            "values": {},
            "problems": ["no VS Code User settings.json found"],
            "notes": [],
            "collector": None,
            "edited_seconds_ago": None,
        }

    path = found[0]
    # First candidate wins, which is stable Code when both it and Insiders/VSCodium
    # have settings. That can report on a product the user is not running, so say
    # so rather than presenting one file as though it were the only one.
    extra_products = [str(p) for p in found[1:]]
    settings, error = read_user_settings(path)
    if error:
        return {
            "verdict": OTEL_UNREADABLE,
            "settings_path": str(path),
            "other_products": extra_products,
            "searched": [str(p) for p in candidates],
            "values": {},
            "problems": [error],
            "notes": [],
            "collector": None,
            "edited_seconds_ago": None,
        }

    values = {k: settings.get(k) for k in OTEL_EXPECTED if k in settings}
    try:
        edited_ago = max(0.0, now - path.stat().st_mtime)
    except OSError:
        edited_ago = None

    result = {
        "settings_path": str(path),
        "other_products": extra_products,
        "searched": [str(p) for p in candidates],
        "values": values,
        "problems": [],
        "notes": [],
        # Derived HERE, before the early returns below, not after them. Derived
        # afterwards it was null whenever captureContent was true or enabled was
        # false -- so a machine deliberately pointed at dev cached as though its
        # collector were unknown, and `.catalyst-env.yml` is a contract downstream
        # skills read. The two states where the field mattered most, because both
        # need someone to go and look, were the two where it was absent.
        "collector": collector_name(settings.get(OTEL_ENDPOINT_KEY)),
        "edited_seconds_ago": edited_ago,
    }

    # Named so the report can say which one, because picking dev is legitimate but
    # forgetting you picked it is not.
    #
    # Appended here rather than after the verdict logic, because three of the
    # verdicts return early. With the note last, someone on the dev collector with
    # `captureContent: true` got the capture finding and was never told they were
    # also on dev -- and those two are plausibly correlated, since a dev endpoint and
    # content capture are both things you set while experimenting. Same for
    # `enabled: false`. The note describes the configuration, not the verdict, so it
    # belongs with the fields rather than with the conclusions.
    if result["collector"] and result["collector"] != OTEL_DEFAULT_COLLECTOR:
        result["notes"].append(
            f"reporting to the {result['collector']} collector, not "
            f"{OTEL_DEFAULT_COLLECTOR} -- valid, and deliberate if you set it; "
            f"run /setup-workspace otel to switch back")

    # captureContent outranks everything: it is the one setting with a
    # compliance consequence, and it is wrong even if nothing else is set.
    if settings.get(OTEL_CAPTURE_KEY) is True:
        result["verdict"] = OTEL_CAPTURE_CONTENT
        result["problems"].append(
            f"{OTEL_CAPTURE_KEY} is true -- conversation text would be sent"
        )
        return result

    if not values:
        result["verdict"] = OTEL_NOT_CONFIGURED
        result["problems"].append("none of the four otel keys are set")
        return result

    if settings.get("github.copilot.chat.otel.enabled") is False:
        result["verdict"] = OTEL_DISABLED
        return result

    for key, expected in OTEL_EXPECTED.items():
        actual = settings.get(key)
        # The endpoint is an OTLP URL from a user-editable file, so a wrong value is
        # exactly where a mistyped credential ends up -- and this problem string is
        # printed into a chat transcript by both `otel` and `check`.
        shown = (redact_url(str(actual)) if key.endswith("otlpEndpoint") and actual
                 else repr(actual))
        if key not in settings:
            result["problems"].append(f"{key} is not set (expected {expected!r})")
        elif key == OTEL_ENDPOINT_KEY:
            if collector_name(actual) is None:
                result["problems"].append(
                    f"{key} is {shown}, which is not a Catalyst collector (expected "
                    f"{expected!r}, or the dev collector)")
        elif actual != expected:
            result["problems"].append(f"{key} is {shown}, expected {expected!r}")

    # Anonymous reporting is a silent failure: the data arrives and cannot be
    # attributed. Treated as a problem, not a nit.
    attrs = settings.get(OTEL_RESOURCE_ATTRS_KEY)
    identity = attrs.get(OTEL_IDENTITY_ATTR) if isinstance(attrs, dict) else None
    result["identity"] = identity
    if not identity:
        result["problems"].append(
            f"{OTEL_RESOURCE_ATTRS_KEY} has no {OTEL_IDENTITY_ATTR}, so every report "
            "is anonymous -- Copilot Chat does not emit it on its own")

    if result["problems"]:
        result["verdict"] = OTEL_MISCONFIGURED
    elif edited_ago is not None and edited_ago < OTEL_RECENT_EDIT_SECONDS:
        result["verdict"] = OTEL_PENDING_RESTART
    else:
        result["verdict"] = OTEL_OK
    return result


# --- Question 5b: the same question for the Claude Code harness ---------------
#
# Claude Code telemetry is a different mechanism from Copilot Chat's: env vars
# rather than settings keys, metrics *and* logs rather than chat metrics, and
# four content switches rather than one. On a DevNext/Coder workspace it is
# usually set by /etc/claude-code/managed-settings.json, which outranks anything
# the user can set -- so this reports which layer is responsible, otherwise a
# user is told to change something they cannot change.

CC_TELEMETRY_KEY = "CLAUDE_CODE_ENABLE_TELEMETRY"

# What a correctly-configured DevNext workspace looks like. The canonical copy is
# docs/telemetry/managed-settings-otel.json; this mirrors the keys the check can
# verify. The endpoint carries the `/s/devnext` suffix so Coder-session telemetry
# lands in its own S3 partition rather than mixing with Copilot data from real
# dev work (cg-open-itg/catalyst-otel PR #12).
CC_OTEL_EXPECTED = {
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
}
# Wanted OFF. It is easy to assume this is the switch that gives per-skill
# attribution -- it is not. `skill.name`, `agent.name`, `plugin.name` and
# `marketplace.name` are *unconditional* attributes on claude_code.api_request
# and on the cost.usage / token.usage metrics, so Catalyst attribution costs
# nothing. What this switch adds is tool_parameters (bash_command, full_command,
# git_commit_id, git_branch) and tool_input (full serialized arguments, ~4KB a
# call) on tool_result events -- over-collection for our use case, and
# code-adjacent even though it is a step below prompt text.
CC_OVER_COLLECTION_SWITCH = "OTEL_LOG_TOOL_DETAILS"

# The attributes Catalyst actually counts. Present without any content switch.
CC_ATTRIBUTION_ATTRS = ("skill.name", "agent.name", "plugin.name", "marketplace.name")
# The producer-side path segment that keeps the two populations apart.
CC_SOURCE_SEGMENT = "/s/devnext"
# The OTLP/HTTP path for the metrics signal. Required on a PER-SIGNAL endpoint,
# which is used verbatim; the generic endpoint gets it appended by the exporter.
CC_METRICS_PATH = "/v1/metrics"
# Enough of the hostname to recognise our own collector in an endpoint, dev or prd.
CATALYST_COLLECTOR_HINT = "catalyst-otel"

# All four ship disabled. Each one sends conversation or code content, so each
# needs a GRC review before it goes on. OTEL_LOG_TOOL_DETAILS is deliberately
# NOT here: it carries tool/skill *names*, not content.
CC_CONTENT_SWITCHES = (
    "OTEL_LOG_USER_PROMPTS",
    "OTEL_LOG_ASSISTANT_RESPONSES",
    "OTEL_LOG_TOOL_CONTENT",
    "OTEL_LOG_RAW_API_BODIES",
)

# With an http/* protocol and no endpoint set, the OTel SDK falls back to this.
# In a container with no local collector that means telemetry is exported into
# nothing -- enabled, costing something, arriving nowhere.
OTLP_HTTP_DEFAULT = ("127.0.0.1", 4318)
OTLP_GRPC_DEFAULT = ("127.0.0.1", 4317)

def _truthy(value: Any) -> bool:
    """Whether an env-style flag reads as on.

    `"TRUE"` and `"yes"` were read as off while telemetry was actually running.
    A false OFF is the same class of wrong answer as a false ON.
    """
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def in_coder_workspace() -> bool:
    """Whether this is a DevNext/Coder workspace, where the /s/<source> rule applies."""
    return bool(os.environ.get("CODER_WORKSPACE_NAME")
                or os.environ.get("CODER_AGENT_TOKEN")
                or Path("/etc/claude-code/managed-settings.json").exists())


CC_OTEL_OFF = "OFF"
CC_OTEL_ON = "ON"
CC_OTEL_NO_DESTINATION = "ON_BUT_NO_DESTINATION"
CC_OTEL_CONTENT_CAPTURE = "CONTENT_CAPTURE_ENABLED"
# Enabled and reaching a destination, but something in the config is wrong -- a
# missing exporter, the wrong source segment, over-collection. Without this,
# `ON` was returned alongside a non-empty problems list, which is the same class
# of false pass as the missing `user.id` this check exists to catch.
CC_OTEL_MISCONFIGURED = "ON_BUT_MISCONFIGURED"
CC_OTEL_UNREADABLE = "SETTINGS_UNREADABLE"
CC_OTEL_NOT_CLAUDE_CODE = "NOT_APPLICABLE"

# Values that routinely carry credentials. OTEL_EXPORTER_OTLP_HEADERS is the
# documented place to put `Authorization=Bearer <token>`, and this output is
# surfaced into a chat transcript.
CC_SECRET_HINTS = ("HEADERS", "TOKEN", "AUTH", "SECRET", "PASSWORD", "KEY")

# Self-serve wherever it can be, and a GitHub issue where it cannot.
#
# These strings used to say "ask the DevNext team" and "report this to the EDO
# team", which stopped being true the moment `/setup-workspace claude-otel` existed:
# the managed policy sets none of the four keys Catalyst needs, so a user-scope
# write takes effect and nobody has to wait on another team. Sending someone to file
# a request they do not need costs them a day and costs that team an interruption.
#
# Where it genuinely is not self-serve, the route is `/catalyst-feedback`, which
# opens a GitHub issue against this repo -- our queue, visible to us, rather than a
# message into someone else's. The one exception is content capture: that is an
# enterprise compliance matter, not a Catalyst setup problem, and GRC is the right
# destination.
SELF_SERVE_FIX = ("Fix it yourself with `/setup-workspace claude-otel --endpoint "
                      "dev` (or `prd`) -- it writes an env block to "
                      "~/.claude/settings.json after showing you the diff, then start "
                      "a new session. The managed policy does not set these keys, so "
                      "nothing overrides them.")
ESCALATE_TO_FEEDBACK = ("If that does not work, raise it with `/catalyst-feedback` so it "
                    "lands as a GitHub issue on this repo.")

CC_OTEL_REMEDIATION = {
    CC_OTEL_OFF: "Claude Code usage reporting is off. " + SELF_SERVE_FIX + " "
                 + ESCALATE_TO_FEEDBACK,
    CC_OTEL_ON: "Claude Code usage reporting is configured.",
    CC_OTEL_NO_DESTINATION: "Telemetry is enabled but has nowhere to go -- no OTLP endpoint is "
                            "set and nothing is listening on the local default, so data is "
                            "produced and discarded. " + SELF_SERVE_FIX + " "
                            + ESCALATE_TO_FEEDBACK,
    CC_OTEL_CONTENT_CAPTURE: "A content-capture switch is on, which sends prompt, response or "
                             "tool content. That needs a Governance, Risk and Compliance "
                             "review -- raise it with the EDO team.",
    # Deliberately does NOT say "data is arriving, so this is not urgent". That was
    # true when this verdict only covered a missing exporter, and became false when a
    # per-signal endpoint with no /v1/metrics path landed here too: that case POSTs
    # every batch to '/' and loses all of it. Telling someone total loss is not
    # urgent is worse than saying nothing.
    # "read the problems named with this verdict", not "listed above": the problems
    # are printed above it by `cmd_check` and `cmd_otel`, but inline immediately
    # before it by the background pass, and a remediation should not describe a layout
    # that depends on which caller rendered it.
    CC_OTEL_MISCONFIGURED: "Telemetry is enabled, but the configuration is not what Catalyst "
                           "expects -- read the problems named with this verdict before "
                           "assuming data is "
                           "arriving. Some of these lose part of what is sent; a metrics "
                           "endpoint missing its /v1/metrics path loses all of it, while still "
                           "looking correctly configured. " + SELF_SERVE_FIX + " "
                           + ESCALATE_TO_FEEDBACK,
    CC_OTEL_UNREADABLE: "A Claude Code settings file exists but will not parse, so the "
                        "telemetry state cannot be determined. The problem is that file's "
                        "syntax, not its contents -- report the named path to whoever owns "
                        "that layer (DevNext, for the managed policy).",
    CC_OTEL_NOT_CLAUDE_CODE: "Not running under Claude Code; this check does not apply.",
}


def detect_harness() -> str:
    """Which agent harness is this running under? Detected, not assumed."""
    if os.environ.get("CLAUDECODE") or os.environ.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude-code"
    if os.environ.get("VSCODE_PID") or os.environ.get("TERM_PROGRAM") == "vscode":
        return "vscode"
    return "unknown"


def claude_code_settings_layers() -> List[Path]:
    """Managed first, then user. Managed outranks everything a developer sets."""
    if sys.platform == "darwin":
        managed = Path("/Library/Application Support/ClaudeCode/managed-settings.json")
    elif os.name == "nt":
        managed = Path(r"C:\ProgramData\ClaudeCode\managed-settings.json")
    else:
        managed = Path("/etc/claude-code/managed-settings.json")
    return [managed, Path.home() / ".claude" / "settings.json"]


def _port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    import socket
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def probe_claude_code_otel(check_local_collector: bool = True) -> Dict[str, Any]:
    """Report Claude Code telemetry state, and which settings layer set it.

    Reads the settings files as well as the live environment, because a value can
    come from either and the user needs to know which -- a managed setting is not
    theirs to change.
    """
    if detect_harness() != "claude-code":
        return {"verdict": CC_OTEL_NOT_CLAUDE_CODE, "harness": detect_harness(),
                "values": {}, "sources": {}, "problems": [], "notes": []}

    # Later layers must not overwrite earlier (managed) ones.
    values: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    unreadable: List[str] = []
    for path in claude_code_settings_layers():
        if not path.exists():
            continue
        settings, err = read_user_settings(path)
        if err:
            # A policy file that exists but will not parse is not "telemetry is
            # off". Reporting OFF sent the user to ask DevNext about a setting
            # when the actual fault is a syntax error in their file. The Copilot
            # path has had SETTINGS_UNREADABLE all along; 5b now matches it.
            unreadable.append(f"{path}: {err}")
            continue
        # `env` is only iterable if it is actually a mapping. A malformed managed
        # file with `"env": "..."` or a list raised here and took down the whole
        # of `check` -- questions 1 to 4 included -- rather than returning a
        # verdict for the one question that could not be answered.
        env = (settings or {}).get("env")
        if not isinstance(env, dict):
            continue
        for key, val in env.items():
            if key not in values:
                values[key] = str(val)
                sources[key] = str(path)
    for key, val in os.environ.items():
        if (key.startswith("OTEL_") or key == CC_TELEMETRY_KEY) and key not in values:
            values[key] = val
            sources[key] = "process environment"

    result: Dict[str, Any] = {"harness": "claude-code", "values": values,
                              "sources": sources, "problems": [], "notes": []}

    if unreadable:
        result["problems"].extend(unreadable)
        result["verdict"] = CC_OTEL_UNREADABLE
        return result

    if not _truthy(values.get(CC_TELEMETRY_KEY)):
        result["verdict"] = CC_OTEL_OFF
        return result

    # Content switches are the enterprise's call, not Catalyst's: prompt and tool
    # logging may be required for security monitoring. So their being ON is not
    # reported as our failure. What IS our concern is where that content is
    # ROUTED -- see the leak check below.
    on_switches = [k for k in CC_CONTENT_SWITCHES if _truthy(values.get(k))]
    result["content_switches_on"] = on_switches

    # Attribution rides on the cost.usage / token.usage METRICS, so the metrics
    # endpoint is the one Catalyst depends on. Per-signal beats generic: the
    # generic variable is only a fallback for signals left unset.
    metrics_endpoint = (values.get("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT")
                        or values.get("OTEL_EXPORTER_OTLP_ENDPOINT"))
    endpoint = metrics_endpoint

    # Per-signal beats generic for the PROTOCOL too, and for the same reason. The
    # fragment this repo publishes sets OTEL_EXPORTER_OTLP_METRICS_PROTOCOL, so
    # reading only the generic variable meant our own recommended configuration
    # went unvalidated: METRICS_PROTOCOL=grpc against an http/protobuf collector
    # reported ON with no problems, and picked the wrong default port too.
    metrics_proto = (values.get("OTEL_EXPORTER_OTLP_METRICS_PROTOCOL")
                     or values.get("OTEL_EXPORTER_OTLP_PROTOCOL"))
    if not endpoint:
        proto = metrics_proto or "http/protobuf"
        host, port = OTLP_GRPC_DEFAULT if proto == "grpc" else OTLP_HTTP_DEFAULT
        listening = _port_open(host, port) if check_local_collector else None
        result["problems"].append(
            f"no OTLP endpoint is set, so the exporter falls back to {host}:{port}"
            + ("" if listening is not False else " and nothing is listening there"))
        # `is False` deliberately. `None` means the probe was skipped, and treating
        # that as "nothing is listening" reported ON_BUT_NO_DESTINATION for a
        # destination that was never tested.
        if listening is False:
            result["no_destination"] = True

    if "otlp" not in values.get("OTEL_METRICS_EXPORTER", ""):
        result["problems"].append(
            "OTEL_METRICS_EXPORTER does not include otlp, so metrics "
            "(claude_code.session.count and friends) are never exported")

    # The one place the two endpoint variables differ, and it is not intuitive:
    #   OTEL_EXPORTER_OTLP_ENDPOINT          -- a BASE url; the exporter appends
    #                                           the signal path itself
    #   OTEL_EXPORTER_OTLP_METRICS_ENDPOINT  -- used AS-IS; nothing is appended
    # So a host-only per-signal endpoint POSTs to `/`, which the Catalyst collector
    # answers with 404 (measured: POST / -> 404, POST /v1/metrics -> 200). Every
    # batch is rejected while the configuration still reads as correct -- the same
    # silent total loss as an unreachable host, which is exactly what this check is
    # for. Only checked for the per-signal variable; appending to the generic one
    # would be wrong.
    def _has_signal_path(url: str) -> bool:
        """Whether the URL's *path* is the metrics path.

        Compared on the parsed path rather than as a whole-string suffix: a legal
        endpoint with a query string or fragment ends in neither, so a suffix match
        flagged it while asserting something demonstrably untrue about it.
        """
        from urllib.parse import urlsplit
        try:
            return urlsplit(url).path.rstrip("/").endswith(CC_METRICS_PATH)
        except ValueError:
            return False

    per_signal = values.get("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT")
    generic = values.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    # The mirror-image mistake, and the more tempting one now that the fragment says
    # "NOTE THE /v1/metrics PATH. It is required" without qualifying which variable.
    # The generic endpoint is a BASE url: the exporter appends the signal path itself,
    # so a generic value that already carries it produces /v1/metrics/v1/metrics -> 404
    # -> total silent loss, and it was reported ON with no problems.
    if generic and _has_signal_path(generic):
        result["problems"].append(
            f"OTEL_EXPORTER_OTLP_ENDPOINT is {redact_url(generic)}, which already "
            f"carries {CC_METRICS_PATH}. The generic endpoint is a base URL and the "
            f"exporter appends the signal path itself, so this resolves to "
            f"{CC_METRICS_PATH}{CC_METRICS_PATH} and every batch is rejected. Drop the "
            "path here, or use OTEL_EXPORTER_OTLP_METRICS_ENDPOINT instead")
    if per_signal and not _has_signal_path(per_signal):
        result["problems"].append(
            f"OTEL_EXPORTER_OTLP_METRICS_ENDPOINT is {redact_url(per_signal)}, which "
            f"has no {CC_METRICS_PATH} path. Per-signal endpoints are used as-is -- "
            "unlike the generic OTEL_EXPORTER_OTLP_ENDPOINT, nothing is appended -- so "
            f"this POSTs to '/' and every batch is rejected. Append {CC_METRICS_PATH}")

    # CC_OTEL_EXPECTED was declared and never consulted, so the protocol went
    # unchecked: OTEL_EXPORTER_OTLP_PROTOCOL=grpc against an http/protobuf
    # collector reported ON with no problems while the data went nowhere.
    expected_proto = CC_OTEL_EXPECTED["OTEL_EXPORTER_OTLP_PROTOCOL"]
    if metrics_proto and metrics_proto != expected_proto:
        which = ("OTEL_EXPORTER_OTLP_METRICS_PROTOCOL"
                 if values.get("OTEL_EXPORTER_OTLP_METRICS_PROTOCOL")
                 else "OTEL_EXPORTER_OTLP_PROTOCOL")
        result["problems"].append(
            f"{which} is {metrics_proto!r}, but the Catalyst "
            f"collector speaks {expected_proto!r} -- the exporter will not be "
            "understood at the other end")

    # The /s/<source> producer partition is NOT deployed yet: cg-open-itg/catalyst-otel
    # PR #12 adds it, and the dev bucket currently holds only raw/year=... with no
    # source= prefix. So an endpoint without the segment is correct for the collector
    # that exists today, and flagging it MISCONFIGURED would fail the very endpoint
    # this repo recommends. Recorded as a note; promote it to a problem once #12 is
    # deployed and the partition is real.
    if endpoint and in_coder_workspace() and CC_SOURCE_SEGMENT not in endpoint:
        result["source_segment_missing"] = True
        # Recorded AND rendered. Storing the flag without printing it anywhere was
        # the same as discarding it: the "demoted to a note" decision only holds if
        # the note actually reaches the reader. `notes` never affects the verdict.
        result["notes"].append(
            f"the endpoint has no {CC_SOURCE_SEGMENT} segment, so this workspace's "
            "telemetry is not separated from the Copilot Chat population. Correct "
            "for today's collector -- cg-open-itg/catalyst-otel#12 adds the "
            "partition and is not deployed (both /s/* paths 404 while /v1/* "
            "answer). Nothing to do until it lands")

    # Also the enterprise's call, and also unreachable from here. TOOL_DETAILS
    # affects LOG records only -- it adds tool_parameters and command lines to
    # tool_result events and changes nothing about cost.usage or token.usage. So it
    # cannot dilute Catalyst's metrics and cannot reach a metrics-only collector.
    # Recorded, not reported as a problem.
    if _truthy(values.get(CC_OVER_COLLECTION_SWITCH)):
        result["tool_details_on"] = True

    # Attribution rides on the api_request event and the cost/token metrics, so
    # losing either exporter loses it. Metrics absence is already reported above;
    # this catches logs being off.
    # No logs exporter is required. `skill.name`, `agent.name`, `plugin.name` and
    # `marketplace.name` are attributes on the cost.usage and token.usage METRICS,
    # so attribution is complete from metrics alone. An earlier revision demanded
    # OTEL_LOGS_EXPORTER=otlp "or skill.name is never exported", which was wrong
    # and would have pushed operators toward shipping log records -- the signal
    # that carries prompt text -- to get something metrics already provide.
    #
    # What matters instead: content is only ever a LOG record, so if a content
    # switch is on AND logs resolve to the Catalyst collector, prompt text is
    # arriving here. That is the leak worth reporting.
    logs_endpoint = (values.get("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT")
                     or values.get("OTEL_EXPORTER_OTLP_ENDPOINT"))
    # An endpoint is not an export. With OTEL_LOGS_EXPORTER=none no log record
    # leaves the process, so a logs endpoint aimed at Catalyst carries nothing and
    # calling that a content leak is a false alarm -- and a costly one, because
    # CONTENT_CAPTURE is the verdict that sends someone to GRC.
    #
    # Deliberately conservative about *unset*: absent an explicit exporter this
    # returns True, so an unknown configuration is still reported. Being wrong in
    # the quiet direction here would mean missing a real leak, which is the one
    # error this check exists to prevent.
    logs_exporter = values.get("OTEL_LOGS_EXPORTER")
    logs_exported = ("otlp" in logs_exporter) if logs_exporter else True
    if on_switches and logs_exported and logs_endpoint and CATALYST_COLLECTOR_HINT in logs_endpoint:
        result["content_leak"] = True
        result["problems"].append(
            f"{', '.join(on_switches)} on, and the LOGS signal resolves to the "
            f"Catalyst collector ({redact_url(logs_endpoint)}) -- content is "
            "arriving here. Point OTEL_EXPORTER_OTLP_LOGS_ENDPOINT at the "
            "enterprise destination, and set only OTEL_EXPORTER_OTLP_METRICS_ENDPOINT "
            "to Catalyst. Metrics carry the attribution and can never carry prompt "
            "text.")
    elif on_switches and logs_endpoint and CATALYST_COLLECTOR_HINT in logs_endpoint:
        # Same routing mistake, currently inert. Worth saying, because re-enabling
        # the exporter would turn it into a live leak with no other warning.
        result["notes"].append(
            f"the LOGS signal points at the Catalyst collector "
            f"({redact_url(logs_endpoint)}) and content switches are on, but "
            f"OTEL_LOGS_EXPORTER is {logs_exporter!r}, so nothing is exported. "
            "Harmless today; setting the exporter back to otlp would make it a "
            "content leak, so fix the routing rather than relying on this")
    elif (values.get("OTEL_EXPORTER_OTLP_ENDPOINT") and on_switches
          and not values.get("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT")):
        # The `and not LOGS_ENDPOINT` is the whole point of the warning. It exists
        # because logs *fall back* to the generic endpoint -- so once a logs-specific
        # endpoint is set, they do not, and the warning was firing at a configuration
        # that had already done exactly what it was about to advise. Which is worse
        # than noise: it reported ON_BUT_MISCONFIGURED for the correct setup.
        result["problems"].append(
            "the generic OTEL_EXPORTER_OTLP_ENDPOINT is set while content logging "
            "is on, and no OTEL_EXPORTER_OTLP_LOGS_ENDPOINT overrides it. The generic "
            "endpoint is the fallback for every unset signal, so logs follow it -- set "
            "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT explicitly so the content signal is "
            "routed deliberately rather than by default.")

    # Content capture is the loudest finding; a dead destination is the next,
    # because everything else is moot if nothing arrives.
    # Reserved for content actually reaching Catalyst. A content switch on its own
    # is the enterprise's business and no longer produces this verdict.
    if result.get("content_leak"):
        result["verdict"] = CC_OTEL_CONTENT_CAPTURE
    elif result.get("no_destination"):
        result["verdict"] = CC_OTEL_NO_DESTINATION
    elif result["problems"]:
        # `ON` has a documented meaning -- enabled, with a destination and both
        # exporters. Returning it while problems are listed contradicts the
        # remediation text and tells the user they are fine when they are not.
        result["verdict"] = CC_OTEL_MISCONFIGURED
    else:
        result["verdict"] = CC_OTEL_ON
    return result


def redact(key: str, value: str) -> str:
    """Hide values that carry credentials.

    This report is printed into a chat transcript, and
    `OTEL_EXPORTER_OTLP_HEADERS` is the documented place for
    `Authorization=Bearer <token>`. Presence is what the check needs; the value
    is not, so it is reported as set-but-hidden rather than echoed.
    """
    if any(hint in key.upper() for hint in CC_SECRET_HINTS):
        return f"<redacted, {len(value)} chars>" if value else "<empty>"
    return value


def redact_url(url: str) -> str:
    """An endpoint reduced to scheme, host, port and path.

    Endpoints go into problem strings that `cmd_otel` prints straight into a chat
    transcript, and an OTLP URL is allowed to carry credentials in two places the
    eye skips: userinfo (`https://user:token@host/`) and the query string, which
    some gateways use for an API key. Neither tells the reader anything the check
    needs -- which collector it is, is the whole question -- so both are dropped
    rather than echoed.

    Not merged into `redact()`: that one keys off the *variable name*, and an
    endpoint variable is not secret-hinting. This keys off the value's shape.
    """
    from urllib.parse import urlsplit
    try:
        parts = urlsplit(url)
        # `urlsplit` accepts `https://host:abc` and defers the error to `.port`,
        # which raises ValueError. Touched inside the try on purpose: this helper
        # is called *before* probe_otel_endpoint gets a chance to return its
        # `bad-url` diagnostic, so raising here crashed the command that exists to
        # explain the malformed endpoint.
        port = parts.port
        hostname = parts.hostname
    except ValueError:
        return "<unparseable endpoint>"
    if not hostname:
        # Not URL-shaped, so there is no structure to trust. Say so instead of
        # returning it verbatim and hoping.
        return "<unparseable endpoint>"
    netloc = hostname + (f":{port}" if port else "")
    shown = f"{parts.scheme}://{netloc}{parts.path}" if parts.scheme else netloc + parts.path
    if parts.username or parts.password:
        shown += "  [credentials in the URL, hidden]"
    if parts.query:
        shown += "  [query string hidden]"
    return shown


def probe_otel_endpoint(url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Can this machine reach the collector? Distinguishes the two failures.

    Off-network and on-VPN-but-unreachable need different advice: the first is
    "connect to VPN", the second is "tell the EDO team", because some remote VPN
    configurations cannot route to this service and retrying never helps.
    """
    import socket
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host = parsed.hostname or ""
    # Never echo the caller's URL. These details are printed straight into a chat
    # transcript, and the malformed-endpoint cases are exactly where a mistyped URL
    # with userinfo or a query credential ends up -- so the one branch most likely
    # to contain a secret was the one quoting it verbatim.
    shown = redact_url(url)
    # `parsed.port` raises ValueError on a malformed port such as
    # `https://collector:abc`, so the promised `bad-url` result has to catch it
    # rather than letting the probe crash.
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError:
        return {"reachable": False, "kind": "bad-url",
                "detail": f"{shown} has an invalid port"}
    if not host:
        return {"reachable": False, "kind": "bad-url",
                "detail": f"cannot parse a host from {shown}"}
    if parsed.scheme not in ("http", "https"):
        return {"reachable": False, "kind": "bad-url",
                "detail": f"{shown} is not an http(s) URL"}

    try:
        socket.getaddrinfo(host, port)
    except socket.gaierror as exc:
        return {
            "reachable": False,
            "kind": "dns",
            "detail": f"{host} does not resolve ({exc}). You are probably off the "
                      "corporate network -- connect to VPN and re-run.",
        }
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
    except OSError as exc:
        return {
            "reachable": False,
            "kind": "unreachable",
            "detail": f"{host} resolves but will not accept a connection ({exc}). If you are "
                      "on VPN, some remote setups cannot route to this service and retrying "
                      "will not help -- raise it with /catalyst-feedback so it lands as a "
                      "GitHub issue we can act on.",
        }

    # A TCP accept is not evidence the collector works. A load balancer with no
    # healthy backend accepts the connection and then resets during the TLS
    # handshake, so stopping at connect() would report a dead collector as fine.
    if parsed.scheme != "https":
        sock.close()
        return {"reachable": True, "kind": "ok", "detail": f"connected to {host}:{port}"}

    import ssl
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(sock, server_hostname=host):
            return {"reachable": True, "kind": "ok",
                    "detail": f"TLS established to {host}:{port}"}
    except ssl.SSLCertVerificationError as exc:
        return {
            "reachable": False,
            "kind": "tls-verify",
            "detail": f"{host}:{port} accepted the connection but its certificate did not "
                      f"verify ({exc.verify_message}). That is corporate TLS interception -- "
                      "point at the CA bundle (NODE_EXTRA_CA_CERTS for Claude Code); never "
                      "disable verification.",
        }
    except (ssl.SSLError, OSError) as exc:
        return {
            "reachable": False,
            "kind": "tls-reset",
            "detail": f"{host}:{port} accepted the TCP connection then failed the TLS "
                      f"handshake ({exc}). Two causes look identical from here: a network "
                      "policy that allows the TCP connection but blocks the flow -- likely "
                      "if you are in a dev environment reaching an internal or production "
                      "endpoint -- or a load balancer with no healthy backend. Neither is "
                      "fixable from your own config. Check whether the endpoint is reachable "
                      "from your network before concluding the collector is down.",
        }
    finally:
        try:
            sock.close()
        except OSError:
            pass


# --- Question 2: which workspace? (config file, no SDK needed) ---------------
def read_profiles() -> List[Dict[str, Any]]:
    """Parse ~/.databrickscfg into a list of profiles.

    Deliberately does not use the SDK: a user who has not installed anything yet
    still deserves to be told which workspaces they have configured.
    """
    if not DATABRICKS_CFG.exists():
        return []

    # `[DEFAULT]` is a real, and usually the primary, Databricks profile -- but
    # configparser treats a section by that name as its magic defaults block:
    # it is omitted from sections() and its keys are inherited by every other
    # section, which would both hide the DEFAULT profile and mis-classify the
    # others' auth style. Renaming the default section keeps [DEFAULT] ordinary.
    parser = configparser.ConfigParser(default_section="__catalyst_no_default__")
    try:
        parser.read(DATABRICKS_CFG)
    except configparser.Error:
        return []

    profiles = []
    for name in parser.sections():
        section = parser[name]
        profiles.append(
            {
                "profile": name,
                "host": section.get("host", ""),
                # Record only which auth *style* is configured, never a secret.
                # An explicit auth_type outranks the presence of a token key.
                "auth": (
                    "oauth-m2m" if section.get("client_id")
                    else section.get("auth_type") if section.get("auth_type")
                    else "pat" if section.get("token")
                    else "unknown"
                ),
            }
        )
    return profiles


def active_workspace(profiles: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Determine which workspace the environment currently points at.

    Env vars win over the config file, matching SDK resolution order.

    `active_profile` is the name of the profile actually in effect, or None when
    the host came from `DATABRICKS_HOST` and no profile is selected. It is
    deliberately not defaulted to "DEFAULT": marking a DEFAULT profile as active
    while `Host:` shows an unrelated env-var host would contradict itself in the
    report. Callers pass `profiles` in to avoid re-reading the config file.
    """
    if profiles is None:
        profiles = read_profiles()

    env_host = os.environ.get("DATABRICKS_HOST", "")
    env_profile = os.environ.get("DATABRICKS_CONFIG_PROFILE", "")
    has_default = any(p["profile"] == "DEFAULT" for p in profiles)

    def _host_of(name: str) -> str:
        return next((p["host"] for p in profiles if p["profile"] == name), "")

    if env_host:
        # An explicit host wins outright, and no profile is in effect.
        return {"host": env_host, "profile": None, "active_profile": None,
                "resolved_from": "DATABRICKS_HOST"}
    if env_profile:
        return {"host": _host_of(env_profile), "profile": env_profile,
                "active_profile": env_profile,
                "resolved_from": f"DATABRICKS_CONFIG_PROFILE={env_profile}"}
    if has_default:
        return {"host": _host_of("DEFAULT"), "profile": "DEFAULT",
                "active_profile": "DEFAULT",
                "resolved_from": "~/.databrickscfg [DEFAULT]"}

    return {"host": "", "profile": None, "active_profile": None, "resolved_from": "none"}


def auth_style() -> Dict[str, Any]:
    """Classify how the user is authenticating, and flag the known PAT trap.

    docs/install.md tells new users to set DATABRICKS_TOKEN, but
    connect-databricks refuses it (DBX-SEC-002) and exits 3. Rather than silently
    pick a side, report the collision so the user sees it here instead of hitting
    an opaque failure three phases later.
    """
    has_pat = bool(os.environ.get("DATABRICKS_TOKEN"))
    has_oauth = bool(
        os.environ.get("DATABRICKS_CLIENT_ID")
        and os.environ.get("DATABRICKS_CLIENT_SECRET")
    )
    return {
        "pat_env_set": has_pat,
        "oauth_m2m_env_set": has_oauth,
        "will_be_refused_by_connect_databricks": has_pat and not has_oauth,
    }


# --- Questions 3 and 4: access and placement (needs the SDK) ----------------
def _workspace_client():
    """Return a WorkspaceClient, preferring Catalyst's tagged client.

    The repo's `get_workspace_client()` adds product attribution (identity.py),
    so it is the better choice when available. But it lives behind a package
    whose `__init__` chain pulls in heavier optional deps -- and a pre-flight that
    breaks when the environment is broken is useless. So fall back to the plain
    SDK, which needs only `databricks-sdk` and resolves auth from the environment
    and ~/.databrickscfg exactly the same way.
    """
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    try:
        from skills.clients.databricks_tools_core.auth import get_workspace_client

        return get_workspace_client(), "catalyst-client"
    except Exception:
        from databricks.sdk import WorkspaceClient

        return WorkspaceClient(), "databricks-sdk"


def probe_access() -> Dict[str, Any]:
    """Probe live access. Returns a 'reachable: False' verdict, never raises."""
    result: Dict[str, Any] = {
        "reachable": False,
        "reason": None,
        "identity": None,
        "client": None,
        "warehouses": [],
        "catalogs": [],
        # Tracked separately from `reason`, and from each other. An empty list
        # because a lookup *failed* is a completely different finding from an
        # empty list because the user genuinely has no access -- conflating them
        # sends people off to file entitlement tickets they do not need.
        "catalogs_error": None,
        "warehouses_error": None,
    }

    try:
        w, which = _workspace_client()
        result["client"] = which
    except Exception as exc:
        result["reason"] = f"no Databricks client available: {exc}"
        return result

    try:
        result["identity"] = w.current_user.me().user_name
        result["reachable"] = True
    except Exception as exc:
        result["reason"] = f"could not authenticate: {exc}"
        return result

    try:
        result["warehouses"] = [
            {"id": wh.id, "name": wh.name,
             "state": getattr(wh.state, "value", wh.state)}
            for wh in islice(w.warehouses.list(), 10)
        ]
    except Exception as exc:
        result["warehouses_error"] = str(exc)

    try:
        result["catalogs"] = [c.name for c in islice(w.catalogs.list(), 50)]
    except Exception as exc:
        result["catalogs_error"] = str(exc)

    return result


# --- Verdict ----------------------------------------------------------------
def exit_code_for(state: Dict[str, Any]) -> int:
    """Top-priority blocker, in the order a user must fix them."""
    tool = state["toolchain"]
    if not tool["python_ok"] or not tool["deps_ok"]:
        return 2
    access = state["access"]
    if not access["reachable"]:
        return 3
    # A failed lookup must outrank the "no access" verdicts below. If the call
    # errored we do not know whether the user has access, and telling them to
    # request an entitlement they may already hold wastes their time and their
    # platform team's. Transient 5xx, a token expiring mid-run, and a network
    # blip all land here.
    if access.get("catalogs_error") or access.get("warehouses_error"):
        return 6
    if not access["catalogs"]:
        return 4
    if not access["warehouses"]:
        return 5
    return 0


REMEDIATION = {
    2: "Run /setup-workspace to install Python 3.13 and the Catalyst dependencies through cgrepo.",
    3: "Run /databricks-config to pick or authenticate a workspace (`databricks auth login`).",
    4: "You are authenticated but see no catalogs. This is an entitlement gap, not a "
       "setup gap -- request Unity Catalog access from your data platform team.",
    5: "No SQL warehouse is reachable. Run /configure-sql-warehouse, or ask for access "
       "to a shared warehouse.",
    6: "A lookup failed, so access could not be determined -- this is NOT necessarily an "
       "entitlement gap. Read the error in section 3 and re-run; if it persists and names "
       "authentication, re-run `databricks auth login`.",
    0: "Ready to build.",
}


def gather() -> Dict[str, Any]:
    toolchain = probe_toolchain()
    # Read the config once and thread it through; active_workspace() used to
    # re-parse it up to three times per call.
    profiles = read_profiles()
    state: Dict[str, Any] = {
        "toolchain": toolchain,
        "auth": auth_style(),
        "active_workspace": active_workspace(profiles),
        "profiles": profiles,
        # Skip the live probe when the toolchain cannot support it -- the
        # blocker is already known and probing would only add noise.
        "access": (
            probe_access()
            if toolchain["deps_ok"]
            else {
                "reachable": False,
                "reason": "dependencies not installed",
                "identity": None,
                "client": None,
                "warehouses": [],
                "catalogs": [],
                "catalogs_error": None,
                "warehouses_error": None,
            }
        ),
    }
    # Advisory only -- see the note above probe_otel. Computed after the exit
    # code so it cannot influence it.
    state["exit_code"] = exit_code_for(state)
    state["verdict"] = "READY" if state["exit_code"] == 0 else "NOT READY"
    state["next_step"] = REMEDIATION[state["exit_code"]]
    state["otel"] = probe_otel()
    state["cc_otel"] = probe_claude_code_otel()
    return state


def _yaml_scalar(v: Any) -> str:
    if v is None:
        return '""'
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return json.dumps(str(v))


def write_cache(state: Dict[str, Any], path: Path = CACHE_FILE) -> Path:
    """Write .catalyst-env.yml. Hand-rolled so the cache works before PyYAML."""
    a, t, w = state["access"], state["toolchain"], state["active_workspace"]
    lines = [
        "# Written by /dplc-preflight -- read by downstream skills, do not hand-edit.",
        f"verdict: {state['verdict']}",
        f"exit_code: {state['exit_code']}",
        "toolchain:",
        f"  python_version: {_yaml_scalar(t['python_version'])}",
        f"  python_ok: {_yaml_scalar(t['python_ok'])}",
        f"  deps_ok: {_yaml_scalar(t['deps_ok'])}",
        "workspace:",
        f"  host: {_yaml_scalar(w['host'])}",
        f"  profile: {_yaml_scalar(w['profile'])}",
        f"  resolved_from: {_yaml_scalar(w['resolved_from'])}",
        f"  identity: {_yaml_scalar(a['identity'])}",
        f"  reachable: {_yaml_scalar(a['reachable'])}",
        "access:",
        # Downstream skills must be able to tell "no access" from "could not
        # tell", so the errors are cached, not just printed.
        f"  catalogs_error: {_yaml_scalar(a.get('catalogs_error'))}",
        f"  warehouses_error: {_yaml_scalar(a.get('warehouses_error'))}",
        f"  catalog_count: {len(a['catalogs'])}",
        "  catalogs:",
    ]
    lines += [f"    - {_yaml_scalar(c)}" for c in a["catalogs"]] or ["    []"]
    lines.append("  warehouses:")
    lines += [
        f"    - {_yaml_scalar(wh.get('name'))}  # {wh.get('state', 'unknown')}"
        for wh in a["warehouses"]
    ] or ["    []"]
    otel = state.get("otel") or {}
    lines += [
        "otel:",
        f"  verdict: {_yaml_scalar(otel.get('verdict'))}",
        f"  settings_path: {_yaml_scalar(otel.get('settings_path'))}",
        # Which collector, so a downstream skill reading this cache can tell a
        # laptop reporting into dev from one reporting into prd.
        f"  collector: {_yaml_scalar(otel.get('collector'))}",
        # Cached so a later run can say "configured N days ago" rather than
        # re-nagging about a restart that has certainly happened by now.
        f"  edited_seconds_ago: {_yaml_scalar(int(otel['edited_seconds_ago']) if otel.get('edited_seconds_ago') is not None else None)}",
        "  problems:",
    ]
    lines += [f"    - {_yaml_scalar(p)}" for p in otel.get("problems", [])] or ["    []"]
    cc = state.get("cc_otel") or {}
    lines += [
        "claude_code_otel:",
        f"  verdict: {_yaml_scalar(cc.get('verdict'))}",
        f"  harness: {_yaml_scalar(cc.get('harness'))}",
        "  problems:",
    ]
    lines += [f"    - {_yaml_scalar(p)}" for p in cc.get("problems", [])] or ["    []"]
    lines.append(f"next_step: {_yaml_scalar(state['next_step'])}")
    path.write_text("\n".join(lines) + "\n")
    return path


def _mark(ok: bool) -> str:
    return "ok" if ok else "MISSING"


def cmd_check(write: bool = True) -> int:
    s = gather()
    t, w, a, auth = s["toolchain"], s["active_workspace"], s["access"], s["auth"]

    print("AI Catalyst pre-flight")
    print("")
    print("1. Can you run Catalyst?")
    print(f"   Python:          {t['python_version']} ({_mark(t['python_ok'])}, need >= 3.10)")
    if t["python_too_new"]:
        print("     warning: newer than the recommended 3.13; dependency wheels may lag.")
    print(f"   Dependencies:    {_mark(t['deps_ok'])}"
          + (f" (missing: {', '.join(t['missing_imports'])})" if t["missing_imports"] else ""))
    print(f"   databricks CLI:  {'present' if t['databricks_cli'] else 'absent'}")

    print("")
    print("2. Which workspace are you pointed at?")
    if w["host"]:
        print(f"   Host:            {w['host']}")
        print(f"   Resolved from:   {w['resolved_from']}")
    elif s["profiles"]:
        # The common zero-to-one case: workspaces exist but none is selected.
        # Say that plainly rather than "none configured", which reads as "you
        # have nothing" when in fact the user just has to pick.
        print("   Host:            none selected yet")
        print(f"   Resolved from:   nothing set -- but {len(s['profiles'])} profile(s) are "
              "configured, so pick one")
        print("   To select:       export DATABRICKS_CONFIG_PROFILE=<profile>")
    else:
        print("   Host:            none configured")
        print("   Resolved from:   nothing set, and no profiles exist yet")
    if s["profiles"]:
        print(f"   Also available:  {len(s['profiles'])} profile(s) in ~/.databrickscfg")
        for p in s["profiles"]:
            active = " <- active" if p["profile"] == w["active_profile"] else ""
            print(f"     - {p['profile']}: {p['host'] or '(no host)'} [{p['auth']}]{active}")
    else:
        print("   Also available:  no profiles in ~/.databrickscfg")
    if auth["will_be_refused_by_connect_databricks"]:
        print("   WARNING: DATABRICKS_TOKEN is set. /connect-databricks refuses PATs")
        print("            (DBX-SEC-002) and will exit 3. Use `databricks auth login`")
        print("            for interactive work, or set DATABRICKS_CLIENT_ID and")
        print("            DATABRICKS_CLIENT_SECRET for a service principal.")

    print("")
    print("3. Do you have access?")
    if a["reachable"]:
        print(f"   Authenticated:   yes, as {a['identity']}")
        # Distinguish "looked and found none" from "could not look". Previously
        # the error text was captured into the report state and never printed,
        # so a failed lookup was indistinguishable from a real entitlement gap.
        if a.get("catalogs_error"):
            print(f"   Catalogs:        LOOKUP FAILED -- {a['catalogs_error']}")
        else:
            print(f"   Catalogs:        {len(a['catalogs'])} visible")
        if a.get("warehouses_error"):
            print(f"   Warehouses:      LOOKUP FAILED -- {a['warehouses_error']}")
        else:
            print(f"   Warehouses:      {len(a['warehouses'])} reachable")
            for wh in a["warehouses"][:5]:
                print(f"     - {wh['name']} ({wh['state']})")
        if a.get("catalogs_error") or a.get("warehouses_error"):
            print("   NOTE: a failed lookup is not evidence of missing entitlements.")
    else:
        print(f"   Authenticated:   no -- {a['reason']}")

    print("")
    print("4. Where would your data product go?")
    if a["catalogs"]:
        print("   Candidate catalogs you can actually write to:")
        for c in a["catalogs"][:12]:
            print(f"     - {c}")
        print("   /build-preflight maps these to SAP / DAP / CAP / Sandbox placement.")
    elif a.get("catalogs_error"):
        print("   Undetermined -- the catalog lookup failed (see section 3). Re-run.")
    else:
        print("   Unknown -- needs catalog access first.")

    print("")
    print("5. Is Copilot Chat usage reporting on?")
    o = s["otel"]
    # Question 5 is about VS Code. On a Coder workspace with no VS Code at all it
    # reported NOT_CONFIGURED and told the user to run `/setup-workspace otel`,
    # which then exits "no VS Code User settings.json found" -- a dead end this
    # report generated. Nothing below applies in that case; 5b covers what does.
    if not o.get("settings_path") and detect_harness() == "claude-code":
        print("   Not applicable -- no VS Code settings file here, and this is a Claude")
        print("   Code session. See 5b for the reporting that applies. Nothing to do.")
    else:
        print(f"   Reporting:       {o['verdict']}")
        if o["settings_path"]:
            print(f"   Settings file:   {o['settings_path']}")
        else:
            print("   Settings file:   none found (looked in "
                  f"{len(o['searched'])} standard locations)")
        for problem in o["problems"]:
            print(f"     - {problem}")
        for note in o.get("notes", []):
            print(f"     note: {note}")
        # Printed for EVERY verdict, not just the healthy ones. NOT_CONFIGURED,
        # MISCONFIGURED and SETTINGS_UNREADABLE are exactly what reading a product you
        # are not running produces, so confining this to OK/PENDING withheld it from
        # the cases that need it most.
        if o.get("other_products"):
            print(f"   Note: {len(o['other_products'])} other VS Code settings file(s) exist "
                  "and were NOT checked -- if you run a different VS Code build, this")
            print("         verdict may be about the wrong file:")
            for other in o["other_products"]:
                print(f"         {other}")
        if o["verdict"] == OTEL_CAPTURE_CONTENT:
            print("   COMPLIANCE: conversation text would be sent. This needs a GRC review;")
            print("               set captureContent back to false.")
        elif o["verdict"] in (OTEL_OK, OTEL_PENDING_RESTART):
            print(f"   Reporting as:    {o.get('identity') or 'ANONYMOUS (no user.id set)'}")
            print("   Note: reporting starts on Developer: Reload Window -- that is enough.")
            print("         A full quit also works but is not required. Either way the")
            print("         failure is silent, so this check is the only confirmation.")
        print(f"   {OTEL_REMEDIATION[o['verdict']]}")

    cc = s["cc_otel"]
    if cc["verdict"] != CC_OTEL_NOT_CLAUDE_CODE:
        print("")
        print("5b. Claude Code usage reporting (this harness)")
        print(f"   Reporting:       {cc['verdict']}")
        # Per-signal keys are listed FIRST and unconditionally-if-present. With the
        # metrics-only policy they are the ones that decide where data goes, so a
        # report that showed only the generic keys said `ON` without ever naming the
        # destination -- which is the fact you need to diagnose anything here.
        for key in (CC_TELEMETRY_KEY, "OTEL_METRICS_EXPORTER",
                    "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
                    "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL",
                    "OTEL_LOGS_EXPORTER", "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
                    "OTEL_EXPORTER_OTLP_PROTOCOL", "OTEL_EXPORTER_OTLP_ENDPOINT"):
            if key in cc["values"]:
                src = cc["sources"].get(key, "?")
                where = "managed" if "managed-settings" in src else (
                    "user" if str(Path.home()) in src else "env")
                shown = (redact_url(cc["values"][key]) if key.endswith("_ENDPOINT")
                         else redact(key, cc["values"][key]))
                print(f"     {key} = {shown}  [{where}]")
        # Where each signal actually resolves, after per-signal-beats-generic. Two
        # keys can both be set and it is not obvious which wins, and "logs go to the
        # localhost default and are discarded" is invisible from the key list alone.
        m_dest = (cc["values"].get("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT")
                  or cc["values"].get("OTEL_EXPORTER_OTLP_ENDPOINT"))
        l_dest = (cc["values"].get("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT")
                  or cc["values"].get("OTEL_EXPORTER_OTLP_ENDPOINT"))
        print(f"     -> metrics resolve to: {redact_url(m_dest) if m_dest else 'the localhost default'}")
        print(f"     -> logs resolve to:    {redact_url(l_dest) if l_dest else 'the localhost default'}")
        for problem in cc["problems"]:
            print(f"     - {problem}")
        for note in cc.get("notes") or []:
            print(f"     note: {note}")
        if cc["verdict"] == CC_OTEL_CONTENT_CAPTURE:
            print("   COMPLIANCE: a content-capture switch is on. Needs a GRC review.")
        print(f"   {CC_OTEL_REMEDIATION[cc['verdict']]}")

    print("")
    print(f"Verdict: {s['verdict']} (exit {s['exit_code']})")
    print(f"Next:    {s['next_step']}")
    # Said separately, and per harness, so it never reads as a blocker on the main
    # verdict. Reporting only the Copilot verdict here meant a Claude Code machine
    # printed OFF / ON_BUT_NO_DESTINATION / ON_BUT_MISCONFIGURED without the
    # "does not affect readiness" qualifier -- the one thing this line exists to say.
    advisory = []
    if o["verdict"] not in (OTEL_OK, OTEL_DISABLED):
        advisory.append(f"Copilot Chat usage reporting is {o['verdict']}")
    if cc["verdict"] not in (CC_OTEL_NOT_CLAUDE_CODE, CC_OTEL_ON):
        advisory.append(f"Claude Code usage reporting is {cc['verdict']}")
    for note in advisory:
        print(f"Also:    {note} (advisory, does not affect readiness)")

    if write:
        try:
            print(f"Cached:  {write_cache(s)}")
        except OSError as exc:
            print(f"Cache:   could not write .catalyst-env.yml ({exc})")

    return s["exit_code"]


def cmd_workspaces() -> int:
    profiles = read_profiles()
    active = active_workspace(profiles)
    if not profiles:
        print(f"No profiles found in {DATABRICKS_CFG}.")
        print("Run `databricks auth login --host <workspace-url>` to add one,")
        print("or invoke /databricks-config for the guided path.")
        return 3
    print(f"Databricks profiles in {DATABRICKS_CFG}:")
    for p in profiles:
        mark = " <- active" if p["profile"] == active["active_profile"] else ""
        print(f"  {p['profile']}: {p['host'] or '(no host)'} [{p['auth']}]{mark}")
    if active["active_profile"] is None and active["host"]:
        print(f"None marked active: DATABRICKS_HOST overrides the config "
              f"({active['host']}).")
    return 0


def cmd_otel(probe_endpoint: bool = False) -> int:
    """Report usage-reporting config alone. Exit 0 unless captureContent is on.

    captureContent is the only nonzero case because it is the only one with a
    consequence the user cannot see and should not ignore. "Not configured" is a
    normal state, not a failure.
    """
    o = probe_otel()
    print("Copilot Chat usage reporting")
    print("")
    print(f"  Verdict:       {o['verdict']}")
    print(f"  Settings file: {o['settings_path'] or 'none found'}")
    if not o["settings_path"]:
        for p in o["searched"]:
            print(f"    looked at: {p}")
    for key in OTEL_EXPECTED:
        if key in o["values"]:
            value = o["values"][key]
            # The endpoint is an OTLP URL read from a user-editable settings.json, so
            # it carries exactly the userinfo/query credential risk redact_url exists
            # for. It was being printed raw while the Claude Code side was sanitised.
            shown = (redact_url(str(value)) if key.endswith("otlpEndpoint")
                     else repr(value))
            print(f"    {key} = {shown}")
    for problem in o["problems"]:
        print(f"  - {problem}")
    for note in o.get("notes", []):
        print(f"  note: {note}")
    print("")
    print(f"  {OTEL_REMEDIATION[o['verdict']]}")

    if probe_endpoint:
        endpoint = o["values"].get(
            "github.copilot.chat.otel.otlpEndpoint",
            OTEL_EXPECTED["github.copilot.chat.otel.otlpEndpoint"],
        )
        print("")
        print(f"  Endpoint:      {endpoint}")
        r = probe_otel_endpoint(str(endpoint))
        print(f"  Reachable:     {'yes' if r['reachable'] else 'no'} ({r['kind']})")
        print(f"    {r['detail']}")

    cc = probe_claude_code_otel()
    if cc["verdict"] != CC_OTEL_NOT_CLAUDE_CODE:
        print("")
        print("Claude Code usage reporting (this harness)")
        print(f"  Verdict:       {cc['verdict']}")
        for k in sorted(cc["values"]):
            if k.startswith("OTEL_") or k == CC_TELEMETRY_KEY:
                # Endpoint keys need URL-shaped redaction, not name-based: `redact`
                # keys off secret-hinting *names* and `..._ENDPOINT` is not one, so
                # sanitising only the leak message still let a userinfo credential
                # through here -- three lines above it.
                shown = (redact_url(cc["values"][k]) if k.endswith("_ENDPOINT")
                         else redact(k, cc["values"][k]))
                print(f"    {k} = {shown}  [{cc['sources'].get(k,'?')}]")
        for problem in cc["problems"]:
            print(f"  - {problem}")
        for note in cc.get("notes") or []:
            print(f"  note: {note}")
        print(f"  {CC_OTEL_REMEDIATION[cc['verdict']]}")

        # Reachability for OUR endpoint, not just Copilot's. Without this the
        # published fragment points at the production collector, which is not
        # routable from an oz-dev workspace, and the resulting total data loss is
        # invisible: the exporter drops batches silently and every local check
        # still says ON. The endpoint value stays as published -- prd is the
        # intended destination -- but "unreachable" should cost one command to
        # discover, not a quarter of missing dashboards.
        if probe_endpoint:
            cc_endpoint = (cc["values"].get("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT")
                           or cc["values"].get("OTEL_EXPORTER_OTLP_ENDPOINT"))
            print("")
            if not cc_endpoint:
                print("  Endpoint:      none set (the exporter falls back to localhost)")
            else:
                print(f"  Endpoint:      {redact_url(cc_endpoint)}")
                r = probe_otel_endpoint(str(cc_endpoint))
                print(f"  Reachable:     {'yes' if r['reachable'] else 'no'} ({r['kind']})")
                print(f"    {r['detail']}")
                if not r["reachable"] and CATALYST_COLLECTOR_HINT in cc_endpoint:
                    print("    Metrics are being dropped. If this is the production "
                          "collector from an oz-dev workspace, that is network "
                          "isolation rather than an outage -- the dev collector is "
                          "reachable; see docs/telemetry/managed-settings-otel.json.")

    bad = (o["verdict"] == OTEL_CAPTURE_CONTENT
           or cc["verdict"] == CC_OTEL_CONTENT_CAPTURE)
    return 1 if bad else 0


# ---------------------------------------------------------------------------
# Background checks -- the quiet pass that runs once a session
# ---------------------------------------------------------------------------
#
# Questions 1-5b answer "can I build a data product here". These answer a
# different question: "is something about to fail for a reason I will not
# recognise". They are the failures that surface as a cryptic error halfway
# through a task rather than as a setup problem at the start.
#
# Three rules, all deliberate:
#   * ADVISORY ONLY. Never changes an exit code, never blocks. Same contract as
#     questions 5 and 5b.
#   * SILENT WHEN CLEAN. Prints nothing at all when there is nothing wrong, so
#     it costs a healthy session no attention.
#   * ONCE PER SESSION. A marker file suppresses repeats, because a check that
#     nags is a check people learn to skip.

def _run(cmd: List[str], timeout: int = 20) -> tuple[int, str]:
    """Run a command for the background checks. Never raises.

    The rest of this script deliberately shells out to nothing -- it reads files
    and answers from them. The background pass is the exception, because
    credential liveness and installed versions cannot be read off disk. Failures
    (missing binary, timeout, non-zero) all come back as a code and text so a
    single broken tool cannot take the pass down.
    """
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)


BACKGROUND_MARKER = Path.home() / ".cache" / "catalyst" / "background-checks.json"
BACKGROUND_TTL_SECONDS = 8 * 3600      # a working day; re-runs next session

# Ranges we publish, read from the file that documents them rather than copied.
#
# `skills/requirements.txt` says in as many words that the range "stays here, in
# this shape, because /build-preflight reads it as text for its tool-version drift
# check" -- so a second copy here would have gone stale the first time the range
# moved, while still claiming to check that file. The Databricks line is
# *commented out* there on purpose (the PyPI `databricks-cli` is the deprecated
# legacy Python CLI and the pin can never resolve), so the parser has to read
# commented lines, which is why this is not the pip-spec parser in
# setup_workspace.py.
SKILLS_REQUIREMENTS = Path(__file__).resolve().parents[2] / "requirements.txt"

_TOOL_SPEC_SOURCES = {
    # tool name -> distribution name to look for in requirements.txt
    "databricks": "databricks-cli",
}


def read_tool_range(tool: str,
                    requirements: Optional[Path] = None) -> Optional[tuple]:
    """`(floor_spec, ceiling_spec)` for *tool*, or None if not declared.

    Reads commented and uncommented lines alike. Returns None rather than a
    fabricated default when the line is absent: a check that invents a range would
    report drift against a number nobody published.
    """
    import re as _re
    dist = _TOOL_SPEC_SOURCES.get(tool)
    if not dist:
        return None
    path = requirements or SKILLS_REQUIREMENTS
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    pattern = _re.compile(
        r"^\s*#?\s*" + _re.escape(dist) + r"\s*(>=?[\d.]+)\s*,\s*(<=?[\d.]+)\s*$")
    for line in text.splitlines():
        found = pattern.match(line)
        if found:
            return found.group(1), found.group(2)
    return None


def _version_tuple(text: str) -> tuple:
    import re as _re
    found = _re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text or "")
    if not found:
        return ()
    return tuple(int(g) for g in found.groups(default="0"))


def check_credential_liveness() -> List[str]:
    """Credentials that expire silently. Findings only; empty means healthy.

    Deliberately structural rather than probing. keeper-env is the important case
    and the honest one: its config carries a device token and a private key but
    **no expiry**, so there is no local way to know a session is live. `doctor`
    reports "Session credentials: present" while fetches fail -- which is exactly
    what happened three times in one afternoon. So the check reports structure,
    names the limitation, and leans on the observed-failure record below rather
    than pretending a green light means working.
    """
    findings: List[str] = []

    if shutil.which("keeper-env"):
        code, out = _run(["keeper-env", "doctor"], timeout=25)
        if code != 0:
            findings.append("keeper-env doctor failed -- credential injection will not work; "
                            "run `keeper-env doctor` to see why")
        elif "Session credentials: present" not in out:
            findings.append("keeper-env has no session credentials -- run `keeper-env login` "
                            "before anything that needs a secret")
        elif "Device finalized: yes" not in out:
            findings.append("keeper-env device is not finalized -- `keeper-env login` from this "
                            "network will finish it")

    if shutil.which("gh"):
        code, out = _gh_auth_status()
        account = gh_active_account(out)
        # `None` is "cannot tell". Silence is right when gh simply answered something
        # unexpected -- reporting an unknown as "not authenticated" is the false alarm
        # this check used to make on every multi-account machine. But it is wrong when
        # gh *could not run the command at all*, because then both this check and the
        # identity one below go quiet on a machine that has a real problem.
        #
        # `--json` shipped in gh 2.81.0 (cli/cli#11544). An older gh answers
        # `unknown flag: --json` on a non-zero exit, which parses to None. Nothing
        # pins a gh floor -- `check_tool_versions` pins `databricks` only, and
        # `skills/requirements.txt` does not mention gh -- so the version is not
        # knowable from config and has to be inferred from the failure.
        if account is None and code != 0:
            findings.append(
                "cannot read `gh auth status --json hosts` (exit "
                f"{code}) -- `--json` needs gh >= 2.81.0; on an older gh both the "
                "credential and identity checks here go silent. `gh --version` to "
                "confirm, then upgrade")
        elif account is not None:
            token_source = account.get("tokenSource") if account else None
            # Read unconditionally, and attach to whichever branch fires. It used to
            # hang off the success branch, so an *expired* GH_TOKEN -- the realistic
            # form of this bug -- reported as "not usable" without ever saying the
            # credential came from the environment. That one fact is what explains
            # why `gh auth login` appears to work and changes nothing.
            from_env = token_source in GH_ENV_TOKEN_SOURCES
            env_note = (
                f" (credential comes from ${token_source}, not the keyring, so "
                f"`gh auth login` will not change it -- unset it first)"
                if from_env else "")
            if not account:
                findings.append(
                    f"no gh credential for {GH_HOST} -- `gh auth login`; a missing "
                    "token surfaces as skills that appear broken rather than as an "
                    "auth error")
            elif account.get("state") != "success":
                # gh interpolates HTTP response bodies here; real ones run to a couple
                # of hundred characters and this output goes into a chat transcript.
                reason = str(account.get("error") or "gh reports it as failing")
                if len(reason) > 160:
                    reason = reason[:157] + "..."
                findings.append(
                    f"gh's active account ({account.get('login') or 'unknown'}) is not usable: "
                    f"{reason} -- `gh auth login`{env_note}")
            elif from_env:
                findings.append(
                    f"gh is authenticated from ${account['tokenSource']} rather than a stored "
                    "login, so it expires with no warning and `gh auth status` will keep "
                    "saying yes")

    return findings


_GH_AUTH_CACHE: Dict[str, Any] = {}

# The env vars gh reports as a token source. Matched exactly rather than by
# substring: the old check tested `"GH_TOKEN" in out`, which never matched the
# `GITHUB_TOKEN` gh actually prints -- so the warning about tokens that expire
# silently had never once fired on a machine authenticated that way.
#
# The two enterprise variants cannot bite while `GH_HOST` is github.com, but `host`
# is a parameter now, so an enterprise caller would otherwise get the state finding
# with no mention that the credential came from the environment -- the same gap this
# tuple exists to close for github.com.
GH_ENV_TOKEN_SOURCES = (
    "GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN",
)


def _gh_auth_status() -> tuple:
    """`gh auth status --json hosts`, run at most once per process.

    `--json` rather than the human output, for two reasons that are both bugs the
    text version caused. It is documented to "always exit with zero regardless of
    any authentication issues", where the plain command exits 1 if *any* configured
    account fails -- including a stale keyring entry sitting beside a perfectly
    healthy active one. And it returns `state`, `active`, `login` and `tokenSource`
    as fields, so nothing here has to regex another product's prose.

    Two checks need it and it is a network call, so it is memoised per process.
    """
    if "result" not in _GH_AUTH_CACHE:
        _GH_AUTH_CACHE["result"] = _run(
            ["gh", "auth", "status", "--json", "hosts"], timeout=20)
    return _GH_AUTH_CACHE["result"]


# The host these checks are actually about. `gh` reports `active` PER HOST, so a
# machine with both github.com and an enterprise host configured has two active
# accounts and no global "the" active one. Every caller here cares about github.com,
# because that is where cg-open-itg lives -- so the host is part of the contract
# rather than whichever key JSON iteration happened to yield first.
GH_HOST = "github.com"


def gh_active_account(payload: str, host: str = GH_HOST) -> Optional[Dict[str, Any]]:
    """The active account for *host* out of `gh auth status --json hosts`.

    Three outcomes, and the distinction between the last two is the point:

    - a dict -- the active account, whose `state` says whether it works
    - ``{}``  -- gh answered and holds no active account *for this host*, including
      the case where the host is not configured at all. A real finding
    - ``None``-- the payload could not be read at all: a gh too old for `--json`,
      or a crash. An *unknown*, which callers report as nothing

    Collapsing `None` into `{}` would reintroduce the false "not authenticated"
    under a new name, so they stay separate.
    """
    import json as _json

    text = payload or ""
    start = text.find("{")
    if start < 0:
        return None
    try:
        # raw_decode, not loads: `_run` concatenates stderr onto stdout, and gh
        # writes "You are not logged into any GitHub hosts" there *while still
        # exiting 0 and printing valid JSON*. Measured, not assumed.
        data, _ = _json.JSONDecoder().raw_decode(text[start:])
    except ValueError:
        return None
    hosts = data.get("hosts") if isinstance(data, dict) else None
    if not isinstance(hosts, dict):
        return None
    if host not in hosts:
        # gh answered, and this host is not configured at all. A real finding rather
        # than an unknown: it is the same situation as having no active account, and
        # it is distinctly NOT "borrow the enterprise host's login instead", which
        # would attribute one identity's health to another.
        return {}
    for account in hosts.get(host) or []:
        if isinstance(account, dict) and account.get("active"):
            return account
    return {}


def check_tool_versions() -> List[str]:
    """Installed tool versions against the ranges this repo documents."""
    findings: List[str] = []
    if not shutil.which("databricks"):
        return findings

    declared = read_tool_range("databricks")
    if not declared:
        findings.append("skills/requirements.txt no longer declares a databricks-cli "
                        "range, so the installed CLI cannot be checked against "
                        "anything -- restore the commented range or drop this check")
        return findings

    floor_spec, ceiling_spec = declared
    code, out = _run(["databricks", "--version"], timeout=15)
    got = _version_tuple(out) if code == 0 else ()

    # A probe that fails is not a pass. Returning no finding here meant a CLI that
    # exits nonzero, or prints something unparseable, was reported as healthy --
    # the same false-green this whole pass exists to remove.
    if not got:
        why = (f"exited {code}" if code != 0 else "printed no recognisable version")
        findings.append(f"`databricks --version` {why}, so its version cannot be "
                        f"checked against the documented {floor_spec},{ceiling_spec}"
                        + (f" (output: {out.strip()[:120]!r})" if out.strip() else ""))
        return findings

    floor = _version_tuple(floor_spec)
    ceiling = _version_tuple(ceiling_spec)
    if got < floor:
        findings.append(f"{out.strip()} is below the documented "
                        f"{floor_spec} -- bundle and job skills may fail")
    elif got >= ceiling:
        findings.append(f"{out.strip()} is at or above the documented "
                        f"ceiling {ceiling_spec}. Either the CLI moved on and "
                        "skills/requirements.txt is stale, or this install is untested here "
                        "-- worth resolving rather than ignoring")
    return findings


def check_identity_coherence() -> List[str]:
    """Whether git, gh and the telemetry identity agree on who you are.

    Silence here is the anonymous-reporting failure in a different costume: if
    nothing can establish an identity, telemetry either attributes the work to
    nobody or to whoever the fallback happens to name.
    """
    findings: List[str] = []
    code, email = _run(["git", "config", "--get", "user.email"], timeout=10)
    git_email = email.strip() if code == 0 else ""
    if not git_email:
        findings.append("git user.email is unset. It is the second source the telemetry "
                        "identity falls back to, so reporting quietly depends on the gh login "
                        "instead -- `git config --global user.email <you>@capgroup.com`")

    # Reuses the `gh auth status` the credential check already ran, instead of a
    # second `gh api user` round trip. Same answer, no additional network cost, and
    # it cannot report a transient identity mismatch that the other check has
    # already reported as an auth failure.
    gh_login = ""
    if shutil.which("gh"):
        # The active account only. Taking the first login mentioned could name a
        # *failing* account and then report a mismatch against it.
        account = gh_active_account(_gh_auth_status()[1]) or {}
        if account.get("state") == "success":
            gh_login = str(account.get("login") or "")

    if git_email and gh_login:
        git_initials = git_email.split("@", 1)[0].lower()
        gh_initials = gh_login.replace("_capgroup", "").lower()
        if git_initials.isalpha() and git_initials != gh_initials:
            findings.append(f"git user.email says {git_initials!r} but the gh login says "
                            f"{gh_initials!r}. Telemetry will attribute your work to whichever "
                            "one resolves first, which may not be you")
    return findings


def check_telemetry() -> List[str]:
    """Whether usage reporting is actually on, for whichever harness this is.

    The reason this belongs in the background pass rather than only in `check`:
    telemetry is the one setting whose failure is *completely* invisible. There is
    no UI confirmation anywhere by design, so a machine that has never reported
    looks identical to one reporting correctly. Everything else here degrades
    loudly and eventually; this degrades silently and forever.

    Reuses the probes questions 5 and 5b already own -- no second implementation
    to drift -- and does no *remote* endpoint probing, so nothing here leaves the
    machine. See `background_findings` for what does.

    It does make the same one-second localhost connect `check` makes, and that is a
    correction rather than a cost: passing `check_local_collector=False` meant
    `no_destination` could never be set, so a session with **no endpoint at all** --
    the worst telemetry state there is, and the one this pass exists to surface --
    was reported as `ON_BUT_MISCONFIGURED` instead of `ON_BUT_NO_DESTINATION`. One
    severity too low, with remediation text that spoke of "a destination" that did
    not exist. A loopback connect is not network egress and `check` already pays it.
    """
    findings: List[str] = []

    cc = probe_claude_code_otel()
    if cc["verdict"] not in (CC_OTEL_NOT_CLAUDE_CODE, CC_OTEL_ON):
        # The named problems AND the fix. An earlier revision printed the problems
        # *instead of* the remediation, which fixed one dead end and created another:
        # the pass said precisely what was wrong and never how to repair it. This is
        # the only place the verdict is rendered, so both halves belong here.
        problems = "; ".join(cc.get("problems") or [])
        fix = CC_OTEL_REMEDIATION[cc["verdict"]]
        detail = f"{problems}. {fix}" if problems else fix
        findings.append(f"Claude Code usage reporting is {cc['verdict']} -- {detail}")

    # Only worth raising where VS Code exists; on a Coder workspace with no VS Code
    # this is not a gap, and question 5 already says so rather than sending anyone
    # to a command that cannot work.
    o = probe_otel()
    # `settings_path` alone was too strict. A first-run VS Code has no User
    # settings.json at all, which is precisely the case that most needs telling --
    # and the gate suppressed it, so the check was silent exactly when reporting was
    # definitely off. The harness check keeps the original intent: on a Coder
    # workspace with no VS Code this is not a gap, and question 5 already says so.
    vscode_present = o["settings_path"] or detect_harness() == "vscode"
    if vscode_present and o["verdict"] not in (OTEL_OK, OTEL_DISABLED):
        # The named problems AND the fix, exactly as the Claude Code branch above
        # does it. This pass prints no per-key table, so a remediation that said
        # "see the per-key detail above" pointed at nothing and left the reader
        # knowing something was wrong but not what.
        problems = "; ".join(o.get("problems") or [])
        fix = OTEL_REMEDIATION[o["verdict"]]
        detail = f"{problems}. {fix}" if problems else fix
        findings.append(f"Copilot Chat usage reporting is {o['verdict']} -- {detail}")
        # A second `if o["verdict"] in (OTEL_OK, OTEL_PENDING_RESTART) and not
        # o.get("identity")` findings.append lived here and was unreachable
        # (AICAT-343): `OTEL_OK` is excluded by the enclosing condition, and a missing
        # `user.id` makes `probe_otel` append a problem, which forces MISCONFIGURED
        # rather than PENDING_RESTART. Removed rather than repaired, because the join
        # above now carries the same sentence from the probe that already computed it
        # -- `check_telemetry` relaying what `probe_otel` found beats it re-deriving
        # the same conclusion from two fields.

    return findings


def background_findings() -> Dict[str, List[str]]:
    """All four families of finding.

    **This pass touches the network**, and the contract is worth stating rather than
    implying: `check_credential_liveness` runs `keeper-env doctor` and
    `gh auth status`, and credential *liveness* cannot be established any other way.
    Both are bounded by `_run` timeouts, and `gh auth status` is memoised so the
    identity check reuses it rather than making a second call.

    What it deliberately does not do is probe a collector endpoint. That stays
    behind `otel --probe-endpoint`, where the user asks for it.
    """
    # Telemetry first, deliberately. It is the only one of the four whose failure
    # is invisible by design -- there is no UI confirmation of Copilot Chat
    # reporting anywhere -- so it is the one a user will never discover unaided.
    return {
        "telemetry": check_telemetry(),
        "credentials": check_credential_liveness(),
        "versions": check_tool_versions(),
        "identity": check_identity_coherence(),
    }


def _background_due(marker: Optional[Path] = None) -> bool:
    """Whether enough time has passed to be worth checking again.

    The marker is resolved at call time, not bound as a default: a default
    argument is evaluated at import, which froze the path and made it impossible
    to point somewhere else.
    """
    marker = marker or BACKGROUND_MARKER
    try:
        age = time.time() - marker.stat().st_mtime
    except OSError:
        return True
    return age > BACKGROUND_TTL_SECONDS


def _record_background_run(findings: Dict[str, List[str]],
                           marker: Optional[Path] = None) -> None:
    marker = marker or BACKGROUND_MARKER
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({
            "checked_at": int(time.time()),
            "findings": findings,
        }, indent=2), encoding="utf-8")
    except OSError:
        pass                                    # a cache we cannot write is not an error


def cmd_background(force: bool = False, quiet_when_clean: bool = True) -> int:
    """The once-a-session pass. Always returns 0 -- it never blocks anything."""
    if not force and not _background_due():
        return 0

    findings = background_findings()
    total = sum(len(v or []) for v in findings.values())
    _record_background_run(findings)

    if total == 0:
        if not quiet_when_clean:
            print("Background checks: nothing to report.")
        return 0

    print("Before we start -- a few things worth knowing (none of these block you):")
    for group, label in (("telemetry", "Usage reporting"),
                         ("credentials", "Credentials"),
                         ("versions", "Tool versions"),
                         ("identity", "Identity")):
        # .get, not [] -- a family that failed to produce a list must not
        # crash a check whose entire contract is that it never blocks.
        for item in findings.get(group) or []:
            print(f"  - {label}: {item}")
    print("")
    print("Run `/dplc-preflight check` for the full readiness report.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="AI Catalyst environment pre-flight.")
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("check", help="Full readiness report.")
    c.add_argument("--no-cache", action="store_true", help="Skip writing .catalyst-env.yml")
    sub.add_parser("workspaces", help="List configured Databricks profiles.")
    b = sub.add_parser("background", help="Quiet once-a-session advisory checks.")
    b.add_argument("--force", action="store_true", help="Run even if already run today.")
    b.add_argument("--verbose", action="store_true", help="Say so even when clean.")
    o = sub.add_parser("otel", help="Report Copilot Chat usage-reporting config.")
    o.add_argument("--probe-endpoint", action="store_true",
                   help="Also test whether the collector endpoint is reachable.")
    args = parser.parse_args(argv)

    if args.command == "check":
        return cmd_check(write=not args.no_cache)
    if args.command == "workspaces":
        return cmd_workspaces()
    if args.command == "background":
        return cmd_background(force=args.force, quiet_when_clean=not args.verbose)
    if args.command == "otel":
        return cmd_otel(probe_endpoint=args.probe_endpoint)
    return 1


if __name__ == "__main__":
    sys.exit(main())
