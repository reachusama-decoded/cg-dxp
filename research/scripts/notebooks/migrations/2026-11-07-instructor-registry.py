"""One-off (7 Nov 2026): SAY and whiteboard scripts leave the notebooks for the run sheet; demo coaching too; agenda as a table;
run sheet mirrors the notebook's sections and parts. Also stamps part times."""
import pathlib, ast
HERE = pathlib.Path(__file__).resolve().parent.parent

def patch(path, pairs):
    s = path.read_text()
    for old, new in pairs:
        assert s.count(old) == 1, f"{path.name}: {s.count(old)} matches for {old[:70]!r}"
        s = s.replace(old, new)
    ast.parse(s); path.write_text(s); print("patched", path.name)

# ---------------- dc.py ----------------
patch(HERE / "dc.py", [
('''import html, pathlib, textwrap
import nbformat''', '''import html, pathlib, re, textwrap
import nbformat'''),
('''def _d(s: str) -> str:
    return textwrap.dedent(s).strip("\\n")
''', '''def _d(s: str) -> str:
    return textwrap.dedent(s).strip("\\n")

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
'''),
('''def md(src: str):
    return new_markdown_cell(_d(src))''', '''def md(src: str | None):
    """A markdown cell; None (an instructor-only helper that only registered its content) produces no cell."""
    return None if src is None else new_markdown_cell(_d(src))'''),
('''def agenda(sections: list[dict], lead: str = ""):
    """The day's agenda: numbered sections, each with what happens inside it (its parts, in order).
    sections: dicts with n, title, anchor, start ("HH:MM"), parts (list of str)."""
    lines = ["## Today", ""]
    if lead:
        lines += [lead, ""]
    for sec in sections:
        lines.append(f"{sec['n']}. **[{sec['title']}](#{sec['anchor']})**<br>")
        lines.append(f"   {' · '.join(sec['parts'])}")
    return md("\\n".join(lines))

def section(n: int, title_text: str, anchor: str):
    """A numbered section: one topic, ideally a whole cycle of demo, activity, shareback and break."""
    return md(f'<a id="{anchor}"></a>\\n\\n## {n}. {title_text}')

def part(label: str, title_text: str = ""):
    """A labelled part of a section: Demo, Activity 6, Challenge 7, Shareback, Debrief, Whiteboard, Guest."""
    return md(f"### {label}" + (f" — {title_text}" if title_text else ""))

def break_(minutes: int, back_at: str, lunch: bool = False):
    icon, word = ("🍽️", "LUNCH") if lunch else ("☕", "BREAK")
    return md(_box("#434343", "#EFEFEF", TEXT, "#fff", f"{icon} {word} &nbsp;·&nbsp; {minutes} min &nbsp;·&nbsp; back at {back_at}",
                   "Questions go in the table at the end; the next part starts on time."))''',
'''def agenda(sections: list[dict], lead: str = ""):
    """The day's agenda as a table: numbered sections and what happens inside each (its parts, in order).
    sections: dicts with n, title, anchor, start ("HH:MM"), parts (list of str)."""
    lines = ["## Today", ""]
    if lead:
        lines += [lead, ""]
    lines += ["| # | Section | What happens |", "|---|---|---|"]
    for sec in sections:
        lines.append(f"| {sec['n']} | **[{sec['title']}](#{sec['anchor']})** | {' · '.join(sec['parts'])} |")
    return md("\\n".join(lines))

def section(n: int, title_text: str, anchor: str):
    """A numbered section: one topic, ideally a whole cycle of demo, activity, shareback and break."""
    REG["sections"].append({"n": n, "title": title_text, "anchor": anchor, "parts": []})
    return md(f'<a id="{anchor}"></a>\\n\\n## {n}. {title_text}')

def part(label: str, title_text: str = "", time: str | None = None):
    """A labelled part of a section: Demo, Activity 6, Challenge 7, Shareback, Debrief, Whiteboard, Guest.
    `time` ("HH:MM", the instructor plan's start) ties the part to its run-sheet block; a part without one belongs to the previous part's block."""
    _cur_section()["parts"].append({"kind": "part", "label": label, "title": title_text, "time": time, "items": []})
    return md(f"### {label}" + (f" — {title_text}" if title_text else ""))

def break_(minutes: int, back_at: str, lunch: bool = False):
    icon, word = ("🍽️", "LUNCH") if lunch else ("☕", "BREAK")
    _cur_section()["parts"].append({"kind": "break", "minutes": minutes, "back_at": back_at, "lunch": lunch})
    return md(_box("#434343", "#EFEFEF", TEXT, "#fff", f"{icon} {word} &nbsp;·&nbsp; {minutes} min &nbsp;·&nbsp; back at {back_at}",
                   "Questions go in the table at the end; the next part starts on time."))'''),
('''def whiteboard(title_text: str, items: list[tuple[str, str]], open_: bool = False) -> str:
    """A folded whiteboard script: (question to ask, answers the room gives / add)."""
    rows = "".join(f"<tr><td style='vertical-align:top;padding:6px 10px;border-top:1px solid #ccc;width:38%'><strong>{q}</strong></td>"
                   f"<td style='vertical-align:top;padding:6px 10px;border-top:1px solid #ccc'>{a}</td></tr>" for q, a in items)
    return (f'<details{" open" if open_ else ""}><summary><strong>🖊️ Whiteboard — {title_text}</strong> (ask, write what the room says, add what is missing)</summary>\\n'
            f'<table style="width:100%;border-collapse:collapse;margin:8px 0;color:{TEXT}"><tr><th style="text-align:left;padding:6px 10px;background:#F3F3F3">Ask</th>'
            f'<th style="text-align:left;padding:6px 10px;background:#F3F3F3">Expect, then add</th></tr>{rows}</table></details>')''',
'''def whiteboard(title_text: str, items: list[tuple[str, str]], open_: bool = False) -> str:
    """The questions the room works through at the whiteboard. The answers rooms give, and what to add, go to the run sheet only."""
    _item("whiteboard", {"title": title_text, "items": items})
    return f"**🖊️ Whiteboard — {title_text}**\\n\\n" + "\\n".join(f"- {q}" for q, _ in items)'''),
('''def activity(number: str, title_text: str, grouping: str, minutes: int, brief: str, outputs: list[str], debrief: list[str] | None = None, early: str | None = None) -> str:
    body = (''', '''def activity(number: str, title_text: str, grouping: str, minutes: int, brief: str, outputs: list[str], debrief: list[str] | None = None, early: str | None = None) -> str:
    _item("activity", {"number": number, "title": title_text, "grouping": grouping, "minutes": minutes})
    body = ('''),
('''    """One line in the box; what learners do, phase by phase, one line per step; then the gate, support and stretch."""
    box = _box(GREY, GREY, "#fff", "#f8f8f8", f"🏆 CHALLENGE TIME &nbsp;—&nbsp; {title_text} &nbsp;·&nbsp; {minutes}",''',
'''    """One line in the box; what learners do, phase by phase, one line per step; then the gate, support and stretch."""
    _item("challenge", {"title": title_text, "path": path, "minutes": minutes})
    box = _box(GREY, GREY, "#fff", "#f8f8f8", f"🏆 CHALLENGE TIME &nbsp;—&nbsp; {title_text} &nbsp;·&nbsp; {minutes}",'''),
('''def demo(title_text: str, line: str, steps: list[str] | None = None) -> str:
    """One line in the box; the exact steps to show learners beneath it, one line each."""
    box = _box("#434343", "#C9DAF8", TEXT, "#fff", f"🖥️ DEMO &nbsp;—&nbsp; {title_text}", line)
    return _after(box, [_list(steps)] if steps else [])''',
'''_COACH = re.compile(r"^(Say\\b|Point at\\b|After each cell\\b|Let it run .*narrate|Before the day\\b)")

def demo(title_text: str, line: str, steps: list[str] | None = None) -> str:
    """One line in the box; beneath it the steps learners will see, one line each.
    Coaching steps (Say …, Point at …, Before the day …) go to the run sheet only; every step is recorded there in order."""
    steps = steps or []
    _item("demo", {"title": title_text, "line": line, "steps": steps})
    shown = [s for s in steps if not _COACH.match(s)]
    box = _box("#434343", "#C9DAF8", TEXT, "#fff", f"🖥️ DEMO &nbsp;—&nbsp; {title_text}", line)
    return _after(box, [_list(shown)] if shown else [])'''),
('''def say(lines: list[str]) -> str:
    return _box("#D9EAD3", "#D9EAD3", TEXT, "#fff", "🗣️ SAY", "<br>".join(f"“{l}”" for l in lines))''',
'''def say(lines: list[str]):
    """Instructor-only: lines to say, recorded for the run sheet. Produces no cell."""
    _item("say", lines)
    return None'''),
('''def fallback(line: str, bullets: list[str] | None = None) -> str:
    box = _box("#F4CCCC", "#F4CCCC", TEXT, "#fff", "🧯 IF IT BREAKS", line)''',
'''def fallback(line: str, bullets: list[str] | None = None) -> str:
    _item("fallback", {"line": line, "bullets": bullets or []})
    box = _box("#F4CCCC", "#F4CCCC", TEXT, "#fff", "🧯 IF IT BREAKS", line)'''),
('''def how_to_use(day: int, extra: str = "") -> list:
    return [md(f"""
    <a id="how-to-use"></a>

    ## How to use this notebook

    - This is the anchor for Day {day}: a numbered agenda, then one section per topic, each a cycle of demo, activity or challenge, shareback and break. Every concept has its diagram, every demo its steps, every activity its brief, every challenge its pointer into the learners' repository. Keep it on the projector; switch to a terminal or the browser when a 🖥️ DEMO box says so. Timings are in `run-sheet.md`.
    - Run the **Setup** cell first. Cells that start with `!` run in a shell in this notebook's folder with the demo environment on `PATH`.
    - 🖊️ Whiteboard blocks are folded: open one when you reach it, ask the questions in order, write what the room says, add what is missing.
    - The last section, **Questions from the room**, is yours to type in during the day: a table for questions, an empty cell to answer with SQL or Python, and `quick_diagram(...)` to sketch a diagram inline before reaching for Excalidraw.
    - Learners can be given this notebook as it is; nothing in it is instructor-only. The instructor-only timing notes are in `run-sheet.md` beside it.
    {extra}
    """)]''',
'''def how_to_use(day: int, extra: str = "") -> list:
    """The learner-safe 'about this notebook' cell. `extra` (instructor preparation lines) goes to the run sheet, not the notebook."""
    if extra:
        REG["prep"] = (REG.get("prep", "") + "\\n" + _d(extra)).strip()
    return [md(f"""
    <a id="how-to-use"></a>

    ## About this notebook

    - Day {day}'s anchor: the agenda, then one numbered section per topic. Each section runs as a cycle: a demo, an activity or challenge, a shareback, a break.
    - Every concept has its diagram; every demo has the cells that run it; every activity has its brief; every challenge points into the training repository.
    - Run the **Setup** cell first. Cells that start with `!` run in a shell in this notebook's folder with the demo environment on `PATH`.
    - 🖊️ Whiteboard lines are the questions the room works through together.
    - The last section, **Questions from the room**, collects the day's questions and their answers as they come.
    """)]'''),
('''def write(cells: list, path: pathlib.Path):
    nb = new_notebook(cells=cells, metadata={''', '''def write(cells: list, path: pathlib.Path):
    nb = new_notebook(cells=[c for c in cells if c is not None], metadata={'''),
])

