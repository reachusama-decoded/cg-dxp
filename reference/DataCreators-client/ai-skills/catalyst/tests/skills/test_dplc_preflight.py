"""Unit tests for the dplc-preflight probe helpers.

Offline only. The live-probe paths (`probe_access`) are not exercised here — they
need a real workspace and are covered by the behavior case. What matters for unit
coverage is the logic that decides *what to tell the user*: config parsing,
workspace resolution, the auth-trap detection, blocker precedence, and the cache
format downstream skills read.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import pathlib
import sys

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "skills" / "dplc-preflight" / "scripts" / "preflight.py"


def _load():
    spec = importlib.util.spec_from_file_location("preflight_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pf():
    return _load()


@pytest.fixture(scope="module")
def real_probes(pf):
    """The unstubbed host probes, for the tests that cover them at the boundary.

    `_pin_environment_probes` replaces these on `pf` for every test, which is right
    for the callers and wrong for testing the probes themselves. Captured here
    instead of undoing that fixture: `monkeypatch` reverts after each test, and a
    module-scoped fixture is built before any function-scoped one, so these are
    always the originals.
    """
    return {"in_coder_workspace": pf.in_coder_workspace,
            "detect_harness": pf.detect_harness}


# --- Profile parsing --------------------------------------------------------

CFG = """\
[DEFAULT]
host = https://dbc-default.cloud.databricks.com
token = dapiSECRET

[sp-prod]
host = https://dbc-prod.cloud.databricks.com
client_id = abc-123
client_secret = shhh

[u2m]
host = https://dbc-u2m.cloud.databricks.com
auth_type = databricks-cli
"""


def test_read_profiles_classifies_auth_styles(pf, tmp_path, monkeypatch):
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text(CFG)
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)

    profiles = {p["profile"]: p for p in pf.read_profiles()}
    assert set(profiles) == {"DEFAULT", "sp-prod", "u2m"}
    assert profiles["DEFAULT"]["auth"] == "pat"
    assert profiles["sp-prod"]["auth"] == "oauth-m2m"
    assert profiles["u2m"]["auth"] == "databricks-cli"


def test_read_profiles_never_leaks_secrets(pf, tmp_path, monkeypatch):
    """A readiness report must never surface a token or client secret."""
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text(CFG)
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)

    blob = repr(pf.read_profiles())
    assert "dapiSECRET" not in blob
    assert "shhh" not in blob
    assert "abc-123" not in blob


def test_read_profiles_missing_file_is_empty_not_error(pf, tmp_path, monkeypatch):
    monkeypatch.setattr(pf, "DATABRICKS_CFG", tmp_path / "nope")
    assert pf.read_profiles() == []


def test_read_profiles_survives_malformed_config(pf, tmp_path, monkeypatch):
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text("this is not ini [[[\n")
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)
    assert pf.read_profiles() == []


# --- Workspace resolution ---------------------------------------------------

def test_env_host_wins_over_config(pf, tmp_path, monkeypatch):
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text(CFG)
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)
    monkeypatch.setenv("DATABRICKS_HOST", "https://from-env.cloud.databricks.com")
    monkeypatch.delenv("DATABRICKS_CONFIG_PROFILE", raising=False)

    active = pf.active_workspace()
    assert active["host"] == "https://from-env.cloud.databricks.com"
    assert active["resolved_from"] == "DATABRICKS_HOST"


def test_named_profile_resolves_its_host(pf, tmp_path, monkeypatch):
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text(CFG)
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    monkeypatch.setenv("DATABRICKS_CONFIG_PROFILE", "sp-prod")

    active = pf.active_workspace()
    assert active["host"] == "https://dbc-prod.cloud.databricks.com"
    assert "sp-prod" in active["resolved_from"]


def test_falls_back_to_default_profile(pf, tmp_path, monkeypatch):
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text(CFG)
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    monkeypatch.delenv("DATABRICKS_CONFIG_PROFILE", raising=False)

    active = pf.active_workspace()
    assert active["host"] == "https://dbc-default.cloud.databricks.com"
    assert "DEFAULT" in active["resolved_from"]


def test_no_config_at_all_resolves_to_none(pf, tmp_path, monkeypatch):
    monkeypatch.setattr(pf, "DATABRICKS_CFG", tmp_path / "nope")
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    monkeypatch.delenv("DATABRICKS_CONFIG_PROFILE", raising=False)

    active = pf.active_workspace()
    assert active["host"] == ""
    assert active["resolved_from"] == "none"


# --- The PAT trap (DBX-SEC-002 vs docs/install.md) --------------------------

def test_pat_only_is_flagged_as_will_be_refused(pf, monkeypatch):
    """install.md tells users to set DATABRICKS_TOKEN; connect-databricks exits 3."""
    monkeypatch.setenv("DATABRICKS_TOKEN", "dapiXXX")
    monkeypatch.delenv("DATABRICKS_CLIENT_ID", raising=False)
    monkeypatch.delenv("DATABRICKS_CLIENT_SECRET", raising=False)

    auth = pf.auth_style()
    assert auth["pat_env_set"] is True
    assert auth["will_be_refused_by_connect_databricks"] is True


def test_oauth_present_clears_the_flag(pf, monkeypatch):
    monkeypatch.setenv("DATABRICKS_TOKEN", "dapiXXX")
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "cid")
    monkeypatch.setenv("DATABRICKS_CLIENT_SECRET", "csec")

    auth = pf.auth_style()
    assert auth["oauth_m2m_env_set"] is True
    assert auth["will_be_refused_by_connect_databricks"] is False


def test_no_pat_is_not_flagged(pf, monkeypatch):
    for var in ("DATABRICKS_TOKEN", "DATABRICKS_CLIENT_ID", "DATABRICKS_CLIENT_SECRET"):
        monkeypatch.delenv(var, raising=False)
    assert pf.auth_style()["will_be_refused_by_connect_databricks"] is False


# --- Blocker precedence -----------------------------------------------------

def _state(*, python_ok=True, deps_ok=True, reachable=True, catalogs=None, warehouses=None):
    return {
        "toolchain": {"python_ok": python_ok, "deps_ok": deps_ok},
        "access": {
            "reachable": reachable,
            "catalogs": catalogs if catalogs is not None else ["sandbox"],
            "warehouses": warehouses if warehouses is not None else [{"name": "wh"}],
        },
    }


@pytest.mark.parametrize(
    "state,expected,why",
    [
        (_state(), 0, "everything present"),
        (_state(python_ok=False), 2, "python too old"),
        (_state(deps_ok=False), 2, "deps missing"),
        (_state(reachable=False), 3, "not connected"),
        (_state(catalogs=[]), 4, "connected but no catalogs"),
        (_state(warehouses=[]), 5, "connected, catalogs, no warehouse"),
    ],
)
def test_exit_code_precedence(pf, state, expected, why):
    assert pf.exit_code_for(state) == expected, why


def test_toolchain_blocker_outranks_access_blocker(pf):
    """Fix what the user can fix first: no point reporting auth when pip is broken."""
    state = _state(deps_ok=False, reachable=False, catalogs=[], warehouses=[])
    assert pf.exit_code_for(state) == 2


def test_every_exit_code_has_remediation(pf):
    for code in (0, 2, 3, 4, 5, 6):
        assert pf.REMEDIATION[code].strip()


# --- Cache format (downstream skills read this) ----------------------------

def _full_state(pf, **kw):
    s = _state(**kw)
    s["toolchain"].update({"python_version": "3.13", "python_too_new": False,
                           "missing_imports": [], "databricks_cli": True})
    s["access"].update({"identity": "user@capgroup.com", "reason": None, "client": "x"})
    s["active_workspace"] = {"host": "https://h", "profile": "DEFAULT",
                             "resolved_from": "~/.databrickscfg [DEFAULT]"}
    s["exit_code"] = pf.exit_code_for(s)
    s["verdict"] = "READY" if s["exit_code"] == 0 else "NOT READY"
    s["next_step"] = pf.REMEDIATION[s["exit_code"]]
    return s


def test_cache_is_valid_yaml_and_round_trips(pf, tmp_path):
    state = _full_state(pf, catalogs=["sandbox", "app_dev"],
                        warehouses=[{"name": "wh1", "state": "RUNNING"}])
    out = pf.write_cache(state, tmp_path / ".catalyst-env.yml")
    parsed = yaml.safe_load(out.read_text())

    assert parsed["verdict"] == "READY"
    assert parsed["exit_code"] == 0
    assert parsed["workspace"]["identity"] == "user@capgroup.com"
    assert parsed["access"]["catalogs"] == ["sandbox", "app_dev"]
    assert parsed["access"]["catalog_count"] == 2


def test_cache_empty_lists_stay_valid_yaml(pf, tmp_path):
    """The not-ready case is the one downstream skills hit most; it must parse."""
    state = _full_state(pf, reachable=False, catalogs=[], warehouses=[])
    out = pf.write_cache(state, tmp_path / ".catalyst-env.yml")
    parsed = yaml.safe_load(out.read_text())

    assert parsed["access"]["catalogs"] == []
    assert parsed["access"]["warehouses"] == []
    assert parsed["verdict"] == "NOT READY"


def test_cache_quotes_values_containing_yaml_specials(pf, tmp_path):
    state = _full_state(pf)
    state["active_workspace"]["resolved_from"] = "DATABRICKS_CONFIG_PROFILE=a: b #c"
    out = pf.write_cache(state, tmp_path / ".catalyst-env.yml")
    parsed = yaml.safe_load(out.read_text())
    assert parsed["workspace"]["resolved_from"] == "DATABRICKS_CONFIG_PROFILE=a: b #c"


# --- Toolchain probe --------------------------------------------------------

def test_probe_toolchain_reports_running_interpreter(pf):
    t = pf.probe_toolchain()
    assert t["python_ok"] is True  # the suite itself requires >= 3.10
    assert t["python_version"].count(".") == 1
    assert isinstance(t["missing_imports"], list)


def test_gather_skips_live_probe_when_deps_missing(pf, monkeypatch):
    """A pre-flight must work on an unprovisioned machine, not crash on it."""
    monkeypatch.setattr(pf, "probe_toolchain", lambda: {
        "python_version": "3.13", "python_ok": True, "python_too_new": False,
        "missing_imports": ["databricks.sdk"], "deps_ok": False, "databricks_cli": False,
    })

    def _boom():
        raise AssertionError("probe_access must not run when deps are missing")

    monkeypatch.setattr(pf, "probe_access", _boom)
    state = pf.gather()
    assert state["exit_code"] == 2
    assert state["access"]["reason"] == "dependencies not installed"


# --- A failed lookup is not an entitlement gap (review B1) -------------------
def _access(**kw):
    base = {
        "reachable": True, "catalogs": ["sandbox"], "warehouses": [{"name": "wh"}],
        "catalogs_error": None, "warehouses_error": None,
    }
    base.update(kw)
    return {"toolchain": {"python_ok": True, "deps_ok": True}, "access": base}


def test_failed_catalog_lookup_is_not_reported_as_an_entitlement_gap(pf):
    """Regression: a transient 5xx used to yield exit 4, whose remediation tells
    the user to go request Unity Catalog access they may already have."""
    state = _access(catalogs=[], catalogs_error="503 Service Unavailable")
    assert pf.exit_code_for(state) == 6
    assert pf.exit_code_for(state) != 4
    assert "entitlement" not in pf.REMEDIATION[6].lower() or "NOT" in pf.REMEDIATION[6]


def test_failed_warehouse_lookup_yields_the_undetermined_code(pf):
    state = _access(warehouses=[], warehouses_error="token expired mid-run")
    assert pf.exit_code_for(state) == 6


def test_undetermined_outranks_both_no_access_verdicts(pf):
    state = _access(catalogs=[], warehouses=[],
                    catalogs_error="boom", warehouses_error="boom")
    assert pf.exit_code_for(state) == 6


def test_genuine_no_catalogs_still_reports_the_entitlement_gap(pf):
    """The real entitlement case must survive the fix -- empty, no error."""
    state = _access(catalogs=[])
    assert pf.exit_code_for(state) == 4
    assert "entitlement gap" in pf.REMEDIATION[4]


def test_genuine_no_warehouses_still_reports_five(pf):
    assert pf.exit_code_for(_access(warehouses=[])) == 5


def test_remediation_for_undetermined_does_not_send_user_to_file_a_ticket(pf):
    text = pf.REMEDIATION[6]
    assert "NOT necessarily an entitlement gap" in text
    assert "re-run" in text


def test_both_lookup_errors_are_tracked_separately(pf, tmp_path):
    """L237 used to overwrite L232, so only the catalog reason survived."""
    state = _full_state(pf, catalogs=[], warehouses=[])
    state["access"]["catalogs_error"] = "catalog boom"
    state["access"]["warehouses_error"] = "warehouse boom"
    state["exit_code"] = pf.exit_code_for(state)
    state["verdict"] = "NOT READY"
    state["next_step"] = pf.REMEDIATION[state["exit_code"]]

    out = pf.write_cache(state, tmp_path / ".catalyst-env.yml")
    parsed = yaml.safe_load(out.read_text())
    assert parsed["access"]["catalogs_error"] == "catalog boom"
    assert parsed["access"]["warehouses_error"] == "warehouse boom"
    assert parsed["exit_code"] == 6


def test_check_output_distinguishes_lookup_failure_from_no_access(pf, monkeypatch, capsys, tmp_path):
    """The error text used to be captured into state and never printed."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(pf, "probe_toolchain", lambda: {
        "python_version": "3.13", "python_ok": True, "python_too_new": False,
        "missing_imports": [], "deps_ok": True, "databricks_cli": True})
    monkeypatch.setattr(pf, "probe_access", lambda: {
        "reachable": True, "reason": None, "identity": "u@capgroup.com",
        "client": "databricks-sdk", "warehouses": [], "catalogs": [],
        "catalogs_error": "503 from catalogs.list", "warehouses_error": None})

    code = pf.cmd_check(write=False)
    out = capsys.readouterr().out

    assert code == 6
    assert "LOOKUP FAILED" in out
    assert "503 from catalogs.list" in out
    assert "not evidence of missing entitlements" in out


# --- Active-profile marking (review N4) --------------------------------------
def test_env_host_does_not_mark_the_default_profile_active(pf, tmp_path, monkeypatch):
    """`<- active` next to DEFAULT while Host: shows an unrelated env host."""
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text(CFG)
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)
    monkeypatch.setenv("DATABRICKS_HOST", "https://from-env.cloud.databricks.com")
    monkeypatch.delenv("DATABRICKS_CONFIG_PROFILE", raising=False)

    active = pf.active_workspace()
    assert active["host"] == "https://from-env.cloud.databricks.com"
    assert active["active_profile"] is None


def test_named_profile_is_marked_active(pf, tmp_path, monkeypatch):
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text(CFG)
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    monkeypatch.setenv("DATABRICKS_CONFIG_PROFILE", "sp-prod")
    assert pf.active_workspace()["active_profile"] == "sp-prod"


def test_default_profile_is_marked_active_when_it_is_the_resolution(pf, tmp_path, monkeypatch):
    cfg = tmp_path / ".databrickscfg"
    cfg.write_text(CFG)
    monkeypatch.setattr(pf, "DATABRICKS_CFG", cfg)
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    monkeypatch.delenv("DATABRICKS_CONFIG_PROFILE", raising=False)
    assert pf.active_workspace()["active_profile"] == "DEFAULT"


def test_active_workspace_accepts_prethreaded_profiles(pf, monkeypatch):
    """gather() reads the config once and passes it in; no re-parsing."""
    monkeypatch.delenv("DATABRICKS_HOST", raising=False)
    monkeypatch.delenv("DATABRICKS_CONFIG_PROFILE", raising=False)
    monkeypatch.setattr(pf, "read_profiles", lambda: (_ for _ in ()).throw(
        AssertionError("read_profiles must not be called when profiles are passed")))
    active = pf.active_workspace([{"profile": "DEFAULT", "host": "https://h", "auth": "pat"}])
    assert active["host"] == "https://h"


# --- Dead code removed (review N3) ------------------------------------------
def test_the_subprocess_helper_is_not_dead_code(pf):
    """`_run` was removed once for being unreferenced, and this test pinned that.

    It is back, and referenced: the background pass cannot read credential
    liveness or installed versions off disk. The original intent was "no dead
    code", not "never shell out", so the assertion is inverted rather than
    deleted -- if `_run` ever becomes unreferenced again it should go again.

    Questions 1 to 4 still do not shell out; they answer from files and the SDK.
    `background` is the single exception, and it is scoped to that.
    """
    import inspect
    assert hasattr(pf, "_run")
    callers = [n for n in ("check_credential_liveness", "check_tool_versions",
                           "check_identity_coherence")
               if "_run(" in inspect.getsource(getattr(pf, n))]
    assert callers, "_run is unreferenced again -- remove it"
    for q in ("probe_otel", "probe_claude_code_otel"):
        assert "_run(" not in inspect.getsource(getattr(pf, q)), (
            f"{q} should answer from files, not by shelling out")


# --- Question 5: usage reporting (OTEL) -------------------------------------
#
# The guardrail tests here are the point of this block: captureContent must
# never be treated as a normal setting, and the JSONC parser must not choke on
# the file VS Code actually writes.


def _settings(tmp_path, body: str):
    p = tmp_path / "settings.json"
    p.write_text(body)
    return p


GOOD_OTEL = """\
{
  "github.copilot.chat.otel.enabled": true,
  "github.copilot.chat.otel.exporterType": "otlp-http",
  "github.copilot.chat.otel.otlpEndpoint": "https://catalyst-otel.datalake.aws.capgroup.com",
  "github.copilot.chat.otel.captureContent": false,
  "github.copilot.chat.otel.resourceAttributes": { "user.id": "RYQF" },
  "editor.fontSize": 13
}
"""


def _probe_with(pf, monkeypatch, path, now=None, mtime=None):
    monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [path])
    if mtime is not None:
        import os as _os
        _os.utime(path, (mtime, mtime))
    return pf.probe_otel(now=now)


