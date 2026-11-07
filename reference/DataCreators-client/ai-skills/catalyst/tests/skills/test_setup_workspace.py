"""Unit tests for setup-workspace's deterministic helpers.

The skill directory uses a hyphen (`setup-workspace/`), not a valid module
name, so we load `setup_workspace.py` via importlib.  These cover the pure
logic: OS and package-manager detection, version parsing, the exit-code
precedence, and the core-vs-extras requirements split.  The install side
effects are exercised end-to-end in a container, not here.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "skills" / "setup-workspace" / "scripts" / "setup_workspace.py"
)


def _load():
    spec = importlib.util.spec_from_file_location(
        "setup_workspace_script", SCRIPT_PATH
    )
    assert spec and spec.loader, "could not build import spec"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def sw():
    return _load()


# --- version parsing ---------------------------------------------------------
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Python 3.13.1", (3, 13)),
        ("Python 3.9.6", (3, 9)),
        ("Python 3.14.6", (3, 14)),
        ("", None),
        ("not a version", None),
    ],
)
def test_parse_python_version(sw, text, expected):
    assert sw.parse_python_version(text) == expected


@pytest.mark.parametrize(
    "ver,ok",
    [((3, 10), True), ((3, 13), True), ((3, 9), False), ((2, 7), False), (None, False)],
)
def test_meets_floor(sw, ver, ok):
    assert sw.meets_floor(ver) is ok


@pytest.mark.parametrize(
    "ver,too_new",
    [((3, 14), True), ((3, 13), False), ((3, 10), False), (None, False)],
)
def test_is_too_new(sw, ver, too_new):
    assert sw.is_too_new(ver) is too_new


# --- OS detection ------------------------------------------------------------
@pytest.mark.parametrize(
    "system,expected",
    [("Darwin", "darwin"), ("Windows", "windows"), ("Linux", "linux")],
)
def test_detect_os(sw, monkeypatch, system, expected):
    monkeypatch.setattr(sw.platform, "system", lambda: system)
    assert sw.detect_os() == expected


# --- package-manager detection ----------------------------------------------
def _which_only(present):
    return lambda name: f"/usr/bin/{name}" if name in present else None


def test_detect_pkg_mgr_prefers_brew_on_mac(sw, monkeypatch):
    monkeypatch.setattr(sw.shutil, "which", _which_only({"brew", "uv"}))
    assert sw.detect_package_manager("darwin") == "brew"


def test_detect_pkg_mgr_uv_when_no_brew(sw, monkeypatch):
    monkeypatch.setattr(sw.shutil, "which", _which_only({"uv"}))
    assert sw.detect_package_manager("darwin") == "uv"


def test_detect_pkg_mgr_linux_apt(sw, monkeypatch):
    monkeypatch.setattr(sw.shutil, "which", _which_only({"apt-get"}))
    assert sw.detect_package_manager("linux") == "apt-get"


def test_detect_pkg_mgr_prefers_winget_on_windows(sw, monkeypatch):
    monkeypatch.setattr(sw.shutil, "which", _which_only({"winget", "choco"}))
    assert sw.detect_package_manager("windows") == "winget"


def test_detect_pkg_mgr_uv_when_no_winget_choco(sw, monkeypatch):
    # uv can provision Python on Windows (bootstrap.ps1), so detection lists it.
    monkeypatch.setattr(sw.shutil, "which", _which_only({"uv"}))
    assert sw.detect_package_manager("windows") == "uv"


def test_detect_pkg_mgr_none(sw, monkeypatch):
    monkeypatch.setattr(sw.shutil, "which", _which_only(set()))
    assert sw.detect_package_manager("darwin") is None


# --- exit-code precedence ----------------------------------------------------
def _state(**over):
    base = {
        "python_ok": True,
        "package_manager": "brew",
        "pip_cgrepo": True,
        "deps": True,
    }
    base.update(over)
    return base


def test_exit_ready(sw):
    assert sw.exit_code_for(_state()) == 0


def test_exit_python_not_ready(sw):
    # Python provisioning is bootstrap.sh's job, so any Python gap is exit 2
    # ("run bootstrap.sh"), regardless of which package manager is present.
    assert sw.exit_code_for(_state(python_ok=False, package_manager="brew")) == 2
    assert sw.exit_code_for(_state(python_ok=False, package_manager="apt-get")) == 2
    assert sw.exit_code_for(_state(python_ok=False, package_manager=None)) == 2


def test_exit_pip_not_cgrepo(sw):
    assert sw.exit_code_for(_state(pip_cgrepo=False)) == 5


def test_exit_deps_missing(sw):
    assert sw.exit_code_for(_state(deps=False)) == 4


def test_exit_precedence_python_wins(sw):
    # multiple gaps at once: the Python gap takes precedence
    state = _state(python_ok=False, package_manager="brew", pip_cgrepo=False, deps=False)
    assert sw.exit_code_for(state) == 2


# --- requirements split (Option B) -------------------------------------------
def test_parse_requirements_splits_core_and_extras(sw):
    core, extras = sw.parse_requirements()
    core_text = " ".join(core)
    extra_text = " ".join(extras)
    # core runtime deps are present
    assert "pydantic" in core_text
    assert "databricks-sdk" in core_text
    # dbt is a tested-against extra, installed best-effort, never core
    assert "dbt-core" in extra_text
    assert "dbt-core" not in core_text
    # comment and option lines are excluded from both
    assert all(not s.startswith(("#", "--")) for s in core + extras)


def test_unsatisfiable_databricks_cli_pin_is_not_a_requirement(sw):
    """The `databricks-cli>=0.218.0` pin must not be installable at all.

    It asks PyPI for a version scheme belonging to the Go CLI; the PyPI package
    of that name is the deprecated legacy CLI and stops at 0.18.0, so the pin can
    never resolve. Because pip fails the whole transaction rather than one line,
    leaving it active meant `pip install -r skills/requirements.txt` installed
    nothing at all.

    This supersedes the earlier best-effort-extra handling: not attempting the
    install is strictly safer than attempting one that cannot succeed. The range
    still lives in requirements.txt as a comment, because /build-preflight reads
    it as text for the tool-version drift check -- asserted below so commenting it
    out cannot silently break that.
    """
    core, extras = sw.parse_requirements()
    assert "databricks-cli" not in " ".join(core + extras)

    text = sw.REQUIREMENTS.read_text()
    assert "databricks-cli>=0.218.0,<1.0.0" in text, (
        "build-preflight greps this range for drift detection; keep the shape"
    )


# --- pip config: TLS trust and non-destructive merge (review R2 / B2 / B3) ----
def test_pip_conf_never_disables_tls_verification(sw, tmp_path, monkeypatch):
    """trusted-host turns off certificate validation for the one host every
    corporate install flows through. It must never be written."""
    conf = tmp_path / "pip.conf"
    monkeypatch.setattr(sw, "_pip_conf_path", lambda: conf)
    monkeypatch.setattr(sw, "pip_index_is_cgrepo", lambda _exe: False)
    monkeypatch.setattr(sw, "verify_cgrepo_tls", lambda *a, **k: (True, "stubbed"))

    sw.ensure_pip_cgrepo("python3")

    text = conf.read_text()
    assert sw.CGREPO_INDEX in text
    assert "trusted-host" not in text


def test_pip_conf_preserves_the_tls_trust_anchor(sw, tmp_path, monkeypatch):
    """A corporate machine behind TLS interception carries `cert = <CA bundle>`.
    Clobbering it breaks pip for everything else the user does."""
    conf = tmp_path / "pip.conf"
    conf.write_text("[global]\ncert = /etc/ssl/corp-ca.pem\ntimeout = 60\n")
    monkeypatch.setattr(sw, "_pip_conf_path", lambda: conf)
    monkeypatch.setattr(sw, "pip_index_is_cgrepo", lambda _exe: False)
    monkeypatch.setattr(sw, "verify_cgrepo_tls", lambda *a, **k: (True, "stubbed"))

    sw.ensure_pip_cgrepo("python3")

    text = conf.read_text()
    assert "cert = /etc/ssl/corp-ca.pem" in text
    assert "timeout = 60" in text
    assert sw.CGREPO_INDEX in text


def test_pip_conf_preserves_unrelated_sections_and_keys(sw, tmp_path, monkeypatch):
    """Only index-url changes. proxy/extra-index-url/[install] survive."""
    conf = tmp_path / "pip.conf"
    conf.write_text(
        "[global]\n"
        "proxy = http://proxy.corp:8080\n"
        "extra-index-url = https://other.internal/simple/\n"
        "index-url = https://pypi.org/simple/\n"
        "\n"
        "[install]\n"
        "no-warn-script-location = true\n"
    )
    monkeypatch.setattr(sw, "_pip_conf_path", lambda: conf)
    monkeypatch.setattr(sw, "pip_index_is_cgrepo", lambda _exe: False)
    monkeypatch.setattr(sw, "verify_cgrepo_tls", lambda *a, **k: (True, "stubbed"))

    sw.ensure_pip_cgrepo("python3")

    import configparser
    cp = configparser.ConfigParser()
    cp.read(conf)
    assert cp["global"]["index-url"] == sw.CGREPO_INDEX      # replaced
    assert cp["global"]["proxy"] == "http://proxy.corp:8080"  # preserved
    assert cp["global"]["extra-index-url"] == "https://other.internal/simple/"
    assert cp["install"]["no-warn-script-location"] == "true"
    assert "pypi.org" not in conf.read_text()


def test_pip_conf_backs_up_before_touching_an_existing_file(sw, tmp_path, monkeypatch):
    conf = tmp_path / "pip.conf"
    conf.write_text("[global]\ncert = /etc/ssl/corp-ca.pem\n")
    monkeypatch.setattr(sw, "_pip_conf_path", lambda: conf)
    monkeypatch.setattr(sw, "pip_index_is_cgrepo", lambda _exe: False)
    monkeypatch.setattr(sw, "verify_cgrepo_tls", lambda *a, **k: (True, "stubbed"))

    sw.ensure_pip_cgrepo("python3")

    backups = list(tmp_path.glob("pip.conf.bak.*"))
    assert len(backups) == 1
    assert "cert = /etc/ssl/corp-ca.pem" in backups[0].read_text()


def test_malformed_pip_conf_is_left_alone(sw, tmp_path, monkeypatch):
    """Do not guess at a config we cannot parse -- back up and refuse."""
    conf = tmp_path / "pip.conf"
    conf.write_text("this is not ini [[[\n")
    monkeypatch.setattr(sw, "_pip_conf_path", lambda: conf)
    monkeypatch.setattr(sw, "pip_index_is_cgrepo", lambda _exe: False)
    monkeypatch.setattr(sw, "verify_cgrepo_tls", lambda *a, **k: (True, "stubbed"))

    assert sw.ensure_pip_cgrepo("python3") is False
    assert conf.read_text() == "this is not ini [[[\n"
    assert list(tmp_path.glob("pip.conf.bak.*"))


def test_pip_conf_path_honors_the_documented_location(sw, monkeypatch, tmp_path):
    """install.md documents ~/.pip/pip.conf. With nothing existing, use it."""
    monkeypatch.setattr(sw, "detect_os", lambda: "darwin")
    monkeypatch.setattr(sw.Path, "home", staticmethod(lambda: tmp_path))
    assert sw._pip_conf_path() == tmp_path / ".pip" / "pip.conf"


def test_pip_conf_path_prefers_an_existing_config_over_creating_a_second(
    sw, monkeypatch, tmp_path
):
    """Merging into the config pip already reads beats a competing new file."""
    monkeypatch.setattr(sw, "detect_os", lambda: "darwin")
    monkeypatch.setattr(sw.Path, "home", staticmethod(lambda: tmp_path))
    xdg = tmp_path / ".config" / "pip" / "pip.conf"
    xdg.parent.mkdir(parents=True)
    xdg.write_text("[global]\ncert = /etc/ssl/corp-ca.pem\n")
    assert sw._pip_conf_path() == xdg


def test_tls_failure_remediation_names_cert_not_trusted_host(sw, monkeypatch):
    """The failure path must teach the secure fix, never the insecure one."""
    import ssl

    def _boom(*_a, **_k):
        raise ssl.SSLCertVerificationError("bad cert")

    err = ssl.SSLCertVerificationError("bad cert")
    err.verify_message = "unable to get local issuer certificate"

    def _raise(*_a, **_k):
        raise err

    monkeypatch.setattr(sw.socket, "create_connection", _raise)
    ok, detail = sw.verify_cgrepo_tls()

    assert ok is False
    assert "cert" in detail
    assert "trusted-host" in detail and "do not set trusted-host" in detail
    assert "disables verification" in detail


def test_tls_probe_reports_unreachable_host_distinctly(sw, monkeypatch):
    def _raise(*_a, **_k):
        raise OSError("network unreachable")

    monkeypatch.setattr(sw.socket, "create_connection", _raise)
    ok, detail = sw.verify_cgrepo_tls()
    assert ok is False
    assert "could not reach" in detail


# --- package-manager honesty (review N5) -------------------------------------
def test_check_does_not_advertise_a_manager_tool_cannot_use(sw, monkeypatch):
    """`check` printed `Package manager: apt-get`, then `tool git` refused it."""
    monkeypatch.setattr(sw, "detect_package_manager", lambda *_a: "apt-get")
    assert sw.can_install_tools("linux") is False
    monkeypatch.setattr(sw, "detect_package_manager", lambda *_a: "brew")
    assert sw.can_install_tools("darwin") is True


def test_every_advertised_tool_manager_has_an_install_command(sw):
    for mgr in sw.TOOL_INSTALL_COMMANDS:
        for tool in ("git", "gh"):
            assert sw.TOOL_INSTALL_COMMANDS[mgr](tool), f"{mgr}/{tool} empty"


# --- requirements marker anchoring (review nit) ------------------------------
def test_tested_against_marker_is_anchored_to_line_start(sw):
    """A future comment merely mentioning the phrase must not move the boundary."""
    assert sw.TESTED_AGAINST_MARKER.startswith("#")


# --- install_deps side effects (review N6) -----------------------------------
def test_install_deps_routes_every_install_through_cgrepo(sw, monkeypatch):
    """Supply-chain policy: no install may reach a public registry."""
    calls: list[list[str]] = []
    monkeypatch.setattr(sw, "_run", lambda cmd, timeout=None: (calls.append(cmd), (0, ""))[1])

    assert sw.install_deps("python3") is True
    assert calls, "expected at least one pip invocation"
    for cmd in calls:
        assert "--index-url" in cmd
        assert cmd[cmd.index("--index-url") + 1] == sw.CGREPO_INDEX
        assert not any("pypi.org" in part for part in cmd)


def test_install_deps_separates_core_from_best_effort_extras(sw, monkeypatch):
    """Core gates readiness; a stale extra pin must not fail the core install."""
    calls: list[list[str]] = []

    def _run(cmd, timeout=None):
        calls.append(cmd)
        # Fail only the second (extras) call.
        return (1, "stale pin") if len(calls) == 2 else (0, "")

    monkeypatch.setattr(sw, "_run", _run)
    assert sw.install_deps("python3") is True, "extras failure must not fail core"
    assert len(calls) == 2


def test_install_deps_fails_when_core_install_fails(sw, monkeypatch):
    monkeypatch.setattr(sw, "_run", lambda cmd, timeout=None: (1, "network down"))
    assert sw.install_deps("python3") is False


# --- Copilot Chat usage reporting (OTEL) ------------------------------------
#
# Two things these tests exist to hold: captureContent must never be written
# true, and the JSONC file must survive the edit with its comments intact. The
# second is the same class of damage as the pip.conf overwrite -- a
# parse-and-rewrite would silently strip every comment in the user's settings.

OTEL_ENABLED = "github.copilot.chat.otel.enabled"
OTEL_CAPTURE = "github.copilot.chat.otel.captureContent"
OTEL_ENDPOINT = "github.copilot.chat.otel.otlpEndpoint"


@pytest.fixture(autouse=True)
def _known_user_id(monkeypatch):
    """Most plan tests are not about identity detection; give them a stable id so
    they exercise the path they are actually testing."""
    monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")


def _settings_file(tmp_path, body):
    p = tmp_path / "settings.json"
    p.write_text(body)
    return p


class TestOtelCollectorChoice:
    """`--endpoint dev` exists so choosing dev is something a user can ask for,
    rather than something they have to hand-edit settings.json to get.

    Names only, no free-form URL: dplc-preflight reports anything that is not one
    of the two known collectors as a problem, so accepting a URL here would let the
    writer produce a state the checker rejects.
    """

    def test_defaults_to_prd(self, sw, tmp_path, _known_user_id):
        plan = sw.plan_otel_settings(_settings_file(tmp_path, '{\n}\n'))
        assert sw.OTEL_COLLECTORS["prd"] in plan["new_text"]
        assert sw.OTEL_COLLECTORS["dev"] not in plan["new_text"]

    def test_dev_writes_the_dev_collector(self, sw, tmp_path, _known_user_id):
        plan = sw.plan_otel_settings(_settings_file(tmp_path, '{\n}\n'), endpoint="dev")
        assert sw.OTEL_COLLECTORS["dev"] in plan["new_text"]
        assert sw.OTEL_COLLECTORS["prd"] not in plan["new_text"]

    def test_switching_back_to_prd_is_a_single_change(self, sw, tmp_path, _known_user_id):
        """Someone who set dev has to be able to get back without hand-editing."""
        body = ('{\n  "github.copilot.chat.otel.enabled": true,\n'
                '  "github.copilot.chat.otel.exporterType": "otlp-http",\n'
                f'  "github.copilot.chat.otel.otlpEndpoint": "{sw.OTEL_COLLECTORS["dev"]}",\n'
                '  "github.copilot.chat.otel.captureContent": false,\n'
                '  "github.copilot.chat.otel.resourceAttributes": { "user.id": "RYQF" }\n}\n')
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body), endpoint="prd")
        assert plan["ok"]
        assert len(plan["changes"]) == 1
        assert sw.OTEL_COLLECTORS["prd"] in plan["new_text"]

    def test_the_cli_refuses_an_unknown_collector_name(self, sw):
        """argparse choices is the boundary; a typo must not reach the writer."""
        with pytest.raises(SystemExit):
            sw.main(["otel", "--endpoint", "prod"])

    def test_the_two_collectors_match_the_preflight_set(self, sw):
        """Writer and checker must agree, or one produces what the other rejects.

        Compared as dicts, not grepped as source text. The earlier version asserted
        each URL appeared somewhere in `preflight.py`, which passes on a match in a
        comment, a docstring, or `OTEL_EXPECTED` -- none of which means the accept
        gate knows the value. It was also one-directional: a collector preflight
        knows and the writer does not was invisible to it, which is the direction
        that produces "the checker accepts what the writer can never emit".
        """
        import importlib.util
        import sys
        from pathlib import Path

        path = (Path(sw.__file__).parents[2]
                / "dplc-preflight" / "scripts" / "preflight.py")
        spec = importlib.util.spec_from_file_location("_pf_for_sync", path)
        assert spec and spec.loader
        pf = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = pf
        spec.loader.exec_module(pf)

        assert sw.OTEL_COLLECTORS == pf.OTEL_COLLECTORS, (
            f"writer has {sw.OTEL_COLLECTORS}, checker has {pf.OTEL_COLLECTORS}"
        )


class TestOtelPlan:
    def test_inserts_every_key_including_the_identity_attribute(self, sw, tmp_path, monkeypatch):
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        p = _settings_file(tmp_path, '{\n  "editor.fontSize": 13\n}\n')
        plan = sw.plan_otel_settings(p)
        assert plan["ok"] and len(plan["changes"]) == 5
        for key in sw.OTEL_KEYS:
            assert f'"{key}"' in plan["new_text"]
        # Without this, reporting arrives and cannot be attributed to anyone.
        assert f'"{sw.OTEL_RESOURCE_ATTRS_KEY}"' in plan["new_text"]
        assert '"user.id": "RYQF"' in plan["new_text"]

    def test_refuses_to_write_anonymous_config_when_id_is_unknown(self, sw, tmp_path, monkeypatch):
        """Silently producing anonymous reporting is worse than not writing: the
        data arrives, the dashboards populate, and nothing is attributable."""
        monkeypatch.delenv("CATALYST_OTEL_USER_ID", raising=False)
        monkeypatch.setattr(sw, "detect_user_id", lambda: (None, "could not determine"))
        p = _settings_file(tmp_path, '{\n}\n')
        plan = sw.plan_otel_settings(p)
        assert plan["ok"] is False
        assert "anonymous" in plan["reason"]
        assert "CATALYST_OTEL_USER_ID" in plan["reason"]

    def test_preserves_extra_attributes_when_the_identity_matches(self, sw, tmp_path,
                                                                  monkeypatch):
        """An existing block may carry attributes beyond user.id, and those are
        not ours to drop — so when the identity already agrees, leave it alone."""
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ('{\n  "%s": { "user.id": "RYQF", "team": "edo" }\n}\n'
                % sw.OTEL_RESOURCE_ATTRS_KEY)
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is True, plan.get("reason")
        assert '"team": "edo"' in plan["new_text"]
        assert '"user.id": "RYQF"' in plan["new_text"]

    def test_refuses_a_block_whose_identity_is_someone_else(self, sw, tmp_path, monkeypatch):
        """Settings copied from a colleague attribute your usage to them.

        This test previously asserted the opposite — that a block naming KXY was
        preserved untouched on an RYQF machine — which encoded the very
        misattribution the check is supposed to catch.
        """
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ('{\n  "%s": { "user.id": "KXY", "team": "edo" }\n}\n'
                % sw.OTEL_RESOURCE_ATTRS_KEY)
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is False
        assert "KXY" in plan["reason"] and "RYQF" in plan["reason"]
        assert plan["new_text"] is None

    def test_refuses_a_block_with_no_identity_at_all(self, sw, tmp_path, monkeypatch):
        """"A block exists" is not "the block identifies someone"."""
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ('{\n  "%s": { "team": "edo" }\n}\n' % sw.OTEL_RESOURCE_ATTRS_KEY)
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is False
        assert "anonymous" in plan["reason"]
        assert plan["new_text"] is None

    def test_a_commented_out_setting_is_not_treated_as_live(self, sw, tmp_path, monkeypatch):
        """Otherwise the patch edits inside the comment, skips inserting the real
        key, and still reports a successful update."""
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ('{\n  // "%s": { "user.id": "OLD" }\n  "editor.fontSize": 13\n}\n'
                % sw.OTEL_RESOURCE_ATTRS_KEY)
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is True, plan.get("reason")
        # The commented line survives untouched, and a live key is inserted.
        assert '// "%s"' % sw.OTEL_RESOURCE_ATTRS_KEY in plan["new_text"]
        assert '"user.id": "RYQF"' in plan["new_text"]

    def test_rejects_an_identity_override_that_would_corrupt_json(self, sw, monkeypatch):
        """The value is interpolated into settings.json, so a quote breaks it."""
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", 'a"b')
        assert sw.detect_user_id()[0] is None

    def test_a_commented_out_capture_content_does_not_block_the_write(self, sw, tmp_path,
                                                                     monkeypatch, capsys):
        """The apply guard matched raw text, so an inert
        `// "...captureContent": true` made --apply refuse and exit 4 — leaving no
        way forward except deleting your own comment. It must see what Copilot sees."""
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ('{\n  // "%s": true\n  "editor.fontSize": 13\n}\n' % sw.OTEL_CAPTURE_KEY)
        p = _settings_file(tmp_path, body)
        plan = sw.plan_otel_settings(p)
        assert plan["ok"] is True, plan.get("reason")
        assert sw.apply_otel_settings(plan) is True
        out = capsys.readouterr().out
        assert "REFUSING" not in out.upper()
        assert '// "%s": true' % sw.OTEL_CAPTURE_KEY in p.read_text()

    def test_an_empty_object_gets_no_trailing_comma(self, sw, tmp_path, monkeypatch):
        """On `{}` the insert block's last comma landed before the closing brace.
        VS Code tolerates it; strict json.loads does not — and this PR names a
        stray comma as a failure mode it fixes."""
        import json
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        plan = sw.plan_otel_settings(_settings_file(tmp_path, "{}\n"))
        assert plan["ok"] is True, plan.get("reason")
        json.loads(plan["new_text"])            # strict, no JSONC tolerance

    def test_an_existing_property_still_gets_its_comma(self, sw, tmp_path, monkeypatch):
        """The comma is only dropped when nothing follows the insertion point."""
        import json
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        plan = sw.plan_otel_settings(_settings_file(tmp_path, '{\n  "a": 1\n}\n'))
        assert plan["ok"] is True, plan.get("reason")
        assert json.loads(plan["new_text"])["a"] == 1

    def test_a_length_changing_patch_does_not_corrupt_later_keys(self, sw, tmp_path,
                                                                monkeypatch):
        """The mask must be rebuilt from the CURRENT text before each search.

        Built once from the original, every offset after a length-changing patch is
        stale. This input produced `"...otel.capfalseContent": true` — still valid
        JSON, so nothing downstream noticed, and the key name no longer matched what
        `apply_otel_settings` guards, so the captureContent guardrail passed it while
        the run reported "captureContent: true -> false".
        """
        import json
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ('{\n  "%s": "https://old-collector.example.com",\n  "%s": true\n}\n'
                % ("github.copilot.chat.otel.otlpEndpoint", sw.OTEL_CAPTURE_KEY))
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is True, plan.get("reason")
        json.loads(plan["new_text"])                       # must still parse
        assert "capfalseContent" not in plan["new_text"]
        assert f'"{sw.OTEL_CAPTURE_KEY}": false' in plan["new_text"]

    def test_a_length_changing_patch_leaves_valid_json(self, sw, tmp_path, monkeypatch):
        """The second reproduction: this one did not even parse (`tfalse}`)."""
        import json
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ('{\n  "%s": false,\n  "%s": true\n}\n'
                % ("github.copilot.chat.otel.enabled", sw.OTEL_CAPTURE_KEY))
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is True, plan.get("reason")
        json.loads(plan["new_text"])
        assert "tfalse" not in plan["new_text"]
        assert f'"{sw.OTEL_CAPTURE_KEY}": false' in plan["new_text"]

    def test_a_trailing_same_line_comment_survives_a_patch(self, sw, tmp_path, monkeypatch):
        """A greedy value group ran through the comment and deleted it."""
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ('{\n  "%s": false // opted out during the pilot\n}\n' % "github.copilot.chat.otel.enabled")
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is True, plan.get("reason")
        assert "// opted out during the pilot" in plan["new_text"]
        assert f'"{"github.copilot.chat.otel.enabled"}": true' in plan["new_text"]

    def test_unknown_identity_with_an_empty_block_refuses(self, sw, tmp_path, monkeypatch):
        """Gating on key *presence* let this through: the key dropped out of
        `wanted`, none of the block validation ran, and four keys were written with
        no identity — the exact outcome the refusal exists to prevent."""
        monkeypatch.delenv("CATALYST_OTEL_USER_ID", raising=False)
        monkeypatch.setattr(sw, "detect_user_id", lambda: (None, "stubbed"))
        body = '{\n  "%s": { "team": "edo" }\n}\n' % sw.OTEL_RESOURCE_ATTRS_KEY
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is False
        assert plan["new_text"] is None

    def test_unknown_identity_with_the_key_only_in_a_comment_refuses(self, sw, tmp_path,
                                                                    monkeypatch):
        monkeypatch.delenv("CATALYST_OTEL_USER_ID", raising=False)
        monkeypatch.setattr(sw, "detect_user_id", lambda: (None, "stubbed"))
        body = ('{\n  // "%s": { "user.id": "OLD" }\n  "a": 1\n}\n'
                % sw.OTEL_RESOURCE_ATTRS_KEY)
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is False
        assert plan["new_text"] is None

    def test_unknown_identity_but_the_block_already_names_someone_proceeds(
            self, sw, tmp_path, monkeypatch):
        """The case that must keep working: detection fails, but the file already
        identifies a person, so there is nothing anonymous about the result."""
        monkeypatch.delenv("CATALYST_OTEL_USER_ID", raising=False)
        monkeypatch.setattr(sw, "detect_user_id", lambda: (None, "stubbed"))
        body = '{\n  "%s": { "user.id": "KXY" }\n}\n' % sw.OTEL_RESOURCE_ATTRS_KEY
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is True, plan.get("reason")
        assert '"user.id": "KXY"' in plan["new_text"]

    def test_a_settings_file_that_opens_with_a_comment_is_accepted(self, sw, tmp_path,
                                                                  monkeypatch):
        """VS Code writes settings.json with a leading comment, so requiring the
        file to start with `{` rejected perfectly normal files."""
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = '// VS Code settings\n{\n  "editor.fontSize": 13\n}\n'
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is True, plan.get("reason")
        assert "// VS Code settings" in plan["new_text"]

    def test_a_brace_inside_a_leading_comment_is_not_the_insertion_point(
            self, sw, tmp_path, monkeypatch):
        """Otherwise the keys land inside the comment, where they do nothing while
        the command reports success."""
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = '// see { here }\n{\n  "editor.fontSize": 13\n}\n'
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] is True, plan.get("reason")
        first = plan["new_text"].splitlines()[0]
        assert first == "// see { here }", f"insertion went into the comment: {first!r}"
        assert any(l.lstrip().startswith('"github.copilot')
                   for l in plan["new_text"].splitlines()[1:])

    def test_a_file_with_no_object_outside_a_comment_is_refused(self, sw, tmp_path,
                                                               monkeypatch):
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        plan = sw.plan_otel_settings(_settings_file(tmp_path, "// just a comment\n"))
        assert plan["ok"] is False
        assert "no top-level" in plan["reason"]

    def test_preserves_comments_and_unrelated_settings(self, sw, tmp_path):
        """A parse-and-rewrite would delete these. That is why the edit is textual."""
        body = ('{\n  // keep me\n  /* and me */\n  "editor.fontSize": 13,\n'
                '  "files.autoSave": "off"\n}\n')
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert "// keep me" in plan["new_text"]
        assert "/* and me */" in plan["new_text"]
        assert '"files.autoSave": "off"' in plan["new_text"]
        assert '"editor.fontSize": 13' in plan["new_text"]

    def test_inserted_keys_are_in_declaration_order(self, sw, tmp_path):
        p = _settings_file(tmp_path, "{\n}\n")
        text = sw.plan_otel_settings(p)["new_text"]
        positions = [text.index(f'"{k}"') for k in sw.OTEL_KEYS]
        assert positions == sorted(positions)

    def test_already_correct_is_a_no_op(self, sw, tmp_path, monkeypatch):
        monkeypatch.setenv("CATALYST_OTEL_USER_ID", "RYQF")
        body = ("{\n" + "".join(f'  "{k}": {v},\n' for k, v in sw.OTEL_KEYS.items())
                + '  "%s": { "user.id": "RYQF" }\n}\n' % sw.OTEL_RESOURCE_ATTRS_KEY)
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert plan["ok"] and plan["changes"] == [] and plan["new_text"] is None

    def test_patches_a_wrong_endpoint_in_place(self, sw, tmp_path):
        body = f'{{\n  "{OTEL_ENDPOINT}": "https://wrong.example.com"\n}}\n'
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert "wrong.example.com" not in plan["new_text"]
        assert "catalyst-otel.datalake.aws.capgroup.com" in plan["new_text"]

    def test_missing_file_is_reported_not_created(self, sw, tmp_path):
        plan = sw.plan_otel_settings(tmp_path / "absent.json")
        assert plan["ok"] is False
        assert not (tmp_path / "absent.json").exists()

    def test_refuses_a_file_that_is_not_an_object(self, sw, tmp_path):
        plan = sw.plan_otel_settings(_settings_file(tmp_path, "[1, 2, 3]\n"))
        assert plan["ok"] is False
        assert "refusing" in plan["reason"].lower()

    def test_plan_produces_a_diff_for_consent(self, sw, tmp_path):
        plan = sw.plan_otel_settings(_settings_file(tmp_path, "{\n}\n"))
        assert plan["diff"].startswith("---")
        assert OTEL_ENABLED in plan["diff"]


class TestOtelCaptureContentGuardrail:
    def test_expected_value_is_false(self, sw):
        assert sw.OTEL_KEYS[OTEL_CAPTURE] == "false"

    def test_existing_true_is_flipped_to_false_and_called_out(self, sw, tmp_path):
        body = f'{{\n  "{OTEL_CAPTURE}": true\n}}\n'
        plan = sw.plan_otel_settings(_settings_file(tmp_path, body))
        assert f'"{OTEL_CAPTURE}": false' in plan["new_text"]
        assert f'"{OTEL_CAPTURE}": true' not in plan["new_text"]
        assert any("conversation text" in c for c in plan["changes"])

    def test_apply_refuses_any_text_with_capture_content_true(self, sw, tmp_path, capsys):
        """Last-line defence: even if a caller hands us the text directly."""
        p = _settings_file(tmp_path, "{\n}\n")
        rigged = {"ok": True, "path": str(p), "changes": ["x"], "diff": "",
                  "new_text": f'{{\n  "{OTEL_CAPTURE}": true\n}}\n'}
        assert sw.apply_otel_settings(rigged) is False
        assert "REFUSING" in capsys.readouterr().out
        assert "true" not in p.read_text()

    def test_no_code_path_writes_capture_content_true(self, sw):
        with open(sw.__file__, encoding="utf-8") as fh:
            source = fh.read()
        assert f'"{OTEL_CAPTURE}": true' not in source


class TestOtelApply:
    def test_backs_up_before_writing(self, sw, tmp_path):
        p = _settings_file(tmp_path, '{\n  "editor.fontSize": 13\n}\n')
        assert sw.apply_otel_settings(sw.plan_otel_settings(p)) is True
        backups = list(tmp_path.glob("settings.json.bak.*"))
        assert len(backups) == 1
        assert '"editor.fontSize": 13' in backups[0].read_text()

    def test_result_is_readable_by_dplc_preflight(self, sw, tmp_path):
        """Cross-skill contract: whatever setup-workspace writes, dplc-preflight
        must be able to parse and verdict. A naive comment-stripper breaks on the
        // inside the endpoint URL, which is exactly the bug this guards."""
        import importlib.util
        import os.path

        pf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(sw.__file__))),
            "dplc-preflight", "scripts", "preflight.py")
        spec = importlib.util.spec_from_file_location("pf_contract", pf_path)
        pf = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pf)

        p = _settings_file(tmp_path, '{\n  // note\n  "editor.fontSize": 13,\n}\n')
        sw.apply_otel_settings(sw.plan_otel_settings(p))
        assert "// note" in p.read_text()

        settings, err = pf.read_user_settings(p)
        assert err is None, err
        assert settings["editor.fontSize"] == 13
        assert settings[OTEL_ENABLED] is True
        assert settings[OTEL_CAPTURE] is False

        # And the verdict a user would see is a good one, not MISCONFIGURED.
        pf.vscode_settings_candidates = lambda: [p]
        assert pf.probe_otel()["verdict"] in (pf.OTEL_OK, pf.OTEL_PENDING_RESTART)

    def test_tells_the_user_to_reload_the_window(self, sw, tmp_path, capsys):
        """The restart is the step people miss, so it has to be in the output.

        This test previously asserted the output demanded a *full quit* and said
        "Reload Window does not start reporting". That was wrong: a window reload is
        sufficient, confirmed by hand and consistent with the extension manifest
        finding on #434. The assertion was pinning the incorrect claim in place.
        """
        p = _settings_file(tmp_path, "{\n}\n")
        sw.apply_otel_settings(sw.plan_otel_settings(p))
        out = capsys.readouterr().out
        assert "RELOAD WINDOW" in out.upper()
        assert "does not start report" not in out.lower()

    def test_dry_run_writes_nothing(self, sw, tmp_path, monkeypatch):
        p = _settings_file(tmp_path, "{\n}\n")
        before = p.read_text()
        monkeypatch.setattr(sw, "_otel_settings_path", lambda: p)
        assert sw.cmd_otel(apply=False) == 0
        assert p.read_text() == before
        assert not list(tmp_path.glob("*.bak.*"))


