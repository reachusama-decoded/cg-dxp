"""
Test Script Generator for dbt-unit-test.

Renders a ready-to-run pytest file from a list of TestCase objects
using the Jinja2 template in ``templates/pytest_test.py.j2``.

Also serialises test cases to JSON for inspection / replay without re-calling the LLM.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from engine.generation.generator import TestCase

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_GENERATED_DIR = Path(__file__).parent.parent / "generated"


class TestScriptGenerator:
    """
    Renders Jinja2 template → pytest `.py` test script.

    Parameters
    ----------
    output_dir : directory where generated scripts are written.
                 Defaults to ``dbt-unit-test/generated/``.
    """

    def __init__(self, output_dir: str | Path | None = None):
        self.output_dir = Path(output_dir) if output_dir else _GENERATED_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def generate_pytest_script(
        self,
        model_name: str,
        test_cases: list[TestCase],
    ) -> Path:
        """
        Render and write a pytest script for ``model_name``.

        Returns the path to the written file.
        """
        try:
            from jinja2 import Environment, FileSystemLoader, StrictUndefined  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "jinja2 not installed. Run: "
                "pip install --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ jinja2"
            ) from exc

        env = Environment(
            loader        = FileSystemLoader(str(_TEMPLATES_DIR)),
            undefined     = StrictUndefined,
            trim_blocks   = True,
            lstrip_blocks = True,
        )
        # Custom filter: tojson with indent support
        env.filters["tojson"] = lambda v, indent=None: json.dumps(v, indent=indent, default=str)

        # Guard against prompt-injection via LLM-generated test identifiers becoming
        # executable Python class/function names. model_name and test_id are interpolated
        # directly into class identifiers in the rendered file.
        _IDENT_RE = re.compile(r"^[A-Za-z_]\w*$")

        def _validate_ident(value: str, field: str) -> None:
            if not _IDENT_RE.match(value):
                raise ValueError(
                    f"Unsafe value for Python identifier {field!r}: {value!r}. "
                    "Expected ^[A-Za-z_]\\w*$. This may indicate prompt-injection in "
                    "the source SQL or Jira content — review Step 2 output before retrying."
                )

        _validate_ident(model_name, "model_name")
        for tc in test_cases:
            _validate_ident(getattr(tc, "test_id", ""), "test_id")

        template = env.get_template("pytest_test.py.j2")
        filename = f"test_{model_name}_ai_generated.py"
        rendered = template.render(
            model_name       = model_name,
            test_cases       = test_cases,
            generated_at     = datetime.now(tz=timezone.utc).isoformat(),
            output_filename  = filename,
        )

        output_path = self.output_dir / filename
        output_path.write_text(rendered, encoding="utf-8")
        logger.info("Test script written → %s", output_path)
        return output_path

    def save_test_cases_json(
        self,
        model_name: str,
        test_cases: list[TestCase],
    ) -> Path:
        """
        Persist test cases as JSON.

        Useful for:
          - Replaying tests without re-calling the LLM (``--json`` flag in ``run_from_json.py`` CLI).
          - Human review / editing of generated test cases.
        """
        json_path = self.output_dir / f"{model_name}_test_cases.json"
        json_path.write_text(
            json.dumps([asdict(tc) for tc in test_cases], indent=2, default=str),
            encoding="utf-8",
        )
        logger.info("Test cases JSON saved → %s", json_path)
        return json_path

    def load_test_cases_json(self, json_path: str | Path) -> list[TestCase]:
        """Load previously saved test cases from JSON (skip LLM call).

        Accepts two formats:
          - Flat array:   [{...}, {...}]                         (canonical storage format)
          - Wrapped dict: {"test_cases": [{...}, ...], ...}     (agent Step 3 output format)
        """
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"Test cases JSON not found: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        # Unwrap agent-emitted {"test_cases": [...]} envelope if present
        if isinstance(data, dict):
            if "test_cases" in data:
                data = data["test_cases"]
            else:
                raise ValueError(
                    f"Expected a JSON array or dict with 'test_cases' key, "
                    f"got dict with keys: {list(data.keys())}"
                )
        if not isinstance(data, list):
            raise ValueError(
                f"Expected a JSON array of test cases, got {type(data).__name__}"
            )
        return [TestCase(**item) for item in data]

    def print_summary(self, model_name: str, test_cases: list[TestCase]) -> None:
        """Print a formatted summary table to stdout."""
        print(f"\n{'─' * 70}")
        print(f"  dbt-unit-test — Generated {len(test_cases)} test cases for: {model_name}")
        print(f"{'─' * 70}")
        for tc in test_cases:
            tags = ", ".join(tc.tags) if tc.tags else "—"
            print(f"  [{tc.test_id}] [{tc.category:15s}] {tc.description[:50]:50s}  tags={tags}")
        print(f"{'─' * 70}\n")
