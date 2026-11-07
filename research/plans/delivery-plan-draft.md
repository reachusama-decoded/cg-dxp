# Delivery plan draft — Data Creators, five days (pending the open questions)

Structure follows `reference/instructor-plan.md` (09:00–15:00, lunch 12–13, Monday–Thursday) plus Friday's capstone. Each day in `delivery/dayN-<slug>/` gets: `run-sheet.md`, `demos/`, `activities/`, `diagrams/`, `fallbacks/`. `delivery/00-week/` holds the start-here, pre-flight checklist and risk register.

## Day 1 — Product discovery and effective AI use

| Block | Run-sheet content | Demo / activity resources to build |
|---|---|---|
| 09:00 Welcome | Logistics, leadership video, introductions; set up the written product list | Opening slide/agenda; the "write it down" instruction |
| 09:15 Challenge 1 | Intros + products and pain points | Activity card 1 (two parts, 5 + 10 min, note taker) |
| 09:30 Sponsor | Hero's four personas; fallback: instructor tells it from the Day 1 notes | Persona diagram; sponsor fallback script |
| 09:45 Share-out | Group naming, visible list | Capture sheet for the room's products (reused Days 1–2) |
| 10:05 What is a data product | Three views, what it is not, capstone preview | Diagram: three views; capstone one-pager |
| 10:30 Discovery questions | Triage questions elicited | Diagram: who/what/exists/can/worth |
| 10:40 Challenge 2 | Justify a product | Activity card 2 with the five questions and the "hardest question" prompt |
| 11:00 Debrief + lifetime value + adoption | Costs, payoffs, barriers, responses | Diagram: cost/payoff/adoption board with the expected answers |
| 11:40 Catalyst demo | Skill files, template, `/ai-catalyst product-requirements-document` | Demo script with exact clicks and prompt; pre-generated PRD fallback |
| 11:50 Challenge 3 | Independent PRDs compared | Activity card 3 |
| 13:00 AI foundations | The seven-step order from the plan; interface walk | Demo script with prompts for model/effort/context; planted-contract-errors example |
| 13:55 Challenge 4 | Interview in threes, record, generate PRD then contract | Activity card 4 (roles, seven questions, Voice Memos/Teams transcript steps); fallback transcript and generated documents |
| 14:25 Debrief | Wrong fields, generic knowledge, discovery methods, document sections | Debrief question list; PRD/contract section checklist |
| 14:45 Challenge 5 | Interview Catalyst on the DPLC | Activity card 5; expected answers (nine phases, build prerequisites) |

## Day 2 — Mappings, service levels, platform, Docker, contract to code

Blocks per the plan: STTM and SLI/SLO/SLA (whiteboard script and nines table); Challenge 6 extend the contract (card); Markdown → HTML demo (prompt, fast-model fallback, pre-rendered example); mapping ambiguity list; paved path (diagram) and data systems timeline (diagram, 15-minute script); Docker demo (dev container Dockerfile walk, image/container commands) and Challenge 7 (route-dependent card: v1 01-docker-intro or v2 docker phase-one tasks 1–4); Databricks setup demo (OAuth, catalog/schema, where tables land); Challenge 8 contract-to-code (card with the six steps and the extension questions; a generated dbt project and DAG as fallback); debrief order; pair code review (card: trace a rule, find an assumption, propose a check); closing corrections.

## Day 3 — dbt practical and consolidation

Launch script for the assigned dbt project (route-dependent commands, prefixes, verify gates); circulation checklist (grain, right-side uniqueness, independent total); instructor dbt demo notebook (sources, staging model anatomy, materialisation, tests, build, select syntax) runnable in the dev container; guest-session agenda or the instructor-led platform talk from the Day 3 notes; recap script (ten topics); test review in pairs (card with the three "wrong result" prompts); day-close checklist.

## Day 4 — Bitemporal loading and Airflow

Bitemporal talk (timeline diagram, the Monday/Wednesday correction example, macro walk-through pointers) for a guest or the instructor; Airflow demo notebook (DAG anatomy, `>>`, callbacks, UI tour, blueprint YAML example); Challenge 10 launch script (route-dependent; Astro boot order and cold-start recovery; the controlled failure); CI/CD and Harness block (script, screenshots to request from CG); release decision in pairs (card: 500 rows/497 IDs); failure-and-repair note (card plus template); Friday preparation checklist.

## Day 5 — Capstone

Briefing script (reading time, table discovery with the worksheet, phases, lunch, presentations); discovery worksheet (producer–creator–consumer map, consumer-backwards map, mini-STTM, glossary and trust questions); instructor circulation notes per Phase 1 section; presentation prompt card (two to three minutes per table) and a tally sheet; certification evidence checklist; close.

## Build order once the decisions are in

1. Week start-here and pre-flight checklist (depends on questions 3–5, 7).
2. Day 1 run sheet, cards, diagrams, Catalyst and Copilot demo scripts, fallback artefacts (depends on 8, 9).
3. Day 2 run sheet, cards, diagrams, Docker and Databricks demos, contract-to-code fallbacks (depends on 1, 9).
4. Days 3 and 4 run sheets, dbt and Airflow demo notebooks, guest fallbacks (depends on 1, 4).
5. Day 5 briefing and worksheet (depends on 2).
6. Optional slide decks (depends on 6).
