# ‹The day's title, the programme overview's, word for word›

[Unit ‹N› · ‹unit title› › Day ‹NN› — lesson plan for instructors]{.breadcrumb}

Timings are a guide: adapt them to the room. Confirm the start and end times, the breaks and the timezone before you deliver.

<!-- The CG Core lesson plan (user, 2026-10-16), adapted from Decoded's lesson plan template. Format: .claude/skills/lesson-plan/references/format.md. Teach from the back of the room: rows stay short, learners spend the time in the challenges. HTML comments like this one never reach the Word document. -->

## Overview

‹Where the session sits: its unit, what it builds on, and the shift it makes.›

‹The thread: what Jordan Mensah (they/them) at Harbourline Asset Management has at the start, and what each module does to it.›

The session's themes:

- **Module 1 — ‹title›.** ‹What it adds, in a line.›
- **Module 2 — ‹title›.** ‹What it adds.›
- **Module 3 — ‹title›.** ‹What it adds.›
- **Open challenge time (optional).** Carry on with any module challenge, or try Put it together, ‹task title›, end to end: ‹what it ships, in a line›.

‹What learners leave with: the artefacts, and what makes them good.›

‹Who it's for: the audience, and what isn't assumed.›

## Objectives and outcomes

| # | Learning objective | By the end of the session, learners can… | Module | Evidence |
|---|---|---|---|---|
| 1 | ‹topic, as a short phrase› | **‹Verb›** ‹the outcome, word for word from the overview› | M1 | ‹what learners make or say that shows it› |
| 2 | ‹topic› | **‹Verb›** ‹outcome› | M1, M2 | ‹evidence› |
| 3 | ‹topic› | **‹Verb›** ‹outcome› | M3 | ‹evidence› |

Module 1 answers session questions ‹1 to 3›, Module 2 question ‹4› and Module 3 question ‹5›.

## Curriculum map

| Unit | Session | Modules |
|---|---|---|
| 1 · ‹unit title› | **S01 · ‹title› (this session)** | M1 ‹title› · M2 ‹title› · M3 ‹title› |
|  | S02 · ‹title› | M1 ‹title› · M2 ‹title› · M3 ‹title› |
| 2 · ‹unit title› | S03 · ‹title› | M1 ‹title› · M2 ‹title› · M3 ‹title› |

<!-- Every session of the programme, from internal-programme-overview.md. This session's row in bold, ending "(this session)". -->

## Before the session

### Materials

Your files are in the session's `instructor/` folder and the learners' in its `learner/` folder, one folder per module on each side, and each path starts there (`moduleNN-<slug>/` with the demo notebook, its files and `challenge-solution/`; `moduleNN-<slug>/` with the challenge notebook, its files and the handbook); the dev container is at the top of the course folder, the data and services in `common/`.

