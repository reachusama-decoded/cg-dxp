"""Guard: skill names are recovered accurately, counted once, and no user text leaks.

The three failure modes that matter, in order:

1. **Emitting `args`.** The transcript holds user-typed text next to the skill
   name. Sending it would put prompt content on the one signal chosen precisely
   because it cannot carry content.
2. **Double counting.** History is re-read on every run, so without state each run
   re-emits everything and the counts climb monotonically for no reason.
3. **Wrong names.** Bare and prefixed forms of the same skill appearing as two
   skills would split one history at an arbitrary date.

Everything here is offline: no network, no real transcripts.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "emit_skill_usage.py"


@pytest.fixture(scope="module")
def emit():
    spec = importlib.util.spec_from_file_location("emit_skill_usage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transcript(tmp_path: Path, records: list) -> Path:
    """A minimal transcript tree in the shape Claude Code writes."""
    root = tmp_path / "projects" / "-some-repo"
    root.mkdir(parents=True)
    path = root / "session.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return tmp_path / "projects"


def skill_call(skill: str, args: str = "some user text", session: str = "s1",
               stamp: str = "2026-09-17T21:00:00Z") -> dict:
    return {
        "sessionId": session,
        "timestamp": stamp,
        "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": skill, "args": args}}
        ]},
    }


# --- the skill list comes from the manifest ----------------------------------

def test_the_skill_list_is_read_from_plugin_json(emit):
    names = emit.catalyst_skill_names()
    assert "dplc-preflight" in names and "setup-workspace" in names
    assert len(names) > 90, f"expected ~106 skills, got {len(names)}"


def test_names_are_bare_not_paths(emit):
    assert not any("/" in n for n in emit.catalyst_skill_names())


def test_a_missing_manifest_yields_nothing_rather_than_a_guess(emit, tmp_path):
    """Refusing beats inventing a skill list: a wrong list silently drops skills."""
    assert emit.catalyst_skill_names(tmp_path / "nope.json") == set()


def test_main_refuses_when_the_manifest_cannot_be_read(emit, monkeypatch, capsys):
    monkeypatch.setattr(emit, "catalyst_skill_names", lambda *a, **k: set())
    assert emit.main([]) == 2
    assert "refusing to guess" in capsys.readouterr().out.lower()


# --- name canonicalisation ---------------------------------------------------

def test_prefixed_and_bare_names_are_the_same_skill(emit):
    """Transcripts carry both: bare before the plugin was installed, prefixed after."""
    assert emit.canonical_skill("ai-catalyst:dplc-preflight") == "dplc-preflight"
    assert emit.canonical_skill("dplc-preflight") == "dplc-preflight"


class TestNamespacing:
    """Our attributes must not collide with Claude Code's own.

    The platform emits `skill.name` and `plugin.name` with the value redacted to
    "third-party". Reusing those names would imply the two are interchangeable --
    but the platform's is a product guarantee and ours is derived from an
    undocumented file format. Distinct names also keep them comparable if the
    redaction is ever lifted and the values disagree.
    """

    def test_our_attributes_are_namespaced(self, emit):
        payload = emit.build_payload([("s1", "t", "ai-catalyst:dplc-preflight")],
                                     emit.resource_attributes())
        assert b"catalyst.skill" in payload
        assert b"catalyst.plugin" in payload

    def test_the_platforms_attribute_names_are_not_reused(self, emit):
        """`skill.name` appearing here would collide with the redacted native field."""
        payload = emit.build_payload([("s1", "t", "ai-catalyst:dplc-preflight")],
                                     emit.resource_attributes())
        assert b"skill.name" not in payload
        assert b"plugin.name" not in payload

    def test_session_id_is_NOT_namespaced(self, emit):
        """The exception that matters: this is the join key onto Claude Code's own
        cost and token metrics. Renaming it breaks the only link between the two
        datasets."""
        payload = emit.build_payload([("s1", "t", "ai-catalyst:dplc-preflight")],
                                     emit.resource_attributes())
        assert b"session.id" in payload
        assert b"catalyst.session" not in payload


class TestProvenance:
    """The bug this class exists for.

    An earlier version canonicalised the plugin prefix away *before* filtering, so a
    foreign plugin shipping `someone-else:dplc-preflight` matched the Catalyst skill
    list on the bare name and was emitted as ours. `service.name` cannot save this --
    it identifies the emitting script, not the skill's origin, so every row carries
    it regardless of provenance.
    """

    def test_the_prefix_is_kept_separately(self, emit):
        assert emit.split_skill("ai-catalyst:dplc-preflight") == ("ai-catalyst", "dplc-preflight")

    def test_a_bare_name_has_no_prefix_rather_than_a_guessed_one(self, emit):
        assert emit.split_skill("dplc-preflight") == (None, "dplc-preflight")

    def test_our_own_prefixed_skill_is_ours(self, emit):
        sk, pl = emit.catalyst_skill_names(), emit.catalyst_plugin_names()
        assert emit.is_catalyst_skill("ai-catalyst:dplc-preflight", sk, pl)

    def test_a_foreign_plugin_with_our_skill_name_is_NOT_ours(self, emit):
        """The collision case. Same skill name, different plugin."""
        sk, pl = emit.catalyst_skill_names(), emit.catalyst_plugin_names()
        assert not emit.is_catalyst_skill("someone-else:dplc-preflight", sk, pl)
        assert not emit.is_catalyst_skill("evil-plugin:setup-workspace", sk, pl)

    def test_another_plugins_own_skills_are_not_ours(self, emit):
        sk, pl = emit.catalyst_skill_names(), emit.catalyst_plugin_names()
        assert not emit.is_catalyst_skill("ai-toolkit:pr-status", sk, pl)

    def test_a_bare_historical_name_still_counts(self, emit):
        """Pre-install transcripts have no prefix; excluding them would lose the
        backfill that is most of this script's value."""
        sk, pl = emit.catalyst_skill_names(), emit.catalyst_plugin_names()
        assert emit.is_catalyst_skill("dplc-preflight", sk, pl)

    def test_the_plugin_name_comes_from_the_manifest(self, emit):
        assert emit.catalyst_plugin_names() == {"ai-catalyst"}

    def test_a_missing_marketplace_manifest_yields_nothing(self, emit, tmp_path):
        assert emit.catalyst_plugin_names(tmp_path / "absent.json") == set()

    def test_main_refuses_without_a_plugin_name(self, emit, monkeypatch, capsys):
        """Refusing beats attributing another team's usage to this product."""
        monkeypatch.setattr(emit, "catalyst_plugin_names", lambda *a, **k: set())
        assert emit.main([]) == 2
        assert "refusing to guess provenance" in capsys.readouterr().out.lower()

    def test_the_payload_carries_plugin_name(self, emit):
        payload = emit.build_payload(
            [("s1", "t", "ai-catalyst:dplc-preflight")], emit.resource_attributes())
        assert b"catalyst.plugin" in payload and b"ai-catalyst" in payload

    def test_an_unprefixed_row_is_marked_unqualified_not_assumed_ours(self, emit):
        payload = emit.build_payload(
            [("s1", "t", "dplc-preflight")], emit.resource_attributes())
        assert emit.UNQUALIFIED.encode() in payload

    def test_a_foreign_skill_never_reaches_the_batch(self, emit, tmp_path, monkeypatch, capsys):
        root = transcript(tmp_path, [
            skill_call("someone-else:dplc-preflight", stamp="t1"),
            skill_call("ai-catalyst:dplc-preflight", stamp="t2"),
        ])
        monkeypatch.setattr(emit, "STATE_FILE", tmp_path / "state.json")
        emit.main(["--transcripts", str(root)])
        out = capsys.readouterr().out
        assert "(1 are Catalyst skills)" in out, out
        assert "someone-else" not in out

