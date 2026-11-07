# Day 5 run sheet — The Atlas capstone

[Data Creators › Day 5 — run sheet for instructors]{.breadcrumb}

Instructor-only companion to the anchor notebook, in the notebook's order: the same numbered sections and labelled parts, each with its time, purpose, what is on screen, what to say, what to ask at the whiteboard (with the answers rooms give and what to add), the demo steps with their coaching, fallbacks, the transition and what to do if ahead or behind. Keep the notebook on the projector and this beside it. Times follow the instructor plan; adapt them to the room and keep the sequence.

## Before the day

- Before the day: `bash support/atlas_duckdb/build.sh` and `python support/expected-results.py`, so the expected numbers below are from this laptop's build of the solution.

## Sections

| # | Section | Time | What happens |
|---|---|---|---|
| 1 | The brief and discovery | 09:00–10:15 | Brief: the day, the rules, ten minutes of reading · Activity 12: discovery worksheet · Playback: two minutes per table |
| 2 | Phase 1: the baseline | 10:15–13:00 | Challenge: Atlas Phase 1 · Circulating: section notes, expected results, blockers · Lunch (flexible) |
| 3 | Phase 2: extensions and presentation prep | 13:00–14:30 | Challenge: the fourteen extensions · Presentation prep: technical work stops at 14:30 |
| 4 | Presentations and close | 14:30–15:00 | Activity 13: presentations · Tally sheet and certification evidence · Close |

## Day at a glance

| § | Time | Block | Type | On screen |
|---|---|---|---|---|
| 1 | 09:00–09:15 | Brief and individual reading | Intro | Anchor › Brief; the capstone README |
| 1 | 09:15–10:15 | Table discovery and playback | Challenge + shareback | Anchor › Activity 12 worksheet; the ERD and pipeline diagrams |
| 2 | 10:15–12:00 | Phase 1 build | Challenge | Anchor › Phase 1 support, expected results |
| 2 | 12:00–13:00 | Lunch (flexible) | Break |  |
| 3 | 13:00–14:30 | Phase 1 completion, Phase 2 extensions, presentation prep | Challenge | Anchor › Phase 2 menu; Activity 13 card |
| 4 | 14:30–15:00 | Presentations and close | Shareback | Anchor › Activity 13; tally sheet |

## Timeline

### 1. The brief and discovery

Brief: the day, the rules, ten minutes of reading · Activity 12: discovery worksheet · Playback: two minutes per table

#### 09:00 · 15 min · Explain — Brief — the day, the rules, ten minutes of reading

**Assessment.** Anchor › Brief; the capstone README

**Purpose.** What the day is, where the project is, the caveats about the data, and ten minutes of reading alone.

**Instructor notes.**

- Start sharp. The README is in challenges/v1/04-atlas-capstone; the work happens in data_products/atlas_elt.
- Extra attendees may join; name cards and a table for them.

**Say.**

- “Read the first third of the README on your own. At 09:15 your table works out what you are being asked to build.”

**Say.**

- “The project is challenges/v1/04-atlas-capstone in your dev container. The work happens in data_products/atlas_elt. Not in the challenge folder.”
- “First job: reverse-engineer the source-to-target mapping from the data you are given and the tables you are asked to produce.”
- “The data is synthetic and has been through several rounds of generation; a few things will look odd. Portfolio and fund do not mean what they mean in our own model; that is deliberate, so the design conversation is real.”
- “Read the first third of the README on your own now. At 09:15, as a table: what are we being asked to do? Stop discussing by 10:00, 10:15 at the latest, so there is time to build.”
- “Phase 1 is what you must complete. Phase 2 is open-ended, for whoever finishes. Lunch when you like; everyone back by 13:30; presentations when every table is done with Phase 1.”

**Transition.** Table discovery.

#### 09:15 · 60 min · Independent or pairs work — Activity 12 — discovery worksheet, then playback

