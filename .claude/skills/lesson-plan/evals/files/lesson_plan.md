# Notebooks to scripts, the command line and Python environments

[Unit 1 · Software engineering with AI › Day 01 — lesson plan for instructors]{.breadcrumb}

Timings are a guide: adapt them to the room. Confirm the start and end times, the breaks and the timezone before you deliver.

## Overview

This is the first session of Unit 1, Software engineering with AI, and of the programme. Learners write their first programs the way an engineer does, with Copilot beside them from the first hour. The shift is from code that works once to code that keeps working.

Jordan Mensah (they/them) works with code and data at Harbourline Asset Management, an invented asset manager, and sends round a weekly table of fund returns. That report is the one artefact the whole session works on. Each learner builds their own version on the challenge data, and each module leaves it in better shape for the next.

The session's themes:

- **Module 1 — Software engineering, your first programs and Copilot.** The report goes from a notebook to a script with a recorded check. Copilot writes; the learner reviews every line.
- **Module 2 — Command line, Linux and remote workflows.** The script runs on a remote Linux machine over SSH, with its data folder a setting and its output, log and exit code captured.
- **Module 3 — Python packages, dependencies and reusable modules.** The script becomes a package with pinned requirements and a README, proved in a fresh environment.
- **Open challenge time (optional).** Carry on with any module challenge, or try Put it together, Ship your report, end to end: the package on the remote, in its own pinned environment.

Learners leave with a fixed report cell, a reviewed script with a check, output and logs from a machine they can't click on, and a package someone else can rerun. The session is for CG engineers comfortable with code and an editor; notebooks, the terminal, Git and Copilot aren't assumed.

You teach from the back of the room: a short demo, then learners work. Every challenge is go-as-far-as-you-can, starting at Q1. Nobody has to finish, and nobody is chased.

## Objectives and outcomes

| # | Learning objective | By the end of the session, learners can… | Module | Evidence |
|---|---|---|---|---|
| 1 | The software lifecycle | **Explain** the stages of the software development lifecycle and where integration, release and deployment sit — naming each stage and one artefact it produces, for the Harbourline reporting script | M1 | A stage for each thing they made in the challenge, and the stages that have nothing yet |
| 2 | Notebooks and scripts | **Write** a small data-processing program first in a notebook and then as a script — same output, no notebook state, run from the terminal on the synthetic fund data, with no prior notebook experience assumed | M1, M2 | One table from the notebook, the terminal and the remote |
| 3 | Working with Copilot | **Refine** code with Copilot — planning the change in a prompt, choosing a mode and model for the task, reviewing every generated line and recording one deterministic check, using CG's VS Code workflow and the Copilot quick reference | M1 | A My checks entry with where, mode and model, review note and passing check |
| 4 | The Linux shell over SSH | **Run** and inspect a scripted task from a Linux shell — navigating the filesystem, capturing standard output and logs to files, inspecting the process and permissions, on a remote container over SSH | M2 | Output, log and exit code from a run on the remote, and what each command did |
| 5 | Reproducible environments | **Create** an isolated, pinned environment and a small reusable module, and **describe** how another developer reproduces the result — install succeeds in a fresh environment, the script imports the module, and a README lists repository, environment file and run command | M3 | A fresh `.venv` built from `requirements.txt` that prints the same table (`identical`, `same-set`), the script importing from `harbourline.returns`, and the steps a colleague types |

Module 1 answers session questions 1 to 3, Module 2 question 4 and Module 3 question 5.

## Curriculum map

| Unit | Session | Modules |
|---|---|---|
| 1 · Software engineering with AI | **S01 · Notebooks to scripts, the command line and Python environments (this session)** | **M1 Software engineering, your first programs and Copilot · M2 Command line, Linux and remote workflows · M3 Python packages, dependencies and reusable modules** |
|  | S02 · Testing with pytest, Git and pull requests, containers and CI | M4 Unit testing with pytest and AI · M5 Git, pull requests and AI-assisted review · M6 Containers and CI — build, run, check |
| 2 · AI engineering | S03 · AI product design, FastAPI and hosted-model calls with AI frameworks | M1 Systems thinking — the shape of an AI product · M2 Rapid JSON API development · M3 Hosted models as components — calling, structured outputs and vendor isolation |
|  | S04 · RAG and grounding, agents and tools, evals | M4 RAG and grounding — documents, numbers and traceability · M5 Agents, tools and AI skills · M6 Evals — gold sets, repeated trials and model choice |
| 3 · Data science with AI | S05 · Exploratory analysis, statistics and time series | M1 Exploratory data analysis in Python with AI · M2 Descriptive and inferential statistics · M3 Time-series analysis |
|  | S06 · Predictive modelling, leakage checks and local pretrained models | M4 Predictive modelling — targets, baselines and reproducible pipelines · M5 Automated improvement, comparison and leakage checks · M6 Local pretrained models |
| 4 · Data engineering with AI | S07 · Data products, platforms and dbt transformations | M1 Introduction to data engineering · M2 Data platforms · M3 ETL/ELT and dbt |
|  | S08 · Data quality, Airflow orchestration and AI-assisted pipelines | M4 Data quality and advanced dbt · M5 Airflow and orchestration · M6 AI-assisted pipeline development |
| Capstone | S09 · Build, containerise and defend an AI-powered data API | P1 Data ingestion and preparation · P2 Analysis, GenAI and API integration · P3 Final demonstration and design defence |

## Before the session

### Materials

Your files are in the session's `instructor/` folder and the learners' in its `learner/` folder, one folder per module on each side, and each path starts there (`module01-first-programs-copilot/` with the demo notebook, its files and `challenge-solution/`; `module01-first-programs-copilot/` with the challenge notebook, its files and the handbook); the dev container is at the top of the course folder, the data and services in `common/`.

| File | For | Use it for |
|---|---|---|
| `module00-overview/day01_overview.pdf`, each module folder's handbook (learner side) | Learners | The welcome: outcomes, self-check, agenda. The module handbooks hold the concepts in depth |
| `moduleNN-<slug>/day01_mN_demo.ipynb` | You (instructors only) | One demo notebook per module, each opening on its module map and ending with a Challenge time box and a Go deeper box |
| `demo/m1_…`, `demo/m2_…`, `demo/m3_fund_report/` | You | The files the demo opens, and the stand-ins for its live Copilot beats: `m1_fund_report_reviewed.py`, `m2_fund_report.py`, `m2_ssh_config.txt` and `m3_fund_report/` |
| `moduleNN-<slug>/day01_mN_challenge.ipynb` | Learners | One challenge notebook per module, and Put it together's in `module99-put-it-together/`, each solution folded under its task |
| `challenge/m1_fund_report_copilot.py`, `challenge/m3_fund_report_copilot/` | Learners | Starters with planted faults: leave them broken. Beside them, `together_fund_report/` is the catch-up for Put it together |
| `moduleNN-<slug>/challenge-solution/day01_mN_challenge.ipynb` | You | The challenge done in full, to walk through in the debriefs. It sits in the instructor module folder, beside the demo, and runs as it is. Never hand it out |
| `instructor/` | You | This lesson plan in Word, and review PDFs: the overview, the demo, the challenge with every solution open, and the completed challenge (`day01_challenge_solution.pdf`). Never hand them out |
| `.devcontainer/`, `common/services/remote-machine/` | Everyone | The dev container, whose terminal everybody uses, and the remote machine. Its `README.md` has commands and fixes; your notes for it are `unit00-programme/instructor/services/remote-machine/INSTRUCTOR.md` |
| `common/data/demo/`, `common/data/challenge/` | Everyone | The demo data (HLF, 46 share classes) and the challenge data (HLP, 49) |

