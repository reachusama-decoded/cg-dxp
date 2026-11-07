"""Astro runtime bootstrap — make each data product's modules importable.

`data_products/` is mounted as the Airflow dags folder (docker-compose.override.yml),
so each product lives at a nested path, e.g.
`/usr/local/airflow/dags/portfolio_analytics/dags/...`. Airflow 3 only puts the
dags *root* on `sys.path`, so a product's sibling packages — its `dags/` modules
(e.g. `callbacks`) and its `include/` package (e.g. `include.alerting`) — are not
importable by default, and its DAGs fail to load with `ModuleNotFoundError`.

This adds each product's root dir and its `dags/` dir to `sys.path` so the DAGs
import in the astro runtime. Airflow imports `airflow_local_settings` during
settings initialisation, before the dag-processor parses DAGs, so the paths are
in place in time. Adding a path that contains no modules is harmless.
"""
import os
import socket
import sys
import time
from http import HTTPStatus

DAGS_ROOT = os.environ.get("AIRFLOW__CORE__DAGS_FOLDER") or "/usr/local/airflow/dags"


def _add_data_product_paths(dags_root: str) -> None:
    if not os.path.isdir(dags_root):
        return
    for product in sorted(os.listdir(dags_root)):
        product_dir = os.path.join(dags_root, product)
        if not os.path.isdir(product_dir):
            continue
        for candidate in (product_dir, os.path.join(product_dir, "dags")):
            if os.path.isdir(candidate) and candidate not in sys.path:
                sys.path.insert(0, candidate)


_add_data_product_paths(DAGS_ROOT)


# The heartbeat/task-start patches below reach into private Airflow SDK
# internals (airflow.sdk.execution_time.supervisor) that were verified only
# against this pinned Airflow line. They are OFF unless explicitly opted in, so
# a stock or upgraded runtime keeps upstream behavior.
_TESTED_AIRFLOW_SUPERVISOR_VERSIONS = ("3.1.",)


def _airflow_supervisor_patches_enabled(version: str | None = None) -> bool:
    if os.environ.get("TRAINING_AIRFLOW3_SUPERVISOR_PATCHES") != "1":
        return False
    if version is None:
        try:
            from airflow import __version__ as version
        except Exception:
            return False
    return any(version.startswith(v) for v in _TESTED_AIRFLOW_SUPERVISOR_VERSIONS)


def _patch_cimon_listener_for_airflow3() -> None:
    """Make cimon listener hooks compatible with Airflow 3 runtime hookspecs.

    Why: the bundled cimon listener still declares a `session` parameter on
    task-instance hooks. Airflow 3.1's listener hookspec no longer defines that
    parameter, so plugin registration raises `PluginValidationError` and local
    DAG tests can fail nondeterministically.
    """
    try:
        from cimon.listeners.cimon_runtime import CimonPolicyListener
    except Exception:
        # Cimon plugin not installed/enabled in this runtime.
        return

    original_failed = CimonPolicyListener.on_task_instance_failed
    original_success = CimonPolicyListener.on_task_instance_success

    def _failed_compat(self, previous_state, task_instance, error, **kwargs):
        # RuntimeTaskInstance in Airflow 3 does not expose get_dagrun.
        if not hasattr(task_instance, "get_dagrun"):
            return None
        return original_failed(self, previous_state, task_instance, error, kwargs.get("session"))

    def _success_compat(self, previous_state, task_instance, **kwargs):
        return original_success(self, previous_state, task_instance, kwargs.get("session"))

    # Preserve hook metadata set by @hookimpl so plugin discovery still works.
    _failed_compat.__dict__.update(getattr(original_failed, "__dict__", {}))
    _success_compat.__dict__.update(getattr(original_success, "__dict__", {}))

    CimonPolicyListener.on_task_instance_failed = _failed_compat
    CimonPolicyListener.on_task_instance_success = _success_compat


_patch_cimon_listener_for_airflow3()


