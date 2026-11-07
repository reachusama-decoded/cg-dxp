#!/usr/bin/env python3
"""Tests for refresh_detect.py — stdlib unittest, tempfile fixtures."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# Make sibling import work whether invoked as a script or module.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import refresh_detect  # noqa: E402


SAMPLE_BODY = """\
bundle:
  name: my-product

targets:
  dev:
    workspace:
      host: https://example.cloud.databricks.com
"""


def _file_with_header(version: int, body: str = SAMPLE_BODY) -> str:
    # header on line 3, matching the prose contract
    return f"# product file\n#\n# Catalyst-version: {version}\n{body}"


def _invoke(argv):
    """Run refresh_detect.main with captured stdout+stderr; return
    (exit_code, stdout_str, stderr_str, parsed_json_or_None)."""
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = refresh_detect.main(argv)
    stdout = out.getvalue()
    stderr = err.getvalue()
    parsed = None
    blob = stdout if stdout.strip() else stderr
    try:
        parsed = json.loads(blob)
    except json.JSONDecodeError:
        parsed = None
    return code, stdout, stderr, parsed


class HelperTests(unittest.TestCase):
    def test_find_header_version_present(self):
        txt = _file_with_header(7)
        self.assertEqual(refresh_detect.find_header_version(txt), 7)

    def test_find_header_version_absent(self):
        self.assertIsNone(refresh_detect.find_header_version("no header here"))

    def test_find_header_version_tolerates_trailing_context(self):
        # Templates in this skill (databricks.yml, dataset.job.yml, etc.) carry
        # parenthesized context after the version number — the regex must
        # capture the int and ignore the rest of the line.
        txt = "# product file\n#\n# Catalyst-version: 2 (per-product layout)\n"
        self.assertEqual(refresh_detect.find_header_version(txt), 2)

    def test_find_header_version_rejects_non_numeric_suffix(self):
        # Guardrail: "2abc" must NOT parse as version 2 — anything stuck to
        # the digits should fail the match, not silently truncate.
        txt = "# Catalyst-version: 2abc\n"
        self.assertIsNone(refresh_detect.find_header_version(txt))

    def test_strip_header_removes_only_header_line(self):
        txt = _file_with_header(3)
        stripped = refresh_detect.strip_header(txt)
        self.assertNotIn("Catalyst-version", stripped)
        self.assertIn("bundle:", stripped)
        # the surrounding lines should still be there
        self.assertIn("# product file", stripped)

    def test_strip_header_no_op_when_missing(self):
        txt = "abc\ndef\n"
        self.assertEqual(refresh_detect.strip_header(txt), txt)


class RefreshDetectIntegrationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo_root = Path(self._tmp.name)
        self.rel_file = "data_products/foo/databricks.yml"
        self.on_disk = self.repo_root / self.rel_file
        self.on_disk.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self._tmp.cleanup()

    # --- helpers --------------------------------------------------------

    def _write(self, text: str) -> None:
        self.on_disk.write_text(text, encoding="utf-8")

    def _bootstrap(self) -> dict:
        code, _, _, parsed = _invoke(
            [
                "--repo-root",
                str(self.repo_root),
                "--file",
                self.rel_file,
                "--bootstrap",
            ]
        )
        self.assertEqual(code, 0)
        return parsed

    def _normal(self, version: int, expected_hash: str) -> dict:
        code, _, _, parsed = _invoke(
            [
                "--repo-root",
                str(self.repo_root),
                "--file",
                self.rel_file,
                "--template-version",
                str(version),
                "--template-hash",
                expected_hash,
            ]
        )
        self.assertEqual(code, 0)
        return parsed

    # --- the six required cases ----------------------------------------

    def test_1_bootstrap_creates_sidecar_with_right_content(self):
        self._write(_file_with_header(1))
        parsed = self._bootstrap()

        self.assertEqual(parsed["verdict"], "bootstrapped")
        sidecar = (
            self.repo_root
            / ".catalyst"
            / "baselines"
            / (self.rel_file + ".sha256")
        )
        self.assertTrue(sidecar.exists())

        expected = refresh_detect.sha256_hex(
            refresh_detect.strip_header(_file_with_header(1))
        )
        self.assertEqual(sidecar.read_text(encoding="utf-8").strip(), expected)
        self.assertEqual(parsed["on_disk_hash"], expected)

    def test_2_hand_edited_file_post_header_change(self):
        original = _file_with_header(1)
        self._write(original)
        self._bootstrap()

        # User edits the body — but keeps the same Catalyst-version.
        edited = _file_with_header(
            1, body=SAMPLE_BODY + "\n# user added this line\n"
        )
        self._write(edited)

        expected_hash = refresh_detect.sha256_hex(
            refresh_detect.strip_header(original)
        )  # template unchanged
        parsed = self._normal(1, expected_hash)

        self.assertEqual(parsed["verdict"], "skip-hand-edited")
        self.assertIn("hand-edited", parsed["reason"])
        self.assertIsNotNone(parsed["diff_summary"])

    def test_3_untouched_file_no_template_change(self):
        original = _file_with_header(1)
        self._write(original)
        self._bootstrap()

        expected_hash = refresh_detect.sha256_hex(
            refresh_detect.strip_header(original)
        )
        parsed = self._normal(1, expected_hash)

        self.assertEqual(parsed["verdict"], "safe-to-regenerate")
        self.assertIn("no template change", parsed["reason"])

    def test_4_untouched_file_template_changed(self):
        original = _file_with_header(1)
        self._write(original)
        self._bootstrap()

        # Caller passes a different template hash — template body changed
        # upstream while on-disk still matches its baseline.
        new_template_hash = "f" * 64
        parsed = self._normal(1, new_template_hash)

        self.assertEqual(parsed["verdict"], "safe-to-regenerate")
        self.assertIn("template changed", parsed["reason"])

    def test_5_missing_baseline_without_bootstrap(self):
        self._write(_file_with_header(1))
        expected_hash = refresh_detect.sha256_hex(
            refresh_detect.strip_header(_file_with_header(1))
        )
        parsed = self._normal(1, expected_hash)

        self.assertEqual(parsed["verdict"], "missing")
        self.assertIn("--bootstrap", parsed["reason"])

    def test_6_header_version_drift(self):
        original = _file_with_header(1)
        self._write(original)
        self._bootstrap()

        # On-disk header is still 1, but caller says template is now 2.
        expected_hash = refresh_detect.sha256_hex(
            refresh_detect.strip_header(original)
        )
        parsed = self._normal(2, expected_hash)

        self.assertEqual(parsed["verdict"], "skip-hand-edited")
        self.assertIn("template version drifted", parsed["reason"])
        self.assertEqual(parsed["header_version"], 1)
        self.assertEqual(parsed["expected_version"], 2)

    # --- hard-error path (nice-to-have, but cheap) ---------------------

    def test_missing_on_disk_file_is_hard_error(self):
        # don't write the file
        code, stdout, stderr, parsed = _invoke(
            [
                "--repo-root",
                str(self.repo_root),
                "--file",
                self.rel_file,
                "--bootstrap",
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["verdict"], "error")


if __name__ == "__main__":
    unittest.main()