### Your checklist

#### Before the day

- [ ] Copy the course folder to your laptop and work in that copy, never inside the shared folder
- [ ] Before you rehearse, keep a second copy aside, untouched: your clean copy
- [ ] Confirm the timetable: start and end times, breaks, timezone
- [ ] Open your copy in the dev container, with Copilot signed in
- [ ] Build the remote's image once, in `common/services/remote-machine/`:
  - `bash service.sh start`
- [ ] Rehearse each demo section top to bottom. Each ends:
  - Module 1 `check passed` · Module 2 `identical` · Module 3 `identical` and `same-set`
  - Module 3's freeze shows a numpy newer than 2.5.4? Learners' freezes will differ in that one line: say so in Module 3
- [ ] In a notebook cell, ask Inline chat (Ctrl+I, Cmd+I on a Mac) for a one-word change. Note the controls that keep or reject it, for Module 1's Q1
- [ ] Check the pip cache prints `Using cached`, then delete the test venv:
  - `python -m venv /tmp/v && /tmp/v/bin/python -m pip install pandas==2.3.3 pyarrow==26.0.0`
  - `rm -rf /tmp/v`
  - Only numpy downloads? The index has a newer numpy: don't rebuild
  - pandas or pyarrow download? Rebuild the dev container, then restart the remote so it reads the new key: `bash service.sh stop`, then `bash service.sh start`

#### On the day

- [ ] On the room's network, time the index check in `common/services/remote-machine/`, before you put the room back:
  - `time bash service.sh connect "python3 -m pip download --no-deps --no-cache-dir -q -d /tmp/probe pyarrow==26.0.0 && rm -rf /tmp/probe && echo index-ok"`
  - No `index-ok`, or more than about 30 seconds? Plan the wheels fallback for Put it together
- [ ] Open the completed challenge for the debriefs: each module's `challenge-solution/` notebook
- [ ] Show its saved outputs, or run it live. To run it live:
  - Start the remote machine with its `harbourline` shortcut
  - Run Module 2's and Put it together's terminal steps first

#### After rehearsing

- [ ] Put the room back. From the instructor module folder, delete:
  - `fund_report.py`, `report.txt`, `report_run2.txt`, `remote_report.txt`, `remote_run.log` and the folder `report/`
  - `m3_fund_report/report.txt` and `m3_fund_report/.venv/`
- [ ] In `demo/m1_break_it.py`, delete Copilot's `pd.to_datetime` line, so it fails again
- [ ] Delete the `Host harbourline` entry from `~/.ssh/config`
- [ ] Reset the remote, in `common/services/remote-machine/`:
  - `bash service.sh reset`, then `bash service.sh start`
- [ ] Did a rehearsal touch `challenge/m3_fund_report_copilot/` or `demo/m3_fund_report/`? Restore it from your clean copy
  - Then delete any `.venv/` in the challenge starter

### Learner setup check

Learners set up at the start of the day: as they arrive, they open the course folder in its dev container and start the remote, and both build while you welcome them. You check it at the end of the welcome.

| Check | Done when | If it isn't |
|---|---|---|
| Dev container | VS Code's bottom-left corner says *Dev Container: CG Core* | **Dev Containers: Reopen in Container** now; the first build takes a few minutes |
| Copilot | The Chat view answers | Sign in, or pair with a neighbour |
| The data reads | From the course folder, the setup's `python -c …` line prints `(56669, 5)` | Check they're in the dev container and the course folder, then pair them |
| The remote | `bash service.sh status` in `common/services/remote-machine/` says it's running | `bash service.sh start` now; it builds during Module 1 |

## Timeline

### Welcome {#day01-welcome}

**Section summary.** Check the setup, use the self-check to set each module's pace, and get into Module 1 fast.

#### 0:00 · 10 min · Intro/Outro — Welcome, setup check and the day

**Purpose.** Learners know what they'll make, how the day runs, and that their setup works.

**On screen.** `day01_overview.md`: the opening, outcomes, self-check and agenda.

**Instructor notes.**

- Housekeeping: timings, a break after every module, how to ask for help. Then the five outcome verbs: explain, write, refine, run, create.
- Setup as they arrive: the dev container and the remote build while you talk. Then `bash service.sh status` in `common/services/remote-machine/`; anyone stopped runs `start` now.
- Self-check, hands up: question N paces Module N. Pair each no with a yes in that module's challenge.

**Say.**

- "Three modules: a short demo, then you work. Go as far as you can in each challenge."
- "Copilot does the typing. You read every line and run the check."

**Transition.** "Here's what Jordan sends every week."

**Assessment.** —

### Module 1 — Software engineering, your first programs and Copilot {#day01-m1}

**Section summary.** Serves outcomes 1, 2 and 3 and answers session questions 1 to 3. Learners fix Jordan's report cell, review a script that hides three problems and record one check: the way of working for the whole programme.

#### 0:10 · 5 min · Instructor-led demo — The finished output

**Purpose.** Learners see the day's one artefact, Jordan's weekly table, before any code.

**On screen.** `module01-first-programs-copilot/day01_m1_demo.ipynb`: the module map · The finished output

**Instructor notes.**

- **The module map.** Open Module 1 from the table of contents. The picture: seven numbered stops, each with what it leaves behind; the last leaves a script and a check.
- **The finished output.** Run the `!` cell, a fresh Python printing 8 UK Equity rows and `Category mean: 26.83%`. No date is typed anywhere.
- **The finished output.** The chart under it: mean one-year return for seven categories, UK Gilts 3.05% to Emerging Markets Equity 55.59%. Its axis starts at zero, so the bars are honest.

**Say.**

- **The module map.** "One report all day. Every stop leaves something you could show someone."
- **The finished output.** "Read the output before any code: this is what Jordan sends every week."

**Transition.** "A notebook made that. Where does a notebook fit?"

**Assessment.** —

#### 0:15 · 5 min · Instructor-led demo — The loop round your code · Bench and card

**Purpose.** Learners see where a notebook fits in the lifecycle, and what a notebook and a script are each good for.

**On screen.** `module01-first-programs-copilot/day01_m1_demo.ipynb`: The loop round your code · Bench and card

**Instructor notes.**

