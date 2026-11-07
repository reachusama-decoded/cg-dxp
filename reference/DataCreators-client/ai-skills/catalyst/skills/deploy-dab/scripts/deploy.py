#!/usr/bin/env python3
"""Deploy a Databricks Asset Bundle to the developer's local dev space.

Non-interactive actuator for the deploy-dab capability skill. Flags in, exit
codes out; the interactive conversation lives in SKILL.md.

Exit codes:
    0  deployed (or, with --dry-run, validated without deploying)
    2  input / config error (precursor missing, bad arguments)
    4  auth: the Databricks CLI could not authenticate (not configured, or a
       validate/deploy call failed authenticating to the workspace)
    5  runtime: `bundle validate` or `bundle deploy` failed for a non-auth reason
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
_OPTIMIZE_LIB = REPO_ROOT / "skills" / "_lib" / "optimize.py"


def _load_optimize_lib():
    """Load the shared redaction helper without packaging _lib as a module."""
    spec = importlib.util.spec_from_file_location("catalyst_lib_optimize", _OPTIMIZE_LIB)
    if not (spec and spec.loader):
        raise RuntimeError(f"could not load optimize lib at {_OPTIMIZE_LIB}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_lib = _load_optimize_lib()


def redact(text: str) -> str:
    """Scrub token-shaped substrings using the shared helper."""
    return _lib.redact_tokens(text)


def load_databricks_yml(bundle_path: Path) -> dict:
    """Parse the bundle's databricks.yml, returning {} for an empty file."""
    path = bundle_path / "databricks.yml"
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open() as handle:
        data = yaml.safe_load(handle)
    return data or {}


def check_precursor(bundle_path: Path, *, require_sources: bool = True) -> list[str]:
    """Return a list of precursor problems; empty means the bundle is ready.

    `require_sources` gates the local `*.job.yml` source-file check. Deploy needs
    those files (it deploys them), but teardown operates on *already-deployed*
    remote resources, so destroy passes `require_sources=False` — a user may have
    restructured or removed the local sources yet still need to tear the deploy
    down. databricks.yml + the `local` target + `target_schema` are still required
    for destroy, since the actuator resolves the schema from them and targets
    `local`.
    """
    problems: list[str] = []
    dbx = bundle_path / "databricks.yml"
    if not dbx.exists():
        problems.append(f"missing {dbx}")
        return problems
    try:
        config = load_databricks_yml(bundle_path)
    except yaml.YAMLError as exc:
        problems.append(f"invalid databricks.yml: {exc}")
        return problems
    except OSError as exc:
        problems.append(f"unreadable databricks.yml: {exc}")
        return problems
    if not isinstance(config, dict):
        problems.append("invalid databricks.yml: expected a top-level mapping")
        return problems
    targets = config.get("targets") or {}
    if "local" not in targets:
        problems.append("databricks.yml has no 'local' target")
    elif not extract_target_schema(config):
        problems.append("local target has no 'target_schema' variable")
    if require_sources and not list(bundle_path.glob("datasets/**/bundle/*.job.yml")):
        problems.append("no datasets/**/bundle/*.job.yml resources found")
    return problems


def _unwrap_default(value: object) -> str | None:
    """A variable may be a bare string or a {default: ...} mapping."""
    if isinstance(value, dict):
        default = value.get("default")
        return default if isinstance(default, str) else None
    return value if isinstance(value, str) else None


def extract_target_schema(config: dict) -> str | None:
    """Read the local target's target_schema (raw, possibly a ${...} template)."""
    local = (config.get("targets") or {}).get("local") or {}
    local_vars = local.get("variables") or {}
    if "target_schema" in local_vars:
        return _unwrap_default(local_vars["target_schema"])
    top_vars = config.get("variables") or {}
    if "target_schema" in top_vars:
        return _unwrap_default(top_vars["target_schema"])
    return None


def target_host(config: dict) -> str | None:
    """Read the local target's literal workspace.host, if present.

    `bundle deploy` resolves auth by matching this host to a profile in
    ~/.databrickscfg (the standard named-profile pattern), so the auth
    pre-check must probe the same host to stay consistent with deploy.
    A ${...} template (no concrete host) is treated as absent.
    """
    if not isinstance(config, dict):
        return None
    local = (config.get("targets") or {}).get("local") or {}
    host = ((local.get("workspace") or {}).get("host"))
    if isinstance(host, str) and host and "${" not in host:
        return host
    return None


def find_repo_root(bundle_path: Path) -> Path:
    """Walk up from the bundle to the repo root (dir holding .git or .claude)."""
    for parent in [bundle_path, *bundle_path.parents]:
        if (parent / ".git").exists() or (parent / ".claude").exists():
            return parent
    return bundle_path