class TestOtelSettingsScope:
    def test_candidates_are_user_scope_only(self, sw):
        for path in sw.vscode_settings_candidates():
            assert path.parent.name == "User"
            assert path.name == "settings.json"

    def test_candidates_cover_the_three_products(self, sw):
        names = {p.parent.parent.name for p in sw.vscode_settings_candidates()}
        assert {"Code", "Code - Insiders", "VSCodium"} <= names


# --- Claude Code usage reporting (AICAT-337) ---------------------------------
#
# The asymmetry these close: `otel` could turn Copilot Chat reporting on for a user
# and nothing could do the same for Claude Code, so people were handed `export` lines
# that die with the shell.

import json as _json


class TestClaudeOtelEndpoint:
    def test_named_collectors_resolve(self, sw):
        assert sw.normalise_metrics_endpoint("dev").startswith(
            "https://catalyst-otel.datalakefoundation.aws-dev")
        assert sw.normalise_metrics_endpoint("prd").startswith(
            "https://catalyst-otel.datalake.aws")

    def test_the_signal_path_is_appended_when_missing(self, sw):
        """The bug this guards. A per-signal endpoint is used AS-IS -- unlike the
        generic variable nothing is appended -- so a host-only value POSTs to '/',
        which the collector answers 404. Measured, not assumed."""
        assert sw.normalise_metrics_endpoint("https://c.invalid") == \
            "https://c.invalid/v1/metrics"
        assert sw.normalise_metrics_endpoint("https://c.invalid/") == \
            "https://c.invalid/v1/metrics"

    def test_an_existing_path_is_not_doubled(self, sw):
        assert sw.normalise_metrics_endpoint("https://c.invalid/v1/metrics") == \
            "https://c.invalid/v1/metrics"

    def test_every_named_collector_carries_the_path(self, sw):
        for name in sw.CLAUDE_OTEL_COLLECTORS:
            assert sw.normalise_metrics_endpoint(name).endswith("/v1/metrics")


