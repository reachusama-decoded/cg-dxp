"""Tiny notebook kit for the Data Creators anchor notebooks.

Builds nbformat notebooks from markdown/code strings and the box styles used by the CG Core
programme (see .claude/skills/lesson-build/references/notebook-boxes.md), so the anchors look
like Decoded's other notebooks. Everything here is plain HTML inside markdown cells, which
VS Code and JupyterLab both render.
"""
from __future__ import annotations
import html, pathlib, re, textwrap
import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell, new_notebook

YEAR = 2026
LOGO = '<img src="https://courseware.decoded.com/images/decoded/logo-decoded.png" align="left" width="100px"/>'
GREY = "#434343"; TEXT = "#1a1a1a"

def _d(s: str) -> str:
    return textwrap.dedent(s).strip("\n")

# ---------- instructor registry: what the run sheet mirrors ----------
# The notebook is learner-facing. Helpers that carry instructor material (what to say, the whiteboard answers,
# demo coaching, fallbacks) record it here, in the order of the notebook's sections and parts; build_all.py renders it.
REG: dict = {"sections": [], "prep": ""}

def reset():
    REG["sections"] = []; REG["prep"] = ""

def _cur_section() -> dict:
    if not REG["sections"]:
        REG["sections"].append({"n": 0, "title": "Before the first section", "anchor": "", "parts": []})
    return REG["sections"][-1]

def _cur_part() -> dict:
    sec = _cur_section()
    if not sec["parts"] or sec["parts"][-1]["kind"] != "part":
        sec["parts"].append({"kind": "part", "label": "Opening", "title": "", "time": None, "items": []})
    return sec["parts"][-1]

def _item(kind: str, payload) -> None:
    _cur_part()["items"].append((kind, payload))

# ---------- cells ----------
def md(src: str | None):
    """A markdown cell; None (an instructor-only helper that only registered its content) produces no cell."""
    return None if src is None else new_markdown_cell(_d(src))

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

def agenda(sections: list[dict], lead: str = ""):
    """The day's agenda as a table: numbered sections and what happens inside each (its parts, in order).
    sections: dicts with n, title, anchor, start ("HH:MM"), parts (list of str)."""
    lines = ["## Today", ""]
    if lead:
        lines += [lead, ""]
    lines += ["| # | Section | What happens |", "|---|---|---|"]
    for sec in sections:
        lines.append(f"| {sec['n']} | **[{sec['title']}](#{sec['anchor']})** | {' · '.join(sec['parts'])} |")
    return md("\n".join(lines))

def section(n: int, title_text: str, anchor: str):
    """A numbered section: one topic, ideally a whole cycle of demo, activity, shareback and break."""
    REG["sections"].append({"n": n, "title": title_text, "anchor": anchor, "parts": []})
    return md(f'<a id="{anchor}"></a>\n\n## {n}. {title_text}')

def part(label: str, title_text: str = "", time: str | None = None):
    """A labelled part of a section: Demo, Activity 6, Challenge 7, Shareback, Debrief, Whiteboard, Guest.
    `time` ("HH:MM", the instructor plan's start) ties the part to its run-sheet block; a part without one belongs to the previous part's block."""
    _cur_section()["parts"].append({"kind": "part", "label": label, "title": title_text, "time": time, "items": []})
    return md(f"### {label}" + (f" — {title_text}" if title_text else ""))

def break_(minutes: int, back_at: str, lunch: bool = False):
    icon, word = ("🍽️", "LUNCH") if lunch else ("☕", "BREAK")
    _cur_section()["parts"].append({"kind": "break", "minutes": minutes, "back_at": back_at, "lunch": lunch})
    return md(_box("#434343", "#EFEFEF", TEXT, "#fff", f"{icon} {word} &nbsp;·&nbsp; {minutes} min &nbsp;·&nbsp; back at {back_at}",
                   "Questions go in the table at the end; the next part starts on time."))

def figure(png: str, alt: str, bullets: list[str] | None = None, rel: str = "../common/diagrams/png", height: int | None = None):
    """`height` caps the picture's height in pixels so the figure and its bullets fit one screen."""
    body = (f'<img src="{rel}/{png}.png" alt="{alt}" style="max-height:{height}px; max-width:100%;">' if height
            else f"![{alt}]({rel}/{png}.png)")
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
    """The questions the room works through at the whiteboard. The answers rooms give, and what to add, go to the run sheet only."""
    _item("whiteboard", {"title": title_text, "items": items})
    return f"**🖊️ Whiteboard — {title_text}**\n\n" + "\n".join(f"- {q}" for q, _ in items)

def activity(number: str, title_text: str, grouping: str, minutes: int, brief: str, outputs: list[str], debrief: list[str] | None = None, early: str | None = None) -> str:
    _item("activity", {"number": number, "title": title_text, "grouping": grouping, "minutes": minutes})
    body = (f'<strong>{brief}</strong><br><br>' +
            "<strong>Produce:</strong><br>" + "<br>".join(f"• {o}" for o in outputs))
    if early:
        body += f"<br><br><strong>Finished early?</strong> {early}"
    if debrief:
        body += "<br><br><strong>Debrief questions:</strong><br>" + "<br>".join(f"• {d}" for d in debrief)
    return _box("#F8DB59", "#F8DB59", "#000", "#fffef5", f"🎯 ACTIVITY {number} &nbsp;—&nbsp; {title_text} &nbsp;·&nbsp; {grouping} &nbsp;·&nbsp; {minutes} min", body)

def _list(items: list[str], numbered: bool = True) -> str:
    return "\n".join((f"{i}. {t}" if numbered else f"- {t}") for i, t in enumerate(items, 1))

