"""Tiny notebook kit for the Data Creators anchor notebooks.

Builds nbformat notebooks from markdown/code strings and the box styles used by the CG Core
programme (see .claude/skills/lesson-build/references/notebook-boxes.md), so the anchors look
like Decoded's other notebooks. Everything here is plain HTML inside markdown cells, which
VS Code and JupyterLab both render.
"""
from __future__ import annotations
import html, pathlib, textwrap
import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell, new_notebook

YEAR = 2026
LOGO = '<img src="https://courseware.decoded.com/images/decoded/logo-decoded.png" align="left" width="100px"/>'
GREY = "#434343"; TEXT = "#1a1a1a"

def _d(s: str) -> str:
    return textwrap.dedent(s).strip("\n")

# ---------- cells ----------
def md(src: str):
    return new_markdown_cell(_d(src))

def code(src: str):
    return new_code_cell(_d(src))

def title(day: int, title_text: str, subtitle: str):
    return md(f"""
    {LOGO}

    # Day {day} — {title_text}

    <small>Data Creators › Day {day} — {subtitle}</small>

    ---
    <small>&copy; {YEAR} Decoded Limited. All rights reserved. [decoded.com](https://decoded.com)</small>
    """)

def heading(text: str, anchor: str, level: int = 2):
    return md(f'<a id="{anchor}"></a>\n\n{"#" * level} {text}')

def toc(rows: list[tuple[str, str, str]]):
    """rows: (section title, anchor, what happens)."""
    lines = ["## 🗺️ Table of contents", "", "| Section | What happens |", "|:---|:---|"]
    for t, a, w in rows:
        lines.append(f"| [{t}](#{a}) | {w} |")
    return md("\n".join(lines))

def figure(png: str, alt: str, bullets: list[str] | None = None, rel: str = "../common/diagrams/png"):
    body = f"![{alt}]({rel}/{png}.png)"
    if bullets:
        body += "\n\n" + "\n".join(f"- {b}" for b in bullets)
    return md(body)

# ---------- boxes ----------
def _box(border: str, head_bg: str, head_fg: str, body_bg: str, header: str, body: str) -> str:
    return (f'<div style="border:2px solid {border}; border-radius:8px; margin:10px 0;">\n'
            f'<div style="background:{head_bg}; color:{head_fg}; padding:8px 14px; font-weight:bold;">{header}</div>\n'
            f'<div style="background:{body_bg}; padding:12px 14px; color:{TEXT};">{body}</div></div>')

def anchor_box(question: str, what: str, why: str, how: str) -> str:
    tile = lambda bg, label, text: (f'<div style="flex:1; min-width:0; background:{bg}; border-radius:6px; padding:10px 12px; color:{TEXT};">'
                                    f'<div style="font-weight:bold; font-size:0.78em; letter-spacing:0.08em; margin-bottom:4px;">{label}</div>{text}</div>')
    return (f'<div style="border:2px solid {GREY}; border-radius:8px; margin:18px 0 12px; overflow:hidden;">\n'
            f'<div style="background:{GREY}; color:#fff; padding:8px 14px; font-weight:bold;">🧭 WHAT, WHY AND HOW</div>\n'
            f'<div style="background:#F3F3F3; padding:10px 14px; color:{TEXT}; font-style:italic;">{question}</div>\n'
            f'<div style="display:flex; gap:8px; padding:10px; background:#fff;">{tile("#D0E0E3", "WHAT", what)}{tile("#FFF2CC", "WHY", why)}{tile("#D9EAD3", "HOW", how)}</div></div>')

def anchor(question, what, why, how):
    return md(anchor_box(question, what, why, how))

def whiteboard(title_text: str, items: list[tuple[str, str]], open_: bool = False) -> str:
    """A folded whiteboard script: (question to ask, answers the room gives / add)."""
    rows = "".join(f"<tr><td style='vertical-align:top;padding:6px 10px;border-top:1px solid #ccc;width:38%'><strong>{q}</strong></td>"
                   f"<td style='vertical-align:top;padding:6px 10px;border-top:1px solid #ccc'>{a}</td></tr>" for q, a in items)
    return (f'<details{" open" if open_ else ""}><summary><strong>🖊️ Whiteboard — {title_text}</strong> (ask, write what the room says, add what is missing)</summary>\n'
            f'<table style="width:100%;border-collapse:collapse;margin:8px 0;color:{TEXT}"><tr><th style="text-align:left;padding:6px 10px;background:#F3F3F3">Ask</th>'
            f'<th style="text-align:left;padding:6px 10px;background:#F3F3F3">Expect, then add</th></tr>{rows}</table></details>')

