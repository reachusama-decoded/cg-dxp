"""Schema validation of the evaluator's output against the bundled JSON Schema.

The schema lives one directory above ``scripts/`` (sibling ``templates/`` dir).
``_validate_against_schema`` is called from the CLI entry to fail before
writing a malformed findings file; tests can also call it directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# Schema lives two dirs above this file: ``rules/`` -> ``scripts/`` -> skill
# root, then into ``templates/``. Kept as a module-level Path so callers can
# monkey-patch for tests if needed.
_SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent.parent / "templates"
    / "compute-optimization-findings.json"
)


def load_schema() -> dict[str, Any]:
    """Load and return the bundled compute-optimization-findings JSON schema.

    Raises RuntimeError when the file is missing so callers see an
    actionable error rather than a generic FileNotFoundError.
    """
    if not _SCHEMA_PATH.exists():
        raise RuntimeError(f"schema not found at {_SCHEMA_PATH}")
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _validate_against_schema(result: dict[str, Any]) -> list[str]:
    """Return a list of jsonschema validation errors against the bundled
    schema. Empty list means the result conforms. ``jsonschema`` is a hard
    dependency declared in scripts/requirements.txt; a missing install is
    treated as a setup error rather than silently skipping validation.
    """
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise RuntimeError(
            "jsonschema not installed; run `pip install -r "
            "skills/optimize-compute/scripts/requirements.txt`"
        ) from exc

    schema = load_schema()
    validator = Draft202012Validator(schema)
    return [
        f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}"
        for err in validator.iter_errors(result)
    ]