- **The loop round your code.** The picture's seven stages in a loop, each with what the report leaves; a notebook is where you build and explore. Point at the yellow three: integrate, release and deploy.
- **Bench and card.** The picture first, beakers used 3, 1, 4, 2 against a numbered card, one table. Run the three cells: `11684 rows`, then the table; `>=` keeps the base date.
- **Bench and card.** The kernel holds variables, not cells: the flow, a kernel left on; each terminal run starts fresh: `NameError`. Delete `x = 1`: still 2. Restart and Run All stops; Undo, and don't Run All again.

**Say.**

- **The loop round your code.** "Programming is making it work once. Engineering is making it keep working."
- **Bench and card.** "Same table both ways. The bench is for trying things; the card is for making it again."

**Transition.** "Now an error, on purpose."

**Assessment.** —

#### 0:20 · 5 min · Instructor-led demo — One error on purpose · What makes a script reusable

**Purpose.** Learners read a traceback from the bottom up, see Copilot fix its cause, and see what makes a script reusable.

**On screen.** `module01-first-programs-copilot/day01_m1_demo.ipynb`: One error on purpose · What makes a script reusable

**Instructor notes.**

- **One error on purpose.** The picture's badges read a traceback bottom up, 1 to 3. Run `python m1_break_it.py`: `TypeError`, `Timestamp` against `datetime.date`, then your own line, 15.
- **One error on purpose.** Fix it live with the COPILOT box 'Convert the date column once', Inline chat on lines 14 and 15: Keep, save, rerun, `11684`. You undo it at the break.
- **What makes a script reusable.** The picture of `m1_fund_report_reviewed.py`, then the file: one job per function, a docstring each, `DATA` from `__file__`, the yellow guard. 'Explain build_report' only if there's time.

**Say.**

- **One error on purpose.** "Read a traceback from the bottom: what happened, which values, then where."
- **What makes a script reusable.** "Run it and it prints. Import it and it doesn't."

**Transition.** "Now the way we'll work with Copilot all programme."

**Assessment.** —

#### 0:25 · 5 min · Instructor-led demo — The four moves · From notebook to script with Copilot

**Purpose.** Learners see the four moves on a real Copilot job, with a check as the evidence.

**On screen.** `module01-first-programs-copilot/day01_m1_demo.ipynb`: The four moves · From notebook to script with Copilot

**Instructor notes.**

- **The four moves.** First, paste and send the next section's COPILOT box 'Turn the notebook into a script' (Agent, Fast). Talk through the moves and the brief while it works.
- **The four moves.** The flow, plan, generate, review, validate. Plan names the check first; a failed check goes back to the plan, not to another prompt.
- **From notebook to script with Copilot.** Review every line: Keep or Undo. The brief's five bands, each striking a guess; the yellow check, 8 rows summing to 214.63. The cells run the stand-in: `identical`, `check passed`. Then `m1_checks.md`.

**Say.**

- **The four moves.** "Plan, generate, review, validate: every time, in that order."
- **From notebook to script with Copilot.** "Done means the check passes, whoever or whatever wrote the code."

**Transition.** "That's the last stop. Here's where the report goes next."

**Assessment.** —

**Adapt.** Copilot slow: Module 1 reference, Fallbacks. A Python-fluent room: spend the time on the review. Running late: show the `x` cells' saved outputs, not Restart and Run All; leave 'Explain build_report' unsent.

#### 0:30 · 15 min · Independent or pairs work — Challenge: Fix, then review

**Purpose.** Learners read a traceback, have Copilot fix the cause, and review a script that hides three problems.

**On screen.** `module01-first-programs-copilot/day01_m1_demo.ipynb`: Where the report goes next, and the Challenge time box

**Instructor notes.**

- **Where the report goes next.** Read the closing line, then open the challenge from the Challenge time box: Q1 fixes a report cell that stops; Q2 reviews a script wrong in three places. Q3 is extra.
- Everyone runs the challenge's setup cell first: `49 share classes`.
- Name the controls that keep or reject an Inline chat change, then step back.

**Say.**

- **Where the report goes next.** "Your report, the challenge data. Start at Q1 and go as far as you can."
- "Read the traceback first: what it tells you goes into your prompt."

**Transition.** Learners carry on; no announcement needed.

**Assessment.** Outcomes 2, 3 · the fixed cell's 8 rows, My reading

#### 0:45 · 10 min · Independent or pairs work — Learners keep working

**Purpose.** Learners carry on at their own pace, with help when they ask.

**On screen.** `module01-first-programs-copilot/day01_m1_demo.ipynb`: the Challenge time box.

**Instructor notes.**

- Stay available at the back; no check-ins. Stall hints: Module 1 reference.
- Note one good My review entry for the debrief.

**Transition.** "Let's stop there, wherever you've got to."

**Assessment.** Outcomes 1 to 3 · the fixed script's check, My review, the stage table

#### 0:55 · 5 min · Feedback and discussion — Debrief

**Purpose.** Learners see a finished version and share what blocked them.

**On screen.** `module01-first-programs-copilot/challenge-solution/day01_m1_challenge.ipynb`: Q1's fixed cell, Q2's My review and check cell, and the Your turn table.

**Instructor notes.**

- Walk through Q2's three problems, then the stage table.
- Ask: "Where did you get stuck?" and "Which problems would a scheduler never report?" (Both: the dropped Inc row and the swallowed error each exit 0.)

**Say.**

- "Seven rows where there should be eight, and no error: that's the quiet wrong answer."

**Transition.** "Take your break. Keep VS Code and the terminal open."

**Assessment.** Outcomes 1 to 3 · blockers, one stage table said aloud

#### 1:00 · 10 min · Break — Before Module 2

**Instructor notes.**

- In `demo/m1_break_it.py`, undo the Inline chat fix and save.
- Open the demo's Module 2 section and a terminal in the instructor module folder. Don't connect yet: the first connection is live.
- Check any remote that wasn't running at the welcome.

**Transition.** "Your script runs from your terminal. Now it has to run on a machine you can't click on."

**Assessment.** —

### Module 2 — Command line, Linux and remote workflows {#day01-m2}

**Section summary.** Serves outcomes 2 and 4 and answers session question 4. Learners run their fixed `m1_fund_report_copilot.py` on the remote over SSH, have Copilot make the data folder a setting (`REPORT_DATA`) and prove the same 11 lines on both machines.

#### 1:10 · 5 min · Instructor-led demo — Two Linux machines, one report to match

**Purpose.** Learners see the target, Module 1's 11 lines, and the two Linux machines that must both print it.

**On screen.** `module02-command-line-remote/day01_m2_demo.ipynb`: the module map · Two Linux machines, one report to match

**Instructor notes.**

- **The module map.** The picture's seven stops. The yellow one is the proof: one table on two machines, and a silent `diff`.
- **Two Linux machines, one report to match.** The picture, the dev container and the remote, two Linux systems on one laptop sharing its kernel, SSH on port 2222 between. The remote is `jordan` on `harbourline-remote`.
- **Two Linux machines, one report to match.** Run the two cells: the target is ` 11 747 report.txt`; here you're `vscode` on Python 3.13.16.

