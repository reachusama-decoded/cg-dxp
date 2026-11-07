# The running example: the US end-of-day price sheet

One product carries every demo and fallback in the week, so the room sees the same thing go from a conversation to a scheduled pipeline. It is synthetic: fictional people, invented instruments mixed with real identifiers, no CG data.

| File | What it is | Used on |
|---|---|---|
| `interview-transcript.md` | A creator interviewing a producer and a consumer (the Day 1 role-play, done well enough to generate from) | Day 1 demo and fallback |
| `prd.md` | The PRD Catalyst's `product-requirements-document` skill produces from that transcript, after review | Day 1 debrief, Day 2 |
| `data-contract.md` | The data contract in Catalyst's eight-section template, reviewed | Day 1, Day 2 |
| `data-contract-planted-errors.md` | The same contract with five invented details left in, for the "find the fabrication" check | Day 1 Challenge 3 and 4 debriefs |
| `sttm.md` | The source-to-target mapping with one rule per target column plus the row rules | Day 2 STTM block, Day 3 |
| `service-levels.md` | SLIs, SLOs and SLAs for the product, with the measurement for each | Day 2 service-levels block |
| `data-contract.html` | The contract rendered as a self-contained HTML page (what the Day 2 Markdown-to-HTML demo makes) | Day 2 |

The implementation of this product is `day2-platform/demos/contract-to-code/eod_prices/` (dbt on DuckDB) and the `eod_prices_daily` DAG in `day4-airflow/demos/airflow_local/`.
