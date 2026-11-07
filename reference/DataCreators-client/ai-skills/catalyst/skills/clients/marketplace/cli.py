"""CLI for the marketplace client.

Usage: python -m skills.clients.marketplace <subcommand> [options]

Subcommands:
    whoami      Check token validity (exit 0/2/3)
    login       Run interactive Okta SSO via Playwright
    search      Search the marketplace
    details     Fetch full details for a single entity ID

Exit codes (used by the agent skill to drive UX):
    0 — success
    1 — generic error
    2 — auth invalid/expired (run `login`)
    3 — no token cached (run `login`)
"""

from __future__ import annotations

import argparse
import json
import sys

from . import auth as auth_mod
from . import client as client_mod
from . import exceptions as exc


# Public exit codes
EXIT_OK = 0
EXIT_GENERIC = 1
EXIT_AUTH = 2
EXIT_NO_TOKEN = 3


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="marketplace",
        description="Catalyst marketplace search/details CLI.",
    )
    p.add_argument(
        "--schema",
        metavar="SUBCOMMAND",
        help="Emit JSON Schema for a subcommand's output (search, details). Bypasses other args.",
    )
    sub = p.add_subparsers(dest="subcommand")

    sub.add_parser("whoami", help="Check token validity")
    sub.add_parser("login", help="Run interactive Okta SSO via Playwright")

    sp_search = sub.add_parser("search", help="Search the marketplace")
    sp_search.add_argument("keyword")
    sp_search.add_argument("--types", help="Comma-separated entity types")
    sp_search.add_argument("--page", type=int, default=1)
    sp_search.add_argument("--page-size", type=int, default=25)
    sp_search.add_argument("--parent-id", type=int)
    sp_search.add_argument("--with-access", action="store_true")
    sp_search.add_argument("--json", action="store_true")

    sp_details = sub.add_parser("details", help="Fetch full entity details")
    sp_details.add_argument("entity_id", type=int)
    sp_details.add_argument("--json", action="store_true")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.schema:
        return _cmd_schema(args.schema)

    if not args.subcommand:
        parser.error("subcommand required (or use --schema)")

    if args.subcommand == "whoami":
        return _cmd_whoami()
    if args.subcommand == "login":
        return _cmd_login()
    if args.subcommand == "search":
        return _cmd_search(args)
    if args.subcommand == "details":
        return _cmd_details(args)

    return EXIT_GENERIC


def _cmd_whoami() -> int:
    tok = auth_mod.load_token()
    if tok is None:
        print(
            "No token cached for marketplace. "
            "Run `python -m skills.clients.marketplace login`.",
            file=sys.stderr,
        )
        return EXIT_NO_TOKEN
    cli = client_mod.MarketplaceClient(bearer=tok.bearer, api_base_url=tok.api_base_url)
    result = cli.whoami()
    if result["valid"]:
        print(json.dumps({"valid": True, "expires_at": tok.expires_at}, indent=2))
        return EXIT_OK
    if result["reason"] == "expired":
        print(
            "Marketplace token expired. "
            "Run `python -m skills.clients.marketplace login`.",
            file=sys.stderr,
        )
        return EXIT_AUTH
    detail = result.get("detail", "")
    status = result.get("status_code")
    msg = f"Marketplace whoami probe failed (reason={result['reason']}"
    if status is not None:
        msg += f", status={status}"
    if detail:
        msg += f"): {detail}"
    else:
        msg += ")."
    print(msg, file=sys.stderr)
    return EXIT_GENERIC


# Stubs for the rest — implemented in Tasks 11/12/13.
def _cmd_login() -> int:
    from . import bootstrap
    try:
        bootstrap.login()
    except KeyboardInterrupt:
        print("Login cancelled by user.", file=sys.stderr)
        return EXIT_NO_TOKEN
    except exc.MarketplaceAuthError as e:
        print(f"Login failed: {e}", file=sys.stderr)
        return EXIT_GENERIC
    return EXIT_OK

