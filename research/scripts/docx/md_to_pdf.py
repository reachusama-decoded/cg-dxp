#!/usr/bin/env python3
"""Markdown -> PDF in the Decoded house style, through pandoc and Chrome's PDF printer.

    ~/.venvs/cg-dxp/bin/python md_to_pdf.py <in.md> <out.pdf> [--landscape] [--crumb "Data Creators › Day 2 — run sheet"]

pandoc turns the Markdown into an HTML fragment; a template wraps it with the fonts in ../fonts, the logo, a running
header and footer, and print CSS (A4, page breaks before each H2, tables that do not split rows); headless Chrome prints
it. Images referenced relatively are resolved against the Markdown's folder. Needs pandoc and Google Chrome.
"""
from __future__ import annotations
import argparse, html, os, pathlib, re, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE.parent / "fonts"
LOGO = HERE / "logo-decoded.png"
CHROME = os.environ.get("CHROME") or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PANDOC = os.environ.get("PANDOC") or shutil.which("pandoc") or "/opt/anaconda3/bin/pandoc"

CSS = """
@font-face { font-family: "Work Sans"; src: url("file://%(fonts)s/WorkSans/WorkSans-Regular.ttf"); font-weight: 400; }
@font-face { font-family: "Work Sans"; src: url("file://%(fonts)s/WorkSans/WorkSans-Bold.ttf"); font-weight: 700; }
@font-face { font-family: "Fira Code"; src: url("file://%(fonts)s/FiraCode/FiraCode-Regular.ttf"); }
@page { size: A4 %(orientation)s; margin: 22mm 18mm 20mm 18mm; }
html { font-size: 10.5pt; }
body { font-family: "Work Sans", Arial, sans-serif; color: #000; line-height: 1.45; margin: 0; }
table.page { width: 100%%; border-collapse: collapse; }
table.page > thead > tr > td, table.page > tfoot > tr > td, table.page > tbody > tr > td { border: 0; padding: 0; }
table.page > tbody > tr { break-inside: auto; }
.runhead, .runfoot { font-size: 8pt; color: #434343; display: flex; justify-content: space-between; }
.runhead { padding-bottom: 4mm; } .runfoot { padding-top: 4mm; }
.logo { width: 42mm; margin: 0 0 8mm 0; }
.crumb { color: #666; font-size: 9pt; margin: 0 0 2mm 0; }
h1 { font-size: 21pt; line-height: 1.2; margin: 0 0 4mm 0; padding-bottom: 3mm; border-bottom: 2.2pt solid #FEF800; }
h2 { font-size: 15pt; margin: 9mm 0 3mm 0; break-after: avoid; }
h2.pb { break-before: page; }
h3 { font-size: 12pt; margin: 6mm 0 2mm 0; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 4mm 0 1.5mm 0; break-after: avoid; }
p { margin: 0 0 2.6mm 0; }
ul, ol { margin: 0 0 2.6mm 0; padding-left: 6mm; } li { margin: 0 0 1mm 0; } li p { margin: 0; }
ul.task-list { list-style: none; padding-left: 1mm; } ul.task-list input { margin-right: 2mm; }
code { font-family: "Fira Code", Menlo, monospace; font-size: 0.88em; background: #F3F3F3; padding: 0 2px; border-radius: 2px; }
pre { background: #F3F3F3; padding: 2.5mm 3mm; border-radius: 3px; font-size: 8.6pt; line-height: 1.35; white-space: pre-wrap; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: inherit; }
table { border-collapse: collapse; width: 100%%; margin: 0 0 4mm 0; font-size: 9pt; }
th, td { border: 0.6pt solid #CCCCCC; padding: 1.6mm 2.2mm; vertical-align: top; text-align: left; }
th { background: #F3F3F3; font-weight: 700; }
tr { break-inside: avoid; } thead { display: table-header-group; }
blockquote { margin: 0 0 3mm 0; padding: 1.5mm 3mm; background: #F3F3F3; border-left: 3pt solid #434343; }
blockquote p { margin: 0; }
figure { margin: 4mm 0; text-align: center; break-inside: avoid; }
figure img { max-width: 100%%; max-height: 120mm; }
figcaption { font-size: 8.5pt; color: #666; font-style: italic; margin-top: 1.5mm; }
img { max-width: 100%%; }
a { color: #1155CC; text-decoration: none; }
hr { border: 0; border-top: 0.6pt solid #CCC; margin: 5mm 0; }
.breadcrumb { color: #666; font-size: 9pt; }
"""

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><title>%(title)s</title><style>%(css)s</style></head>
<body>
<table class="page">
<thead><tr><td><div class="runhead"><span>%(head_left)s</span><span>For instructors</span></div></td></tr></thead>
<tfoot><tr><td><div class="runfoot"><span>&nbsp;</span><span>&copy; 2026 Decoded Limited &middot; decoded.com</span></div></td></tr></tfoot>
<tbody><tr><td>
<img class="logo" src="file://%(logo)s" alt="">
%(body)s
</td></tr></tbody>
</table>
</body></html>"""

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--landscape", action="store_true")
    ap.add_argument("--crumb", default="")
    ap.add_argument("--head", default="Data Creators")
    a = ap.parse_args()
    src = pathlib.Path(a.src).resolve(); out = pathlib.Path(a.out).resolve()
    md = src.read_text()
    # a breadcrumb line written for the Word builder ([text]{.breadcrumb}) becomes the crumb if none was given
    m = re.search(r"^\[(.+?)\]\{\.breadcrumb\}\s*$", md, re.M)
    crumb = a.crumb or (m.group(1) if m else "")
    if m:
        md = md[:m.start()] + md[m.end():]
    r = subprocess.run([PANDOC, "-f", "markdown", "-t", "html5", "--no-highlight"], input=md, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr, file=sys.stderr); return 1
    body = r.stdout
    # relative images resolve against the Markdown's folder
    body = re.sub(r'src="(?!file:|https?:|data:)([^"]+)"', lambda mm: f'src="file://{(src.parent / mm.group(1)).resolve()}"', body)
    # the crumb sits under the logo, above the title; every H2 after the first starts a new page
    if crumb:
        body = re.sub(r"<h1", f'<p class="crumb">{html.escape(crumb)}</p>\n<h1', body, count=1)
    # a page break before each numbered section (an H2 whose text starts with a digit), never before the first H2
    h2s = [mm for mm in re.finditer(r"<h2([^>]*)>(.*?)</h2>", body, re.S)]
    for mm in reversed(h2s[1:]):
        if re.match(r"\s*\d", re.sub(r"<[^>]+>", "", mm.group(2))):
            body = body[:mm.start()] + '<h2 class="pb"' + body[mm.start() + 3:]
    title = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    title_text = re.sub(r"<[^>]+>", "", title.group(1)) if title else src.stem
    page = TEMPLATE % {"title": html.escape(title_text), "css": CSS % {"fonts": FONTS, "orientation": "landscape" if a.landscape else "portrait"},
                       "head_left": html.escape(f"{a.head} · {crumb}" if crumb and a.head not in crumb else html.escape(crumb or a.head)), "logo": LOGO, "body": body}
    with tempfile.TemporaryDirectory() as td:
        html_path = pathlib.Path(td) / (src.stem + ".html"); html_path.write_text(page)
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--allow-file-access-from-files", "--no-pdf-header-footer",
               "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000", f"--print-to-pdf={out}", f"file://{html_path}"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not out.exists():
        print(r.stderr[-800:], file=sys.stderr); return 1
    print(f"written {out} ({out.stat().st_size:,} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