class TestStripJsonc:
    def test_line_comments_removed(self, pf):
        assert '"a"' in pf._strip_jsonc('{\n // note\n "a": 1\n}')
        assert "note" not in pf._strip_jsonc('{\n // note\n "a": 1\n}')

    def test_block_comments_removed(self, pf):
        assert "gone" not in pf._strip_jsonc('{ /* gone */ "a": 1 }')

    def test_urls_survive(self, pf):
        """The // in https:// must not be eaten as a comment — every endpoint
        value in a real settings.json contains one."""
        out = pf._strip_jsonc('{"u": "https://example.com/x"}')
        import json as _json
        assert _json.loads(out)["u"] == "https://example.com/x"

    def test_escaped_quote_inside_string(self, pf):
        import json as _json
        out = pf._strip_jsonc(r'{"a": "he said \"hi\" // not a comment"}')
        assert _json.loads(out)["a"] == 'he said "hi" // not a comment'

    def test_trailing_comma_removed(self, pf):
        import json as _json
        assert _json.loads(pf._strip_jsonc('{"a": 1,\n}'))["a"] == 1

    def test_real_vscode_file_parses(self, pf, tmp_path):
        body = """\
{
  // Catalyst usage reporting
  "github.copilot.chat.otel.enabled": true,
  "github.copilot.chat.otel.otlpEndpoint": "https://catalyst-otel.datalake.aws.capgroup.com",
  /* trailing comma below is legal in JSONC */
  "editor.fontSize": 13,
}
"""
        settings, err = pf.read_user_settings(_settings(tmp_path, body))
        assert err is None
        assert settings["github.copilot.chat.otel.enabled"] is True


class TestStripJsoncCommas:
    """The comment pass tracked strings; the trailing-comma pass did not, so a
    comma inside a string value followed by `}` was silently removed — rewriting
    the parsed data, which then gets diagnosed as a different configuration than
    the one actually on disk."""

    def test_a_comma_inside_a_string_survives(self, pf):
        import json
        assert json.loads(pf._strip_jsonc('{"x":"a,}"}')) == {"x": "a,}"}

    def test_a_real_trailing_comma_is_still_removed(self, pf):
        import json
        assert json.loads(pf._strip_jsonc('{"a":1,}')) == {"a": 1}
        assert json.loads(pf._strip_jsonc('{"b":[1,2,]}')) == {"b": [1, 2]}

    def test_an_escaped_quote_does_not_end_the_string(self, pf):
        import json
        assert json.loads(pf._strip_jsonc(r'{"e":"q\",}"}')) == {"e": 'q",}'}

    def test_a_url_in_a_value_still_survives(self, pf):
        import json
        got = json.loads(pf._strip_jsonc('{"u":"https://h/p","a":1,}'))
        assert got["u"] == "https://h/p"


class TestOtelVerdicts:
    def test_no_settings_file_anywhere(self, pf, monkeypatch, tmp_path):
        monkeypatch.setattr(pf, "vscode_settings_candidates",
                            lambda: [tmp_path / "nope.json"])
        r = pf.probe_otel()
        assert r["verdict"] == pf.OTEL_NOT_CONFIGURED
        assert r["settings_path"] is None
        assert r["searched"]

    def test_configured_correctly_and_settled(self, pf, monkeypatch, tmp_path):
        p = _settings(tmp_path, GOOD_OTEL)
        r = _probe_with(pf, monkeypatch, p, now=10_000_000, mtime=1_000)
        assert r["verdict"] == pf.OTEL_OK
        assert r["problems"] == []

    def test_recent_edit_reports_pending_restart(self, pf, monkeypatch, tmp_path):
        """Correct settings edited seconds ago almost certainly have not been
        followed by the full quit the exporter needs."""
        p = _settings(tmp_path, GOOD_OTEL)
        r = _probe_with(pf, monkeypatch, p, now=1_060, mtime=1_000)
        assert r["verdict"] == pf.OTEL_PENDING_RESTART

    def test_all_four_right_but_no_user_id_is_still_a_problem(self, pf, monkeypatch, tmp_path):
        """Copilot Chat does not emit user.id on its own — RBLW verified that
        against 693 production payloads (PR #434). Passing on the other four
        would report a machine that sends only anonymous data as healthy."""
        body = GOOD_OTEL.replace(
            '  "github.copilot.chat.otel.resourceAttributes": { "user.id": "RYQF" },\n', "")
        p = _settings(tmp_path, body)
        r = _probe_with(pf, monkeypatch, p, now=10_000_000, mtime=1_000)
        assert r["verdict"] == pf.OTEL_MISCONFIGURED
        assert any("anonymous" in prob for prob in r["problems"])
        assert r["identity"] is None

    def test_identity_is_reported_when_set(self, pf, monkeypatch, tmp_path):
        p = _settings(tmp_path, GOOD_OTEL)
        r = _probe_with(pf, monkeypatch, p, now=10_000_000, mtime=1_000)
        assert r["identity"] == "RYQF"

    def test_nothing_set_is_not_configured(self, pf, monkeypatch, tmp_path):
        p = _settings(tmp_path, '{"editor.fontSize": 13}')
        r = _probe_with(pf, monkeypatch, p)
        assert r["verdict"] == pf.OTEL_NOT_CONFIGURED

    def test_wrong_endpoint_is_misconfigured(self, pf, monkeypatch, tmp_path):
        p = _settings(tmp_path, GOOD_OTEL.replace(
            "https://catalyst-otel.datalake.aws.capgroup.com", "https://wrong.example.com"))
        r = _probe_with(pf, monkeypatch, p, now=10_000_000, mtime=1_000)
        assert r["verdict"] == pf.OTEL_MISCONFIGURED
        assert any("otlpEndpoint" in p_ for p_ in r["problems"])

    def test_missing_exporter_type_is_misconfigured(self, pf, monkeypatch, tmp_path):
        body = GOOD_OTEL.replace(
            '  "github.copilot.chat.otel.exporterType": "otlp-http",\n', "")
        p = _settings(tmp_path, body)
        r = _probe_with(pf, monkeypatch, p, now=10_000_000, mtime=1_000)
        assert r["verdict"] == pf.OTEL_MISCONFIGURED
        assert any("exporterType" in p_ and "not set" in p_ for p_ in r["problems"])

    def test_explicitly_disabled_is_its_own_verdict(self, pf, monkeypatch, tmp_path):
        """enabled=false is a deliberate opt-out, not a misconfiguration to nag
        about."""
        p = _settings(tmp_path, GOOD_OTEL.replace(
            '"github.copilot.chat.otel.enabled": true', '"github.copilot.chat.otel.enabled": false'))
        r = _probe_with(pf, monkeypatch, p)
        assert r["verdict"] == pf.OTEL_DISABLED

    def test_unparseable_settings_is_reported_not_raised(self, pf, monkeypatch, tmp_path):
        p = _settings(tmp_path, '{"a": 1,, }')
        r = _probe_with(pf, monkeypatch, p)
        assert r["verdict"] == pf.OTEL_UNREADABLE
        assert r["problems"]


class TestCaptureContentGuardrail:
    """captureContent=true sends conversation text and needs a GRC review. It
    must be surfaced, must outrank every other verdict, and must never be
    presented as a normal option."""

    def test_capture_content_true_is_flagged(self, pf, monkeypatch, tmp_path):
        p = _settings(tmp_path, GOOD_OTEL.replace(
            '"github.copilot.chat.otel.captureContent": false',
            '"github.copilot.chat.otel.captureContent": true'))
        r = _probe_with(pf, monkeypatch, p)
        assert r["verdict"] == pf.OTEL_CAPTURE_CONTENT
        assert any("captureContent" in p_ for p_ in r["problems"])

    def test_capture_content_outranks_otherwise_broken_config(self, pf, monkeypatch, tmp_path):
        """Even with everything else wrong, captureContent is the headline."""
        p = _settings(tmp_path, '{"github.copilot.chat.otel.captureContent": true}')
        r = _probe_with(pf, monkeypatch, p)
        assert r["verdict"] == pf.OTEL_CAPTURE_CONTENT

    def test_expected_config_never_enables_capture_content(self, pf):
        assert pf.OTEL_EXPECTED[pf.OTEL_CAPTURE_KEY] is False

    def test_remediation_names_grc_and_says_turn_it_off(self, pf):
        text = pf.OTEL_REMEDIATION[pf.OTEL_CAPTURE_CONTENT]
        assert "Governance" in text
        assert "false" in text

    def test_otel_subcommand_exits_nonzero_only_for_capture_content(self, pf, monkeypatch, tmp_path):
        # Isolate the Copilot half: the Claude Code probe has its own exit
        # contribution, tested separately below.
        monkeypatch.setattr(pf, "detect_harness", lambda: "vscode")
        p = _settings(tmp_path, GOOD_OTEL.replace(
            '"github.copilot.chat.otel.captureContent": false',
            '"github.copilot.chat.otel.captureContent": true'))
        monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [p])
        assert pf.cmd_otel() == 1
        good = _settings(tmp_path, GOOD_OTEL)
        monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [good])
        assert pf.cmd_otel() == 0

    def test_otel_subcommand_also_fails_on_claude_code_content_capture(
            self, pf, monkeypatch, tmp_path):
        """Either harness leaking content should make the subcommand fail."""
        good = _settings(tmp_path, GOOD_OTEL)
        monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [good])
        monkeypatch.setattr(pf, "probe_claude_code_otel",
                            lambda *a, **k: {"verdict": pf.CC_OTEL_CONTENT_CAPTURE,
                                             "harness": "claude-code", "values": {},
                                             "sources": {}, "problems": ["x"]})
        assert pf.cmd_otel() == 1


class TestDevCollectorIsAccepted:
    """Both Catalyst collectors are valid, not just prd.

    Pointing Copilot Chat at dev is a legitimate override -- the Claude Code side
    has named and chosen between the same two since AICAT-337. Checking against prd
    alone produced a report that said MISCONFIGURED directly above `Reachable: yes`
    for that same endpoint, which is how a check teaches people to ignore it.
    """

    def _with_endpoint(self, pf, monkeypatch, tmp_path, url):
        body = GOOD_OTEL.replace("https://catalyst-otel.datalake.aws.capgroup.com", url)
        return _probe_with(pf, monkeypatch, _settings(tmp_path, body),
                           now=10_000_000, mtime=1_000)

    def test_dev_collector_is_on_not_misconfigured(self, pf, monkeypatch, tmp_path):
        r = self._with_endpoint(pf, monkeypatch, tmp_path, pf.OTEL_COLLECTORS["dev"])
        assert r["verdict"] == pf.OTEL_OK
        assert r["problems"] == []

    def test_dev_collector_is_named_in_a_note(self, pf, monkeypatch, tmp_path):
        """Accepted, but never silently: a laptop reporting into dev for a month
        because someone forgot is the failure this note exists to prevent."""
        r = self._with_endpoint(pf, monkeypatch, tmp_path, pf.OTEL_COLLECTORS["dev"])
        assert r["collector"] == "dev"
        assert any("dev collector" in n for n in r["notes"])

    def test_prd_collector_gets_no_note(self, pf, monkeypatch, tmp_path):
        r = self._with_endpoint(pf, monkeypatch, tmp_path, pf.OTEL_COLLECTORS["prd"])
        assert r["collector"] == "prd"
        assert r["notes"] == []

    def test_a_trailing_slash_is_still_the_same_collector(self, pf, monkeypatch, tmp_path):
        r = self._with_endpoint(pf, monkeypatch, tmp_path,
                                pf.OTEL_COLLECTORS["dev"] + "/")
        assert r["verdict"] == pf.OTEL_OK
        assert r["collector"] == "dev"

    def test_an_unknown_endpoint_is_still_a_problem(self, pf, monkeypatch, tmp_path):
        """Widening to two collectors must not widen to anything at all."""
        r = self._with_endpoint(pf, monkeypatch, tmp_path, "https://wrong.example.com")
        assert r["verdict"] == pf.OTEL_MISCONFIGURED
        assert r["collector"] is None
        assert any("not a Catalyst collector" in p_ for p_ in r["problems"])

    def test_a_lookalike_host_is_not_accepted(self, pf, monkeypatch, tmp_path):
        """The match is a lookup against two known URLs, not a substring test."""
        r = self._with_endpoint(
            pf, monkeypatch, tmp_path,
            "https://catalyst-otel.datalake.aws.capgroup.com.evil.example.com")
        assert r["verdict"] == pf.OTEL_MISCONFIGURED
        assert r["collector"] is None

    def test_a_padded_url_is_not_accepted(self, pf, monkeypatch, tmp_path):
        """Whitespace is not cosmetic: the exporter uses the value verbatim.

        An earlier revision did `url.strip().rstrip("/")`, so a padded endpoint was
        accepted and reported `collector: prd` with a green `ON` -- directly above
        `Reachable: no`, with nothing naming the padding as the cause. Normalising
        inside an accept gate is how a check ends up confidently wrong, which is the
        one thing this skill must never be.
        """
        padded = "  " + pf.OTEL_COLLECTORS["prd"] + "  "
        assert pf.collector_name(padded) is None
        r = self._with_endpoint(pf, monkeypatch, tmp_path, padded)
        assert r["verdict"] == pf.OTEL_MISCONFIGURED
        assert r["collector"] is None

    def test_an_internally_padded_url_is_not_accepted(self, pf):
        """`\t` and `\n`, not just spaces -- a hand-edited settings.json is where
        these come from."""
        for pad in ("\t", "\n", " \n\t"):
            assert pf.collector_name(pad + pf.OTEL_COLLECTORS["dev"]) is None
            assert pf.collector_name(pf.OTEL_COLLECTORS["dev"] + pad) is None


class TestOtelIsAdvisoryOnly:
    def test_otel_never_changes_the_exit_code(self, pf):
        """Telemetry is not a prerequisite for building a data product. A broken
        or absent OTEL config must not make a ready machine report NOT READY."""
        ready = {
            "toolchain": {"python_ok": True, "deps_ok": True},
            "access": {"reachable": True, "catalogs": ["c"], "warehouses": [{"name": "w"}],
                       "catalogs_error": None, "warehouses_error": None},
        }
        assert pf.exit_code_for(ready) == 0
        for verdict in (pf.OTEL_NOT_CONFIGURED, pf.OTEL_CAPTURE_CONTENT, pf.OTEL_MISCONFIGURED):
            ready["otel"] = {"verdict": verdict}
            assert pf.exit_code_for(ready) == 0, verdict

    def test_settings_candidates_are_user_scope_only(self, pf):
        """Workspace and folder settings do not enable the exporter, so writing
        or reading them would be misleading."""
        for path in pf.vscode_settings_candidates():
            assert path.name == "settings.json"
            assert path.parent.name == "User"


class TestEndpointReachability:
    def test_unresolvable_host_is_reported_as_dns_and_says_vpn(self, pf):
        r = pf.probe_otel_endpoint("https://not-a-real-host.invalid", timeout=1)
        assert r["reachable"] is False
        assert r["kind"] == "dns"
        assert "VPN" in r["detail"]

    def test_bad_url_does_not_raise(self, pf):
        r = pf.probe_otel_endpoint("not-a-url")
        assert r["reachable"] is False
        assert r["kind"] == "bad-url"

    def test_tcp_accept_is_not_treated_as_reachable_for_https(self, pf, monkeypatch):
        """A load balancer with no healthy backend accepts TCP then resets during
        TLS. Stopping at connect() would report a dead collector as fine — which
        is exactly what it did before this was fixed."""
        import socket as _socket
        import ssl as _ssl

        class _Sock:
            def close(self): pass

        monkeypatch.setattr(_socket, "create_connection", lambda *a, **k: _Sock())
        monkeypatch.setattr(_socket, "getaddrinfo", lambda *a, **k: [None])

        def _boom(self, sock, server_hostname=None):
            raise _ssl.SSLError(104, "Connection reset by peer")
        monkeypatch.setattr(_ssl.SSLContext, "wrap_socket", _boom)

        r = pf.probe_otel_endpoint("https://collector.example.com")
        assert r["reachable"] is False
        assert r["kind"] == "tls-reset"
        # Must name both causes, not assert one: network isolation and an
        # unhealthy backend are indistinguishable from a client.
        assert "network policy" in r["detail"]
        assert "no healthy backend" in r["detail"]

    def test_tls_verify_failure_says_ca_bundle_not_disable_verification(self, pf, monkeypatch):
        """Same rule as cgrepo: corporate TLS interception is fixed by pointing at
        the trust anchor, never by turning verification off."""
        import socket as _socket
        import ssl as _ssl

        class _Sock:
            def close(self): pass
        monkeypatch.setattr(_socket, "create_connection", lambda *a, **k: _Sock())
        monkeypatch.setattr(_socket, "getaddrinfo", lambda *a, **k: [None])

        def _verify_fail(self, sock, server_hostname=None):
            exc = _ssl.SSLCertVerificationError("bad cert")
            exc.verify_message = "unable to get local issuer certificate"
            raise exc
        monkeypatch.setattr(_ssl.SSLContext, "wrap_socket", _verify_fail)

        r = pf.probe_otel_endpoint("https://collector.example.com")
        assert r["kind"] == "tls-verify"
        assert "NODE_EXTRA_CA_CERTS" in r["detail"]
        assert "never" in r["detail"] and "disable" in r["detail"]

    def test_dns_and_unreachable_give_different_advice(self, pf):
        """Off-network and on-VPN-but-blocked need different next steps: connect
        to VPN versus tell the EDO team, because retrying never fixes the second."""
        dns = pf.probe_otel_endpoint("https://not-a-real-host.invalid", timeout=1)
        assert "VPN and re-run" in dns["detail"]
        assert "EDO team" not in dns["detail"]


