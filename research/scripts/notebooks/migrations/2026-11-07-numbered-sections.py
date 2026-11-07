"""One-off (7 Nov 2026): numbered sections with labelled parts and break markers; agenda replaces the TOC and the time table."""
import ast, pathlib, re
HERE = pathlib.Path(__file__).resolve().parent.parent

def L(*lines): return list(lines)

SECTIONS = {
"day1.py": '''SECTIONS = [
 dict(n=1, title="Welcome, the room and the operating model", anchor="s1", start="09:00",
      parts=["Welcome", "Activity 1: introductions and pain points", "Guest: the DXP operating model", "Shareback: products and pain points", "Whiteboard: what is a data product?", "Break"]),
 dict(n=2, title="Discovery, justification and Catalyst", anchor="s2", start="10:30",
      parts=["Whiteboard: how do you design a data product?", "Activity 2: justify a product", "Debrief", "Whiteboard: lifetime value and adoption", "Demo: Catalyst", "Activity 3: compare independent PRDs", "Lunch"]),
 dict(n=3, title="AI foundations and effective practice", anchor="s3", start="13:00",
      parts=["Whiteboard: the seven ideas", "Demo: the interface on the running example", "Break"]),
 dict(n=4, title="Interview, generate and the lifecycle", anchor="s4", start="13:55",
      parts=["Demo: Voice Memos to transcript", "Activity 4: interview and generate", "Debrief: requirements discovery", "Reflect: the planted-errors contract", "Activity 5: explore the lifecycle", "Before learners leave"]),
]

''',
"day2.py": '''SECTIONS = [
 dict(n=1, title="Mappings and service commitments", anchor="s1", start="09:00",
      parts=["Demo: STTM and service levels", "Activity 6: extend the contract", "Break", "Shareback: review and present a contract"]),
 dict(n=2, title="Platform architecture", anchor="s2", start="10:15",
      parts=["Demo: warehouse, lake, lakehouse", "Demo: Databricks under the hood, Delta, Spark", "Demo: how the tools fit together", "Shareback", "Break"]),
 dict(n=3, title="Docker", anchor="s3", start="11:00",
      parts=["Demo: the five steps and the dev container's Dockerfile", "Challenge 7: Docker practical", "Lunch"]),
 dict(n=4, title="Contract to code", anchor="s4", start="13:00",
      parts=["Demo: where output lands, live generation", "Activity 8: generate and investigate", "Break", "Debrief", "Activity 8b: review another pair's code", "Close"]),
]

''',
"day3.py": '''SECTIONS = [
 dict(n=1, title="The dbt practical: launch, Phase 1 and the walkthrough", anchor="s1", start="09:00",
      parts=["Launch: the pipeline", "Challenge 9: dbt practical", "Walkthrough: Phase 1 on DuckDB", "Break", "Walkthrough: Phase 2 on DuckDB", "Circulating"]),
 dict(n=2, title="The platform session", anchor="s2", start="11:00",
      parts=["Guest: the platform team (or the instructor-led version)", "Lunch"]),
 dict(n=3, title="Complete and extend the practical", anchor="s3", start="13:00",
      parts=["Challenge 9 continued: Phase 2", "Stretch: macros, snapshots, incremental, unit tests", "Break"]),
 dict(n=4, title="Consolidation", anchor="s4", start="14:30",
      parts=["Debrief: what did we learn?", "Activity 9: test review in pairs", "Close"]),
]

''',
"day4.py": '''SECTIONS = [
 dict(n=1, title="Bitemporal loading", anchor="s1", start="09:00",
      parts=["Demo: two clocks, three loads, four questions", "Guest or volunteer: a real table", "Shareback: which clock?"]),
 dict(n=2, title="Airflow orchestration", anchor="s2", start="09:45",
      parts=["Orientation: the DAG, and Friday", "Break", "Demo: the stack, a run, the UI, a controlled failure", "Challenge 10: Airflow practical", "Lunch", "Shareback: one run, one log, one output check"]),
 dict(n=3, title="CI/CD and release operations", anchor="s3", start="13:30",
      parts=["Demo: GitOps, Harness, Datadog", "Break", "Activity 10: release decision", "Activity 11: explain a failure and repair", "Friday preparation"]),
]

''',
"day5.py": '''SECTIONS = [
 dict(n=1, title="The brief and discovery", anchor="s1", start="09:00",
      parts=["Brief: the day, the rules, ten minutes of reading", "Activity 12: discovery worksheet", "Playback: two minutes per table"]),
 dict(n=2, title="Phase 1: the baseline", anchor="s2", start="10:15",
      parts=["Challenge: Atlas Phase 1", "Circulating: section notes, expected results, blockers", "Lunch (flexible)"]),
 dict(n=3, title="Phase 2: extensions and presentation prep", anchor="s3", start="13:00",
      parts=["Challenge: the fourteen extensions", "Presentation prep: technical work stops at 14:30"]),
 dict(n=4, title="Presentations and close", anchor="s4", start="14:30",
      parts=["Activity 13: presentations", "Tally sheet and certification evidence", "Close"]),
]

''',
}

