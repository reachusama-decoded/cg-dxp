#!/usr/bin/env python3
"""Emit which Catalyst skills were invoked, as OTLP metrics.

WHY THIS EXISTS

Claude Code already reports skill usage — and redacts it. `skill.name` on the
`cost.usage` and `token.usage` metrics is set to the literal string
`"third-party"` for any skill from a non-official marketplace, which is what
Catalyst is (`cg-open-itg/catalyst`). Measured, twice, across both a directory
marketplace and a GitHub one: two distinct skills, one value. See AICAT-339.

So the platform tells us *that* a third-party skill ran, what it cost, on which
model, for which user — everything except which skill. That last field is the
whole point of the measurement.

WHERE THE REAL NAMES COME FROM

The session transcript. Claude Code records every skill invocation as a
first-class tool call:

    {"type": "tool_use", "name": "Skill",
     "input": {"skill": "ai-catalyst:dplc-preflight", "args": "..."}}

`input.skill` is a named field holding the answer, not something inferred from a
path — which is the distinction that matters, because the previous attempt at
this (a VS Code hook regexing `read_file` paths for `SKILL.md`) died when Copilot
stopped reading those files. A field cannot stop containing its own value
without the tool's input contract changing.

WHAT IS DELIBERATELY NOT EMITTED

`input.args` is user-typed text. It is never read into a payload, never logged,
and never written to the state file. Only the skill name, its plugin, the session
id and the timestamp leave this script -- emitted as `catalyst.skill` and
`catalyst.plugin`, namespaced so they are never confused with Claude Code's own
redacted `skill.name` / `plugin.name`. That is what keeps this on the METRICS signal, which
is structurally incapable of carrying content — pointing anything at the logs
signal is the one change that would route prompt text to the Catalyst collector,
and the managed policy sets OTEL_LOG_USER_PROMPTS=1 where we cannot override it.

THE HONEST CAVEAT

The transcript is an internal file format with no stability contract, unlike the
documented hook API. This is cheaper to build and it backfills history that a
hook never could — but if the format changes, this stops working. It is a
nice-to-have layered on a working pipeline, not the pipeline itself.

IDEMPOTENCY

History is re-read on every run, so without state every run would re-emit every
past invocation and inflate the counts monotonically. A marker file records the
`(session, timestamp, skill)` keys already emitted. Deleting it re-emits
everything, which is the intended way to backfill into a fresh collector.

USAGE

    python3 scripts/emit_skill_usage.py                       # dry run: what would be sent
    python3 scripts/emit_skill_usage.py --endpoint dev --apply
    python3 scripts/emit_skill_usage.py --since 2026-09-16    # bound the window
    python3 scripts/emit_skill_usage.py --all --apply         # ignore state, re-emit
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import struct
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_JSON = REPO_ROOT / "plugin.json"
TRANSCRIPT_ROOT = Path.home() / ".claude" / "projects"
STATE_FILE = Path.home() / ".cache" / "catalyst" / "emitted-skill-usage.json"

# Named collectors. The choice is not cosmetic: production is not routable from an
# oz-dev Coder workspace (TCP 443 opens, TLS resets), so pointing there silently
# drops every batch while reporting success.
COLLECTORS = {
    "dev": "https://catalyst-otel.datalakefoundation.aws-dev.capgroup.com",
    "prd": "https://catalyst-otel.datalake.aws.capgroup.com",
}
# Required on a per-signal endpoint: it is used AS-IS, unlike the generic
# OTEL_EXPORTER_OTLP_ENDPOINT to which the exporter appends the signal path. A
# host-only value POSTs to `/`, which the collector answers 404 -- measured.
METRICS_PATH = "/v1/metrics"

METRIC_NAME = "catalyst.skill.invocation"


# --- what counts as a Catalyst skill -----------------------------------------

def catalyst_skill_names(plugin_json: Optional[Path] = None) -> Set[str]:
    """The skill names this repo ships, from the manifest rather than a hardcoded list.

    `plugin.json` is the source of truth for what Catalyst is, so a skill added or
    renamed there is picked up without touching this script.
    """
    path = plugin_json or PLUGIN_JSON
    try:
        entries = json.loads(path.read_text(encoding="utf-8")).get("skills") or []
    except (OSError, json.JSONDecodeError):
        return set()
    return {e.rsplit("/", 1)[-1] for e in entries if isinstance(e, str)}


MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
# Emitted as `catalyst.plugin` for a transcript entry with no prefix. Those predate the
# plugin being installed, when skills resolved from the working tree, so provenance
# is genuinely unknown rather than merely unrecorded -- and a query that needs to
# exclude ambiguous rows has to be able to see which ones they are.
UNQUALIFIED = "unqualified"


def catalyst_plugin_names(marketplace_json: Optional[Path] = None) -> Set[str]:
    """The plugin names this repo publishes, from its own marketplace manifest.

    Read rather than hardcoded so a rename cannot silently orphan every row.
    """
    path = marketplace_json or MARKETPLACE_JSON
    try:
        entries = json.loads(path.read_text(encoding="utf-8")).get("plugins") or []
    except (OSError, json.JSONDecodeError):
        return set()
    return {e["name"] for e in entries if isinstance(e, dict) and e.get("name")}


def split_skill(raw: str) -> Tuple[Optional[str], str]:
    """`ai-catalyst:dplc-preflight` -> `("ai-catalyst", "dplc-preflight")`.

    The prefix is the provenance and must not be discarded. An earlier version
    canonicalised it away before filtering, which meant a foreign plugin shipping
    `someone-else:dplc-preflight` matched the Catalyst skill list on the bare name
    and was emitted as ours -- attributing another team's usage to this product,
    silently and unfalsifiably.

    A bare name returns `None`, not a guess.
    """
    if not raw:
        return None, ""
    text = raw.strip()
    if ":" in text:
        prefix, name = text.split(":", 1)
        return prefix.strip() or None, name.strip()
    return None, text


def canonical_skill(raw: str) -> str:
    """The bare skill name, for counting and joining.

    Historical transcripts carry both forms -- bare before the plugin was installed
    and prefixed after -- so counting the two separately would split one skill's
    history at an arbitrary date. Provenance is carried alongside in `catalyst.plugin`
    rather than folded into this.
    """
    return split_skill(raw)[1]


def is_catalyst_skill(raw: str, known_skills: Set[str],
                      known_plugins: Set[str]) -> bool:
    """Whether this invocation belongs to Catalyst.

    The prefix decides when there is one: a prefixed skill from another plugin is
    not ours no matter what it is called. Only an unprefixed name falls back to
    matching the skill list, and those rows are marked `unqualified` so a consumer
    can exclude them if a name collision ever makes them ambiguous.
    """
    prefix, name = split_skill(raw)
    if prefix is not None:
        return prefix in known_plugins and name in known_skills
    return name in known_skills


# --- reading the transcripts --------------------------------------------------

def iter_invocations(root: Optional[Path] = None,
                     since: Optional[float] = None) -> Iterable[Tuple[str, str, str]]:
    """Yield `(session_id, iso_timestamp, raw_skill)` for every Skill call.

    `input.args` is deliberately not read. It is user-typed text and has no place
    in a metrics payload.
    """
    root = root or TRANSCRIPT_ROOT
    if not root.is_dir():
        return
    for path in sorted(root.rglob("*.jsonl")):
        try:
            if since is not None and path.stat().st_mtime < since:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            # Cheap prefilter: most lines are not tool calls at all, and parsing
            # 46MB of JSON per run for a handful of hits is wasteful.
            if '"Skill"' not in line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = ((record.get("message") or {}).get("content"))
            if not isinstance(content, list):
                continue
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "tool_use" or item.get("name") != "Skill":
                    continue
                raw = ((item.get("input") or {}).get("skill")) or ""
                if not canonical_skill(raw):
                    continue
                session = record.get("sessionId") or path.stem
                stamp = record.get("timestamp") or ""
                # The RAW name is yielded, prefix intact. Callers decide provenance;
                # this function does not get to throw that away on their behalf.
                yield str(session), str(stamp), raw


def key_for(session: str, stamp: str, skill: str) -> str:
    """The identity of one invocation, for de-duplication across runs."""
    return f"{session}|{stamp}|{skill}"


# --- state --------------------------------------------------------------------

def load_state(path: Optional[Path] = None) -> Set[str]:
    path = path or STATE_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    emitted = data.get("emitted")
    return set(emitted) if isinstance(emitted, list) else set()


def save_state(keys: Set[str], path: Optional[Path] = None) -> None:
    """Write atomically: this file is the only thing preventing double counting."""
    path = path or STATE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps({"emitted": sorted(keys)}, indent=0), encoding="utf-8")
    os.replace(tmp, path)


# --- OTLP encoding ------------------------------------------------------------
#
# Hand-rolled because no opentelemetry package is installed and public PyPI is
# blocked on this network. The encoder self-checks before sending -- an earlier
# version double-wrapped every KeyValue and the collector stored it regardless,
# because the receiver never parses payloads. Acceptance proves the transport,
# not the encoding.

def _varint(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def _ld(field: int, blob: bytes) -> bytes:
    return _varint((field << 3) | 2) + _varint(len(blob)) + blob


def _string(field: int, value: str) -> bytes:
    return _ld(field, value.encode("utf-8"))


def _fixed64(field: int, value: int) -> bytes:
    return _varint((field << 3) | 1) + struct.pack("<Q", value)


def _varint_field(field: int, value: int) -> bytes:
    return _varint((field << 3) | 0) + _varint(value)


def _kv_body(key: str, value: str) -> bytes:
    """A KeyValue *without* its own field tag, so callers choose the field number.

    Resource.attributes is field 1 and NumberDataPoint.attributes is field 7; a
    helper that emitted its own tag could only ever serve one of them, which is
    how the first version of this encoder came to be malformed.
    """
    return _string(1, key) + _ld(2, _string(1, value))


def build_payload(invocations: List[Tuple[str, str, str]],
                  resource: Dict[str, str],
                  now_ns: Optional[int] = None) -> bytes:
    """One `catalyst.skill.invocation` sum, one datapoint per invocation."""
    now_ns = now_ns if now_ns is not None else time.time_ns()
    points = []
    for session, stamp, raw in invocations:
        prefix, skill = split_skill(raw)
        attrs = b"".join(_ld(7, _kv_body(k, v)) for k, v in (
            # NAMESPACED, deliberately. Claude Code emits `skill.name` and
            # `plugin.name` on its own metrics with the value redacted to
            # "third-party". Reusing those names would imply the two are
            # interchangeable, and they are not: the platform's is a product
            # guarantee, ours is derived by this script from an undocumented file
            # format that can break without notice. Distinct names also keep the
            # two comparable -- if the redaction is ever lifted, the values could
            # disagree, and identical names would hide that rather than surface it.
            ("catalyst.skill", skill),
            # Provenance. Two plugins may ship a skill with the same name, and
            # `service.name` cannot distinguish them -- that identifies this
            # emitter, not the skill's origin. Rows from before the plugin was
            # installed carry no prefix and are marked UNQUALIFIED rather than
            # assumed to be ours.
            ("catalyst.plugin", prefix or UNQUALIFIED),
            # NOT namespaced, and this is the exception that matters: `session.id`
            # is how these rows join to Claude Code's own cost and token metrics
            # ("this skill ran in this session, which cost this much"). Renaming it
            # would break the only thing tying the two datasets together.
            ("session.id", session),
            # The original event time, kept as an attribute rather than as the
            # datapoint timestamp: a collector may reject points far in the past,
            # and backfilling ten days of history would trip exactly that.
            ("invoked.at", stamp),
        ))
        points.append(_ld(1,
                          _fixed64(2, now_ns) + _fixed64(3, now_ns)
                          + _varint((6 << 3) | 1) + struct.pack("<q", 1)
                          + attrs))
    # Sum: data_points=1, aggregation_temporality=2 (DELTA=1), is_monotonic=3
    sum_msg = b"".join(points) + _varint_field(2, 1) + _varint_field(3, 1)
    metric = _string(1, METRIC_NAME) + _string(3, "1") + _ld(7, sum_msg)
    scope = _ld(1, _string(1, "catalyst.emit_skill_usage")) + _ld(2, metric)
    res = _ld(1, b"".join(_ld(1, _kv_body(k, v)) for k, v in resource.items()))
    return _ld(1, res + _ld(2, scope))


def decode_resource_attributes(payload: bytes) -> Dict[str, str]:
    """Read back the resource block, so the encoder can check its own output."""
    def rv(b: bytes, i: int) -> Tuple[int, int]:
        n = shift = 0
        while True:
            x = b[i]
            i += 1
            n |= (x & 0x7F) << shift
            if not x & 0x80:
                return n, i
            shift += 7

    def walk(b: bytes):
        i = 0
        while i < len(b):
            try:
                key, i = rv(b, i)
            except IndexError:
                return
            field, wire = key >> 3, key & 7
            if wire == 2:
                ln, i = rv(b, i)
                yield field, b[i:i + ln]
                i += ln
            elif wire == 0:
                _, i = rv(b, i)
            elif wire == 1:
                i += 8
            elif wire == 5:
                i += 4
            else:
                return

    out: Dict[str, str] = {}
    for f1, rm in walk(payload):
        if f1 != 1:
            continue
        for f2, resource in walk(rm):
            if f2 != 1:
                continue
            for f3, kv in walk(resource):
                if f3 != 1:
                    continue
                key = value = None
                for f4, blob in walk(kv):
                    if f4 == 1:
                        key = blob.decode("utf-8", "replace")
                    elif f4 == 2:
                        for f5, inner in walk(blob):
                            if f5 == 1:
                                value = inner.decode("utf-8", "replace")
                if key is not None:
                    out[key] = value
    return out


# --- sending ------------------------------------------------------------------

def normalise_endpoint(value: str) -> str:
    """A collector name or URL -> a full per-signal metrics endpoint."""
    name = (value or "").strip()
    url = COLLECTORS.get(name.lower(), name)
    if url is name and not name.lower().startswith(("http://", "https://")):
        raise ValueError(f"{value!r} is neither a known collector "
                         f"({', '.join(sorted(COLLECTORS))}) nor an http(s) URL")
    url = url.rstrip("/")
    return url if url.endswith(METRICS_PATH) else url + METRICS_PATH


def post(url: str, payload: bytes, timeout: float = 30.0) -> Tuple[bool, str]:
    try:
        import truststore
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        ctx = ssl.create_default_context()
    request = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/x-protobuf"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ctx) as response:
            return True, f"{response.status} {response.reason}"
    except urllib.error.HTTPError as exc:
        return False, f"{exc.code} {exc.reason}"
    except Exception as exc:                                  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def resource_attributes() -> Dict[str, str]:
    """Mirrors the fragment so these rows join with Claude Code's own metrics."""
    coder = bool(os.environ.get("CODER_WORKSPACE_NAME")
                 or os.environ.get("CODER_AGENT_TOKEN"))
    return {
        "service.name": "catalyst-skill-usage",
        "workspace.kind": "coder" if coder else "local",
        "department": "edo",
        "telemetry.producer": "claude-code",
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit Catalyst skill invocations from session transcripts as OTLP metrics.")
    parser.add_argument("--endpoint", default="dev",
                        help="'dev', 'prd', or a full URL. /v1/metrics is appended if missing.")
    parser.add_argument("--apply", action="store_true",
                        help="Send. Without this, nothing leaves the machine.")
    parser.add_argument("--all", action="store_true",
                        help="Ignore recorded state and re-emit every invocation found.")
    parser.add_argument("--since", default=None,
                        help="Only read transcripts modified on/after YYYY-MM-DD.")
    parser.add_argument("--transcripts", default=None, help="Override the transcript root.")
    args = parser.parse_args(argv)

    try:
        url = normalise_endpoint(args.endpoint)
    except ValueError as exc:
        print(f"Bad --endpoint: {exc}")
        return 2

    since = None
    if args.since:
        try:
            since = time.mktime(time.strptime(args.since, "%Y-%m-%d"))
        except ValueError:
            print(f"Bad --since: {args.since!r}; expected YYYY-MM-DD")
            return 2

    known = catalyst_skill_names()
    if not known:
        print("Could not read the skill list from plugin.json; refusing to guess "
              "which skills are Catalyst's.")
        return 2
    plugins = catalyst_plugin_names()
    if not plugins:
        print("Could not read the plugin name from .claude-plugin/marketplace.json; "
              "refusing to guess provenance. Without it a foreign plugin's "
              "same-named skill would be attributed to Catalyst.")
        return 2

    root = Path(args.transcripts) if args.transcripts else None
    found = list(iter_invocations(root, since=since))
    catalyst = [inv for inv in found
                if is_catalyst_skill(inv[2], known, plugins)]
    state = set() if args.all else load_state()
    fresh = [inv for inv in catalyst if key_for(*inv) not in state]

    print("Catalyst skill usage from session transcripts")
    print("")
    print(f"  Endpoint:        {url}")
    print(f"  Skill calls seen: {len(found)}  ({len(catalyst)} are Catalyst skills)")
    print(f"  Already emitted:  {len(catalyst) - len(fresh)}")
    print(f"  To send:          {len(fresh)}")

    if not fresh:
        print("")
        print("Nothing new to send.")
        return 0

    counts: Dict[Tuple[str, str], int] = {}
    for _, _, raw in fresh:
        prefix, skill = split_skill(raw)
        key = (skill, prefix or UNQUALIFIED)
        counts[key] = counts.get(key, 0) + 1
    print("")
    print("  Skills in this batch:")
    for (skill, prefix), n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"    {n:4}  {skill}   [catalyst.plugin={prefix}]")
    if any(prefix == UNQUALIFIED for _, prefix in counts):
        print("")
        print(f"  Some rows are {UNQUALIFIED}: they predate the plugin being installed, so")
        print("  the transcript recorded no prefix. They matched on skill name alone, which")
        print("  is weaker evidence -- the attribute is emitted so a query can exclude them.")
    print("")
    print("  Emitted per invocation: catalyst.skill, catalyst.plugin, session.id,")
    print("  invoked.at. Namespaced so they are never confused with Claude Code's own")
    print("  redacted skill.name / plugin.name.")
    print("  Nothing else -- the transcript's `args` field is user-typed text and is")
    print("  never read.")

    payload = build_payload(fresh, resource_attributes())
    decoded = decode_resource_attributes(payload)
    if decoded != resource_attributes():
        print("")
        print(f"REFUSING to send: the encoder did not round-trip. Decoded {decoded!r}.")
        return 4
    print(f"  Payload:          {len(payload)} bytes, encoder self-check passed")

    if not args.apply:
        print("")
        print("Dry run. Re-run with --apply to send.")
        return 0

    ok, detail = post(url, payload)
    print("")
    if not ok:
        print(f"Send failed ({detail}). State not updated, so nothing is lost -- re-run.")
        return 4
    print(f"Sent: {detail}")
    save_state(state | {key_for(*inv) for inv in fresh})
    print(f"Recorded {len(fresh)} invocation(s) in {STATE_FILE} so they are not re-sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
