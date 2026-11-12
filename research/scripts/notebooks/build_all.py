#!/usr/bin/env python3
"""Build every day's anchor notebook, run sheet (Markdown and Word), and activity cards from the day modules.
Usage: ~/.venvs/cg-dxp/bin/python build_all.py [--no-docx] [--week] [--pdf] [day ...]   (--week also builds the week documents to Word; --pdf prints every instructor document to PDF from its Markdown)

The Word run sheet is built by research/scripts/docx/build_lesson_plan.js (CG Core's lesson-plan builder) from a second
Markdown written in that builder's dialect under research/build/run-sheets/; courseware/<day>/run-sheet.md keeps its own format."""
from __future__ import annotations
import importlib, os, pathlib, re, shutil, subprocess, sys, textwrap
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import dc
ROOT = pathlib.Path(__file__).resolve().parents[3]
COURSEWARE = ROOT / "courseware"          # learner-shareable
INSTRUCTOR = ROOT / "instructor"          # instructor-only: run sheets, prep guides, the week docs
BUILD = ROOT / "research" / "build" / "run-sheets"
DOCX_BUILDER = ROOT / "research" / "scripts" / "docx" / "build_lesson_plan.js"

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

# ---------- the Word run sheet, in the CG Core lesson-plan dialect ----------
# One H4 row per timed part (and per break), typed with one of the builder's seven activity types; a part without a time
# of its own is folded into the previous row as a bold sub-heading. Fields use the builder's labels (Purpose, On screen,
# Instructor notes, Say, Transition, Adapt); the whiteboard script, demo steps, fallbacks and activity pointers follow as
# plain paragraphs, tables and lists, which the builder renders inside the row.
TYPE_BY_LABEL = [("Welcome", "Intro/Outro"), ("Friday preparation", "Intro/Outro"), ("Demo", "Instructor-led demo"),
                 ("Walkthrough", "Instructor-led demo"), ("Activity", "Independent or pairs work"), ("Challenge", "Independent or pairs work"),
                 ("Circulating", "Independent or pairs work"), ("Shareback", "Feedback and discussion"), ("Debrief", "Feedback and discussion"),
                 ("Close", "Feedback and discussion"), ("Tally", "Feedback and discussion"), ("Whiteboard", "Questioning"),
                 ("Guest", "Explain"), ("Orientation", "Explain"), ("Launch", "Explain"), ("Brief", "Explain")]

def row_type(label: str, block: dict | None) -> str:
    for prefix, t in TYPE_BY_LABEL:
        if label.startswith(prefix):
            return t
    bt = (block or {}).get("type", "")
    if "Break" in bt: return "Break"
    if "Demo" in bt: return "Instructor-led demo"
    if any(k in bt for k in ("Challenge", "Practical", "activity", "Individual")): return "Independent or pairs work"
    if any(k in bt for k in ("Shareback", "Debrief")): return "Feedback and discussion"
    if bt.startswith("Intro"): return "Intro/Outro"
    return "Explain"

_TAGS = [(r"<code>(.*?)</code>", r"`\1`"), (r"</?(?:em|i)>", "*"), (r"</?(?:strong|b)>", "**"), (r"<br\s*/?>", " "),
         (r"</?details>|</?summary>", ""), (r"<a [^>]*>(.*?)</a>", r"\1")]

def mdtext(s, cell: bool = False) -> str:
    """HTML written for the notebook boxes becomes Markdown the Word builder accepts: no raw HTML, placeholders as ‹…›."""
    s = str(s)
    for pat, rep in _TAGS:
        s = re.sub(pat, rep, s, flags=re.S)
    parts = s.split("`")
    for k in range(0, len(parts), 2):                      # outside code spans only
        parts[k] = re.sub(r"<([^<>`]+)>", "‹\\1›", parts[k])
    s = "`".join(parts)
    if cell:
        s = s.replace("|", "\\|").replace("\n", " ")
    return s

def _hm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"

def _end(b: dict) -> int:
    return _mins(b["time"].split("–")[1])