**Assessment.** Anchor › Activity 12 worksheet; the ERD and pipeline diagrams

**Purpose.** Reverse-engineer the product from the outputs: producer-creator-consumer map, consumer-backwards map, mini-STTM, glossary and trust questions; two-minute playbacks.

**Instructor notes.**

- Nudge tables towards different outputs so the playbacks differ.
- A PRD or contract from Catalyst during this hour is desirable, not required.

**Say.**

- “Work backwards from the output to the sources. Describe the transformations in English; no SQL yet.”

**Activity 12 — Atlas discovery worksheet.** Tables, 60 min; the card is in `activities/`.

**Transition.** Phase 1.

**Adapt.** Wrap by 10:15 at the latest; the build needs the time.

### 2. Phase 1: the baseline

Challenge: Atlas Phase 1 · Circulating: section notes, expected results, blockers · Lunch (flexible)

#### 10:15 · 105 min · Independent or pairs work — Challenge — Atlas Phase 1

**Assessment.** Anchor › Phase 1 support, expected results

**Purpose.** Every team establishes the baseline: readiness, seeds, source-aligned, domain-aligned, consumer-aligned, tests, orchestration understood.

**Instructor notes.**

- Circulate with the section notes; compare numbers with the expected results; never type in a learner's project.
- Record each team's progress on the tally sheet.

**Say.**

- “A successful build is a prerequisite. A number you checked another way is evidence.”

**Challenge — Atlas capstone, Phase 1.** `challenges/v1/04-atlas-capstone/README.md` · two to three hours.

**Circulating — section notes, expected results, blockers.**

**Transition.** Lunch is flexible; everyone back by 13:30 at the latest.

#### 12:00 · 60 min · Break — Lunch, back at 13:30 at the latest

### 3. Phase 2: extensions and presentation prep

Challenge: the fourteen extensions · Presentation prep: technical work stops at 14:30

#### 13:00 · 90 min · Independent or pairs work — Challenge — choose extensions by value to the consumer; technical work stops at 14:30

**Assessment.** Anchor › Phase 2 menu; Activity 13 card

**Purpose.** Teams finish Phase 1, choose extensions that add value, and prepare a two-to-three-minute presentation.

**Instructor notes.**

- The day ends when every team has completed Phase 1; bring presentations forward if that happens early.
- Technical work stops at 14:30 (or earlier) to prepare.

**Say.**

- “Pick the extension that changes what your consumer can do, not the one that looks hardest.”

**Transition.** Presentations.

**Adapt.** Advanced learners who finish Phase 2 can take the advanced path in the README: a product of their own.

### 4. Presentations and close

Activity 13: presentations · Tally sheet and certification evidence · Close

#### 14:30 · 30 min · Independent or pairs work — Activity 13 — capstone presentation

**Assessment.** Anchor › Activity 13; tally sheet

**Purpose.** One person per table, two to three minutes; the certification evidence recorded; the week closed.

**Instructor notes.**

- If senior leaders attend, invite tables to mention Catalyst, the paved path and the mission.
- Prizes if there are any. Thank the guests and the platform team.

**Say.**

- “Do we feel we can create a data product? Then you are done.”

**Activity 13 — Capstone presentation.** One person per table, 3 min; the card is in `activities/`.

**Tally sheet and certification evidence.**

**Close.**

**Say.**

- “One person per table, two to three minutes: what you built, what was hard, one finding, one trust question and its answer.”
- “Do we feel we can create a data product and make it work? Then you are done. Thank you for the week.”

## Before learners leave

- [ ] Each team's Phase 1 evidence recorded on the tally sheet: layers built, tests passed, one independent value check, orchestration explained.
- [ ] Each team's worksheet and presentation kept with their project.
- [ ] The week's artefacts (PRDs, contracts, STTMs, generated code, dbt and Airflow projects) saved where the learners can find them.
- [ ] The list of open questions for the platform team handed over with names.