def test_an_empty_name_is_not_a_skill(emit):
    assert emit.canonical_skill("") == ""
    assert emit.canonical_skill(None) == ""


# --- reading transcripts -----------------------------------------------------

def test_skill_calls_are_found_with_the_prefix_intact(emit, tmp_path):
    """The reader must not discard provenance on the caller's behalf."""
    root = transcript(tmp_path, [skill_call("ai-catalyst:dplc-preflight")])
    found = list(emit.iter_invocations(root))
    assert found == [("s1", "2026-09-17T21:00:00Z", "ai-catalyst:dplc-preflight")]


def test_non_skill_tool_calls_are_ignored(emit, tmp_path):
    root = transcript(tmp_path, [
        {"sessionId": "s1", "timestamp": "t", "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}},
    ])
    assert list(emit.iter_invocations(root)) == []


def test_malformed_lines_do_not_stop_the_scan(emit, tmp_path):
    root = tmp_path / "projects" / "-r"
    root.mkdir(parents=True)
    (root / "s.jsonl").write_text(
        'not json at all "Skill"\n' + json.dumps(skill_call("dplc-preflight")) + "\n",
        encoding="utf-8")
    assert len(list(emit.iter_invocations(tmp_path / "projects"))) == 1


def test_a_missing_transcript_root_is_empty_not_an_error(emit, tmp_path):
    assert list(emit.iter_invocations(tmp_path / "nothing-here")) == []


def test_since_bounds_the_window(emit, tmp_path):
    import os, time
    root = transcript(tmp_path, [skill_call("dplc-preflight")])
    old = root / "-some-repo" / "session.jsonl"
    os.utime(old, (time.time() - 86400 * 30, time.time() - 86400 * 30))
    assert list(emit.iter_invocations(root, since=time.time() - 3600)) == []
    assert len(list(emit.iter_invocations(root))) == 1


# --- the privacy guarantee ---------------------------------------------------

def test_user_text_never_reaches_the_payload(emit, tmp_path):
    """The one that matters. `args` sits next to the skill name in the transcript."""
    secret = "MY-PRIVATE-PROMPT-TEXT-abc123"
    root = transcript(tmp_path, [skill_call("dplc-preflight", args=secret)])
    found = list(emit.iter_invocations(root))
    assert secret not in repr(found)
    payload = emit.build_payload(found, emit.resource_attributes())
    assert secret.encode() not in payload

def test_user_text_never_reaches_the_state_file(emit, tmp_path):
    secret = "MY-PRIVATE-PROMPT-TEXT-abc123"
    root = transcript(tmp_path, [skill_call("dplc-preflight", args=secret)])
    state = tmp_path / "state.json"
    emit.save_state({emit.key_for(*inv) for inv in emit.iter_invocations(root)}, state)
    assert secret not in state.read_text()

def test_only_the_intended_attributes_are_emitted(emit):
    """A field added carelessly here is a field shipped to the collector."""
    payload = emit.build_payload([("s1", "2026-09-17T21:00:00Z", "dplc-preflight")],
                                 emit.resource_attributes())
    for expected in (b"catalyst.skill", b"catalyst.plugin", b"session.id", b"invoked.at"):
        assert expected in payload
    for forbidden in (b"args", b"prompt", b"content"):
        assert forbidden not in payload


# --- idempotency -------------------------------------------------------------

def test_state_round_trips(emit, tmp_path):
    path = tmp_path / "state.json"
    emit.save_state({"a", "b"}, path)
    assert emit.load_state(path) == {"a", "b"}

def test_a_missing_state_file_reads_as_empty(emit, tmp_path):
    assert emit.load_state(tmp_path / "absent.json") == set()

def test_a_corrupt_state_file_reads_as_empty_rather_than_crashing(emit, tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{ not json")
    assert emit.load_state(path) == set()

def test_the_key_distinguishes_repeat_invocations(emit):
    """The same skill twice in one session is two invocations, not one."""
    a = emit.key_for("s1", "2026-09-17T21:00:00Z", "dplc-preflight")
    b = emit.key_for("s1", "2026-09-17T21:05:00Z", "dplc-preflight")
    assert a != b

def test_the_same_invocation_has_a_stable_key(emit):
    args = ("s1", "2026-09-17T21:00:00Z", "dplc-preflight")
    assert emit.key_for(*args) == emit.key_for(*args)


# --- endpoint handling -------------------------------------------------------

def test_named_collectors_resolve_with_the_signal_path(emit):
    for name in emit.COLLECTORS:
        assert emit.normalise_endpoint(name).endswith("/v1/metrics")

def test_a_host_only_url_gains_the_path(emit):
    """A per-signal endpoint is used as-is, so a bare host POSTs to '/' and 404s."""
    assert emit.normalise_endpoint("https://c.invalid") == "https://c.invalid/v1/metrics"

def test_a_typo_is_rejected(emit):
    for bad in ("prod", "localhost", "", "ftp://x.invalid"):
        with pytest.raises(ValueError):
            emit.normalise_endpoint(bad)

def test_collector_names_are_case_insensitive(emit):
    assert emit.normalise_endpoint("DEV") == emit.normalise_endpoint("dev")


# --- the encoder must verify itself ------------------------------------------

def test_resource_attributes_round_trip(emit):
    """An earlier version of this encoder double-wrapped every KeyValue, and the
    collector stored it anyway because the receiver never parses payloads. So
    acceptance proves the transport and says nothing about the encoding."""
    resource = emit.resource_attributes()
    payload = emit.build_payload([("s1", "t", "dplc-preflight")], resource)
    assert emit.decode_resource_attributes(payload) == resource

def test_the_producer_tag_is_present(emit):
    resource = emit.resource_attributes()
    assert resource["telemetry.producer"] == "claude-code"


# --- CLI ---------------------------------------------------------------------

def test_dry_run_sends_nothing(emit, tmp_path, monkeypatch, capsys):
    root = transcript(tmp_path, [skill_call("ai-catalyst:dplc-preflight")])
    sent = []
    monkeypatch.setattr(emit, "post", lambda *a, **k: sent.append(a) or (True, "200"))
    monkeypatch.setattr(emit, "STATE_FILE", tmp_path / "state.json")
    assert emit.main(["--transcripts", str(root)]) == 0
    assert not sent
    assert "Dry run" in capsys.readouterr().out

def test_apply_sends_and_records(emit, tmp_path, monkeypatch):
    root = transcript(tmp_path, [skill_call("ai-catalyst:dplc-preflight")])
    state = tmp_path / "state.json"
    monkeypatch.setattr(emit, "post", lambda *a, **k: (True, "200 OK"))
    monkeypatch.setattr(emit, "STATE_FILE", state)
    assert emit.main(["--transcripts", str(root), "--apply"]) == 0
    assert emit.load_state(state), "the invocation was not recorded"

def test_a_failed_send_does_not_record_state(emit, tmp_path, monkeypatch, capsys):
    """Otherwise a transient failure silently loses those invocations forever."""
    root = transcript(tmp_path, [skill_call("dplc-preflight")])
    state = tmp_path / "state.json"
    monkeypatch.setattr(emit, "post", lambda *a, **k: (False, "503"))
    monkeypatch.setattr(emit, "STATE_FILE", state)
    assert emit.main(["--transcripts", str(root), "--apply"]) == 4
    assert emit.load_state(state) == set()
    assert "nothing is lost" in capsys.readouterr().out

def test_a_second_run_sends_nothing_new(emit, tmp_path, monkeypatch, capsys):
    root = transcript(tmp_path, [skill_call("dplc-preflight")])
    state = tmp_path / "state.json"
    monkeypatch.setattr(emit, "post", lambda *a, **k: (True, "200 OK"))
    monkeypatch.setattr(emit, "STATE_FILE", state)
    emit.main(["--transcripts", str(root), "--apply"])
    capsys.readouterr()
    assert emit.main(["--transcripts", str(root), "--apply"]) == 0
    assert "Nothing new to send" in capsys.readouterr().out

def test_all_ignores_state_so_a_fresh_collector_can_be_backfilled(emit, tmp_path, monkeypatch, capsys):
    root = transcript(tmp_path, [skill_call("dplc-preflight")])
    state = tmp_path / "state.json"
    monkeypatch.setattr(emit, "post", lambda *a, **k: (True, "200 OK"))
    monkeypatch.setattr(emit, "STATE_FILE", state)
    emit.main(["--transcripts", str(root), "--apply"])
    capsys.readouterr()
    emit.main(["--transcripts", str(root), "--all"])
    assert "To send:          1" in capsys.readouterr().out

def test_non_catalyst_skills_are_excluded(emit, tmp_path, monkeypatch, capsys):
    """The stated scope is Catalyst skills only."""
    root = transcript(tmp_path, [
        skill_call("ai-toolkit:pr-status", stamp="t1"),
        skill_call("dataviz", stamp="t2"),
        skill_call("ai-catalyst:dplc-preflight", stamp="t3"),
    ])
    monkeypatch.setattr(emit, "STATE_FILE", tmp_path / "state.json")
    emit.main(["--transcripts", str(root)])
    out = capsys.readouterr().out
    assert "3 skill" in out.replace("Skill calls seen: ", "") or "seen: 3" in out
    assert "(1 are Catalyst skills)" in out
    assert "dplc-preflight" in out and "pr-status" not in out

def test_a_bad_endpoint_exits_2_before_reading_anything(emit, capsys):
    assert emit.main(["--endpoint", "prod"]) == 2
    assert "Bad --endpoint" in capsys.readouterr().out

def test_a_bad_since_is_rejected(emit, capsys):
    assert emit.main(["--since", "yesterday"]) == 2
    assert "Bad --since" in capsys.readouterr().out