class TestOtelInCache:
    def test_cache_records_verdict_and_problems(self, pf, tmp_path, monkeypatch):
        monkeypatch.setattr(pf, "vscode_settings_candidates",
                            lambda: [tmp_path / "absent.json"])
        state = {
            "verdict": "READY", "exit_code": 0, "next_step": "Ready to build.",
            "toolchain": {"python_version": "3.13", "python_ok": True, "deps_ok": True},
            "active_workspace": {"host": "h", "profile": "p", "resolved_from": "env"},
            "access": {"identity": "me", "reachable": True, "catalogs": [], "warehouses": [],
                       "catalogs_error": None, "warehouses_error": None},
            "otel": pf.probe_otel(),
        }
        out = pf.write_cache(state, tmp_path / ".catalyst-env.yml")
        loaded = yaml.safe_load(out.read_text())
        assert loaded["otel"]["verdict"] == pf.OTEL_NOT_CONFIGURED
        assert loaded["otel"]["problems"]


# --- Question 5b: Claude Code telemetry -------------------------------------
#
# Different mechanism from Copilot Chat: env vars rather than settings keys, and
# on a DevNext workspace usually set by managed settings the user cannot change.
# These tests pin the three findings that matter operationally — content capture
# on, a dead destination, and metrics never exported — plus the settings-layer
# precedence, because telling a user to change a managed value wastes their time.


@pytest.fixture(autouse=True)
def _pin_environment_probes(pf, monkeypatch):
    """Pin the two probes that read the host, for every test in this module.

    `detect_harness` and `in_coder_workspace` answer from the real machine, so an
    unpinned test asserts against wherever the suite happened to run — green on a
    Coder workspace under Claude Code, red on a macOS VS Code checkout.

    Autouse rather than a parameter on `_cc_env`, because only 1 of the 3 coupled
    call sites went through that helper. Nine more test bodies hand-roll the same
    setup and two call the probes directly; a fix at helper level leaves those
    uncovered and needing one-off pins that nothing guards. Same reasoning as
    `_clear_gh_auth_cache` below.

    A test wanting different values patches them itself — `monkeypatch.setattr` in
    the test body runs after this fixture and wins. That is how every VS Code and
    Copilot harness test in this file keeps working.

    **These stub internal functions, which `rfd/0008/python/test.md` (`py-test-007`)
    rightly warns against: an internal mock tests the mock.** The stub is here only
    to make *callers* deterministic. The functions' own behaviour is covered at the
    boundary instead — see `TestInCoderWorkspaceReadsItsInputs`, which is what makes
    dropping a clause from `in_coder_workspace` fail. Without that class this pin is
    pure coverage loss, and it was: `return True` and `return False` mutants of
    `in_coder_workspace` both survived all 231 tests.
    """
    monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
    monkeypatch.setattr(pf, "in_coder_workspace", lambda: False)


def _cc_env(pf, monkeypatch, env, managed=None, user=None, port_open=False,
            in_coder=None):
    """Drive `probe_claude_code_otel` against a pinned environment.

    `detect_harness` and `in_coder_workspace` are pinned by `_pin_environment_probes`
    above, not here — so they are never set in two places. `in_coder=True` overrides
    that pin for the tests that need a Coder workspace; `None` keeps the default.
    """
    layers = [p for p in (managed, user) if p is not None]
    monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: layers)
    monkeypatch.setattr(pf, "_port_open", lambda *a, **k: port_open)
    if in_coder is not None:
        monkeypatch.setattr(pf, "in_coder_workspace", lambda: in_coder)
    monkeypatch.setattr(pf.os, "environ", env)
    return pf.probe_claude_code_otel()


@pytest.fixture(autouse=True)
def _clear_gh_auth_cache(pf):
    """`_gh_auth_status` memoises per process, which is right for a one-shot CLI and
    wrong for a test session: without this, whichever test ran first decides what
    every later test believes about `gh`."""
    pf._GH_AUTH_CACHE.clear()
    yield
    pf._GH_AUTH_CACHE.clear()


def _gh_json(login="RYQF_capgroup", state="success", token_source="keyring",
             others=(), noise=True, error=None):
    """A `gh auth status --json hosts` payload.

    `noise` reproduces what `_run` actually hands the parser: it concatenates
    stderr onto stdout, and gh writes a human line there even when it exits 0 with
    valid JSON. Tests that omitted it would pass against a plain `json.loads`.
    """
    import json as _json
    account = {"state": state, "active": True, "host": "github.com",
               "login": login, "tokenSource": token_source}
    if error is not None:
        # gh interpolates the HTTP response body here; real ones run to a couple of
        # hundred characters, which is why the renderer truncates.
        account["error"] = error
    accounts = [account]
    accounts.extend(others)
    payload = _json.dumps({"hosts": {"github.com": accounts}})
    return payload + ("\nYou are not logged into any GitHub hosts." if noise else "")


def _gh_failed_account(login="RYQF_capgroup", token_source="keyring"):
    """A non-active account gh reports as broken -- the stale keyring entry that
    makes `gh auth status` exit 1 while the active account is perfectly fine."""
    return {"state": "error", "error": "HTTP 401: Bad credentials", "active": False,
            "host": "github.com", "login": login, "tokenSource": token_source}


def _write_settings(tmp_path, name, env):
    import json as _json
    p = tmp_path / name
    p.write_text(_json.dumps({"env": env}))
    return p


class TestHarnessDetection:
    def test_claude_code_detected_from_env(self, pf, monkeypatch):
        monkeypatch.setenv("CLAUDECODE", "1")
        assert pf.detect_harness() == "claude-code"

    def test_entrypoint_marker_also_counts(self, pf, monkeypatch):
        monkeypatch.delenv("CLAUDECODE", raising=False)
        monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "cli")
        assert pf.detect_harness() == "claude-code"

    def test_not_applicable_when_not_claude_code(self, pf, monkeypatch):
        monkeypatch.setattr(pf, "detect_harness", lambda: "vscode")
        r = pf.probe_claude_code_otel()
        assert r["verdict"] == pf.CC_OTEL_NOT_CLAUDE_CODE
        assert r["problems"] == []

    def test_managed_path_is_os_appropriate(self, pf):
        layers = pf.claude_code_settings_layers()
        assert layers[-1].name == "settings.json"
        assert "managed-settings.json" in layers[0].name


class TestClaudeCodeOtelVerdicts:
    def test_off_when_telemetry_not_enabled(self, pf, monkeypatch):
        r = _cc_env(pf, monkeypatch, {})
        assert r["verdict"] == pf.CC_OTEL_OFF

    def test_fully_configured_is_on(self, pf, monkeypatch):
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOGS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://collector.example.com/s/devnext",
        })
        assert r["verdict"] == pf.CC_OTEL_ON
        assert r["problems"] == []

    def test_endpoint_without_the_source_segment_is_noted_not_flagged(self, pf,
                                                                     monkeypatch):
        """Recorded, not a problem, until catalyst-otel#12 is deployed.

        The producer partition does not exist yet -- the dev bucket holds only
        raw/year=... with no source= prefix -- so an endpoint without the segment is
        correct for today's collector. Flagging it failed the endpoint this repo
        itself recommends, which is how a check loses credibility.

        `in_coder=True` because the note is only raised inside a Coder workspace,
        which is the condition the assertion is about.
        """
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOG_TOOL_DETAILS": "1",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://collector.example.com",
        }, in_coder=True)
        assert r.get("source_segment_missing") is True
        assert not any(pf.CC_SOURCE_SEGMENT in p for p in r["problems"])

    def test_tool_details_on_is_recorded_but_not_our_problem(self, pf, monkeypatch):
        """Policy change: it is the enterprise's call, and it cannot reach us.

        TOOL_DETAILS affects LOG records only -- it adds tool_parameters and command
        lines to tool_result events and changes nothing about cost.usage or
        token.usage. So it neither dilutes Catalyst's metrics nor can arrive at a
        metrics-only collector. This test previously asserted it was reported as a
        problem, which overreached into a setting security monitoring may want.
        """
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOG_TOOL_DETAILS": "1",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://catalyst-otel.example.com/v1/metrics",
        })
        assert r.get("tool_details_on") is True
        assert not any("tool arguments" in p for p in r["problems"])

    def test_tool_details_off_is_not_a_problem(self, pf, monkeypatch):
        """The inverse of the above, and the config we actually recommend."""
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOGS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://collector.example.com/s/devnext",
        })
        assert r["verdict"] == pf.CC_OTEL_ON
        assert r["problems"] == []

    def test_tool_details_is_not_a_content_switch(self, pf):
        """Over-collection, not a GRC breach — it must not trip that verdict."""
        assert pf.CC_OVER_COLLECTION_SWITCH not in pf.CC_CONTENT_SWITCHES

    def test_no_logs_exporter_is_fine_because_metrics_carry_attribution(
            self, pf, monkeypatch):
        """This test asserted the opposite and was wrong.

        `skill.name`, `agent.name`, `plugin.name` and `marketplace.name` are
        attributes on the cost.usage and token.usage METRICS, so attribution is
        complete without any log records. Demanding a logs exporter pushed operators
        toward shipping the one signal that carries prompt text in order to get
        something metrics already provide.
        """
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://catalyst-otel.example.com/v1/metrics",
        })
        assert not any("skill.name" in p for p in r["problems"])
        assert r["verdict"] == pf.CC_OTEL_ON

    def test_enabled_with_no_endpoint_and_no_local_collector(self, pf, monkeypatch):
        """The real DevNext failure mode: telemetry on, exporting to a localhost
        default with nothing listening, so data is produced and discarded."""
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOGS_EXPORTER": "otlp",
        }, port_open=False)
        assert r["verdict"] == pf.CC_OTEL_NO_DESTINATION
        assert any("nothing is listening" in p for p in r["problems"])

    def test_no_endpoint_but_a_local_collector_is_not_a_dead_destination(self, pf, monkeypatch):
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
        }, port_open=True)
        assert r["verdict"] != pf.CC_OTEL_NO_DESTINATION

    def test_missing_metrics_exporter_is_reported(self, pf, monkeypatch):
        """Logs-only is easy to ship by accident and silently loses every metric."""
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_LOGS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://collector.example.com",
        })
        assert any("OTEL_METRICS_EXPORTER" in p for p in r["problems"])

    def test_grpc_protocol_uses_the_grpc_default_port(self, pf, monkeypatch):
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
            "OTEL_METRICS_EXPORTER": "otlp",
        }, port_open=False)
        assert any("4317" in p for p in r["problems"])


class TestOnMeansOn:
    """`ON` is documented as enabled, with a destination and both exporters. It
    was being returned alongside a non-empty problems list, which is the same
    class of false pass as the missing `user.id` this whole check exists for."""

    def test_a_missing_metrics_exporter_is_not_on(self, pf, monkeypatch):
        """Now the METRICS exporter, not the logs one. Attribution rides on
        cost.usage and token.usage, so its absence is what actually loses the data
        -- the live DevNext policy omits it."""
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://catalyst-otel.example.com/v1/metrics",
        })
        assert any("OTEL_METRICS_EXPORTER" in p for p in r["problems"])
        assert r["verdict"] == pf.CC_OTEL_MISCONFIGURED

    def test_the_generic_endpoint_with_content_logging_is_not_on(self, pf, monkeypatch):
        """The new hazard. The generic endpoint is the fallback for every unset
        signal, so with content logging on it routes prompt text wherever it points
        -- which is exactly what the metrics-specific variable exists to avoid."""
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOG_USER_PROMPTS": "1",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://somewhere.example.com",
        })
        assert any("generic" in p for p in r["problems"])
        assert r["verdict"] == pf.CC_OTEL_MISCONFIGURED

    def test_a_clean_metrics_only_config_is_on(self, pf, monkeypatch):
        """The configuration this repo recommends must pass its own check."""
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://catalyst-otel.example.com/v1/metrics",
            "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL": "http/protobuf",
        })
        assert r["verdict"] == pf.CC_OTEL_ON, r["problems"]

    def test_every_verdict_has_remediation_text(self, pf):
        """A verdict with no remediation prints a KeyError at the user."""
        for name in dir(pf):
            if name.startswith("CC_OTEL_") and name != "CC_OTEL_REMEDIATION":
                verdict = getattr(pf, name)
                if isinstance(verdict, str):
                    assert verdict in pf.CC_OTEL_REMEDIATION, name

    def test_a_content_leak_outranks_every_other_problem(self, pf, monkeypatch):
        """Content actually arriving at Catalyst is the loudest finding there is and
        must not be masked by a missing exporter or a wrong protocol."""
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_LOG_USER_PROMPTS": "1",
            "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "https://catalyst-otel.example.com",
            "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
        })
        assert r["verdict"] == pf.CC_OTEL_CONTENT_CAPTURE
        assert r["content_leak"] is True


