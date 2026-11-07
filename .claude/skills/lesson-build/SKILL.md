---
name: lesson-build
description: The mechanics of producing CG Core session material — the session folder's file shapes (learner/module00-overview/dayNN_overview.md for learners, instructor/module00-overview/dayNN_lesson_plan.md for instructors, one L6-style handbook per module under learner/moduleNN-<slug>/, the per-module demo and challenge notebooks (instructor/moduleNN-<slug>/dayNN_mN_demo.ipynb, learner/moduleNN-<slug>/dayNN_mN_challenge.ipynb) with the files beside them, the completed challenge in instructor/moduleNN-<slug>/challenge-solution/, figures in courseware/common/figures/<session>/), the Markdown dialect the bundled house builder (./build-pdf) renders (callouts such as session, expert, catalyst, workflow, extra), plain handbook headings and captions that the PDF numbers, figure generation, anchor-notebook furniture including the 🗺️ table of contents built by `scripts/nbkit.py toc` and AIA's box set built only through nbkit helpers (difficulty legend, ⚡ Q1/Q2/Q3 task boxes, 💭 reflect box and folded solution, ⌨️ terminal, 🎯 your turn, 🏆 challenge time, the one 📚 Go deeper box per module section, the 🤖 Copilot prompt box with its settings legend, and its ::: copilot twin for PDF Markdown) and the programme's way of working in challenges (learners prompt Copilot to write, fix or change code and review it, never writing code by hand), code formatting with scripts/format_code.py and ship state, and how to check material and, only after the user's review, build release/latest/ with scripts/build-session.sh (the lesson plan's own format is the lesson-plan skill's). Use whenever you create, edit, lint, convert or build any overview, lesson plan, handbook, figure, demo or challenge anchor or file beside it for CG Core, including "just fix this callout" requests.
---

# Lesson build

