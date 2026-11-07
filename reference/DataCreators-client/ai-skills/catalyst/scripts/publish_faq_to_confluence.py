#!/usr/bin/env python3
"""publish_faq_to_confluence — mirror the Getting Started FAQ into Confluence.

The FAQ lives in `docs/getting-started-faq.html` and publishes to GitHub Pages.
Most people reading onboarding material at Capital Group start in Confluence, on
the **AI Catalyst Onboarding** tree, not on our Pages site — so the FAQ has to
exist there too, as a sibling of *0 Pre-Req: Setting Up VS Code GitHub Copilot*
rather than as a competing copy somewhere else.

Two copies of a document is exactly how #434 and #439 ended up publishing the
same guide, so this mirrors mechanically from one source instead of inviting a
hand-maintained second version. `docs/getting-started-faq.html` stays canonical;
the Confluence page is generated and says so.

Why a conversion and not an upload
----------------------------------
The FAQ is a styled standalone page. Confluence storage format is a constrained
XHTML dialect: it drops `<style>`, `class`, and inline `style`, and it renders
callouts and code blocks through its own macros. Pasting the file in produces an
unstyled wall of text with silently-lost structure — so the presentational layer
is stripped deliberately and the semantic structure is translated:

    div.note      -> ac:structured-macro info      (the callouts)
    pre > code    -> ac:structured-macro code      (fenced blocks)
    span.pending  -> literal "(link pending)"      (the chip has no CSS there)
    span.q        -> dropped                       ("Q:" is decoration; the
                                                    heading text is the question)
    class=/style= -> stripped

Relative links are the one thing this cannot guess: `href="./"` and
`href="release-comms/..."` resolve against the Pages site, which is not
discoverable from here (the Pages API returns 403 for this token). So
`--site-base` is **required** when the document contains relative links, and the
script refuses rather than publishing links that 404 for every reader.

Usage
-----
    # dry run — prints the storage format and what it would do
    python3 scripts/publish_faq_to_confluence.py --site-base https://<pages-host>/catalyst/

    # write it
    python3 scripts/publish_faq_to_confluence.py \
        --site-base https://<pages-host>/catalyst/ --apply

Idempotent: the rendered body carries a content hash, and an unchanged FAQ is a
no-op rather than a new page version. Exit 0 on success or a clean no-op, 1 when
a publish was needed and `--apply` was not given, 2 on bad invocation.

Env (from the repo-root .env, per docs/install.md):
    CONFLUENCE_URL | CONFLUENCE_BASE_URL   e.g. https://capitalgroup.atlassian.net
    CONFLUENCE_USERNAME                    Atlassian account e-mail
    CONFLUENCE_API_TOKEN                   Atlassian API token
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FAQ_PATH = REPO_ROOT / "docs" / "getting-started-faq.html"
# The client imports itself as `skills.clients.*`, so the repo root is what
# has to be importable — not the skills directory.
sys.path.insert(0, str(REPO_ROOT))

# The AI Catalyst Onboarding page in ENTDATA. The FAQ belongs beside the pre-req
# page, which is a child of this one.
DEFAULT_PARENT_ID = "404951408"
DEFAULT_SPACE = "ENTDATA"
DEFAULT_TITLE = "AI Catalyst: Getting Started FAQ"

# Marker carrying the source hash, so a re-run on an unchanged FAQ is a no-op.
HASH_MARKER = "catalyst-faq-source-sha256"

# Tags Confluence storage format understands and we want to keep.
KEEP = {
    "p", "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td",
    "strong", "em", "code", "br", "h1", "h2", "h3", "h4", "a", "hr",
}
VOID = {"br", "hr"}
# Chrome that carries no onboarding content.
DROP_SUBTREE = {"style", "script", "head", "nav", "footer", "title"}


class FaqConverter(HTMLParser):
    """Translate the FAQ body into Confluence storage format."""

    def __init__(self, site_base: str | None) -> None:
        super().__init__(convert_charrefs=True)
        self.site_base = (site_base or "").rstrip("/") + "/" if site_base else None
        self.out: list[str] = []
        # A stack of the dropped tags currently open, NOT a counter. A counter
        # breaks on void descendants: <head> holds <meta> and <link>, which have
        # no end tag, so each one would increment a counter that never comes back
        # down — and the body would never be entered at all.
        self._drop_stack: list[str] = []
        self._in_body = False
        self._pre_depth = 0
        self._pre_buf: list[str] = []
        self._note_depth: list[bool] = []
        self._skip_text_depth = 0
        self.relative_links: list[str] = []

    # -- helpers ------------------------------------------------------------

    def _emit(self, text: str) -> None:
        if self._pre_depth:
            self._pre_buf.append(text)
        else:
            self.out.append(text)

    def _resolve(self, href: str) -> str:
        """Absolutise a link, recording anything that needs --site-base."""
        if href.startswith(("http://", "https://", "mailto:", "#")):
            return href
        self.relative_links.append(href)
        if not self.site_base:
            return href                      # caller refuses before publishing
        return self.site_base + href.lstrip("./")

    # -- parser callbacks ---------------------------------------------------

    def handle_starttag(self, tag: str, attrs_list: list) -> None:
        attrs = dict(attrs_list)
        if tag == "body":
            self._in_body = True
            return
        if tag in DROP_SUBTREE:
            self._drop_stack.append(tag)
            return
        if self._drop_stack:
            return
        if not self._in_body:
            return

        classes = (attrs.get("class") or "").split()

        # The "Q:" chip is decoration; the heading text is already the question.
        if tag == "span" and "q" in classes:
            self._skip_text_depth += 1
            return
        if tag == "span" and "pending" in classes:
            self._skip_text_depth += 1
            self._emit("(link pending)")
            return
        if tag == "span":
            return                            # unwrap other spans

        if tag == "pre":
            self._pre_depth += 1
            self._pre_buf = []
            return
        if tag == "code" and self._pre_depth:
            return                            # the <code> inside <pre> is noise

        if tag == "div":
            is_note = "note" in classes
            self._note_depth.append(is_note)
            if is_note:
                self._emit('<ac:structured-macro ac:name="info">'
                           '<ac:rich-text-body>')
            return

        if tag == "a":
            href = self._resolve(attrs.get("href", ""))
            self._emit(f'<a href="{escape_attr(href)}">')
            return

        if tag in KEEP:
            self._emit(f"<{tag}/>" if tag in VOID else f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        if self._drop_stack:
            if tag == self._drop_stack[-1]:
                self._drop_stack.pop()
            return
        if tag == "body":
            self._in_body = False
            return
        if not self._in_body:
            return

        if tag == "span":
            if self._skip_text_depth:
                self._skip_text_depth -= 1
            return
        if tag == "pre":
            self._pre_depth -= 1
            code = "".join(self._pre_buf).strip("\n")
            self.out.append(
                '<ac:structured-macro ac:name="code">'
                '<ac:parameter ac:name="language">bash</ac:parameter>'
                f"<ac:plain-text-body><![CDATA[{sanitise_cdata(code)}]]>"
                "</ac:plain-text-body></ac:structured-macro>"
            )
            self._pre_buf = []
            return
        if tag == "code" and self._pre_depth:
            return
        if tag == "div":
            if self._note_depth and self._note_depth.pop():
                self._emit("</ac:rich-text-body></ac:structured-macro>")
            return
        if tag in KEEP and tag not in VOID:
            self._emit(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._drop_stack or not self._in_body:
            return
        if self._skip_text_depth and not self._pre_depth:
            return
        if self._pre_depth:
            self._pre_buf.append(data)
            return
        text = data.strip("\n")
        if text.strip():
            self._emit(escape_text(collapse(text)))


def collapse(text: str) -> str:
    """The source is hard-wrapped for readability; Confluence doesn't need that."""
    return re.sub(r"\s+", " ", text)


