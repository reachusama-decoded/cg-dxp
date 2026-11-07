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

def run_sheet_md(mod) -> str:
    out = [f"# Day {mod.DAY} run sheet — {mod.TITLE}", "",
           "Instructor-only timing companion to the anchor notebook. Times follow the instructor plan; adapt them to the room and keep the sequence. Each row: purpose, what is on screen, notes, a line to say, the transition, and what to do if ahead or behind.", "",
           "| Time | Block | Type | On screen |", "|---|---|---|---|"]
    for b in mod.BLOCKS:
        out.append(f"| {b['time']} | {b['title']} | {b['type']} | {b['on_screen']} |")
    out += ["", "## Blocks", ""]
    for b in mod.BLOCKS:
        out += [f"### {b['time']} · {b['title']} ({b['type']})", "", f"**Purpose.** {b['purpose']}", "", f"**On screen.** {b['on_screen']}", ""]
        if b.get("notes"):
            out += ["**Instructor notes.**", ""] + [f"- {n}" for n in b["notes"]] + [""]
        if b.get("say"):
            out += ["**Say.**", ""] + [f"- “{s}”" for s in b["say"]] + [""]
        if b.get("transition"):
            out += [f"**Transition.** {b['transition']}", ""]
        if b.get("flex"):
            out += [f"**If ahead or behind.** {b['flex']}", ""]
    if getattr(mod, "LEAVE_WITH", None):
        out += ["## Before learners leave", ""] + [f"- [ ] {i}" for i in mod.LEAVE_WITH] + [""]
    if getattr(mod, "RUN_SHEET_EXTRA", None):
        out += [textwrap.dedent(mod.RUN_SHEET_EXTRA).strip(), ""]
    return "\n".join(out)

def build(day_name: str):
    mod = importlib.import_module(day_name)
    folder = COURSEWARE / mod.SLUG
    nb = dc.write(mod.cells(), folder / f"day{mod.DAY}_anchor.ipynb")
    (folder / "run-sheet.md").write_text(run_sheet_md(mod))
    (folder / "activities").mkdir(exist_ok=True)
    for a in mod.ACTIVITIES:
        slug = re.sub(r"[^a-z0-9]+", "-", a["title"].lower()).strip("-")
        (folder / "activities" / f"{a['number']}-{slug}.md").write_text(activity_md(a, mod.DAY))
    print(f"day {mod.DAY}: {nb.name} ({len(mod.cells())} cells), run-sheet.md, {len(mod.ACTIVITIES)} activity cards -> {folder}")

if __name__ == "__main__":
    days = sys.argv[1:] or ["day1", "day2", "day3", "day4", "day5"]
    for d in days:
        build(d)
