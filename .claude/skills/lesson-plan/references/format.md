# The CG Core lesson plan: format

The lesson plan is the instructor's document for one session, `courseware/<unit>/dayNN-<slug>/instructor/module00-overview/dayNN_lesson_plan.md`. It adapts Decoded's lesson plan template (`reference/Lesson Plan Template [MAKE A COPY].md`) to CG Core (user, 2026-10-16). The Markdown is the source; the build turns it into `release/latest/<unit>/dayNN-<slug>/instructor/module00-overview/dayNN_lesson_plan.docx`, a Word document in the Decoded house style. Edit the Markdown, never the Word file. Placeholders in the blank plan are written ‹like this› (never `<like this>`, which pandoc reads as HTML); a finished plan has none.

The plan teaches from the back of the room (user, 2026-10-16): instructors explain less, learners spend the time in the challenges, and the rows stay short. An instructor should be able to read any row in a glance.

Contents: [Sections](#sections-in-order) · [Title block](#title-block) · [Overview](#overview) · [Objectives and outcomes](#objectives-and-outcomes) · [Curriculum map](#curriculum-map) · [Before the session](#before-the-session) · [Timeline](#timeline) · [Demo rows](#demo-rows) · [The shape of a session](#the-shape-of-a-session) · [Module reference](#module-reference) · [Question bank](#question-bank) · [Support and stretch](#support-and-stretch) · [FAQs](#faqs) · [Activity types](#activity-types) · [Times](#times) · [Voice](#voice) · [The Word document](#the-word-document)

## Sections, in order

| H2 section | From Decoded's template | What it holds |
|---|---|---|
| (title block) | The title lines | The content title, the breadcrumb, one line on timings |
| `## Overview` | Overview | Where the session sits, the Jordan thread, the themes, what learners leave with, who it's for |
| `## Objectives and outcomes` | Learning objectives and outcomes, without the KSB column | One row per outcome: objective, outcome, module, evidence; then which module answers which session question |
| `## Curriculum map` | Curriculum | Every session of the programme with its modules, this one marked |
| `## Before the session` | (added for CG Core) | Materials, your checklist, the learner setup check |
| `## Timeline` | Lesson plan (the big table) | Section rows and activity rows: in Word, one table of Timing, Activity and notes, Assessment |
| `## Module N reference`, `## Put it together reference` | (added for CG Core) | Short: what a finished challenge looks like, the likeliest stalls, fallbacks, the facts to have at hand |
| `## Question bank` | Menti question bank | Per module: its key questions, then check-for-understanding questions with answers |
| `## Support and stretch` | Support, stretch and challenge | Per module: what to do for a newcomer and for someone who already knows it |
| `## FAQs` | Workshop FAQs | Questions learners ask, with answers |
| `## Activity types` | Activity types | The key to the activity labels, copied as given below |

Left out on purpose (user, 2026-10-16), because CG Core is a corporate programme, not an apprenticeship: Key links, KSBs and the KSB review, Functional skills and the FS column, the contents list, the safeguarding script, Canvas, the Learner Success Coach and Help Centre, portfolio evidence, pre- and post-assessments, the workshop recording, and Menti by name. Don't add them back. The template's housekeeping, feedback form and next-session preview stay, briefly, in the welcome and the wrap-up.

## Title block

```markdown
# Notebooks to scripts, the command line and Python environments

[Unit 1 · Software engineering with AI › Day 01 — lesson plan for instructors]{.breadcrumb}

Timings are a guide: adapt them to the room. Confirm the start and end times, the breaks and the timezone before you deliver.
```

The H1 is the day's canonical title, the programme overview's word for word, as in the overview (user, 2026-10-27); the breadcrumb comes from `nbkit.breadcrumb(unit, unit_title, NN, "lesson plan for instructors")`.

## Overview

A few short paragraphs, in the instructor's voice, no in-line references:

1. Where the session sits: its unit, what it builds on (the previous session, or the setup for S01), and the shift it makes.
2. The thread: Jordan Mensah (they/them) at Harbourline Asset Management, what Jordan's artefact is at the start and what each module does to it.
3. "The session's themes:" then one bullet per module, and a last one, "**Open challenge time (optional).** Carry on with any module challenge, or try Put it together, ‹task title›, end to end: …", each in a line.
4. What learners leave with: the artefacts, and what makes them good (rerunnable, checked, reproducible).
5. Who it's for: the audience and what isn't assumed.

## Objectives and outcomes

```markdown
| # | Learning objective | By the end of the session, learners can… | Module | Evidence |
|---|---|---|---|---|
| 1 | The software lifecycle | **Explain** the lifecycle and where integrate, release and deploy sit | M1 | A stage for each thing they made in the challenge, and the stages with nothing yet |

Module 1 answers session questions 1 to 3, Module 2 question 4 and Module 3 question 5.
```

- **#** is the outcome's number, the one the Assessment field cites ("Outcome 1").
- **Learning objective**: the topic the session teaches for that outcome, as a short noun phrase.
- **By the end of the session, learners can…**: the outcome, copied word for word from `dayNN_overview.md`, bold verb included.
- **The outcomes are `internal-programme-overview.md` section 6's, word for word** (user, 2026-10-16): the session's outcomes table there is the source, and `dayNN_overview.md`'s bullets and this column carry each outcome in the same words, bold verb included. A change to an outcome is made in all of them in the same edit: `internal-programme-overview.md`, the overview, this table and any partial quote of it in the session's notebooks and Markdown (a Say line, a reflect answer). `module-audit`'s `scripts/audit.py` reports any that differ.
- **Module**: M1, M2, M3, or a pair ("M1, M2").
- **Evidence**: what the learner makes or says that shows the outcome, and where (a challenge tier, the demo, the debrief). Core clauses are evidenced at Q1 or Q2; a clause evidenced only in the demo or debrief says so ("refactoring: demo and debrief only").
- The sentence under the table maps the overview's session questions to modules. The lesson plan is the only place that mapping lives.

## Curriculum map

```markdown
| Unit | Session | Modules |
|---|---|---|
| 1 · Software engineering with AI | **S01 · Notebooks to scripts, the command line and Python environments (this session)** | M1 Software engineering, your first programs and Copilot · M2 Command line, Linux and remote workflows · M3 Python packages, dependencies and reusable modules |
|  | S02 · <title> | M1 … · M2 … · M3 … |
```

One row per session of the whole programme, in order, with the unit named on its first session's row. Titles come from `internal-programme-overview.md`; this session's row is bold and ends "(this session)". No weeks or dates until the timetable is confirmed.

## Before the session

```markdown
### Materials

Your files are in the session's `instructor/` folder and the learners' in its `learner/` folder, one folder per module on each side (user, 2026-10-27), and each path starts there (`module01-first-programs-copilot/` with the demo notebook, its files and `challenge-solution/`; `module01-first-programs-copilot/` with the challenge notebook, its files and the handbook); the dev container is at the top of the course folder, the data and services in `common/`.

| File | For | Use it for |
|---|---|---|
| `module00-overview/day01_overview.pdf`, each module folder's handbook (learner side) | Learners | The welcome: outcomes, self-check, agenda. The module handbooks hold the concepts in depth |
| `moduleNN-<slug>/day01_mN_demo.ipynb` | You (instructors only) | One demo notebook per module, each opening on its module map and ending with a Challenge time box and a Go deeper box |

### Your checklist

#### Before the day

- [ ] Copy the course folder to your laptop and work in that copy, never inside the shared folder
- [ ] Before you rehearse, keep a second copy aside, untouched: your clean copy
- [ ] Confirm the timetable: start and end times, breaks, timezone
- [ ] Build the remote's image once, in `common/services/remote-machine/`:
  - `bash service.sh start`

#### On the day

- [ ] …

#### After rehearsing

- [ ] Put the room back. From `module01-first-programs-copilot/`, delete:
  - `fund_report.py`, `report.txt` and the folder `report/`

### Learner setup check

Learners set up at the start of the day: as they arrive, they open the course folder in its dev container and start the session's services, and both build while you welcome them. You check it at the end of the welcome.
```

Paths in Materials start in the session's `instructor/` folder (your files) or its `learner/` folder (the learners'), and the table opens with the line saying so; the dev container is at the top of the course folder, the data and services in `common/`. The overview and handbooks share the first row, the handbooks described as the concepts in depth, never when to read them. The completed challenge has its row: File `challenge-solution/day01_challenge.ipynb`, For You, Use it for "The challenge done in full, to walk through in the debriefs. It sits in `instructor/` at the same depth as the learners' `challenge/` and runs as it is. Never hand it out". The session's `instructor/` folder has its row too: File `instructor/`, For You, Use it for "This lesson plan in Word, and review PDFs: the demo, the challenge with every solution open, and the completed challenge (`day01_challenge_solution.pdf`). Never hand them out" (user, 2026-10-19; 2026-10-27). Then a row for `.devcontainer/` and the session's `common/services/<name>/` (For Everyone: the dev container whose terminal everybody uses, and each service with its `README.md` of commands and fixes; your notes for it are `unit00-programme/instructor/services/<name>/INSTRUCTOR.md`) and one for `common/data/demo/`, `common/data/challenge/` (For Everyone).