Every CG Core session is plain Markdown, one demo and one challenge notebook per module (or Markdown anchors) and the files beside them, in one folder of the same shape, split into `learner/` and `instructor/` and then into module folders (`module00-overview/`, `moduleNN-<slug>/`; user, 2026-10-27), with figures, data and services in `courseware/common/` (`programme-profile/references/layout.md`). Each learner Markdown file with an H1 builds its own PDF (`module00-overview/dayNN_overview.pdf`, each module folder's `dayNN_mN_handbook.pdf`) through the bundled house builder `./build-pdf` (run as `.venv/bin/python ./build-pdf`), configured by `builder.toml`; the lesson plan is built to Word only (`instructor/module00-overview/dayNN_lesson_plan.docx`, by `scripts/docx/build_lesson_plan.js`), with no lesson-plan PDF. Write for the build, check with Pandoc and `module-audit`, never hand-edit a PDF, and **build no PDF until the user has reviewed the content** (user, 2026-10-15). Full dialect: [references/markdown-conventions.md](references/markdown-conventions.md).

## Environment

- `./build-pdf` fetches its own pandoc (3.1.11) and tectonic into `~/.cache/build-pdf` on first use (`./build-pdf setup` pre-fetches them) and uses the MacTeX `xelatex` when present. Run the builder as `.venv/bin/python ./build-pdf …` (its `#!` line would otherwise take the system Python 3.9). `./build-pdf doctor` crashes with a `TypeError` while the PATH's pandoc is older than 2.17 (Anaconda's 2.12 here); builds are unaffected, and `scripts/README.md` → PDF toolchain gives the one-command workaround. Otherwise use `./build-pdf config` and a real session build as the check. `./build-pdf docs` prints the authoring guide, `./build-pdf docs config` the config reference.
- Mermaid is rendered at build time by `mmdc`, installed project-locally: `cd scripts/mermaid && npm install`. `scripts/build-session.sh` puts `scripts/mermaid/node_modules/.bin` on the PATH; the installed CLI must be 11.x.
- Python for figures, checks and notebooks: the project venv `.venv/bin/python` (Python 3.13, with nbformat, nbclient and an ipykernel `python3` kernel; created and filled as `scripts/README.md` says) or the dev container. **Never install, upgrade, sync or remove packages in `/opt/anaconda3` or any global Python, and never run `pip sync` outside `.venv`.** Conda's base environment is active in the default shell, and uv targets an active conda environment before a local `.venv`, so every `uv pip` command names `--python .venv/bin/python`. Figures render on CPU with the brand fonts registered from `scripts/fonts/` (Work Sans, Fira Code) through `scripts/figures/brand.py`.
- Notebook builder and verify scripts live in the scratchpad; figure scripts live in `scripts/figures/dayNN/` and ship with the repo. Once anyone edits a notebook directly, its builder script is out of date: update it, or mark it retired before anyone reruns it (S02's `s02c/`).

## The development flow

Each step is written from the one before it (user, 2026-10-15):

**handbook → lesson plan → overview → demo → challenges**

The handbook fixes the concepts, names, numbers and order; the lesson-plan block teaches from it; the overview's outcomes, agenda and questions come from the lesson plan; the demo section shows what the handbook explains; the challenge section applies the demo's skill to the challenge data. A change upstream is mirrored downstream in the same pass. The build order is handbooks first, approved by the user, then everything downstream together for every module (`module-builder` → Build order); the session is checked against `module-builder/references/session-checklist.md`.

**The way of working** in every challenge, Put it together (the optional stretch in open challenge time) and the capstone, and the key difference from AIA: learners prompt Copilot to write, fix or change the code (maths included), review what it wrote, run it and confirm with a check, keeping or undoing the change; they never type code or do the maths by hand. It is stated once, with what it means for task boxes, code cells, gaps and solutions, in `programme-profile/references/conventions.md` → "Learners direct AI and review what it wrote"; `module-challenge` applies it.

**The Copilot box** (user, 2026-10-16): wherever learners or instructors are told to prompt Copilot, in any file, the prompt sits in the one standard 🤖 COPILOT box, with badges in the order WHERE (Chat view, Inline chat, Terminal chat: the surface to open), MODE (Ask, Plan, Agent; Chat view only, where it is required), MODEL (Fast, Reasoning, Auto) and, when needed, ATTACH (`#<file>`, `selection`, `#codebase`, `#terminalLastCommand`, `#terminalSelection`; several separated by spaces), each label in its own colour (WHERE aqua, MODE yellow, MODEL blue, ATTACH green), the prompt in a ```` ```text ```` block with lines under about 90 characters, and the closing line for its surface (Chat view's by mode; Inline chat: read the change in the editor, then Keep or Undo; Terminal chat: Insert, not Run). Inline chat in a notebook cell (2026-10-16) keeps WHERE Inline chat but sets its own closing line with `then=`, because VS Code shows the diff in the cell with **Accept and Run**, which applies the change and reruns the cell: pass `then=nbkit.COPILOT_THEN_NOTEBOOK_CELL` or a line fitted to the task that names Accept and Run and no reject button (the docs name none); a box for a `.py` file in the editor keeps the Keep or Undo default. Ctrl+I in a file with Chat view edits not yet kept or undone opens the prompt in the Chat view instead (Ask in Chat), so a task that follows an Agent edit says to Keep or Undo first. Shortcuts give the Mac key in words, as in Ctrl+I (Cmd+I on a Mac), never as a key symbol. What it is, when to use it and how to choose the settings: `programme-profile/references/conventions.md` → "The Copilot box". Notebooks use `copilot_prompt`, `copilot_legend` and `copilot_solution` (Notebook tools, below); Markdown that becomes a PDF uses the `::: copilot` div (Callouts, below). Never a blockquote or a bare fenced block for a prompt.

## File shapes

**Overview** `learner/module00-overview/dayNN_overview.md` — learners, one H1, in learner order:

```markdown
# <the day's canonical title, the programme overview's word for word> {#sNN}

[Unit N · <unit title> › Day NN — overview]{.breadcrumb}

<The opening: one or two sentences that introduce Jordan before anything else (S01: "Every session follows **Jordan Mensah**, who works
with code and data at Harbourline Asset Management, an invented UK asset manager. Here's where Jordan stands as this session begins.";
user, 2026-10-19).>

#### Persona card — Jordan Mensah
<nbkit.persona_card_pdf_md(rows): Who · This session · What gets in the way · By the end · You, adapted to this session
(user, 2026-10-16)>

<The session, in a paragraph (no in-line links or citations): what you'll do and leave with, tied to Jordan's report ("Everything works
on Jordan's report, the weekly fund table, and you build your own copy of it as you go").>

<How the day runs, in a paragraph: the five-hour day (user, 2026-11-02), a 25-minute intro that starts with arriving, settling and finishing the setup check, then three 75-minute modules, each a 20-minute demo, a 25-minute challenge, 15 minutes of Shareback/questions, a 5-minute debrief and a 10-minute break, then optional open challenge time and the close; in each challenge
start at Q1 and go as far as you can; the last block, open challenge time, is optional: carry on, or try Put it together end to end.>

## The questions you'll answer {#dayNN-questions}

::: session
<One sentence: each module answers some of these questions; the wrap-up brings the answers together.>

- <Session question?>
- …
:::

## What you will be able to do {#dayNN-outcomes}
By the end of this session you will be able to:

- **<Verb>** <what> — <standard>, <condition>
- … (about five, copied verbatim from internal-programme-overview.md §6; no module tag on any outcome)

## Before you start {#dayNN-before}

<One or two sentences: which session it pairs with, and what's assumed and not assumed.>

### What's in this session {#dayNN-contents}

| File | What it's for |
|---|---|
| `module01-first-programs-copilot/m1-<slug>.md` | Module 1 handbook: concepts in depth, in the module's folder |
| … | … |
| `moduleNN-<slug>/dayNN_mN_challenge.ipynb` and the project folder beside it (one per module; Put it together in its own module folder) | Your tasks, each solution folded beneath, and the files they start from |
| `.devcontainer/`, at the top of the course folder | <what the dev container gives you> |
| `common/services/<name>/`, at the top of the course folder | <the service, with a `README.md` of commands and fixes> |

### Set up at the start of the day {#dayNN-setup}

<One line: do these as you arrive, so the dev container and services build while the session opens (user, 2026-10-19).>

**Services this session uses:** <each `common/services/<name>/` the session starts and what for, or "none">.

::: workflow
1. <Start Docker Desktop · Dev Containers (every session needs it) and Reopen in Container · the data check in the dev container's
terminal · start each service. Never a platform, download or unzip step.>
:::

### What you already know {#dayNN-self-check}

<One line: answer yes or no during the welcome; a no shows where to focus.>

1. <At most three yes-or-no questions, one per module in module order, untagged.>

## Agenda {#dayNN-agenda}
<One line: about four hours, each module runs the same way. No times or minutes anywhere in the learner's agenda (user, 2026-10-15):
the timings live in dayNN_lesson_plan.md.>

<No 🧭 anchor anywhere in the overview, the day's or a module's (user, 2026-10-27).>

::: {.outlined}
| Block | Flow | What you produce |
|---|---|---|
| Arrive and settle, then the welcome (a unit's first day) or Welcome back | Laptops open; the programme and this unit, how a day runs, introductions; Jordan and the day, what you will be able to do | One system you built or relied on, and what would make the unit worthwhile |
| Module 1 — <canonical title, word for word> | Demo · Challenge · Debrief · Break | <evidence> |
| Module 2 — <title> | Demo · Challenge · Debrief · Break | <evidence> |
| Module 3 — <title> | Demo · Challenge · Debrief · Break | <evidence> |
| Open challenge time (optional) | Carry on with any challenge, or try Put it together end to end | As far as you get |
| Closing debrief and questions | What blocked you, what you shipped, and anything about the day | Your blockers talked through |
| Wrap-up | Back to the outcomes and the questions | Your evidence per outcome |
:::

### How the challenges work {#dayNN-challenges}

<One or two lines: start at Q1 and go as far as you can; none of it is compulsory (user, 2026-10-19).>

::: {.outlined}
| Tier | Who it's for | What to expect |
|---|---|---|
| [Q1 · CORE]{.tier .core} | Everyone | Start here, then go as far as you can |
| [Q2 · STRETCH]{.tier .stretch} | Anyone who finishes Core | More of the decisions left to you |
| [Q3 · BONUS]{.tier .bonus} | Anyone with time left | Not expected: extra practice, if you want it |
:::

<A few lines: in every tier you direct Copilot and review what it writes; Your turn, What to show, the folded solutions; Put it together
is optional. How to read the tiers, never what each task is.>

<The agenda table and the tier table each sit in a `::: {.outlined}` div, which the PDF draws as an outlined table in the cards' family:
dark frame, shaded bold header, rules between rows (scripts/pdf-filters/outlined-table.lua; user, 2026-10-19). The tier labels are marked
[Q1 · CORE]{.tier .core}, [Q2 · STRETCH]{.tier .stretch} and [Q3 · BONUS]{.tier .bonus}, which the PDF draws as the notebooks' tier
badges (scripts/pdf-filters/tier-badge.lua).>

## The data {#dayNN-data}
<after the agenda and How the challenges work (user, 2026-10-19), just before the work starts: a data card for each dataset the session uses (`nbkit.data_card_pdf_md(name, rows)`: "#### Data card — the demo data",
then a grid table of Name, Used in, What, Rows, Files, Note, the Files row one file and what it holds per line, which the PDF draws as the blue DATA box; no 🗂️ here, the PDF has no glyph for it; never a paragraph of
data facts), after a one-line lead-in naming the two datasets>
```

No outcome, question or self-check item carries a trailing module tag ("*(Module 1)*", "*(Modules 1, 2)*", "(M2)"); the lesson plan holds that mapping in its own column or notes (user, 2026-10-15). The "what you already know" self-check has at most three yes-or-no questions, one per module in module order, each about the prior knowledge that most changes how fast and how deep that module goes (S01: Python functions; commands on a remote machine; a Python environment others can recreate); the lesson plan's welcome says which question paces which module and what to adjust on a mostly-yes or mostly-no room (user, 2026-10-15).

The builder requires a heading directly above every `::: session` box. The overview carries no times; the timings live in the lesson plan. Rows for modules not yet built are left out, not stubbed.

**Lesson plan** `instructor/module00-overview/dayNN_lesson_plan.md` — instructors: Decoded's lesson plan template adapted for CG Core and built to Word (user, 2026-10-16). The format, the blank plan and the rules belong to the `lesson-plan` skill: overview, objectives and outcomes, curriculum map, before the session, a timeline of rows of 2.5 to 20 minutes in 2.5-minute steps, one row per demo `### ` heading, a reference section per module, question bank, support and stretch, FAQs and the activity-type key. It may name modules and sessions, say the timetable is working and hold everything a learner should not read; it may point to "the Module N handbook" as a whole but never cites a handbook section by number or title (sections are numbered only in the PDF, and titles change). It replaces inline `::: notes` blocks.

**Slides** `instructor/module00-overview/dayNN_slides.md` — the day's deck (user, 2026-10-27), written once the lesson plan is final: `.venv/bin/python scripts/make_slides.py draft dayNN` drafts it from the plan's rows, `dayNN_anchors.md`, the demo `### ` headings and figures, the challenge Q titles and the debrief questions, in Decoded's builder slide dialect (`tools/builder`, pinned; layouts follow the `decoded-slides` skill's writing rules: one idea a slide, short titles). Running order (user, 2026-10-27; the five-hour day, 2026-11-02): cover · Arrive and settle (the standard slide, the same in every unit and day, id `arrive-and-settle`, for the plan's Arrive and settle row: `full-visual`, the usual title at the top over the shared picture `common/figures/shared/setup-check.png` on yellow (alt text as an attribute, `![](…){alt="…"}`, so no caption is drawn) and no other text, its notes the setup cue; drawn by `scripts/figures/shared_setup_check.py` with `brand.slide_figure()`) · the welcome: on a unit's first day (a `Welcome` row) one drafted `dayNN-welcome` title-body slide, Welcome, of the row's On screen points, hand-tunable, while the welcome itself runs from its own deck, `unit00-programme/day00-welcome/instructor/module00-overview/day00_slides.pptx`, beside the day's (user, 2026-11-02: kept separate; sync retires the welcome's old ids from a day's deck); on its second day (a `Welcome back` row) one drafted `dayNN-welcome-back` title-body slide of the row's On screen points, hand-tunable · Jordan and the day (Decoded's `table` layout: a short phrase a row, the card word for word in the notes) · What you will be able to do (a table: a short phrase per outcome, each outcome word for word in the notes; outcomes appear once a day) · Today (`agenda-3` tiles on the yellow photograph: "Module 01", the full canonical title, never shortened, then the module in one short line, the anchors file's **In short:**; a title that needs three lines is built with a stand-in and placed by `make_slides.py` with its caption moved down, user 2026-10-27) · per module: divider (`section-divider-photo`, the same yellow photograph as Today: "#1" and the canonical title) · the module's question (`statement`) · What, why and how (`recap-3` tiles, the anchors file's short phrases; the anchor word for word in the notes) · map · one slide per demo heading · a think slide (the first Ask's question as the title, its lead-in and any second Ask as prompts) · challenge brief and continuation · Shareback/questions (`challenge-continuation`, id `dayNN-mN-shareback`, drafted from the row's On screen points or Purpose, hand-tunable; user, 2026-11-02; sync retires the old `dayNN-mN-catch-up`) · debrief · break · Put it together · Closing debrief and questions (the Wrap-up's first row, id `dayNN-closing-debrief`) · Key takeaways · Thank you for participating (title and photo only; the feedback form stays in the notes, never on the slide); no Meet and greet or Setup check slide (user, 2026-11-02). **Concise slides** (user, 2026-10-27, like Fundamentals'): a title of 8 words or fewer (canonical titles and a statement slide's question exempt), at most 3 bullets a slot, each bullet, line or table cell 12 words or fewer; the rest goes in the speaker notes (**Detail:**, **Say:**), so nothing is lost. The generator drafts to it (`short`, `concise`) and `make_slides.py check` and the audit fail on longer text (`concise_problems`). Speaker notes are the row's Say (**Say:**), its notes and transition (**Delivery:**) and, for a Questioning row, **Listen for:** and **If stuck:**. Tune it by hand after drafting; `draft` won't overwrite without `--force`. After any lesson-plan change, run `.venv/bin/python scripts/make_slides.py sync dayNN`, then `make_slides.py check dayNN` (user, 2026-10-27): sync adds a slide for each new row or heading, refreshes every slide's title by id and its speaker notes from its row (dropping the notes when the row has none, unless **Detail:**), rewrites the frame slides whole (cover, Arrive and settle, agenda, dividers, the module question and what/why/how tiles, Thank you), refreshes timed slots (a challenge's minutes), retires drafted slides the plan no longer implies, and otherwise never overwrites a hand-tuned slide body, a hand-written **Detail:** note or a hand-added slide. There is no day-level question or what/why/how slide. Titles are the canonical ones, never cut: a long title gets a smaller font. Slide ids are stable (`dayNN-meet-greet`, `dayNN-persona`, `dayNN-outcomes`, `setup-check` (fixed, in every deck), `dayNN-agenda`, `dayNN-mN-question`, `dayNN-mN-whatwhyhow`, `dayNN-mN-<heading slug>`, `dayNN-mN-questioning`, `dayNN-key-takeaways`, `dayNN-thank-you` …); `make_slides.py check dayNN` and the audit fail when a demo heading, Questioning row, challenge, shareback, debrief, break or wrap-up row has no slide, an id repeats or an image doesn't resolve. The build ships `dayNN_slides.pptx` and `dayNN_slides.pdf` (the builder's slides-pdf) to `instructor/module00-overview/`; the `.md` never ships.

**Handbook** `learner/moduleNN-<slug>/dayNN_mN_handbook.md` — learners, one H1, self-contained, in the style of the L6 handbook (`reference/L6-source content/M09 … Handbook (WIP).md`):

```markdown
# <Module title> {#dayNN-mN-handbook}

[Unit N · <unit title> › Day NN › Module N — handbook]{.breadcrumb}

*<One italic line: where the work starts and where it ends.>*

<The intro paragraph: what this handbook covers ("This handbook covers …"); no persona, invented-data or real-run sentences, which are the card's.>

#### Persona card — Jordan Mensah
<nbkit.persona_card_pdf_md(rows): Who · This module · What gets in the way · By the end · The examples, true to this handbook,
with no version numbers ("Python and pandas") (user, 2026-10-19)>

<The module's 🧭 anchor, generated from `dayNN_anchors.md` (`## mN`); never typed. The card stays as it is.>

<The useful output it starts from, if any.>

## What this handbook covers {#dayNN-mN-covers .unnumbered}

- **<Topic.>** <What it adds, in a line.>
- …

## <Section title> {#dayNN-mN-1}

<Concept text in connected paragraphs, no in-line links or citations. Worked example on the demo data with Jordan and real tested output.>

The chart below <introduces the figure from the line above>.

![<The caption: what the figure shows, one sentence.>](../../../../common/figures/dayNN/mN-<what>.png){width=90%}

```{.mermaid height="0.32" fontsize="18"}
flowchart LR
  A[Plan] --> B[Generate]
```
<!-- caption: "<The Mermaid figure's caption.>" -->

### <Subsection>
…
### Optional further reading
- **<Type>:** [*<Title>*](https://…) by <Source> — what it adds, one line. (The only place the handbook links or names a source; the PDF shows
  the type and the web address, with the description indented beneath, by scripts/pdf-filters/further-reading.lua.)

## <Section title> {#dayNN-mN-2}
…
## Summary {#dayNN-mN-summary .unnumbered}
…
## Going further with <topic> {#dayNN-mN-appendix .unnumbered}   (optional: see markdown-conventions.md)
```

Headings and captions carry no typed numbers (user, 2026-10-15): when the PDF is built, `scripts/pdf-filters/handbook-section-numbers.lua` numbers the H2s 1, 2, 3 … and H3s 1.1, 1.2 … in each handbook (it keys on the H1 id ending in `-handbook` and skips `{.unnumbered}`), and the PDF numbers the figures. An image's caption is its description; a Mermaid block's caption is the `<!-- caption: "…" -->` comment straight after its fence. Prose never cites a figure or section by number ("the chart below", not "Figure 1.2"; "the four moves", not "section 1.6"). Every H2 section ends with an "Optional further reading" subsection; the Summary is `{.unnumbered}`. Catalyst appears only inside `::: catalyst` boxes. Learner words: 3,000 to 12,000, aiming for about 7,000; past 7,000 only for topic knowledge (user, 2026-10-26). Prose is specific (a reference back names the file, the command and what it shows) and defines every term before any shorthand for it, and names the testing level of any test it shows. Prose is connected paragraphs of usually three to six sentences with transitions, never runs of one- and two-sentence paragraphs; it carries no in-line references (links, citations, "(… docs)" asides) and paraphrases documentation rather than quoting it; no "The proper words" line repeats a mapping a figure already labels (`markdown-conventions.md` → Prose rules). A handbook never mentions demos, challenges, the session, the agenda, setup, instructors or Asana, never links into `demo/` or `challenge/`, and never promises a later module; it may build on concepts from earlier handbooks.

**Demo notebook** `instructor/moduleNN-<slug>/dayNN_mN_demo.ipynb` (or `.md`), one per module (user, 2026-10-27), instructors only, self-contained — nbkit's short, identical header, then the module section, in order:

- Cell 1: the Decoded title cell (`nbkit.title_cell("<session title>", nbkit.breadcrumb(<unit>, "<unit title>", NN, "demo notebook"))` (no version line)). Cell 2: the 🗺️ table of contents in its own cell (id `toc`), which `scripts/nbkit.py toc --nb <anchor>` builds after `write()` from the notebook's own headings and boxes, giving every `## ` heading cell its anchor line; never typed or edited by hand ([references/notebook-boxes.md](references/notebook-boxes.md) → "Table of contents"). Cell 3: how to use this notebook (which files sit beside it, where the data is), followed by the Copilot settings legend (`md(nbkit.copilot_legend())`, in that cell or the next) whenever the notebook has a 🤖 COPILOT box. Then a `## Setup` section holding the data card of every dataset the notebook reads (`md(nbkit.data_card(name, rows))`, the same fields as the overview's card, the Files row given as a list so each file and what it holds sits on its own line), before the first module section: it serves every module, and no module section repeats it; a module that reads data the card doesn't cover adds it to this card. Last cell: the footer.
- Per module, each in its own cell: a `## Module N — <title>` heading cell, the 🧭 anchor cell (generated by `scripts/nbkit.py anchors --session <folder>`; never typed), a bridge cell ("This builds on …", naming the project, numbers and repository, plus one line into the map), the module map cell, then the beats (the AI-assisted beat's prompt in a 🤖 COPILOT box, `md(nbkit.copilot_prompt(title, prompt, mode, model, attach=…, where=…))`), any bridge out, the **🏆 CHALLENGE TIME box** (`md(nbkit.challenge_time_box(…))`: the challenge anchor and section, a line per tier, then `nbkit.CHALLENGE_TIME_LAST`, "Start at Q1 and go as far as you can. Q3 is a bonus, not expected."), and last the module's **Go deeper box** in its own markdown cell (`md(nbkit.go_deeper(N, "<what the handbook adds>"))`). A ⌨️ TERMINAL box (`nbkit.terminal_box`) comes before each terminal step. **Visual-first:** each beat is one visual (a brand concept card from `../../../../common/figures/dayNN/`, made by `scripts/figures/dayNN/`, or a ```` ```mermaid ```` flow), three to five bullets, and a short code cell only when the beat runs something; contrasts side by side; no "The proper words" line under a visual that already labels the mapping; a figure whose rows explain something lines them up with it. A config file the demo opens (a Dockerfile, a pipeline file) gets a plain line-by-line table in the file's own order: each line and what it does, one short sentence each. A step too slow for its lesson-plan row (a push, a pipeline run, a first image build) is pre-run in the break, and the beat says so. Where a file beside the anchor carries the work, a markdown cell says **open** `m1_fund_report_reviewed.py`, **look at** the lines or the behaviour to notice, **come back** here; the next code cell runs or checks it.
- **The handbook is mentioned only in that box** (user, 2026-10-15): never in a beat title, a bullet, a code comment, an image's alt text, a module map or card, or a file beside the anchor, and never by section number or title.
- Data from `../../../../common/data/demo` (the module notebook sits four folders below `courseware/`; a completed challenge in `challenge-solution/` sits five); scripts beside the anchor resolve their paths from `Path(__file__)`.
- Shipped executed, top to bottom, with sequential execution counts and no absolute paths, keys or learner traces in outputs.

**Challenge notebook** `learner/moduleNN-<slug>/dayNN_mN_challenge.ipynb` (or `.md`), one per module, and Put it together's `learner/module99-put-it-together/dayNN_together_challenge.ipynb` — each self-contained, nbkit's short, identical header then the module's tasks:

- Title cell, the 🗺️ table of contents (`scripts/nbkit.py toc --nb <anchor>`, as in the demo; the completed copy gets the same table after its answers are in), how-to-use cell with the difficulty legend (`nbkit.difficulty_legend_html()`) and the Copilot settings legend (`md(nbkit.copilot_legend())`, in that cell or the next), a `## Setup` section (the challenge data's card, `md(nbkit.data_card(…))` with the Files row as a list and values in HTML, the blue 🗂️ DATA box, then a setup cell: imports, the path to `../../../../common/data/challenge`, a file check) before the first module section, footer. Per task, each in its own cell: the heading, the 🧭 anchor (identical to the demo's, a recap), the bridge ("This builds on …", naming the starting folder and what's already in it), then one recap visual of the demo section it follows (the module map) (no times anywhere in the challenge: the demo's 🏆 CHALLENGE TIME box gives the one fixed time for all three tiers (user, 2026-10-16)), then AIA's box set from `nbkit`: one ⚡ task box per tier (`task_box`: Q1 · CORE for everyone and first in every section, Q2 · STRETCH, Q3 · BONUS not expected; "Task N.k —" lines that ask Copilot to write, fix or change the code, then review it and run the check), the starting code with its planted fault in the cells between, a 🤖 COPILOT box (`copilot_prompt`) wherever a task hands learners a prompt to use, ⌨️ TERMINAL boxes before terminal steps (`terminal_box`), a 💭 REFLECT box with the solution folded under it in one cell (`reflect_solution`, whose body `copilot_solution` gives as a model prompt with the Copilot box's badges and text block, the change and the check), 🎯 YOUR TURN boxes for short no-code tasks (`your_turn_box`), and last, in each module section, the 📚 Go deeper box (`go_deeper`). The put-it-together section uses the same boxes and has no Go deeper box; nothing else mentions the handbook.
- **AI writes the code; learners review it** (`programme-profile/references/conventions.md`): code cells hold complete starting code, `___` only records an observation or decision in markdown or a string, never code to write; no `# TODO` for learners, no "Step N", no "fill the gaps"; light maths.
- **Self-contained**: data from `../../../../common/data/challenge`, its own setup cell and starter files (module-prefixed, only where a task needs them); never a demo cell, file, variable or path into `instructor/` (services in `courseware/common/services/`, such as S01's SSH remote, are setup and may be used). A starter file with planted faults is named for its part in the story (`*_copilot.py`), never for its faults.
- Shipped **without outputs** (a challenge notebook is the learner's to run).

## Callouts (the only ones the build renders)

| Fence | Use | Where |
|---|---|---|
| `::: session` | Questions the session answers, untagged (the lead-in may say each module answers some of them; the lesson plan holds the mapping) | `dayNN_overview.md` (one); must contain a bullet list and sit under a heading |
| `::: expert` | Expert note: the practitioner's view, the thing the docs don't say | Handbook; at most two per handbook |
| `::: {.catalyst source="skills/<id>/SKILL.md @ Catalyst <version>"}` | Quoted Catalyst guidance | Handbook; `source=` mandatory; quote, do not paraphrase |
| `::: workflow` | A numbered sequence of steps | Handbook, overview |
| `::: predict` | A predict-before-reveal prompt | Handbook |
| `::: blocked` | A house-builder feature that CG Core content never uses (user, 2026-10-16) | Nowhere: the course runs on local containers and carries no CG-access notes (`programme-profile` rule 3). The audit warns on one and the build refuses it |
| `::: extra` | Optional depth | Handbook; never a prerequisite |
| `::: {.copilot title="…" where="Chat view\|Inline chat\|Terminal chat" mode="Ask\|Plan\|Agent" model="Fast\|Reasoning\|Auto" attach="…"}` | A prompt learners or instructors type into Copilot, around a ```` ```text ```` block: the 🤖 COPILOT box, drawn by `scripts/pdf-filters/copilot-box.lua` and, in the Word lesson plan, `scripts/docx/build_lesson_plan.js` (user, 2026-10-16) | Handbook, lesson plan, overview: every prompt, never a blockquote or a bare fenced block; `title`, `where` and `model` required, `mode` with Chat view only (a div with no `where` draws as Chat view, and the audit warns), `attach` only when the prompt needs context |

**The persona card** is not a callout but has its own PDF box (user, 2026-10-19): `scripts/pdf-filters/persona-card.lua` draws every "#### Persona card — <name>" heading and the two-column table straight after it as one branded box, the same in the overview and every handbook (a brand-yellow "PERSONA — <name>" header bar, pale-yellow labels beside white values, a thin dark frame). Write it only with `nbkit.persona_card_pdf_md`, never styled by hand; the design and its colours are in [references/markdown-conventions.md](references/markdown-conventions.md) → "The persona card's design", and `nbkit.persona_card_html` is its notebook twin. **The data card** is the same box in blue (user, 2026-10-19): the filter draws every "#### Data card — <name>" heading and its grid table with the same function, a "DATA — <name>" header bar in the Copilot MODEL badge blue `#C9DAF8` and pale-blue labels `#E4EDFC` (→ "The data card's design"); in notebooks `nbkit.data_card` gives the twin, header "🗂️ DATA — <name>", from the helper the persona card's HTML uses.

`::: notes` is retired (instructor material is the lesson plan). `::: group-challenge`, `::: solution`, `::: debrief` and `::: hint` belonged to the old combined lesson and are not used: challenges, hints and solutions live in the challenge anchor, debriefs in the lesson plan. Callouts do not render in Jupyter; anchors use plain Markdown and `<details>`. Headings inside a callout become bold run-in lines; do not rely on them. Mermaid goes in a fenced block ```` ```{.mermaid height="0.32" fontsize="18"} ````; Python figures are PNG in `courseware/common/figures/dayNN/`, made by `scripts/figures/dayNN/`.

## Notebook tools

`scripts/nbkit.py` (tracked in the repo, so every clone has it; moved from this skill's `scripts/` on 2026-10-19) gives the title cell, the footer and every box (user, 2026-10-15): `difficulty_legend`, `task_box(tier, title, mode, goal, tasks)`, `reflect_solution(question, solution, answer)` with `copilot_solution(prompt, change, check, mode=…, model=…, attach=…, where=…)` for its body, `copilot_prompt(title, prompt, mode, model, attach=None, purpose=None, then=None, where="Chat view")` for every prompt learners or the instructor are given (with `then=COPILOT_THEN_NOTEBOOK_CELL` for Inline chat in a notebook cell), `copilot_legend()` once in "How to use this notebook" of an anchor with a Copilot box, `terminal_box(title, body, commands)`, `your_turn_box(title, body)`, `challenge_time_box(module, minutes, anchor, section, line, q1, q2, q3)` and `go_deeper(module, body)`. Each returns a markdown cell (pass it to `md()`), and each has an `*_html` twin returning the string for a Markdown anchor. The exact HTML, copied from AIA, is in [references/notebook-boxes.md](references/notebook-boxes.md); never write a box by hand. `scripts/nbkit.py selftest` renders every helper and compares it with that file byte for byte (on a clone without `.claude/` it reports those comparisons skipped and still checks the patterns and the PDF filters' colours), and `module-audit` checks every box in an anchor against `nbkit.box_patterns()`, built from the same code. After changing a box, change the reference file, nbkit and nothing else, then run `selftest`. Its other AIA helpers (break, live code, discussion, banner, `setup_cell`) are not used in Core. `scripts/nbkit.py summary --nb X.ipynb` prints the sanity line; `scripts/nbkit.py clear` clears a challenge notebook; `scripts/nbkit.py patch-md` edits markdown without losing outputs. `scripts/nbkit.py toc --nb X.ipynb` builds the 🗺️ table of contents and the section anchors (`nbkit.apply_toc(nb, kind)` from a script; the kind comes from the folder), and `--check` writes nothing and exits 1 when they are out of date: run it after every `write()` and after any change to a `## ` or `### ` heading, a task box or a your-turn box. It changes markdown only, so an executed demo needs no re-run after it. Execute a demo anchor with nbclient on the `python3` kernel from `demo/` as the working directory, and keep the builder script in the scratchpad.

## Check (every edit)

```bash
# 1. Dialect check: pandoc must parse every Markdown file and every callout must close (the builder's own pandoc)
PANDOC=$(ls ~/.cache/build-pdf/tools/pandoc-*/pandoc-*/bin/pandoc | head -1)
for f in courseware/<unit>/dayNN-<slug>/learner/module00-overview/dayNN_overview.md courseware/<unit>/dayNN-<slug>/instructor/module00-overview/dayNN_lesson_plan.md courseware/<unit>/dayNN-<slug>/learner/moduleNN-<slug>/*.md; do
  "$PANDOC" "$f" -f markdown -t html -o /dev/null && echo "parses: $f"; done
# 2. Formatting: isort, black (notebooks too) and blacken-docs; --check must pass after every code change
.venv/bin/python scripts/format_code.py courseware/<unit>/dayNN-<slug>/ && .venv/bin/python scripts/format_code.py --check courseware/<unit>/dayNN-<slug>/
# 3. Mechanical sweep: per-file-kind rules, typed numbers, every box against nbkit's spelling, Go deeper and challenge-time placement, Q1-first tiers, reflect before every solution, Copilot boxes, the Copilot legend and prompts outside the box, code gaps, a self-contained challenge, planted-fault files (by name), handbook mentions, in-line references, paragraph runs, links, images, visuals, naming, banned words, names, markers, notebooks, formatting, litter
.venv/bin/python scripts/audit.py courseware/<unit>/dayNN-<slug>/
# 4. Run the demo anchor top to bottom and every file it opens; run each challenge cell and starter file as shipped (it fails where the task says), then apply each folded solution's change to a fresh copy and run its check (in the dev container image: quoted outputs never come from .venv)
# 5. Tables of contents, anchors and the environment
.venv/bin/python scripts/nbkit.py toc --nb <notebook> --check            # each notebook
.venv/bin/python scripts/nbkit.py anchors --session <session folder> --check
# when pins or services changed: scripts/test-dev-container.sh and each scripts/test-<service>.sh
# before handing over (session checklist part E), all of it in one go, audit at 0 errors and 0 warnings:
scripts/check-session.sh dayNN
```

## Code formatting (every code change)

After creating or changing any code the course ships (`scripts/`, the files and notebooks in `instructor/moduleNN-<slug>/`, `learner/moduleNN-<slug>/` and `instructor/moduleNN-<slug>/challenge-solution/`, Python blocks in handbooks, lesson plans and READMEs), run `.venv/bin/python scripts/format_code.py <paths>` and finish with `--check` passing (user, 2026-10-15). It runs isort with black's profile (files beside the one being sorted count as local imports; notebook cells one by one), black (notebooks too) and blacken-docs for Python blocks in Markdown, with the settings in `pyproject.toml` (line length 88). Comments go above the code they explain wherever a comment at the end of the line would make black split it, and `scripts/format_code.py` moves them there automatically; a short end-of-line comment on a line that still fits in 88 characters may stay (user, 2026-10-16). Solution code folded in a challenge's markdown `<details>` is not reached by black: write it in black's style. A demo anchor reformatted by black is re-executed so its outputs match its code.

## Build (only after the user has reviewed the content)

```bash
scripts/build-session.sh day01 --out <scratch dir> --no-gates   # a throwaway build outside the repo, to look at
scripts/build-session.sh day01 --reviewed                       # after the user's review: release/latest/
scripts/build-session.sh all --reviewed                       # every session that has an overview
```

Drive gets everything in its final form (user, 2026-10-27): reading Markdown ships only as its PDF or Word file, working files ship as they are, authoring files never ship. The build (user, 2026-10-16; `scripts/build_session.py`) writes one tree, `release/latest/`, laid out exactly like `courseware/` (user, 2026-10-27; tracked in git), with each Markdown source that becomes a document replaced by its built form. The full tree and how it's shared on Google Drive are in `programme-profile/references/layout.md` → Built outputs and sharing. `release/latest/` has `.devcontainer/`; `common/` (`data/`, the services the overview names, `figures/<session>/`); `unit00-programme/learner/start-here.pdf` and `unit00-programme/instructor/` (the instructors' `start-here.pdf`, `release-notes.pdf` and each shipped service's `INSTRUCTOR.pdf`), `RELEASE.pdf` (the inventory; `RELEASE.md` stays beside it for git and the checks and isn't synced); per session `learner/` (one PDF per source file, `module00-overview/dayNN_overview.pdf` and each module folder's `dayNN_mN_handbook.pdf`, through `./build-pdf` and `builder.toml`, and a copy of each learner module folder's challenge notebook and project folder, tracked files only) and `instructor/` (`dayNN_lesson_plan.docx` from `scripts/docx/build_lesson_plan.js`, review PDFs of the demo, the challenge (`scripts/notebook_pdf.py`: solutions open, the files beside them appended) and the completed challenge (`dayNN_mN_challenge_solution.pdf`), and copies of each instructor module folder's demo notebook and files and its `challenge-solution/`, so they run as they are). Gates stop the build on a challenge with outputs, a demo without them, a missing `challenge-solution/`, one with a code cell that never ran or counts out of order, or untracked files in a committed one (each a warning in a scratch build), one without outputs or with an error output, a CG-access note in anything shipped (a `::: blocked` callout, a `<!-- blocked:` marker or "Needs CG access"; CG Core content never carries one), a `<!-- sensitive` marker in anything shipped (markers are retired, user, 2026-10-19), a missing service, or instructor material outside an `instructor/` folder (a lesson plan, demo, completed challenge, solutions-open PDF, release notes or `INSTRUCTOR.md` in `learner/` or `common/`, or a learner file linking into `instructor/`); `--no-gates` reports them instead. It refuses to write into the repo without `--reviewed` (`--out <dir>` builds `<dir>/release/latest/` anywhere else), and stops if git tracks nothing under `courseware/` (it copies tracked files). A build that passes its gates writes `.build-manifest.json` at the top of `release/latest/` (tracked in git, never synced); one whose gates failed (`--no-gates`) removes it and never syncs. A `--reviewed` build into the repo then runs `scripts/check_release.py` on the tree and, only if that passes, syncs to Drive's `release/latest/` (`scripts/sync-release.sh`) on the release owner's machine, the one where the Drive folder is configured; anywhere else it skips the sync and says so, and `--no-sync` skips it. Every developer runs `scripts/install-hooks.sh` once per clone (its pre-commit hook runs `check_release.py --staged` when a commit touches `release/latest/`); only the release owner releases. The release steps (build, confirm "verified" in the log, commit `release/latest/`, the release-notes line) are `module-materials`'. Text that ships never names `courseware/`: shipped paths start from the course folder (`common/data/challenge/`, `common/services/remote-machine/`), and `dayNN_anchors.md` never ships. References name files as they ship (user, 2026-10-19): the build renames every mention of a source `.md` it converts (`dayNN_overview.md`, each module's `mN-*.md` handbook, `start-here.md`, `release-notes.md` → `.pdf`, `dayNN_lesson_plan.md` → `.docx`) in the PDFs, the Word file, the notebook PDFs and the copied text files, and stops on any it missed; keep the `.md` links in `courseware/`. `builder.toml` holds the house PDF settings: `rewrite-relative-assets = true`, `[toc] depth = 2`, the local filters in `scripts/pdf-filters/` (`strip-html-comments.lua`, `handbook-section-numbers.lua`, `breadcrumb.lua`, `shipped-refs.lua`, `persona-card.lua` for the persona and data cards, `tier-badge.lua`, `further-reading.lua`, `outlined-table.lua`, `code-with-output.lua`, `copilot-box.lua`) and the `[headers] extra` files in `scripts/pdf-headers/` (`code-as-typed.tex`, `link-colour.tex`, `spacing.tex`). Nothing is zipped. Look at every rendered page before shipping: figures, captions, callouts, the Word timeline.

Every PDF keeps the identical house cover and formatting. Fix a PDF that reads badly by its wording (the H1 becomes the cover subtitle), never by changing its layout or cover, unless the user asks.

## The Decoded LMS

The courseware is also imported into the Decoded LMS (`~/Documents/decoded-lms`), unit by unit. What the importer reads, the Markdown it understands, and how to write knowledge checks, reflections, assignments, feedback forms, sessions and discussions as a module's `dayNN_mN_activities.yaml` are in `~/Documents/decoded-lms/docs/guides/curriculum.md`; read it before writing anything meant for the LMS. Before handing a unit over, check it from the LMS folder: `npm run import:check -- --courseware ../ts-cg-core/courseware --unit <unit folder>` must say "Ready to import".

## Ship state

No `.ipynb_checkpoints/`, `__pycache__/`, `.DS_Store`, `_verify` twins, stray logs, built PDFs or zips inside `courseware/`, generated data outside `courseware/common/data/`, "practice" in any name or path, unformatted code, absolute paths (`/Users/…`) in any file or notebook output, real keys, `.env` files, individual names, or `TODO`/`TBC` in learner-facing text. `module-audit` greps for all of these.

**Action-first prose (user, 2026-11-02).** Summaries, purposes, section summaries, slide lines, cards and speaker notes say what learners do, in order, with a concrete object ("Write pytest tests for the report's code, fix it test-first…"), never a topic summary ("Make a change the way a team does", "An AI service that answers with evidence"). The rule and its banned words are in `courseware-conventions/references/writing-rules.md` → Learner-facing descriptions; reviews flag any line a reader couldn't picture doing at their laptop.

**Technical terms and completeness (user, 2026-11-02).** A summary names the techniques in the field's terms (FastAPI, RAG, agents, evals, dbt, Airflow), explained at first use or in the notes, and covers every module it summarises; check it against the module list ("Build a FastAPI service with model calls, RAG, agents and evals", not "Serve a JSON API whose AI summaries cite sources"). Rule: `courseware-conventions/references/writing-rules.md` → Learner-facing descriptions.