class TestBackgroundChecks:
    """The quiet pass. Its whole value is being ignorable when healthy and
    specific when not, so the tests are about noise and blocking, not coverage."""

    def test_telemetry_is_checked_and_comes_first(self, pf):
        """The whole point of the pass. Telemetry is the only one of the four whose
        failure is invisible by design -- there is no UI confirmation of Copilot
        Chat reporting anywhere -- so a user will never discover it unaided."""
        import inspect
        src = inspect.getsource(pf.background_findings)
        assert "check_telemetry()" in src
        # First key, because ordering is what the user reads first.
        keys = [l.split('"')[1] for l in src.splitlines() if '":' in l]
        assert keys[0] == "telemetry", keys

    def test_telemetry_reuses_the_existing_probes(self, pf):
        """A second implementation of the OTEL checks would drift from questions
        5 and 5b, which are the tested ones."""
        import inspect
        src = inspect.getsource(pf.check_telemetry)
        assert "probe_claude_code_otel(" in src and "probe_otel(" in src

    def test_telemetry_check_does_not_probe_a_remote_endpoint(self, pf, monkeypatch):
        """It has to be cheap enough to run without anyone noticing.

        This test used to assert `"check_local_collector=False" in getsource(...)`,
        which became a **false pass** the moment that kwarg was removed: the string
        survived in the function's own docstring, so the assertion held while the
        behaviour it described had been deliberately inverted. Two tests in this file
        then asserted opposite things and both passed.

        What matters is not which kwarg is passed but that nothing here leaves the
        machine, so that is what is asserted -- against behaviour, not source text.
        """
        calls = []
        monkeypatch.setattr(pf, "probe_otel_endpoint",
                            lambda *a, **k: calls.append(("remote",) + a) or {})
        monkeypatch.setattr(pf, "_port_open",
                            lambda host, port, **k: calls.append(("port", host, port)) or False)
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [])
        monkeypatch.setattr(pf.os, "environ", {"CLAUDE_CODE_ENABLE_TELEMETRY": "1"})
        pf.check_telemetry()
        assert not [c for c in calls if c[0] == "remote"], f"probed a remote endpoint: {calls}"
        # A loopback connect is expected and is not egress -- it is what lets this
        # reach ON_BUT_NO_DESTINATION instead of under-reporting it.
        assert any(c[0] == "port" and c[1].startswith("127.") for c in calls), calls

    def test_a_healthy_harness_reports_no_telemetry_finding(self, pf, monkeypatch):
        monkeypatch.setattr(pf, "probe_claude_code_otel",
                            lambda **k: {"verdict": pf.CC_OTEL_ON, "problems": []})
        monkeypatch.setattr(pf, "probe_otel",
                            lambda **k: {"verdict": pf.OTEL_OK, "settings_path": "/x",
                                         "identity": "RYQF", "problems": []})
        assert pf.check_telemetry() == []

    def test_content_capture_is_surfaced(self, pf, monkeypatch):
        """The live finding on a DevNext workspace: OTEL_LOG_USER_PROMPTS on."""
        monkeypatch.setattr(pf, "probe_claude_code_otel",
                            lambda **k: {"verdict": pf.CC_OTEL_CONTENT_CAPTURE,
                                         "problems": []})
        monkeypatch.setattr(pf, "probe_otel",
                            lambda **k: {"verdict": pf.OTEL_OK, "settings_path": None,
                                         "identity": None, "problems": []})
        findings = pf.check_telemetry()
        assert any("CONTENT_CAPTURE" in f for f in findings)

    # --- the anonymous-Copilot case, driven by the real probe ----------------
    #
    # This used to be one test that stubbed
    #   {"verdict": OTEL_PENDING_RESTART, "identity": None, "problems": []}
    # and asserted "anonymous" appeared in the findings. `probe_otel` cannot produce
    # that triple: a missing `user.id` makes it append a problem, and a non-empty
    # problems list forces MISCONFIGURED. So the test passed against a state that does
    # not exist, reporting coverage of a branch that is unreachable --
    #   `if o["verdict"] in (OTEL_OK, OTEL_PENDING_RESTART) and not o.get("identity")`
    # with OTEL_OK already excluded by the enclosing condition. AICAT-343.
    #
    # Split in two: what happens, and what should.

    def _no_user_id(self, pf, monkeypatch, tmp_path):
        """All four Copilot keys correct, no `resourceAttributes.user.id`, through the
        real `probe_otel` rather than a hand-built result."""
        import json as _json
        s = tmp_path / "settings.json"
        s.write_text(_json.dumps({
            "github.copilot.chat.otel.enabled": True,
            "github.copilot.chat.otel.exporterType": "otlp-http",
            "github.copilot.chat.otel.otlpEndpoint":
                "https://catalyst-otel.datalake.aws.capgroup.com",
            "github.copilot.chat.otel.captureContent": False,
        }))
        monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [s])
        monkeypatch.setattr(pf, "probe_claude_code_otel",
                            lambda **k: {"verdict": pf.CC_OTEL_NOT_CLAUDE_CODE,
                                         "problems": []})
        return pf.probe_otel()

    def test_a_missing_user_id_is_misconfigured_not_pending(self, pf, monkeypatch, tmp_path):
        """Pins the state the old stub got wrong, so the xfail below cannot drift."""
        r = self._no_user_id(pf, monkeypatch, tmp_path)
        assert r["verdict"] == pf.OTEL_MISCONFIGURED
        assert r["identity"] is None
        assert any("user.id" in p for p in r["problems"])

    def test_anonymous_copilot_reporting_is_surfaced(self, pf, monkeypatch, tmp_path):
        """Configured but with no user.id: the exporter works and nothing is
        attributable, which is the defect #439 exists to close.

        **Was `xfail(strict=True)` against AICAT-343, and this PR fixes it** -- which
        is how the marker announced itself: joining `o["problems"]` into the finding
        makes the sentence reach the user, so the xfail XPASSed and reddened the
        build. Caught by @CONNMS_capgroup against the actual merge result rather than
        a rebase, and it is the reason the marker was strict.

        Note *which* half is fixed. The user-visible defect is gone: `probe_otel`
        produces "resourceAttributes has no user.id, so every report is anonymous"
        and `check_telemetry` now renders it. The unsatisfiable inner branch is a
        separate thing, removed in this PR as dead code rather than repaired --
        `OTEL_OK` is excluded by the enclosing condition, and a missing `user.id`
        forces `MISCONFIGURED`, never `PENDING_RESTART`, so nothing could ever reach
        it. The assertion below deliberately does not care which line produced the
        text, only that the user is told.
        """
        self._no_user_id(pf, monkeypatch, tmp_path)
        findings = pf.check_telemetry()
        assert any("anonymous" in f for f in findings), findings
        assert any("user.id" in f for f in findings), (
            "the cause has to be named, not just the consequence"
        )

    # `test_no_vs_code_is_not_reported_as_a_telemetry_gap` lived here. Deleted
    # rather than repaired: once the harness is pinned it contributes no coverage
    # that `TestVsCodeWithNoSettingsFileIsStillReported` does not already provide --
    # measured kill sets are identical with it present or absent, across four
    # mutations of `check_telemetry` and its harness heuristic. That class is the
    # better home anyway: it is parameterised on (harness, settings_path) and has
    # the positive counterpart, so the "no VS Code is not a gap" rule and the "a
    # settings file is reported regardless of harness" rule are stated next to each
    # other. Keeping both meant two places to edit the next time the heuristic moves.

    def test_it_never_blocks(self, pf, monkeypatch, tmp_path):
        """Advisory means advisory: the same contract as questions 5 and 5b."""
        monkeypatch.setattr(pf, "BACKGROUND_MARKER", tmp_path / "m.json")
        monkeypatch.setattr(pf, "background_findings",
                            lambda: {"telemetry": ["t"], "credentials": ["a"],
                                     "versions": ["b"], "identity": ["c"]})
        assert pf.cmd_background(force=True) == 0

    def test_it_says_nothing_when_clean(self, pf, monkeypatch, tmp_path, capsys):
        """A check that speaks when there is nothing to say gets tuned out."""
        monkeypatch.setattr(pf, "BACKGROUND_MARKER", tmp_path / "m.json")
        monkeypatch.setattr(pf, "background_findings",
                            lambda: {"telemetry": [], "credentials": [], "versions": [], "identity": []})
        pf.cmd_background(force=True)
        assert capsys.readouterr().out == ""

    def test_it_suppresses_a_repeat_within_the_window(self, pf, monkeypatch, tmp_path,
                                                     capsys):
        marker = tmp_path / "m.json"
        monkeypatch.setattr(pf, "BACKGROUND_MARKER", marker)
        monkeypatch.setattr(pf, "background_findings",
                            lambda: {"telemetry": [], "credentials": ["x"], "versions": [], "identity": []})
        pf.cmd_background(force=True)
        assert "x" in capsys.readouterr().out
        pf.cmd_background()                      # not forced
        assert capsys.readouterr().out == ""

    def test_it_runs_again_once_the_window_passes(self, pf, monkeypatch, tmp_path,
                                                 capsys):
        import os as _os
        marker = tmp_path / "m.json"
        monkeypatch.setattr(pf, "BACKGROUND_MARKER", marker)
        monkeypatch.setattr(pf, "background_findings",
                            lambda: {"telemetry": [], "credentials": ["x"], "versions": [], "identity": []})
        pf.cmd_background(force=True)
        capsys.readouterr()
        stale = pf.time.time() - pf.BACKGROUND_TTL_SECONDS - 60
        _os.utime(marker, (stale, stale))
        pf.cmd_background()
        assert "x" in capsys.readouterr().out

    def test_an_unwritable_marker_is_not_an_error(self, pf, monkeypatch):
        """A cache we cannot write is not a reason to fail a check that never blocks."""
        monkeypatch.setattr(pf, "BACKGROUND_MARKER", Path("/proc/nope/m.json"))
        monkeypatch.setattr(pf, "background_findings",
                            lambda: {"telemetry": [], "credentials": [], "versions": [], "identity": []})
        assert pf.cmd_background(force=True) == 0

    def test_a_missing_binary_does_not_take_the_pass_down(self, pf, monkeypatch):
        """One broken tool must not cost us the other two families."""
        monkeypatch.setattr(pf.shutil, "which", lambda name: None)
        out = pf.background_findings()
        assert set(out) == {"telemetry", "credentials", "versions", "identity"}

    def test_run_never_raises(self, pf):
        code, out = pf._run(["definitely-not-a-real-binary-xyz"])
        assert code != 0 and isinstance(out, str)

    def test_version_drift_is_reported_in_both_directions(self, pf, monkeypatch):
        """Below the floor is unsupported; at or above the ceiling means either the
        tool moved on or our own requirements.txt is stale. Both worth saying."""
        monkeypatch.setattr(pf.shutil, "which", lambda n: "/usr/bin/databricks")
        monkeypatch.setattr(pf, "_run", lambda *a, **k: (0, "Databricks CLI v0.100.0"))
        assert any("below" in f for f in pf.check_tool_versions())
        monkeypatch.setattr(pf, "_run", lambda *a, **k: (0, "Databricks CLI v1.16.1"))
        assert any("ceiling" in f for f in pf.check_tool_versions())
        monkeypatch.setattr(pf, "_run", lambda *a, **k: (0, "Databricks CLI v0.240.0"))
        assert pf.check_tool_versions() == []

    def test_an_unset_git_email_is_reported_because_telemetry_leans_on_it(self, pf,
                                                                        monkeypatch):
        monkeypatch.setattr(pf, "_run", lambda cmd, **k: (1, "") if "git" in cmd[0]
                            else (1, ""))
        assert any("user.email" in f for f in pf.check_identity_coherence())

    def test_disagreeing_identities_are_reported(self, pf, monkeypatch):
        def fake(cmd, **k):
            if cmd[0] == "git":
                return 0, "kxy@capgroup.com"
            # The login now comes out of `gh auth status --json hosts`, reusing the
            # call the credential check already makes.
            return 0, _gh_json(login="RYQF_capgroup")
        monkeypatch.setattr(pf, "_run", fake)
        findings = pf.check_identity_coherence()
        assert any("kxy" in f and "ryqf" in f for f in findings)

    def test_agreeing_identities_are_silent(self, pf, monkeypatch):
        def fake(cmd, **k):
            if cmd[0] == "git":
                return 0, "ryqf@capgroup.com"
            return 0, _gh_json(login="RYQF_capgroup")
        monkeypatch.setattr(pf, "_run", fake)
        assert pf.check_identity_coherence() == []

    def test_the_agreeing_case_is_not_silent_by_accident(self, pf, monkeypatch):
        """Guard on the test above: an unresolved login skips the comparison
        entirely, so the assertion would pass without ever exercising agreement.
        Pinning that the login really is resolved."""
        def fake(cmd, **k):
            if cmd[0] == "git":
                return 0, "ryqf@capgroup.com"
            return 0, _gh_json(login="RYQF_capgroup")
        monkeypatch.setattr(pf, "_run", fake)
        assert pf.gh_active_account(fake(["gh"])[1])["login"] == "RYQF_capgroup"


class TestRblwReviewFindings:
    """Regressions from RBLW's review — mostly false OFFs and false ONs."""

    def test_truthy_accepts_the_spellings_users_actually_write(self, pf):
        """`TRUE` and `yes` read as OFF while telemetry was running."""
        for on in ("1", "true", "TRUE", "True", "yes", "on", " 1 "):
            assert pf._truthy(on) is True, on
        for off in ("0", "false", "no", "", None, "maybe"):
            assert pf._truthy(off) is False, off

    def test_an_unparseable_layer_is_unreadable_not_off(self, pf, tmp_path, monkeypatch):
        """Reporting OFF for a file nobody can parse sent the user to ask DevNext
        about a setting when the fault is their file's syntax.

        The harness is pinned by `_pin_environment_probes`, which this test relies
        on: the probe short-circuits to NOT_APPLICABLE off Claude Code, so without
        the pin it never reaches the parser on a VS Code machine at all. It used to
        carry its own inline pin, which nothing guarded -- deleting that one line was
        invisible from inside Claude Code and failed only for a VS Code reviewer,
        which is exactly how this test broke in the first place.
        """
        bad = tmp_path / "settings.json"
        bad.write_text('{"env": {"broken": }')
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [bad])
        r = pf.probe_claude_code_otel()
        assert r["verdict"] == pf.CC_OTEL_UNREADABLE
        assert r["problems"]

    def test_every_claude_verdict_has_remediation(self, pf):
        for name in dir(pf):
            if name.startswith("CC_OTEL_") and name != "CC_OTEL_REMEDIATION":
                v = getattr(pf, name)
                if isinstance(v, str):
                    assert v in pf.CC_OTEL_REMEDIATION, name

    def test_a_skipped_probe_is_not_a_dead_destination(self, pf, monkeypatch):
        """`None` means the probe was skipped. Treating it as falsy reported
        ON_BUT_NO_DESTINATION for a destination never tested."""
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [])
        monkeypatch.setattr(pf.os, "environ", {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOGS_EXPORTER": "otlp",
        })
        r = pf.probe_claude_code_otel(check_local_collector=False)
        assert r.get("no_destination") is not True
        assert r["verdict"] != pf.CC_OTEL_NO_DESTINATION

    def test_a_wrong_protocol_is_reported(self, pf, monkeypatch):
        """CC_OTEL_EXPECTED was declared and never consulted, so grpc against an
        http/protobuf collector reported ON with no problems."""
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOGS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://c.example.com/s/devnext",
        })
        assert any("PROTOCOL" in p for p in r["problems"])
        assert r["verdict"] == pf.CC_OTEL_MISCONFIGURED

    def test_the_source_segment_rule_is_scoped_to_coder(self, pf, monkeypatch):
        """The /s/<source> partition exists to separate DevNext sessions from real
        dev work, so the warning is meaningless on a laptop.

        The laptop comes from `_pin_environment_probes`. This used to set it up with
        two `delenv` calls plus `monkeypatch.setattr(pf.Path, "exists", ...)`, all
        three of which fed the real `in_coder_workspace()` that `_cc_env` then stubbed
        one line later -- so the setup was dead, and the test passed just as happily
        with the ambient state forced to Coder *and* `in_coder=True`.

        It asserts on `notes` as well as `problems` because the segment only ever
        reaches `notes` today: the `problems` assertion alone cannot fail, since
        `CC_SOURCE_SEGMENT` appears in production at the condition and at
        `notes.append` and nowhere else. Both are asserted so this keeps holding
        through the note-to-problem promotion the comment above the condition
        anticipates -- this is meant to be the test that stops it firing on laptops.
        """
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOGS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://c.example.com",
        })
        assert r.get("source_segment_missing") is None
        assert not any(pf.CC_SOURCE_SEGMENT in n for n in r["notes"])
        assert not any(pf.CC_SOURCE_SEGMENT in p for p in r["problems"])

    def test_constants_declared_for_checking_are_actually_checked(self, pf):
        """CC_OTEL_EXPECTED sat unused, which is how the protocol went unchecked.
        A declared expectation that nothing consults is worse than none."""
        import inspect
        # Not `"CC_OTEL_EXPECTED" in source`: that string also appears in a *comment*
        # in the same function, so deleting the real usage would leave this passing --
        # the same false-pass class already found twice on this branch. Comments are
        # stripped and the subscript is required, so only real consultation counts.
        source = inspect.getsource(pf.probe_claude_code_otel)
        code = "\n".join(ln for ln in source.splitlines()
                         if not ln.lstrip().startswith("#"))
        assert "CC_OTEL_EXPECTED[" in code, "declared but never consulted"


class TestSecretsAreNotEchoed:
    """This report is printed into a chat transcript, and
    OTEL_EXPORTER_OTLP_HEADERS is the documented home for a bearer token."""

    def test_headers_value_is_redacted(self, pf):
        out = pf.redact("OTEL_EXPORTER_OTLP_HEADERS", "Authorization=Bearer sekrit")
        assert "sekrit" not in out and "Bearer" not in out
        assert "redacted" in out

    def test_presence_is_still_visible(self, pf):
        assert "<empty>" == pf.redact("OTEL_EXPORTER_OTLP_HEADERS", "")
        assert "chars" in pf.redact("OTEL_EXPORTER_OTLP_HEADERS", "x")

    def test_diagnostic_values_are_not_redacted(self, pf):
        """Over-redaction would break the diagnosis this check exists for."""
        for key in list(pf.CC_OTEL_EXPECTED) + list(pf.CC_CONTENT_SWITCHES) + [
                pf.CC_TELEMETRY_KEY, pf.CC_OVER_COLLECTION_SWITCH]:
            assert pf.redact(key, "visible") == "visible", key


class TestEndpointProbeBadInput:
    def test_a_malformed_port_does_not_crash(self, pf):
        """urlparse().port raises ValueError on `https://host:abc`."""
        r = pf.probe_otel_endpoint("https://collector.example.com:abc")
        assert r["kind"] == "bad-url"
        assert r["reachable"] is False

    def test_a_non_http_scheme_is_rejected(self, pf):
        assert pf.probe_otel_endpoint("ftp://h/p")["kind"] == "bad-url"

    def test_garbage_is_rejected(self, pf):
        assert pf.probe_otel_endpoint("notaurl")["kind"] == "bad-url"


class TestClaudeCodeContentGuardrail:
    def test_all_four_switches_are_covered(self, pf):
        assert set(pf.CC_CONTENT_SWITCHES) == {
            "OTEL_LOG_USER_PROMPTS", "OTEL_LOG_ASSISTANT_RESPONSES",
            "OTEL_LOG_TOOL_CONTENT", "OTEL_LOG_RAW_API_BODIES",
        }

    def test_tool_details_is_not_treated_as_content(self, pf):
        """It is not a *content* switch, which is a narrower claim than it looks.

        OTEL_LOG_TOOL_DETAILS does not carry skill names — `skill.name`,
        `agent.name`, `plugin.name` and `marketplace.name` are unconditional
        attributes, so attribution needs no switch. What it adds is serialized
        tool arguments and bash command lines. It therefore sits outside
        CC_CONTENT_SWITCHES (it is not conversation or code content) while still
        being expected OFF, which CC_OVER_COLLECTION_SWITCH is what enforces.
        """
        assert "OTEL_LOG_TOOL_DETAILS" not in pf.CC_CONTENT_SWITCHES
        # ...and it is still not something we want on.
        assert pf.CC_OVER_COLLECTION_SWITCH == "OTEL_LOG_TOOL_DETAILS"

    def test_each_switch_alone_trips_the_verdict_only_when_routed_to_us(
            self, pf, monkeypatch):
        """The guardrail is now about ROUTING, not about the switch being on.

        A content switch is the enterprise's call. What Catalyst must never do is
        receive what it produces -- so the verdict fires when content logging is on
        AND the logs signal resolves to the Catalyst collector.
        """
        for switch in pf.CC_CONTENT_SWITCHES:
            leaking = _cc_env(pf, monkeypatch, {
                "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
                "OTEL_METRICS_EXPORTER": "otlp",
                "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "https://catalyst-otel.example.com",
                switch: "1",
            })
            assert leaking["verdict"] == pf.CC_OTEL_CONTENT_CAPTURE, switch
            assert leaking.get("content_leak") is True, switch

            elsewhere = _cc_env(pf, monkeypatch, {
                "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
                "OTEL_METRICS_EXPORTER": "otlp",
                "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://catalyst-otel.example.com/v1/metrics",
                "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "https://security-audit.example.com",
                switch: "1",
            })
            assert elsewhere["verdict"] != pf.CC_OTEL_CONTENT_CAPTURE, switch
            assert switch in elsewhere["content_switches_on"], switch

    def test_prompts_on_with_no_endpoint_is_not_a_catalyst_leak(self, pf, monkeypatch):
        """The live DevNext state: prompts logged, nowhere to send them.

        Content is being produced and dropped at the localhost default. That is
        wasteful and worth knowing, but it is not content arriving at Catalyst, so
        it must not read as our compliance problem.
        """
        r = _cc_env(pf, monkeypatch, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
            "OTEL_LOG_USER_PROMPTS": "1",
        }, port_open=False)
        assert r["verdict"] != pf.CC_OTEL_CONTENT_CAPTURE
        assert not r.get("content_leak")
        assert "OTEL_LOG_USER_PROMPTS" in r["content_switches_on"]

    def test_remediation_points_at_grc_not_at_a_local_edit(self, pf):
        text = pf.CC_OTEL_REMEDIATION[pf.CC_OTEL_CONTENT_CAPTURE]
        assert "Governance" in text

    def test_off_remediation_is_self_serve_not_a_handoff(self, pf):
        """Reversed deliberately, because the reasoning this test used to encode was
        wrong. It asserted "managed settings outrank the user, so telling them to edit
        it is wrong" -- true in general, false here: the managed policy sets none of
        the four keys Catalyst needs, so a user-scope write takes effect and nothing
        overrides it. Sending someone to another team for something they can fix in
        one command costs them a day and costs that team an interruption."""
        text = pf.CC_OTEL_REMEDIATION[pf.CC_OTEL_OFF]
        assert "claude-otel" in text
        assert "does not set these keys" in text
        assert "DevNext team" not in text


