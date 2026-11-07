# Review summary — Data Creators delivery, week of 9 November 2026

What was reviewed: the Cohort 7 recordings' transcripts, AI notes, agendas and presentations (all five days); the Cohort 3–5 slide deck; the Cohort 7 instructor plan PDF against the current `reference/instructor-plan.md` (diff in `research/notes/instructor-plan-md-vs-cohort7-pdf.md`); the client training repo (`edo-training-data-products`, v1 and v2 challenges, the CG capstone, dev-container docs, instructor demo stories, the other instructor's Oct-5 delivery notes); the Catalyst skills; the CG Core programme's conventions and a built session; the learner book's table of contents (not its 459 pages, per the brief).

## Ten things that matter for next week

1. **The instructor plan is the skeleton of what Cohort 7 actually did, tidied.** Day 1 matches closely. Days 2–4 in the plan add structure Cohort 7 never ran (pair code review, test review, release decision, failure note). Cohort 7 ran ahead on Day 2 (finished 14:35) and Day 3 (14:10) and left Friday afternoon unused. The new structured exercises are the right use of that slack, but they have no tested material yet.

2. **Three challenge routes exist and the documents disagree about which one is "current".** Cohort 7 used v1 (`challenges/v1/01…04`). The current instructor plan describes the **v2 Portfolio Analytics phase-one** tasks for Docker, dbt and Airflow and the **v1 Atlas** capstone for Friday. The repo README says v2 plus the **CG product-information capstone** (a 09:00–16:00 individually assessed day) is the assigned route. The v2 Docker and Airflow instructor demos are marked draft pending live rehearsal. This is the biggest decision and it changes Days 2–5.

3. **Guests carried a lot of the week.** Sponsor talk (Hero, Day 1), platform session (Martin, Day 3, one hour), bitemporal loading (a learner, Day 4), Harness (a learner, Day 4). The plan assumes equivalents. If they are not booked, instructor-led fallbacks are needed; Martin's content and the bitemporal talk are captured in the Day 3 and Day 4 notes and can be taught from them.

4. **Day 1 is whiteboard-led, not slide-led.** Michael elicited everything (data product definition, triage questions, costs/payoffs, adoption, SLIs). The scripts are in `research/notes/cohort7/day1.md` and `day2.md` with the answers the room gave, which is the fastest way for a new instructor to run the same conversations.

5. **The Catalyst and Copilot demos need rehearsal with the real plugin.** On Day 1 the live PRD demo ran once without Catalyst installed; on Day 2 the HTML demo stalled at high effort. Pre-generated fallbacks (a PRD, a contract, an HTML render) remove that risk. The interface demo needs to know which models CG exposes this month.

6. **Access problems appeared every day:** Catalyst repo not found (Day 1), GitHub team membership (Day 3), dev container rebuilds (Day 2, Day 4), slow OAuth setup. A pre-flight checklist sent before Monday and a platform-support contact in the room are worth more than any slide.

7. **The 80/20 message is the course's spine:** design conversations, transcripts and reviewed contracts produce most of the code; the practicals exist so learners can check what Catalyst generated. Every debrief should return to it.

8. **Timings that worked:** interview role-play 30–35 minutes including generation; justify-a-product 20 minutes plus a 25-minute debrief; Docker practical 35 minutes; dbt Phase 1 about an hour; Airflow Phase 1 about 1.5 hours; Atlas Phase 1 two to three hours with a 45–60 minute reverse-mapping discussion first.

9. **The learner book versions do not line up.** The current plan links to a book with numbered chapters (`01-day-1-design-skills.md`, `30-appendix-course-challenges.md`, `47-reference-temporal-data.md`); the Cohort 7 PDF is "v4-3" with Monday–Thursday chapters; the sibling repo holds "v4" with `01…10` chapters. Which book learners receive matters only for the links in the plan; teaching does not depend on it.

10. **The slide deck in the folder is for Cohorts 3–5** (six-day structure with a design canvas, empathy maps, RAID/RICE, Day 5 operations). Useful as a source of diagrams and phrasing, not as the deck for this flow.

## What Cohort 7 taught that the plan does not say

- Name the groups fast and keep a visible list of the room's own products; every later activity reuses it.
- Tell people to write things down on the paper provided; Cohort 7's first share-out had nothing written.
- Rotate tables once (after lunch on Day 1 by counting off) so people meet other teams.
- "Five minutes of fun" and merch for the best submission kept energy up; the leadership video opened the week.
- Let the technical people go deep on Day 2 afternoon (bitemporal macro, Airflow-to-Datadog) rather than holding everyone to the same task.
- End-of-day recap by asking the room "what did we learn?" and writing the facts up, rather than lecturing.

## Risks ranked

| Risk | Likelihood | Mitigation in the pack |
|---|---|---|
| Wrong challenge route built into the run sheets | High until decided | Decision 1 in `research/plans/open-questions.md`; run sheets parameterised by route |
| Catalyst/GitHub access on Monday morning | High | Pre-flight email, a Day 1 lunchtime setup slot, Access Central steps in the start-here |
| No guest for the platform session or deployment demo | Medium | Instructor-led versions from the Day 3 and Day 4 notes, Harness/Datadog screenshots to collect from CG |
| Astro/Databricks setup eats the Day 4 practical | Medium | Boot order checklist, cold-start recovery steps, a prepared failing example |
| Instructor's own laptop cannot run the dev container, Catalyst or Databricks | Unknown | Decide what demos must be live vs recorded/screenshotted (question 7) |