| File | For | Use it for |
|---|---|---|
| `module00-overview/dayNN_overview.pdf`, each module folder's handbook (learner side) | Learners | The welcome: outcomes, self-check, agenda. The module handbooks hold the concepts in depth |
| `moduleNN-<slug>/dayNN_mN_demo.ipynb` (one per module) | You (instructors only) | ‹…› |
| `moduleNN-<slug>/dayNN_mN_challenge.ipynb` (one per module; Put it together's in its own module folder) | Learners | ‹…› |
| `moduleNN-<slug>/challenge-solution/dayNN_mN_challenge.ipynb` | You | Each module's challenge done in full, to walk through in the debriefs. It sits in `instructor/moduleNN-<slug>/`, beside the demo, and runs as it is. Never hand it out |
| `instructor/` | You | This lesson plan in Word, and review PDFs: the demo, the challenge with every solution open, and the completed challenge (`dayNN_mN_challenge_solution.pdf`). Never hand them out |
| `.devcontainer/`, `common/services/‹name›/` | Everyone | The dev container, whose terminal everybody uses, and ‹the session's services›. Each service's `README.md` has commands and fixes; your notes for it are `unit00-programme/instructor/services/‹name›/INSTRUCTOR.md` |
| `common/data/demo/`, `common/data/challenge/` | Everyone | The demo data (HLF, 46 share classes) and the challenge data (HLP, 49) |

### Your checklist

<!-- Short items of one line each; any command or file list goes in an indented sub-bullet under its item. -->

#### Before the day

- [ ] Copy the course folder to your laptop and work in that copy, never inside the shared folder
- [ ] Before you rehearse, keep a second copy aside, untouched: your clean copy
- [ ] Confirm the timetable: start and end times, breaks, timezone
- [ ] ‹Rehearse the demo top to bottom on a fresh kernel. Each section ends:›
  - ‹what each module's last cell prints›
- [ ] ‹Anything to start or download before learners arrive:›
  - ‹the command›

#### On the day

- [ ] ‹The check for a slow network, and the plan if it's slow:›
  - ‹the command›
- [ ] ‹Pre-run in the break before Module N: what to push, run or build, so its demo row fits›
- [ ] Open the completed challenge for the debriefs: each module's `challenge-solution/` notebook

#### After rehearsing

- [ ] ‹Put the room back, so the live beats start clean. From the instructor module folder, delete:›
  - ‹the files and folders a rehearsal leaves›

### Learner setup check

Learners set up at the start of the day: as they arrive, they open the course folder in its dev container and start ‹the session's services›, and both build while you welcome them. You check it at the end of the welcome.

| Check | Done when | If it isn't |
|---|---|---|
| Dev container | VS Code's bottom-left corner says *Dev Container: CG Core* | **Dev Containers: Reopen in Container** now; the first build takes a few minutes |
| ‹…› | ‹…› | ‹…› |

## Timeline

### Welcome {#dayNN-welcome}

**Section summary.** ‹Settle in, the welcome, meet Jordan, read the day's outcomes then into Module 1.›

<!-- The mandatory 25-minute intro, every day, on the five-hour day (user, 2026-11-02): these four rows, in this order: Arrive and settle 5, Welcome or Welcome back 15, Jordan and the day 2.5, What you will be able to do 2.5. The second is Welcome on a unit's first day (Day 01, 03, 05, 07), where the welcome day's own plan, unit00-programme/day00-welcome/, runs inside the row from its own deck, day00_slides.pptx, beside the day's, and the day's deck has one drafted Welcome slide, dayNN-welcome, of this row's On screen points (user, 2026-11-02: kept separate), or Welcome back on its second day (Day 02, 04, 06, 08). No Setup check row (setup is pre-work) and no Meet and greet row (introductions live in the welcome). The two
**From the overview.** fields quote dayNN_overview.md word for word: overview → lesson plan → slides. -->

#### 0:00 · 5 min · Intro/Outro — Arrive and settle

**Purpose.** Everyone is in, set up and settled before the welcome: the setup check finished, with help for anyone joining the unit (user, 2026-11-02).

**On screen.** `module00-overview/dayNN_slides.pptx`: Arrive and settle

**Instructor notes.**

- As learners arrive, they open the course folder in its dev container and start ‹the session's services›; both build while they settle.
- Walk the room: the setup check finished (`unit00-programme/learner/setup.pdf`), dev container open, Copilot answering, Docker running; help anyone stuck, especially anyone new to the unit.
- Housekeeping: timings, a break after every module, how to ask for help.

**Say.**

- "Open the course folder in its dev container while you settle; we start at five past."

**Transition.** "‹One line into the welcome.›"

**Assessment.** —

#### 0:05 · 15 min · Intro/Outro — Welcome

<!-- A unit's first day. On its second day this row is "#### 0:05 · 15 min · Intro/Outro — Welcome back": yesterday's list of what learners work on and want to learn, today's thread, in the same fields, and its On screen lists the slide's points after the deck's name, "`module00-overview/dayNN_slides.pptx`: Welcome back · ‹point› · ‹point›". -->

**Purpose.** Learners know why the programme runs, how a day runs and who is in the room.

**On screen.** `module00-overview/dayNN_slides.pptx`: Welcome · The programme, and where this unit sits · How a day works · You and the room

**Instructor notes.**

- Run the welcome from its own plan, `unit00-programme/day00-welcome/instructor/module00-overview/day00_lesson_plan.docx`, and its own deck, `unit00-programme/day00-welcome/instructor/module00-overview/day00_slides.pptx`, beside this one; move slides across if you want.
- Keep the introductions list for the closing debrief.

**Transition.** "Now meet the person whose report we work on all day."

**Assessment.** —

#### 0:20 · 2.5 min · Explain — Jordan and the day

**Purpose.** Learners know whose report they work on, what gets in its way and where it ends today.

**On screen.** `module00-overview/dayNN_overview.md`: the persona card

**From the overview.**

‹The overview's persona card grid table, word for word.›

**Instructor notes.**

- Read the card row by row: who Jordan is, where the report stands, what gets in the way, where it ends today.
- The last row is theirs: each learner does the same with their own copy, on the challenge data.

**Say.**

- "‹One brief line.›"

**Transition.** "Here's what you'll be able to do by the end."

**Assessment.** —

#### 0:22:30 · 2.5 min · Explain — What you will be able to do

**Purpose.** Learners know the day's outcomes.

**On screen.** `module00-overview/dayNN_overview.md`: What you will be able to do

**From the overview.**

By the end of this session you will be able to:

- ‹The overview's outcome bullets, word for word.›

**Instructor notes.**

- Read the outcome verbs: ‹the verbs›.
- Self-check, hands up: ‹which question paces which module›. Pair each no with a yes in that module's challenge.

**Say.**

- "‹One brief line.›"

**Transition.** "First, a question about your own work."

**Assessment.** —

### Module 1 — ‹module title, the programme overview's, word for word› {#dayNN-m1}

<!-- Outcomes appear once, in the intro: no Module outcomes here (user, 2026-10-27). The module's 🧭 anchor: write it in dayNN_anchors.md and run scripts/nbkit.py anchors --session <folder>. Never type it. -->

**Section summary.** Serves outcomes ‹…› and answers session questions ‹…›. ‹What learners make, in a sentence.›

#### 0:25 · 2.5 min · Instructor-led demo — ‹the first section's heading, word for word›

**Purpose.** ‹One line.›

**On screen.** `moduleNN-<slug>/dayNN_mN_demo.ipynb`: the anchor, the map, then ‹the first section's heading, as the demo prints it›

**Instructor notes.**

- **The module map.** ‹Open Module 1 from the table of contents; what its stops leave.›
- **‹The first section's heading›.** ‹What to run or show, and what to expect on screen.›

**Say.**

- **The module map.** "‹The anchor's question, asked to the room.›"
- **‹The first section's heading›.** "‹One brief line.›"

**Transition.** "‹One line into the next beat.›"

**Assessment.** —

<!-- One row per demo ### heading, to 0:45, in the demo's order, in 2.5-minute steps (2.5, 5, 7.5 …; a half-minute
start is written 0:27:30), so the demo totals about 20 minutes. The row's title is its heading, word for word; On
screen reads "`moduleNN-<slug>/dayNN_mN_demo.ipynb`: <heading>" (the last row: "<heading>, to its closing lines", since the
closing lines end the last beat and are not a heading). Every note and Say line opens with the heading in bold. -->

