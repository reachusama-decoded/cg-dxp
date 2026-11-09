# The running example: the US end-of-day price sheet

One product carries every demo and fallback in the week, so the room sees the same thing go from a conversation to a scheduled pipeline. It is synthetic: fictional people, invented instruments mixed with real identifiers, no CG data.

| # | File | What it is | Lifecycle phase · Catalyst skill | Used on |
|---|---|---|---|---|
| 1 | `01-interview-transcript.md` | A creator interviewing a producer and a consumer (the Day 1 role-play, done well enough to generate from) | 2 Discovery · the interview, recorded and transcribed | Day 1 demo and fallback |
| 2 | `02-prd.md` | The PRD the `product-requirements-document` skill produces from that transcript, after review (corrections in brackets) | 2 Discovery · `product-requirements-document` | Day 1 debrief, Day 2 |
| 3 | `03-data-contract.md` | The data contract in the eight-section template, written from the PRD and reviewed | 3 Design · `data-contract` | Day 1, Day 2 |
| 3 | `03-data-contract-planted-errors.md` | The same contract with five invented details left in, for the "find the fabrication" check | 3 Design · a teaching variant of step 3 | Day 1 debriefs |
| 3 | `03-data-contract.html` | The contract rendered as a self-contained HTML page (what the Day 2 Markdown-to-HTML demo makes) | 3 Design · a rendering of step 3 | Day 2 |
| 4 | `04-sttm.md` | The source-to-target mapping: one rule per target column in the contract's schema, plus the row rules | 3 Design · `transformation-spec` | Day 2 STTM block, Day 3 |
| 5 | `05-service-levels.md` | The service levels: an indicator, objective and agreement per commitment, with its clock and measurement | 3 Design · `sla-dashboard-spec` | Day 2 service-levels block, Day 4 |

The implementation of this product is `day2-platform/demos/contract-to-code/eod_prices/` (dbt on DuckDB) and the `eod_prices_daily` DAG in `day4-airflow/demos/airflow_local/`.

## The order, and why

The numbers are the order of creation, which is the lifecycle's order: the interview produces the transcript; the PRD is generated from the transcript (why the product exists, who decides with it); the data contract is written from the PRD (what is promised, to whom); the mapping needs the contract's target schema (how each column is produced); the service levels need the consumer's decision time (the numbers the contract's SLA section promises). Each later document revises the one before it, which is what the contract's revision history is for. Only after the five are reviewed does the code start: the schema becomes models, the quality rules become tests, the mapping becomes the CTEs and the service levels become the schedule and the freshness gate (`courseware/day2-platform/demos/contract-to-code/eod_prices/` and the `eod_prices_daily` DAG in the Day 4 stack).