def escape_text(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def escape_attr(value: str) -> str:
    return escape_text(value).replace('"', "&quot;")


def sanitise_cdata(text: str) -> str:
    """`]]>` inside CDATA would close the block early and corrupt the page."""
    return text.replace("]]>", "]] >")


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def rendered_hash(body: str) -> str:
    """The hash a freshly rendered body should carry.

    Strips the marker paragraph so the hash covers everything *except* itself —
    otherwise it would have to hash its own value.
    """
    return content_hash(re.sub(r"<p><!-- " + HASH_MARKER + r":[0-9a-f]+ --></p>\s*$",
                               "", body))


def build_storage(html: str, site_base: str | None) -> tuple[str, list[str]]:
    """Return (storage body, relative links found)."""
    converter = FaqConverter(site_base)
    converter.feed(html)
    body = "".join(converter.out)
    body = re.sub(r"(<p></p>|<p>\s*</p>)", "", body)

    header = (
        '<ac:structured-macro ac:name="info"><ac:rich-text-body>'
        "<p><strong>This page is generated.</strong> It mirrors "
        '<code>docs/getting-started-faq.html</code> in the '
        '<a href="https://github.com/cg-open-itg/catalyst">cg-open-itg/catalyst</a> '
        "repository, which is the source of truth. Edits made here are overwritten "
        "on the next publish — raise a pull request against that file instead.</p>"
        "</ac:rich-text-body></ac:structured-macro>"
    )
    # The marker hashes the **rendered** body, not the source HTML. Hashing the
    # source was wrong in two ways: the rendering also depends on `--site-base`,
    # so changing the docs host left stale absolute links while reporting "up to
    # date"; and a human editing the page in Confluence kept the source marker
    # intact, so the edit was reported as current even though the banner directly
    # above it promises the page will be overwritten.
    rendered = header + body
    footer = f"<p><!-- {HASH_MARKER}:{content_hash(rendered)} --></p>"
    return rendered + footer, converter.relative_links


def published_hash(body: str) -> str | None:
    found = re.search(rf"{HASH_MARKER}:([0-9a-f]+)", body or "")
    return found.group(1) if found else None


def load_env() -> dict[str, str]:
    """base_url / email / token, from the environment.

    Read from the process environment only — this deliberately does not parse
    `.env` itself, so the same script works under a credential injector.
    """
    base = os.environ.get("CONFLUENCE_URL") or os.environ.get("CONFLUENCE_BASE_URL")
    email = os.environ.get("CONFLUENCE_USERNAME")
    token = os.environ.get("CONFLUENCE_API_TOKEN") or os.environ.get("CONFLUENCE_TOKEN")
    missing = [n for n, v in (("CONFLUENCE_URL", base),
                              ("CONFLUENCE_USERNAME", email),
                              ("CONFLUENCE_API_TOKEN", token)) if not v]
    if missing:
        raise SystemExit(
            "publish_faq_to_confluence: missing " + ", ".join(missing) +
            ".\nSource the repo-root .env, or export them for one command.")
    return {"base_url": base, "email": email, "token": token}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write to Confluence")
    ap.add_argument("--site-base", help="absolute base for the published docs site, "
                                        "required when the FAQ has relative links")
    ap.add_argument("--parent-id", default=DEFAULT_PARENT_ID)
    ap.add_argument("--space", default=DEFAULT_SPACE)
    ap.add_argument("--title", default=DEFAULT_TITLE)
    ap.add_argument("--faq", default=str(FAQ_PATH))
    ap.add_argument("--print-storage", action="store_true",
                    help="print the converted body and exit (no network)")
    args = ap.parse_args(argv)

    faq_path = Path(args.faq)
    if not faq_path.is_file():
        print(f"publish_faq_to_confluence: no FAQ at {faq_path}", file=sys.stderr)
        return 2

    html = faq_path.read_text(encoding="utf-8")
    body, relative = build_storage(html, args.site_base)

    if args.print_storage:
        print(body)
        return 0

    if relative and not args.site_base:
        unique = sorted(set(relative))
        print("publish_faq_to_confluence: refusing to publish — "
              f"{len(unique)} relative link(s) would 404 for every Confluence "
              "reader. Pass --site-base <published docs URL>.\n  "
              + "\n  ".join(unique), file=sys.stderr)
        return 2

    from skills.clients.confluence import ConfluenceClient  # noqa: E402

    cfg = load_env()
    client = ConfluenceClient(cfg["base_url"], cfg["email"], cfg["token"])

    existing = client.find_child_by_title(args.parent_id, args.title)
    if existing is None:
        print(f"would CREATE {args.title!r} under {args.parent_id} "
              f"in {args.space} ({len(body)} bytes of storage format)")
        if not args.apply:
            print("\nDry run — re-run with --apply to write.")
            return 1
        try:
            created = client.create_page(args.space, args.title, body, args.parent_id)
        except Exception as exc:                       # noqa: BLE001 - see below
            # Confluence titles are unique **per space**, not per parent, and
            # find_child_by_title only looks under our parent. So if this page was
            # moved, or a same-titled page exists elsewhere in the space, the
            # create fails with a 400 whose body says nothing useful. Say what
            # actually happened instead of surfacing a traceback.
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status == 400:
                print(f"publish_faq_to_confluence: Confluence refused to create "
                      f"{args.title!r}. Titles are unique per space, so a page with "
                      f"this title probably already exists in {args.space} somewhere "
                      f"other than under {args.parent_id} — most likely it was moved. "
                      f"Find it, and either move it back or pass --parent-id/--title "
                      f"to match.", file=sys.stderr)
                return 2
            print(f"publish_faq_to_confluence: create failed: {exc}", file=sys.stderr)
            return 2
        print(f"created page {created.get('id')}")
        return 0

    page_id = str(existing.get("id"))
    current = client.get_page(page_id)
    current_body = (((current.get("body") or {}).get("storage") or {}).get("value")
                    or "")
    if published_hash(current_body) == rendered_hash(body):
        print(f"up to date — page {page_id} already matches the current FAQ")
        return 0

    version = int(((current.get("version") or {}).get("number")) or 1)
    print(f"would UPDATE page {page_id} ({args.title!r}) from version {version}")
    if not args.apply:
        print("\nDry run — re-run with --apply to write.")
        return 1
    client.update_page(page_id, args.title, body, version)
    print(f"updated page {page_id} to version {version + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