def _rows(mod, reg) -> list[dict]:
    by_start = {_start(b): b for b in mod.BLOCKS}
    break_blocks = [b for b in mod.BLOCKS if "Break" in b["type"]]
    rows, k = [], 0
    for sec in reg["sections"]:
        for p in sec["parts"]:
            if p["kind"] == "break":
                bb = break_blocks[k] if k < len(break_blocks) else None; k += 1
                if bb:
                    start, minutes = _start(bb), _end(bb) - _start(bb)
                else:
                    m = re.match(r"(\d+:\d\d)", p["back_at"])
                    start, minutes = ((_mins(m.group(1)) - p["minutes"]) if m else None), p["minutes"]
                rows.append({"kind": "break", "sec": sec, "start": start, "minutes": minutes, "back_at": p["back_at"], "lunch": p["lunch"], "block": bb})
            elif p.get("time") or not rows or rows[-1]["kind"] != "row" or rows[-1]["sec"] is not sec:
                rows.append({"kind": "row", "sec": sec, "start": _mins(p["time"]) if p.get("time") else None,
                             "label": p["label"], "title": p["title"], "items": list(p["items"]), "sub": []})
            else:
                rows[-1]["sub"].append(p)
    prev = None
    for r in rows:
        if r["start"] is None:
            r["start"] = prev if prev is not None else _start(mod.BLOCKS[0])
        prev = r["start"]
    day_end = _end(mod.BLOCKS[-1])
    for i, r in enumerate(rows):
        if r["kind"] == "row":
            nxt = next((x["start"] for x in rows[i + 1:] if x["start"] > r["start"]), day_end)
            r["minutes"] = max(nxt - r["start"], 5)
    current = None
    for r in rows:
        if r["kind"] == "row":
            current = by_start.get(r["start"], current); r["block"] = current
    return rows

def _items_md(items) -> list[str]:
    out = []
    for kind, pl in items:
        if kind == "say":
            out += ["**Say.**", ""] + [f"- “{mdtext(x)}”" for x in pl] + [""]
        elif kind == "whiteboard":
            out += [f"**Ask at the whiteboard — {mdtext(pl['title'])}.** Ask in order, write what the room says, add what is missing.", "",
                    "| Ask | Expect, then add |", "|---|---|"] + [f"| {mdtext(q, cell=True)} | {mdtext(a, cell=True)} |" for q, a in pl["items"]] + [""]
        elif kind == "demo":
            out += [f"**Demo — {mdtext(pl['title'])}.** {mdtext(pl['line'])}", ""] + [f"{k}. {mdtext(x)}" for k, x in enumerate(pl["steps"], 1)] + [""]
        elif kind == "fallback":
            out += [f"**If it breaks.** {mdtext(pl['line'])}", ""] + ([f"- {mdtext(x)}" for x in pl["bullets"]] + [""] if pl["bullets"] else [])
        elif kind == "activity":
            out += [f"**Activity {pl['number']} — {mdtext(pl['title'])}.** {pl['grouping']}, {pl['minutes']} min; the card is in `activities/`.", ""]
        elif kind == "challenge":
            out += [f"**Challenge — {mdtext(pl['title'])}.** `{pl['path']}` · {mdtext(pl['minutes'])}.", ""]
    return out

def _label(label: str, title: str) -> str:
    t = f"{label} — {mdtext(title)}" if title else label
    return t if t[-1:] in "?.!" else t + "."

