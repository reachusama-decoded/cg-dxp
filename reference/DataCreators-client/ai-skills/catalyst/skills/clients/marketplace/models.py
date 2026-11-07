"""Pydantic models for the marketplace client.

These models are the source of truth for the JSON Schema emitted by
`marketplace --schema`. Field choices follow the spec's "designed for
agent consumption" rules:

- Codes are paired with labels (no opaque strings).
- Nullable fields are explicit (no silent coercion).
- Empty collections stay as empty arrays (not omitted).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_serializer


# ---- Type / platform code-label pairs ---------------------------------------

_KNOWN_ENTITY_TYPE_LABELS: dict[str, str] = {
    "data_product": "Data Product",
    "external_data_product": "External Data Product",
    "data_domain": "Data Domain",
    "domain_group": "Domain Group",
    "dataset": "Dataset",
    "dataset_table": "Dataset Table",
    "data_package": "Data Package",
    "data_source": "Data Source",
}

_KNOWN_PLATFORM_NAMES: dict[str, str] = {
    "CSPN": "Caspian",
    "CASPIAN": "Caspian",
    "LASR": "LASR",
}


class EntityType(BaseModel):
    """Type code + human-readable label."""

    code: str
    label: str

    @classmethod
    def from_code(cls, code: str) -> "EntityType":
        label = _KNOWN_ENTITY_TYPE_LABELS.get(
            code, " ".join(part.capitalize() for part in code.split("_"))
        )
        return cls(code=code, label=label)


class Platform(BaseModel):
    """Platform code + human-readable name."""

    code: str
    name: str

    @classmethod
    def from_code(cls, code: str) -> "Platform":
        return cls(code=code, name=_KNOWN_PLATFORM_NAMES.get(code, code))


class Health(BaseModel):
    """Entity health/quality rating with explicit unrated state."""

    rating: Optional[str] = None

    @property
    def status(self) -> str:
        return self.rating if self.rating else "unrated"

    @model_serializer(mode="wrap")
    def _serialize(self, handler):
        data = handler(self)
        data["status"] = self.status
        return data


class AccessInfo(BaseModel):
    """Access status + AD entitlement(s) + UI deep link."""

    has_access: bool
    entitlements: list[str] = Field(default_factory=list)
    request_access_url: str
    platform_code: str


class Entity(BaseModel):
    """Marketplace entity (data product, dataset, domain, etc.)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    entity_id: int
    name: str
    description: str
    type: EntityType
    platform: Platform
    validated: bool
    health: Health
    ancestry: list[str] = Field(default_factory=list)
    detail_url: str
    search_rank: Optional[float] = None

    # Populated only by details() or search(with_access=True):
    sources: Optional[dict[str, list[str]]] = None
    access: Optional[AccessInfo] = None
    field_schema: Optional["SchemaInfo"] = Field(default=None, alias="schema")
    business_terms: Optional[list["BusinessTerm"]] = None
    preview: Optional["PreviewData"] = None


class SearchResults(BaseModel):
    items: list[Entity]
    total_count: int
    current_page: int
    page_size: int
    total_pages: int


class FieldInfo(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class SchemaInfo(BaseModel):
    field_count: int
    fields: list[FieldInfo]


class BusinessTerm(BaseModel):
    name: str
    definition: Optional[str] = None


class PreviewData(BaseModel):
    row_count: int
    rows: list[dict]


class ResponseMeta(BaseModel):
    fetched_at: str
    endpoints_called: int
    schema_version: str = "1.0"


class DetailsResponse(BaseModel):
    """Full output of `marketplace details <id>`."""

    entity: Entity
    meta: ResponseMeta = Field(alias="_meta")

    model_config = ConfigDict(populate_by_name=True)


# Resolve forward refs
Entity.model_rebuild()