class TestClaudeOtelEnvBlock:
    def test_the_exact_key_set(self, sw):
        """Five, not four. `CLAUDE_CODE_ENABLE_TELEMETRY` was added after review:
        without it nothing exports on a machine that has had no fleet rollout, which
        is exactly this command's audience -- and the tool still reported success."""
        env = sw.claude_otel_env("dev", workspace_kind="coder")
        assert set(env) == {"CLAUDE_CODE_ENABLE_TELEMETRY",
                            "OTEL_METRICS_EXPORTER",
                            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
                            "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL",
                            "OTEL_RESOURCE_ATTRIBUTES"}

    def test_telemetry_is_actually_enabled(self, sw):
        """The laptop case: an endpoint with no enable flag exports nothing."""
        assert sw.claude_otel_env("dev")["CLAUDE_CODE_ENABLE_TELEMETRY"] == "1"

    def test_nothing_about_logs_or_content(self, sw):
        """The whole guarantee. Content is only ever a log record, so a config that
        names no logs destination cannot carry prompt text to Catalyst."""
        env = sw.claude_otel_env("dev")
        for key in sw.CLAUDE_FORBIDDEN_KEYS:
            assert key not in env, key

    def test_the_generic_endpoint_is_forbidden_not_merely_absent(self, sw):
        """It is the fallback for every unset signal, so aiming it here would route
        logs to us. Being on the refusal list is what keeps that structural."""
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" in sw.CLAUDE_FORBIDDEN_KEYS

    def test_producer_tag_is_present(self, sw):
        attrs = dict(p.split("=", 1) for p in
                     sw.claude_otel_env("dev")["OTEL_RESOURCE_ATTRIBUTES"].split(","))
        assert attrs["telemetry.producer"] == "claude-code"

    def test_resource_attributes_parse(self, sw):
        raw = sw.claude_otel_env("dev")["OTEL_RESOURCE_ATTRIBUTES"]
        assert " " not in raw and ";" not in raw
        for pair in raw.split(","):
            assert pair.count("=") == 1 and all(pair.split("="))

    def test_workspace_kind_is_stable_across_shells(self, sw, monkeypatch):
        """The bug this pins.

        `workspace.kind` used to include a `coder-eks` value derived from
        `KUBERNETES_SERVICE_HOST`, which is visible in a pod but not in a host shell
        sharing the same `~/.claude`. So the value flipped depending on where the
        command ran -- and since it is written to a file, every alternate run reported
        a change, rewrote it, and dropped another `settings.json.bak.<timestamp>`.

        A label that changes with the shell it was computed in is not a label.
        """
        monkeypatch.setenv("CODER_WORKSPACE_NAME", "w")
        monkeypatch.setenv("KUBERNETES_SERVICE_HOST", "1.2.3.4")
        with_k8s = sw.detect_workspace_kind()
        monkeypatch.delenv("KUBERNETES_SERVICE_HOST")
        without_k8s = sw.detect_workspace_kind()
        assert with_k8s == without_k8s == "coder"

    def test_a_non_coder_machine_is_local(self, sw, monkeypatch):
        monkeypatch.delenv("CODER_WORKSPACE_NAME", raising=False)
        monkeypatch.delenv("CODER_AGENT_TOKEN", raising=False)
        assert sw.detect_workspace_kind() == "local"

    def test_the_same_input_twice_produces_no_second_change(self, sw, tmp_path, monkeypatch):
        """The churn this prevents: a re-run must be a no-op, not another backup."""
        monkeypatch.setenv("CODER_WORKSPACE_NAME", "w")
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"model": "opus"}))
        assert sw.apply_claude_otel(sw.plan_claude_otel("dev", path=f))
        first = f.read_text()
        plan2 = sw.plan_claude_otel("dev", path=f)
        assert plan2["changes"] == [] and plan2["new_text"] is None
        assert f.read_text() == first