def preferences_path(repo_root: Path) -> Path:
    """Location of the per-user, gitignored preferences file."""
    return repo_root / ".claude" / "markers" / "deploy-dab.user-preferences"


def read_preferences(prefs_path: Path) -> dict:
    """Load the preferences JSON; return {} when absent, unreadable, or corrupt."""
    if not prefs_path.exists():
        return {}
    try:
        with prefs_path.open() as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        print(f"deploy-dab: ignoring corrupt preferences ({exc})", file=sys.stderr)
        return {}
    except OSError as exc:
        print(f"deploy-dab: ignoring unreadable preferences ({exc})", file=sys.stderr)
        return {}
    if not isinstance(data, dict):
        # Valid JSON but not an object (e.g. [], "x", 7) — callers assume a dict,
        # so treat anything non-object as corrupt rather than letting a later
        # prefs.get(...) raise AttributeError.
        print(
            "deploy-dab: ignoring preferences (expected a JSON object)",
            file=sys.stderr,
        )
        return {}
    return data


def is_schema_confirmed(prefs: dict, bundle: str, schema: str) -> bool:
    """True only when this bundle's stored confirmation matches schema."""
    entry = (prefs.get("schema_confirmations") or {}).get(bundle) or {}
    return entry.get("confirmed") is True and entry.get("schema") == schema


def write_schema_confirmation(prefs_path: Path, bundle: str, schema: str) -> None:
    """Persist a confirmed schema for this bundle, creating dirs as needed."""
    prefs = read_preferences(prefs_path)
    confirmations = prefs.setdefault("schema_confirmations", {})
    confirmations[bundle] = {"schema": schema, "confirmed": True}
    prefs_path.parent.mkdir(parents=True, exist_ok=True)
    with prefs_path.open("w") as handle:
        json.dump(prefs, handle, indent=2)


def parse_summary_links(summary_json: str) -> list[dict]:
    """Extract {type, name, url} for every deployed resource that has a URL."""
    data = _loads_lenient(summary_json)
    if not isinstance(data, dict):
        return []
    resources = data.get("resources") or {}
    if not isinstance(resources, dict):
        return []
    links: list[dict] = []
    for resource_type, items in resources.items():
        if not isinstance(items, dict):
            continue
        for key, obj in items.items():
            if not isinstance(obj, dict):
                continue
            url = obj.get("url")
            if not url:
                continue
            links.append({"type": resource_type, "name": obj.get("name") or key, "url": url})
    return links