class TestSettingsLayerPrecedence:
    def test_managed_wins_over_user(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  {"CLAUDE_CODE_ENABLE_TELEMETRY": "1",
                                   "OTEL_EXPORTER_OTLP_ENDPOINT": "https://managed.example.com",
                                   "OTEL_METRICS_EXPORTER": "otlp"})
        user = _write_settings(tmp_path, "settings.json",
                               {"OTEL_EXPORTER_OTLP_ENDPOINT": "https://user.example.com"})
        r = _cc_env(pf, monkeypatch, {}, managed=managed, user=user)
        assert r["values"]["OTEL_EXPORTER_OTLP_ENDPOINT"] == "https://managed.example.com"
        assert "managed-settings.json" in r["sources"]["OTEL_EXPORTER_OTLP_ENDPOINT"]

    def test_source_is_reported_so_users_know_what_they_cannot_change(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  {"CLAUDE_CODE_ENABLE_TELEMETRY": "1",
                                   "OTEL_LOG_USER_PROMPTS": "1"})
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        # The switch is recorded with its source so the user can see they cannot
        # change it locally -- but with no endpoint it is not reaching Catalyst, so
        # it is not a content-capture verdict.
        assert "OTEL_LOG_USER_PROMPTS" in r["content_switches_on"]
        assert r["sources"]["OTEL_LOG_USER_PROMPTS"].endswith("managed-settings.json")

    def test_settings_files_win_over_process_env(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  {"CLAUDE_CODE_ENABLE_TELEMETRY": "1",
                                   "OTEL_METRICS_EXPORTER": "otlp",
                                   "OTEL_EXPORTER_OTLP_ENDPOINT": "https://managed.example.com"})
        r = _cc_env(pf, monkeypatch,
                    {"OTEL_EXPORTER_OTLP_ENDPOINT": "https://env.example.com"},
                    managed=managed)
        assert r["values"]["OTEL_EXPORTER_OTLP_ENDPOINT"] == "https://managed.example.com"


class TestClaudeCodeOtelIsAdvisory:
    def test_never_changes_the_exit_code(self, pf):
        ready = {
            "toolchain": {"python_ok": True, "deps_ok": True},
            "access": {"reachable": True, "catalogs": ["c"], "warehouses": [{"name": "w"}],
                       "catalogs_error": None, "warehouses_error": None},
        }
        for verdict in (pf.CC_OTEL_OFF, pf.CC_OTEL_CONTENT_CAPTURE,
                        pf.CC_OTEL_NO_DESTINATION):
            ready["cc_otel"] = {"verdict": verdict}
            assert pf.exit_code_for(ready) == 0, verdict


class TestManagedSettingsFragment:
    """Guards on `docs/telemetry/managed-settings-otel.json`.

    The fragment is copied by hand into a file owned by another team, so a defect
    in it is expensive to walk back. Nothing here talks to a collector.
    """

    FRAGMENT = REPO_ROOT / "docs" / "telemetry" / "managed-settings-otel.json"

    @staticmethod
    def _load(text):
        """Parse, recording every key seen rather than only the survivors."""
        import collections
        import json
        counts = collections.Counter()

        def hook(pairs):
            for key, _ in pairs:
                counts[key] += 1
            return dict(pairs)

        return json.loads(text, object_pairs_hook=hook), counts

    @property
    def _parsed(self):
        return self._load(self.FRAGMENT.read_text(encoding="utf-8"))

    @property
    def _env(self):
        doc, _ = self._parsed
        return {k: v for k, v in doc["env"].items() if not k.startswith("//")}

    def test_no_duplicate_keys(self):
        """The bug this test exists for.

        Commentary rides in `//`-prefixed keys, which are numbered by hand. A
        renumbering left two `//a13`..`//a19` runs in the same object; JSON keeps
        the last of each, so seven lines of explanation were silently discarded at
        parse time while the file still looked complete in a diff.
        """
        _doc, counts = self._parsed
        dupes = {k: n for k, n in counts.items() if n > 1}
        assert not dupes, f"duplicate keys lose their earlier value: {dupes}"

    def test_sets_the_metrics_signal_and_not_the_generic_one(self):
        """The generic variable is the fallback for every unset signal, so aiming
        it at the Catalyst collector would route prompt text here. The whole
        metrics-only guarantee rests on this one distinction."""
        env = self._env
        assert "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT" in env
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" not in env

    def test_sets_no_logs_destination_and_no_content_switch(self):
        """Content switches are the enterprise's call, and a logs destination is
        what would make them our problem."""
        env = self._env
        assert "OTEL_LOGS_EXPORTER" not in env
        assert "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT" not in env
        for switch in ("OTEL_LOG_USER_PROMPTS", "OTEL_LOG_ASSISTANT_RESPONSES",
                       "OTEL_LOG_TOOL_CONTENT", "OTEL_LOG_RAW_API_BODIES",
                       "OTEL_LOG_TOOL_DETAILS"):
            assert switch not in env, f"{switch} is not Catalyst's to set"

    def test_exports_metrics_or_the_attribution_never_arrives(self):
        """skill.name rides on cost.usage/token.usage. Without an exporter the
        endpoint is decoration -- which is exactly Finding 2 of AICAT-335."""
        assert "otlp" in self._env["OTEL_METRICS_EXPORTER"]

    def test_endpoint_is_a_catalyst_collector_preflight_will_recognise(self, pf):
        """preflight matches on a substring, so an endpoint that does not carry it
        would be classified as somebody else's collector."""
        endpoint = self._env["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"]
        assert pf.CATALYST_COLLECTOR_HINT in endpoint

    def test_resource_attributes_carry_a_producer_tag(self):
        """Distinguishing Claude Code from VS Code Copilot Chat. Copilot sends
        service.name=copilot-chat unprompted; Claude Code's value is unverified,
        so the tag is explicit rather than inferred."""
        attrs = dict(
            pair.split("=", 1)
            for pair in self._env["OTEL_RESOURCE_ATTRIBUTES"].split(",")
        )
        assert attrs["telemetry.producer"] == "claude-code"

    def test_resource_attributes_parse_as_the_w3c_baggage_style_list(self):
        """A space or a stray semicolon makes the whole string unparseable, and
        the exporter drops it without complaining."""
        raw = self._env["OTEL_RESOURCE_ATTRIBUTES"]
        assert " " not in raw and ";" not in raw
        for pair in raw.split(","):
            assert pair.count("=") == 1 and all(pair.split("="))


