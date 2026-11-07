"""pytest config for the behavior-test harness's *internal* unit tests.

Note: there is no pytest-driven case dispatcher here. Behavior cases are
run via `bin/bt` (or `python -m tests.behavior`); pytest only sees the
unit tests under `tests/behavior/tests/`.

This file remains so pytest treats `tests/behavior/` as a package and
picks up the project root for module imports.
"""
from __future__ import annotations