**Say.**

- **The module map.** "The same report, now on a machine you can't click on."
- **Two Linux machines, one report to match.** "Read the prompt before you type. It tells you which machine you're on."

**Transition.** "To get in, the remote needs your key, and you need to trust it."

**Assessment.** —

#### 1:15 · 5 min · Instructor-led demo — A key, a trusted host and a shortcut · Same path, two machines

**Purpose.** Learners see a first SSH connection, a Terminal chat command read before it runs, and a path that fails on the other machine.

**On screen.** `module02-command-line-remote/day01_m2_demo.ipynb`: A key, a trusted host and a shortcut · Same path, two machines

**Instructor notes.**

- **A key, a trusted host and a shortcut.** The picture, SSH checks both ways, the remote's host key by you, yours by it. Do the box 'Connect once, and trust the remote'; type `yes` live.
- **A key, a trusted host and a shortcut.** The live beat: the COPILOT box 'Add an SSH shortcut for the remote', Terminal chat. Insert, then check `>>` and the four settings against `m2_ssh_config.txt`, press Enter, then the two cells: `ok`.
- **Same path, two machines.** The picture, four folders up lands in the course folder here, `/home/jordan` there. The run: `exit code: 1`, an empty `remote_report.txt`, a 33-line log ending `FileNotFoundError`.

**Say.**

- **A key, a trusted host and a shortcut.** "Insert puts the command at your prompt, so you read it before it runs."
- **Same path, two machines.** "Same path, different machine, different answer."

**Transition.** "So where the data lives can't be written into the script."

**Assessment.** —

**Adapt.** An SSH-fluent room: spend the time on `>` against `>>`. Running late: run Same path's cells without pausing, as 1:20 needs their remote folder; leave the optional boxes unsent.

#### 1:20 · 5 min · Instructor-led demo — Where the data lives is a setting · Three streams, one table on two machines

**Purpose.** Learners see the data folder become a setting, and one table proved on two machines by its exit code, log and `diff`.

**On screen.** `module02-command-line-remote/day01_m2_demo.ipynb`: Where the data lives is a setting · Three streams, one table on two machines

**Instructor notes.**

- **Where the data lives is a setting.** The flow, `REPORT_DATA` if set, four folders up if not, the same 11 lines either way. The cell: `identical: the default`, then `FileNotFoundError` for `/nowhere`, on purpose.
- **Where the data lives is a setting.** Send the COPILOT box 'Read the data folder from a setting' only if there's time, the chip on `demo/fund_report.py`, not `m3_fund_report/`'s.
- **Three streams, one table on two machines.** The picture's 0 in, 1 out, 2 errors. Exit 0, empty log, `identical`; then `;` hides `remote_exit=1` as `ssh_exit=0`. Catalyst's CONT-BASE-003 on screen: strict mode would stop at the failure.

**Say.**

- **Where the data lives is a setting.** "Where the data lives is a fact about the machine, so the machine says it."
- **Three streams, one table on two machines.** "Exit code first, then the log, then the report."

**Transition.** "It runs over there. So who may change what?"

**Assessment.** —

#### 1:25 · 5 min · Instructor-led demo — Who may do what · A job that keeps running

**Purpose.** Learners see who may change what on the remote, and how a job outlives a dropped connection.

**On screen.** `module02-command-line-remote/day01_m2_demo.ipynb`: Who may do what · A job that keeps running

**Instructor notes.**

- **Who may do what.** The picture, an `ls -l` line's ten characters, `r` 4, `w` 2, `x` 1. Run the cell: `jordan` has no `sudo`; `/data` says `Read-only file system`. Catalyst's CONT-BASE-002 is on screen.
- **A job that keeps running.** The flow, `exit` leaves background jobs running; a dropped connection's hang-up stops every job not started with `nohup`.
- **A job that keeps running.** Run the box 'Run the report in the background, then stop it' only if you're ahead of time: Q3 does it. Send 'Explain one part of the command' after it, if asked.

**Say.**

- **Who may do what.** "A report should never be able to change its data."
- **A job that keeps running.** "`nohup` keeps a job running when the connection drops."

**Transition.** "That's the last stop. Here's where the report goes next."

**Assessment.** —

#### 1:30 · 15 min · Independent or pairs work — Challenge: Run it on the remote

**Purpose.** Learners run their own report over SSH, read the failure, have Copilot make the data folder a setting, and prove one table on two machines.

**On screen.** `module02-command-line-remote/day01_m2_demo.ipynb`: Where the report goes next, and the Challenge time box

**Instructor notes.**

- **Where the report goes next.** Read the closing line (nothing written down says which versions it needs), then the Challenge time box: Q1 makes your report work on the remote; Q2 adds a shortcut and a look around.
- A 10-line baseline means Module 1's fixes aren't in: the COPILOT box 'Catch up: the Module 1 fixes' first.
- Pair the noes to self-check question 2 with a yes, the newcomer driving.

**Say.**

- **Where the report goes next.** "Your Global Equity report, on your remote. Start at Q1 and go as far as you can."
- "Commands from the boxes, changes from Copilot, the checking from you."

**Transition.** Learners carry on; no announcement needed.

**Assessment.** Outcomes 2 to 4 · remote exit codes, the `REPORT_DATA` change, `identical`

#### 1:45 · 10 min · Independent or pairs work — Learners keep working

**Purpose.** Learners carry on at their own pace, with help when they ask.

**On screen.** `module02-command-line-remote/day01_m2_demo.ipynb`: the Challenge time box.

**Instructor notes.**

- Stay available; no check-ins. Connection fixes: Module 2 reference.
- Remote commands typed in the dev container? The prompt settles it.

**Transition.** "Let's stop there, wherever you've got to."

**Assessment.** Outcome 4 · My checks: the remote run, the shortcut's `ok`, the corrections

#### 1:55 · 5 min · Feedback and discussion — Debrief

**Purpose.** Learners see a finished version and share what blocked them.

**On screen.** `module02-command-line-remote/challenge-solution/day01_m2_challenge.ipynb`: Q1's My checks (the remote run and its check cell), then the Your turn table.

**Instructor notes.**

- Walk through Q1's two runs: exit code 1 and the log's last line, then exit code 0 and `identical`.
- Ask: "Where did the connection stop you?" and "Which two explanations were wrong?" (Rows 3 and 4: Module 2 reference.)

**Say.**

- "Exit code 1 first, then `identical`: the failure told you what to fix."
- "Every explanation gets checked against what the machine does, whoever wrote it."

**Transition.** "Take your break. Module 3 starts from this script."

**Assessment.** Outcomes 2, 4 · blockers, the two corrections said aloud

#### 2:00 · 10 min · Break — Before Module 3

**Instructor notes.**

- Open the demo's Module 3 section; check `demo/report/` doesn't exist.
- Run the first cell of What a colleague gets now: the split's check needs `m3_fund_report/report.txt`.
- In the Chat view (Agent, Fast, `#m2_fund_report.py`), paste the prompt from the box 'Split the script into a package', under From one script to a package, ready to send.