Instructors still prepare before the day (the dry run, building each service once), so their machine is ready for the first demo; only learners set up on the day. The checklist holds what goes wrong if it's missed, grouped so each item reads at a glance (user, 2026-10-19): three `####` headings, **Before the day**, **On the day** and **After rehearsing**, each with short `- [ ]` items of one line, and any command or file list moved to an indented sub-bullet under its item. Before the day opens with copying the course folder to your laptop and working in that copy, never inside the shared folder, and keeping a clean copy aside (say "the shared folder", never the platform it's on); then the dry run and anything to start or download early (the images the session pulls). On the day holds the slow-network check, opening the completed challenge and the pre-runs: what to run in which break, so that a slow demo step is done before its row; After rehearsing, the room reset (what to delete or undo after a rehearsal or a previous run, so the live beats start clean). Keep every fact and command; reword to keep each item short.

## Timeline

The template's lesson plan table. In the Markdown it is headings; in Word it becomes one table with three columns, **Timing**, **Activity and notes** and **Assessment**, where each H3 is a full-width section row and each H4 an activity row.

### Section rows

One H3 per block, in order:

- `### Welcome {#dayNN-welcome}`
- `### Module N — <module title> {#dayNN-mN}` for each module, the title the programme overview's, word for word (`programme-profile/references/conventions.md` → "Titles")
- `### Open challenge time {#dayNN-open}`
- `### Wrap-up {#dayNN-wrapup}`

