#!/usr/bin/env python3
"""audit_dbt_config: dbt project + profile snapshot for optimize-compute.

Pure parser. Reads ``dbt_project.yml`` and the resolved ``profiles.yml``
(plus ``.dbt/manifest.json`` if present) and emits a normalized JSON
snapshot that the evaluator (``evaluate_findings.py``) reads. Does NOT
call ``dbt parse`` so it has no transitive dbt install dependency — only
PyYAML.

CLI:
    python audit_dbt_config.py --project-dir . [--profile-name myproject] [--target dev] --output dbt-config.json

Exit codes:
    0  success
    2  bad CLI args / required file missing / malformed YAML
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover
    print(
        "error: PyYAML is required. Install via "
        "pip install --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Profile discovery + load
# ---------------------------------------------------------------------------


def _resolve_profiles_path(explicit: str | None) -> Path:
    """Mirror dbt's discovery order: $DBT_PROFILES_DIR -> ~/.dbt."""
    if explicit:
        return Path(explicit).expanduser()
    env_dir = os.environ.get("DBT_PROFILES_DIR")
    if env_dir:
        return Path(env_dir).expanduser() / "profiles.yml"
    return Path.home() / ".dbt" / "profiles.yml"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    with path.open("r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"failed to parse {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not parse to a mapping")
    return data


# ---------------------------------------------------------------------------
# Project / profile normalisation
# ---------------------------------------------------------------------------


def _walk_model_configs(
    node: Any, path: list[str], out: dict[str, dict[str, Any]]
) -> None:
    """Walk a dbt_project.yml ``models:`` tree, collecting ``+key: value`` pairs.

    A node is a folder if it has dict children that are themselves folders or
    +-prefixed keys. We record one entry per path-prefix, with the +-keys
    flattened to a config dict.
    """
    if not isinstance(node, dict):
        return
    plus_config = {k.lstrip("+"): v for k, v in node.items() if k.startswith("+")}
    if plus_config:
        out["/".join(path)] = plus_config
    for k, v in node.items():
        if k.startswith("+"):
            continue
        if isinstance(v, dict):
            _walk_model_configs(v, path + [k], out)


def extract_model_materializations(
    dbt_project: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    models_tree = dbt_project.get("models") or {}
    out: dict[str, dict[str, Any]] = {}
    _walk_model_configs(models_tree, [], out)
    return out


# ---------------------------------------------------------------------------
# Jinja literal-default extraction
#
# The dominant EDO `profiles.yml` shape uses nested `env_var()` / `var()`
# calls with a literal-string fallback as the deepest argument:
#
#   "{{ env_var('DBT_HTTP_PATH',
#                var('http_path',
#                    '/sql/1.0/warehouses/a0e57263293aee36'))
#    }}"
#
# Without an env var or a project-level `var:` binding the actual value
# dbt resolves to at runtime IS that innermost literal. We pre-pass the
# templated string and pull out the deepest literal default so the
# downstream resolver (in `_classify_http_path` on the evaluator side)
# can classify the target without an API call. This is documented in
# `references/dbt-config-audit.md` as the fallback for the dominant
# `profiles.yml` shape.
# ---------------------------------------------------------------------------


def extract_jinja_literal_default(value: Any) -> Any:
    """Walk a templated Jinja string for the innermost literal-string default.

    Handles three common shapes:

    - ``"{{ var('NAME', 'literal_default') }}"``
    - ``"{{ env_var('VAR', 'literal_default') }}"``
    - Nested: ``"{{ env_var('X', var('y', 'literal_default')) }}"``

    The "default" argument position is the *second* positional arg to
    ``var()`` / ``env_var()``; a single-arg call (``env_var('FOO')``) has
    no default and the input is returned unchanged. Nested calls in the
    default slot are descended recursively until a literal string is
    found.

    Returns the innermost literal-string default when one is found; returns
    the input unchanged otherwise (including for non-string inputs, for
    single-arg calls with no default, and for templated strings whose
    default chain bottoms out in something non-literal).
    """
    if not isinstance(value, str):
        return value
    if "{{" not in value:
        return value
    # Pull out everything between `{{` and `}}` so we operate on the
    # expression, not the surrounding text.
    m = re.search(r"\{\{(.+?)\}\}", value, re.DOTALL)
    if not m:
        return value
    expr = m.group(1).strip()

    def _split_top_args(s: str) -> list[str]:
        """Split a comma-separated arg list at depth-0 commas only."""
        out: list[str] = []
        depth = 0
        buf: list[str] = []
        i = 0
        while i < len(s):
            ch = s[i]
            if ch in ("'", '"'):
                # Skip over a string literal so commas inside don't split.
                quote = ch
                buf.append(ch)
                i += 1
                while i < len(s) and s[i] != quote:
                    buf.append(s[i])
                    i += 1
                if i < len(s):
                    buf.append(s[i])
                    i += 1
                continue
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "," and depth == 0:
                out.append("".join(buf).strip())
                buf = []
                i += 1
                continue
            buf.append(ch)
            i += 1
        tail = "".join(buf).strip()
        if tail:
            out.append(tail)
        return out

    def _resolve(node: str) -> str | None:
        """Return the innermost literal default of `node`, or None.

        Expected `node` shape: ``env_var(...)``, ``var(...)``, or a bare
        quoted literal. Anything else returns None (not a literal we can
        confidently pull out).
        """
        node = node.strip()
        # Bare quoted literal: this IS the default value, return it.
        if len(node) >= 2 and node[0] in ("'", '"') and node[-1] == node[0]:
            return node[1:-1]
        # env_var(...) or var(...) call: parse the args.
        m_call = re.match(r"^(env_var|var)\s*\((.*)\)\s*$", node, re.DOTALL)
        if not m_call:
            return None
        args = _split_top_args(m_call.group(2))
        if len(args) < 2:
            # Single-arg call -- no default. We deliberately do NOT
            # return the first arg (the env-var name) here.
            return None
        # The default is the second positional argument. Recurse into
        # it: it may itself be a nested var()/env_var(...) call whose
        # own default we want, or a bare literal.
        return _resolve(args[1])

    resolved = _resolve(expr)
    return resolved if resolved is not None else value


def extract_target_outputs(
    profiles: dict[str, Any], profile_name: str
) -> dict[str, dict[str, Any]]:
    profile = profiles.get(profile_name)
    if not isinstance(profile, dict):
        return {}
    outputs = profile.get("outputs") or {}
    if not isinstance(outputs, dict):
        return {}
    normalized: dict[str, dict[str, Any]] = {}
    for target_name, cfg in outputs.items():
        if not isinstance(cfg, dict):
            continue
        # Pre-resolve templated string fields to their innermost literal
        # defaults when available. This lets the evaluator's http_path
        # classifier work on the dominant EDO `profiles.yml` shape
        # without needing the env vars set at scan time.
        raw_http_path = cfg.get("http_path")
        raw_host = cfg.get("host")
        raw_cluster_id = cfg.get("cluster_id")
        normalized[target_name] = {
            "type": cfg.get("type"),
            "threads": cfg.get("threads"),
            "http_path": extract_jinja_literal_default(raw_http_path),
            "host": extract_jinja_literal_default(raw_host),
            "cluster_id": extract_jinja_literal_default(raw_cluster_id),
            "catalog": cfg.get("catalog") or cfg.get("database"),
            "schema": cfg.get("schema"),
            # Preserve the raw value (with templates intact) for
            # diagnostics. The evaluator uses `http_path`; this is only
            # for the report's "we extracted the literal default from
            # X" note.
            "http_path_raw": raw_http_path if raw_http_path != extract_jinja_literal_default(raw_http_path) else None,
        }
    return normalized


def _classify_compute_ref(http_path: Any, cluster_id: Any) -> tuple[str, str] | None:
    """Classify target compute from literal-resolved profile values.

    Returns ``(compute_id, kind)`` where kind is one of:
    ``warehouse | all_purpose_cluster | job_cluster | cluster_unknown``.

    Warehouse paths are classified definitively. Cluster paths (and bare
    cluster_id strings) cannot be classified as all-purpose vs job cluster
    without calling /clusters/get, which this parser-only audit does not do;
    they are returned as ``cluster_unknown`` so DBX-WASTE-010 emits a
    warning (low confidence), not a hard error. Higher-fidelity callers
    can override the kind in their own snapshot.
    """
    candidate = http_path if isinstance(http_path, str) and http_path else cluster_id
    if not isinstance(candidate, str):
        return None
    s = candidate.strip()
    if not s:
        return None

    m = re.match(r"^/sql/1\.0/warehouses/([\w-]+)$", s)
    if m:
        return m.group(1), "warehouse"

    m = re.match(r"^/sql/protocolv1/o/\d+/([\w-]+)$", s)
    if m:
        return m.group(1), "cluster_unknown"

    if re.match(r"^[\w-]+$", s):
        # Bare cluster_id shape in profiles.yml.
        return s, "cluster_unknown"

    return None


def build_resolved_compute(
    targets: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Build evaluator-facing resolved_compute map keyed by compute id."""
    resolved: dict[str, dict[str, Any]] = {}
    for target_name, cfg in (targets or {}).items():
        if not isinstance(cfg, dict):
            continue
        classified = _classify_compute_ref(cfg.get("http_path"), cfg.get("cluster_id"))
        if not classified:
            continue
        compute_id, kind = classified
        resolved[compute_id] = {
            "kind": kind,
            "source": "audit_dbt_config.profile_target_classifier",
            "target": target_name,
        }
    return resolved


def extract_dispatch(dbt_project: dict[str, Any]) -> list[dict[str, Any]]:
    raw = dbt_project.get("dispatch") or []
    return raw if isinstance(raw, list) else []


def extract_vars(dbt_project: dict[str, Any]) -> dict[str, Any]:
    raw = dbt_project.get("vars") or {}
    return raw if isinstance(raw, dict) else {}


def extract_pre_post_hooks(
    materializations: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Surface pre_hook / post_hook configs declared at the model-tree level."""
    out: dict[str, dict[str, Any]] = {}
    for prefix, cfg in materializations.items():
        hooks = {
            k: cfg[k]
            for k in ("pre_hook", "post_hook", "pre-hook", "post-hook")
            if k in cfg
        }
        if hooks:
            out[prefix] = hooks
    return out


# ---------------------------------------------------------------------------
# Optional manifest merge
# ---------------------------------------------------------------------------


def merge_manifest(
    snapshot: dict[str, Any], manifest_path: Path
) -> None:
    """If a manifest.json is present, merge per-model resolved configs.

    Manifest is optional; failures here are non-fatal — we record a warning
    and continue with the YAML-only snapshot.
    """
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        snapshot["manifest"] = {
            "status": "skipped",
            "reason": f"failed to read {manifest_path}: {type(exc).__name__}: {exc}",
        }
        return

    nodes = manifest.get("nodes", {}) or {}
    resolved: dict[str, dict[str, Any]] = {}
    for unique_id, node in nodes.items():
        if not isinstance(node, dict):
            continue
        if node.get("resource_type") != "model":
            continue
        cfg = node.get("config") or {}
        resolved[unique_id] = {
            "materialized": cfg.get("materialized"),
            "schema": cfg.get("schema"),
            "alias": cfg.get("alias"),
            "tags": cfg.get("tags"),
            "pre_hook": cfg.get("pre_hook") or cfg.get("pre-hook"),
            "post_hook": cfg.get("post_hook") or cfg.get("post-hook"),
            "meta": cfg.get("meta"),
            "cluster_by": cfg.get("cluster_by"),
            "partition_by": cfg.get("partition_by"),
        }
    snapshot["manifest"] = {
        "status": "merged",
        "path": str(manifest_path),
        "model_count": len(resolved),
        "models": resolved,
    }


# ---------------------------------------------------------------------------
# Top-level audit
# ---------------------------------------------------------------------------


def audit(
    project_dir: Path,
    profile_name: str | None,
    target: str | None,
    profiles_path: str | None,
) -> dict[str, Any]:
    project_file = project_dir / "dbt_project.yml"
    dbt_project = load_yaml(project_file)
    resolved_profile_name = profile_name or dbt_project.get("profile") or ""
    if not resolved_profile_name:
        raise ValueError(
            "could not resolve profile name. Pass --profile-name or set "
            "`profile:` in dbt_project.yml"
        )

    profiles_file = _resolve_profiles_path(profiles_path)
    profiles = load_yaml(profiles_file)

    model_materializations = extract_model_materializations(dbt_project)
    targets = extract_target_outputs(profiles, resolved_profile_name)
    selected_target = target or (profiles.get(resolved_profile_name) or {}).get(
        "target"
    )

    snapshot: dict[str, Any] = {
        "schema_version": "1.0.0",
        "project_dir": str(project_dir),
        "project_file": str(project_file),
        "profiles_file": str(profiles_file),
        "profile_name": resolved_profile_name,
        "target": selected_target,
        "project_name": dbt_project.get("name"),
        "profile_targets": targets,
        "selected_target_config": targets.get(selected_target) if selected_target else None,
        "resolved_compute": build_resolved_compute(targets),
        "model_materializations": model_materializations,
        "model_pre_post_hooks": extract_pre_post_hooks(model_materializations),
        "dispatch": extract_dispatch(dbt_project),
        "vars": extract_vars(dbt_project),
    }

    manifest_path = project_dir / "target" / "manifest.json"
    legacy_manifest = project_dir / ".dbt" / "manifest.json"
    if manifest_path.exists():
        merge_manifest(snapshot, manifest_path)
    elif legacy_manifest.exists():
        merge_manifest(snapshot, legacy_manifest)
    else:
        snapshot["manifest"] = {
            "status": "absent",
            "reason": "no manifest.json found at target/ or .dbt/; using YAML-only snapshot",
        }

    return snapshot


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="audit_dbt_config",
        description=__doc__.splitlines()[0] if __doc__ else "",
    )
    p.add_argument(
        "--project-dir",
        type=str,
        required=True,
        help="Path to the dbt project root (contains dbt_project.yml)",
    )
    p.add_argument(
        "--profile-name",
        type=str,
        default=None,
        help="Profile name (overrides `profile:` in dbt_project.yml)",
    )
    p.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target name (overrides `target:` in profiles.yml)",
    )
    p.add_argument(
        "--profiles-path",
        type=str,
        default=None,
        help="Override path to profiles.yml (defaults to $DBT_PROFILES_DIR or ~/.dbt/profiles.yml)",
    )
    p.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to write the normalized JSON snapshot",
    )
    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.is_dir():
        print(f"error: --project-dir not found: {project_dir}", file=sys.stderr)
        return 2

    try:
        snapshot = audit(
            project_dir=project_dir,
            profile_name=args.profile_name,
            target=args.target,
            profiles_path=args.profiles_path,
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True))
    print(
        f"wrote dbt snapshot ({len(snapshot.get('model_materializations', {}))} model-tree entries) to {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
