"""Core function: fetch a Confluence page and convert to Markdown.

Wraps ConfluenceClient.  HTML-to-Markdown conversion uses the markitdown
library when available; falls back to a simple tag-stripping heuristic so the
function works in environments where markitdown is not installed.
"""

from __future__ import annotations

import io
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def fetch_confluence_page(
    client: Any,
    page_id: str,
    include_children: bool = False,
) -> str:
    """Fetch a Confluence page and convert to Markdown.

    Args:
        client: ConfluenceClient instance.
        page_id: Numeric Confluence page identifier.
        include_children: If True, recursively fetches child pages and
                          appends their Markdown content separated by
                          horizontal rules.

    Returns:
        Markdown string of the page content.
        If *include_children* is True, child pages are appended in pre-order
        (parent first, then children depth-first).
    """
    if include_children:
        pages = client.get_page_tree(page_id)
    else:
        pages = [client.get_page(page_id)]

    sections: list[str] = []
    for page in pages:
        title = page.get("title", "")
        html = page.get("body", {}).get("storage", {}).get("value", "")
        md = _html_to_markdown(html)
        section = f"# {title}\n\n{md}".strip()
        sections.append(section)

    return "\n\n---\n\n".join(sections)


# ---------------------------------------------------------------------------
# HTML → Markdown conversion
# ---------------------------------------------------------------------------


def _html_to_markdown(html: str) -> str:
    """Convert Confluence HTML storage format to Markdown.

    Tries markitdown first for best results; falls back to a lightweight
    regex-based stripper so the function never raises.
    """
    if not html or not html.strip():
        return ""

    try:
        return _markitdown_convert(html)
    except Exception:
        pass

    return _simple_html_to_markdown(html)


def _markitdown_convert(html: str) -> str:
    """Convert HTML via markitdown (optional dependency)."""
    from markitdown import MarkItDown, StreamInfo  # type: ignore[import]

    md_converter = MarkItDown()
    stream = io.BytesIO(html.encode("utf-8"))
    result = md_converter.convert_stream(
        stream, stream_info=StreamInfo(extension=".html")
    )
    return result.text_content or ""


def _simple_html_to_markdown(html: str) -> str:
    """Lightweight HTML → Markdown: handles common tags, strips the rest."""
    # Headings
    for level in range(6, 0, -1):
        html = re.sub(
            rf"<h{level}[^>]*>(.*?)</h{level}>",
            lambda m, l=level: "#" * l + " " + m.group(1).strip(),
            html,
            flags=re.I | re.DOTALL,
        )

    # Bold / italic
    html = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", html, flags=re.I | re.DOTALL)
    html = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", html, flags=re.I | re.DOTALL)
    html = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", html, flags=re.I | re.DOTALL)
    html = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", html, flags=re.I | re.DOTALL)

    # Code
    html = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", html, flags=re.I | re.DOTALL)
    html = re.sub(r"<pre[^>]*>(.*?)</pre>", r"```\n\1\n```", html, flags=re.I | re.DOTALL)

    # Links
    html = re.sub(r'<a[^>]+href="([^"]*)"[^>]*>(.*?)</a>', r"[\2](\1)", html, flags=re.I | re.DOTALL)

    # Lists
    html = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1", html, flags=re.I | re.DOTALL)
    html = re.sub(r"<[uo]l[^>]*>|</[uo]l>", "", html, flags=re.I)

    # Paragraphs and line breaks
    html = re.sub(r"<p[^>]*>", "", html, flags=re.I)
    html = re.sub(r"</p>", "\n\n", html, flags=re.I)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)

    # Horizontal rule
    html = re.sub(r"<hr\s*/?>", "\n---\n", html, flags=re.I)

    # Strip remaining HTML tags
    html = re.sub(r"<[^>]+>", "", html)

    # Unescape common HTML entities
    html = html.replace("&amp;", "&")
    html = html.replace("&lt;", "<")
    html = html.replace("&gt;", ">")
    html = html.replace("&quot;", '"')
    html = html.replace("&#39;", "'")
    html = html.replace("&nbsp;", " ")

    # Normalise whitespace
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()
