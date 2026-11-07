"""Token storage and lifecycle for the marketplace client.

Token cache file:  ~/.config/catalyst/marketplace.json (mode 0600)
Parent dir:        ~/.config/catalyst/                 (mode 0700)
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import platformdirs
from pydantic import BaseModel, ValidationError

from . import exceptions as exc


class CachedToken(BaseModel):
    bearer: str
    captured_at: str
    expires_at: Optional[str] = None
    api_base_url: str


def token_path() -> Path:
    """Per-OS canonical config location.

    Linux/Mac: ~/.config/catalyst/marketplace.json
    Windows:   C:\\Users\\<user>\\AppData\\Roaming\\catalyst\\marketplace.json
    """
    return Path(platformdirs.user_config_dir("catalyst", appauthor=False)) / "marketplace.json"


def load_token() -> Optional[CachedToken]:
    p = token_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise exc.MarketplaceError(f"Token cache at {p} is not valid JSON: {e}")
    try:
        return CachedToken(**data)
    except ValidationError as e:
        raise exc.MarketplaceError(f"Token cache at {p} has invalid shape: {e}")


def save_token(
    bearer: str,
    api_base_url: str,
    expires_at: Optional[str] = None,
) -> None:
    p = token_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform != "win32":
        os.chmod(p.parent, 0o700)
    payload = CachedToken(
        bearer=bearer,
        captured_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        expires_at=expires_at,
        api_base_url=api_base_url,
    )
    p.write_text(payload.model_dump_json(indent=2))
    if sys.platform != "win32":
        os.chmod(p, 0o600)


def clear_token() -> None:
    p = token_path()
    if p.exists():
        p.unlink()