class TestClaudeOtelPlan:
    def test_a_missing_file_is_created(self, sw, tmp_path):
        plan = sw.plan_claude_otel("dev", path=tmp_path / "settings.json")
        assert plan["ok"] and plan["new_text"]
        assert any("create" in c for c in plan["changes"])

    def test_unrelated_keys_survive(self, sw, tmp_path):
        """This file holds the user's own preferences; losing one is not acceptable
        collateral for turning telemetry on."""
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"model": "opus", "theme": "auto",
                                  "enabledPlugins": {"a": True}}))
        plan = sw.plan_claude_otel("dev", path=p)
        out = _json.loads(plan["new_text"])
        assert out["model"] == "opus" and out["theme"] == "auto"
        assert out["enabledPlugins"] == {"a": True}

    def test_an_existing_env_block_is_merged_not_replaced(self, sw, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"env": {"MY_OWN_VAR": "keep me"}}))
        plan = sw.plan_claude_otel("dev", path=p)
        env = _json.loads(plan["new_text"])["env"]
        assert env["MY_OWN_VAR"] == "keep me"
        assert env["OTEL_METRICS_EXPORTER"] == "otlp"

    def test_already_configured_is_a_no_op(self, sw, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"env": sw.claude_otel_env("dev")}))
        plan = sw.plan_claude_otel("dev", path=p)
        assert plan["ok"] and plan["changes"] == [] and plan["new_text"] is None

    def test_a_changed_value_is_reported_as_a_change_not_an_addition(self, sw, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"env": {"OTEL_METRICS_EXPORTER": "none"}}))
        plan = sw.plan_claude_otel("dev", path=p)
        assert any("->" in c for c in plan["changes"]), plan["changes"]

    def test_comments_are_refused_rather_than_deleted(self, sw, tmp_path):
        """A parse-and-rewrite would drop every comment silently."""
        p = tmp_path / "settings.json"
        p.write_text('{\n  // my note\n  "model": "opus"\n}\n')
        plan = sw.plan_claude_otel("dev", path=p)
        assert not plan["ok"] and "comment" in plan["reason"].lower()

    def test_a_url_is_not_mistaken_for_a_comment(self, sw, tmp_path):
        """The `//` in `https://` is not a comment. Treating it as one would refuse
        to write any settings file containing a URL -- which is most of them."""
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"env": {"SOME_URL": "https://x.invalid/a"}}))
        plan = sw.plan_claude_otel("dev", path=p)
        assert plan["ok"], plan["reason"]

    def test_unparseable_json_is_refused(self, sw, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text('{"model": "opus",}')
        plan = sw.plan_claude_otel("dev", path=p)
        assert not plan["ok"] and "parse" in plan["reason"].lower()

    def test_a_non_object_env_is_refused(self, sw, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"env": "not-an-object"}))
        plan = sw.plan_claude_otel("dev", path=p)
        assert not plan["ok"]

    def test_an_empty_file_is_treated_as_empty_settings(self, sw, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text("")
        plan = sw.plan_claude_otel("dev", path=p)
        assert plan["ok"] and plan["new_text"]

    def test_the_plan_never_writes(self, sw, tmp_path):
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"model": "opus"}))
        before = p.read_text()
        sw.plan_claude_otel("dev", path=p)
        assert p.read_text() == before