def _after(box: str, parts: list[str]) -> str:
    """A one-line box, then plain Markdown beneath it (a blank line ends the HTML block)."""
    return box + "".join("\n\n" + p for p in parts if p)

def challenge(title_text: str, path: str, minutes: str, line: str, phases: list[tuple[str, list[str]]], gate: str,
              support: list[str] | None = None, stretch: str | None = None) -> str:
    """One line in the box; what learners do, phase by phase, one line per step; then the gate, support and stretch."""
    _item("challenge", {"title": title_text, "path": path, "minutes": minutes})
    box = _box(GREY, GREY, "#fff", "#f8f8f8", f"🏆 CHALLENGE TIME &nbsp;—&nbsp; {title_text} &nbsp;·&nbsp; {minutes}",
               f"{line} &nbsp;·&nbsp; <code>{path}</code>")
    parts = [f"**{label}**\n\n{_list(steps)}" for label, steps in phases]
    parts.append(f"**Gate.** {gate}")
    if support:
        parts.append("**Support.**\n\n" + _list(support, numbered=False))
    if stretch:
        parts.append(f"**Finished early?** {stretch}")
    return _after(box, parts)

def terminal(title_text: str, body: str) -> str:
    return _box(GREY, GREY, "#fff", "#f8f8f8", f"⌨️ TERMINAL &nbsp;—&nbsp; {title_text}", body)

_COACH = re.compile(r"^(Say\b|Point at\b|After each cell\b|Let it run .*narrate|Before the day\b)")

def demo(title_text: str, line: str, steps: list[str] | None = None) -> str:
    """One line in the box; beneath it the steps learners will see, one line each.
    Coaching steps (Say …, Point at …, Before the day …) go to the run sheet only; every step is recorded there in order."""
    steps = steps or []
    _item("demo", {"title": title_text, "line": line, "steps": steps})
    shown = [s for s in steps if not _COACH.match(s)]
    box = _box("#434343", "#C9DAF8", TEXT, "#fff", f"🖥️ DEMO &nbsp;—&nbsp; {title_text}", line)
    return _after(box, [_list(shown)] if shown else [])

def reflect(title_text: str, line: str, bullets: list[str] | None = None) -> str:
    box = _box("#F8DB59", "#FFF2CC", "#000", "#fffef5", f"💭 {title_text}", line)
    return _after(box, [_list(bullets, numbered=False)] if bullets else [])

def say(lines: list[str]):
    """Instructor-only: lines to say, recorded for the run sheet. Produces no cell."""
    _item("say", lines)
    return None

def notes(title_text: str, items: list[str]):
    """Instructor-only: the explanation that goes with a picture, a table or a set of commands, recorded for the run sheet. Produces no cell."""
    _item("notes", {"title": title_text, "items": list(items)})
    return None

def command_note(command: str, text: str):
    """Instructor-only: what to say about one command. Consecutive commands share one run-sheet list. Produces no cell."""
    items = _cur_part()["items"]
    if not items or items[-1][0] != "commands":
        items.append(("commands", []))
    items[-1][1].append((command, text))
    return None

def fallback(line: str, bullets: list[str] | None = None) -> str:
    _item("fallback", {"line": line, "bullets": bullets or []})
    box = _box("#F4CCCC", "#F4CCCC", TEXT, "#fff", "🧯 IF IT BREAKS", line)
    return _after(box, [_list(bullets, numbered=False)] if bullets else [])

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
    """The learner-safe 'about this notebook' cell. `extra` (instructor preparation lines) goes to the run sheet, not the notebook."""
    if extra:
        REG["prep"] = (REG.get("prep", "") + "\n" + _d(extra)).strip()
    return [md(f"""
    <a id="how-to-use"></a>

    ## About this notebook

    - Day {day}'s anchor: the agenda, then one numbered section per topic. Each section runs as a cycle: a demo, an activity or challenge, a shareback, a break.
    - Every concept has its diagram; every demo has the cells that run it; every activity has its brief; every challenge points into the training repository.
    - Run the **Setup** cell first. Cells that start with `!` run in a shell in this notebook's folder with the demo environment on `PATH`.
    - 🖊️ Whiteboard lines are the questions the room works through together.
    - The last section, **Questions from the room**, collects the day's questions and their answers as they come.
    """)]

def setup_cell(day: int) -> str:
    return _d(f"""
    # Setup: the demo environment on PATH, a sql() helper for showing results, a quick diagram helper
    import os, sys, subprocess, textwrap
    from pathlib import Path
    from IPython.display import Image, Markdown, display

    VENV = Path(os.environ.get("CG_DXP_VENV", Path.home() / ".venvs" / "cg-dxp"))
    os.environ["PATH"] = ":".join([str(VENV / "bin"), str(Path.home() / ".local" / "bin"),
                                   "/Applications/Docker.app/Contents/Resources/bin", "/opt/homebrew/bin", os.environ["PATH"]])
    os.environ.setdefault("DBT_SEND_ANONYMOUS_USAGE_STATS", "false")
    # The notebook's own folder, courseware/day{day}-*/, found from wherever the kernel is now, so this cell can be
    # run again after a %cd into a demo folder. It also changes back to that folder.
    HERE = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / "day{day}_anchor.ipynb").exists()), None)
    assert HERE is not None, "Open this notebook from its own folder (courseware/day{day}-*)"
    os.chdir(HERE)
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
        \"\"\"Run a query against a demo warehouse file and show it as a table.\"\"\"
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
    nb = new_notebook(cells=[c for c in cells if c is not None], metadata={
        "kernelspec": {"name": "cg-dxp", "display_name": "Python (cg-dxp)", "language": "python"},
        "language_info": {"name": "python"},
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, str(path))
    return path
