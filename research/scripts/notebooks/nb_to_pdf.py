#!/usr/bin/env python3
"""Print an anchor notebook to PDF beside it: nbconvert (lab template, images embedded, prompts hidden) to HTML,
a little print CSS (A4, a page per numbered section, code wrapped), then headless Chrome.
Usage: ~/.venvs/cg-dxp/bin/python nb_to_pdf.py 2 [3 …]      -> courseware/day2-platform/day2_anchor.pdf
Outputs saved in the notebook are printed too; the notebooks are committed without outputs, so Run All and save first
if the PDF should show results."""
import pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
SLUGS = {1: "day1-design", 2: "day2-platform", 3: "day3-dbt", 4: "day4-airflow", 5: "day5-capstone"}
JUPYTER = pathlib.Path.home() / ".venvs" / "cg-dxp" / "bin" / "jupyter"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = """<style>
@page { size: A4; margin: 14mm 12mm; }
body, .jp-Notebook { max-width: none !important; padding: 0 !important; }
.jp-Cell { page-break-inside: avoid; }
h2 { page-break-before: always; }
pre { white-space: pre-wrap; word-break: break-word; font-size: 0.85em; }
img { max-width: 100%; }
</style></head>"""

def convert(day: int) -> pathlib.Path:
    folder = ROOT / "courseware" / SLUGS[day]
    nb = folder / f"day{day}_anchor.ipynb"
    pdf = folder / f"day{day}_anchor.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([str(JUPYTER), "nbconvert", "--to", "html", "--embed-images", "--template", "lab", "--no-prompt",
                        str(nb), "--output-dir", tmp, "--output", nb.stem], check=True, capture_output=True, cwd=folder)
        html = pathlib.Path(tmp) / f"{nb.stem}.html"
        html.write_text(html.read_text().replace("</head>", CSS, 1))
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--allow-file-access-from-files",
                        "--no-pdf-header-footer", f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True, timeout=300)
    return pdf

if __name__ == "__main__":
    for d in [int(a) for a in sys.argv[1:]] or [2]:
        out = convert(d)
        print(f"day {d}: {out.relative_to(ROOT)} ({out.stat().st_size / 1048576:.1f} MB)")