EDITS = {
"day1.py": [
 ("line", r'dc\.heading\("Welcome", "welcome"\),', L('dc.section(1, "Welcome, the room and the operating model", "s1"),', 'dc.part("Welcome", "the week, and the people in the room"),')),
 ("move", 'dc.heading("The DXP operating model", "dxp"),', 'dc.heading("What is a data product?", "data-product"),', 'dc.md("### The room\'s products and pain points'),
 ("before", 'act("1"),', L('dc.part("Activity 1", "introductions and pain points"),')),
 ("line", r'dc\.heading\("The DXP operating model", "dxp"\),', L('dc.part("Guest", "the DXP operating model: the sponsor, or the fallback below"),')),
 ("rep", 'dc.md("### The room\'s products and pain points\\n\\n', 'dc.part("Shareback", "products and pain points"),\n          dc.md("'),
 ("line", r'dc\.heading\("What is a data product\?", "data-product"\),', L('dc.part("Whiteboard", "what is a data product?"),')),
 ("line", r'dc\.heading\("Discovery and justification", "discovery"\),', L('dc.break_(15, "10:30"),', 'dc.section(2, "Discovery, justification and Catalyst", "s2"),', 'dc.part("Whiteboard", "how do you design a data product?"),')),
 ("before", 'act("2"),', L('dc.part("Activity 2", "justify a product"),')),
 ("before", 'dc.whiteboard("Activity 2 debrief"', L('dc.part("Debrief"),')),
 ("before", 'dc.anchor("How do you estimate the lifetime value', L('dc.part("Whiteboard", "lifetime value and adoption"),')),
 ("line", r'dc\.heading\("Catalyst", "catalyst"\),', L('dc.part("Demo", "Catalyst: a skill is a prompt"),')),
 ("before", 'act("3"),', L('dc.part("Activity 3", "compare independent PRDs"),')),
 ("line", r'dc\.heading\("AI foundations and effective practice", "ai"\),', L('dc.break_(60, "13:00", lunch=True),', 'dc.section(3, "AI foundations and effective practice", "s3"),', 'dc.part("Whiteboard", "the seven ideas, in order"),')),
 ("before", 'dc.demo("the interface on the running example"', L('dc.part("Demo", "the interface on the running example"),')),
 ("line", r'dc\.heading\("Interview and generate", "interview"\),', L('dc.break_(15, "13:55"),', 'dc.section(4, "Interview, generate and the lifecycle", "s4"),')),
 ("before", 'dc.demo("Voice Memos to transcript"', L('dc.part("Demo", "Voice Memos to transcript"),')),
 ("before", 'act("4"),', L('dc.part("Activity 4", "interview and generate"),')),
 ("before", 'dc.figure("d1-discovery-methods"', L('dc.part("Debrief", "requirements discovery"),')),
 ("line", r'dc\.heading\("Explore the lifecycle", "lifecycle"\),', L('dc.part("Activity 5", "explore the lifecycle"),')),
],
"day2.py": [
 ("line", r'dc\.heading\("Welcome", "welcome"\),', L('dc.section(1, "Mappings and service commitments", "s1"),', 'dc.part("Welcome", "yesterday\'s contract is today\'s input"),')),
 ("line", r'dc\.heading\("Mappings and service commitments", "[^"]+"\),', L('dc.part("Demo", "STTM and service levels"),')),
 ("before", 'act("6"),', L('dc.part("Activity 6", "extend the contract"),')),
 ("line", r'dc\.heading\("Review and present a contract", "review"\),', L('dc.break_(15, "10:00"),', 'dc.part("Shareback", "review and present a contract"),')),
 ("line", r'dc\.heading\("Platform architecture", "platform"\),', L('dc.section(2, "Platform architecture", "s2"),', 'dc.part("Demo", "warehouse, lake and lakehouse; Databricks under the hood; Delta; Spark; the tools together"),')),
 ("before", 'dc.reflect("SHAREBACK — one minute per table"', L('dc.part("Shareback", "one minute per table"),')),
 ("line", r'dc\.heading\("Docker", "docker"\),', L('dc.break_(15, "11:00"),', 'dc.section(3, "Docker", "s3"),', 'dc.part("Demo", "containers, the challenge\'s five steps, the dev container\'s Dockerfile"),')),
 ("before", 'act("7"),', L('dc.part("Challenge 7", "Docker practical"),')),
 ("line", r'dc\.heading\("Contract to code", "contract-to-code"\),', L('dc.break_(60, "13:00", lunch=True),', 'dc.section(4, "Contract to code", "s4"),', 'dc.part("Demo", "where output lands, and one minute of live generation"),')),
 ("before", 'act("8"),', L('dc.part("Activity 8", "generate and investigate"),')),
 ("before", 'dc.whiteboard("debrief, in this order"', L('dc.break_(10, "14:15"),', 'dc.part("Debrief", "in this order"),')),
 ("before", 'act("8b"),', L('dc.part("Activity 8b", "review another pair\'s generated code"),')),
 ("before", 'dc.say(["Make one correction now', L('dc.part("Close", "corrections and closing discussion"),')),
],
"day3.py": [
 ("line", r'dc\.heading\("Welcome and launch", "[^"]+"\),', L('dc.section(1, "The dbt practical: launch, Phase 1 and the walkthrough", "s1"),', 'dc.part("Launch", "the pipeline you will build today"),')),
 ("before", 'dc.challenge("dbt practical (challenge 02)"', L('dc.part("Challenge 9", "dbt practical: Phase 1 first"),')),
 ("line", r'dc\.heading\("Walkthrough: Phase 1, sources and staging", "[^"]+"\),', L('dc.part("Walkthrough", "Phase 1 on DuckDB: sources and staging"),')),
 ("line", r'dc\.heading\("Walkthrough: Phase 2, intermediate, marts, tests, docs", "[^"]+"\),', L('dc.break_(15, "10:15"),', 'dc.part("Walkthrough", "Phase 2 on DuckDB: intermediate, marts, tests, docs"),')),
 ("line", r'dc\.heading\("Circulating", "[^"]+"\),', L('dc.part("Circulating", "three questions per learner, and the symptom table"),')),
 ("line", r'dc\.heading\("The platform session", "[^"]+"\),', L('dc.section(2, "The platform session", "s2"),', 'dc.part("Guest", "the platform team, or the instructor-led version"),')),
 ("line", r'dc\.heading\("Stretch: macros, snapshots, incremental, unit tests", "[^"]+"\),', L('dc.break_(60, "13:00", lunch=True),', 'dc.section(3, "Complete and extend the practical", "s3"),', 'dc.part("Challenge 9 continued", "Phase 2, then the stretch: macros, snapshots, incremental, unit tests"),')),
 ("line", r'dc\.heading\("Consolidation", "[^"]+"\),', L('dc.break_(15, "14:30"),', 'dc.section(4, "Consolidation", "s4"),', 'dc.part("Debrief", "what did we learn?"),')),
 ("before", 'act("9"),', L('dc.part("Activity 9", "test review in pairs"),')),
 ("before", 'dc.say(["Two or three examples to the room', L('dc.part("Close", "closing discussion"),')),
],
"day4.py": [
 ("line", r'dc\.heading\("Welcome", "welcome"\),', L('dc.section(1, "Bitemporal loading", "s1"),')),
 ("line", r'dc\.heading\("Bitemporal loading", "bitemporal"\),', L('dc.part("Demo", "two clocks, three loads, four questions"),')),
 ("before", 'dc.reflect("GUEST OR VOLUNTEER BRIEF', L('dc.part("Guest or volunteer", "a real bitemporal table"),')),
 ("before", 'dc.reflect("SHAREBACK — which clock?"', L('dc.part("Shareback", "which clock?"),')),
 ("line", r'dc\.heading\("Orchestration and Friday", "orchestration"\),', L('dc.section(2, "Airflow orchestration", "s2"),', 'dc.part("Orientation", "the DAG, and Friday\'s preview"),')),
 ("line", r'dc\.heading\("Airflow", "airflow"\),', L('dc.break_(15, "10:15"),', 'dc.part("Demo", "the stack, a run, the UI, a controlled failure"),')),
 ("line", r'dc\.heading\("Challenge 10", "challenge"\),', L('dc.part("Challenge 10", "Airflow practical"),')),
 ("line", r'dc\.heading\("CI/CD and deployment", "cicd"\),', L('dc.break_(60, "13:00", lunch=True),', 'dc.part("Shareback", "one run, one log line, one output check per pair"),',
     'dc.md(dc.reflect("SHAREBACK — 13:30, one pair at a time", "Show the run ID, the log line that told you what happened, and the table it produced.", ["Keep credential and path errors separate from the intended data-quality failure.", "Fast finishers: what happens if the input is late? If the quality check fails? If the run is repeated?"])),',
     'dc.section(3, "CI/CD and release operations", "s3"),', 'dc.part("Demo", "GitOps, Harness, Datadog"),')),
 ("line", r'dc\.heading\("Release decision and the failure note", "exercises"\),', L('dc.break_(15, "14:15"),', 'dc.part("Activity 10", "release decision"),')),
 ("before", 'act("11"),', L('dc.part("Activity 11", "explain a failure and repair"),')),
 ("line", r'dc\.heading\("Friday preparation", "friday"\),', L('dc.part("Friday preparation", "the checklist, then the close"),')),
],
"day5.py": [
 ("line", r'dc\.heading\("The brief", "brief"\),', L('dc.section(1, "The brief and discovery", "s1"),', 'dc.part("Brief", "the day, the rules, ten minutes of reading"),')),
 ("line", r'dc\.heading\("Discovery", "discovery"\),', L('dc.part("Activity 12", "discovery worksheet, then playback"),')),
 ("line", r'dc\.heading\("Phase 1 support", "phase1"\),', L('dc.section(2, "Phase 1: the baseline", "s2"),', 'dc.part("Challenge", "Atlas Phase 1"),')),
 ("before", '| Section | What to check when circulating', L('dc.part("Circulating", "section notes, expected results, blockers"),')),
 ("line", r'dc\.heading\("Phase 2 menu", "phase2"\),', L('dc.break_(60, "13:30 at the latest", lunch=True),', 'dc.section(3, "Phase 2: extensions and presentation prep", "s3"),', 'dc.part("Challenge", "choose extensions by value to the consumer; technical work stops at 14:30"),')),
 ("line", r'dc\.heading\("Presentations and certification", "presentations"\),', L('dc.section(4, "Presentations and close", "s4"),', 'dc.part("Activity 13", "capstone presentation"),')),
 ("before", '### Tally sheet (fill in during the day)', L('dc.part("Tally sheet and certification evidence"),')),
 ("rep", '### Tally sheet (fill in during the day)', '**Tally sheet** (fill in during the day)'),
 ("before", 'dc.say(["One person per table', L('dc.part("Close"),')),
],
}

