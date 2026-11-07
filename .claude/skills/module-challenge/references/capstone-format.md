# Capstone format (Session 09)

The capstone is a half-day in three phases, building a **backend JSON API** that serves deterministic analytical results from the synthetic fund pack plus a vendor-GenAI summary of them, packaged with Docker, with a dbt preparation stage. Brief: `designer/core/transcripts/cg-design-core.md` from line 467. Dataset, endpoint schema, assessment criteria and team format are open MJB/dev decisions; everything below is the working shape.

## Scaffold (adapted from the Deloitte capstone)

`courseware/unit05-capstone/day09-ai-powered-data-api/learner/moduleNN-<slug>/`, one module folder per phase (the phase anchors and their files; the activity is "challenge", never "practice"):

```
README.md            # the brief, phases, what to show, how it is assessed (working)
p1-ingest-prepare/   # dbt project on courseware/common/data/challenge/raw/, quality tests, stable intermediate outputs
p2-analyse-serve/    # FastAPI app: /health, /funds/{id}/summary (analysis + GenAI narrative), Pydantic models, Dockerfile, fixtures/
p3-demonstrate/      # demo script, architecture one-pager template, evidence checklist
starter/             # reachable core: everything wired; the regions to change are named in the brief, never TODO gaps
(the complete reference, verified live and with fixtures, is `instructor/moduleNN-<slug>/challenge-solution/`, like every session's completed challenge)
tests/               # deterministic checks on analytical fields and schema; a small case set for summary consistency
```

Principles: a reachable core (it runs before learners touch it), clearly named regions to change, offline fixtures and test contracts, optional extensions, a preserved route to live vendor-API evidence. Replace the Deloitte retailer/Streamlit surface with the Harbourline analytical JSON API.

## Way of working

The capstone is the fullest rehearsal of the programme's way of working (`programme-profile/references/conventions.md` → "Learners direct AI and review what it wrote"): teams brief Copilot to write, fix or change the code, any calculation included, review every line it wrote, run the tests and checks, and keep or undo each change. They do not type the code or work out the maths by hand. The phase briefs say what to ask for and what evidence proves it; the evidence includes the prompts, the review notes and the check results, not only the working API. Phase briefs in an anchor use the same box set as every challenge (`lesson-build/references/notebook-boxes.md`, built with `nbkit`), and `solution/` shows a model prompt, the change and the check for each phase rather than only the finished code.

## Phases and demonstrations

| Phase | Build | Demonstration |
|---|---|---|
| P1 Data ingestion and preparation | dbt models and tests from the raw extracts to a validated dataset | Working preparation stage, pipeline run and quality report, the engineering choices explained |
| P2 Analysis, GenAI and API integration | Analysis functions, vendor call with Pydantic output, FastAPI routes, Docker image, each written by Copilot from the team's brief and reviewed | Checked JSON output, traceability to data and methods, test evidence, the prompts and review notes, how the GenAI output was verified |
| P3 Final demonstration and design review | Run the container, present architecture, quality controls, purpose | Runnable API/container and a concise explanation of choices, validity and the GenAI component's value |

## Required outputs (brief)

Source-controlled repository with run steps and container assets · pipeline run report and data-quality checks · analytical results and validation notes · API response examples and test evidence · final demonstration artefact and impact summary.

## Alignment

Earlier challenges in S02 (tests, Docker, CI), S03–S04 (vendor API, Pydantic, JSON API, evaluation), S07–S08 (dbt, quality, orchestration) produce artefacts in these shapes. When the capstone schema is confirmed, revisit those challenges (stage 6 of each module) so they feed it.
