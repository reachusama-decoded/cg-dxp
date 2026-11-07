#!/usr/bin/env python3
"""Sync version + release date from plugin.json → marketplace.json description.

Source of truth: plugin.json (version, description)
Targets updated:
  - .github/plugin/marketplace.json  →  metadata.version, plugins[0].version,
    plugins[0].description (with " (vX.Y.Z · YYYY-MM-DD)" suffix)

Usage:
  python scripts/sync_plugin_version.py          # fix in-place
  python scripts/sync_plugin_version.py --check   # exit 1 if out of sync (CI mode)
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_JSON = REPO_ROOT / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".github" / "plugin" / "marketplace.json"

# Regex to strip an existing version/date suffix like " (v1.1.0 · 2026-05-01)"
SUFFIX_RE = re.compile(r"\s*\(v[\d.]+(?: · \d{4}-\d{2}-\d{2})?\)\s*$")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync(*, check_only: bool = False) -> bool:
    plugin = load_json(PLUGIN_JSON)
    marketplace = load_json(MARKETPLACE_JSON)

    version = plugin["version"]
    base_desc = plugin["description"]
    today = date.today().isoformat()
    suffix = f" (v{version} · {today})"

    # Build the suffixed description from plugin.json's base description
    clean_base = SUFFIX_RE.sub("", base_desc).rstrip()
    new_desc = clean_base + suffix

    dirty = False

    # metadata.version
    if marketplace.get("metadata", {}).get("version") != version:
        dirty = True
    # plugins[0].version
    if marketplace["plugins"][0].get("version") != version:
        dirty = True
    # plugins[0].description
    if marketplace["plugins"][0].get("description") != new_desc:
        dirty = True

    if check_only:
        if dirty:
            print(f"✗ marketplace.json is out of sync with plugin.json v{version}")
            print(f"  Run: python scripts/sync_plugin_version.py")
            return False
        print(f"✓ marketplace.json is in sync (v{version})")
        return True

    if not dirty:
        print(f"✓ Already in sync (v{version} · {today})")
        return True

    marketplace["metadata"]["version"] = version
    marketplace["plugins"][0]["version"] = version
    marketplace["plugins"][0]["description"] = new_desc

    write_json(MARKETPLACE_JSON, marketplace)
    print(f"✓ Synced marketplace.json → v{version} · {today}")
    return True


if __name__ == "__main__":
    check_only = "--check" in sys.argv
    ok = sync(check_only=check_only)
    sys.exit(0 if ok else 1)