# ---------------- build_all.py ----------------
p = HERE / "build_all.py"; s = p.read_text()
start = s.index("def run_sheet_md(mod) -> str:"); end = s.index("def build(day_name: str):")
new_rs = '''def _start(b: dict) -> int:
    return _mins(b["time"].split("–")[0])

def run_sheet_md(mod, reg) -> str:
    """The instructor's companion, in the notebook's order: the same numbered sections and labelled parts; each part carries its block's
    purpose, on-screen note, instructor notes, lines to say, the whiteboard script with answers, the demo steps with coaching, fallbacks,
    the transition and the flex. The time table from the instructor plan stays at the top."""
    secs = getattr(mod, "SECTIONS", [])
    out = [f"# Day {mod.DAY} run sheet — {mod.TITLE}", "",
           "Instructor-only companion to the anchor notebook, in the notebook's order: the same numbered sections and labelled parts, each with its time, purpose, what is on screen, what to say, what to ask at the whiteboard (with the answers rooms give and what to add), the demo steps with their coaching, fallbacks, the transition and what to do if ahead or behind. Keep the notebook on the projector and this beside it. Times follow the instructor plan; adapt them to the room and keep the sequence.", ""]
    if reg.get("prep"):
        out += ["## Before the day", "", reg["prep"], ""]
    if secs:
        out += ["## Sections", "", "| # | Section | Time | What happens |", "|---|---|---|---|"]
        for i, sec in enumerate(secs):
            end = secs[i + 1]["start"] if i + 1 < len(secs) else "15:00"
            out.append(f"| {sec['n']} | {sec['title']} | {sec['start']}–{end} | {' · '.join(sec['parts'])} |")
        out.append("")
    out += ["## Timeline", "", "| § | Time | Block | Type | On screen |", "|---|---|---|---|---|"]
    for b in mod.BLOCKS:
        out.append(f"| {section_of(mod, b)} | {b['time']} | {b['title']} | {b['type']} | {b['on_screen']} |")
    out.append("")
    # map each part to the instructor-plan block that starts at its time; a part without a time inherits the previous part's block
    by_start = {_start(b): b for b in mod.BLOCKS}
    flat = [p for sec in reg["sections"] for p in sec["parts"]]
    current, mapped = None, []
    for p in flat:
        if p["kind"] == "part" and p.get("time"):
            current = by_start.get(_mins(p["time"]), current)
        mapped.append(current if p["kind"] == "part" else None)
    first, last = {}, {}
    for i, b in enumerate(mapped):
        if b is not None:
            first.setdefault(id(b), i); last[id(b)] = i
    i = -1
    for sec in reg["sections"]:
        out += [f"## {sec['n']}. {sec['title']}" if sec["n"] else f"## {sec['title']}", ""]
        for p in sec["parts"]:
            i += 1
            if p["kind"] == "break":
                out += [f"> {'🍽️ Lunch' if p['lunch'] else '☕ Break'} · {p['minutes']} min · back at {p['back_at']}", ""]
                continue
            b = mapped[i]
            head = f"### {p['label']}" + (f" — {p['title']}" if p["title"] else "") + (f" · {b['time']}" if b else "")
            out += [head, ""]
            if b and first[id(b)] == i:
                out += [f"**Purpose.** {b['purpose']}", "", f"**On screen.** {b['on_screen']}", ""]
                if b.get("notes"):
                    out += ["**Instructor notes.**", ""] + [f"- {n}" for n in b["notes"]] + [""]
                if b.get("say"):
                    out += ["**Say.**", ""] + [f"- “{x}”" for x in b["say"]] + [""]
            for kind, pl in p["items"]:
                if kind == "say":
                    out += ["**Say.**", ""] + [f"- “{x}”" for x in pl] + [""]
                elif kind == "whiteboard":
                    out += [f"**Ask at the whiteboard — {pl['title']}.** Ask in order, write what the room says, add what is missing.", "",
                            "| Ask | Expect, then add |", "|---|---|"] + [f"| {q} | {a} |" for q, a in pl["items"]] + [""]
                elif kind == "demo":
                    out += [f"**Demo — {pl['title']}.** {pl['line']}", ""] + [f"{k}. {x}" for k, x in enumerate(pl["steps"], 1)] + [""]
                elif kind == "fallback":
                    out += [f"**If it breaks.** {pl['line']}", ""] + ([f"- {x}" for x in pl["bullets"]] + [""] if pl["bullets"] else [])
                elif kind == "activity":
                    out += [f"**Activity {pl['number']} — {pl['title']}.** {pl['grouping']}, {pl['minutes']} min; the card is in `activities/`.", ""]
                elif kind == "challenge":
                    out += [f"**Challenge — {pl['title']}.** `{pl['path']}` · {pl['minutes']}.", ""]
            if b and last[id(b)] == i:
                if b.get("transition"):
                    out += [f"**Transition.** {b['transition']}", ""]
                if b.get("flex"):
                    out += [f"**If ahead or behind.** {b['flex']}", ""]
    placed = {id(b) for b in mapped if b is not None}
    missing = [b for b in mod.BLOCKS if id(b) not in placed and b["type"] != "Break"]
    if missing:
        out += ["## Blocks not placed in a section (give a part their start time)", ""] + [f"- {b['time']} {b['title']}" for b in missing] + [""]
    if getattr(mod, "LEAVE_WITH", None):
        out += ["## Before learners leave", ""] + [f"- [ ] {i}" for i in mod.LEAVE_WITH] + [""]
    if getattr(mod, "RUN_SHEET_EXTRA", None):
        out += [textwrap.dedent(mod.RUN_SHEET_EXTRA).strip(), ""]
    return "\\n".join(out)

'''
s = s[:start] + new_rs + s[end:]
old_build = '''    folder = COURSEWARE / mod.SLUG
    nb = dc.write(mod.cells(), folder / f"day{mod.DAY}_anchor.ipynb")
    (folder / "run-sheet.md").write_text(run_sheet_md(mod))'''
