# Activity 12 — Atlas discovery worksheet

*Day 5 · Tables · 60 minutes*

Before anyone builds, understand the product. Choose at least two business-facing outputs (for example `rpt_portfolio_summary`, `rpt_advisor_book`, `agg_segment_aum`, `agg_instrument_activity`, `agg_fund_nav`, `ts_daily_market`, `api_latest_price`) and work backwards from consumer need to source data. Assign roles: facilitator, scribe, quality challenger, playback spokesperson. Fill one shared worksheet with the four sections below. Describe transformations in plain English; no SQL, no physical keys, no schema design yet.

**Produce**

- Producer–creator–consumer map: who supplies, who creates, who consumes each chosen output
- Consumer-backwards map: consumer need | output | required sources | rules and assumptions
- Mini-STTM for four to six important fields: target field | business meaning | source field(s) | transformation in English | check
- Shared glossary (AUM, position, latest price, gross value, fee, basis point, advisor book, valid trade) and trust questions (latest-price selection, invalid trades, fee calculation, reconciliation, no FX conversion)

**Finished early?** Draft a PRD or a data contract with Catalyst for one output.

**Debrief questions**

- Which definition did the table disagree about, and how did you settle it?
- Which assumption could make the result untrustworthy?
- Who is the consumer, and what decision changes?

**Timebox.** About 5 minutes on roles and the scenario, 10 choosing outputs and decisions, 15 to 25 on reverse-mapping and the mini-STTM, 10 on definitions and quality checks, 5 to 10 on playback. Playback: two to three minutes per table.

**Sources (seeds).** `trades` (Trading), `instruments` (Security Master), `portfolios` (Portfolio Administration), `clients` and `advisors` (CRM), `funds` and `fund_holdings` (Fund Reference).