class TestClaudeOtelApply:
    def _plan(self, sw, tmp_path, existing=None):
        p = tmp_path / "settings.json"
        if existing is not None:
            p.write_text(_json.dumps(existing))
        return sw.plan_claude_otel("dev", path=p), p

    def test_writes_and_backs_up(self, sw, tmp_path, capsys):
        plan, p = self._plan(sw, tmp_path, {"model": "opus"})
        assert sw.apply_claude_otel(plan)
        out = _json.loads(p.read_text())
        assert out["model"] == "opus"
        assert out["env"]["OTEL_METRICS_EXPORTER"] == "otlp"
        assert list(tmp_path.glob("settings.json.bak.*")), "no backup written"

    def test_creates_the_parent_directory(self, sw, tmp_path):
        target = tmp_path / "nested" / ".claude" / "settings.json"
        plan = sw.plan_claude_otel("dev", path=target)
        assert sw.apply_claude_otel(plan)
        assert target.exists()

    def test_refuses_a_forbidden_key(self, sw, tmp_path, capsys):
        """Last line of defence against a future caller assembling the block itself."""
        plan, p = self._plan(sw, tmp_path, {"model": "opus"})
        doc = _json.loads(plan["new_text"])
        doc["env"]["OTEL_LOGS_EXPORTER"] = "otlp"
        plan["new_text"] = _json.dumps(doc)
        assert not sw.apply_claude_otel(plan)
        assert "REFUSING" in capsys.readouterr().out

    def test_refuses_the_generic_endpoint(self, sw, tmp_path, capsys):
        plan, p = self._plan(sw, tmp_path, {"model": "opus"})
        doc = _json.loads(plan["new_text"])
        doc["env"]["OTEL_EXPORTER_OTLP_ENDPOINT"] = "https://catalyst-otel.x.invalid"
        plan["new_text"] = _json.dumps(doc)
        assert not sw.apply_claude_otel(plan)

    def test_it_says_a_new_session_is_needed_not_a_reload(self, sw, tmp_path, capsys):
        """Unlike VS Code there is no reload: the SDK reads env once at process
        start, so an existing session keeps exporting nowhere."""
        plan, _ = self._plan(sw, tmp_path, {"model": "opus"})
        sw.apply_claude_otel(plan)
        out = capsys.readouterr().out.lower()
        assert "new claude code session" in out
        assert "reload the window" not in out


