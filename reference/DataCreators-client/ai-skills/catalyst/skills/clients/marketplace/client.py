"""MarketplaceClient — REST wrapper for the marketplace API.

No business logic. No prompting. Just typed calls + typed responses.
"""

from __future__ import annotations

import os
from typing import Optional

import requests

from . import auth as auth_mod
from . import exceptions as exc
from . import models

DEFAULT_API_BASE_URL = "https://marketplace-service.datalake.aws.capgroup.com"
DEFAULT_UI_BASE_URL = "https://marketplace.capgroup.com"

DEFAULT_LEVEL_TYPES = [
    "data_domain",
    "dataset",
    "external_data_product",
    "data_product",
]


def _default_api_base_url() -> str:
    return os.getenv("MARKETPLACE_API_BASE_URL", DEFAULT_API_BASE_URL)


def _default_ui_base_url() -> str:
    return os.getenv("MARKETPLACE_UI_BASE_URL", DEFAULT_UI_BASE_URL)


class MarketplaceClient:
    """Direct REST client. Construct via from_cache() in normal use."""

    def __init__(
        self,
        bearer: str,
        api_base_url: Optional[str] = None,
        ui_base_url: Optional[str] = None,
        timeout: float = 15.0,
    ) -> None:
        self._bearer = bearer
        self._api_base_url = (api_base_url or _default_api_base_url()).rstrip("/")
        self._ui_base_url = (ui_base_url or _default_ui_base_url()).rstrip("/")
        self._timeout = timeout

    @classmethod
    def from_cache(cls) -> "MarketplaceClient":
        tok = auth_mod.load_token()
        if tok is None:
            raise exc.TokenMissingError(
                "No marketplace token cached. "
                "Run `python -m skills.clients.marketplace login` first."
            )
        return cls(bearer=tok.bearer, api_base_url=tok.api_base_url)

    # -- HTTP helpers ---------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": self._bearer,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "catalyst-marketplace/1.0",
        }

    def _post(self, path: str, *, params=None, json_body=None) -> dict:
        url = f"{self._api_base_url}{path}"
        resp = requests.post(
            url, headers=self._headers(), params=params, json=json_body, timeout=self._timeout
        )
        return self._handle(resp)

    def _get(self, path: str, *, params=None) -> dict:
        url = f"{self._api_base_url}{path}"
        resp = requests.get(url, headers=self._headers(), params=params, timeout=self._timeout)
        return self._handle(resp)

    def _handle(self, resp) -> dict:
        if resp.status_code == 401:
            raise exc.TokenExpiredError(
                "Marketplace API rejected the token (401). Run `marketplace login`."
            )
        if resp.status_code >= 400:
            raise exc.MarketplaceError(
                f"Marketplace API error {resp.status_code}: {resp.text[:300]}"
            )
        try:
            return resp.json()
        except ValueError as e:
            raise exc.MarketplaceError(f"Marketplace API returned non-JSON: {e}")

    # -- Public methods -------------------------------------------------------

    def whoami(self) -> dict:
        """Cheap auth probe. Returns {"valid": bool, "reason": str | None, "status_code": int | None}.

        Hits /api/v1/marketplace/labels?type=TAG — a small authed read that
        returns 200 + a JSON list when the bearer is valid. The type=TAG
        parameter is required (without it, the endpoint returns 500).
        """
        url = f"{self._api_base_url}/api/v1/marketplace/labels"
        try:
            resp = requests.get(
                url,
                headers=self._headers(),
                params={"type": "TAG"},
                timeout=self._timeout,
            )
        except requests.RequestException as e:
            return {"valid": False, "reason": "unknown", "status_code": None, "detail": str(e)}
        if resp.status_code == 200:
            return {"valid": True, "reason": None, "status_code": 200}
        if resp.status_code == 401:
            return {"valid": False, "reason": "expired", "status_code": 401}
        return {"valid": False, "reason": "unknown", "status_code": resp.status_code, "detail": resp.text[:200]}

    def search(
        self,
        keyword: str,
        types: Optional[list[str]] = None,
        page: int = 1,
        page_size: int = 25,
        parent_id: Optional[int] = None,
    ) -> models.SearchResults:
        body: dict = {
            "keyword": keyword,
            "levelTypes": types or DEFAULT_LEVEL_TYPES,
        }
        if parent_id is not None:
            body["parents"] = [{"parentId": parent_id}]

        raw = self._post(
            "/api/v1/marketplace/search/entities",
            params={"page": page, "pageSize": page_size},
            json_body=body,
        )
        return self._parse_search(raw)

    # -- Parsers --------------------------------------------------------------

    def _parse_search(self, raw: dict) -> models.SearchResults:
        stats = raw.get("stats") or {}
        items = []
        for it in raw.get("items") or []:
            items.append(self._parse_entity(it))
        return models.SearchResults(
            items=items,
            total_count=stats.get("totalCount", 0),
            current_page=stats.get("currentPage", 1),
            page_size=stats.get("pageSize", 0),
            total_pages=stats.get("totalPages", 0),
        )

    def _parse_entity(self, it: dict) -> models.Entity:
        type_code = it.get("type", "")
        ancestry = [
            a.get("name", "")
            for a in (it.get("hierarchyInfo") or {}).get("ancestry") or []
        ]
        rank = (
            (it.get("resultsMetadata") or {}).get("searching") or {}
        ).get("searchRank")
        return models.Entity(
            entity_id=it["entityId"],
            name=it.get("name", ""),
            description=it.get("description", ""),
            type=models.EntityType.from_code(type_code),
            platform=models.Platform.from_code(it.get("platform") or "UNKNOWN"),
            validated=bool(it.get("isValidated", False)),
            health=models.Health(rating=(it.get("health") or {}).get("rating")),
            ancestry=ancestry,
            detail_url=f"{self._ui_base_url}/entity/{it['entityId']}",
            search_rank=rank,
        )

    def _normalize_entity_detail(self, raw: dict) -> dict:
        """Flatten the /entities/{id} response into the same shape _parse_entity expects."""
        # The detail endpoint wraps everything under a nested "entity" key with "contents".
        # If the raw dict already has "entityId" at top level it's already flat (e.g. in tests).
        if "entityId" in raw:
            return raw
        entity = raw.get("entity") or raw
        contents = entity.get("contents") or {}
        overview = contents.get("overview") or {}
        about = overview.get("aboutThisData") or {}
        is_validated_block = contents.get("isValidated") or {}
        health_block = contents.get("health") or {}
        return {
            "entityId": entity.get("entityId"),
            "name": entity.get("name", ""),
            "type": entity.get("type", ""),
            "description": overview.get("description", ""),
            "platform": about.get("platform"),
            "isValidated": is_validated_block.get("isValidated", False),
            "hierarchyInfo": {"ancestry": []},
            "health": health_block,
        }

    def details(self, entity_id: int) -> models.Entity:
        """Fetch full entity details: 6 endpoints aggregated into one Entity."""
        entity_raw = self._get(f"/api/v1/marketplace/entities/{entity_id}")
        consumable_raw = self._get(f"/api/v1/marketplace/entities/{entity_id}/consumable")

        normalized = self._normalize_entity_detail(entity_raw)
        entity = self._parse_entity(normalized)
        sources = self._parse_sources(consumable_raw)
        entity.sources = sources

        # Schema (best-effort — not every entity has a queryable schema)
        try:
            fields_raw = self._get(
                "/api/v1/marketplace/table/fields/search",
                params={"query": entity.name},
            )
            entity.field_schema = self._parse_schema(fields_raw)
        except exc.MarketplaceError:
            entity.field_schema = models.SchemaInfo(field_count=0, fields=[])

        # Business terms
        try:
            bt_raw = self._post(
                "/api/v1/marketplace/business-terms/by-tables",
                json_body={"tables": [consumable_raw.get("technicalName")]},
            )
            entity.business_terms = self._parse_business_terms(bt_raw)
        except exc.MarketplaceError:
            entity.business_terms = []

        # Preview
        try:
            preview_raw = self._post(
                "/api/v1/marketplace/datadelivery/preview/by-views",
                json_body={"views": [consumable_raw.get("technicalName")]},
            )
            entity.preview = self._parse_preview(preview_raw)
        except exc.MarketplaceError:
            entity.preview = models.PreviewData(row_count=0, rows=[])

        # Access (platform-aware)
        platform = (consumable_raw.get("platform") or "").upper()
        entity.access = self._fetch_access(platform, consumable_raw, entity_id)

        return entity

    def _fetch_access(
        self, platform: str, consumable_raw: dict, entity_id: int
    ) -> models.AccessInfo:
        if platform in ("CSPN", "CASPIAN"):
            return self._access_caspian(consumable_raw, entity_id, platform)
        if platform == "LASR":
            return self._access_lasr(consumable_raw, entity_id, platform)
        raise exc.UnsupportedPlatformError(platform)

    def _access_caspian(
        self, consumable_raw: dict, entity_id: int, platform: str
    ) -> models.AccessInfo:
        view_paths = []
        for src in consumable_raw.get("sources") or []:
            if src.get("system") == "dremio":
                for v in src.get("values") or []:
                    view_paths.append({"viewPath": v.split("."), "platform": "CASPIAN"})
        if not view_paths:
            return self._empty_access(entity_id, platform)
        raw = self._post(
            "/api/v1/marketplace/table/view-access",
            json_body={"items": view_paths},
        )
        return self._parse_access(raw, entity_id, platform)

    def _access_lasr(
        self, consumable_raw: dict, entity_id: int, platform: str
    ) -> models.AccessInfo:
        items = []
        for src in consumable_raw.get("sources") or []:
            if src.get("system") == "lasr":
                for v in src.get("values") or []:
                    items.append({"tableName": v, "platform": "LASR"})
        if not items:
            tn = consumable_raw.get("technicalName")
            if tn:
                items.append({"tableName": tn, "platform": "LASR"})
        raw = self._post("/api/v1/marketplace/entities/table-access", json_body=items)
        return self._parse_access(raw, entity_id, platform)

    def _empty_access(self, entity_id: int, platform: str) -> models.AccessInfo:
        return models.AccessInfo(
            has_access=False,
            entitlements=[],
            request_access_url=f"{self._ui_base_url}/entity/{entity_id}/request-access",
            platform_code=platform,
        )

    def _parse_access(
        self, raw: dict, entity_id: int, platform: str
    ) -> models.AccessInfo:
        items = raw.get("items") or []
        if not items:
            return self._empty_access(entity_id, platform)
        any_no_access = any(not it.get("access", False) for it in items)
        ents: list[str] = []
        for it in items:
            for ent in it.get("entitlements") or []:
                name = ent.get("name") if isinstance(ent, dict) else None
                if name and name not in ents:
                    ents.append(name)
        return models.AccessInfo(
            has_access=not any_no_access,
            entitlements=ents,
            request_access_url=f"{self._ui_base_url}/entity/{entity_id}/request-access",
            platform_code=platform,
        )

    def _parse_sources(self, consumable_raw: dict) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for src in consumable_raw.get("sources") or []:
            sys_ = src.get("system") or "unknown"
            for v in src.get("values") or []:
                out.setdefault(sys_, []).append(v)
        return out

    def _parse_schema(self, raw: dict) -> models.SchemaInfo:
        fields = []
        for it in raw.get("items") or raw.get("fields") or []:
            fields.append(models.FieldInfo(
                name=it.get("name", ""),
                type=it.get("type") or it.get("dataType") or "unknown",
                description=it.get("description"),
            ))
        return models.SchemaInfo(field_count=len(fields), fields=fields)

    def _parse_business_terms(self, raw: dict) -> list[models.BusinessTerm]:
        out = []
        for it in raw.get("items") or raw.get("terms") or []:
            out.append(models.BusinessTerm(
                name=it.get("name", ""),
                definition=it.get("definition"),
            ))
        return out

    def _parse_preview(self, raw: dict) -> models.PreviewData:
        rows = raw.get("rows") or raw.get("items") or []
        return models.PreviewData(row_count=len(rows), rows=list(rows))
