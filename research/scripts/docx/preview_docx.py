"""Render a .docx to page PNGs, to look at a built lesson plan without Word (user, 2026-10-16).

docx-preview draws the document in headless Chrome, Chrome prints it, and each page becomes a PNG. It is a check, not
Word: list numbers don't show (Word shows them); the house fonts are loaded from scripts/fonts/ so wrapping matches. For page
one exactly as macOS renders Word files, `qlmanage -t -s 1400 -o <dir> <file.docx>`.

    .venv/bin/python scripts/docx/preview_docx.py <file.docx> <out_dir> [first_page] [last_page]
"""

import base64
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

HERE = Path(__file__).resolve().parent
CHROME = [
    os.environ.get("CHROME"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome"),
    shutil.which("chromium"),
]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    last = int(sys.argv[4]) if len(sys.argv) > 4 else 999
    chrome = next((c for c in CHROME if c and Path(c).exists()), None)
    if not chrome:
        sys.exit("preview_docx: Chrome not found; set CHROME to its path")
    lib = HERE / "node_modules"
    if not (lib / "docx-preview").is_dir():
        sys.exit("preview_docx: run `cd scripts/docx && npm install` first")
    out.mkdir(parents=True, exist_ok=True)
    jszip = (lib / "jszip/dist/jszip.min.js").read_text()
    preview = (lib / "docx-preview/dist/docx-preview.min.js").read_text()
    data = base64.b64encode(src.read_bytes()).decode()
    # print on the document's own page shape: the lesson plan is A4 landscape (user, 2026-10-19), and an A4 portrait
    # page would crop its right-hand side
    with zipfile.ZipFile(src) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    size = "A4 landscape" if re.search(r'w:orient="landscape"', xml) else "A4"
    # the house fonts from scripts/fonts/, so lines wrap as Word wraps them and the page count is right (2026-11-04)
    fonts = HERE.parent / "fonts"
    faces = "".join(
        f"@font-face {{ font-family: '{name}'; src: url('{(fonts / rel).as_uri()}'); font-display: swap }}\n"
        for name, rel in (
            ("Work Sans", "WorkSans/WorkSans-Regular.ttf"),
            ("Work Sans SemiBold", "WorkSans/WorkSans-SemiBold.ttf"),
            ("Fira Code", "FiraCode/FiraCode-Regular.ttf"),
        )
        if (fonts / rel).exists()
    )
    page = out / f"{src.stem}.html"
    page.write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<style>{faces}@page {{ size: {size}; margin: 0 }} body {{ margin: 0; background: white }}
.docx-wrapper {{ background: white !important; padding: 0 !important }}
.docx-wrapper > section.docx {{ box-shadow: none !important; margin: 0 !important; break-after: page }}
* {{ -webkit-print-color-adjust: exact; print-color-adjust: exact }}</style>
<script>{jszip}</script><script>{preview}</script></head><body><div id="c"></div><script>
const bytes = Uint8Array.from(atob("{data}"), c => c.charCodeAt(0));
const faces = ["Work Sans", "Work Sans SemiBold", "Fira Code"].map(f => document.fonts.load("10px '" + f + "'").catch(() => null));
Promise.all(faces).then(() => docx.renderAsync(bytes, document.getElementById("c"), null, {{ breakPages: true, renderHeaders: true, renderFooters: true }}))
  .catch(e => document.body.innerText = "ERROR " + e);
</script></body></html>""")
    pdf = out / f"{src.stem}.preview.pdf"
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--virtual-time-budget=30000",
            f"--print-to-pdf={pdf}",
            page.as_uri(),
        ],
        check=True,
        capture_output=True,
    )
    reader = PdfReader(str(pdf))
    print(f"{len(reader.pages)} pages")
    for i in range(first - 1, min(last, len(reader.pages))):
        one = out / f"{src.stem}-p{i + 1}.pdf"
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        with open(one, "wb") as f:
            writer.write(f)
        png = one.with_suffix(".png")
        subprocess.run(
            ["sips", "-s", "format", "png", "-Z", "1400", str(one), "--out", str(png)],
            check=True,
            capture_output=True,
        )
        one.unlink()
        print(png)


if __name__ == "__main__":
    main()