def run_sheet_docx_md(mod, reg) -> str:
    secs = getattr(mod, "SECTIONS", []); by_n = {x["n"]: x for x in secs}
    out = [f"# Day {mod.DAY} run sheet — {mod.TITLE}", "", f"[Data Creators › Day {mod.DAY} — run sheet for instructors]{{.breadcrumb}}", "",
           "Instructor-only companion to the anchor notebook, in the notebook's order: the same numbered sections and labelled parts, each with its time, purpose, what is on screen, what to say, what to ask at the whiteboard (with the answers rooms give and what to add), the demo steps with their coaching, fallbacks, the transition and what to do if ahead or behind. Keep the notebook on the projector and this beside it. Times follow the instructor plan; adapt them to the room and keep the sequence.", ""]
    if reg.get("prep"):
        out += ["## Before the day", "", mdtext(reg["prep"]), ""]
    if secs:
        out += ["## Sections", "", "| # | Section | Time | What happens |", "|---|---|---|---|"]
        for i, sec in enumerate(secs):
            end = secs[i + 1]["start"] if i + 1 < len(secs) else _hm(_end(mod.BLOCKS[-1]))
            out.append(f"| {sec['n']} | {mdtext(sec['title'], cell=True)} | {sec['start']}–{end} | {mdtext(' · '.join(sec['parts']), cell=True)} |")
        out.append("")
    out += ["## Day at a glance", "", "| § | Time | Block | Type | On screen |", "|---|---|---|---|---|"]
    for b in mod.BLOCKS:
        out.append(f"| {section_of(mod, b)} | {b['time']} | {mdtext(b['title'], cell=True)} | {b['type']} | {mdtext(b['on_screen'], cell=True)} |")
    out += ["", "## Timeline", ""]
    rows = _rows(mod, reg)
    first, last = {}, {}
    for r in rows:
        if r["kind"] == "row" and r.get("block"):
            first.setdefault(id(r["block"]), r); last[id(r["block"])] = r
    cur = None
    for r in rows:
        if r["sec"] is not cur:
            cur = r["sec"]
            out += [f"### {cur['n']}. {mdtext(cur['title'])}" if cur["n"] else f"### {mdtext(cur['title'])}", ""]
            if cur["n"] in by_n:
                out += [mdtext(" · ".join(by_n[cur["n"]]["parts"])), ""]
        if r["kind"] == "break":
            out += [f"#### {_hm(r['start'])} · {r['minutes']} min · Break — {'Lunch' if r['lunch'] else 'Break'}, back at {mdtext(r['back_at'])}", ""]
            if r["block"] and r["block"].get("notes"):
                out += ["**Instructor notes.**", ""] + [f"- {mdtext(n)}" for n in r["block"]["notes"]] + [""]
            continue
        b = r["block"]
        out += [f"#### {_hm(r['start'])} · {r['minutes']} min · {row_type(r['label'], b)} — {r['label']}" + (f" — {mdtext(r['title'])}" if r["title"] else ""), ""]
        if b and first[id(b)] is r:
            out += [f"**Purpose.** {mdtext(b['purpose'])}", ""]
            if b.get("notes"):
                out += ["**Instructor notes.**", ""] + [f"- {mdtext(n)}" for n in b["notes"]] + [""]
            if b.get("say"):
                out += ["**Say.**", ""] + [f"- “{mdtext(x)}”" for x in b["say"]] + [""]
        out += _items_md(r["items"])
        for sub in r["sub"]:
            out += [f"**{_label(sub['label'], sub['title'])}**", ""] + _items_md(sub["items"])
        if b and last[id(b)] is r:
            if b.get("transition"):
                out += [f"**Transition.** {mdtext(b['transition'])}", ""]
            if b.get("flex"):
                out += [f"**Adapt.** {mdtext(b['flex'])}", ""]
        # the right-hand column (headed "On screen"); last, because the builder attaches every unlabelled block that
        # follows a field to that field, and the tables and lists above belong in the notes column
        if b:
            out += [f"**Assessment.** {mdtext(b['on_screen']) or '—'}", ""]
    if getattr(mod, "LEAVE_WITH", None):
        out += ["## Before learners leave", ""] + [f"- [ ] {mdtext(i)}" for i in mod.LEAVE_WITH] + [""]
    return "\n".join(out)

