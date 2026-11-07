"""Unit tests for deploy-dab's deploy.py actuator."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import deploy
import pytest


def _write_bundle(
    root: Path, *, with_local: bool = True, with_job: bool = True, with_schema: bool = True
) -> Path:
    """Stub a minimal data-product bundle under root and return the bundle dir."""
    bundle = root / "data_products" / "demo"
    bundle.mkdir(parents=True)
    targets = ""
    if with_local:
        variables = ""
        if with_schema:
            variables = textwrap.dedent(
                """\
                    variables:
                      target_schema: ${workspace.current_user.short_name}
                """
            )
        targets = textwrap.dedent(
            """
            targets:
              local:
                mode: development
                default: true
            """
        )
        if variables:
            targets += textwrap.indent(variables, "    ")
    (bundle / "databricks.yml").write_text(
        "bundle:\n  name: demo\n" + targets
    )
    if with_job:
        job = bundle / "datasets" / "sales" / "bundle"
        job.mkdir(parents=True)
        (job / "sales.job.yml").write_text("resources:\n  jobs: {}\n")
    return bundle


def test_redact_scrubs_token_shaped_text():
    assert "dapi" not in deploy.redact("token=dapiABCDEF0123456789xyz")


def test_check_precursor_passes_for_complete_bundle(tmp_path):
    bundle = _write_bundle(tmp_path)
    assert deploy.check_precursor(bundle) == []


def test_check_precursor_reports_missing_databricks_yml(tmp_path):
    problems = deploy.check_precursor(tmp_path / "nope")
    assert any("databricks.yml" in p for p in problems)


def test_check_precursor_reports_missing_local_target(tmp_path):
    bundle = _write_bundle(tmp_path, with_local=False)
    problems = deploy.check_precursor(bundle)
    assert any("local" in p for p in problems)


def test_check_precursor_reports_missing_job_files(tmp_path):
    bundle = _write_bundle(tmp_path, with_job=False)
    problems = deploy.check_precursor(bundle)
    assert any("job.yml" in p for p in problems)


def test_extract_schema(tmp_path):
    bundle = _write_bundle(tmp_path)
    config = deploy.load_databricks_yml(bundle)
    assert deploy.extract_target_schema(config) == "${workspace.current_user.short_name}"


def test_preferences_path_under_claude_markers(tmp_path):
    assert deploy.preferences_path(tmp_path) == (
        tmp_path / ".claude" / "markers" / "deploy-dab.user-preferences"
    )


def test_find_repo_root_walks_up_to_git(tmp_path):
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "data_products" / "demo"
    nested.mkdir(parents=True)
    assert deploy.find_repo_root(nested) == tmp_path


def test_write_then_confirm_roundtrip(tmp_path):
    prefs_path = deploy.preferences_path(tmp_path)
    deploy.write_schema_confirmation(prefs_path, "demo", "knxa")
    prefs = deploy.read_preferences(prefs_path)
    assert deploy.is_schema_confirmed(prefs, "demo", "knxa") is True


def test_changed_schema_is_not_confirmed(tmp_path):
    prefs_path = deploy.preferences_path(tmp_path)
    deploy.write_schema_confirmation(prefs_path, "demo", "knxa")
    prefs = deploy.read_preferences(prefs_path)
    assert deploy.is_schema_confirmed(prefs, "demo", "someone_else") is False


def test_read_preferences_missing_file_returns_empty(tmp_path):
    assert deploy.read_preferences(tmp_path / "nope.json") == {}


_SUMMARY = json.dumps(
    {
        "resources": {
            "jobs": {
                "sales_job": {
                    "id": "123",
                    "name": "[dev knxa] sales",
                    "url": "https://dbc.example.com/jobs/123",
                }
            },
            "pipelines": {
                "dq_pipeline": {"id": "9", "url": "https://dbc.example.com/pipelines/9"}
            },
            "experiments": {"noop": {"id": "x"}},  # no url -> skipped
        }
    }
)


def test_parse_summary_links_extracts_urls():
    links = deploy.parse_summary_links(_SUMMARY)
    urls = {item["url"] for item in links}
    assert urls == {
        "https://dbc.example.com/jobs/123",
        "https://dbc.example.com/pipelines/9",
    }


def test_parse_summary_links_prefers_resource_name():
    links = deploy.parse_summary_links(_SUMMARY)
    job = next(item for item in links if item["type"] == "jobs")
    assert job["name"] == "[dev knxa] sales"


def test_format_links_lists_each_resource():
    out = deploy.format_links(deploy.parse_summary_links(_SUMMARY))
    assert "https://dbc.example.com/jobs/123" in out
    assert "[jobs]" in out


def test_format_links_handles_empty():
    assert "no resource URLs" in deploy.format_links([])


def test_main_precheck_fails_without_bundle(tmp_path, capsys):
    rc = deploy.main(["--bundle-path", str(tmp_path / "nope"), "--mode", "precheck"])
    assert rc == 2
    assert "setup-databricks-asset-bundle" in capsys.readouterr().err


def test_main_precheck_passes(tmp_path):
    bundle = _write_bundle(tmp_path)
    rc = deploy.main(["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "precheck"])
    assert rc == 0


def test_main_resolve_schema_emits_json(tmp_path, capsys):
    bundle = _write_bundle(tmp_path)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "resolve-schema"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["bundle"] == "data_products/demo"
    assert payload["confirmed"] is False


def test_main_remember_then_resolve_reports_confirmed(tmp_path, capsys):
    bundle = _write_bundle(tmp_path)
    common = ["--bundle-path", str(bundle), "--repo-root", str(tmp_path)]
    deploy.main([*common, "--mode", "remember-schema", "--schema",
                 "${workspace.current_user.short_name}"])
    capsys.readouterr()
    deploy.main([*common, "--mode", "resolve-schema"])
    assert json.loads(capsys.readouterr().out)["confirmed"] is True


_SCHEMA = "${workspace.current_user.short_name}"


def test_main_deploy_routes_auth_failure_to_exit_4(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: False)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 4


def test_main_deploy_returns_5_on_validate_failure(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", lambda args, path: (1, "validate boom", ""))
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 5


def test_main_deploy_returns_5_on_deploy_failure(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)

    def fake_run(args, path):
        if "deploy" in args:
            return (1, "deploy boom", "")
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 5


def test_main_dry_run_validates_without_deploying(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    calls: list[list[str]] = []

    def fake_run(args, path):
        calls.append(args)
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    rc = deploy.main(["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--dry-run"])
    assert rc == 0
    assert any("validate" in c for c in calls)
    assert not any("deploy" in c for c in calls)


def test_main_deploy_happy_path_prints_links(tmp_path, monkeypatch, capsys):
    bundle = _write_bundle(tmp_path)

    def fake_run(args, path):
        if "summary" in args:
            return (0, _SUMMARY, "")
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 0
    assert "https://dbc.example.com/jobs/123" in capsys.readouterr().out


# --- precursor / schema-presence ---

def test_check_precursor_reports_missing_target_schema(tmp_path):
    bundle = _write_bundle(tmp_path, with_schema=False)
    problems = deploy.check_precursor(bundle)
    assert any("target_schema" in p for p in problems)


# --- missing CLI binary ---

def test_run_cli_missing_binary_returns_127(tmp_path, monkeypatch):
    def boom(*_a, **_k):
        raise FileNotFoundError("databricks")

    monkeypatch.setattr(deploy.subprocess, "run", boom)
    rc, out, err = deploy.run_cli(["auth", "env"], tmp_path)
    assert rc == 127 and out == "" and "not found" in err


def test_main_deploy_missing_cli_routes_to_exit_4(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "run_cli", lambda args, path: (127, "", "not found"))
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 4


def test_unauthenticated_message_recommends_u2m_login_with_host(tmp_path, monkeypatch, capsys):
    host = "https://dbc.example.com"
    bundle = _write_bundle_with_host(tmp_path, host)
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: False)
    rc = deploy._run_deploy(bundle, dry_run=False)
    assert rc == 4
    err = capsys.readouterr().err
    assert f"databricks auth login --host {host}" in err
    assert "/connect-databricks" in err  # M2M noted as the CI/shared path only


# --- confirmation enforcement ---

def test_main_deploy_blocked_when_schema_unconfirmed(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", lambda args, path: (0, "ok", ""))
    rc = deploy.main(["--bundle-path", str(bundle), "--repo-root", str(tmp_path)])
    assert rc == 2


def test_main_deploy_allowed_with_stored_confirmation(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    common = ["--bundle-path", str(bundle), "--repo-root", str(tmp_path)]
    deploy.main([*common, "--mode", "remember-schema", "--schema", _SCHEMA])
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", lambda args, path: (0, "ok", ""))
    rc = deploy.main(common)
    assert rc == 0


# --- remember-schema validation ---

def test_remember_schema_without_schema_returns_2(tmp_path, capsys):
    bundle = _write_bundle(tmp_path)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "remember-schema"]
    )
    assert rc == 2
    assert "--schema is required" in capsys.readouterr().err


def test_remember_schema_rejects_mismatched_schema(tmp_path, capsys):
    bundle = _write_bundle(tmp_path)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--mode", "remember-schema", "--schema", "typo_schema"]
    )
    assert rc == 2
    assert "does not match" in capsys.readouterr().err


# --- summary robustness ---

def test_main_summary_invalid_json_does_not_crash(tmp_path, monkeypatch, capsys):
    bundle = _write_bundle(tmp_path)

    def fake_run(args, path):
        if "summary" in args:
            return (0, "Warning: progress\n{not valid json", "")
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 0
    assert "could not parse" in capsys.readouterr().out


def test_main_summary_nonzero_rc_reports_fallback(tmp_path, monkeypatch, capsys):
    bundle = _write_bundle(tmp_path)

    def fake_run(args, path):
        if "summary" in args:
            return (1, "", "boom")
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 0
    assert "could not read" in capsys.readouterr().out


def test_parse_summary_links_non_dict_returns_empty():
    assert deploy.parse_summary_links("[]") == []
    assert deploy.parse_summary_links("null") == []


# --- redaction of deploy + summary output ---

def test_main_deploy_output_is_redacted(tmp_path, monkeypatch, capsys):
    bundle = _write_bundle(tmp_path)
    secret = "dapiABCDEF0123456789abcdef"

    def fake_run(args, path):
        if "deploy" in args:
            return (0, f"deploying with token={secret}", "")
        if "summary" in args:
            return (0, json.dumps({"resources": {}}), "")
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 0
    assert secret not in capsys.readouterr().out


def test_main_summary_links_are_redacted(tmp_path, monkeypatch, capsys):
    bundle = _write_bundle(tmp_path)
    secret = "dapiABCDEF0123456789abcdef"
    summary = json.dumps(
        {"resources": {"jobs": {"j": {"name": f"job-{secret}",
                                      "url": "https://dbc.example.com/jobs/1"}}}}
    )

    def fake_run(args, path):
        if "summary" in args:
            return (0, summary, "")
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert secret not in out
    assert "https://dbc.example.com/jobs/1" in out


def test_confirmation_key_uses_relative_path(tmp_path):
    bundle = tmp_path / "data_products" / "sales"
    assert deploy.confirmation_key(tmp_path, bundle) == "data_products/sales"


def test_check_precursor_reports_non_mapping_yaml(tmp_path):
    bundle = tmp_path / "data_products" / "demo"
    bundle.mkdir(parents=True)
    (bundle / "databricks.yml").write_text("not-a-mapping\n")
    problems = deploy.check_precursor(bundle)
    assert any("expected a top-level mapping" in p for p in problems)


def test_check_precursor_reports_unreadable_databricks_yml(tmp_path):
    bundle = tmp_path / "data_products" / "demo"
    bundle.mkdir(parents=True)
    (bundle / "databricks.yml").mkdir()  # a directory -> open() raises OSError
    problems = deploy.check_precursor(bundle)
    assert any("unreadable databricks.yml" in p for p in problems)


def test_read_preferences_unreadable_file_returns_empty(tmp_path, capsys):
    prefs = tmp_path / "prefs.json"
    prefs.mkdir()  # a directory -> open() raises OSError
    assert deploy.read_preferences(prefs) == {}
    assert "unreadable preferences" in capsys.readouterr().err


def test_main_summary_call_includes_target_local(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    summary_calls: list[list[str]] = []

    def fake_run(args, path):
        if "summary" in args:
            summary_calls.append(args)
            return (0, _SUMMARY, "")
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert summary_calls and "--target" in summary_calls[0]
    assert "local" in summary_calls[0]


# --- auth errors surfaced at validate/deploy route to exit 4 (Finding B) ---

_SCIM_403 = (
    "Error: Invalid access token. [ReqId: x] (403 403)\n"
    "Endpoint: GET https://host/api/2.0/preview/scim/v2/Me?\n"
    "HTTP Status: 403 Forbidden\n"
)


def test_validate_auth_error_routes_to_exit_4(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", lambda args, path: (1, "", _SCIM_403))
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 4


def test_validate_non_auth_error_still_exit_5(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", lambda args, path: (1, "schema error: bad field", ""))
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 5


def test_deploy_auth_error_routes_to_exit_4(tmp_path, monkeypatch):
    bundle = _write_bundle(tmp_path)

    def fake_run(args, path):
        if "deploy" in args:
            return (1, "", _SCIM_403)
        return (0, "ok", "")

    monkeypatch.setattr(deploy, "cli_authenticated", lambda _path: True)
    monkeypatch.setattr(deploy, "run_cli", fake_run)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    assert rc == 4


def test_looks_like_auth_error_discriminates():
    assert deploy.looks_like_auth_error("HTTP Status: 403 Forbidden") is True
    assert deploy.looks_like_auth_error("Invalid access token") is True
    assert deploy.looks_like_auth_error("unknown field 'foo' in bundle") is False
    # A misconfigured `authentication` block in databricks.yml is a bundle defect
    # (exit 5), not a token problem (exit 4) — the bare word must not match.
    assert deploy.looks_like_auth_error("authentication type not recognized") is False


# --- host-aware auth gate (Finding C) ---

def _write_bundle_with_host(root: Path, host: str | None) -> Path:
    bundle = root / "data_products" / "demo"
    bundle.mkdir(parents=True)
    workspace = f"\n    workspace:\n      host: {host}" if host else ""
    (bundle / "databricks.yml").write_text(
        "bundle:\n  name: demo\n"
        "targets:\n  local:\n    mode: development\n    default: true"
        f"{workspace}\n"
        "    variables:\n      target_schema: ${workspace.current_user.short_name}\n"
    )
    job = bundle / "datasets" / "sales" / "bundle"
    job.mkdir(parents=True)
    (job / "sales.job.yml").write_text("resources:\n  jobs: {}\n")
    return bundle


def test_target_host_reads_literal_host(tmp_path):
    bundle = _write_bundle_with_host(tmp_path, "https://example.cloud.databricks.com")
    config = deploy.load_databricks_yml(bundle)
    assert deploy.target_host(config) == "https://example.cloud.databricks.com"


def test_target_host_ignores_template_host(tmp_path):
    bundle = _write_bundle_with_host(tmp_path, "${var.workspace_host}")
    config = deploy.load_databricks_yml(bundle)
    assert deploy.target_host(config) is None


def test_target_host_none_when_absent(tmp_path):
    bundle = _write_bundle_with_host(tmp_path, None)
    config = deploy.load_databricks_yml(bundle)
    assert deploy.target_host(config) is None


def test_cli_authenticated_probes_target_host(tmp_path, monkeypatch):
    """The auth gate must pass the target host to `auth env` so named OAuth
    profiles resolve the same way `bundle deploy` does (Finding C)."""
    bundle = _write_bundle_with_host(tmp_path, "https://example.cloud.databricks.com")
    seen = {}

    def fake_run(args, path):
        seen["args"] = args
        return (0, "{}", "")

    monkeypatch.setattr(deploy, "run_cli", fake_run)
    assert deploy.cli_authenticated(bundle) is True
    assert seen["args"] == ["auth", "env", "--host", "https://example.cloud.databricks.com"]


def test_cli_authenticated_falls_back_to_bare_without_host(tmp_path, monkeypatch):
    bundle = _write_bundle_with_host(tmp_path, None)
    seen = {}

    def fake_run(args, path):
        seen["args"] = args
        return (0, "{}", "")

    monkeypatch.setattr(deploy, "run_cli", fake_run)
    assert deploy.cli_authenticated(bundle) is True
    assert seen["args"] == ["auth", "env"]



# --- teardown gate (--mode destroy) ---

def _destroy_run_cli(records, *, summary=None, destroy=(0, "Destroy complete!", "")):
    """Fake run_cli that records calls and answers summary/destroy subcommands."""
    summary_payload = (0, _SUMMARY, "") if summary is None else summary

    def fake(args, path):
        records.append(list(args))
        if "summary" in args:
            return summary_payload
        if "destroy" in args:
            return destroy
        return (0, "ok", "")

    return fake


def _run_destroy_main(tmp_path, monkeypatch, *, confirm=None, authed=True,
                      summary=None, destroy=(0, "Destroy complete!", "")):
    bundle = _write_bundle(tmp_path)
    records: list[list[str]] = []
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _p: authed)
    monkeypatch.setattr(deploy, "run_cli",
                        _destroy_run_cli(records, summary=summary, destroy=destroy))
    argv = ["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "destroy"]
    if confirm is not None:
        argv += ["--confirm-destroy", confirm]
    rc = deploy.main(argv)
    return rc, records


def test_destroy_unconfirmed_lists_and_blocks(tmp_path, monkeypatch, capsys):
    rc, records = _run_destroy_main(tmp_path, monkeypatch, confirm=None)
    out = capsys.readouterr()
    assert rc == 2
    # listed resources first...
    assert "would be removed" in out.out
    # ...and never ran destroy
    assert not any("destroy" in c for c in records)
    assert "not confirmed" in out.err


def test_destroy_confirmed_runs_destroy_local_only(tmp_path, monkeypatch, capsys):
    rc, records = _run_destroy_main(tmp_path, monkeypatch, confirm=_SCHEMA)
    assert rc == 0
    destroy_calls = [c for c in records if "destroy" in c]
    assert destroy_calls == [["bundle", "destroy", "--target", "local", "--auto-approve"]]
    assert "local deploy destroyed" in capsys.readouterr().out


def test_destroy_wrong_schema_rejected(tmp_path, monkeypatch):
    rc, records = _run_destroy_main(tmp_path, monkeypatch, confirm="not-the-schema")
    assert rc == 2
    assert not any("destroy" in c for c in records)


def test_destroy_only_ever_targets_local(tmp_path, monkeypatch):
    rc, records = _run_destroy_main(tmp_path, monkeypatch, confirm=_SCHEMA)
    assert rc == 0
    for call in records:
        if "--target" in call:
            assert call[call.index("--target") + 1] == "local"


def test_destroy_unauthenticated_exits_4(tmp_path, monkeypatch, capsys):
    rc, records = _run_destroy_main(tmp_path, monkeypatch, confirm=_SCHEMA, authed=False)
    assert rc == 4
    assert "databricks auth login" in capsys.readouterr().err
    assert not any("destroy" in c for c in records)


def test_destroy_failure_routes_exit_5(tmp_path, monkeypatch):
    rc, _ = _run_destroy_main(tmp_path, monkeypatch, confirm=_SCHEMA,
                              destroy=(1, "", "boom: some non-auth error"))
    assert rc == 5


def test_destroy_auth_error_routes_exit_4(tmp_path, monkeypatch):
    rc, _ = _run_destroy_main(tmp_path, monkeypatch, confirm=_SCHEMA,
                              destroy=(1, "", "Error: 403 Forbidden on /scim/v2/Me"))
    assert rc == 4


def test_destroy_output_is_redacted(tmp_path, monkeypatch, capsys):
    secret = "dapi0123456789abcdef0123456789ab"
    rc, _ = _run_destroy_main(tmp_path, monkeypatch, confirm=_SCHEMA,
                              destroy=(0, f"deleting {secret}", ""))
    assert rc == 0
    assert secret not in capsys.readouterr().out


def test_parse_summary_links_tolerates_prefixed_json():
    noisy = "Warning: something\n" + _SUMMARY
    links = deploy.parse_summary_links(noisy)
    assert any(l["url"] for l in links)


def test_parse_resource_inventory_includes_urlless_resources():
    inventory = deploy.parse_resource_inventory(_SUMMARY)
    types = {item["type"] for item in inventory}
    assert "jobs" in types
    # experiments has no url but must still be listed for teardown
    assert any(item["type"] == "experiments" for item in inventory)


def test_destroy_listing_output_is_redacted(tmp_path, monkeypatch, capsys):
    # Token embedded in a resource *name* must be scrubbed in the inventory listing
    # (the contract calls out the teardown listing specifically).
    secret = "dapifedcba9876543210fedcba987654"
    noisy_summary = json.dumps(
        {"resources": {"jobs": {"j1": {"name": f"job-{secret}"}}}}
    )
    rc, _ = _run_destroy_main(
        tmp_path, monkeypatch, confirm=None, summary=(0, noisy_summary, "")
    )
    assert rc == 2
    assert secret not in capsys.readouterr().out


def test_destroy_aborts_when_summary_unparseable_even_if_confirmed(tmp_path, monkeypatch):
    # rc==0 but unparseable JSON: the inventory can't be shown, so destroy must
    # abort with exit 5 (runtime failure) and never run `bundle destroy`, even
    # when the schema is already confirmed. The contract guarantees "list first"
    # unconditionally.
    rc, records = _run_destroy_main(
        tmp_path, monkeypatch, confirm=_SCHEMA,
        summary=(0, "Header comment\nnot json at all", ""),
    )
    assert rc == 5
    assert not any("destroy" in c for c in records)


def test_destroy_summary_failure_is_runtime_exit_5(tmp_path, monkeypatch):
    # `bundle summary` failing for a non-auth reason is a runtime error (exit 5),
    # not a config/confirm error (exit 2) — even with no confirmation supplied.
    rc, records = _run_destroy_main(
        tmp_path, monkeypatch, confirm=None,
        summary=(1, "", "Error: workspace temporarily unavailable"),
    )
    assert rc == 5
    assert not any("destroy" in c for c in records)


def test_destroy_summary_auth_failure_routes_exit_4(tmp_path, monkeypatch):
    # An auth failure surfacing at `bundle summary` (e.g. a 403 on /scim/v2/Me
    # from a stale token) routes to re-auth (exit 4), like every other CLI step.
    rc, records = _run_destroy_main(
        tmp_path, monkeypatch, confirm=_SCHEMA,
        summary=(1, "", "Error: 403 Forbidden on /scim/v2/Me"),
    )
    assert rc == 4
    assert not any("destroy" in c for c in records)


def test_read_preferences_non_object_json_returns_empty(tmp_path, capsys):
    # Valid JSON that is not an object (list/string/number) must be treated as
    # corrupt so callers that do prefs.get(...) never hit AttributeError.
    for payload in ("[]", '["a"]', '"hello"', "7", "true"):
        prefs = tmp_path / "prefs.json"
        prefs.write_text(payload)
        assert deploy.read_preferences(prefs) == {}
    assert "expected a JSON object" in capsys.readouterr().err


def test_read_preferences_object_json_is_returned(tmp_path):
    prefs = tmp_path / "prefs.json"
    prefs.write_text('{"schema_confirmations": {"demo": {"schema": "x", "confirmed": true}}}')
    loaded = deploy.read_preferences(prefs)
    assert isinstance(loaded, dict)
    assert deploy.is_schema_confirmed(loaded, "demo", "x") is True


def test_parse_resource_inventory_tolerates_non_dict_entries():
    # Non-dict resource entries (unexpected `bundle summary` shapes) must not crash;
    # the key is used as the name.
    summary = json.dumps(
        {"resources": {"jobs": {"j1": "not-a-dict", "j2": ["also", "bad"], "j3": {"name": "ok"}}}}
    )
    inventory = deploy.parse_resource_inventory(summary)
    names = {item["name"] for item in inventory}
    assert names == {"j1", "j2", "ok"}


def test_main_unreadable_databricks_yml_after_precheck_returns_2(tmp_path, monkeypatch, capsys):
    # Simulate a TOCTOU change: check_precursor passes, but the subsequent raw
    # re-read raises. main() must exit 2, not throw a stack trace.
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "check_precursor", lambda _p, **_k: [])

    def boom(_bundle_path):
        raise OSError("disappeared")

    monkeypatch.setattr(deploy, "load_databricks_yml", boom)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "precheck"]
    )
    assert rc == 2
    assert "could not read databricks.yml" in capsys.readouterr().err


def test_main_invalid_yaml_after_precheck_returns_2(tmp_path, monkeypatch, capsys):
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "check_precursor", lambda _p, **_k: [])

    def boom(_bundle_path):
        raise deploy.yaml.YAMLError("bad yaml")

    monkeypatch.setattr(deploy, "load_databricks_yml", boom)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "resolve-schema"]
    )
    assert rc == 2
    assert "could not read databricks.yml" in capsys.readouterr().err


def test_main_non_mapping_databricks_yml_after_precheck_returns_2(tmp_path, monkeypatch, capsys):
    # Valid YAML that parses to a non-mapping (list/scalar) must exit 2, not throw
    # AttributeError in extract_target_schema. Reachable only via a TOCTOU swap
    # because check_precursor normally rejects non-mappings first.
    bundle = _write_bundle(tmp_path)
    monkeypatch.setattr(deploy, "check_precursor", lambda _p, **_k: [])
    monkeypatch.setattr(deploy, "load_databricks_yml", lambda _p: ["not", "a", "mapping"])
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "resolve-schema"]
    )
    assert rc == 2
    assert "expected a top-level mapping" in capsys.readouterr().err


# --- Blocker 1: destroy must not require local source files (precursor) -------

def test_destroy_proceeds_without_job_sources(tmp_path, monkeypatch, capsys):
    # A bundle whose *.job.yml sources were restructured/removed must still be
    # tear-downable: precursor's source-file check is skipped for destroy.
    bundle = _write_bundle(tmp_path, with_job=False)
    records: list[list[str]] = []
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _p: True)
    monkeypatch.setattr(
        deploy, "run_cli", _destroy_run_cli(records, destroy=(0, "Destroy complete!", ""))
    )
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "destroy",
         "--confirm-destroy", _SCHEMA]
    )
    out = capsys.readouterr()
    assert rc == 0
    assert "local deploy destroyed" in out.out
    # Did NOT bail out via the deploy precursor's setup message.
    assert "setup-databricks-asset-bundle" not in out.err
    assert "no datasets" not in out.err


def test_deploy_still_requires_job_sources(tmp_path, monkeypatch, capsys):
    # The same missing-sources bundle must STILL be blocked for a real deploy.
    bundle = _write_bundle(tmp_path, with_job=False)
    monkeypatch.setattr(deploy, "cli_authenticated", lambda _p: True)
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path),
         "--confirmed-schema", _SCHEMA]
    )
    err = capsys.readouterr().err
    assert rc == 2
    assert "no datasets/**/bundle/*.job.yml" in err
    assert "setup-databricks-asset-bundle" in err


def test_destroy_missing_databricks_yml_uses_teardown_message(tmp_path, monkeypatch, capsys):
    # Destroy still needs databricks.yml/local target; the recovery message must
    # be teardown-appropriate, not "run setup".
    bundle = tmp_path / "data_products" / "demo"
    bundle.mkdir(parents=True)  # no databricks.yml at all
    rc = deploy.main(
        ["--bundle-path", str(bundle), "--repo-root", str(tmp_path), "--mode", "destroy",
         "--confirm-destroy", _SCHEMA]
    )
    err = capsys.readouterr().err
    assert rc == 2
    assert "cannot tear down" in err
    assert "setup-databricks-asset-bundle" not in err


# --- Blocker 2: _loads_lenient must survive a '{' inside a warning prefix ------

def test_loads_lenient_pure_json():
    assert deploy._loads_lenient('{"resources": {"jobs": {}}}') == {"resources": {"jobs": {}}}


def test_loads_lenient_warning_prefix_without_brace():
    text = 'Warning: deprecated flag\n{"resources": {"jobs": {"a": {"url": "u"}}}}'
    assert deploy._loads_lenient(text)["resources"]["jobs"]["a"]["url"] == "u"


def test_loads_lenient_warning_prefix_containing_brace():
    # The exact failure mode RBAP flagged: a '{' inside the warning would anchor a
    # first-'{'-to-last-'}' slice inside the warning and lose the real object.
    text = 'Warning: config {deprecated} ignored\n{"resources": {"jobs": {"a": {"url": "u"}}}}'
    parsed = deploy._loads_lenient(text)
    assert parsed["resources"]["jobs"]["a"]["url"] == "u"


def test_loads_lenient_no_json_reraises():
    with pytest.raises(json.JSONDecodeError):
        deploy._loads_lenient("Warning: nothing parseable here {oops")


def test_parse_summary_links_survives_brace_in_warning():
    text = 'Warn {x}\n{"resources": {"jobs": {"j1": {"name": "n", "url": "https://h/j"}}}}'
    links = deploy.parse_summary_links(text)
    assert links == [{"type": "jobs", "name": "n", "url": "https://h/j"}]


def test_loads_lenient_warning_is_itself_valid_json():
    # Even if a warning prefix is a complete JSON value, the real trailing summary
    # (which reaches furthest into the text) must win.
    text = 'Warning: {"old": 1} is deprecated\n{"resources": {"jobs": {"a": {"url": "u"}}}}'
    parsed = deploy._loads_lenient(text)
    assert parsed["resources"]["jobs"]["a"]["url"] == "u"
