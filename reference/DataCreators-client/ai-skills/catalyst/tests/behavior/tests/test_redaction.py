"""Redactor tests — strings, nested structures, and the env-var pickup."""
from __future__ import annotations

import pytest

from tests.behavior.runner.redaction import (
    build_redactor,
    collect_secrets,
)


class TestRedactStrings:
    def test_replaces_secret_value_with_named_placeholder(self):
        r = build_redactor({"CONFLUENCE_API_TOKEN": "ATATT3xFfGF0SHR5"})
        out = r("curl -u user:ATATT3xFfGF0SHR5 https://example/")
        assert out == "curl -u user:<redacted:CONFLUENCE_API_TOKEN> https://example/"

    def test_multiple_secrets_in_one_string(self):
        r = build_redactor({
            "CONFLUENCE_API_TOKEN": "ATATT3xFfGF0SHR5",
            "DATABRICKS_TOKEN": "dapideadbeef0123",
        })
        out = r("ATATT3xFfGF0SHR5 and dapideadbeef0123")
        assert "ATATT3xFfGF0SHR5" not in out
        assert "dapideadbeef0123" not in out
        assert "<redacted:CONFLUENCE_API_TOKEN>" in out
        assert "<redacted:DATABRICKS_TOKEN>" in out

    def test_no_match_passes_through(self):
        r = build_redactor({"CONFLUENCE_API_TOKEN": "secret-value-here"})
        assert r("nothing sensitive here") == "nothing sensitive here"

    def test_empty_secrets_is_identity(self):
        r = build_redactor({})
        assert r("anything goes") == "anything goes"
        assert r({"a": 1}) == {"a": 1}


class TestRedactStructures:
    def test_walks_nested_dict(self):
        r = build_redactor({"CONFLUENCE_API_TOKEN": "shh-it-is-a-secret-1234"})
        out = r({"command": "echo shh-it-is-a-secret-1234", "depth": {"more": "shh-it-is-a-secret-1234"}})
        assert out["command"] == "echo <redacted:CONFLUENCE_API_TOKEN>"
        assert out["depth"]["more"] == "<redacted:CONFLUENCE_API_TOKEN>"

    def test_walks_list(self):
        r = build_redactor({"CONFLUENCE_API_TOKEN": "shh-it-is-a-secret-1234"})
        out = r([{"x": "shh-it-is-a-secret-1234"}, "shh-it-is-a-secret-1234", "ok"])
        assert out == [
            {"x": "<redacted:CONFLUENCE_API_TOKEN>"},
            "<redacted:CONFLUENCE_API_TOKEN>",
            "ok",
        ]

    def test_passes_through_scalars(self):
        r = build_redactor({"CONFLUENCE_API_TOKEN": "shh-it-is-a-secret-1234"})
        assert r(42) == 42
        assert r(None) is None
        assert r(True) is True

    def test_none_value_safe(self):
        r = build_redactor({"CONFLUENCE_API_TOKEN": "shh-it-is-a-secret-1234"})
        assert r(None) is None

    def test_longest_secret_wins_on_overlap(self):
        # If one secret is a prefix of another, the longer one should match
        # first — otherwise we'd leave a partial token.
        r = build_redactor({
            "SHORT": "abcd",
            "LONG": "abcdefgh",
        })
        out = r("the value is abcdefgh")
        assert out == "the value is <redacted:LONG>"


class TestCollectSecrets:
    def test_picks_up_default_vars_set_in_env(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "this-is-long-enough-to-be-a-token")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        secrets = collect_secrets()
        assert secrets["CONFLUENCE_API_TOKEN"] == "this-is-long-enough-to-be-a-token"
        assert "ANTHROPIC_API_KEY" not in secrets

    def test_skips_short_values(self, monkeypatch: pytest.MonkeyPatch):
        # A 3-char "secret" would scrub far too aggressively (e.g., "abc"
        # in normal output). Guard with a min-length.
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "abc")
        secrets = collect_secrets()
        assert "CONFLUENCE_API_TOKEN" not in secrets

    def test_extra_env_var_extends_list(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("MY_CUSTOM_TOKEN", "very-secret-value-here")
        monkeypatch.setenv("BEHAVIOR_TESTS_REDACT_VARS", "MY_CUSTOM_TOKEN")
        secrets = collect_secrets()
        assert secrets["MY_CUSTOM_TOKEN"] == "very-secret-value-here"

    def test_unset_vars_skipped(self, monkeypatch: pytest.MonkeyPatch):
        for name in ("CONFLUENCE_API_TOKEN", "JIRA_API_TOKEN",
                     "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
                     "DATABRICKS_TOKEN", "TEST_DATABRICKS_TOKEN"):
            monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv("BEHAVIOR_TESTS_REDACT_VARS", raising=False)
        assert collect_secrets() == {}