def _patch_airflow_task_heartbeat_conflict() -> None:
    """Ignore transient queued-state heartbeat conflicts in local Airflow 3.

    In `airflow dags test`, some task subprocesses can heartbeat before the API
    server has finalized the TI state transition from queued->running. Airflow
    then returns a conflict (`not_running`, `current_state=queued`) and the
    supervisor kills the process immediately, which surfaces as dbt
    KeyboardInterrupt/CANCEL noise.

    This patch only softens that exact transient conflict; all other NOT_FOUND/
    CONFLICT responses keep the default hard-stop behavior.
    """
    if not _airflow_supervisor_patches_enabled():
        return
    try:
        from airflow.sdk.execution_time import supervisor as _supervisor
    except Exception:
        return

    original = _supervisor.ActivitySubprocess._send_heartbeat_if_needed

    def _is_transient_queued_conflict(detail: object) -> bool:
        if not isinstance(detail, dict):
            return False
        nested = detail.get("detail")
        if isinstance(nested, dict):
            current_state = nested.get("current_state")
            reason = nested.get("reason")
            if current_state == "queued" and reason == "not_running":
                return True
            if reason == "running_elsewhere" and nested.get("current_hostname") == socket.gethostname():
                return True
        return False

    def _is_transient_failed_conflict(detail: object) -> bool:
        if not isinstance(detail, dict):
            return False
        nested = detail.get("detail")
        if not isinstance(nested, dict):
            return False
        return nested.get("reason") == "not_running" and nested.get("current_state") in {
            "failed",
            "up_for_retry",
        }

    def _patched_send_heartbeat_if_needed(self):
        if (time.monotonic() - self._last_heartbeat_attempt) < _supervisor.MIN_HEARTBEAT_INTERVAL:
            return
        if self._terminal_state:
            return

        self._last_heartbeat_attempt = time.monotonic()
        try:
            self.client.task_instances.heartbeat(self.id, pid=self._process.pid)
            self._last_successful_heartbeat = time.monotonic()
            self.failed_heartbeats = 0
        except _supervisor.ServerResponseError as e:
            status = e.response.status_code
            if status in {HTTPStatus.NOT_FOUND, HTTPStatus.CONFLICT}:
                if status == HTTPStatus.CONFLICT and _is_transient_queued_conflict(e.detail):
                    _supervisor.log.warning(
                        "Transient queued-state heartbeat conflict; will retry",
                        detail=e.detail,
                        status_code=status,
                        ti_id=self.id,
                    )
                    return
                if status == HTTPStatus.CONFLICT and _is_transient_failed_conflict(e.detail):
                    _supervisor.log.warning(
                        "Transient failed-state heartbeat conflict; suppressing forced termination",
                        detail=e.detail,
                        status_code=status,
                        ti_id=self.id,
                    )
                    return
                self.process_log.error(
                    "Server indicated the task shouldn't be running anymore. Terminating process",
                    detail=e.detail,
                )
                self.kill(_supervisor.signal.SIGTERM, force=True)
                self.process_log.error("Task killed!")
                self._terminal_state = _supervisor.SERVER_TERMINATED
            else:
                self._handle_heartbeat_failures(e)
        except Exception as e:  # pragma: no cover - defensive parity with upstream
            self._handle_heartbeat_failures(e)

    # Avoid stacking wrappers across repeated DAG parses.
    if getattr(_supervisor.ActivitySubprocess._send_heartbeat_if_needed, "__name__", "") != "_patched_send_heartbeat_if_needed":
        _supervisor.ActivitySubprocess._send_heartbeat_if_needed = _patched_send_heartbeat_if_needed


_patch_airflow_task_heartbeat_conflict()


def _patch_airflow_task_start_race() -> None:
    """Retry transient execution-API errors when a task subprocess starts.

    In local `airflow dags test`, we intermittently see `ServerResponseError`
    from `task_instances.start(...)` right after the scheduler has queued the
    task. A short retry window avoids treating this as a hard task failure when
    the API/server state is still converging.
    """
    if not _airflow_supervisor_patches_enabled():
        return
    try:
        from airflow.sdk.execution_time import supervisor as _supervisor
    except Exception:
        return

    original = _supervisor.ActivitySubprocess._on_child_started

    def _is_retryable_start_error(err: Exception) -> bool:
        if not isinstance(err, _supervisor.ServerResponseError):
            return False
        status = err.response.status_code
        if status not in {HTTPStatus.NOT_FOUND, HTTPStatus.CONFLICT}:
            return False
        detail = getattr(err, "detail", None)
        if not isinstance(detail, dict):
            return True
        nested = detail.get("detail")
        if not isinstance(nested, dict):
            return True
        reason = nested.get("reason")
        current_state = nested.get("current_state")
        if reason in {"not_running", "running_elsewhere"}:
            return True
        if status == HTTPStatus.NOT_FOUND:
            return True
        if status == HTTPStatus.CONFLICT and current_state in {"queued", "running"}:
            return True
        return False

    def _is_already_running_start_conflict(err: Exception) -> bool:
        if not isinstance(err, _supervisor.ServerResponseError):
            return False
        if err.response.status_code != HTTPStatus.CONFLICT:
            return False
        detail = getattr(err, "detail", None)
        if isinstance(detail, dict):
            nested = detail.get("detail")
            if isinstance(nested, dict):
                if nested.get("current_state") == "running":
                    return True
                if nested.get("previous_state") == "running":
                    return True
                if nested.get("reason") == "invalid_state":
                    return True
        return "invalid state" in str(detail).lower()

    def _patched_on_child_started(self, ti, dag_rel_path, bundle_info):
        retries = 5
        delay_seconds = 0.35
        for attempt in range(1, retries + 1):
            try:
                return original(self, ti, dag_rel_path, bundle_info)
            except Exception as err:
                if _is_already_running_start_conflict(err):
                    _supervisor.log.warning(
                        "Duplicate task-start conflict; killing duplicate launcher "
                        "and leaving the authoritative TI state to the server",
                        status_code=getattr(getattr(err, "response", None), "status_code", None),
                        detail=getattr(err, "detail", None),
                        ti_id=self.id,
                    )
                    self.kill(_supervisor.signal.SIGKILL, force=True)
                    self._exit_code = 0
                    return
                if attempt >= retries or not _is_retryable_start_error(err):
                    raise
                _supervisor.log.warning(
                    "Transient task start API error; retrying",
                    attempt=attempt,
                    max_retries=retries,
                    status_code=getattr(getattr(err, "response", None), "status_code", None),
                    detail=getattr(err, "detail", None),
                )
                time.sleep(delay_seconds)

    if getattr(_supervisor.ActivitySubprocess._on_child_started, "__name__", "") != "_patched_on_child_started":
        _supervisor.ActivitySubprocess._on_child_started = _patched_on_child_started


_patch_airflow_task_start_race()