new_build = '''    folder = COURSEWARE / mod.SLUG
    dc.reset()
    cells = mod.cells()
    nb = dc.write(cells, folder / f"day{mod.DAY}_anchor.ipynb")
    (folder / "run-sheet.md").write_text(run_sheet_md(mod, dc.REG))'''
assert s.count(old_build) == 1; s = s.replace(old_build, new_build)
old_print = '''    print(f"day {mod.DAY}: {nb.name} ({len(mod.cells())} cells), run-sheet.md, {len(mod.ACTIVITIES)} activity cards -> {folder}")'''
new_print = '''    print(f"day {mod.DAY}: {nb.name} ({sum(c is not None for c in cells)} cells), run-sheet.md, {len(mod.ACTIVITIES)} activity cards -> {folder}")'''
assert s.count(old_print) == 1; s = s.replace(old_print, new_print)
ast.parse(s); p.write_text(s); print("patched build_all.py")

# ---------------- part times ----------------
TIMES = {
"day1.py": [('dc.part("Welcome", "the week, and the people in the room")', "09:00"), ('dc.part("Activity 1", "introductions and pain points")', "09:15"),
            ('dc.part("Guest", "the DXP operating model: the sponsor, or the fallback below")', "09:30"), ('dc.part("Shareback", "products and pain points")', "09:45"),
            ('dc.part("Whiteboard", "what is a data product?")', "10:05"), ('dc.part("Whiteboard", "how do you design a data product?")', "10:30"),
            ('dc.part("Activity 2", "justify a product")', "10:40"), ('dc.part("Debrief")', "11:00"), ('dc.part("Whiteboard", "lifetime value and adoption")', "11:25"),
            ('dc.part("Demo", "Catalyst: a skill is a prompt")', "11:40"), ('dc.part("Activity 3", "compare independent PRDs")', "11:50"),
            ('dc.part("Whiteboard", "the seven ideas, in order")', "13:00"), ('dc.part("Demo", "Voice Memos to transcript")', "13:55"),
            ('dc.part("Debrief", "requirements discovery")', "14:25"), ('dc.part("Activity 5", "explore the lifecycle")', "14:45")],
"day2.py": [('dc.part("Welcome", "yesterday\'s contract is today\'s input")', "09:00"), ('dc.part("Activity 6", "extend the contract")', "09:20"),
            ('dc.part("Shareback", "review and present a contract")', "10:00"),
            ('dc.part("Demo", "warehouse, lake and lakehouse; Databricks under the hood; Delta; Spark; the tools together")', "10:15"),
            ('dc.part("Demo", "containers, the challenge\'s five steps, the dev container\'s Dockerfile")', "11:00"), ('dc.part("Challenge 7", "Docker practical")', "11:25"),
            ('dc.part("Demo", "where output lands, and one minute of live generation")', "13:00"), ('dc.part("Activity 8", "generate and investigate")', "13:15"),
            ('dc.part("Debrief", "in this order")', "14:15"), ('dc.part("Activity 8b", "review another pair\'s generated code")', "14:30"),
            ('dc.part("Close", "corrections and closing discussion")', "14:50")],
"day3.py": [('dc.part("Launch", "the pipeline you will build today")', "09:00"), ('dc.part("Walkthrough", "Phase 2 on DuckDB: intermediate, marts, tests, docs")', "10:15"),
            ('dc.part("Guest", "the platform team, or the instructor-led version")', "11:00"),
            ('dc.part("Challenge 9 continued", "Phase 2, then the stretch: macros, snapshots, incremental, unit tests")', "13:00"),
            ('dc.part("Debrief", "what did we learn?")', "14:30"), ('dc.part("Activity 9", "test review in pairs")', "14:45"), ('dc.part("Close", "closing discussion")', "14:55")],
"day4.py": [('dc.part("Demo", "two clocks, three loads, four questions")', "09:00"), ('dc.part("Orientation", "the DAG, and Friday\'s preview")', "09:45"),
            ('dc.part("Demo", "the stack, a run, the UI, a controlled failure")', "10:15"), ('dc.part("Challenge 10", "Airflow practical")', "10:45"),
            ('dc.part("Shareback", "one run, one log line, one output check per pair")', "13:00"), ('dc.part("Demo", "GitOps, Harness, Datadog")', "13:30"),
            ('dc.part("Activity 10", "release decision")', "14:15"), ('dc.part("Activity 11", "explain a failure and repair")', "14:35"),
            ('dc.part("Friday preparation", "the checklist, then the close")', "14:50")],
"day5.py": [('dc.part("Brief", "the day, the rules, ten minutes of reading")', "09:00"), ('dc.part("Activity 12", "discovery worksheet, then playback")', "09:15"),
            ('dc.part("Challenge", "Atlas Phase 1")', "10:15"), ('dc.part("Challenge", "choose extensions by value to the consumer; technical work stops at 14:30")', "13:00"),
            ('dc.part("Activity 13", "capstone presentation")', "14:30")],
}
for fname, pairs in TIMES.items():
    patch(HERE / fname, [(call + ",", call[:-1] + f', time="{t}"),') for call, t in pairs])
