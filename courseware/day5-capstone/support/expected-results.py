#!/usr/bin/env python3
"""Query the Atlas DuckDB warehouse (built by atlas_duckdb/build.sh) and write
expected-results.md: row counts and the headline numbers an instructor can compare
against a learner's Databricks output during the capstone."""
import os, pathlib, duckdb
here = pathlib.Path(__file__).resolve().parent
db = os.environ.get("ATLAS_DUCKDB_PATH", str(here / "atlas_duckdb/warehouse/training_dev.duckdb"))
con = duckdb.connect(db, read_only=True)
S = "training_demo"
out = ["# Atlas capstone: expected results (from the solution build on DuckDB)", "",
       "Numbers come from the supplied seeds and the solution models, so a learner's Databricks build of the same models should match. Money is in native trade currency (no FX), as the brief says.", ""]
out += ["## Row counts per model", "", "| Model | Layer | Rows |", "|---|---|---:|"]
layer = {"src_": "source-aligned", "dom_": "domain-aligned"}
for (n,) in con.execute(f"select table_name from information_schema.tables where table_schema='{S}' and table_name not in (select table_name from information_schema.tables where table_schema='{S}' and table_type='BASE TABLE' and table_name in ('trades','instruments','portfolios','clients','advisors','funds','fund_holdings')) order by 1").fetchall():
    if n.endswith("_snapshot"): lay = "snapshot (Phase 2)"
    else: lay = layer.get(n[:4], "consumer-aligned")
    c = con.execute(f'select count(*) from {S}."{n}"').fetchone()[0]
    out.append(f"| `{n}` | {lay} | {c:,} |")
def table(title, sql, note=""):
    out.extend(["", f"## {title}", ""])
    if note: out.extend([note, ""])
    rel = con.execute(sql); cols = [d[0] for d in rel.description]; rows = rel.fetchall()
    out.append("| " + " | ".join(cols) + " |"); out.append("|" + "---|" * len(cols))
    for r in rows:
        out.append("| " + " | ".join(f"{v:,.2f}" if isinstance(v, float) else str(v) for v in r) + " |")
table("Seeds", f"select 'trades' as seed, count(*) as rows from {S}.trades union all select 'instruments', count(*) from {S}.instruments union all select 'portfolios', count(*) from {S}.portfolios union all select 'clients', count(*) from {S}.clients union all select 'advisors', count(*) from {S}.advisors union all select 'funds', count(*) from {S}.funds union all select 'fund_holdings', count(*) from {S}.fund_holdings")
table("Valid trades vs raw trades (the domain filter: qty > 0, price_cents > 0, side in B/S)",
      f"select (select count(*) from {S}.src_trading__trades) as raw_trades, (select count(*) from {S}.dom_trading__trade) as valid_trades, (select count(distinct trade_date) from {S}.dom_trading__trade) as trade_days, (select min(trade_date) from {S}.dom_trading__trade) as first_day, (select max(trade_date) from {S}.dom_trading__trade) as last_day")
table("Advisor leaderboard, top 10 by book AUM", f"select rank, advisor_id, advisor_name, region, round(book_aum, 2) as book_aum, round(fees_generated, 2) as fees_generated from {S}.rpt_advisor_leaderboard order by rank limit 10")
table("Segment AUM", f"select segment, clients, portfolios, round(aum, 2) as aum from {S}.agg_segment_aum order by aum desc")
table("Region report", f"select region, portfolios, clients, round(aum, 2) as aum, round(fees_generated, 2) as fees_generated from {S}.rpt_region_report order by aum desc")
table("Portfolio summary, five largest", f"select portfolio_id, strategy, client_name, segment, advisor_name, positions, round(aum, 2) as aum, round(fees_paid, 2) as fees_paid, trades from {S}.rpt_portfolio_summary order by aum desc limit 5")
table("Totals that must reconcile (the four singular tests)",
      f"select round((select sum(aum) from {S}.rpt_portfolio_summary), 2) as summary_aum, round((select sum(book_aum) from {S}.rpt_advisor_book), 2) as advisor_book_aum, round((select sum(aum) from {S}.agg_segment_aum), 2) as segment_aum, round((select sum(aum) from {S}.rpt_region_report), 2) as region_aum, (select sum(trades) from {S}.dom_positions__position) as position_trades, (select sum(trades) from {S}.ts_daily_market) as daily_trades, (select sum(trades) from {S}.agg_instrument_activity) as instrument_trades")
table("Instrument activity, top 5 by value traded", f"select ticker, asset_class, sector, qty_traded, round(value_traded, 2) as value_traded, trades from {S}.agg_instrument_activity order by value_traded desc limit 5")
table("Daily market, first 5 days", f"select trade_date, round(traded_value, 2) as traded_value, round(fees, 2) as fees, trades from {S}.ts_daily_market order by trade_date limit 5")
table("Fund NAV, top 5", f"select fund_id, name, style, holdings, round(nav_per_100_units, 4) as nav_per_100_units from {S}.agg_fund_nav order by nav_per_100_units desc limit 5")
table("Latest price lookup, sample", f"select instrument_id, round(last_price, 2) as last_price, last_ts from {S}.api_latest_price order by instrument_id limit 5")
(here / "expected-results.md").write_text("\n".join(out) + "\n")
print("\n".join(out[:12])); print("..."); print(f"written {here / 'expected-results.md'}")