def _cmd_search(args) -> int:
    tok = auth_mod.load_token()
    if tok is None:
        print(
            "No token cached for marketplace. "
            "Run `python -m skills.clients.marketplace login`.",
            file=sys.stderr,
        )
        return EXIT_NO_TOKEN
    cli = client_mod.MarketplaceClient(bearer=tok.bearer, api_base_url=tok.api_base_url)
    probe = cli.whoami()
    if not probe["valid"]:
        if probe["reason"] == "expired":
            print(
                "Marketplace token expired. "
                "Run `python -m skills.clients.marketplace login`.",
                file=sys.stderr,
            )
            return EXIT_AUTH
        print(
            f"Marketplace pre-check failed (reason={probe['reason']}).",
            file=sys.stderr,
        )
        return EXIT_GENERIC

    types = [t.strip() for t in args.types.split(",")] if args.types else None
    try:
        results = cli.search(
            keyword=args.keyword,
            types=types,
            page=args.page,
            page_size=args.page_size,
            parent_id=args.parent_id,
        )
    except exc.TokenExpiredError:
        print("Marketplace token expired mid-call. Run `marketplace login`.", file=sys.stderr)
        return EXIT_AUTH
    except exc.MarketplaceError as e:
        print(f"Marketplace search failed: {e}", file=sys.stderr)
        return EXIT_GENERIC

    if args.json:
        print(results.model_dump_json(indent=2))
    else:
        _print_search_table(results)
    return EXIT_OK


def _print_search_table(results) -> None:
    print(f"\nMarketplace Search Results — {results.total_count} matches")
    print(f"Page {results.current_page} of {results.total_pages}\n")
    if not results.items:
        print("(no matches)")
        return
    print(f"{'Name':<50}  {'Type':<25}  {'Rank':>6}  {'Validated'}")
    print("-" * 100)
    for it in results.items:
        rank = f"{it.search_rank:.2f}" if it.search_rank is not None else "-"
        print(f"{it.name[:49]:<50}  {it.type.label[:24]:<25}  {rank:>6}  {'yes' if it.validated else 'no'}")


def _cmd_details(args) -> int:
    tok = auth_mod.load_token()
    if tok is None:
        print(
            "No token cached for marketplace. Run `marketplace login`.",
            file=sys.stderr,
        )
        return EXIT_NO_TOKEN
    cli = client_mod.MarketplaceClient(bearer=tok.bearer, api_base_url=tok.api_base_url)
    probe = cli.whoami()
    if not probe["valid"]:
        if probe["reason"] == "expired":
            print("Marketplace token expired. Run `marketplace login`.", file=sys.stderr)
            return EXIT_AUTH
        print(f"Marketplace pre-check failed (reason={probe['reason']}).", file=sys.stderr)
        return EXIT_GENERIC

    try:
        entity = cli.details(args.entity_id)
    except exc.UnsupportedPlatformError as e:
        print(f"{e}", file=sys.stderr)
        return EXIT_GENERIC
    except exc.TokenExpiredError:
        print("Marketplace token expired. Run `marketplace login`.", file=sys.stderr)
        return EXIT_AUTH
    except exc.MarketplaceError as e:
        print(f"Marketplace details failed: {e}", file=sys.stderr)
        return EXIT_GENERIC

    payload = _details_payload(entity)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_details_human(payload)
    return EXIT_OK


def _details_payload(entity) -> dict:
    from datetime import datetime, timezone
    return {
        "entity": entity.model_dump(mode="json", by_alias=True),
        "_meta": {
            "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "endpoints_called": 6,
            "schema_version": "1.0",
        },
    }


def _print_details_human(payload) -> None:
    e = payload["entity"]
    print(f"\n{e['name']} (id {e['entity_id']})")
    print(f"  Type:      {e['type']['label']}")
    print(f"  Platform:  {e['platform']['name']}")
    print(f"  Validated: {'yes' if e['validated'] else 'no'}")
    print(f"  Health:    {e['health']['status']}")
    print(f"  Detail:    {e['detail_url']}")
    if e.get("access"):
        a = e["access"]
        print(f"\nAccess: {'yes' if a['has_access'] else 'no'}")
        print(f"  Entitlements: {', '.join(a['entitlements']) or '(none)'}")
        print(f"  Request:      {a['request_access_url']}")


def _cmd_schema(name: str) -> int:
    from . import models
    schemas = {
        "search": models.SearchResults.model_json_schema(),
        "details": _details_schema(),
    }
    if name not in schemas:
        print(f"Unknown schema name: {name}. Try: {', '.join(schemas)}", file=sys.stderr)
        return EXIT_GENERIC
    print(json.dumps(schemas[name], indent=2))
    return EXIT_OK


def _details_schema() -> dict:
    """JSON Schema for the `details` payload (entity + _meta)."""
    from . import models
    entity_schema = models.Entity.model_json_schema()
    return {
        "type": "object",
        "properties": {
            "entity": entity_schema,
            "_meta": models.ResponseMeta.model_json_schema(),
        },
        "required": ["entity", "_meta"],
    }