def indent_of(src, pos):
    ls = src.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", src[ls:]).group(0), ls

def line_start_of_cell(src, marker):
    """Start offset of the cell entry (a line beginning with `dc.` / `act(` / `*dc.`) that contains or precedes the marker."""
    pos = src.index(marker)
    ls = src.rfind("\n", 0, pos) + 1
    while not re.match(r"[ \t]*(dc\.|act\(|\*dc\.)", src[ls:ls + 40]):
        ls = src.rfind("\n", 0, ls - 1) + 1
        assert ls > 0, marker
    return ls

def apply(fname):
    p = HERE / fname; src = p.read_text(); tree = ast.parse(src)
    # agenda replaces the Today cell; the toc cell and the agenda assignment go
    today = toc = assign = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr == "toc": toc = n
            if n.func.attr == "md" and n.args and isinstance(n.args[0], ast.JoinedStr) and n.args[0].values and isinstance(n.args[0].values[0], ast.Constant) and str(n.args[0].values[0].value).startswith("### Today"):
                today = n
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "agenda" for t in n.targets): assign = n
    assert today and toc and assign, (fname, today, toc, assign)
    lead = str(today.args[0].values[-1].value).strip().replace("\n", " ")
    today_seg = ast.get_source_segment(src, today); toc_seg = ast.get_source_segment(src, toc); assign_seg = ast.get_source_segment(src, assign)
    src = src.replace(today_seg, f"dc.agenda(SECTIONS, lead={lead!r})", 1)
    assert src.count(toc_seg + ",") == 1; src = src.replace(toc_seg + ",", "", 1)
    assert src.count(assign_seg) == 1; src = src.replace(assign_seg, "", 1)
    # SECTIONS before cells()
    assert src.count("\ndef cells():") == 1; src = src.replace("\ndef cells():", "\n" + SECTIONS[fname] + "def cells():", 1)
    # the edits
    for kind, *args in EDITS[fname]:
        if kind == "line":
            pat, new = args
            m = list(re.finditer(r"^([ \t]*)" + pat + r"[ \t]*$", src, re.M)); assert len(m) == 1, (fname, pat, len(m))
            ind = m[0].group(1); src = src[:m[0].start()] + "\n".join(ind + l for l in new) + src[m[0].end():]
        elif kind == "before":
            marker, new = args
            assert src.count(marker) == 1, (fname, marker, src.count(marker))
            ls = line_start_of_cell(src, marker); ind, _ = indent_of(src, ls)
            src = src[:ls] + "".join(ind + l + "\n" for l in new) + src[ls:]
        elif kind == "rep":
            old, new = args
            assert src.count(old) == 1, (fname, old); src = src.replace(old, new, 1)
        elif kind == "move":
            a_marker, b_marker, dest_marker = args
            a = line_start_of_cell(src, a_marker); b = line_start_of_cell(src, b_marker); assert a < b
            block = src[a:b]; src = src[:a] + src[b:]
            d = line_start_of_cell(src, dest_marker); src = src[:d] + block + src[d:]
    ast.parse(src); p.write_text(src); print(f"{fname}: sections and parts in place")

for f in ["day1.py", "day2.py", "day3.py", "day4.py", "day5.py"]:
    apply(f)
