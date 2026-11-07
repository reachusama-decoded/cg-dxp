"""Shared promotions.yml reader for deploy-* skills.

Resolves a deployment ID for a (system, target) pair from a YAML file
shaped like:

    astronomer:
      dev: { deployment_id: "dpl-dev-001" }
      qa:  { deployment_id: "dpl-qa-001" }
      prod:{ deployment_id: "dpl-prod-001" }

    databricks:
      dev: { deployment_id: "..." }
      ...
"""

from __future__ import annotations

from pathlib import Path

import yaml


def read_deployment_id(promotions_path: Path, system: str, target: str) -> str:
    """Return the deployment_id for the given system + target.

    Raises FileNotFoundError if the file does not exist, yaml.YAMLError
    for malformed YAML, and KeyError with a helpful message if the
    system, target, or deployment_id field is absent.
    """
    promotions_path = Path(promotions_path)
    if not promotions_path.exists():
        raise FileNotFoundError(
            f"promotions file not found: {promotions_path}"
        )

    data = yaml.safe_load(promotions_path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError(
            f"promotions file {promotions_path} must be a mapping at the top level"
        )

    if system not in data:
        raise KeyError(
            f"promotions file {promotions_path} has no entry for system {system!r}; "
            f"known systems: {sorted(data.keys())}"
        )
    system_block = data[system] or {}
    if not isinstance(system_block, dict):
        raise ValueError(
            f"promotions[{system!r}] must be a mapping of target -> {{deployment_id}}"
        )

    if target not in system_block:
        raise KeyError(
            f"promotions[{system!r}] has no target {target!r}; "
            f"known targets: {sorted(system_block.keys())}"
        )
    target_block = system_block[target] or {}
    if not isinstance(target_block, dict):
        raise ValueError(
            f"promotions[{system!r}][{target!r}] must be a mapping containing deployment_id"
        )

    deployment_id = target_block.get("deployment_id")
    if not deployment_id or not isinstance(deployment_id, str):
        raise KeyError(
            f"promotions[{system!r}][{target!r}] is missing a non-empty "
            f"deployment_id field"
        )
    return deployment_id