def activity(number: str, title_text: str, grouping: str, minutes: int, brief: str, outputs: list[str], debrief: list[str] | None = None, early: str | None = None) -> str:
    body = (f'<strong>{brief}</strong><br><br>' +
            "<strong>Produce:</strong><br>" + "<br>".join(f"• {o}" for o in outputs))
    if early:
        body += f"<br><br><strong>Finished early?</strong> {early}"
    if debrief:
        body += "<br><br><strong>Debrief questions:</strong><br>" + "<br>".join(f"• {d}" for d in debrief)
    return _box("#F8DB59", "#F8DB59", "#000", "#fffef5", f"🎯 ACTIVITY {number} &nbsp;—&nbsp; {title_text} &nbsp;·&nbsp; {grouping} &nbsp;·&nbsp; {minutes} min", body)

def challenge(title_text: str, path: str, minutes: str, body: str) -> str:
    return _box(GREY, GREY, "#fff", "#f8f8f8", f"🏆 CHALLENGE TIME &nbsp;—&nbsp; {title_text} &nbsp;·&nbsp; {minutes}",
                f"In the training repository: <code>{path}</code>.<br><br>{body}")

def terminal(title_text: str, body: str) -> str:
    return _box(GREY, GREY, "#fff", "#f8f8f8", f"⌨️ TERMINAL &nbsp;—&nbsp; {title_text}", body)

def demo(title_text: str, body: str) -> str:
    return _box("#434343", "#C9DAF8", TEXT, "#fff", f"🖥️ DEMO &nbsp;—&nbsp; {title_text}", body)

def reflect(title_text: str, body: str) -> str:
    return _box("#F8DB59", "#FFF2CC", "#000", "#fffef5", f"💭 {title_text}", body)

def say(lines: list[str]) -> str:
    return _box("#D9EAD3", "#D9EAD3", TEXT, "#fff", "🗣️ SAY", "<br>".join(f"“{l}”" for l in lines))

def fallback(body: str) -> str:
    return _box("#F4CCCC", "#F4CCCC", TEXT, "#fff", "🧯 IF IT BREAKS", body)

def prompt(where: str, text: str, claude: str | None = None) -> str:
    badge = lambda l, bg, v: (f'<span style="display:inline-block;margin:0 6px 4px 0;border:1px solid {GREY};border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;">'
                              f'<span style="background:{bg};color:{TEXT};padding:2px 7px;font-weight:700;letter-spacing:0.05em;">{l}</span><span style="background:#fff;color:{TEXT};padding:2px 7px;">{v}</span></span>')
    body = badge("LEARNERS", "#D0E0E3", "Copilot Chat · " + where) + f'<pre style="white-space:pre-wrap;background:#f8f8f8;padding:8px;border-radius:4px;">{html.escape(text)}</pre>'
    if claude:
        body += badge("INSTRUCTOR", "#C9DAF8", "Claude Code") + f'<pre style="white-space:pre-wrap;background:#f8f8f8;padding:8px;border-radius:4px;">{html.escape(claude)}</pre>'
    return _box(GREY, "#D0E0E3", TEXT, "#fff", "🤖 PROMPT", body)

def leave_with(items: list[str]) -> str:
    return _box("#434343", "#D9EAD3", TEXT, "#fff", "✅ BEFORE LEARNERS LEAVE", "<br>".join(f"☐ {i}" for i in items))

# ---------- standard cells ----------
def how_to_use(day: int, extra: str = "") -> list:
    return [md(f"""
    <a id="how-to-use"></a>

    ## How to use this notebook

    - This is the anchor for Day {day}: the agenda, every concept with its diagram, the whiteboard scripts, the activity briefs and the pointers into the learners' challenges. Keep it on the projector; switch to a terminal or the browser when a 🖥️ DEMO box says so.
    - Run the **Setup** cell first. Cells that start with `!` run in a shell in this notebook's folder with the demo environment on `PATH`.
    - 🖊️ Whiteboard blocks are folded: open one when you reach it, ask the questions in order, write what the room says, add what is missing.
    - The last section, **Questions from the room**, is yours to type in during the day: a table for questions, an empty cell to answer with SQL or Python, and `quick_diagram(...)` to sketch a diagram inline before reaching for Excalidraw.
    - Learners can be given this notebook as it is; nothing in it is instructor-only. The instructor-only timing notes are in `run-sheet.md` beside it.
    {extra}
    """)]

