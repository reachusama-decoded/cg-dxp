# Start here — the week in one page

[Data Creators › instructor pack — start here]{.breadcrumb}

## What the week is

Five days, in person, that take a room of CG engineers, product managers and architects from "what is a data product?" to a data product they built on the paved path. Monday to Thursday teach and practise; Friday is the Atlas capstone, which certifies them. Hours 09:00–15:00 with lunch 12:00–13:00 and a break mid-morning and mid-afternoon; Friday finishes when the presentations do, usually early afternoon.

| Day | Theme | Learners leave with | Practical (learners' repo) |
|---|---|---|---|
| 1 | Product discovery and effective AI use | A justified product, an interview transcript, a reviewed PRD and data contract, the nine DPLC phases | Catalyst in Copilot |
| 2 | Mappings, service levels, platform architecture (warehouse, lake, lakehouse; Databricks, Delta and Spark; how the tools fit together), Docker, contract to code | A contract with STTM rules and measurable SLAs, a built container, generated dbt and Airflow code they can explain | `challenges/v1/01-docker-intro` |
| 3 | dbt practical and consolidation | A built, tested, documented Portfolio Analytics pipeline on Databricks | `challenges/v1/02-dbt-pipeline` |
| 4 | Bitemporal loading and Airflow orchestration | A scheduled DAG with a freshness gate, callbacks and a controlled failure; the deployment picture | `challenges/v1/03-airflow-orchestration` |
| 5 | Capstone | The Atlas data product: discovery, Phase 1 baseline, extensions, a presentation | `challenges/v1/04-atlas-capstone` |

The thread through the week: design conversations, transcripts and reviewed contracts produce most of the code; the practicals exist so learners can check what Catalyst generated. Say it on Day 1, prove it on Day 2 afternoon, repeat it in every debrief.

## How a day runs

- **Anchor from the notebook.** Each day has one notebook, `dayN-*/dayN_anchor.ipynb`, that stays on the projector: a numbered agenda, diagrams, whiteboard questions, demo cells, activity and challenge boxes, and a Questions section for live notes. Every section runs as demo, challenge, shareback, break. It is learner-facing; everything instructor-only is in `run-sheet.md` beside it, in the same section order.
- **Teach from the whiteboard.** Day 1 and the first hour of Day 2 are elicitation: ask, write what the room says, add what is missing. The anchors carry the questions; the run sheets carry the answers rooms give and what to add.
- **Demo from the laptop.** Every demo in this pack runs locally (DuckDB, Docker Desktop, the Astro CLI, Claude Code with Catalyst skills). Learners see the same thing in their dev container against Databricks. Say so once; then stop mentioning it.
- **Practise in the learners' repository.** The challenge READMEs are the learner material. Launch each with the run sheet's script, circulate with its checklist, and regroup at the stated times.
- **Debrief by asking.** "What did we learn?" and write it up, as the Day 3 recap script does. Then the pair exercise, then save the artefacts.

## Who is in the room

Tables of three or four, mixed by team where possible. Each person has a laptop; pairs and tables share one screen for discussions. Rotate tables once after lunch on Day 1 (count off) so people meet other teams. Use the room's experience: ask who has used dbt, Airflow, Docker, Harness or has bitemporal loading in production, and give those people the stretch tasks and the Thursday morning teaching slots.

## Guests

People may come to speak, usually in the morning: a sponsor's welcome on Day 1, a platform-team session on Day 3, and bitemporal loading or deployment on Day 4. Each slot in the run sheets has an instructor-led version in case nobody comes, written from what the platform team and learners said in the previous cohort. If a guest confirms, send them the slot's agenda line and keep the slot's questions ready for them.

## Before Monday

Work through [preflight-checklist.md](preflight-checklist.md). The two things that break a Monday are Catalyst access and the dev container, both on the learners' side; the checklist has what to send learners and what to verify in the first hour.

## Where things are

- Learner-facing, in `courseware/` (shareable as it is): anchor notebooks `courseware/dayN-*/dayN_anchor.ipynb` (kernel `cg-dxp`; generated from `research/scripts/notebooks/`), activity cards `courseware/dayN-*/activities/`, demo code with a README per folder `courseware/dayN-*/demos/` and `courseware/day5-capstone/support/`.
- Instructor-only, in `instructor/`: this folder (`00-week/`), and per day `instructor/dayN-*/run-sheet.md`, the printable `run-sheet.docx`, and the prep guide `dayN_prep-guide.md` (and `.docx`): the concepts in depth, teaching notes, demo and challenge mechanics, a self-test.
- The running example (a US end-of-day prices product) used in every demo and fallback: `courseware/common/running-example/`.
- Prompts for every AI beat, with Copilot and Claude variants: `courseware/common/prompts/`.
- Whiteboard diagrams as Mermaid: `courseware/common/diagrams/`.
- The LLM guide (how to use Claude on this laptop, what learners see in Copilot, diagnostic prompts to share): [llm-guide.md](llm-guide.md).
- Risks and fallbacks: [risks-and-fallbacks.md](risks-and-fallbacks.md).