def _loads_lenient(text: str) -> object:
    """Parse JSON, tolerating a non-JSON prefix (e.g. a CLI progress/warning line).

    `bundle summary --output json` is expected to emit pure JSON on stdout, but
    if the CLI ever prefixes a line, fall back to scanning each `{`/`[` candidate
    and decoding it with `raw_decode`. A first-`{`-to-last-`}` slice is *not* safe:
    a warning prefix containing a `{` (e.g. ``Warning: config {deprecated}``)
    would anchor the slice inside the warning and never recover the real object,
    silently dropping the inventory. Among the candidates that decode, return the
    one whose value reaches furthest into the text, so the real (trailing) summary
    wins even if a warning prefix is itself a complete JSON value. `raw_decode`
    stops at the end of the first valid value, so trailing data is tolerated.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        decoder = json.JSONDecoder()
        best: tuple[int, object] | None = None
        for idx, ch in enumerate(text):
            if ch in "{[":
                try:
                    obj, end = decoder.raw_decode(text, idx)
                except json.JSONDecodeError:
                    continue
                if best is None or end > best[0]:
                    best = (end, obj)
        if best is None:
            raise exc
        return best[1]


def format_links(links: list[dict]) -> str:
    """Render the deployed-resource URLs as a human-readable report."""
    if not links:
        return "deploy-dab: deployed (no resource URLs reported by bundle summary)."
    lines = ["deploy-dab: deployed resources:"]
    for link in links:
        lines.append(f"  [{link['type']}] {link['name']}: {link['url']}")
    return "\n".join(lines)


def parse_resource_inventory(summary_json: str) -> list[dict]:
    """List every resource (type, name) the bundle declares, URL or not.

    Unlike `parse_summary_links` (which keeps only URL-bearing entries for the
    deploy report), teardown must show the full set of resources that a destroy
    would remove, including ones the summary reports as not-yet-deployed.
    """
    data = _loads_lenient(summary_json)
    if not isinstance(data, dict):
        return []
    resources = data.get("resources") or {}
    if not isinstance(resources, dict):
        return []
    inventory: list[dict] = []
    for resource_type, items in resources.items():
        if not isinstance(items, dict):
            continue
        for key, obj in items.items():
            # obj may be a non-dict on unexpected `bundle summary` shapes; only
            # read its "name" when it really is a mapping. (The original
            # one-line ternary was already safe — `or` binds tighter than the
            # conditional, so obj.get was never reached for non-dicts — but the
            # explicit form is harder to misread.)
            if isinstance(obj, dict):
                name = obj.get("name") or key
            else:
                name = key
            inventory.append({"type": resource_type, "name": name})
    return inventory


def format_inventory(inventory: list[dict]) -> str:
    """Render the to-be-destroyed resource inventory as a human-readable report."""
    if not inventory:
        return "deploy-dab: no resources found in the bundle's local target."
    lines = ["deploy-dab: resources in the local target (would be removed):"]
    for item in inventory:
        lines.append(f"  [{item['type']}] {item['name']}")
    return "\n".join(lines)


def run_cli(args: list[str], bundle_path: Path) -> tuple[int, str, str]:
    """Run a `databricks` subcommand in the bundle dir.

    Returns (returncode, stdout, stderr). If the CLI binary is not on PATH,
    returns (127, "", <message>) instead of raising, so callers can route to
    the documented auth/precursor exit codes.
    """
    try:
        proc = subprocess.run(
            ["databricks", *args],
            cwd=bundle_path,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", "databricks CLI not found on PATH"
    return proc.returncode, (proc.stdout or ""), (proc.stderr or "")


def cli_authenticated(bundle_path: Path) -> bool:
    """True when the Databricks CLI has a usable auth context for this bundle.

    `databricks auth env` (bare) only resolves the DEFAULT profile or an
    explicit --host; it ignores DATABRICKS_CONFIG_PROFILE and won't match a
    named OAuth profile. That produces a false negative for the common setup
    where ~/.databrickscfg holds only named profiles and the bundle's target
    selects one by host. So probe with the target's host when we can read it,
    mirroring how `bundle deploy` actually authenticates; fall back to the
    bare check (DEFAULT profile / --host-less) when no literal host is present.
    """
    args = ["auth", "env"]
    try:
        host = target_host(load_databricks_yml(bundle_path))
    except (OSError, yaml.YAMLError):
        host = None
    if host:
        args += ["--host", host]
    rc, _, _ = run_cli(args, bundle_path)
    return rc == 0


def _emit(text: str) -> None:
    """Print user-facing output with tokens redacted."""
    print(redact(text))


# Substrings that mark a `bundle validate`/`deploy` failure as fundamentally an
# authentication problem (an otherwise-valid bundle the CLI can't act on because
# the token is missing/expired/invalid) rather than a bundle defect. The local
# target resolves ${workspace.current_user.short_name} via /scim/v2/Me, so a
# stale token surfaces here as a 403 even though `auth env` reported a profile.
_AUTH_ERROR_SIGNATURES = (
    "/scim/v2/me",
    "invalid access token",
    "403 forbidden",
    "default auth: cannot configure",
    "no default profile",
)


def looks_like_auth_error(text: str) -> bool:
    """True when CLI output indicates an auth failure, not a bundle defect."""
    low = text.lower()
    return any(sig in low for sig in _AUTH_ERROR_SIGNATURES)


def _auth_hint(bundle_path: Path) -> str:
    """U2M remediation for the local dev space, with the target host when known.

    Local deploys go to the developer's own dev space and resolve
    `${workspace.current_user.short_name}` via `/scim/v2/Me`, so the developer
    must authenticate as themselves — user-to-machine (U2M) OAuth via
    `databricks auth login`. M2M client-credentials (`/connect-databricks`) is
    the CI/shared path, not the local one.
    """
    try:
        host = target_host(load_databricks_yml(bundle_path))
    except (OSError, yaml.YAMLError):
        host = None
    login = f"databricks auth login --host {host}" if host else "databricks auth login"
    return (
        f"Log in to your local dev space with U2M user OAuth: `{login}` "
        "(or select your matching ~/.databrickscfg profile). "
        "M2M client-credentials (/connect-databricks) is for CI/shared deploys, not local."
    )


def _run_deploy(bundle_path: Path, *, dry_run: bool) -> int:
    if not cli_authenticated(bundle_path):
        print(
            "deploy-dab: Databricks CLI is not authenticated (or not installed). "
            + _auth_hint(bundle_path),
            file=sys.stderr,
        )
        return 4
    rc, out, err = run_cli(["bundle", "validate", "--target", "local"], bundle_path)
    combined = out + err
    _emit(combined)
    if rc != 0:
        if looks_like_auth_error(combined):
            print(
                "deploy-dab: `bundle validate` failed authenticating to the "
                "workspace. " + _auth_hint(bundle_path) + " Then retry.",
                file=sys.stderr,
            )
            return 4
        print("deploy-dab: `bundle validate` failed.", file=sys.stderr)
        return 5
    if dry_run:
        print("deploy-dab: dry-run complete (validated, not deployed).")
        return 0
    rc, out, err = run_cli(["bundle", "deploy", "--target", "local"], bundle_path)
    combined = out + err
    _emit(combined)
    if rc != 0:
        if looks_like_auth_error(combined):
            print(
                "deploy-dab: `bundle deploy` failed authenticating to the "
                "workspace. " + _auth_hint(bundle_path) + " Then retry.",
                file=sys.stderr,
            )
            return 4
        print("deploy-dab: `bundle deploy` failed.", file=sys.stderr)
        return 5
    rc, summary_out, _ = run_cli(
        ["bundle", "summary", "--target", "local", "--output", "json"], bundle_path
    )
    if rc != 0:
        print("deploy-dab: deployed (could not read `bundle summary`).")
        return 0
    try:
        links = parse_summary_links(summary_out)
    except (json.JSONDecodeError, ValueError, AttributeError, TypeError):
        print("deploy-dab: deployed (could not parse `bundle summary` output).")
        return 0
    _emit(format_links(links))
    return 0


def _run_destroy(bundle_path: Path, *, schema: str | None, confirm: str | None) -> int:
    """Tear down the bundle's `local` deploy behind a deterministic gate.

    Always lists the resources first (redacted), then enforces an explicit
    confirmation that must equal the resolved per-user `target_schema` before any
    `bundle destroy` runs. The target is hardcoded to `local`; there is no way for
    a caller to point this at a shared/prod target.
    """
    if not cli_authenticated(bundle_path):
        print(
            "deploy-dab: Databricks CLI is not authenticated (or not installed). "
            + _auth_hint(bundle_path),
            file=sys.stderr,
        )
        return 4

    rc, summary_out, summary_err = run_cli(
        # Teardown is hardcoded to the `local` target; it must never be steerable
        # to a shared/prod target by a caller.
        ["bundle", "summary", "--target", "local", "--output", "json"], bundle_path
    )
    listed = False
    if rc == 0:
        try:
            inventory = parse_resource_inventory(summary_out)
            _emit(format_inventory(inventory))
            listed = True
        except (json.JSONDecodeError, ValueError, AttributeError, TypeError):
            pass
    if not listed:
        combined = summary_out + summary_err
        # `bundle summary` resolves /scim/v2/Me for the local target, so a stale
        # token surfaces here as an auth failure — route it to re-auth (exit 4)
        # like every other CLI step, not to a generic runtime error.
        if rc != 0 and looks_like_auth_error(combined):
            print(
                "deploy-dab: `bundle summary` failed authenticating to the "
                "workspace. " + _auth_hint(bundle_path) + " Then retry.",
                file=sys.stderr,
            )
            return 4
        detail = summary_err.strip() or summary_out.strip()
        if detail:
            _emit(detail)
        # A failed listing is a runtime failure (exit 5), not a config/confirm
        # problem (exit 2): destroy must never proceed without a reviewable
        # inventory, even if --confirm-destroy was already supplied.
        print(
            "deploy-dab: aborting destroy — `bundle summary` failed, so the "
            "resources that would be removed cannot be listed. Resolve the "
            "failure above and re-run; destroy never proceeds without a "
            "reviewable inventory.",
            file=sys.stderr,
        )
        return 5
    confirmed = confirm is not None and schema is not None and confirm == schema
    if not confirmed:
        print(
            f"deploy-dab: destroy of schema '{schema}' is not confirmed. Review the "
            "resources listed above, then re-run with "
            f"--confirm-destroy '{schema}' to tear down the local deploy. "
            "Deleting data assets (schemas/pipelines/volumes) may be irreversible.",
            file=sys.stderr,
        )
        return 2

    rc, out, err = run_cli(
        ["bundle", "destroy", "--target", "local", "--auto-approve"], bundle_path
    )
    combined = out + err
    _emit(combined)
    if rc != 0:
        if looks_like_auth_error(combined):
            print(
                "deploy-dab: `bundle destroy` failed authenticating to the "
                "workspace. " + _auth_hint(bundle_path) + " Then retry.",
                file=sys.stderr,
            )
            return 4
        print("deploy-dab: `bundle destroy` failed.", file=sys.stderr)
        return 5
    print("deploy-dab: local deploy destroyed.")
    return 0


def confirmation_key(repo_root: Path, bundle_path: Path) -> str:
    """Stable per-bundle identity for confirmations: repo-relative path."""
    try:
        return str(bundle_path.relative_to(repo_root))
    except ValueError:
        return bundle_path.name


def main(argv: list[str] | None = None) -> int:
    """Entry point: dispatch on --mode and return an exit code."""
    parser = argparse.ArgumentParser(
        description="Deploy a Databricks Asset Bundle to the local dev space."
    )
    parser.add_argument("--bundle-path", required=True)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument(
        "--mode",
        choices=["deploy", "precheck", "resolve-schema", "remember-schema", "destroy"],
        default="deploy",
    )
    parser.add_argument("--schema", default=None)
    parser.add_argument(
        "--confirmed-schema",
        default=None,
        help="One-shot deploy confirmation; must equal the bundle's target_schema.",
    )
    parser.add_argument(
        "--confirm-destroy",
        default=None,
        help="Explicit teardown confirmation; must equal the bundle's target_schema.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.mode == "remember-schema" and not args.schema:
        print("deploy-dab: --schema is required for remember-schema.", file=sys.stderr)
        return 2

    bundle_path = Path(args.bundle_path).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root(bundle_path)
    prefs_path = preferences_path(repo_root)
    confirm_key = confirmation_key(repo_root, bundle_path)

    is_destroy = args.mode == "destroy"
    problems = check_precursor(bundle_path, require_sources=not is_destroy)
    if problems:
        for problem in problems:
            print(f"deploy-dab: {problem}", file=sys.stderr)
        if is_destroy:
            # Teardown context: the bundle's local target/databricks.yml is
            # missing or invalid, so there is nothing this actuator can resolve a
            # `local` schema from to tear down. Pointing the user at setup would be
            # wrong here.
            print(
                "deploy-dab: cannot tear down — the bundle's databricks.yml or its "
                "'local' target is missing or invalid.",
                file=sys.stderr,
            )
        else:
            print(
                "deploy-dab: bundle not ready. Run /setup-databricks-asset-bundle first.",
                file=sys.stderr,
            )
        return 2

    try:
        config = load_databricks_yml(bundle_path)
    except (OSError, yaml.YAMLError) as exc:
        # check_precursor already read this file, but guard the re-read against a
        # TOCTOU change (or a future precursor that no longer reads it) so a
        # mid-run unreadable/invalid databricks.yml exits 2, not a stack trace.
        print(f"deploy-dab: could not read databricks.yml ({exc})", file=sys.stderr)
        return 2
    if not isinstance(config, dict):
        # Valid YAML but not a mapping (e.g. a top-level list/scalar) — mirror
        # check_precursor's mapping guard so extract_target_schema(config) below
        # can't hit AttributeError on a non-dict.
        print(
            "deploy-dab: invalid databricks.yml (expected a top-level mapping)",
            file=sys.stderr,
        )
        return 2
    schema = extract_target_schema(config)

    if args.mode == "precheck":
        print("deploy-dab: precursor OK.")
        return 0
    if args.mode == "resolve-schema":
        prefs = read_preferences(prefs_path)
        confirmed = bool(schema) and is_schema_confirmed(prefs, confirm_key, schema)
        print(json.dumps({"bundle": confirm_key, "schema": schema, "confirmed": confirmed}))
        return 0
    if args.mode == "remember-schema":
        if args.schema != schema:
            print(
                f"deploy-dab: --schema '{args.schema}' does not match the bundle's "
                f"target_schema '{schema}'.",
                file=sys.stderr,
            )
            return 2
        write_schema_confirmation(prefs_path, confirm_key, schema)
        print(f"deploy-dab: remembered schema '{schema}' for bundle '{confirm_key}'.")
        return 0

    if args.mode == "destroy":
        return _run_destroy(bundle_path, schema=schema, confirm=args.confirm_destroy)

    if not args.dry_run:
        prefs = read_preferences(prefs_path)
        confirmed = is_schema_confirmed(prefs, confirm_key, schema) or (
            args.confirmed_schema is not None and args.confirmed_schema == schema
        )
        if not confirmed:
            print(
                f"deploy-dab: schema '{schema}' is not confirmed for this bundle. "
                "Confirm via the skill (or pass --confirmed-schema) before deploying.",
                file=sys.stderr,
            )
            return 2

    return _run_deploy(bundle_path, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