**Transition.** "Your script runs on two machines, but nothing says which library versions it needs."

**Assessment.** —

### Module 3 — Python packages, dependencies and reusable modules {#day01-m3}

**Section summary.** Serves outcome 5 and answers session question 5. Learners install their report, split into a package, like a colleague, pin what its `requirements.txt` left out and prove it in a fresh `.venv`, with venvs in the terminal and notebooks on the dev container's Python.

#### 2:10 · 5 min · Instructor-led demo — What a colleague gets

**Purpose.** Learners see what a colleague needs to rerun the report: the code as a package, a pinned list and a README.

**On screen.** `module03-packages-dependencies/day01_m3_demo.ipynb`: the module map · What a colleague gets

**Instructor notes.**

- **The module map.** First, press Send on the split prompt you pasted in the break, so it works while you talk. The picture's seven stops, each leaving something to hand over, and one colleague's question behind them all.
- **What a colleague gets.** The picture, a package, a pinned list and a README; `.gitignore` keeps `.venv/` out. Run the two cells: the file list, then `identical: the split changed nothing`.

**Say.**

- **The module map.** "One question all module: a colleague asks, how do I run this?"
- **What a colleague gets.** "The `.venv` never travels. Each machine builds its own from the list."

**Transition.** "Copilot's split should be back. Let's review it."

**Assessment.** —

#### 2:15 · 5 min · Instructor-led demo — From one script to a package · Where import looks

**Purpose.** Learners see a split reviewed against what its brief ruled out, and the order import searches in.

**On screen.** `module03-packages-dependencies/day01_m3_demo.ipynb`: From one script to a package · Where import looks

**Instructor notes.**