#### 0:27:30 · 5 min · Instructor-led demo — ‹the next section's heading, word for word›

**Purpose.** ‹One line.›

**On screen.** `moduleNN-<slug>/dayNN_mN_demo.ipynb`: ‹the next section's heading›

**Instructor notes.**

- **‹The next section's heading›.** ‹What to run or show, and what to expect on screen.›

**Say.**

- **‹The next section's heading›.** "‹One brief line.›"

**Transition.** "‹One line into the next beat.›"

**Assessment.** —

<!-- … one row like this for every remaining ### heading, chained with no gaps, to 0:42:30. -->

#### 0:37:30 · 5 min · Instructor-led demo — ‹the last section's heading, word for word›

**Purpose.** ‹One line.›

**On screen.** `moduleNN-<slug>/dayNN_mN_demo.ipynb`: ‹the last section's heading›, to its closing lines

**Instructor notes.**

- **‹The last section's heading›.** ‹The live beat: the COPILOT box, the mode, the check, and what it prints.›
- **‹The last section's heading›.** ‹End on the closing lines: where the work goes next.›

**Say.**

- **‹The last section's heading›.** "‹One brief line.›"

**Transition.** "‹One line into the question.›"

**Assessment.** —

<!-- Two Questioning rows of 2.5 minutes per module (user, 2026-10-27): this one straight after the demo's last beat, its
minutes taken from the demo by shortening one 5-minute beat; the next between the challenge's two rows, its minutes taken
from the second. Fields: Purpose, On screen, Ask (one or two questions), Listen for, If stuck, Transition, Assessment. -->

#### 0:42:30 · 2.5 min · Questioning — Check the demo

**Purpose.** ‹One line: what learners show they understood from the demo.›

**On screen.** `moduleNN-<slug>/dayNN_mN_demo.ipynb`: ‹the last section's heading›

**Ask.**