```markdown
### Module 1 — Software engineering, your first programs and Copilot {#day01-m1}

**Module outcomes.**

- Outcome 1 · **Explain** the stages of the software development lifecycle and where integration, release and deployment sit — …

::: {.anchor key="m1" title="WHAT, WHY AND HOW"}
…
:::

**Section summary.** Serves outcomes 1, 2 and 3 and answers session questions 1 to 3. Learners turn Jordan's notebook into a script with Copilot, review it and record one check.
```

Each module's section opens, straight under its heading, with the module's 🧭 anchor, then the section summary. Outcomes appear once, in the intro's *What you will be able to do* row: no **Module outcomes.** under a module heading, and no module objectives slide (user, 2026-10-27; the audit fails on one). The anchor is the `::: {.anchor}` div that `scripts/nbkit.py anchors --session <folder>` writes from `dayNN_anchors.md`. Never type or edit it: change `dayNN_anchors.md` and rerun the command. The Word build draws it as the same box.

- **Section summary** (required): one or two sentences: the outcomes it serves, the session questions it answers, what learners make.
- No key questions here or in the rows: a module's key questions live in its part of the [Question bank](#question-bank).

### Activity rows

One H4 per row, under its section:

```markdown
#### 0:25 · 2.5 min · Instructor-led demo — See the finished weekly report

**Purpose.** Learners see the report the module ends with, before any code.

**On screen.** `module01-first-programs-copilot/day01_m1_demo.ipynb`: the module map · See the finished weekly report

**Instructor notes.**

- **The module map.** Open Module 1 from the table of contents: seven stops, each leaving something; the last is a script and a check.
- **See the finished weekly report.** Run the `!` cell: the chart runs from UK Gilts at 3.05 to Emerging Markets Equity at 55.59, from zero.

**Say.**

- **The module map.** "One report all day: each stop leaves something you could show."
- **See the finished weekly report.** "Read the output before any code."

**Transition.** "Where does a notebook stop? The loop round your code."

**Assessment.** —
```

The heading is `#### H:MM · N min · <Activity type> — <Title>`:

