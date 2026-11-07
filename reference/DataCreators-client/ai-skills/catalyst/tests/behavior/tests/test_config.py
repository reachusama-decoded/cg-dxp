import os
import pytest
from tests.behavior.config import Config

class TestConfig:
    def test_loads_from_env(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.setenv("TEST_CATALOG", "cat")
        monkeypatch.setenv("TEST_SCHEMA", "sch")
        cfg = Config.from_env()
        assert cfg.anthropic_api_key == "sk-test"
        assert cfg.test_catalog == "cat"
        assert cfg.test_schema == "sch"
        assert cfg.judge_model == "claude-sonnet-4-6"
        assert cfg.judge_temperature == 0.0

    def test_missing_api_key_is_optional(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        cfg = Config.from_env()
        assert cfg.anthropic_api_key is None

    def test_substitute_env_in_string(self, monkeypatch):
        monkeypatch.setenv("TEST_CATALOG", "main_test")
        cfg = Config.from_env()
        assert cfg.substitute("${TEST_CATALOG}.foo") == "main_test.foo"
        assert cfg.substitute("no vars here") == "no vars here"

    def test_substitute_unset_var_raises(self, monkeypatch):
        monkeypatch.delenv("TEST_CATALOG", raising=False)
        cfg = Config.from_env()
        with pytest.raises(KeyError, match="TEST_CATALOG"):
            cfg.substitute("${TEST_CATALOG}.foo")

    def test_substitute_lenient_replaces_unset_with_marker(self, monkeypatch):
        monkeypatch.delenv("TEST_CATALOG", raising=False)
        cfg = Config.from_env()
        assert cfg.substitute("${TEST_CATALOG}.foo", strict=False) == "<unset:TEST_CATALOG>.foo"
