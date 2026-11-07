#!/usr/bin/env python3
"""Build every day's anchor notebook, run sheet and activity cards from the day modules.
Usage: ~/.venvs/cg-dxp/bin/python build_all.py [day ...]"""
from __future__ import annotations
import importlib, pathlib, re, sys, textwrap
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import dc
ROOT = pathlib.Path(__file__).resolve().parents[3]
COURSEWARE = ROOT / "courseware"

def activity_md(a: dict, day: int) -> str:
    lines = [f"# Activity {a['number']} — {a['title']}", "",
             f"*Day {day} · {a['grouping']} · {a['minutes']} minutes*", "", a["brief"], "", "**Produce**", ""]
    lines += [f"- {o}" for o in a["outputs"]]
    if a.get("early"):
        lines += ["", f"**Finished early?** {a['early']}"]
    if a.get("debrief"):
        lines += ["", "**Debrief questions**", ""] + [f"- {d}" for d in a["debrief"]]
    if a.get("extra"):
        lines += ["", textwrap.dedent(a["extra"]).strip()]
    return "\n".join(lines) + "\n"

def _mins(t: str) -> int:
    h, m = t.strip().split(":"); return int(h) * 60 + int(m)

def section_of(mod, block) -> str:
    """The notebook section a run-sheet block belongs to: the last section whose start is not after the block's start."""
    n = ""
    for sec in getattr(mod, "SECTIONS", []):
        if _mins(sec["start"]) <= _mins(block["time"].split("–")[0]):
            n = str(sec["n"])
    return n

def _start(b: dict) -> int:
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
    return "\n".join(out)

def build(day_name: str):
    mod = importlib.import_module(day_name)
    folder = COURSEWARE / mod.SLUG
    dc.reset()
    cells = mod.cells()
    nb = dc.write(cells, folder / f"day{mod.DAY}_anchor.ipynb")
    (folder / "run-sheet.md").write_text(run_sheet_md(mod, dc.REG))
    (folder / "activities").mkdir(exist_ok=True)
    for a in mod.ACTIVITIES:
        slug = re.sub(r"[^a-z0-9]+", "-", a["title"].lower()).strip("-")
        (folder / "activities" / f"{a['number']}-{slug}.md").write_text(activity_md(a, mod.DAY))
    print(f"day {mod.DAY}: {nb.name} ({sum(c is not None for c in cells)} cells), run-sheet.md, {len(mod.ACTIVITIES)} activity cards -> {folder}")

if __name__ == "__main__":
    days = sys.argv[1:] or ["day1", "day2", "day3", "day4", "day5"]
    for d in days:
        build(d)
