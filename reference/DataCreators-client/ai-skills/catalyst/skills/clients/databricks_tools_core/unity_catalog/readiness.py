"""
Unity Catalog - Readiness Probes

Boolean access checks used by pre-flight skills to answer "can this identity
actually do the thing?" before a build or deploy is attempted.

These differ from the rest of `unity_catalog` in one deliberate way: a permission
failure is an **answer**, not an error.  `list_catalogs()` raising PermissionDenied
means "the call failed"; `check_catalog_access()` returning False means "you do not
have access" — which is exactly what a readiness report needs to print.  Only
genuinely unexpected conditions (a malformed argument) raise.

Exception classes moved between modules across databricks-sdk releases, and this
package pins a wide range (>=0.30.0,<1.0.0).  These probes therefore catch broad
`Exception` rather than importing specific error types, so a probe can never fail
closed because of an SDK refactor.
"""

import logging
from itertools import islice
from typing import Any, Dict, List, Optional

from ..auth import get_current_username, get_workspace_client

logger = logging.getLogger(__name__)


def _normalize_privilege(privilege: str) -> str:
    """Normalize a UC privilege to its enum spelling.

    Unity Catalog spells privileges with underscores (``CREATE_TABLE``), but
    prose and skill docs commonly write them with spaces (``CREATE TABLE``).
    Accept either.
    """
    return privilege.strip().upper().replace(" ", "_")


def _parse_volume_path(volume_path: str) -> tuple[str, str, str]:
    """Split a volume reference into (catalog, schema, volume).

    Accepts either the ``/Volumes/<catalog>/<schema>/<volume>`` filesystem form
    (with or without a trailing path) or the dotted ``catalog.schema.volume``
    form.

    Raises:
        ValueError: If the reference does not name all three parts.
    """
    ref = volume_path.strip()
    if ref.startswith("/Volumes/") or ref.startswith("Volumes/"):
        parts = [p for p in ref.split("/") if p and p != "Volumes"]
    else:
        parts = [p for p in ref.split(".") if p]

    if len(parts) < 3:
        raise ValueError(
            f"Cannot parse a catalog, schema, and volume out of {volume_path!r}. "
            "Expected /Volumes/<catalog>/<schema>/<volume> or catalog.schema.volume."
        )
    return parts[0], parts[1], parts[2]


def check_catalog_access(catalog_name: str) -> bool:
    """
    Check whether the active identity can use a catalog.

    Listing schemas is the probe: it requires USE CATALOG and is read-only, so it
    is safe to run during a readiness check. An empty catalog the caller *can*
    use returns True (the list is empty, but the call succeeded).

    Args:
        catalog_name: Name of the catalog to probe

    Returns:
        True if the catalog exists and the identity can use it, False if it is
        absent or access is denied.
    """
    if not catalog_name or not catalog_name.strip():
        raise ValueError("catalog_name must be a non-empty string")

    w = get_workspace_client()
    try:
        for _ in w.schemas.list(catalog_name=catalog_name):
            break
        return True
    except Exception as exc:
        logger.debug("check_catalog_access(%s) -> False: %s", catalog_name, exc)
        return False


def check_schema_grants(
    catalog: str,
    schema: str,
    privilege: str = "CREATE_TABLE",
    principal: Optional[str] = None,
) -> bool:
    """
    Check whether a principal holds a privilege on a schema.

    Uses *effective* grants, so a privilege inherited from the catalog or from a
    group membership counts — which is what matters operationally.

    Args:
        catalog: Catalog name
        schema: Schema name
        privilege: Privilege to check, e.g. "CREATE_TABLE" or "CREATE TABLE"
        principal: Principal to check; defaults to the active identity. Per
            DBX-SEC-002 this should be the service principal in a deploy context,
            which is whatever `get_workspace_client()` is authenticated as.

    Returns:
        True if the principal holds the privilege (directly or inherited),
        False if not, or if the grant lookup is itself denied.
    """
    wanted = _normalize_privilege(privilege)
    who = principal or get_current_username()

    w = get_workspace_client()
    try:
        result = w.grants.get_effective(
            securable_type="SCHEMA",
            full_name=f"{catalog}.{schema}",
            principal=who,
        )
    except Exception as exc:
        logger.debug(
            "check_schema_grants(%s.%s, %s) -> False: %s", catalog, schema, wanted, exc
        )
        return False

    for assignment in result.privilege_assignments or []:
        for entry in assignment.privileges or []:
            # Effective grants wrap the privilege; direct grants expose it flat.
            value = getattr(entry, "privilege", entry)
            name = getattr(value, "value", value)
            if _normalize_privilege(str(name)) == wanted:
                return True
    return False


def check_volume_exists(volume_path: str) -> bool:
    """
    Check whether a UC volume exists and is reachable by the active identity.

    Args:
        volume_path: Either ``/Volumes/<catalog>/<schema>/<volume>`` or
            ``catalog.schema.volume``

    Returns:
        True if the volume exists and is readable, False if absent or denied.

    Raises:
        ValueError: If *volume_path* does not name a catalog, schema, and volume.
    """
    catalog, schema, volume = _parse_volume_path(volume_path)

    w = get_workspace_client()
    try:
        w.volumes.read(name=f"{catalog}.{schema}.{volume}")
        return True
    except Exception as exc:
        logger.debug("check_volume_exists(%s) -> False: %s", volume_path, exc)
        return False


def accessible_catalogs(limit: int = 50) -> List[Dict[str, Any]]:
    """
    List the catalogs the active identity can actually see.

    Unlike `list_catalogs()`, this never raises — an identity with no catalog
    access gets an empty list, which is a reportable readiness state rather than
    a crash.

    Args:
        limit: Maximum number of catalogs to return

    Returns:
        List of dicts with keys: name, owner, comment, catalog_type
    """
    w = get_workspace_client()
    try:
        # islice, not list(...)[:limit] -- the SDK paginates, so materialising
        # every page on a large metastore only to discard most of it is waste.
        catalogs = list(islice(w.catalogs.list(), limit))
    except Exception as exc:
        logger.debug("accessible_catalogs() -> []: %s", exc)
        return []

    out: List[Dict[str, Any]] = []
    for c in catalogs:
        ctype = getattr(c, "catalog_type", None)
        out.append(
            {
                "name": c.name,
                "owner": getattr(c, "owner", None),
                "comment": getattr(c, "comment", None),
                "catalog_type": getattr(ctype, "value", ctype),
            }
        )
    return out
