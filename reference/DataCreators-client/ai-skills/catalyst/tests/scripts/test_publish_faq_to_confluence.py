"""Guard: the FAQ converts to valid Confluence storage format, and cannot
publish links that would 404.

This script writes to a shared Confluence space that other teams read. The two
failure modes that matter are both silent: malformed storage format (Confluence
rejects the whole page, or worse accepts it and renders garbage), and relative
links that resolve against the Pages site and therefore 404 for every Confluence
reader.

Everything here is offline — the converter is pure, and the publish path is
exercised through fakes.
"""
from __future__ import annotations

import importlib.util
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "publish_faq_to_confluence.py"
FAQ = REPO_ROOT / "docs" / "getting-started-faq.html"

NS = ('<root xmlns:ac="http://atlassian.com/content" '
      'xmlns:ri="http://atlassian.com/resource/identifier">{}</root>')


@pytest.fixture(scope="module")
def pub():
    spec = importlib.util.spec_from_file_location("publish_faq", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def faq_html():
    return FAQ.read_text(encoding="utf-8")


def page(html: str) -> str:
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>p{{}}</style>" \
           f"</head><body>{html}</body></html>"


# ---------------------------------------------------------------------------
# The real document
# ---------------------------------------------------------------------------

def test_the_real_faq_produces_valid_storage_format(pub, faq_html):
    """Malformed storage means Confluence rejects the page, or renders garbage."""
    body, _ = pub.build_storage(faq_html, "https://example.invalid/catalyst/")
    ET.fromstring(NS.format(body))          # raises on malformed XML


def test_the_real_faq_keeps_its_structure(pub, faq_html):
    """A conversion that silently drops sections is worse than not publishing."""
    body, _ = pub.build_storage(faq_html, "https://example.invalid/catalyst/")
    assert body.count("<h2>") >= 5, "section headings lost"
    assert body.count("<h3>") >= 15, "question headings lost"
    assert body.count("<table>") >= 6, "tables lost"
    assert 'ac:name="code"' in body, "code blocks lost"
    assert 'ac:name="info"' in body, "callouts lost"
    assert len(body) > 20_000, f"suspiciously small output: {len(body)} bytes"


def test_head_with_void_tags_does_not_swallow_the_body(pub):
    """The bug this test exists for.

    A drop *counter* increments on every descendant of <head>, and <meta>/<link>
    never emit an end tag — so the counter never returns to zero and the entire
    body is dropped. The first run of this script produced 483 bytes for a 47KB
    document. A stack keyed on the dropped tag is what fixes it.
    """
    html = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='x'><link rel='icon' href='y'>"
            "<title>t</title><style>p{color:red}</style></head>"
            "<body><h2>Kept</h2><p>Body survived.</p></body></html>")
    body, _ = pub.build_storage(html, None)
    assert "Kept" in body and "Body survived." in body
    assert "color:red" not in body and "viewport" not in body


# ---------------------------------------------------------------------------
# Relative links — the guard
# ---------------------------------------------------------------------------

def test_relative_links_are_reported(pub):
    _body, rel = pub.build_storage(page('<a href="release-comms/x.html">r</a>'), None)
    assert rel == ["release-comms/x.html"]


def test_absolute_and_mailto_and_anchors_are_left_alone(pub):
    html = page('<a href="https://x.invalid/a">a</a><a href="mailto:x@y.z">m</a>'
                '<a href="#frag">f</a>')
    body, rel = pub.build_storage(html, None)
    assert rel == []
    for href in ("https://x.invalid/a", "mailto:x@y.z", "#frag"):
        assert f'href="{href}"' in body


def test_site_base_absolutises_relative_links(pub):
    body, rel = pub.build_storage(
        page('<a href="./">home</a><a href="release-comms/x.html">r</a>'),
        "https://site.invalid/catalyst")
    assert rel  # still reported
    assert 'href="https://site.invalid/catalyst/"' in body
    assert 'href="https://site.invalid/catalyst/release-comms/x.html"' in body


def test_publish_refuses_when_relative_links_have_no_site_base(pub, tmp_path):
    """Exit 2, not a publish. Broken links for every reader is the worse outcome."""
    faq = tmp_path / "faq.html"
    faq.write_text(page('<a href="release-comms/x.html">r</a>'))
    assert pub.main(["--faq", str(faq)]) == 2


# ---------------------------------------------------------------------------
# Conversion details
# ---------------------------------------------------------------------------

def test_note_divs_become_info_macros(pub):
    body, _ = pub.build_storage(
        page('<div class="note"><div class="t">T</div><p>Body</p></div>'), None)
    assert 'ac:structured-macro ac:name="info"' in body
    assert "<p>Body</p>" in body


def test_plain_divs_do_not_become_macros(pub):
    """Only `div.note` is a callout. The one macro present is the generated banner."""
    body, _ = pub.build_storage(page('<div><p>plain</p></div>'), None)
    assert body.count('ac:name="info"') == 1
    assert "<p>plain</p>" in body


def test_pre_becomes_a_code_macro_with_cdata(pub):
    body, _ = pub.build_storage(
        page("<pre><code>claude --version</code></pre>"), None)
    assert 'ac:name="code"' in body
    assert "<![CDATA[claude --version]]>" in body


def test_cdata_terminator_in_source_cannot_break_the_page(pub):
    """`]]>` inside a code block would close the CDATA early and corrupt it."""
    body, _ = pub.build_storage(page("<pre><code>echo a]]>b</code></pre>"), None)
    assert "a]]>b" not in body
    ET.fromstring(NS.format(body))