- **From one script to a package.** The picture, three functions move to `harbourline/returns.py`; settings, `main()` and the guard stay. Then review Copilot's `report/` against the review cell's three points (Catalyst's RFD 0008).
- **From one script to a package.** Run its `diff` for `identical`, Keep or Undo; `report/` is a throwaway. Open `m3_fund_report/`, which the cells run: one import line, a docstring-only `__init__.py`. The cell prints `main`'s docstring: imported, not run.
- **Where import looks.** The picture's shelves, top down, first match wins. Predict, then run: by its path, `Category mean: 26.83%`; a bare import, `ModuleNotFoundError`. Its Explain box only if a minute is spare.

**Say.**

- **From one script to a package.** "A split moves code. It never changes what the code does."
- **Where import looks.** "`import` takes the first match on `sys.path`, from the top down."

**Transition.** "Now give the project a Python of its own."

**Assessment.** —

#### 2:20 · 5 min · Instructor-led demo — A venv of its own, and the notebook's Python · Asked for two, got seven

**Purpose.** Learners see a venv isolate one project while the notebook stays on its own Python, and two packages bring seven.

**On screen.** `module03-packages-dependencies/day01_m3_demo.ipynb`: A venv of its own, and the notebook's Python · Asked for two, got seven

**Instructor notes.**

- **A venv of its own, and the notebook's Python.** The picture's toolboxes, one per project. The cell ends `No module named 'pandas'`: empty, on purpose. Do the box 'Activate it in the terminal'; decline VS Code's new-environment offer.
- **A venv of its own, and the notebook's Python.** The second card: two Pythons side by side. A `!` line uses the notebook's, `/usr/local/bin/python`, so cells call the venv's by its path. `No module named 'ipykernel'` is why the notebook stays put.
- **Asked for two, got seven.** The picture, two packages asked for, seven in the receipt, each with who asked. Run the install: numpy is the newest that fits `numpy>=1.26.0`.

**Say.**

- **A venv of its own, and the notebook's Python.** "A container isolates a machine. A venv isolates one project inside it."
- **Asked for two, got seven.** "Asked for two, got seven. Pin all seven."

**Transition.** "Seven packages. Where do you write them down from?"

**Assessment.** —

**Adapt.** Running late: show the install, freeze and fresh-venv cells' saved outputs.

#### 2:25 · 5 min · Instructor-led demo — Pin it from a clean venv · A fresh .venv proves it

**Purpose.** Learners see where to freeze, and a fresh venv built from the file alone print the same table.

**On screen.** `module03-packages-dependencies/day01_m3_demo.ipynb`: Pin it from a clean venv · A fresh .venv proves it

**Instructor notes.**

- **Pin it from a clean venv.** The card, `pip freeze` in the dev container's own Python lists 39 lines, in the report's venv the seven it needs: freeze there.
- **A fresh .venv proves it.** The flow, empty venv, install from the file, `pip check`, run, `diff`. Run the cell: `No broken requirements found.`, then `identical` and `same-set`.
- **A fresh .venv proves it.** Open the README and `.gitignore`: Repository, Environment and Run; Python 3.13, because numpy 2.5.4 needs 3.12 or later; the `REPORT_DATA` line.

**Say.**

- **Pin it from a clean venv.** "Freeze where only the project lives, and the file says exactly what it needs."
- **A fresh .venv proves it.** "The proof is a venv built from the file alone."

**Transition.** "That's the last stop. Here's where the report goes next."

**Assessment.** —

#### 2:30 · 15 min · Independent or pairs work — Challenge: Install it like a colleague

**Purpose.** Learners find what `requirements.txt` left out, have Copilot pin it, and prove it in a fresh `.venv`.

**On screen.** `module03-packages-dependencies/day01_m3_demo.ipynb`: Where the report goes next, and the Challenge time box

**Instructor notes.**

- **Where the report goes next.** Read the closing line: a machine nobody clicks on builds its own environment from `requirements.txt`. Then open the challenge from the Challenge time box, with `challenge/m3_fund_report_copilot/` open beside it.
- Brief it: Q1 installs the package like a colleague and fixes the pins, done at `identical`, then `same-set`, from a seven-line `requirements.txt`; Q2 reviews the split and adds a README.
- The pin prompt goes in Terminal chat with the venv active: Insert, to read it before it runs.

**Say.**

- **Where the report goes next.** "Your Global Equity report, split into a package. Start at Q1 and go as far as you can."
- "It works in the dev container. That's the trap."

**Transition.** Learners carry on; no announcement needed.

**Assessment.** Outcome 5 · Q1's `identical`, `same-set`, a seven-line `requirements.txt`

#### 2:45 · 10 min · Independent or pairs work — Learners keep working

**Purpose.** Learners carry on at their own pace, with help when they ask.

**On screen.** `module03-packages-dependencies/day01_m3_demo.ipynb`: the Challenge time box.

**Instructor notes.**

- Stay available; no check-ins. A 39-line `requirements.txt` means the venv wasn't active: Module 3 reference.
- Attaching files for Copilot? Check the chip says `m3_fund_report_copilot/`.
- Short of time? The two Explain prompts are optional: skip them unless stuck.

**Transition.** "Let's stop there, wherever you've got to."

**Assessment.** Outcome 5 · Q2's check cell and README, the Your turn table

#### 2:55 · 5 min · Feedback and discussion — Debrief

**Purpose.** Learners see a finished version and share what blocked them.

**On screen.** `module03-packages-dependencies/challenge-solution/day01_m3_challenge.ipynb`: Q1's failed install, My reading and check cell, then Q2's check cell.

**Instructor notes.**

- Walk through Q1: the `ImportError`, pyarrow at 26.0.0, then `identical` and `same-set`.
- Ask: "Where did the venv catch you out?" and "A colleague has your folder: what do they type?" (A venv, `pip install -r requirements.txt`, `REPORT_DATA`, the run.)

**Say.**

- "A 39-line `requirements.txt` only means you froze outside the venv: common, and quick to fix."

**Transition.** "Take your break. After it, you choose what to carry on with."

**Assessment.** Outcome 5 · blockers, a colleague's steps said aloud

#### 3:00 · 10 min · Break — Before open challenge time

**Instructor notes.**

- Check for stopped remotes: `bash service.sh status`, then `start`.
- The index check was slow? Have the wheels fallback ready (its reference).

**Transition.** "Pick up where you left off in any module. If you finish the module challenges early, ship your report."

**Assessment.** —

### Open challenge time {#day01-open}

**Section summary.** Serves outcomes 1 to 5. Everyone carries on with any module challenge, and fast finishers take Put it together, Ship your report, the optional stretch.

#### 3:10 · 20 min · Independent or pairs work — Carry on, or ship your report

**Purpose.** Learners finish what matters most to them; fast finishers ship the package.

**On screen.** any module's `challenge/day01_mN_challenge.ipynb`, or *Put it together — Ship your report*.

**Instructor notes.**

- Brief it: carry on with any module; if you finish the module challenges early, Put it together ships your package. Nobody has to reach it.
- Shippers open a new terminal in their Put it together folder, as Put it together's first box says. Module 3 unfinished? Ship the catch-up, `together_fund_report/`.
- Stay available. Stall hints: its reference. Refused at `./run_report.sh` in Q2? The COPILOT box 'Let only the owner run it'.

**Say.**

- "Your choice now: finish a module, or ship it."
- "Shipped means the remote prints your laptop's table, from a `.venv` built from your pins."

**Transition.** Learners carry on; no announcement needed.

**Assessment.** Outcomes 2 to 5 · check cells; Put it together's `same-files`, `same-set`, `identical`

#### 3:30 · 15 min · Independent or pairs work — Learners keep working

**Purpose.** Learners carry on at their own pace, with help when they ask.

**On screen.** `module01-first-programs-copilot/day01_m1_challenge.ipynb`: the *How to use this notebook* badge table.

**Instructor notes.**

- Stay available; no check-ins. Remote installs crawl? Switch shippers to the wheels fallback.
- Ask two learners to keep something they finished on screen for the wrap-up.

**Transition.** "Let's stop there, wherever you've got to."

**Assessment.** Outcomes 1 to 5 · finished check cells, the stage table

#### 3:45 · 5 min · Feedback and discussion — Closing debrief

**Purpose.** Learners share what blocked them and anything they shipped.

**On screen.** `module99-put-it-together/challenge-solution/day01_together_challenge.ipynb`: Q1's check cell (`same-set`, `identical`).

**Instructor notes.**

- Walk through the check cell: the job ran `.venv/bin/python`, and `same-set` shows the environment came from the pins, not the remote's own `python3`.
- Ask: "What's still blocking you?" and "Who shipped? What did the remote print?"

**Say.**

- "Wherever you stopped, you've got something that runs and a check that says so."

**Transition.** "Let's put what you made against what you came for."

**Assessment.** Outcomes 1, 5 · blockers, anything shipped

### Wrap-up {#day01-wrapup}

**Section summary.** Back to the outcomes and the session questions, then the next session and the feedback form.

#### 3:50 · 10 min · Intro/Outro — Evidence, next session and feedback

**Purpose.** Learners see where they showed each outcome, know what comes next, and give feedback.

**On screen.** `day01_overview.md`: the five session questions.

**Instructor notes.**

- Two learners show what they kept. Read the five outcome verbs, a hand for each, and ask which session question they can now answer.
- Next: Session 02, *Testing with pytest, Git and pull requests, containers and CI*, picks up this same report.
- Ask for the feedback form before they leave.

**Say.**

- "Same output on two machines is evidence. 'It works on my laptop' isn't."
- "Your `requirements.txt` is the handover: anyone can build the same environment from it."

**Assessment.** Outcomes 1 to 5 · a hand per outcome, a question answered with something made

## Module 1 reference {#day01-m1-reference}

### What a finished challenge looks like

- **Q1.** Copilot changes `ongoing_charge` to `ongoing_charge_pct` and nothing else; the rerun prints 8 Global Equity rows, best first, from HLP007-I-ACC at 52.68.
- **Q2.** Three problems found: a data path read from the terminal's folder, a filter that drops the Inc class, an `except` that hides errors. After the fixes: `check passed: 8 rows, sum 325.75, same table as Q1`.
- **Your turn.** Build, Build, Test, Test. Integrate, Release, Deploy and Operate have nothing yet.
- **Q3.** `"UK Equity"` prints 9 rows and `Category mean: 27.95%`; `"UK equity"` stops with `error: unknown category` and exit code 2.

### The likeliest stalls

| Stall | Hint |
|---|---|
| Asking Copilot before reading the traceback | "Last line, the name, your own line: write those down first, then put them in your prompt." |
| Q2 finds one problem, not three | "Count rows against your Q1 table, then ask what the script does when the data isn't there." |
| Ctrl+I opens the Chat view, not Inline chat | "That file has Copilot edits waiting: Keep or Undo each, then Ctrl+I (Cmd+I on a Mac) again." |

### Fallbacks

| Problem | Do this |
|---|---|
| Copilot is slow or not signed in, in the demo | In the instructor module folder, `cp m1_fund_report_reviewed.py fund_report.py`, say so, and review and check that file |
| A learner has no Copilot | Pair them with a neighbour; they review |
| The notebook kernel won't start | Run the scripts from the terminal: nothing in Module 1 needs Jupyter to make its point |

### Facts to have ready

- **The demo's report.** UK Equity, demo data, to 2026-09-30: 8 rows summing to 214.63, `Category mean: 26.83%`. With `>` for `>=` the sum is 222.78.
- **The error on purpose.** `m1_break_it.py` stops with `TypeError: Cannot compare Timestamp with datetime.date`; fixed, it prints `11684`.
- **The check rounds.** It checks the 2-dp column: unrounded, the challenge's returns sum to 325.74.
- **CI/CD, if asked.** Harness is CG's CI/CD platform: name it, don't demo it.

## Module 2 reference {#day01-m2-reference}

### What a finished challenge looks like

- **Q1.** Baseline ` 11 751 report.txt`. First remote run: exit code 1, the log ending `No such file or directory: '/home/jordan/data/challenge/funds.csv'`. After Copilot's `REPORT_DATA` change: exit code 0, an empty log, `identical`.
- **Q2.** The shortcut came by Insert with `>>`, and its check prints `ok`. On the remote: `-rw-r--r--` for files that arrived by `scp`, `-rw-------` after `chmod 600`, and `Read-only file system` from `/data`.
- **Your turn.** Rows 3 and 4 are wrong: nothing quotes the redirections, so both files are made in the dev container; and `NAME=value` sets it for one command only.
- **Q3.** The report 60 times, 5 seconds apart, under `nohup`: its PID and parent, then `[1]+  Terminated` after `kill %1`. `No such process` means it had finished: start it again and stop it sooner.

### The likeliest stalls

| Stall | Hint |
|---|---|
| The remote isn't reachable: exit code 255 | "`bash service.sh status`. After a dev container rebuild: `stop`, then `start`. A changed host key: `reset`, then `start`, and the first terminal box again." |
| The first remote run works, from a 10-line baseline | "Count your baseline: 10 lines, not 11? Use the Catch up box, then run it again. It worked by luck, not design." |
| Remote commands typed in the dev container | "Read the prompt: `jordan@harbourline-remote`? Log in first." |

### Fallbacks

| Problem | Do this |
|---|---|
| Copilot isn't answering, in the demo | The shortcut: in the instructor module folder, `cat m2_ssh_config.txt >> ~/.ssh/config`. The setting: skip the send; the cells run `m2_fund_report.py`. Say so, and review each as if Copilot wrote it |
| A learner's remote won't start | Pair them with a neighbour whose remote runs; the README's troubleshooting table is for the break |
| A notebook `ssh` cell shows the trust question and keeps running | Interrupt it, connect once in VS Code's terminal, then rerun the cell |

### Facts to have ready

- **Exit codes.** 0 worked; 1 Python stopped on an error; 127 command not found; 255 an SSH or `scp` failure.
- **Ports.** `ssh -p 2222`, but `scp -P 2222`. From the dev container the remote is `host.docker.internal`; `localhost` is the dev container itself.
- **The remote forgets.** After `bash service.sh stop` or `reset`, then `start`, the home folder is empty and the host key is new. A remote that stopped because Docker quit keeps its files: if SSH connects without a warning, carry on.

## Module 3 reference {#day01-m3-reference}

### What a finished challenge looks like

- **Q1.** The venv from the one-line file stops with `ImportError: Unable to find a usable engine`. Pinned from a clean venv: seven lines, pyarrow 26.0.0 among them, and the check cell prints `identical`, then `same-set`.
- **Q2.** Three problems: a `sys.path` line, a relative import, a facade in `__init__.py`. The check cell prints `clean: no sys.path change, no relative import`, `identical`, then the `from harbourline.returns import …` line; the README has Repository, Environment and Run.
- **Your turn.** `os` from the standard library, `harbourline` from the project folder, pandas and pyarrow from the venv, and a notebook's pandas from the dev container's own packages.
- **Q3.** In a colleague's folder the run stops with `'/data/challenge/funds.csv'` until the README sets `REPORT_DATA` to the data folder's absolute path; then `identical`.

### The likeliest stalls

| Stall | Hint |
|---|---|
| The venv isn't active at the pin step: `requirements.txt` has 39 lines | "Does your prompt show `(.venv)`? Put the file back with `echo "pandas==2.3.3" > requirements.txt`, then `python -m venv --clear .venv` and run the install box again." |
| Two problems in My review, not three | "Read the import line in `fund_report.py`. Which file defines `build_report`?" |
| Changes landed outside `m3_fund_report_copilot/` | "Check the attachment chip: pick the files in `m3_fund_report_copilot/`. Undo, then send again." |

### Fallbacks

| Problem | Do this |
|---|---|
| Copilot is slow in the demo's split | Open `demo/m3_fund_report/` as if Copilot wrote it, say so, and review and check it there |
| Installs stop with a connection error | Walk the room through the completed challenge's Q1, then move learners on to Q2's review and the Your turn |
| VS Code moved the notebook or terminal to a venv | **Python: Select Interpreter**, then `/usr/local/bin/python`, and open a new terminal |

### Facts to have ready

- **The seven.** numpy 2.5.4, pandas 2.3.3, pyarrow 26.0.0, python-dateutil 2.9.0.post0, pytz 2026.5, six 1.17.0, tzdata 2026.5. Nothing asks for pyarrow, so `pip install pandas` never brings it. A newer numpy on the index changes that one line.
- **Freeze.** 39 lines in the dev container's own Python, seven in the project's venv.
- **Two Pythons.** The notebook's kernel is `/usr/local/bin/python`, Python 3.13.16; a `!` line always uses it, whatever the terminal has activated.

## Put it together reference {#day01-together-reference}

### What a finished challenge looks like

- **Q1.** The package copied without `.venv` and `__pycache__` (`same-files`), a `.venv` built on the remote (`same-set`, `No broken requirements found.`), the job in the background with `exit code: 0` and `identical`. The check cell prints `same-set`, then `identical`.
- **Q2.** `run_report.sh` reviewed against five points; `Permission denied` (exit code 126) until the COPILOT box 'Let only the owner run it' gives `-rwxr--r--`; then `exit code: 0`, `identical` and a dated log line; the README's Run on the remote section.
- **Your turn.** Test, Release, Deploy and Operate now have something. Integrate still doesn't.
- **Q3.** One `ssh` line runs the job: `exit code: 0`. The check cell prints `identical`, then `exit code: 1` for a wrong setting.

### The likeliest stalls

| Stall | Hint |
|---|---|
| `Could not resolve hostname harbourline` | "No shortcut yet: run the block under *Could not resolve hostname harbourline?* in the first terminal box, once. It ends with `ok`." |
| The baseline fails, or the remote's job ends `ImportError` | "Prompt shows `(.venv)`, or a folder in `/tmp/colleague`? Open a new terminal in the module folder, as the first box says. One-line `requirements.txt`? `exit`, `ssh harbourline "rm -rf fund-report"`, then ship the catch-up folder." |
| The copy uses `rsync`, or brings `.venv` across | "Which tools does the remote have, and what did the brief leave out? After Task 1.3, the remote's own `.venv` is fine." |

### Fallbacks

| Problem | Do this |
|---|---|
| The remote can't reach the package index, or downloads crawl | The wheels fallback. In the dev container's project folder: `pip download -r requirements.txt -d wheels` (cached); copy as usual; on the remote, `python3 -m venv .venv`, `.venv/bin/pip install --no-index --find-links wheels -r requirements.txt` |
| A changed host key | `bash service.sh reset`, then `start`, connect and type `yes`, then copy again: the remote's files are gone |
| A learner's remote won't start | Pair them with a neighbour whose remote runs |

### Facts to have ready

- **On the remote.** The package in `~/fund-report/`, the log in `/var/log/harbourline/global-equity.log`. The remote has `tar` and `nohup`, but not `rsync`, `sudo` or an editor.
- **The install.** About 80 MB per learner, all at once; a 315 MB `.venv`. After the wheels fallback, delete `wheels/` on both machines.
- **Why `python3` would also work.** The remote's own Python has the same three packages. Only `.venv/bin/python` and `same-set` show the pinned environment did the work.

## Question bank

### Module 1

**Key questions.**

1. What is software engineering, and what are the stages of the software development lifecycle?
2. How do notebooks and scripts differ, and when is each useful?
3. How does Python execute code in Jupyter and VS Code?
4. Which Python syntax and control structures are needed for the exemplar task?
5. How do I debug, organise and document code so it can be reused?
6. Where do integration, release and deployment fit into the lifecycle?
7. How do I use CG's VS Code and Copilot workflow for engineering tasks: context, prompts, planning a change, reviewing generated code, validating with deterministic checks, retaining responsibility for correctness?

| Ask after | Question | Answers (correct in bold) |
|---|---|---|
| 0:15 · The loop round your code · Bench and card | Where in the lifecycle does a notebook do its work? | Test · **Build** · Deploy |
| 0:20 · One error on purpose · What makes a script reusable | Which line of a traceback do you read first? | The first line · **The last line** · The longest line |
| 0:55 · Debrief | What shows a change to the script is done? | A summary of the change · **A check you ran that passes** · The code looking right |

### Module 2

**Key questions.**

1. What is Linux, and why does it matter in software engineering, data engineering and data science?
2. How do I navigate a filesystem and run commands or programmes?
3. What are standard input and standard output, and how do I capture logs and output artefacts?
4. What is root, and how do I inspect and manage permissions?
5. How do I inspect processes and use shell utilities for the task?
6. What is SSH, and how do I run commands on a remote machine?

| Ask after | Question | Answers (correct in bold) |
|---|---|---|
| 1:15 · A key, a trusted host and a shortcut · Same path, two machines | What does SSH's first-connection question ask? | For your password · **Whether to trust the remote's host key** · Whether to make a key pair |
| 1:15 · A key, a trusted host and a shortcut · Same path, two machines | The script finds its data from its own file, yet fails on the remote. Why? | The remote has no pandas · **Three folders up from it, over there, is the home folder** · The data is read-only |
| 1:55 · Debrief | `ssh harbourline "python3 report.py; echo done"` exits with 0. Did the report work? | Yes · No · **You can't tell: 0 is `echo`'s exit code** |

### Module 3

**Key questions.**

1. What are environments, packages and modules, and how do Python imports work?
2. Why isolate dependencies in a virtual environment?
3. How do I install and manage dependencies with `pip` and, where appropriate, `uv`?
4. How do I pin dependencies and recreate a working environment?
5. How do I structure reusable functions as a module or package?

| Ask after | Question | Answers (correct in bold) |
|---|---|---|
| 2:20 · A venv of its own, and the notebook's Python · Asked for two, got seven | Your terminal has `.venv` active. Which Python does a `!python` line in the notebook use? | The venv's · **The notebook's own** · Whichever ran last |
| 2:25 · Pin it from a clean venv · A fresh .venv proves it | Where do you run `pip freeze` to write `requirements.txt`? | The dev container's own Python · **A venv that holds only what the project installed** · Any terminal |
| 3:45 · Closing debrief | The remote's own `python3` prints the same table. What shows your pinned environment ran the job? | Nothing · **The job named `.venv/bin/python`, and `same-set` matched** · The README |

## Support and stretch

### Module 1

**Support.** Pair newcomers with someone confident, the newcomer as reviewer. Anyone new to notebooks runs the demo's cells one at a time with Shift+Enter.

**Stretch.** Take the bench and card quickly and spend the time on the review: does every change Copilot made trace back to the brief? Early finishers take Q3.

### Module 2

**Support.** One habit: read the prompt before every command, and run `whoami` when in doubt. Newcomers stay on Q1, where every command is in a terminal box.

**Stretch.** Ask what `set -euo pipefail` would change in the demo's hidden failure. Early finishers take Q3, then the demo's background-job box with the COPILOT box 'Explain one part of the command'.

### Module 3

**Support.** One habit: `which python` before every run. Anyone lost in activation calls `.venv/bin/python` and `.venv/bin/python -m pip` by their paths instead.

**Stretch.** Early finishers take Q3, then the Python-version dry run in the Module 3 handbook. Then compare two installers: pip comes inside every venv, and uv is a separate install that resolves and installs faster. Install uv into a scratch venv of its own, rebuild a copy of the project with `uv pip install -r requirements.txt` and compare the freeze: the same seven.

## FAQs

**Do I have to finish every question?**

No. Go as far as you can, starting at Q1. Q3 and Put it together are there if you have time.

**Why does SSH say the remote host identification has changed?**

The training remote makes a new host key each time it's reset. In `common/services/remote-machine/`, `bash service.sh reset`, then `start`, then connect and copy your files again. On a real server, find out why before you remove the old key.

**Can I change the script on the remote?**

No: the remote has no editor, by design. Change it in the dev container, with Copilot, and copy it across. One reviewed version, and the remote runs a copy.

**Which Copilot mode should I use?**

Each suits a different job: Ask for questions and explanations, Plan to work out a change before any file moves, Agent to change files and run commands. A Fast model suits quick edits and questions, a Reasoning model multi-step work.

**Isn't the dev container already isolated? Why a venv?**

The container isolates a machine where everything shares one Python. A venv isolates one project, so its packages can be listed and rebuilt on their own.

**Can I use uv, conda or poetry?**

The ideas carry over to all of them: one environment per project, every version pinned, a fresh install as the proof. Each is good for something different:

- **pip**, the tool this session uses, comes inside every venv.
- **uv** resolves and installs faster, and reads the same `requirements.txt` with `uv pip`.
- **poetry** keeps dependencies, packaging and a lock file in one `pyproject.toml`.
- **conda** also installs Python itself and non-Python libraries, which suits much data science work.

**Why pin numpy when the report never imports it?**

pandas needs it, and an unpinned numpy is whatever is newest on the day.

**Why not copy the `.venv` with the folder, or put it in Git?**

It's big and records its own absolute path, so a copy breaks or quietly uses the original. `requirements.txt` travels, and each machine builds its own `.venv`.

## Activity types

| Activity type | What it means here |
|---|---|
| Intro/Outro | Opening or closing the session: welcome, housekeeping, outcomes, agenda; the session questions, the feedback form, the next session |
| Explain | The instructor teaches an idea from a visual, briefly |
| Instructor-led demo | The instructor runs the demo live, code, terminal or Copilot, while learners watch or follow |
| Questioning | Questions to the room, by hands up or a poll: the self-check, a prediction |
| Independent or pairs work | Learners work through the challenge at their own pace, alone or in pairs, as far as they get; the instructor stays available |
| Feedback and discussion | A short debrief: walk through the solution, or ask questions that surface blockers |
| Break | A rest. The instructor checks setups and collects questions |