- "‹A question that makes learners think about the module's idea, not recall a word.›"

**Listen for.** ‹What a good answer contains.›

**If stuck.** "‹A prompt or simpler question that gets the room there.›"

**Transition.** "‹One line into the challenge.›"

**Assessment.** Outcome ‹N› · ‹evidence›

#### 0:45 · 15 min · Independent or pairs work — ‹Module 1 challenge — the challenge's own section title›

**Purpose.** ‹One line.›

**On screen.** `moduleNN-<slug>/dayNN_mN_demo.ipynb`: the Challenge time box; then the learners' `moduleNN-<slug>/dayNN_mN_challenge.ipynb`, ‹the challenge's section title›

**Instructor notes.**

- Brief the tasks by their exact titles: Q1 · CORE *‹title›*; Q2 · STRETCH *‹title›*; Q3 · BONUS *‹title›*.
- ‹Where learners work, and pairing from the self-check, if any.›

**Say.**

- "‹One brief line into the challenge: start at Q1, go as far as you can.›"

**Transition.** "Hands up for a moment: one question while you work."

**Assessment.** Outcome ‹N› · ‹evidence›

#### 1:00 · 2.5 min · Questioning — Mid-challenge check-in

**Purpose.** ‹One line: what learners show about their own work so far.›

**On screen.** The learners' `moduleNN-<slug>/dayNN_mN_challenge.ipynb`, ‹the challenge's section title›

**Ask.**

- "‹A question about the learners' own work: how they know it's right.›"

**Listen for.** ‹What a good answer contains.›

**If stuck.** "‹A prompt or simpler question.›"

**Transition.** "Back to it: carry on from where you are."

**Assessment.** Outcome ‹N› · ‹evidence›

#### 1:02:30 · 7.5 min · Independent or pairs work — Learners keep working

**Purpose.** Learners carry on at their own pace, with help when they ask.

**On screen.** `moduleNN-<slug>/dayNN_mN_demo.ipynb`: the Challenge time box.

**Instructor notes.**

- Stay available at the back of the room; no further check-ins.

**Transition.** "Time to share what you found, and your questions."

**Assessment.** Outcome ‹N› · ‹evidence›

#### 1:10 · 15 min · Feedback and discussion — Shareback/questions

<!-- Every module, on the five-hour day (user, 2026-11-02): this row, Feedback and discussion, exactly 15 minutes, after the challenge's rows and straight before the debrief. It replaced the same day's 10-minute Catch-up and questions row (Independent or pairs work), which the audit now fails. The deck's slide is dayNN-mN-shareback, from this row's On screen points or Purpose. -->

**Purpose.** Learners share what they found and where they stuck, and ask what is still blocking them.

**On screen.** `moduleNN-<slug>/dayNN_mN_challenge.ipynb`: Shareback/questions · ‹what you found› · ‹where you stuck›

**Instructor notes.**

- Ask two or three learners or pairs to share a finding or a stall; take questions from the room.
- ‹What to have ready: the stall hints in the Module 1 reference.›

**Say.**

- "What did you find, and where did you get stuck? Ask anything now."

**Transition.** "‹One line into the debrief.›"

**Assessment.** Outcome ‹N› · ‹a finding shared, a question asked›

#### 1:25 · 5 min · Feedback and discussion — Debrief

**Purpose.** ‹One line.›

**On screen.** `moduleNN-<slug>/challenge-solution/dayNN_mN_challenge.ipynb`: ‹Q1's task box and check cell.›

**Instructor notes.**

- ‹Walk through the solution, or ask two or three questions that surface blockers.›

**Transition.** "‹One line.›"

**Assessment.** Outcome ‹N› · ‹evidence›

#### 1:30 · 10 min · Break — Before Module 2

**Instructor notes.**

- ‹Check any setup that failed; reset what the next demo needs.›

**Transition.** "‹The bridge into Module 2, in a line.›"

**Assessment.** —

### Module 2 — ‹module title, the programme overview's, word for word› {#dayNN-m2}

<!-- The same shape as Module 1, from 1:40 to 2:55. -->

### Module 3 — ‹module title, the programme overview's, word for word› {#dayNN-m3}

<!-- The same shape as Module 1, from 2:55 to 4:10. -->

### Open challenge time {#dayNN-open}

**Section summary.** ‹Serves outcomes …. Learners carry on with any module challenge, as far as they can; Put it together, ‹task title›, is the optional stretch for fast finishers.›