def build_docx(md_path: pathlib.Path, out_path: pathlib.Path, kind: str = "run sheet", portrait: bool = False) -> bool:
    node = shutil.which("node") or "/opt/homebrew/bin/node"
    env = dict(os.environ, DOC_PROGRAMME="Data Creators", DOC_KIND=kind, DOC_ASSESS_HEADER="On screen",
               DOC_ORIENTATION="portrait" if portrait else "landscape")
    env.setdefault("PANDOC", shutil.which("pandoc") or "/opt/anaconda3/bin/pandoc")
    r = subprocess.run([node, str(DOCX_BUILDER), str(md_path), str(out_path)], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        print(f"  Word build failed for {md_path.name}: {r.stderr.strip()[-800:]}")
        return False
    return True

def build(day_name: str):
    mod = importlib.import_module(day_name)
    folder = COURSEWARE / mod.SLUG
    dc.reset()
    cells = mod.cells()
    nb = dc.write(cells, folder / f"day{mod.DAY}_anchor.ipynb")
    inst = INSTRUCTOR / mod.SLUG                      # instructor-only: run sheets and the prep guide
    inst.mkdir(parents=True, exist_ok=True)
    (inst / "run-sheet.md").write_text(run_sheet_md(mod, dc.REG))
    for name, make in getattr(mod, "BACKUP_NOTEBOOKS", {}).items():   # instructor-only notebooks, beside the run sheet
        dc.write(make(), inst / name)
    docx_note = ""
    if DOCX:
        BUILD.mkdir(parents=True, exist_ok=True)
        src = BUILD / f"day{mod.DAY}_run-sheet.md"
        src.write_text(run_sheet_docx_md(mod, dc.REG))
        docx_note = ", run-sheet.docx" if build_docx(src, inst / "run-sheet.docx") else ", run-sheet.docx FAILED"
        guide = inst / f"day{mod.DAY}_prep-guide.md"
        if guide.exists():
            docx_note += ", prep-guide.docx" if build_docx(guide, inst / f"day{mod.DAY}_prep-guide.docx", kind="instructor prep guide", portrait=True) else ", prep-guide.docx FAILED"
    (folder / "activities").mkdir(exist_ok=True)
    for a in mod.ACTIVITIES:
        slug = re.sub(r"[^a-z0-9]+", "-", a["title"].lower()).strip("-")
        (folder / "activities" / f"{a['number']}-{slug}.md").write_text(activity_md(a, mod.DAY))
    print(f"day {mod.DAY}: {nb.name} ({sum(c is not None for c in cells)} cells), {len(mod.ACTIVITIES)} activity cards -> {folder.relative_to(ROOT)}; run-sheet.md{docx_note} -> {inst.relative_to(ROOT)}")

# ---------- the week documents (Markdown only) to Word, and every instructor document to PDF ----------
WEEK_DOCS = [("instructor/README.md", "instructor pack"), ("instructor/00-week/start-here.md", "start here"),
             ("instructor/00-week/preflight-checklist.md", "pre-flight checklist"), ("instructor/00-week/llm-guide.md", "LLM guide"),
             ("instructor/00-week/risks-and-fallbacks.md", "risks and fallbacks")]

def build_week_docs() -> list[str]:
    """Each week document becomes a .docx beside it: the Markdown is copied under research/build/ with a breadcrumb
    line after its title (the builder wants one), then built portrait."""
    out = []
    BUILD.parent.joinpath("instructor-docs").mkdir(parents=True, exist_ok=True)
    for rel, kind in WEEK_DOCS:
        src = ROOT / rel
        if not src.exists():
            continue
        text = src.read_text()
        title_line, rest = text.split("\n", 1)
        crumb = f"[Data Creators › instructor pack — {kind}]{{.breadcrumb}}"
        tmp = BUILD.parent / "instructor-docs" / src.name
        tmp.write_text(f"{title_line}\n\n{crumb}\n{rest}")
        ok = build_docx(tmp, src.with_suffix(".docx"), kind=kind, portrait=True)
        out.append(f"{rel} -> .docx" + ("" if ok else " FAILED"))
    return out

MD_TO_PDF = ROOT / "research" / "scripts" / "docx" / "md_to_pdf.py"

def export_pdfs() -> list[str]:
    """Every instructor document (run sheets, prep guides, the week documents, the README) becomes a .pdf beside its
    Markdown, printed by Chrome from pandoc's HTML with the house print stylesheet (research/scripts/docx/md_to_pdf.py).
    Word will not open files under automation on this Mac and Pages drops the fonts and the page breaks, so the
    Markdown, not the .docx, is the PDF's source."""
    jobs = []
    for mod_name in ["day1", "day2", "day3", "day4", "day5"]:
        mod = importlib.import_module(mod_name)
        folder = INSTRUCTOR / mod.SLUG
        jobs.append((folder / "run-sheet.md", ["--landscape", "--crumb", f"Data Creators › Day {mod.DAY} — run sheet"]))
        jobs.append((folder / f"day{mod.DAY}_prep-guide.md", []))
    for rel, kind in WEEK_DOCS:
        jobs.append((ROOT / rel, ["--crumb", f"Data Creators › instructor pack — {kind}"]))
    out = []
    for src, extra in jobs:
        if not src.exists():
            continue
        pdf = src.with_suffix(".pdf")
        r = subprocess.run([sys.executable, str(MD_TO_PDF), str(src), str(pdf), *extra], capture_output=True, text=True, timeout=300)
        out.append(f"{src.relative_to(ROOT)} -> .pdf" + ("" if r.returncode == 0 and pdf.exists() else f" FAILED: {r.stderr.strip()[-300:]}"))
    return out

DOCX = True
if __name__ == "__main__":
    args = sys.argv[1:]
    if "--no-docx" in args:
        DOCX = False; args.remove("--no-docx")
    pdf = "--pdf" in args
    if pdf:
        args.remove("--pdf")
    week = "--week" in args
    if week:
        args.remove("--week")
    days = args or ["day1", "day2", "day3", "day4", "day5"]
    for d in days:
        build(d)
    if DOCX and (week or not args):
        for line in build_week_docs():
            print("week docs:", line)
    if pdf:
        for line in export_pdfs():
            print("pdf:", line)