class TestPerSignalProtocol:
    """The metrics-specific protocol must be read in preference to the generic one.

    Reading only `OTEL_EXPORTER_OTLP_PROTOCOL` left the fragment this repo
    publishes unvalidated, because that fragment sets the metrics-specific
    variable. A wrong protocol is total, silent data loss: the collector cannot
    decode what arrives.
    """

    BASE = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://catalyst-otel.x.invalid/v1/metrics"}

    def test_metrics_specific_protocol_mismatch_is_caught(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  dict(self.BASE, OTEL_EXPORTER_OTLP_METRICS_PROTOCOL="grpc"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert r["verdict"] == pf.CC_OTEL_MISCONFIGURED
        assert any("METRICS_PROTOCOL" in p and "grpc" in p for p in r["problems"]), r["problems"]

    def test_the_published_protocol_is_accepted(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(
            tmp_path, "managed-settings.json",
            dict(self.BASE, OTEL_EXPORTER_OTLP_METRICS_PROTOCOL="http/protobuf"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert r["verdict"] == pf.CC_OTEL_ON, r["problems"]

    def test_metrics_specific_wins_over_a_wrong_generic(self, pf, monkeypatch, tmp_path):
        """Generic grpc + metrics http/protobuf: metrics is what carries our data."""
        managed = _write_settings(
            tmp_path, "managed-settings.json",
            dict(self.BASE, OTEL_EXPORTER_OTLP_PROTOCOL="grpc",
                 OTEL_EXPORTER_OTLP_METRICS_PROTOCOL="http/protobuf"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert r["verdict"] == pf.CC_OTEL_ON, r["problems"]

    def test_generic_is_still_used_when_metrics_specific_is_absent(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  dict(self.BASE, OTEL_EXPORTER_OTLP_PROTOCOL="grpc"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert any("OTEL_EXPORTER_OTLP_PROTOCOL" in p for p in r["problems"])

    def test_default_port_follows_the_metrics_protocol(self, pf, monkeypatch, tmp_path):
        """grpc falls back to 4317, not 4318 -- probing the wrong port would report
        a live collector as dead, or the reverse."""
        seen = []
        monkeypatch.setattr(pf, "_port_open", lambda h, p, **k: seen.append((h, p)) or False)
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  {"CLAUDE_CODE_ENABLE_TELEMETRY": "1",
                                   "OTEL_METRICS_EXPORTER": "otlp",
                                   "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL": "grpc"})
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [managed])
        monkeypatch.setattr(pf.os, "environ", {})
        pf.probe_claude_code_otel()
        assert seen == [pf.OTLP_GRPC_DEFAULT]


class TestContentLeakRequiresAnActualExport:
    """`CONTENT_CAPTURE_ENABLED` is the verdict that sends someone to GRC, so a
    false positive is expensive. An endpoint is not an export."""

    LEAKY = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
             "OTEL_LOG_USER_PROMPTS": "1",
             "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT": "https://catalyst-otel.x.invalid"}

    def test_logs_exporter_none_is_not_a_leak(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  dict(self.LEAKY, OTEL_LOGS_EXPORTER="none"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert not r.get("content_leak")
        assert r["verdict"] != pf.CC_OTEL_CONTENT_CAPTURE

    def test_but_the_misrouting_is_still_reported_as_a_note(self, pf, monkeypatch, tmp_path):
        """Inert today, live the moment someone re-enables the exporter."""
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  dict(self.LEAKY, OTEL_LOGS_EXPORTER="none"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert any("Catalyst collector" in n for n in r["notes"]), r["notes"]

    def test_logs_exporter_otlp_is_a_leak(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json",
                                  dict(self.LEAKY, OTEL_LOGS_EXPORTER="otlp"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert r["verdict"] == pf.CC_OTEL_CONTENT_CAPTURE

    def test_an_unset_exporter_still_reports_the_leak(self, pf, monkeypatch, tmp_path):
        """Deliberately conservative. Guessing 'probably not exported' from an
        absent variable would mean missing the one thing this check is for."""
        managed = _write_settings(tmp_path, "managed-settings.json", dict(self.LEAKY))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert r["verdict"] == pf.CC_OTEL_CONTENT_CAPTURE

    def test_the_endpoint_is_redacted_in_the_problem_text(self, pf, monkeypatch, tmp_path):
        """cmd_otel prints problems into a chat transcript."""
        managed = _write_settings(
            tmp_path, "managed-settings.json",
            dict(self.LEAKY, OTEL_LOGS_EXPORTER="otlp",
                 OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="https://u:sh3cret@catalyst-otel.x.invalid/v1/logs"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        joined = " ".join(r["problems"])
        assert "sh3cret" not in joined and "u:" not in joined
        assert "catalyst-otel.x.invalid/v1/logs" in joined


class TestRedactUrl:
    def test_userinfo_is_dropped(self, pf):
        out = pf.redact_url("https://user:tok@host.invalid/v1/logs")
        assert "tok" not in out and "user" not in out
        assert "host.invalid/v1/logs" in out and "credentials" in out

    def test_query_string_is_dropped(self, pf):
        out = pf.redact_url("https://host.invalid/v1/logs?api_key=abc")
        assert "abc" not in out and "query string hidden" in out

    def test_host_port_and_path_survive_because_they_are_the_answer(self, pf):
        assert pf.redact_url("https://h.invalid:4318/v1/logs") == "https://h.invalid:4318/v1/logs"

    def test_a_non_url_is_not_echoed_verbatim(self, pf):
        """No structure to trust means no basis for deciding it is safe to print."""
        assert pf.redact_url("sh3cret-looking-junk") == "<unparseable endpoint>"


class TestToolRangeComesFromRequirements:
    """The range is declared in `skills/requirements.txt`, which says in as many
    words that it is read as text. A second copy goes stale silently."""

    def test_reads_the_commented_databricks_line(self, pf):
        assert pf.read_tool_range("databricks") == (">=0.218.0", "<1.0.0")

    def test_unknown_tool_is_none_not_a_guess(self, pf):
        assert pf.read_tool_range("nonesuch") is None

    def test_a_missing_declaration_is_none_rather_than_a_default(self, pf, tmp_path):
        """Inventing a range would report drift against a number nobody published."""
        empty = tmp_path / "requirements.txt"
        empty.write_text("# nothing here\nrequests>=2.0\n")
        assert pf.read_tool_range("databricks", requirements=empty) is None

    def test_an_uncommented_line_is_read_too(self, pf, tmp_path):
        """It is commented out today for a packaging reason, not forever."""
        req = tmp_path / "requirements.txt"
        req.write_text("databricks-cli>=0.300.0,<2.0.0\n")
        assert pf.read_tool_range("databricks", requirements=req) == (">=0.300.0", "<2.0.0")

    def test_an_unreadable_file_is_none_not_a_traceback(self, pf, tmp_path):
        assert pf.read_tool_range("databricks", requirements=tmp_path / "nope.txt") is None

    def test_the_range_is_not_hard_coded_anywhere(self, pf):
        """The duplication this replaced. A literal here would drift again."""
        src = pathlib.Path(pf.__file__).read_text() if getattr(pf, "__file__", None) else SCRIPT.read_text()
        assert "0.218.0" not in src, "the range is back in the source"


class TestFailedVersionProbeIsNotHealthy:
    """A probe that fails is not a pass -- that is the false-green this pass exists
    to remove."""

    def _run_returns(self, pf, monkeypatch, code, out, which=True):
        monkeypatch.setattr(pf.shutil, "which", lambda n: "/usr/bin/databricks" if which else None)
        monkeypatch.setattr(pf, "_run", lambda *a, **k: (code, out))

    def test_nonzero_exit_is_reported(self, pf, monkeypatch):
        self._run_returns(pf, monkeypatch, 1, "boom")
        findings = pf.check_tool_versions()
        assert findings and "exited 1" in findings[0]

    def test_unparseable_output_is_reported(self, pf, monkeypatch):
        self._run_returns(pf, monkeypatch, 0, "databricks (unknown build)")
        findings = pf.check_tool_versions()
        assert findings and "no recognisable version" in findings[0]

    def test_a_good_version_is_still_silent(self, pf, monkeypatch):
        self._run_returns(pf, monkeypatch, 0, "Databricks CLI v0.287.0")
        assert pf.check_tool_versions() == []

    def test_below_the_floor_is_reported(self, pf, monkeypatch):
        self._run_returns(pf, monkeypatch, 0, "Databricks CLI v0.100.0")
        findings = pf.check_tool_versions()
        assert findings and "below the documented" in findings[0]

    def test_no_databricks_installed_is_not_a_finding(self, pf, monkeypatch):
        self._run_returns(pf, monkeypatch, 0, "", which=False)
        assert pf.check_tool_versions() == []

    def test_a_missing_declared_range_is_reported(self, pf, monkeypatch):
        self._run_returns(pf, monkeypatch, 0, "Databricks CLI v0.287.0")
        monkeypatch.setattr(pf, "read_tool_range", lambda *a, **k: None)
        findings = pf.check_tool_versions()
        assert findings and "no longer declares" in findings[0]


class TestNotesAreRendered:
    """A recorded-but-never-printed field is a discarded field.

    So these assert on **stdout**, not on the returned dict. The class previously
    requested `capsys` and never read it, which meant the claim in its own name was
    untested for one of the two renderers: deleting the note loop from `cmd_otel`
    left every test green, silently stopping `/dplc-preflight otel` from printing
    both of its invisible-failure warnings.
    """

    MANAGED = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1",
               "OTEL_METRICS_EXPORTER": "otlp",
               "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT":
                   "https://catalyst-otel.x.invalid/v1/metrics"}

    def _probe(self, pf, monkeypatch, tmp_path, endpoint=None):
        values = dict(self.MANAGED)
        if endpoint is not None:
            values["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] = endpoint
        managed = _write_settings(tmp_path, "managed-settings.json", values)
        return _cc_env(pf, monkeypatch, {}, managed=managed, in_coder=True)

    def test_source_segment_note_reaches_the_report(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path)
        assert r.get("source_segment_missing")
        assert any(pf.CC_SOURCE_SEGMENT in n for n in r["notes"])

    def test_an_endpoint_that_has_the_segment_is_not_flagged(self, pf, monkeypatch, tmp_path):
        """The third term of the gate, which nothing reached.

        Mutating `if endpoint and in_coder_workspace() and CC_SOURCE_SEGMENT not in
        endpoint:` to drop the last clause -- i.e. flag *every* Coder endpoint,
        correctly-configured ones included -- left all 231 tests green. Deleting
        every `/s/devnext` literal from this file did too. So `/dplc-preflight` could
        tell a correctly-configured DevNext workspace its endpoint was wrong, and the
        suite would say nothing.
        """
        r = self._probe(
            pf, monkeypatch, tmp_path,
            endpoint=f"https://catalyst-otel.x.invalid{pf.CC_SOURCE_SEGMENT}/v1/metrics")
        assert r.get("source_segment_missing") is None
        assert not any(pf.CC_SOURCE_SEGMENT in n for n in r["notes"])

    def test_a_note_never_changes_the_verdict(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path)
        assert r["notes"] and r["verdict"] == pf.CC_OTEL_ON

    def test_the_note_is_printed_by_cmd_otel(self, pf, monkeypatch, tmp_path, capsys):
        """`cmd_otel`'s note loop, which had no coverage at all.

        `cmd_check`'s loop is covered (mutating it to `[]` fails a test);
        `cmd_otel`'s was not (mutating it to `[]` failed nothing). Both print the
        same notes, and both notes exist to warn about failures that are otherwise
        invisible -- a missing `/s/<source>` segment, and logs pointing at Catalyst
        with the exporter off. A warning that is not printed is not a warning.
        """
        managed = _write_settings(tmp_path, "managed-settings.json", dict(self.MANAGED))
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [managed])
        monkeypatch.setattr(pf, "_port_open", lambda *a, **k: False)
        monkeypatch.setattr(pf, "in_coder_workspace", lambda: True)
        monkeypatch.setattr(pf.os, "environ", {})
        monkeypatch.setattr(pf, "probe_otel", lambda: {
            "verdict": pf.OTEL_NOT_CONFIGURED, "settings_path": None,
            "searched": [], "identity": None, "problems": [], "values": {}})

        pf.cmd_otel(probe_endpoint=False)
        out = capsys.readouterr().out

        assert f"note: the endpoint has no {pf.CC_SOURCE_SEGMENT}" in out, (
            "cmd_otel dropped the note; the probe recorded it and nobody saw it"
        )

    def test_every_probe_path_returns_a_notes_key(self, pf, monkeypatch):
        """Renderers do `for n in cc["notes"]`; a missing key is a KeyError in the
        one code path that was working."""
        monkeypatch.setattr(pf, "detect_harness", lambda: "copilot")
        assert "notes" in pf.probe_claude_code_otel()


class TestInCoderWorkspaceReadsItsInputs:
    """Direct coverage of `in_coder_workspace`, because `_pin_environment_probes`
    stubs it everywhere else.

    Without this class the function is unguarded: mutating its whole body to
    `return True` or `return False` left all 231 tests green, so dropping the
    `CODER_AGENT_TOKEN` clause, inverting the `bool()`, or typo'ing
    `CODER_WORKSPACE_NAME` all shipped silently. The consequence is operational --
    DevNext gets the `/s/<source>` note on every laptop, or on no Coder workspace at
    all.

    Tested at the boundary rather than through a caller: the function's inputs are
    two environment variables and one filesystem path, all three of which a test can
    set for real. `py-test-007` exists for exactly this -- the seam is available, so
    there is no reason to assert against a stub of our own code.

    Each clause gets its own test, because an `or` chain is where a dropped term
    hides: a single positive case passes with any one clause working.
    """

    MANAGED = "/etc/claude-code/managed-settings.json"

    @pytest.fixture(autouse=True)
    def _clean_machine(self, pf, monkeypatch):
        """Start each test from a known-negative machine.

        The three real inputs are cleared rather than assumed absent, because this
        suite does run on DevNext workspaces where all three are present -- which is
        the coupling this PR is about.
        """
        monkeypatch.delenv("CODER_WORKSPACE_NAME", raising=False)
        monkeypatch.delenv("CODER_AGENT_TOKEN", raising=False)
        monkeypatch.setattr(pf.Path, "exists", lambda self: False)

    def test_a_bare_machine_is_not_a_coder_workspace(self, real_probes):
        assert real_probes["in_coder_workspace"]() is False

    def test_the_workspace_name_is_enough(self, real_probes, monkeypatch):
        monkeypatch.setenv("CODER_WORKSPACE_NAME", "oz-dev-ryqf")
        assert real_probes["in_coder_workspace"]() is True

    def test_the_agent_token_alone_is_enough(self, real_probes, monkeypatch):
        """Second clause, on its own. A Coder workspace exports the token without
        always exporting the name, so a check on the name alone would miss it."""
        monkeypatch.setenv("CODER_AGENT_TOKEN", "t")
        assert real_probes["in_coder_workspace"]() is True

    def test_managed_settings_alone_is_enough(self, pf, real_probes, monkeypatch):
        """Third clause, and the one env cannot reach -- a DevNext workspace is
        identified by the managed policy file even with no Coder variables set."""
        managed = self.MANAGED  # not `self.MANAGED` inside the lambda: `self` there
        monkeypatch.setattr(pf.Path, "exists",  # is the Path instance, not the test
                            lambda p: str(p) == managed)
        assert real_probes["in_coder_workspace"]() is True

    def test_an_empty_value_does_not_count(self, real_probes, monkeypatch):
        """`bool()` not `is not None`: an exported-but-empty variable is how a
        half-configured shell looks, and it is not a Coder workspace."""
        monkeypatch.setenv("CODER_WORKSPACE_NAME", "")
        monkeypatch.setenv("CODER_AGENT_TOKEN", "")
        assert real_probes["in_coder_workspace"]() is False


class TestTheEnvironmentIsPinnedRegardlessOfWhereThisRuns:
    """Guard on `_pin_environment_probes`. Three tests used to assert against
    whichever machine ran them -- green on a Coder workspace under Claude Code, red
    on a macOS VS Code checkout.

    These assert the pin holds **against the real machine**, by setting the
    environment the unpinned functions would read. An earlier version of this class
    set up its "ambient" side with a second `monkeypatch.setattr` on the same
    function, so it compared a stub to a stub: it passed against a conditional pin
    that fired only when a parameter was passed -- i.e. against a default that merely
    looked pinned -- and would have kept passing if the helper were refactored to set
    `CODER_WORKSPACE_NAME` instead of stubbing.
    """

    ENV = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1",
           "OTEL_METRICS_EXPORTER": "otlp",
           "OTEL_EXPORTER_OTLP_ENDPOINT": "https://collector.example.com"}

    # The ambient values go **inside the env dict**, not through `monkeypatch.setenv`.
    #
    # `_cc_env` does `monkeypatch.setattr(pf.os, "environ", env)`, and `pf.os is os`,
    # so it swaps the process-global `os.environ` for this plain dict. Any `setenv` or
    # `delenv` written before that call is invisible to the code under test -- it
    # silently no-ops.
    #
    # That bit these two tests. An earlier version used `setenv`, and both did fail
    # when the pin was removed -- but only because *this* machine has
    # `/etc/claude-code/managed-settings.json`, the third thing `in_coder_workspace`
    # reads. On a laptop they would have passed with the pin gone: a guard against
    # environment-dependence that was itself environment-dependent.

    def test_a_real_coder_workspace_does_not_leak_in(self, pf, monkeypatch):
        """The environment says Coder; the pinned default must still say laptop."""
        r = _cc_env(pf, monkeypatch,
                    dict(self.ENV, CODER_WORKSPACE_NAME="oz-dev-ryqf",
                         CODER_AGENT_TOKEN="t"))
        assert r.get("source_segment_missing") is None

    def test_an_explicit_true_overrides_the_pin(self, pf, monkeypatch):
        """The documented override, asserted against the pin rather than a stub."""
        r = _cc_env(pf, monkeypatch, dict(self.ENV), in_coder=True)
        assert r.get("source_segment_missing") is True

    def test_the_harness_is_pinned_regardless_of_where_this_runs(self, pf, monkeypatch):
        """Exact verdict, not `!=` one of seven. With `!= CC_OTEL_NOT_CLAUDE_CODE`,
        removing the `os.environ` patch from `_cc_env` made the probe read the real
        machine and return `OFF` -- and this test still passed.

        `TERM_PROGRAM=vscode` with no Claude markers is what an unpinned
        `detect_harness` answers `"vscode"` to, which short-circuits the probe to
        `NOT_APPLICABLE`.
        """
        r = _cc_env(pf, monkeypatch, dict(self.ENV, TERM_PROGRAM="vscode"))
        assert r["verdict"] == pf.CC_OTEL_ON


class TestPerSignalEndpointNeedsItsSignalPath:
    """The one place the two endpoint variables genuinely differ.

    `OTEL_EXPORTER_OTLP_ENDPOINT` is a base URL and the exporter appends
    `/v1/metrics`. `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` is used **as-is**. So a
    host-only per-signal endpoint POSTs to `/`, which the Catalyst collector
    answers 404 -- measured, not assumed: `POST /` -> 404 and `POST /v1/metrics`
    -> 200. Every batch is rejected while the config still reads as correct.
    """

    BASE = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp"}

    def _probe(self, pf, monkeypatch, tmp_path, endpoint):
        managed = _write_settings(
            tmp_path, "managed-settings.json",
            dict(self.BASE, OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=endpoint))
        return _cc_env(pf, monkeypatch, {}, managed=managed)

    def test_host_only_per_signal_endpoint_is_a_problem(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path, "https://catalyst-otel.x.invalid")
        assert r["verdict"] == pf.CC_OTEL_MISCONFIGURED
        assert any("/v1/metrics" in p for p in r["problems"]), r["problems"]

    def test_a_trailing_slash_does_not_hide_it(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path, "https://catalyst-otel.x.invalid/")
        assert any("/v1/metrics" in p for p in r["problems"]), r["problems"]

    def test_the_full_path_is_accepted(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path,
                        "https://catalyst-otel.x.invalid/v1/metrics")
        assert r["verdict"] == pf.CC_OTEL_ON, r["problems"]

    def test_a_trailing_slash_after_the_path_is_accepted(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path,
                        "https://catalyst-otel.x.invalid/v1/metrics/")
        assert r["verdict"] == pf.CC_OTEL_ON, r["problems"]

    def test_the_generic_endpoint_is_not_required_to_carry_a_path(self, pf, monkeypatch, tmp_path):
        """The exporter appends the signal path to the generic variable, so
        demanding it there would flag a correct configuration."""
        managed = _write_settings(
            tmp_path, "managed-settings.json",
            dict(self.BASE, OTEL_EXPORTER_OTLP_ENDPOINT="https://catalyst-otel.x.invalid"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert not any("/v1/metrics" in p for p in r["problems"]), r["problems"]
        assert r["verdict"] == pf.CC_OTEL_ON

    def test_the_published_fragment_carries_the_path(self):
        """The fragment shipped without it, so `ON` was reported for a config that
        would have 404ed every batch in production."""
        import json
        frag = REPO_ROOT / "docs" / "telemetry" / "managed-settings-otel.json"
        env = json.loads(frag.read_text(encoding="utf-8"))["env"]
        endpoint = env["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"]
        assert endpoint.rstrip("/").endswith("/v1/metrics"), endpoint


class TestCheckReportNamesTheDestination:
    """`5b` printed only the generic keys, so the metrics-only policy produced an
    `ON` verdict that never said where metrics were going -- the one fact you need
    in order to diagnose it.

    Drives the real `cmd_check` with the leaf probes stubbed, so `gather()` builds
    the state exactly as it does in production. A hand-built state dict would drift
    from the real shape and agree with itself while the CLI differed.
    """

    METRICS = "https://catalyst-otel.x.invalid/v1/metrics"

    def _out(self, pf, monkeypatch, capsys, tmp_path, values, notes=None,
             verdict=None):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(pf, "probe_toolchain", lambda: {
            "python_version": "3.13", "python_ok": True, "python_too_new": False,
            "missing_imports": [], "deps_ok": True, "databricks_cli": True})
        monkeypatch.setattr(pf, "probe_access", lambda: {
            "reachable": True, "reason": None, "identity": "u@capgroup.com",
            "client": "databricks-sdk", "warehouses": [], "catalogs": [],
            "catalogs_error": None, "warehouses_error": None})
        monkeypatch.setattr(pf, "probe_claude_code_otel", lambda **k: {
            "verdict": verdict or pf.CC_OTEL_ON, "harness": "claude-code",
            "values": values,
            "sources": {k2: "process environment" for k2 in values},
            "problems": [], "notes": notes or []})
        pf.cmd_check(write=False)
        return capsys.readouterr().out

    # --- the advisory gate ---------------------------------------------------
    #
    # `if cc["verdict"] not in (CC_OTEL_NOT_CLAUDE_CODE, CC_OTEL_ON):` had no
    # coverage at either end: both single-term mutations left the suite green. The
    # structurally identical gate in `check_telemetry` *is* covered, which is what
    # made the gap easy to miss.

    HEALTHY = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp"}

    # The `Also:` prefix, not the bare phrase: the remediation line for a healthy
    # machine also reads "Claude Code usage reporting is configured", so a substring
    # match on the phrase alone can never distinguish advisory from remediation.
    ADVISORY = "Also:    Claude Code usage reporting"

    def test_a_healthy_machine_gets_no_advisory(self, pf, monkeypatch, capsys, tmp_path):
        """Drop `CC_OTEL_ON` from the tuple and a correctly-configured machine is
        told its reporting needs attention -- advice that is both wrong and
        unactionable."""
        out = self._out(pf, monkeypatch, capsys, tmp_path,
                        dict(self.HEALTHY, OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=self.METRICS))
        assert self.ADVISORY not in out

    def test_a_copilot_only_machine_gets_no_advisory(self, pf, monkeypatch, capsys, tmp_path):
        """The other end of the same tuple. `NOT_APPLICABLE` means "not running under
        this harness", so advising on it sends every VS Code user to fix something
        that does not apply to them."""
        out = self._out(pf, monkeypatch, capsys, tmp_path, {},
                        verdict=pf.CC_OTEL_NOT_CLAUDE_CODE)
        assert self.ADVISORY not in out

    def test_a_broken_machine_does_get_an_advisory(self, pf, monkeypatch, capsys, tmp_path):
        """The positive case, so the two tests above cannot be satisfied by deleting
        the advisory entirely."""
        out = self._out(pf, monkeypatch, capsys, tmp_path, {},
                        verdict=pf.CC_OTEL_NO_DESTINATION)
        assert f"{self.ADVISORY} is ON_BUT_NO_DESTINATION" in out
        assert "advisory, does not affect readiness" in out

    def test_the_per_signal_endpoint_appears(self, pf, monkeypatch, capsys, tmp_path):
        out = self._out(pf, monkeypatch, capsys, tmp_path, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": self.METRICS})
        assert "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT" in out
        assert "catalyst-otel.x.invalid/v1/metrics" in out

    def test_it_says_where_each_signal_resolves(self, pf, monkeypatch, capsys, tmp_path):
        """Per-signal beats generic, and which wins is not obvious from a key list."""
        out = self._out(pf, monkeypatch, capsys, tmp_path, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": self.METRICS,
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://enterprise.x.invalid"})
        assert f"metrics resolve to: {self.METRICS}" in out
        assert "logs resolve to:    https://enterprise.x.invalid" in out

    def test_unset_logs_are_named_as_the_discarded_default(self, pf, monkeypatch, capsys, tmp_path):
        """The live DevNext case: prompt logs collected and dropped on localhost."""
        out = self._out(pf, monkeypatch, capsys, tmp_path, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": self.METRICS})
        assert "logs resolve to:    the localhost default" in out

    def test_credentials_in_an_endpoint_are_not_printed(self, pf, monkeypatch, capsys, tmp_path):
        out = self._out(pf, monkeypatch, capsys, tmp_path, {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT":
                "https://u:sh3cret@c.invalid/v1/metrics"})
        assert "sh3cret" not in out

    def test_notes_reach_this_report_too(self, pf, monkeypatch, capsys, tmp_path):
        """`cmd_otel` rendered notes and `cmd_check` did not, so the same field was
        visible from one entry point and invisible from the other."""
        out = self._out(pf, monkeypatch, capsys, tmp_path,
                        {"CLAUDE_CODE_ENABLE_TELEMETRY": "1",
                         "OTEL_METRICS_EXPORTER": "otlp",
                         "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": self.METRICS},
                        notes=["a note worth reading"])
        assert "note: a note worth reading" in out


class TestRedactUrlSurvivesAMalformedPort:
    """`urlsplit` accepts `https://host:abc` and defers the error to `.port`.

    This helper runs *before* `probe_otel_endpoint` gets a chance to return its
    `bad-url` diagnostic, so raising here crashed the very command whose job is to
    explain the malformed endpoint.
    """

    def test_an_invalid_port_does_not_raise(self, pf):
        assert pf.redact_url("https://collector:abc/v1/metrics") == "<unparseable endpoint>"

    def test_probe_still_reports_bad_url_rather_than_crashing(self, pf):
        r = pf.probe_otel_endpoint("https://collector:abc/v1/metrics")
        assert r["kind"] == "bad-url" and not r["reachable"]

    def test_the_bad_url_detail_does_not_echo_the_input(self, pf):
        """The malformed-endpoint branch is exactly where a mistyped URL with a
        credential in it ends up, and it was the one quoting the input verbatim."""
        r = pf.probe_otel_endpoint("https://u:sh3cret@collector:abc/v1/metrics")
        assert "sh3cret" not in r["detail"]

    def test_a_non_http_scheme_detail_is_also_sanitised(self, pf):
        r = pf.probe_otel_endpoint("ftp://u:sh3cret@collector/v1/metrics")
        assert r["kind"] == "bad-url" and "sh3cret" not in r["detail"]

    def test_an_unresolvable_host_detail_carries_no_credentials(self, pf):
        r = pf.probe_otel_endpoint("https://u:sh3cret@nx.invalid.invalid/v1/metrics")
        assert "sh3cret" not in r["detail"]


class TestOtelRendererRedactsEndpoints:
    """`cmd_otel` printed every value through `redact()`, which keys off secret-
    hinting *names* -- and `..._ENDPOINT` is not one. So sanitising the leak
    message still let a userinfo credential through three lines above it."""

    def test_endpoint_credentials_are_not_printed(self, pf, monkeypatch, capsys, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json", {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT":
                "https://u:sh3cret@catalyst-otel.x.invalid/v1/metrics"})
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [managed])
        monkeypatch.setattr(pf.os, "environ", {})
        monkeypatch.setattr(pf, "probe_otel", lambda: {
            "verdict": pf.OTEL_NOT_CONFIGURED, "settings_path": None, "searched": [],
            "values": {}, "problems": [], "identity": None})
        pf.cmd_otel()
        out = capsys.readouterr().out
        assert "sh3cret" not in out
        assert "catalyst-otel.x.invalid/v1/metrics" in out


class TestGenericEndpointWarningIsGated:
    """The warning exists because logs *fall back* to the generic endpoint. Once a
    logs-specific endpoint is set they do not -- so firing then reported
    ON_BUT_MISCONFIGURED for a configuration that had already taken the advice."""

    BASE = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_LOG_USER_PROMPTS": "1",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://enterprise.x.invalid"}

    def test_no_warning_when_a_logs_endpoint_overrides_the_generic(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json", dict(
            self.BASE, OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="https://enterprise-logs.x.invalid"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert not any("generic OTEL_EXPORTER_OTLP_ENDPOINT" in p for p in r["problems"]), \
            r["problems"]
        assert r["verdict"] == pf.CC_OTEL_ON

    def test_the_warning_still_fires_without_one(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json", dict(self.BASE))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert any("generic OTEL_EXPORTER_OTLP_ENDPOINT" in p for p in r["problems"])

    def test_a_logs_endpoint_aimed_at_catalyst_is_still_a_leak_not_a_pass(self, pf, monkeypatch, tmp_path):
        """Overriding the generic endpoint does not help if the override points here."""
        managed = _write_settings(tmp_path, "managed-settings.json", dict(
            self.BASE, OTEL_LOGS_EXPORTER="otlp",
            OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="https://catalyst-otel.x.invalid/v1/logs"))
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert r["verdict"] == pf.CC_OTEL_CONTENT_CAPTURE


class TestIdentityReusesTheAuthCall:
    """The identity check used `gh api user` -- a second network round trip in the
    pass documented as quiet. It now reuses the `gh auth status` output the
    credential check already fetched."""

    def test_login_is_parsed_from_auth_status(self, pf):
        assert pf.gh_active_account(_gh_json(login="RYQF_capgroup"))["login"] == "RYQF_capgroup"

    def test_absent_login_is_empty_not_a_guess(self, pf):
        """`{}` means gh answered and holds nothing; `None` means unreadable."""
        assert pf.gh_active_account('{"hosts": {}}') == {}
        assert pf.gh_active_account("X Failed to log in") is None
        assert pf.gh_active_account("") is None

    def test_gh_api_user_is_never_called(self, pf, monkeypatch):
        calls = []

        def fake_run(cmd, **kw):
            calls.append(cmd)
            if cmd[:3] == ["gh", "auth", "status"]:
                return 0, _gh_json(login="ryqf")
            if cmd[:2] == ["git", "config"]:
                return 0, "ryqf@capgroup.com"
            return 0, ""

        monkeypatch.setattr(pf, "_run", fake_run)
        monkeypatch.setattr(pf.shutil, "which", lambda n: f"/usr/bin/{n}")
        pf.check_identity_coherence()
        assert not any("api" in c for c in calls), calls

    def test_auth_status_runs_once_across_both_checks(self, pf, monkeypatch):
        """Two checks need it and it is a network call."""
        calls = []

        def fake_run(cmd, **kw):
            calls.append(tuple(cmd))
            if cmd[:3] == ["gh", "auth", "status"]:
                return 0, _gh_json(login="ryqf")
            if cmd[:2] == ["git", "config"]:
                return 0, "ryqf@capgroup.com"
            if cmd[:2] == ["keeper-env", "doctor"]:
                return 0, "Session credentials: present\nDevice finalized: yes"
            return 0, ""

        monkeypatch.setattr(pf, "_run", fake_run)
        monkeypatch.setattr(pf.shutil, "which", lambda n: f"/usr/bin/{n}")
        pf.check_credential_liveness()
        pf.check_identity_coherence()
        assert sum(1 for c in calls if c[:3] == ("gh", "auth", "status")) == 1, calls

    def test_a_mismatch_is_still_detected_through_the_shared_call(self, pf, monkeypatch):
        def fake_run(cmd, **kw):
            if cmd[:3] == ["gh", "auth", "status"]:
                return 0, _gh_json(login="someoneelse")
            if cmd[:2] == ["git", "config"]:
                return 0, "ryqf@capgroup.com"
            return 0, ""

        monkeypatch.setattr(pf, "_run", fake_run)
        monkeypatch.setattr(pf.shutil, "which", lambda n: f"/usr/bin/{n}")
        findings = pf.check_identity_coherence()
        assert any("someoneelse" in f for f in findings), findings

    def test_a_failing_account_does_not_supply_the_identity(self, pf, monkeypatch):
        """A broken account's login must not be compared against git user.email --
        that reports an identity mismatch when the real problem is auth."""
        def fake_run(cmd, **kw):
            if cmd[:3] == ["gh", "auth", "status"]:
                return 0, _gh_json(login="someoneelse", state="error")
            if cmd[:2] == ["git", "config"]:
                return 0, "ryqf@capgroup.com"
            return 0, ""

        monkeypatch.setattr(pf, "_run", fake_run)
        monkeypatch.setattr(pf.shutil, "which", lambda n: f"/usr/bin/{n}")
        assert pf.check_identity_coherence() == []


class TestGhMultiAccount:
    """`gh auth status` exits 1 if *any* configured account fails, even when the
    active one is healthy -- so a stale keyring entry beside a working login was
    reported as "gh is not authenticated". Measured on a real machine.

    The fix reads `--json hosts`, which gh documents as always exiting zero and
    which returns `state` / `active` / `login` / `tokenSource` as fields, so
    nothing here parses another product's prose.
    """

    def _findings(self, pf, monkeypatch, payload, code=0):
        def fake_run(cmd, **kw):
            if cmd[:3] == ["gh", "auth", "status"]:
                return code, payload
            return 0, ""
        monkeypatch.setattr(pf, "_run", fake_run)
        monkeypatch.setattr(pf.shutil, "which",
                            lambda n: f"/usr/bin/{n}" if n == "gh" else None)
        return pf.check_credential_liveness()

    def test_a_healthy_active_account_beside_a_broken_one_is_silent(self, pf, monkeypatch):
        """The exact shape on the machine that exposed this: active GITHUB_TOKEN
        account working, stale keyring account failing, gh exiting 1."""
        payload = _gh_json(token_source="oauth_token", others=[_gh_failed_account()])
        findings = self._findings(pf, monkeypatch, payload, code=1)
        assert not any("not authenticated" in f for f in findings), findings

    def test_the_exit_code_is_not_consulted_at_all(self, pf, monkeypatch):
        assert self._findings(pf, monkeypatch, _gh_json(token_source="oauth_token"),
                              code=1) == []

    def test_no_accounts_at_all_is_still_reported(self, pf, monkeypatch):
        """Widening must not swallow the finding this check exists for. gh returns
        `{"hosts": {}}` and exits 0 when nothing is configured -- verified."""
        findings = self._findings(pf, monkeypatch, '{"hosts": {}}')
        # Names the host rather than claiming "gh is not authenticated": an
        # enterprise-only setup also lands here, and telling that user they are
        # unauthenticated points at a host they may not use at all.
        assert any(f"no gh credential for {pf.GH_HOST}" in f for f in findings), findings

    def test_a_broken_active_account_is_reported_with_its_reason(self, pf, monkeypatch):
        payload = _gh_json(login="ryqf", state="error")
        findings = self._findings(pf, monkeypatch, payload)
        assert any("not usable" in f and "ryqf" in f for f in findings), findings

    def test_an_old_gh_is_named_not_reported_as_unauthenticated(self, pf, monkeypatch):
        """An older gh without `--json` must not be reported as unauthenticated.

        That is the stated intent, and it still holds. The assertion used to be
        `findings == []` -- silence -- which was *stronger* than the intent and hid a
        second problem: `--json` shipped in gh 2.81.0, so on an older gh both this
        check and the identity one below went quiet on a machine that has a real
        issue. Nothing pins a gh floor, so the version is only knowable from the
        failure.

        So: still not "unauthenticated", but no longer silent either.
        """
        findings = self._findings(
            pf, monkeypatch, "unknown flag: --json", code=1)
        assert findings, "an unreadable gh must not be silent"
        assert not any("not authenticated" in f for f in findings), (
            "the original false alarm must not come back"
        )
        assert any("2.81.0" in f for f in findings), findings

    def test_a_readable_but_odd_payload_is_still_silent(self, pf, monkeypatch):
        """Exit 0 with output we cannot parse is genuinely "cannot tell", and stays
        silent -- the new finding keys on the non-zero exit, not on the parse."""
        findings = self._findings(pf, monkeypatch, "surprising but fine", code=0)
        assert findings == []

    def test_an_expired_env_token_still_says_it_came_from_the_env(self, pf, monkeypatch):
        """The realistic form of the bug, and the one the warning existed for.

        `tokenSource` used to hang off the success branch, so an *expired* `GH_TOKEN`
        took the `state != "success"` branch and the user was never told the
        credential came from the environment -- the one fact that explains why
        `gh auth login` appears to work and changes nothing.
        """
        payload = _gh_json(login="ryqf", state="error", token_source="GH_TOKEN")
        findings = self._findings(pf, monkeypatch, payload)
        assert any("not usable" in f for f in findings), findings
        assert any("$GH_TOKEN" in f for f in findings), (
            "an expired env token must say where it came from"
        )
        assert any("unset it first" in f for f in findings), findings

    def test_a_long_gh_error_is_truncated(self, pf, monkeypatch):
        """gh interpolates HTTP response bodies here and this output lands in a chat
        transcript."""
        payload = _gh_json(login="ryqf", state="error", error="x" * 400)
        findings = self._findings(pf, monkeypatch, payload)
        assert findings and "..." in findings[0]
        assert len(findings[0]) < 400, len(findings[0])

    def test_enterprise_env_tokens_are_recognised_too(self, pf):
        """`host` is a parameter now, so an enterprise caller would otherwise get the
        state finding with no mention of the environment."""
        for name in ("GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN"):
            assert name in pf.GH_ENV_TOKEN_SOURCES

    def test_github_token_is_detected_as_an_env_token(self, pf, monkeypatch):
        """The old check tested `"GH_TOKEN" in out`, which never matches the
        `GITHUB_TOKEN` gh actually reports -- so this warning had never fired."""
        findings = self._findings(pf, monkeypatch, _gh_json(token_source="GITHUB_TOKEN"))
        assert any("GITHUB_TOKEN" in f and "expires with no warning" in f
                   for f in findings), findings

    def test_gh_token_is_detected_too(self, pf, monkeypatch):
        findings = self._findings(pf, monkeypatch, _gh_json(token_source="GH_TOKEN"))
        assert any("$GH_TOKEN" in f for f in findings), findings

    def test_a_stored_login_is_silent(self, pf, monkeypatch):
        assert self._findings(pf, monkeypatch, _gh_json(token_source="oauth_token")) == []

    def test_json_survives_the_stderr_gh_concatenates_onto_it(self, pf):
        """`_run` merges stderr into stdout and gh writes a human line there while
        still exiting 0 with valid JSON, so a plain json.loads would fail."""
        assert pf.gh_active_account(_gh_json(login="ryqf", noise=True))["login"] == "ryqf"

    def test_the_json_flag_is_actually_requested(self, pf, monkeypatch):
        """Without --json the command exits 1 on a partial failure, which is the
        entire bug. Pin the flag so it cannot be dropped."""
        seen = []
        monkeypatch.setattr(pf, "_run", lambda cmd, **kw: (seen.append(cmd), (0, "{}"))[1])
        pf._gh_auth_status()
        assert seen[0] == ["gh", "auth", "status", "--json", "hosts"]


class TestBackgroundNamesTheOtelProblem:
    """The background pass printed "see the per-key detail above" while printing no
    per-key detail -- a remediation pointing at nothing."""

    def test_the_finding_names_the_wrong_key(self, pf, monkeypatch):
        monkeypatch.setattr(pf, "probe_claude_code_otel",
                            lambda **k: {"verdict": pf.CC_OTEL_NOT_CLAUDE_CODE,
                                         "problems": []})
        monkeypatch.setattr(pf, "probe_otel", lambda **k: {
            "verdict": pf.OTEL_MISCONFIGURED, "settings_path": "/tmp/settings.json",
            "identity": "RYQF",
            "problems": ["github.copilot.chat.otel.exporterType is not set"]})
        findings = pf.check_telemetry()
        assert any("exporterType" in f for f in findings), findings

    def test_no_remediation_points_at_detail_that_is_not_printed(self, pf):
        """Both dicts. This pinned `OTEL_REMEDIATION` only, and
        `CC_OTEL_REMEDIATION` still said "listed above" -- the same defect, one
        namespace over, in the half the test did not look at.

        "above" is the wrong word regardless of caller: `cmd_check` and `cmd_otel`
        print the problems above the remediation, while the background pass renders
        them inline immediately before it. A remediation should not describe a layout
        that depends on who rendered it.
        """
        for name, table in (("OTEL_REMEDIATION", pf.OTEL_REMEDIATION),
                            ("CC_OTEL_REMEDIATION", pf.CC_OTEL_REMEDIATION)):
            for verdict, text in table.items():
                assert "above" not in text, f"{name}[{verdict}]: {text}"


class TestVsCodeWithNoSettingsFileIsStillReported:
    """`settings_path` alone suppressed every NOT_CONFIGURED finding, so the pass
    was silent exactly when reporting was definitely off -- a first-run VS Code has
    no User settings.json at all."""

    def _telemetry(self, pf, monkeypatch, harness, settings_path):
        monkeypatch.setattr(pf, "detect_harness", lambda: harness)
        monkeypatch.setattr(pf, "probe_claude_code_otel", lambda **k: {
            "verdict": pf.CC_OTEL_NOT_CLAUDE_CODE, "problems": [], "notes": [],
            "values": {}, "sources": {}})
        monkeypatch.setattr(pf, "probe_otel", lambda: {
            "verdict": pf.OTEL_NOT_CONFIGURED, "settings_path": settings_path,
            "searched": [], "values": {}, "problems": [], "identity": None})
        return pf.check_telemetry()

    def test_vscode_with_no_settings_file_is_reported(self, pf, monkeypatch):
        assert self._telemetry(pf, monkeypatch, "vscode", None), \
            "a first-run VS Code is the case that most needs telling"

    def test_a_coder_workspace_with_no_vscode_stays_quiet(self, pf, monkeypatch):
        """The original intent, preserved: this is not a gap there, and question 5
        already says so rather than sending anyone to a command that cannot work."""
        assert self._telemetry(pf, monkeypatch, "claude-code", None) == []

    def test_an_existing_settings_file_is_reported_regardless_of_harness(self, pf, monkeypatch):
        assert self._telemetry(pf, monkeypatch, "unknown", "/some/settings.json")


class TestMetricsPathProblemIsRedacted:
    """The path diagnostic added in 8c5bc46 interpolated the endpoint verbatim --
    the same leak class fixed elsewhere in the same commit, reintroduced by the new
    message."""

    def test_credentials_do_not_reach_the_problem_text(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json", {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://u:sh3cret@c.invalid"})
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        joined = " ".join(r["problems"])
        assert "/v1/metrics" in joined, "the finding must still be reported"
        assert "sh3cret" not in joined

    def test_the_host_is_still_named_because_that_is_the_diagnosis(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json", {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://c.invalid"})
        r = _cc_env(pf, monkeypatch, {}, managed=managed)
        assert any("c.invalid" in p for p in r["problems"])


class TestMisconfiguredVerdictIsNotDescribedAsHarmless:
    """`ON_BUT_MISCONFIGURED` covers both partial and *total* loss now that a
    missing signal path lands there, so documentation promising "data arrives" would
    make total loss read as non-urgent."""

    def test_the_skill_does_not_promise_data_arrives(self):
        skill = (REPO_ROOT / "skills" / "dplc-preflight" / "SKILL.md").read_text()
        row = next(ln for ln in skill.splitlines() if "`ON_BUT_MISCONFIGURED`" in ln)
        assert "Data arrives;" not in row
        assert "total loss" in row or "all of it" in row

    def test_the_remediation_does_not_promise_it_either(self, pf):
        text = pf.CC_OTEL_REMEDIATION[pf.CC_OTEL_MISCONFIGURED]
        assert "Data is arriving" not in text, text


class TestBackgroundReachesTheNoDestinationVerdict:
    """The bug this test exists for.

    `check_telemetry` passed `check_local_collector=False`, so `no_destination`
    could never be set and the *worst* telemetry state -- enabled with no endpoint
    at all, producing and discarding everything -- was reported one severity too
    low as `ON_BUT_MISCONFIGURED`, with remediation text that referred to "a
    destination" that did not exist. Observed live on an EKS Coder workspace whose
    managed policy sets neither an exporter nor an endpoint.
    """

    NO_ENDPOINT = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_LOGS_EXPORTER": "otlp"}

    def _findings(self, pf, monkeypatch, tmp_path, env, port_open):
        managed = _write_settings(tmp_path, "managed-settings.json", env)
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [managed])
        monkeypatch.setattr(pf.os, "environ", {})
        monkeypatch.setattr(pf, "_port_open", lambda *a, **k: port_open)
        monkeypatch.setattr(pf, "probe_otel", lambda: {
            "verdict": pf.OTEL_NOT_CONFIGURED, "settings_path": None, "searched": [],
            "values": {}, "problems": [], "identity": None})
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        return pf.check_telemetry()

    def test_no_endpoint_and_nothing_listening_is_no_destination(self, pf, monkeypatch, tmp_path):
        found = self._findings(pf, monkeypatch, tmp_path, self.NO_ENDPOINT, port_open=False)
        assert found, "the loudest telemetry failure must not be silent"
        assert pf.CC_OTEL_NO_DESTINATION in found[0], found

    def test_it_no_longer_reports_the_milder_verdict(self, pf, monkeypatch, tmp_path):
        found = self._findings(pf, monkeypatch, tmp_path, self.NO_ENDPOINT, port_open=False)
        assert pf.CC_OTEL_MISCONFIGURED not in found[0], found

    def test_a_listening_local_collector_is_a_destination(self, pf, monkeypatch, tmp_path):
        """Then it is genuinely misconfigured rather than undirected -- data goes
        somewhere, just not somewhere Catalyst asked for."""
        found = self._findings(pf, monkeypatch, tmp_path, self.NO_ENDPOINT, port_open=True)
        assert found and pf.CC_OTEL_NO_DESTINATION not in found[0], found

    def test_a_healthy_config_stays_silent(self, pf, monkeypatch, tmp_path):
        healthy = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
                   "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT":
                       "https://catalyst-otel.x.invalid/v1/metrics"}
        assert self._findings(pf, monkeypatch, tmp_path, healthy, port_open=False) == []

    def test_the_misconfigured_text_does_not_claim_a_destination(self, pf):
        """It is reachable with and without one, so it cannot assert either."""
        text = pf.CC_OTEL_REMEDIATION[pf.CC_OTEL_MISCONFIGURED]
        assert "with a destination set" not in text, text


class TestPreReviewFindings:
    """Findings from an independent adversarial pass before human review.

    Grouped together because they share a cause: four rounds of automated review
    had checked the code against itself, and these are the things only a fresh
    reading of *behaviour* surfaced.
    """

    BASE = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp"}

    def _probe(self, pf, monkeypatch, tmp_path, env, port_open=False):
        managed = _write_settings(tmp_path, "managed-settings.json", dict(self.BASE, **env))
        return _cc_env(pf, monkeypatch, {}, managed=managed, port_open=port_open)

    # --- the generic endpoint carrying a signal path -------------------------
    def test_generic_endpoint_with_the_signal_path_is_a_problem(self, pf, monkeypatch, tmp_path):
        """The mirror image of the per-signal bug, and the more tempting one: the
        generic endpoint is a BASE url, so a value already carrying /v1/metrics
        resolves to /v1/metrics/v1/metrics -> 404 -> total silent loss. It was
        reported ON with no problems."""
        r = self._probe(pf, monkeypatch, tmp_path,
                        {"OTEL_EXPORTER_OTLP_ENDPOINT": "https://catalyst-otel.x/v1/metrics"})
        assert r["verdict"] == pf.CC_OTEL_MISCONFIGURED
        assert any("already carries" in p for p in r["problems"]), r["problems"]

    def test_a_correct_generic_endpoint_is_still_fine(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path,
                        {"OTEL_EXPORTER_OTLP_ENDPOINT": "https://catalyst-otel.x"})
        assert r["verdict"] == pf.CC_OTEL_ON, r["problems"]

    # --- path checked as a path, not a string suffix -------------------------
    def test_a_query_string_does_not_read_as_a_missing_path(self, pf, monkeypatch, tmp_path):
        """A suffix match flagged a legal endpoint while asserting something
        demonstrably untrue about it."""
        r = self._probe(pf, monkeypatch, tmp_path,
                        {"OTEL_EXPORTER_OTLP_METRICS_ENDPOINT":
                             "https://catalyst-otel.x/v1/metrics?tenant=edo"})
        assert r["verdict"] == pf.CC_OTEL_ON, r["problems"]

    def test_a_fragment_does_not_either(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path,
                        {"OTEL_EXPORTER_OTLP_METRICS_ENDPOINT":
                             "https://catalyst-otel.x/v1/metrics#f"})
        assert r["verdict"] == pf.CC_OTEL_ON, r["problems"]

    def test_a_genuinely_missing_path_is_still_caught(self, pf, monkeypatch, tmp_path):
        r = self._probe(pf, monkeypatch, tmp_path,
                        {"OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://catalyst-otel.x?a=1"})
        assert any("/v1/metrics" in p for p in r["problems"]), r["problems"]

    # --- the background pass must name the problems ---------------------------
    def test_background_reports_the_named_problems_not_just_the_verdict(
            self, pf, monkeypatch, tmp_path):
        """`ON_BUT_MISCONFIGURED`'s remediation says to "read the problems listed
        above", and this is the only place that verdict is rendered -- so without
        them the most likely finding on a DevNext box was a message whose actionable
        half did not exist."""
        managed = _write_settings(tmp_path, "managed-settings.json", {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_LOGS_EXPORTER": "otlp"})
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [managed])
        monkeypatch.setattr(pf.os, "environ", {})
        monkeypatch.setattr(pf, "_port_open", lambda *a, **k: True)   # a destination exists
        monkeypatch.setattr(pf, "probe_otel", lambda: {
            "verdict": pf.OTEL_NOT_CONFIGURED, "settings_path": None, "searched": [],
            "values": {}, "problems": [], "identity": None})
        found = pf.check_telemetry()
        assert found
        assert "OTEL_METRICS_EXPORTER" in found[0], found

    # --- the Copilot endpoint is an OTLP URL too ------------------------------
    def test_copilot_endpoint_credentials_are_not_printed(self, pf, monkeypatch, tmp_path, capsys):
        """`redact_url` was applied to every Claude Code endpoint and to none of the
        Copilot ones, though both are OTLP URLs read from user-editable files."""
        leaky = "https://svc:sh3cret@catalyst-otel.x.invalid?api_key=LEAKME"
        monkeypatch.setattr(pf, "probe_otel", lambda: {
            "verdict": pf.OTEL_MISCONFIGURED, "settings_path": "/tmp/s.json",
            "searched": [], "identity": "RYQF",
            "values": {"github.copilot.chat.otel.otlpEndpoint": leaky},
            "problems": [f"github.copilot.chat.otel.otlpEndpoint is "
                         f"{pf.redact_url(leaky)}, expected '...'"]})
        monkeypatch.setattr(pf, "probe_claude_code_otel", lambda **k: {
            "verdict": pf.CC_OTEL_NOT_CLAUDE_CODE, "values": {}, "sources": {},
            "problems": [], "notes": []})
        pf.cmd_otel()
        out = capsys.readouterr().out
        assert "sh3cret" not in out and "LEAKME" not in out
        assert "catalyst-otel.x.invalid" in out, "the host is the diagnosis; keep it"

    def test_the_mismatch_problem_string_redacts_the_endpoint(self, pf, tmp_path, monkeypatch):
        """Built in `probe_otel` and printed by both `otel` and `check`."""
        import json as _json
        s = tmp_path / "settings.json"
        s.write_text(_json.dumps({
            "github.copilot.chat.otel.enabled": True,
            "github.copilot.chat.otel.otlpEndpoint":
                "https://svc:sh3cret@catalyst-otel.x.invalid?api_key=LEAKME"}))
        monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [s])
        joined = " ".join(pf.probe_otel()["problems"])
        assert "sh3cret" not in joined and "LEAKME" not in joined

    # --- the contract statements must match the code -------------------------
    def test_the_module_docstring_admits_the_background_egress(self, pf):
        """It said `otel --probe-endpoint` was the only call leaving the machine.
        `background` shells out to keeper-env and gh, which do. For a script whose
        contract is read-only-and-mostly-local, the docstring IS the contract."""
        doc = pf.__doc__ or ""
        assert "background" in doc, "the subcommand is undocumented"
        assert "keeper-env" in doc and "gh auth status" in doc
        assert "the only network call" not in doc

    def test_the_skill_does_not_claim_the_background_pass_is_networkless(self):
        skill = (REPO_ROOT / "skills" / "dplc-preflight" / "SKILL.md").read_text()
        assert "the only network call outside `check`" not in skill


class TestRemediationIsSelfServe:
    """Catalyst setup problems are the user's to fix, and ours to hear about.

    These strings used to say "ask the DevNext team" and "report this to the EDO
    team". That stopped being true when `/setup-workspace claude-otel` existed: the
    managed policy sets none of the keys Catalyst needs, so a user-scope write takes
    effect and nobody waits on another team. Sending someone to file a request they
    do not need costs them a day and costs that team an interruption.
    """

    SETUP_VERDICTS = ("CC_OTEL_OFF", "CC_OTEL_NO_DESTINATION", "CC_OTEL_MISCONFIGURED")

    def test_no_setup_verdict_sends_the_user_to_another_team(self, pf):
        for name in self.SETUP_VERDICTS:
            text = pf.CC_OTEL_REMEDIATION[getattr(pf, name)]
            assert "DevNext team" not in text, name
            assert "EDO team" not in text, name

    def test_every_setup_verdict_names_the_self_serve_command(self, pf):
        for name in self.SETUP_VERDICTS:
            text = pf.CC_OTEL_REMEDIATION[getattr(pf, name)]
            assert "claude-otel" in text, name

    def test_every_setup_verdict_offers_the_feedback_route(self, pf):
        """Our queue, on our repo -- not a message into someone else's."""
        for name in self.SETUP_VERDICTS:
            assert "catalyst-feedback" in pf.CC_OTEL_REMEDIATION[getattr(pf, name)], name

    def test_it_says_the_managed_policy_will_not_override_the_fix(self, pf):
        """The reason self-serve works at all, and the first thing a sceptical user
        will ask about a workspace whose settings are centrally managed."""
        assert "does not set these keys" in pf.CC_OTEL_REMEDIATION[pf.CC_OTEL_NO_DESTINATION]

    def test_content_capture_still_escalates_to_grc(self, pf):
        """The deliberate exception. That is an enterprise compliance matter, not a
        Catalyst setup problem, so a GitHub issue on this repo is the wrong queue."""
        text = pf.CC_OTEL_REMEDIATION[pf.CC_OTEL_CONTENT_CAPTURE]
        assert "Governance, Risk and Compliance" in text
        assert "catalyst-feedback" not in text

    def test_the_healthy_verdict_offers_nothing(self, pf):
        text = pf.CC_OTEL_REMEDIATION[pf.CC_OTEL_ON]
        assert "claude-otel" not in text and "catalyst-feedback" not in text

    def test_an_unreachable_collector_routes_to_our_queue(self, pf):
        """The collector is ours, so an unreachable one is our issue to triage."""
        result = pf.probe_otel_endpoint("https://nx.invalid.invalid/v1/metrics")
        assert not result["reachable"]

    def test_the_copilot_path_also_offers_the_feedback_route(self, pf):
        assert "catalyst-feedback" in pf.OTEL_REMEDIATION[pf.OTEL_NOT_CONFIGURED]


class TestBackgroundNamesBothTheProblemAndTheFix:
    """One dead end was replaced by another.

    The pass first printed only the verdict, so `ON_BUT_MISCONFIGURED`'s "read the
    problems listed above" pointed at nothing. The fix printed the problems *instead
    of* the remediation -- so it then said precisely what was wrong and never how to
    repair it. Both halves belong here; this is the only place the verdict renders.
    """

    def _findings(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json", {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_LOGS_EXPORTER": "otlp"})
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [managed])
        monkeypatch.setattr(pf.os, "environ", {})
        monkeypatch.setattr(pf, "_port_open", lambda *a, **k: False)
        monkeypatch.setattr(pf, "probe_otel", lambda: {
            "verdict": pf.OTEL_NOT_CONFIGURED, "settings_path": None, "searched": [],
            "values": {}, "problems": [], "identity": None})
        return pf.check_telemetry()

    def test_the_named_problems_are_present(self, pf, monkeypatch, tmp_path):
        found = self._findings(pf, monkeypatch, tmp_path)
        assert found and "OTEL_METRICS_EXPORTER" in found[0]

    def test_the_fix_is_present_too(self, pf, monkeypatch, tmp_path):
        found = self._findings(pf, monkeypatch, tmp_path)
        assert "claude-otel" in found[0], found

    def test_it_does_not_send_the_user_to_another_team(self, pf, monkeypatch, tmp_path):
        found = self._findings(pf, monkeypatch, tmp_path)
        assert "DevNext team" not in found[0] and "EDO team" not in found[0]

    def test_a_healthy_config_stays_silent(self, pf, monkeypatch, tmp_path):
        managed = _write_settings(tmp_path, "managed-settings.json", {
            "CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "otlp",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "https://catalyst-otel.x.invalid/v1/metrics"})
        monkeypatch.setattr(pf, "detect_harness", lambda: "claude-code")
        monkeypatch.setattr(pf, "claude_code_settings_layers", lambda: [managed])
        monkeypatch.setattr(pf.os, "environ", {})
        monkeypatch.setattr(pf, "_port_open", lambda *a, **k: False)
        monkeypatch.setattr(pf, "probe_otel", lambda: {
            "verdict": pf.OTEL_NOT_CONFIGURED, "settings_path": None, "searched": [],
            "values": {}, "problems": [], "identity": None})
        assert pf.check_telemetry() == []


class TestGhAccountIsHostScoped:
    """`gh` reports `active` per host, so there is no global "the" active account.

    Looping every host and returning the first active one meant a machine with both
    github.com and an enterprise host configured derived its identity and token
    diagnostics from whichever key JSON iteration yielded first -- so the health of
    one login could be reported for the other.
    """

    @staticmethod
    def payload(hosts):
        import json as _json
        return _json.dumps({"hosts": hosts})

    GH = {"github.com": [{"active": True, "login": "RYQF_capgroup",
                          "state": "success", "tokenSource": "keyring"}]}
    ENT = {"github.cg.invalid": [{"active": True, "login": "someone-else",
                                  "state": "failing", "tokenSource": "GH_TOKEN"}]}

    def test_the_github_com_account_is_returned(self, pf):
        got = pf.gh_active_account(self.payload(dict(self.GH, **self.ENT)))
        assert got["login"] == "RYQF_capgroup"

    def test_an_enterprise_host_listed_first_does_not_win(self, pf):
        """The ordering case. Previously decided by JSON key order."""
        got = pf.gh_active_account(self.payload(dict(self.ENT, **self.GH)))
        assert got["login"] == "RYQF_capgroup", "took the enterprise host's account"

    def test_a_failing_enterprise_host_does_not_taint_a_healthy_github(self, pf):
        got = pf.gh_active_account(self.payload(dict(self.ENT, **self.GH)))
        assert got["state"] == "success"

    def test_github_com_absent_is_a_finding_not_a_borrowed_identity(self, pf):
        """`{}` rather than the enterprise account: no login here is a real problem,
        and silently substituting another host's would hide it."""
        assert pf.gh_active_account(self.payload(self.ENT)) == {}

    def test_the_host_is_overridable_and_part_of_the_contract(self, pf):
        got = pf.gh_active_account(self.payload(self.ENT), host="github.cg.invalid")
        assert got["login"] == "someone-else"

    def test_an_unreadable_payload_is_still_unknown_not_a_finding(self, pf):
        """`None` must stay distinct from `{}`, or the false "not authenticated"
        returns under a new name."""
        assert pf.gh_active_account("not json at all") is None
        assert pf.gh_active_account("") is None

    def test_no_active_account_on_a_configured_host_is_a_finding(self, pf):
        payload = self.payload({"github.com": [{"active": False, "login": "x"}]})
        assert pf.gh_active_account(payload) == {}


class TestCollectorSurvivesTheEarlyReturns:
    """The cache contract has to hold in the states that most need looking at.

    `collector` was derived after the early returns for `captureContent=true` and
    `enabled=false`, so a machine deliberately pointed at dev cached as
    `collector: null` in exactly those two cases -- indistinguishable from an
    unknown collector, in a file downstream skills read.
    """

    DEV = "https://catalyst-otel.datalakefoundation.aws-dev.capgroup.com"

    def _probe(self, pf, tmp_path, monkeypatch, extra):
        import json as _json
        s = tmp_path / "settings.json"
        s.write_text(_json.dumps(dict({
            "github.copilot.chat.otel.enabled": True,
            "github.copilot.chat.otel.exporterType": "otlp-http",
            "github.copilot.chat.otel.otlpEndpoint": self.DEV,
            "github.copilot.chat.otel.captureContent": False,
        }, **extra)))
        monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [s])
        return pf.probe_otel()

    def test_capture_content_still_records_the_collector(self, pf, tmp_path, monkeypatch):
        r = self._probe(pf, tmp_path, monkeypatch,
                        {"github.copilot.chat.otel.captureContent": True})
        assert r["verdict"] == pf.OTEL_CAPTURE_CONTENT
        assert r["collector"] == "dev", "the compliance case needs it most"

    def test_explicitly_off_still_records_the_collector(self, pf, tmp_path, monkeypatch):
        r = self._probe(pf, tmp_path, monkeypatch,
                        {"github.copilot.chat.otel.enabled": False})
        assert r["verdict"] == pf.OTEL_DISABLED
        assert r["collector"] == "dev"

    def test_the_healthy_case_is_unchanged(self, pf, tmp_path, monkeypatch):
        assert self._probe(pf, tmp_path, monkeypatch, {})["collector"] == "dev"

    def test_a_missing_settings_file_is_still_none(self, pf, monkeypatch, tmp_path):
        """`None` must keep meaning "nothing to read", not "not a Catalyst collector"."""
        monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [tmp_path / "absent.json"])
        assert pf.probe_otel()["collector"] is None

    def test_a_foreign_endpoint_is_none_not_a_guess(self, pf, tmp_path, monkeypatch):
        r = self._probe(pf, tmp_path, monkeypatch,
                        {"github.copilot.chat.otel.otlpEndpoint": "https://elsewhere.invalid"})
        assert r["collector"] is None

    # The field survived the early returns; the *note* did not. Asserting only the
    # field is what let that through -- `collector: dev` was cached correctly while
    # the report never said so, on the two paths where someone most needs telling.

    def test_capture_content_also_gets_the_dev_note(self, pf, tmp_path, monkeypatch):
        """And this pairing is not hypothetical: a dev endpoint and content capture
        are both things you set while experimenting, so they travel together."""
        r = self._probe(pf, tmp_path, monkeypatch,
                        {"github.copilot.chat.otel.captureContent": True})
        assert r["verdict"] == pf.OTEL_CAPTURE_CONTENT
        assert any("dev collector" in n for n in r["notes"]), (
            "the capture-content path returns before the note is appended"
        )

    def test_explicitly_off_also_gets_the_dev_note(self, pf, tmp_path, monkeypatch):
        r = self._probe(pf, tmp_path, monkeypatch,
                        {"github.copilot.chat.otel.enabled": False})
        assert r["verdict"] == pf.OTEL_DISABLED
        assert any("dev collector" in n for n in r["notes"])

    def test_an_unconfigured_file_gets_no_note(self, pf, tmp_path, monkeypatch):
        """Hoisting the note must not make it fire where there is no collector to
        name -- otherwise the fix trades one wrong report for another."""
        import json as _json
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"editor.fontSize": 13}))
        monkeypatch.setattr(pf, "vscode_settings_candidates", lambda: [f])
        r = pf.probe_otel()
        assert r["verdict"] == pf.OTEL_NOT_CONFIGURED
        assert r["notes"] == []