- `H:MM` is the row's start, counted from 0:00 at the start of the session, written `H:MM:SS` when it falls on a half minute (`0:12:30`).
- `N` is a step of 2.5 from 2.5 to 20 (`2.5`, `5`, `7.5` … `20`): a row may run up to 20 minutes (user, 2026-10-27).
- The activity type is exactly one of the seven in [Activity types](#activity-types).
- The title is a few words in sentence case: about six words or fewer, saying what happens, in plain words, with no metaphor or teaser and no question mark (user, 2026-10-27). In an Instructor-led demo row it is the one demo `### ` heading the row covers, word for word (see [Demo rows](#demo-rows)). In a module's first challenge row it is the challenge's own section title, word for word: `Module 4 challenge — Test and fix the returns code`.

The fields are bold labels ending in a full stop, always in this order. Leave out an optional field rather than write "none".

| Field | Needed | What it holds |
|---|---|---|
| **Purpose.** | Every row but a break | One line: what the row achieves for learners |
| **On screen.** | Where something is showing | One line: the file first, by its path from the session folder, then the section (user, 2026-10-19): `` `moduleNN-<slug>/dayNN_mN_challenge.ipynb`: Q1 ``, `` `module00-overview/dayNN_overview.md`: the agenda ``; in a demo row, `` `moduleNN-<slug>/dayNN_mN_demo.ipynb`: <heading> `` (the first row: `the anchor, the map, then <heading>`; the last: `<heading>, to its closing lines`), and in a module's first challenge row, `` `moduleNN-<slug>/dayNN_mN_demo.ipynb`: the Challenge time box; then `moduleNN-<slug>/dayNN_mN_challenge.ipynb`, <challenge section title> `` (see [Demo rows](#demo-rows)); in a debrief, the completed challenge, `` `challenge-solution/dayNN_mN_challenge.ipynb`, Module N: <task boxes> `` |
| **From the overview.** | The two intro rows only | Straight after On screen (user, 2026-10-27): the overview's text, word for word. In *Jordan and the day*, the persona card's grid table; in *What you will be able to do*, the lead line "By the end of this session you will be able to:" and the outcome bullets. Copy it from the overview, never the other way: overview → lesson plan → slides |
| **Instructor notes.** | Every row but a Questioning row | Up to three short bullets, imperative |
| **Ask.** | Questioning rows | One or two questions, as bullets, a line each, put to the room as written |
| **Listen for.** | Questioning rows | One line: what a good answer contains |
| **If stuck.** | Questioning rows | One line: the prompt or simpler question that gets the room there |
| **Say.** | Optional | Up to two brief lines, each said in one breath, as quotes (three in Key takeaways, one per module) |
| **Transition.** | Every row but the last | One line: the move into the next row |
| **Assessment.** | Every row | Two short parts, `Outcome N · <evidence>`, or `—` |
| **Adapt.** | Only where it really matters | One line: what to change for a quicker or a newer room |

Key questions don't go in rows: they belong to the module's part of the Question bank. A Questioning row's **Ask.** is the exception: the one or two questions the instructor puts to the room there and then. A line is about 35 words at most, a Say line about 25 (one breath); `module-audit` warns past those, past two Say lines and past three notes. A demo row's bold heading label at the start of a note or Say line (see [Demo rows](#demo-rows)) doesn't count toward its words.

The Assessment field fills the template's "Assessment method & type" column, which is narrow in Word (user, 2026-10-19), so it is two short parts: the outcome by number ("Outcome 3", "Outcomes 2, 3", "Outcomes 1 to 5"), then the evidence, in a few words, commas between items: "Outcomes 2, 3 · remote exit codes, the `REPORT_DATA` change". No third part saying how the instructor sees it; if that matters, it goes in the notes. About 15 words at most. A row that serves no outcome, a demo row included, gets `—`: the evidence comes from what learners make. `module-audit` warns on any other number of parts and past 15 words.

The timeline always covers the whole session, and every module's rows and `## Module N reference` are written together, from the approved handbooks (user, 2026-10-26); nothing is invented to fill a gap.

A prompt quoted in full is a `::: {.copilot title="…" where="Chat view" mode="…" model="…" attach="…"}` div around a ```` ```text ```` block, or for a shell command `::: {.copilot title="…" where="Terminal chat" model="Fast"}` with no mode. `where` is Chat view (questions, plans, jobs that change files; mode required), Inline chat (one change to the selected code; no mode) or Terminal chat (a shell command; no mode); `attach` is `#<file>`, `selection`, `#codebase`, `#terminalLastCommand` or `#terminalSelection`. The closing lines per surface and mode are in `programme-profile/references/conventions.md` → "The Copilot box"; the Word lesson plan draws the same badges. Usually a row points to the box instead: "the COPILOT box 'Turn the notebook into a script' in the demo".

### Demo rows

One row per heading (user, 2026-10-27): every `### ` heading in a module's demo notebook is exactly one `Instructor-led demo` row, with the same title, in the same order, so an instructor always knows which section of the notebook they're on, and nothing is skipped or grouped. A module's demo still totals about 20 minutes, so rows run in 2.5-minute steps (2.5, 5, 7.5 …).

- **A beat** is one `### ` section of the module's demo with everything under it: its visual, its cells, any `#### ` sub-visual, its Copilot boxes and its open-and-come-back steps. The module map frames the module (the `## Module N` heading cell, its 🧭 anchor cell, the bridge cell and the map cell): it lives in the first row, whose first Say asks the anchor's question.
- **No closing heading.** The module's closing lines ("Where the report goes next" in S02) are the last lines of the final beat, bold-led text with no heading, just before the 🏆 CHALLENGE TIME box; the last demo row's note ends on them and its Transition leads into the challenge.
- **The title is the heading**, word for word: `#### 0:22:30 · 2.5 min · Instructor-led demo — Your first pytest test`. **On screen** names the module's demo notebook, then the heading: `` `moduleNN-<slug>/dayNN_mN_demo.ipynb`: <heading> ``; the first row's reads `the anchor, the map, then <heading>`, the last row's `<heading>, to its closing lines`.
- **The module section title** in the lesson plan is the demo's `## Module N — …` heading, word for word.
- **Every row has a note and a Say of its own**, each opening with the heading's exact name in bold (`- **Your first pytest test.** …`); the first row's module-map lines are labelled `**The module map.**`. Each says what to run or show, what to expect on screen (the visual, the number a cell prints) and what to say over it, within the lean limits (three notes, two Say lines). A step too slow for its row (a push, a pipeline run, a first image build) is pre-run in the break before the module: the Break row's notes say what to run, and the demo row's note says it ran in the break and what to show from it.
- **The first challenge row** is titled with the challenge's own section title (`Module 4 challenge — Test and fix the returns code`), names its tasks by their exact titles (`Q1 · CORE *Pin it, then fix it*; Q2 · STRETCH …; Q3 · BONUS …`) and says where learners work. Its On screen names the demo's Challenge time box, then the challenge section.
- The notebook carries the bullets. A note says what to do and what to expect, and never retells the beat.

`module-audit` reads each module's `### ` headings from that module's demo notebook (across the day's module folders) and checks the demo rows against them: one row per heading, the same title word for word, in order, none missing or extra, each with a labelled note and Say; the module section title equal to the demo's `## Module` heading; the first challenge row titled with the challenge's section title.

### Questioning rows

Every module has two `Questioning` rows of 2.5 minutes (user, 2026-10-27), so the instructor checks understanding while it's fresh:

- **After the demo**, straight after its last beat (`Questioning — Check the demo`): a question or two on what the demo showed, before learners start. Its minutes come from the demo: shorten one 5-minute beat to 2.5, and add an Adapt to that beat if it's tight.
- **Within the challenge**, between its two rows (`Questioning — Mid-challenge check-in`): hands up for a moment, a question or two on the learners' own work, then back to it. Its minutes come from the second challenge row (10 becomes 7.5).

A Questioning row's fields are **Purpose.**, **On screen.**, **Ask.** (one or two questions, as bullets), **Listen for.** (what a good answer contains), **If stuck.** (the prompt or simpler question that gets the room there), **Transition.** and **Assessment.**; no notes or Say. Write questions that make learners think about the module's idea, not recall a word: "A test Copilot drafted passes. What do you do before you trust it?", not "What is a unit test?".

```markdown
#### 0:27:30 · 2.5 min · Questioning — Check the demo

**Purpose.** Learners say how they'd decide a test drafted by Copilot is worth keeping.

**On screen.** `module04-unit-testing-pytest/day02_m4_demo.ipynb`: Break the code to test the tests

**Ask.**

- "A test Copilot drafted passes. What do you do before you trust it?"

**Listen for.** Break the code on purpose and see it go red; check the expected values are written out, not worked out again.

**If stuck.** "What has a test that has never failed proved?"

**Transition.** "Nine tests that bite. Your turn, on the challenge data."

**Assessment.** Outcomes 1, 2 · a way to make a test show it can fail
```

`module-audit` checks, on template sessions, a Questioning row after each module's demo and one within its challenge, each with Ask (one or two questions), Listen for and If stuck; the four intro rows, 5, 15, 2.5 and 2.5 minutes, the second Welcome or Welcome back, and no Setup check or Meet and greet row (`check_lp_intro`; user, 2026-11-02); a Shareback/questions row in every module, Feedback and discussion, exactly 15 minutes, after the last challenge row and straight before the Debrief, and no Catch-up and questions row, an error that names the shareback (`check_lp_shareback`; user, 2026-11-02); the day ending with Closing debrief and questions, Key takeaways and Thank you for participating (`check_lp_ending`); the modules starting at 0:25, 1:40 and 2:55 and open challenge time at 4:10 for 30 minutes (`check_lp_starts`, warnings; user, 2026-11-02); and the **From the overview.** quotes matching the overview word for word, with no **Module outcomes.** in a module section (`check_lp_quotes`). The demo-row check skips Questioning rows.

## The shape of a session

A session is a five-hour day, 0:00 to 5:00 (`SESSION_MINUTES`, 300; user, 2026-11-02, replacing the four-hour day). The start and the end take 45 minutes on the template (the 25-minute intro and the 20-minute wrap-up, the closing debrief in it; `LP_TEMPLATE_START_END`; user, 2026-11-02); every module, with all its activities, is 75 minutes, at 0:25, 1:40 and 2:55 (`LP_MODULE_STARTS`; user, 2026-11-02); open challenge time is 30 minutes at 4:10.

| Block | Rows |
|---|---|
| Welcome, 25, every day (user, 2026-11-02) | Four rows: `Intro/Outro — Arrive and settle`, 5 (learners open the course folder in its dev container and start the services while they settle; the instructor walks the room; the deck's standard Arrive and settle slide); `Intro/Outro — Welcome`, 15, on a unit's first day (Day 01, 03, 05, 07: the welcome day's own plan, `unit00-programme/day00-welcome/`, runs inside this row from its own deck, beside the day's, and the day's deck has one drafted Welcome slide, `dayNN-welcome`; user, 2026-11-02: kept separate) or `Intro/Outro — Welcome back`, 15, on its second day (Day 02, 04, 06, 08: yesterday's list and today's thread, one drafted slide); `Explain — Jordan and the day`, 2.5 (**From the overview.** the persona card); `Explain — What you will be able to do`, 2.5 (**From the overview.** the outcomes; notes carry the self-check pacing). No Setup check row (setup is pre-work in the overview, user 2026-10-27) and no Meet and greet row (introductions live in the welcome) |
| Each module, 75 minutes (user, 2026-11-02) | **Demo, about 20**: one `Instructor-led demo` row per demo `### ` heading, in 2.5-minute steps, a note and a Say for every row ([Demo rows](#demo-rows)). **Challenge, 20 to 25**: two `Independent or pairs work` rows, the first a brief of a line or two and then learners work, the second learners still working with the instructor available; paired work runs in parallel, swapping only for the review. **Two `Questioning` rows, 2.5 each** ([Questioning rows](#questioning-rows)): one straight after the demo's last beat, its minutes taken from the demo by shortening one 5-minute beat; one between the challenge's two rows, its minutes taken from the second. **Shareback/questions, 15** (user, 2026-11-02, replacing the same day's 10-minute Catch-up and questions): one `Feedback and discussion` row titled `Shareback/questions`, exactly 15 minutes, after the challenge's rows and straight before the debrief: learners share what they found and where they stuck, and ask anything; the instructor takes the questions. **Debrief, 5**: one `Feedback and discussion` row that walks through the solution in `challenge-solution/` or asks two or three questions that surface blockers. **Break, 5 to 10**: one `Break` row whose notes list the next module's pre-runs and whose Transition is the bridge into the next block |
| Open challenge time (optional), 30 at 4:10 | `Independent or pairs work` rows only, 20 + 10: learners carry on with any module challenge, as far as they can, or take Put it together, the optional stretch for fast finishers. No closing debrief here: it opens the Wrap-up (user, 2026-11-02) |
| Wrap-up, 20 | Three rows, always the day's last (user, 2026-11-02): `Feedback and discussion — Closing debrief and questions`, 10 (blockers, anything shipped, and the questions the day has left); `Feedback and discussion — Key takeaways`, 5, its first note a very brief look back ("Look back first, briefly: read the outcome verbs, a hand for each."), three Say lines, one takeaway per module; then `Intro/Outro — Thank you for participating`, 5, the thanks, the feedback form and the next session's preview, Assessment `—` |

A module may run a little faster or slower with its complexity (a 15-minute demo and a 25-minute challenge, say), keeping the pattern: demo, Questioning, challenge in two rows with a Questioning row between them, shareback/questions, debrief, break, about 75 minutes in all (user, 2026-11-02). The demo's 🏆 CHALLENGE TIME box gives the challenge's minutes.

S02's timeline, the example (S01's has the same shape, with `Welcome` in place of `Welcome back`; the five-hour day, user 2026-11-02, retimed the same day):

| Start | Block | Rows |
|---|---|---|
| 0:00 | Welcome | Arrive and settle 5 · Welcome back 15 · Jordan and the day 2.5 · What you will be able to do 2.5 |
| 0:25 | Module 4 | demo 2.5 + 2.5 + 2.5 + 5 + 5 (five headings) · Questioning 2.5 · challenge 15 · Questioning 2.5 · 7.5 · Shareback/questions 15 · debrief 5 · break 10 |
| 1:40 | Module 5 | demo 2.5 + 2.5 + 2.5 + 2.5 + 2.5 + 5 (six headings) · Questioning 2.5 · challenge 15 · Questioning 2.5 · 7.5 · Shareback/questions 15 · debrief 5 · break 10 |
| 2:55 | Module 6 | demo 2.5 + 5 + 2.5 + 2.5 + 5 (five headings) · Questioning 2.5 · challenge 15 · Questioning 2.5 · 7.5 · Shareback/questions 15 · debrief 5 · break 10 |
| 4:10 | Open challenge time | 20 + 10, with Put it together the optional stretch |
| 4:40 | Wrap-up | Closing debrief and questions 10 · Key takeaways 5 · Thank you for participating 5, to 5:00 |

**Challenges go as far as you can.** No tier is mandatory and nobody is chased: learners start at Q1 and stop where the time stops. The instructor teaches from the back of the room and stays available; the rows carry no timed check-ins, "walk the room at" times or five-minute warnings, beyond the one 2.5-minute Questioning row mid-challenge.

**Put it together is never a block everyone does** (user, 2026-10-16). It is the optional stretch for fast finishers, inside the last block of open challenge time. Name it there, once, as optional.

**A debrief shows a finished version or surfaces blockers.** Its **On screen.** may name the completed challenge by its notebook, which instructors show in VS Code, at the task being discussed: "`` `challenge-solution/day01_challenge.ipynb`, Module 1: Q1's fixed cell ``". Its PDF, `instructor/dayNN_mN_challenge_solution.pdf` (from the session's folder), is the fallback the checklist names. Instructors show it; learners don't get it.

## Module reference

After the timeline, one H2 per module, `## Module N reference {#dayNN-mN-reference}`, then `## Put it together reference {#dayNN-together-reference}` when the session has one. Each is short, and holds only what an instructor looks up mid-session; the demo and challenge notebooks carry the rest. In this order:

- `### What a finished challenge looks like`: one line per tier, with the real numbers.
- `### The likeliest stalls`: the three likeliest, as a table `| Stall | Hint |`, each hint one line.
- `### Fallbacks`: two or three, as a table `| Problem | Do this |`.
- `### Facts to have ready`: only the facts an instructor needs at hand, exactly as the demo or challenge prints them.

No points for each visual and no demo walk-through in the reference: the demo rows carry a note and a Say for each beat.

## Question bank

```markdown
### Module 1

**Key questions.**

1. What is software engineering, and what are the stages of the software development lifecycle?

| Ask after | Question | Answers (correct in bold) |
|---|---|---|
| 0:20 · One error on purpose · What makes a script reusable | Which line of a traceback do you read first? | The first line · **The last line** · The longest line |
```

One H3 per module. **Key questions** are the module's questions from the brief, numbered: the instructor's compass, never read out as a list. Then two or three check-for-understanding questions, each checking one idea the module teaches. "Ask after" names a timeline row by its start and title. Multiple-choice answers are separated by ` · ` with the correct one in bold; an open question gives the answer you're listening for in bold. They work in any poll tool, with hands up, or in a debrief.

## Support and stretch

```markdown
### Module 1

**Support.** For a learner or room missing a prerequisite: what to slow down, what to show again, who to pair them with.

**Stretch.** For a learner or room that already knows it: what to take quickly, and what to spend the saved time on.
```

One H3 per module, each two lines. "Challenge" means the learner activity in CG Core, which is why the template's "Support, stretch and challenge" is renamed.

## FAQs

```markdown
**Do I need to know Python already?**

No. Copilot writes the code in the challenge: your job is to read it and check it.
```

Questions learners actually ask, each in bold, with the answer in a sentence or two. An FAQ about a tool or a choice answers with pros and cons and what each is good for, never a tool's limitations (CG rule 2).

## Activity types

Copy this table as it is; the labels are the only ones the timeline uses. `scripts/audit.py` keeps its own copy (`LP_ACTIVITY_TYPES`, so the audit works on a clone without `.claude/`), and its `--self-test` fails when the two differ: change both together.

| Activity type | What it means here |
|---|---|
| Intro/Outro | Opening or closing the session: welcome, housekeeping, outcomes, agenda; the session questions, the feedback form, the next session |
| Explain | The instructor teaches an idea from a visual, briefly |
| Instructor-led demo | The instructor runs the demo live, code, terminal or Copilot, while learners watch or follow |
| Questioning | Questions to the room, by hands up or a poll: the self-check, a prediction |
| Independent or pairs work | Learners work through the challenge at their own pace, alone or in pairs, as far as they get; the instructor stays available |
| Feedback and discussion | A short debrief: walk through the solution, or ask questions that surface blockers |
| Break | A rest. The instructor checks setups and collects questions |

## Times

Row lengths run in 2.5-minute steps from 2.5 to 20 (user, 2026-10-27, replacing the 2026-10-16 multiples of five), so every demo heading gets its own row and a module's demo still totals about 20 minutes. Start times are `H:MM`, or `H:MM:SS` on a half minute (`0:12:30`); each row starts where the one before ends, and the last ends at the session's length, 5:00 (user, 2026-11-02). Blocks outside the demo (challenge, shareback, debrief, break, open challenge time, wrap-up) keep whole five-minute lengths; the intro's Jordan and the day and What you will be able to do run 2.5 each (user, 2026-11-02), as do the Questioning rows. Times are a guide; instructors adapt them.

## Voice

Decoded's voice: plain, warm and direct, in British English (`courseware-conventions/references/tone-of-voice-guidelines.txt` and `writing-rules.md`). Short sentences, no jargon for its own sake, no hedging, nothing an instructor would feel silly saying aloud. Say lines sound like a person in a room, not a script. Jordan Mensah is they/them. The person delivering is "the instructor".

## The Word document

`node scripts/docx/build_lesson_plan.js <dayNN_lesson_plan.md> <out.docx>` builds it (pandoc reads the Markdown; docx-js writes the document in the house style of the programme overview's Word version; `cd scripts/docx && npm install` once), and `scripts/build-session.sh dayNN --reviewed` puts it in `release/latest/<unit>/<session>/instructor/`. The lesson plan is built to Word only: there is no lesson-plan PDF. In Word:

- A4 landscape (user, 2026-10-19), the Decoded logo, the breadcrumb and the title on the first page; "CG Core · Session NN lesson plan" and "For instructors" in the header; "Page X of Y" and "© Decoded Limited · decoded.com" in the footer. Work Sans and Fira Code are embedded, so the document looks the same where they aren't installed.
- The timeline starts on a new page as one table with its header row repeated on every page: **Timing** (the start in bold, then "N min"), **Activity and notes** (a coloured activity label, the title in bold, then the fields), **Assessment** (narrow: 1,900 twips of the landscape page's 14,570, so its entries stay two short parts). Each section is a dark band across the table with its summary in a light row under it.
- Each activity type has its own label colour (Intro/Outro aqua, Explain blue, Instructor-led demo yellow, Questioning light yellow, Independent or pairs work green, Feedback and discussion light red, Break grey), and the Activity types table shows the same colours.
- Tables follow the house style, checklists print as ☐ with their wrapped lines hanging under the text and a little room above each item, sub-bullets indented under them, code in Fira Code, and `::: copilot` as the Copilot box with its colour-coded badges. (The builder can also draw `::: blocked` as a red-edged box; CG Core content never uses it.) The reference sections start on a new page after the timeline.
- To look at it without Word: `.venv/bin/python scripts/docx/preview_docx.py <docx> <dir>`.
