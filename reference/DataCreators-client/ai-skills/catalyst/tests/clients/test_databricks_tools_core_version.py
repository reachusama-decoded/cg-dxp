"""The vendored client's ``VERSION`` file, and the audit trail that depends on it.

Every Databricks SDK call made through ``databricks_tools_core`` carries a
User-Agent built from ``identity.PRODUCT_VERSION``, which lands in the
``system.access.audit`` system table. ``identity._load_version()`` sources that
string from a ``VERSION`` file it finds by walking up from its own directory, and
falls back to ``"0.0.0-unknown"`` with a ``logger.warning`` when there is none.

The vendored package shipped without one, so every call attributed to
``databricks-ai-dev-kit/0.0.0-unknown``.

These tests assert the fix, and they do it by **asking the library** rather than
re-implementing its search: a test that walks the directories itself passes even
when ``_load_version`` is broken, and would not have caught the bug it guards.

The value is deliberately the package's own ``__version__`` (``0.1.0``) and not
the Catalyst plugin version. The two are unrelated: the plugin version describes
this repo, while this string claims to be a release of an upstream project, and
an upstream release number that upstream never shipped is worse than a missing
one — it is a lie in an audit table.

Offline only — no network I/O, no SDK calls.
"""
from __future__ import annotations

import importlib
import logging
import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_PACKAGE_PATH = REPO_ROOT / "skills" / "clients" / "databricks_tools_core"
_VERSION_FILE = _PACKAGE_PATH / "VERSION"

# The sibling integrity tests skip rather than fail when the vendored package is
# absent, because it ships on a feature branch. Match that, for the same reason:
# a hard failure here would report "the VERSION file is missing" on a branch
# where the package it belongs to is missing too, which points at the wrong fix.
_PACKAGE_PRESENT = _PACKAGE_PATH.is_dir()
_SKIP_REASON = (
    "skills/clients/databricks_tools_core is not present on this branch "
    "(it ships on feat/databricks-build-skills)"
)

pytestmark = pytest.mark.skipif(not _PACKAGE_PRESENT, reason=_SKIP_REASON)

# ``identity`` imports ``databricks.sdk`` and ``yaml`` at module scope, so it
# cannot be imported at all without them installed.
_identity = pytest.importorskip(
    "skills.clients.databricks_tools_core.identity",
    reason="requires databricks-sdk and PyYAML (skills/requirements.txt)",
)


def test_version_file_exists_next_to_the_module_that_reads_it() -> None:
    """The file must sit in the package directory, i.e. hop 0 of the walk.

    Any ancestor directory would also be found, but only this location travels
    with the package: it survives being copied, installed, or vendored onward,
    and it shadows a stray ancestor ``VERSION`` belonging to some unrelated
    project that happens to be checked out above it.
    """
    assert _VERSION_FILE.is_file(), (
        f"{_VERSION_FILE.relative_to(REPO_ROOT)} is missing — every SDK call "
        f"will attribute to databricks-ai-dev-kit/0.0.0-unknown in "
        f"system.access.audit"
    )


def test_loaded_version_is_the_packages_own_version() -> None:
    """``PRODUCT_VERSION`` must agree with the package's ``__version__``.

    This is the truthfulness property, and the reason the file does not carry
    the Catalyst plugin version. Asserting equality with ``__version__`` rather
    than a hardcoded ``"0.1.0"`` means a legitimate upstream version bump moves
    both together and this test keeps passing, while a *divergence* — the actual
    defect — fails.
    """
    package = importlib.import_module("skills.clients.databricks_tools_core")

    assert _identity.PRODUCT_VERSION == package.__version__, (
        f"VERSION says {_identity.PRODUCT_VERSION!r} but the package declares "
        f"__version__ = {package.__version__!r}; the User-Agent would claim an "
        f"upstream release that does not exist"
    )


def test_loaded_version_is_not_the_fallback() -> None:
    """Guard the specific regression, stated in the terms the bug had.

    Separate from the agreement test above because it fails differently: this
    one catches "no file was found", that one catches "the file disagrees".
    """
    assert _identity.PRODUCT_VERSION != "0.0.0-unknown", (
        "_load_version() fell through to its fallback — the VERSION file was "
        "not found from the package directory"
    )


def test_resolution_is_silent() -> None:
    """A successful load must not warn.

    ``_load_version`` warns only on the fallback path, so re-running it under
    ``caplog`` distinguishes "resolved correctly" from "resolved to something by
    accident". The module-level ``PRODUCT_VERSION`` was computed at import time,
    before ``caplog`` was installed, so the function has to be called again.
    """
    with caplog_at_warning() as records:
        version = _identity._load_version()

    assert version == _identity.PRODUCT_VERSION
    assert not records, f"_load_version() warned: {[r.getMessage() for r in records]}"


def test_version_file_is_tracked_by_git() -> None:
    """An untracked or ignored ``VERSION`` fixes nothing for anyone else.

    The filesystem assertions above pass against a file that exists only in this
    working tree. Without this, a ``.gitignore`` rule — present or added later —
    would leave every clone back on the fallback while the suite stayed green.
    """
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(_VERSION_FILE.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"{_VERSION_FILE.relative_to(REPO_ROOT)} is not tracked by git — it "
        f"exists here but would be absent for every other clone. "
        f"git said: {result.stderr.strip()}"
    )


def test_version_file_contents_are_a_bare_version() -> None:
    """One line, no adornment.

    ``_load_version`` applies only ``.strip()``, so the whole file body becomes
    the User-Agent. A comment, a ``v`` prefix, or a second line would be
    embedded verbatim in the audit string.
    """
    assert _VERSION_FILE.is_file(), (
        f"{_VERSION_FILE.relative_to(REPO_ROOT)} is missing — run this after "
        f"test_version_file_exists_next_to_the_module_that_reads_it, which "
        f"diagnoses it properly. Guarded here so this test reports the cause "
        f"rather than a bare FileNotFoundError."
    )
    raw = _VERSION_FILE.read_text(encoding="utf-8")
    body = raw.strip()

    assert body, "VERSION is empty — the User-Agent would carry an empty version"
    assert len(body.splitlines()) == 1, f"VERSION must be a single line, got {len(body.splitlines())}"
    assert not body.startswith("v"), f"VERSION must not carry a 'v' prefix, got {body!r}"
    assert "#" not in raw, "VERSION must not contain comments — the file body is the version"


class _Collector(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class caplog_at_warning:
    """Capture WARNING+ records from the ``identity`` logger.

    pytest's own ``caplog`` fixture would do this, but it cannot be requested
    from a helper, and attaching directly keeps the capture scoped to the one
    logger under test rather than the root.
    """

    def __enter__(self) -> list[logging.LogRecord]:
        self._handler = _Collector()
        self._logger = _identity.logger
        self._previous = self._logger.propagate
        self._logger.addHandler(self._handler)
        self._logger.propagate = False
        return self._handler.records

    def __exit__(self, *exc_info: object) -> None:
        self._logger.removeHandler(self._handler)
        self._logger.propagate = self._previous