class TestClaudeOtelCli:
    def test_dry_run_writes_nothing(self, sw, tmp_path, monkeypatch, capsys):
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"model": "opus"}))
        monkeypatch.setattr(sw, "CLAUDE_SETTINGS", p)
        before = p.read_text()
        assert sw.main(["claude-otel", "--endpoint", "dev"]) == 0
        assert p.read_text() == before
        assert "Dry run" in capsys.readouterr().out

    def test_apply_writes(self, sw, tmp_path, monkeypatch):
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"model": "opus"}))
        monkeypatch.setattr(sw, "CLAUDE_SETTINGS", p)
        assert sw.main(["claude-otel", "--endpoint", "dev", "--apply"]) == 0
        assert _json.loads(p.read_text())["env"]["OTEL_METRICS_EXPORTER"] == "otlp"

    def test_endpoint_is_required_so_nothing_is_guessed(self, sw):
        """prd is unroutable from oz-dev and dev is wrong on a laptop; a default
        would silently configure a black hole."""
        with pytest.raises(SystemExit):
            sw.main(["claude-otel"])

    def test_the_dry_run_states_what_is_not_set(self, sw, tmp_path, monkeypatch, capsys):
        p = tmp_path / "settings.json"
        p.write_text(_json.dumps({"model": "opus"}))
        monkeypatch.setattr(sw, "CLAUDE_SETTINGS", p)
        sw.main(["claude-otel", "--endpoint", "dev"])
        out = capsys.readouterr().out
        assert "Deliberately NOT set" in out


