# Cohort 7 (12–16 October 2026, Irvine) — what the recordings and notes tell us

Source files: `reference/DCP Cohort 7 (Oct _26)/` (transcript and AI-notes PDFs per day, m4a recordings, Day 1 agenda docx, Day 3 agenda, capstone presentations, the Cohort 3–5 slide deck, the instructor plan PDF and the v4-3 learner book). Plain-text extracts of every PDF are in `extracts/cohort7/` (regenerate with `research/scripts/extract_cohort7.sh`). The m4a recordings were not transcribed locally (no ffmpeg/whisper on this machine); the transcript PDFs are the text of those recordings.

## Facts about the cohort

| Item | What the material shows |
|---|---|
| Dates and place | Monday 12 to Friday 16 October 2026, CG office in Irvine, California. Hours 09:00–15:00, lunch 12:00–13:00, breaks mid-morning and mid-afternoon. |
| Room | 17 learners on 5 tables. Mix: EDO (data operations, data engineers, data product managers), Digital/CXT (client experience technology), investment operations software engineers, IG tech, digital marketing solutions engineers, technical and solution architects. Several had used dbt or Airflow before; one person knew dbt macros, two had bitemporal-loading experience, one had Harness access. |
| Decoded team | Michael Burgess (lead; designed the programme; whiteboard-led teaching) and Sophie McMurray (support, floor walking). |
| CG people | Nicole (programme coordinator: lunch vouchers, Teams channel, logistics, leadership video); Hero (sponsor, DXP operating model talk, Day 1 09:30); Martin (platform team, Day 3 11:00–12:00 guest session on Airflow/Astronomer, Databricks/Unity Catalog, the vended repo, data contracts); learner Chris plus a colleague presented bitemporal loading (Day 4 09:07); a learner demonstrated Harness (Day 4 13:40); Jeff (learner, data-owner perspective on effective dating). |
| Challenge route | The **v1** challenges in the training repo: `challenges/01-docker-intro` (Day 2), `02-dbt-pipeline` (Day 3), `03-airflow-orchestration` (Day 4), `04-atlas-capstone` (Day 5). Not the v2 phase route and not the CG product-information capstone. |
| Tools shown | VS Code + Copilot chat with the AI Catalyst plugin (`/ai-catalyst product-requirements-document`, data-contract skill), model picker (Claude Opus / Sonnet / Haiku; GPT "Sol", "Terra", "Lunar") and "thinking effort", Apple Voice Memos for interview transcripts, Markdown editor/preview, Docker Desktop, the EDO training dev container, `mise run setup:databricks`, the Databricks UI catalog (`training_dev.training_<user>`), the Airflow UI, Harness UI (learner demo), the Caspian associate dimension table (learner demo). |
| Finishing times | Day 1 ~15:00, Day 2 ~14:35 ("two hours ahead"), Day 3 14:10, Day 4 15:00, Day 5 ~14:00 (presentations 13:45–14:00). |

## Per-day notes

- [Day 1 — design, business case, adoption, Catalyst, AI practice, interview role-play](day1.md)
- [Day 2 — STTM, SLIs/SLOs/SLAs, paved path, data systems, Docker, Databricks, contract-to-code](day2.md)
- [Day 3 — dbt self-paced practical, Martin's platform session, recap](day3.md)
- [Day 4 — bitemporal loading, Airflow, CI/CD and Harness, capstone briefing](day4.md)
- [Day 5 — Atlas capstone and team presentations](day5.md)

## The two agendas that were actually used

Day 1 agenda (docx), as planned by the Decoded team on the morning:

```
Nicole's intro, Michael & Sophie intro (10 min)
09:10–09:30 learner challenge in groups (intros)
Talk from Hero (25 min); learner share-back (10 min)
Intro to programme and definition of a data product (10 min)
Break 10:15–10:30
Learner challenge: identifying a data product (20 min); share-back (30 min); group discussion (20 min)
11:40–12:00 pairs: use Catalyst to generate a PRD
Lunch 12–1
AI and effective AI practice (30 min); demo Catalyst, model options (gpt-5.6 Terra vs Claude Opus 5 etc.) and thinking effort (10 min)
Break 13:40–14:00; introduce challenge; group challenge (switch groups) 14:10–14:40; share-back until 15:00
```

Day 3 agenda (pdf): 09:05 learners work through dbt challenges · 10:00 break then continue · 11:00 Martin's talk · 12:00 lunch · 13:00 back to challenges · 14:00 learners report back what they've learnt; learners asked to give teaching demos tomorrow on bitemporal loading and Harness/CI-CD · 14:10 end.

## Where Cohort 7 departed from the written instructor plan

- Day 2 ran far ahead: the afternoon became "generate dbt and Airflow from your contract with Catalyst" (a preview of Days 3 and 4) followed by a debrief, not the plan's structured Challenge 8 plus pair code review.
- Day 3 was almost entirely self-paced dbt (v1 challenge 02), with Martin's hour and a 10-minute recap; no "test review in pairs".
- Day 4's Airflow block ran 09:30–13:30; the afternoon was CI/CD theory, a learner's Harness demo and more practical. No release-decision exercise, no failure-and-repair note.
- Day 5 was the v1 Atlas capstone: teams, reverse-mapping discovery, Phase 1, some Phase 2, four short presentations, finished by 14:00.
- Demonstrations that were promised but did not happen: a finished Opus-generated HTML contract (too slow, swapped to a small model), Datadog, S3/Lambda triggers.
