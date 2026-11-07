# Cohort 7 — Day 5 (Friday): the Atlas capstone

Source: `extracts/cohort7/d5-transcript.txt`, `d5-ai-notes.txt`, `d5-capstone-presentations.txt`.

## As delivered

| Time | What happened |
|---|---|
| 09:00 | Extra attendees in the room. Brief: the project is `challenges/04-atlas-capstone` ("mysteriously named capstone"); first reverse-engineer the source-to-target mappings from the data and the tables to be produced; the data is AI-generated and has been rationalised, but every pass through the platform team adds another wave of generation, and "portfolio" and "fund" do not mean what they mean in the CG model. |
| 09:00–09:15 | Read the first third (at least a quarter) of the README individually. |
| 09:15–10:00 (10:15 latest) | Table discussion: what are we trying to do; ideally produce a PRD or data contract you could show. |
| 10:15 onwards | Phase 1 (certification) then Phase 2 (open-ended, for advanced technical practitioners). "The end of the day commences when everyone is done with Phase 1." No fixed lunch; back in the room by 13:30. |
| 13:45 | Table debriefs, two to three minutes each: what you did, hard/easy, where you got to, Catalyst and the design documentation. If leaders attend, mention Catalyst, the paved path and the mission. Merch prizes (DXP caps, a Decoded t-shirt). |
| ~14:00 | Done. "Do we feel we can create the product? Yes. Then you're done." |

## What the teams presented

- **Group 1 — Portfolio Summary and Advisor Book.** Staging and integration models, final outputs, reconciliation passes, data quality checks, build tests, the Airflow DAGs; seven source-aligned tables and about nine models; consumers: advisory leadership and portfolio oversight (AUM and portfolio health). Finding: trades dated before the portfolio inception date; kept the rows and flagged to business users rather than guessing a rule. Ran two jobs; Airflow runs and Databricks catalogs inspectable.
- **Group 2 — Instrument Activity and Client-segment aggregates.** Seed → staging → domain → consumer-aligned; cleaning steps: valid trades only, price conversion, aggregation. Risks listed: is the latest price fair and current; invalid trades; fee calculation; no currency conversion; trades pointing at unknown instruments drop out of the join; the same trade counted twice; net buys minus sells for positions; segment labels must be trusted. PRD from Catalyst covered current state, future state, why now.
- **Group 3 — Portfolio Summary and Advisor Book.** Worked backwards from outputs to sources (advisor/CRM, trades, fund report); an ERD to drive the team discussion and PRD; clarified definitions; data quality validation; data owners and approvals called out; "presented in a unique CG way".
- **Group 4 (individual).** Used the Day-1 trick to make a summary document (PRD, contract, lineage diagrams, calculations); basis points: divide by 10,000 not 1,000; "what readers should not assume"; got near the end of Phase 2; imports were the hardest part; asked AI for a one-page summary of the day.

## Observations for next time

- Teams all picked the same two outputs; nudging tables to different outputs would make the share-out richer.
- The "reverse-map first, then build" shape worked; the opening discussion fills the morning's first hour.
- Finishing at 14:00 left time unused; the instructor plan now says 09:00–15:00 Monday–Thursday only and leaves Friday to the capstone guide.