class TestRblwReviewOn443:
    """RBLW's review of #443. Grouped because they share a theme: each is a case
    where the tool reported success for something that would not have worked, or
    printed something it should not have."""

    # --- the diff must not show neighbouring env entries ----------------------
    def test_the_output_does_not_show_other_env_entries(self, sw, tmp_path):
        """The one with a real disclosure cost. A whole-file unified diff put the hunk
        inside `env` with three lines of context, pulling in neighbours -- and SKILL.md
        tells the agent to run this and show the output, so it lands in a transcript."""
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"env": {
            "ANTHROPIC_AUTH_TOKEN": "sk-secret-value",
            "AWS_SECRET_ACCESS_KEY": "aws-secret-value",
            "MY_OTHER_VAR": "innocuous",
        }}))
        plan = sw.plan_claude_otel("dev", path=f)
        blob = plan["diff"]
        for secret in ("sk-secret-value", "aws-secret-value", "ANTHROPIC_AUTH_TOKEN",
                       "AWS_SECRET_ACCESS_KEY"):
            assert secret not in blob, f"{secret} leaked into the consent output"
        assert "OTEL_METRICS_EXPORTER" in blob, "it must still show what it writes"

    def test_it_says_how_many_entries_it_is_not_showing(self, sw, tmp_path):
        """Silently omitting is worse than saying 'and 3 others, untouched'."""
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"env": {"A": "1", "B": "2", "C": "3"}}))
        assert "3 other env entries" in sw.plan_claude_otel("dev", path=f)["diff"]

    # --- endpoint typos ------------------------------------------------------
    def test_a_collector_typo_is_rejected(self, sw):
        """`prod` for `prd` was written verbatim as `prod/v1/metrics` with a success
        message -- the silent black hole the named-collector design exists to avoid."""
        with pytest.raises(sw.EndpointError):
            sw.normalise_metrics_endpoint("prod")

    def test_collector_names_are_case_insensitive(self, sw):
        assert sw.normalise_metrics_endpoint("DEV") == sw.normalise_metrics_endpoint("dev")

    def test_a_bare_word_is_not_a_url(self, sw):
        for bad in ("localhost", "catalyst-otel", "ftp://x.invalid", ""):
            with pytest.raises(sw.EndpointError):
                sw.normalise_metrics_endpoint(bad)

    def test_a_real_url_still_works(self, sw):
        assert sw.normalise_metrics_endpoint("https://c.invalid") == "https://c.invalid/v1/metrics"

    def test_the_cli_exits_2_and_writes_nothing_on_a_typo(self, sw, tmp_path, monkeypatch, capsys):
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"model": "opus"}))
        monkeypatch.setattr(sw, "CLAUDE_SETTINGS", f)
        before = f.read_text()
        assert sw.main(["claude-otel", "--endpoint", "prod", "--apply"]) == 2
        assert f.read_text() == before
        assert "Bad --endpoint" in capsys.readouterr().out

    # --- forbidden keys must be caught at plan time ---------------------------
    def test_a_users_existing_logs_endpoint_is_refused_in_the_dry_run(self, sw, tmp_path):
        """Checking the merged env only at apply meant a clean dry run inviting
        --apply, then a refusal exiting 4 naming a key this tool never wrote. That
        user -- one who followed the old `export` advice -- is this PR's audience."""
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"env": {
            "OTEL_EXPORTER_OTLP_ENDPOINT": "https://somewhere.invalid"}}))
        plan = sw.plan_claude_otel("dev", path=f)
        assert not plan["ok"]
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" in plan["reason"]
        assert plan["new_text"] is None

    def test_the_dry_run_and_the_apply_now_agree(self, sw, tmp_path, monkeypatch, capsys):
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"env": {"OTEL_LOGS_EXPORTER": "otlp"}}))
        monkeypatch.setattr(sw, "CLAUDE_SETTINGS", f)
        dry = sw.main(["claude-otel", "--endpoint", "dev"])
        applied = sw.main(["claude-otel", "--endpoint", "dev", "--apply"])
        assert dry == applied == 3, "both paths must refuse, with the same code"

    # --- resource attributes are themselves a list ----------------------------
    def test_existing_resource_attributes_are_merged_not_dropped(self, sw, tmp_path):
        """The `env` block is merged one level up on the grounds that it is shared;
        replacing this value wholesale did the opposite one level down."""
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"env": {
            "OTEL_RESOURCE_ATTRIBUTES": "service.name=foo,team=bar"}}))
        plan = sw.plan_claude_otel("dev", path=f)
        attrs = dict(pair.split("=", 1) for pair in
                     _json.loads(plan["new_text"])["env"]["OTEL_RESOURCE_ATTRIBUTES"].split(","))
        assert attrs["service.name"] == "foo" and attrs["team"] == "bar"
        assert attrs["telemetry.producer"] == "claude-code"

    def test_ours_wins_on_a_key_collision(self, sw):
        merged = sw.merge_resource_attributes(
            "telemetry.producer=something-else", "telemetry.producer=claude-code")
        assert merged == "telemetry.producer=claude-code"

    def test_malformed_existing_attributes_do_not_break_it(self, sw):
        out = sw.merge_resource_attributes("garbage,,=,a=1", "b=2")
        assert "b=2" in out and "a=1" in out

    # --- the write must be atomic --------------------------------------------
    def test_a_failed_write_leaves_the_original_intact(self, sw, tmp_path, monkeypatch, capsys):
        """This file belongs to a live Claude Code session and its settings are strict
        JSON, so a half-written file is a session that cannot parse its own config."""
        f = tmp_path / "settings.json"
        original = _json.dumps({"model": "opus"})
        f.write_text(original)
        plan = sw.plan_claude_otel("dev", path=f)

        real_replace = sw.os.replace
        monkeypatch.setattr(sw.os, "replace",
                            lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
        assert not sw.apply_claude_otel(plan)
        monkeypatch.setattr(sw.os, "replace", real_replace)
        assert f.read_text() == original, "the original must survive a failed write"
        assert not list(tmp_path.glob("*.tmp")), "the temp file must be cleaned up"

    def test_no_temp_file_survives_a_success(self, sw, tmp_path):
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"model": "opus"}))
        assert sw.apply_claude_otel(sw.plan_claude_otel("dev", path=f))
        assert not list(tmp_path.glob("*.tmp"))

    # --- non-ASCII values -----------------------------------------------------
    def test_non_ascii_values_are_not_escaped(self, sw, tmp_path):
        """`ensure_ascii=True` turned a user's own value into \\uXXXX escapes."""
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"env": {"GREETING": "café"}}, ensure_ascii=False),
                     encoding="utf-8")
        plan = sw.plan_claude_otel("dev", path=f)
        assert "café" in plan["new_text"]
        assert "\\u00e9" not in plan["new_text"]

    # --- the docs must not overclaim -----------------------------------------
    def test_the_skill_does_not_promise_byte_for_byte_preservation(self):
        skill = (REPO_ROOT / "skills" / "setup-workspace" / "SKILL.md").read_text()
        assert "preserving\neverything else in the file" not in skill
        assert "not a byte-for-byte edit" in skill

    def test_the_markers_distinguish_added_from_changed(self, sw, tmp_path):
        """Comparing against the already-merged env marked every key `+`, including
        ones being changed -- so the consent output misdescribed its own effect."""
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"env": {
            "OTEL_METRICS_EXPORTER": "otlp",                     # already correct
            "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL": "grpc",       # being changed
        }}))
        out = sw.plan_claude_otel("dev", path=f)["diff"]
        lines = {ln.strip().split('"')[1]: ln.strip()[0]
                 for ln in out.splitlines() if '":' in ln}
        assert lines["CLAUDE_CODE_ENABLE_TELEMETRY"] == "+", out
        assert lines["OTEL_EXPORTER_OTLP_METRICS_PROTOCOL"] == "~", out
        assert lines["OTEL_METRICS_EXPORTER"] == '"', out   # unchanged -> no marker

    def test_an_unreadable_settings_file_is_a_reason_not_a_traceback(self, sw, tmp_path):
        """`plan_otel_settings` already returned a reason for read errors; this path
        raised and aborted the command. In a tool whose contract is "a missing
        precondition is a finding to report, never a stack trace", that is a bug."""
        f = tmp_path / "settings.json"
        f.write_text(_json.dumps({"model": "opus"}))
        f.chmod(0o000)
        try:
            plan = sw.plan_claude_otel("dev", path=f)
        finally:
            f.chmod(0o644)
        assert not plan["ok"]
        assert "could not read" in plan["reason"].lower(), plan["reason"]

    def test_a_non_utf8_settings_file_is_reported_distinctly(self, sw, tmp_path):
        """A different fix from a permissions problem, so a different message."""
        f = tmp_path / "settings.json"
        f.write_bytes(b'{"model": "\xff\xfe invalid"}')
        plan = sw.plan_claude_otel("dev", path=f)
        assert not plan["ok"]
        assert "utf-8" in plan["reason"].lower(), plan["reason"]

    def test_the_cli_exits_3_rather_than_tracebacking(self, sw, tmp_path, monkeypatch):
        f = tmp_path / "settings.json"
        f.write_bytes(b'{"model": "\xff invalid"}')
        monkeypatch.setattr(sw, "CLAUDE_SETTINGS", f)
        assert sw.main(["claude-otel", "--endpoint", "dev"]) == 3