def setup_cell(day: int) -> str:
    return _d(f"""
    # Setup: the demo environment on PATH, DuckDB and pandas for showing results, a quick diagram helper
    import os, sys, subprocess, textwrap
    from pathlib import Path
    from IPython.display import Image, Markdown, display

    VENV = Path(os.environ.get("CG_DXP_VENV", Path.home() / ".venvs" / "cg-dxp"))
    os.environ["PATH"] = ":".join([str(VENV / "bin"), str(Path.home() / ".local" / "bin"),
                                   "/Applications/Docker.app/Contents/Resources/bin", "/opt/homebrew/bin", os.environ["PATH"]])
    os.environ.setdefault("DBT_SEND_ANONYMOUS_USAGE_STATS", "false")
    HERE = Path.cwd()                      # courseware/day{day}-*/
    COMMON = HERE.parent / "common"
    assert COMMON.exists(), "Open this notebook from its own folder (courseware/day{day}-*)"

    def quick_diagram(mermaid: str, name: str = "scratch"):
        \"\"\"Render a Mermaid diagram typed live and show it inline (needs node; first use downloads mermaid-cli).\"\"\"
        src = HERE / f"{{name}}.mmd"; out = HERE / f"{{name}}.png"
        src.write_text(textwrap.dedent(mermaid).strip() + "\\n")
        cfg = COMMON / "diagrams" / "mermaid-config.json"
        r = subprocess.run(["npx", "-y", "-p", "@mermaid-js/mermaid-cli@11.17.0", "mmdc", "-i", str(src), "-o", str(out), "-c", str(cfg), "-b", "white", "-s", "2"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-800:]); return
        display(Image(filename=str(out)))

    def sql(query: str, db: Path, read_only: bool = True):
        \"\"\"Run a query against a DuckDB file and show it as a table.\"\"\"
        import duckdb, pandas as pd
        pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
        con = duckdb.connect(str(db), read_only=read_only)
        try:
            return con.execute(query).df()
        finally:
            con.close()

    print("✅ Day {day} setup:", subprocess.run(["dbt", "--version"], capture_output=True, text=True).stdout.split("\\n")[1].strip() if subprocess.run(["which", "dbt"], capture_output=True).returncode == 0 else "dbt not on PATH: run common/env/setup-env.sh")
    """)

def qa_section(day: int) -> list:
    return [
        heading("Questions from the room", "questions"),
        md("""
        Type the question in the table as it comes; answer live in the cells below; tidy up at the break. Anything unanswered goes to the platform team or the Teams channel, with the person who asked.

        | # | Question | Who asked | Answer / where it went |
        |---|---|---|---|
        | 1 |  |  |  |
        | 2 |  |  |  |
        | 3 |  |  |  |
        """),
        code("# Answer live here: SQL against a demo warehouse, a small Python check, or a shell command.\n# Example: sql(\"select * from training_demo.stg_holdings limit 5\", HERE / \"demos/portfolio_analytics/warehouse/training_dev.duckdb\")\n"),
        code('# Sketch a diagram live (before Excalidraw). Edit and run.\nquick_diagram("""\nflowchart LR\n  A[source file] --> B[dbt rules on Databricks] --> C[consumer table]\n""")\n'),
        md(f"**Answers written up after the day** — fill in here, then share the notebook.\n\n- "),
        md(f"---\n<small>&copy; {YEAR} Decoded Limited. All rights reserved. [decoded.com](https://decoded.com)</small>"),
    ]

def write(cells: list, path: pathlib.Path):
    nb = new_notebook(cells=cells, metadata={
        "kernelspec": {"name": "cg-dxp", "display_name": "Python (cg-dxp)", "language": "python"},
        "language_info": {"name": "python"},
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, str(path))
    return path