<!-- 30 minutes at 4:10, Independent or pairs work rows only (user, 2026-11-02): the closing debrief opens the Wrap-up. -->

#### 4:10 · 20 min · Independent or pairs work — Carry on, or Put it together

**Purpose.** ‹One line.›

**On screen.** `module99-put-it-together/dayNN_together_challenge.ipynb`: ‹Put it together — task title›, or any module's challenge notebook.

**Instructor notes.**

- ‹Everyone picks up where they stopped; fast finishers open Put it together, which is optional.›
- ‹Stay available.›

**Transition.** "‹One line.›"

**Assessment.** Outcomes ‹…› · ‹evidence›

#### 4:30 · 10 min · Independent or pairs work — Learners keep working

**Purpose.** Learners carry on at their own pace, with help when they ask.

**On screen.** `module99-put-it-together/dayNN_together_challenge.ipynb`: ‹the How to use this notebook badge table.›

**Instructor notes.**

- Stay available at the back of the room; no check-ins.

**Transition.** "‹One line into the closing debrief.›"

**Assessment.** Outcomes ‹…› · ‹evidence›

### Wrap-up {#dayNN-wrapup}

**Section summary.** ‹The closing debrief and the questions the day has left, the three takeaways, one per module, then thanks, the feedback form and what's next.›

<!-- The day always ends with these three rows (user, 2026-11-02): Closing debrief and questions (10), Key takeaways (5), then Thank you for participating (5), to 5:00. -->

#### 4:40 · 10 min · Feedback and discussion — Closing debrief and questions

**Purpose.** ‹One line: blockers, anything shipped, and the questions the day has left.›

**On screen.** `module99-put-it-together/challenge-solution/dayNN_together_challenge.ipynb`: ‹the task box and check cell.›

**Instructor notes.**

- ‹Blockers anyone still has, and anything shipped.›
- ‹Take the questions the day has left; come back to the welcome's list of wants.›

**Transition.** "‹One line.›"

**Assessment.** Outcomes ‹…› · ‹evidence›

#### 4:50 · 5 min · Feedback and discussion — Key takeaways

**Purpose.** Learners leave with one takeaway per module, in a sentence each.

**On screen.** `module00-overview/dayNN_overview.md`: the outcomes.

**Instructor notes.**

- Look back first, briefly: read the outcome verbs, a hand for each. ‹Then two learners show what they kept.›
- ‹Ask which session question they can now answer.›

**Say.**

- "‹Module 1's takeaway, in a sentence.›"
- "‹Module 2's takeaway.›"
- "‹Module 3's takeaway.›"

**Transition.** "‹One line into the thanks.›"

**Assessment.** Outcomes ‹…› · ‹evidence›

#### 4:55 · 5 min · Intro/Outro — Thank you for participating

**Purpose.** ‹One line: thanks, feedback and what's next.›

**On screen.** `module00-overview/dayNN_overview.md`: ‹what's next.›

**Instructor notes.**

- ‹The feedback form, before learners leave.›
- ‹The next session: its title, what it builds on, what to set up.›

**Say.**

- "Thank you for participating today."
- "‹The feedback form, in a line.›"

**Assessment.** —

## Module 1 reference {#dayNN-m1-reference}

### What a finished challenge looks like

- **Q1.** ‹One line, with the real numbers.›
- **Q2.** ‹One line.›
- **Your turn.** ‹One line, where the section has one.›
- **Q3.** ‹One line.›

### The likeliest stalls

| Stall | Hint |
|---|---|
| ‹What you'll see› | "‹One line.›" |

### Fallbacks

| Problem | Do this |
|---|---|
| ‹…› | ‹…› |

### Facts to have ready

- ‹Only what you need at hand, exactly as the demo or challenge prints it.›

## Put it together reference {#dayNN-together-reference}

<!-- The same parts as a module reference, as the task needs them. -->

## Question bank

### Module 1

**Key questions.**

1. ‹The module's questions from the brief.›

| Ask after | Question | Answers (correct in bold) |
|---|---|---|
| ‹1:35 · Debrief› | ‹…› | ‹option› · **‹correct option›** · ‹option› |

## Support and stretch

### Module 1

**Support.** ‹For a learner or room missing a prerequisite, in a line or two.›

**Stretch.** ‹For a learner or room that already knows it.›

## FAQs

**‹A question learners ask›**

‹The answer, in a sentence or two.›

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