def test_q_chip_is_dropped_but_the_question_survives(pub):
    body, _ = pub.build_storage(
        page('<h3><span class="q">Q:</span> How do I install it?</h3>'), None)
    assert "How do I install it?" in body
    assert "Q:" not in body


def test_pending_chip_becomes_readable_text(pub):
    """The chip is pure CSS; unconverted it would vanish and read as a fact."""
    body, _ = pub.build_storage(
        page('<p>Causeway<span class="pending">link pending</span></p>'), None)
    assert "(link pending)" in body


def test_presentational_attributes_are_stripped(pub):
    body, _ = pub.build_storage(
        page('<p class="x" style="color:red">t</p>'), None)
    assert "class=" not in body and "style=" not in body


def test_text_is_xml_escaped(pub):
    body, _ = pub.build_storage(page("<p>a &lt; b &amp; c</p>"), None)
    assert "&lt;" in body and "&amp;" in body
    ET.fromstring(NS.format(body))


def test_generated_banner_names_the_source_of_truth(pub, faq_html):
    """Someone editing in Confluence must be told their edit will be lost."""
    body, _ = pub.build_storage(faq_html, "https://example.invalid/")
    assert "generated" in body.lower()
    assert "docs/getting-started-faq.html" in body
    assert "cg-open-itg/catalyst" in body


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

def test_hash_marker_round_trips(pub, faq_html):
    body, _ = pub.build_storage(faq_html, "https://example.invalid/")
    assert pub.published_hash(body) == pub.rendered_hash(body)


def test_hash_changes_when_the_faq_changes(pub):
    assert pub.content_hash("<p>a</p>") != pub.content_hash("<p>b</p>")


def test_changing_site_base_invalidates_the_page(pub, faq_html):
    """Hashing the *source* missed this: same FAQ, different docs host, so every
    absolute link changes — and the page reported itself up to date with stale links."""
    a, _ = pub.build_storage(faq_html, "https://a.invalid/catalyst/")
    b, _ = pub.build_storage(faq_html, "https://b.invalid/catalyst/")
    assert pub.published_hash(a) != pub.published_hash(b)


def test_an_edit_made_in_confluence_is_detected(pub, faq_html):
    """The banner promises the page is overwritten on the next publish. A
    source-only hash let a human edit survive while reporting "up to date"."""
    body, _ = pub.build_storage(faq_html, "https://example.invalid/")
    edited = body.replace("<p>", "<p>EDITED ", 1)
    assert pub.rendered_hash(edited) != pub.published_hash(body)


def test_the_hash_excludes_its_own_marker(pub, faq_html):
    """Otherwise it would have to hash its own value."""
    body, _ = pub.build_storage(faq_html, "https://example.invalid/")
    assert pub.HASH_MARKER not in pub.rendered_hash(body)
    stripped = body.rsplit("<p><!--", 1)[0]
    assert pub.rendered_hash(body) == pub.content_hash(stripped)


def test_missing_marker_reads_as_unpublished(pub):
    assert pub.published_hash("<p>no marker here</p>") is None
    assert pub.published_hash("") is None


# ---------------------------------------------------------------------------
# Invocation
# ---------------------------------------------------------------------------

def test_missing_faq_file_is_an_error(pub):
    assert pub.main(["--faq", "/nonexistent/faq.html"]) == 2


def test_print_storage_needs_no_credentials(pub, capsys, tmp_path, monkeypatch):
    """The conversion must be reviewable without touching Confluence."""
    monkeypatch.delenv("CONFLUENCE_URL", raising=False)
    faq = tmp_path / "faq.html"
    faq.write_text(page("<p>hello</p>"))
    assert pub.main(["--faq", str(faq), "--print-storage"]) == 0
    assert "hello" in capsys.readouterr().out


def test_a_duplicate_title_explains_itself_rather_than_tracebacking(pub, tmp_path,
                                                                    monkeypatch):
    """Confluence titles are unique per *space*, but find_child_by_title only looks
    under our parent — so a moved page makes create fail with an unhelpful 400."""
    import requests

    faq = tmp_path / "faq.html"
    faq.write_text(page("<p>hi</p>"))

    class FakeResponse:
        status_code = 400

    class FakeClient:
        def __init__(self, *a, **k): pass
        def find_child_by_title(self, *a, **k): return None
        def create_page(self, *a, **k):
            raise requests.HTTPError("Bad Request", response=FakeResponse())

    monkeypatch.setattr(pub, "load_env",
                        lambda: {"base_url": "https://x.invalid",
                                 "email": "e", "token": "t"})
    import skills.clients.confluence as cc
    monkeypatch.setattr(cc, "ConfluenceClient", FakeClient)

    rc = pub.main(["--faq", str(faq), "--site-base", "https://s.invalid/", "--apply"])
    assert rc == 2


def test_the_token_is_never_printed(pub):
    """This runs in a terminal whose output gets pasted into tickets and chats."""
    src = (REPO_ROOT / "scripts" / "publish_faq_to_confluence.py").read_text()
    # The token reaches exactly one place: the client constructor.
    assert src.count('cfg["token"]') == 1
    assert 'print' not in src.split('cfg["token"]')[0].rsplit("\n", 1)[-1]


def test_defaults_target_the_onboarding_parent(pub):
    """Wrong parent means the FAQ lands somewhere nobody is looking."""
    assert pub.DEFAULT_PARENT_ID == "404951408"
    assert pub.DEFAULT_SPACE == "ENTDATA"
