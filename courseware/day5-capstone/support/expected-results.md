# Atlas capstone: expected results (from the solution build on DuckDB)

Numbers come from the supplied seeds and the solution models, so a learner's Databricks build of the same models should match. Money is in native trade currency (no FX), as the brief says.

## Row counts per model

| Model | Layer | Rows |
|---|---|---:|
| `agg_fund_nav` | consumer-aligned | 60 |
| `agg_instrument_activity` | consumer-aligned | 788 |
| `agg_segment_aum` | consumer-aligned | 4 |
| `api_latest_price` | consumer-aligned | 788 |
| `dom_fund__fund` | domain-aligned | 60 |
| `dom_fund__holding` | domain-aligned | 3,205 |
| `dom_instrument__instrument` | domain-aligned | 1,500 |
| `dom_party__advisor` | domain-aligned | 120 |
| `dom_party__client` | domain-aligned | 2,000 |
| `dom_portfolio__portfolio` | domain-aligned | 2,500 |
| `dom_positions__position` | domain-aligned | 3,717 |
| `dom_trading__latest_price` | domain-aligned | 788 |
| `dom_trading__trade` | domain-aligned | 9,880 |
| `portfolios_snapshot` | snapshot (Phase 2) | 2,500 |
| `rpt_advisor_book` | consumer-aligned | 120 |
| `rpt_advisor_leaderboard` | consumer-aligned | 120 |
| `rpt_portfolio_performance` | consumer-aligned | 1,028 |
| `rpt_portfolio_summary` | consumer-aligned | 1,028 |
| `rpt_region_report` | consumer-aligned | 6 |
| `src_crm__advisors` | source-aligned | 120 |
| `src_crm__clients` | source-aligned | 2,002 |
| `src_fundref__fund_holdings` | source-aligned | 3,205 |
| `src_fundref__funds` | source-aligned | 60 |
| `src_portfolio__portfolios` | source-aligned | 2,501 |
| `src_secmaster__instruments` | source-aligned | 1,502 |
| `src_trading__trades` | source-aligned | 10,000 |
| `ts_daily_asset_class` | consumer-aligned | 1,789 |
| `ts_daily_market` | consumer-aligned | 520 |
| `ts_daily_market_incremental` | consumer-aligned | 520 |

## Seeds

| seed | rows |
|---|---|
| trades | 10000 |
| instruments | 1502 |
| portfolios | 2501 |
| clients | 2002 |
| advisors | 120 |
| funds | 60 |
| fund_holdings | 3205 |

## Valid trades vs raw trades (the domain filter: qty > 0, price_cents > 0, side in B/S)

| raw_trades | valid_trades | trade_days | first_day | last_day |
|---|---|---|---|---|
| 10000 | 9880 | 520 | 2024-06-03 | 2026-05-29 |

## Advisor leaderboard, top 10 by book AUM

| rank | advisor_id | advisor_name | region | book_aum | fees_generated |
|---|---|---|---|---|---|
| 1 | 72 | William Vaughan | Zurich | 551,154,146.77 | 248,440.62 |
| 2 | 9 | Oliver Thorne | NewYork | 513,369,922.83 | 252,885.96 |
| 3 | 67 | Grace Sinclair | HongKong | 376,394,756.52 | 139,701.75 |
| 4 | 83 | Beatrice Hollis | NewYork | 372,009,975.21 | 190,797.90 |
| 5 | 39 | George Wexford | NewYork | 308,068,144.96 | 194,520.75 |
| 6 | 97 | Olivia Ashworth | Zurich | 289,219,472.32 | 182,172.14 |
| 7 | 27 | Edward Merrick | Zurich | 283,334,766.96 | 146,043.18 |
| 8 | 66 | Beatrice Merrick | Singapore | 280,294,530.73 | 120,631.84 |
| 9 | 54 | Edward Hollis | Zurich | 263,422,577.51 | 136,192.40 |
| 10 | 47 | Emily Thorne | NewYork | 263,086,127.41 | 155,160.38 |

## Segment AUM

| segment | clients | portfolios | aum |
|---|---|---|---|
| Institutional | 59 | 103 | 4,736,807,535.72 |
| UHNW | 119 | 192 | 1,697,924,446.95 |
| HNW | 200 | 227 | 236,390,671.74 |
| Retail | 506 | 506 | 50,695,494.58 |

## Region report

| region | portfolios | clients | aum | fees_generated |
|---|---|---|---|---|
| Zurich | 287 | 246 | 1,978,757,922.56 | 1,242,520.18 |
| NewYork | 241 | 197 | 1,693,714,454.67 | 1,050,718.43 |
| London | 207 | 185 | 1,083,797,948.90 | 719,318.14 |
| HongKong | 140 | 125 | 987,836,625.34 | 538,619.27 |
| Singapore | 85 | 73 | 694,630,664.49 | 365,299.46 |
| Dubai | 68 | 58 | 283,080,533.03 | 215,457.40 |

## Portfolio summary, five largest

| portfolio_id | strategy | client_name | segment | advisor_name | positions | aum | fees_paid | trades |
|---|---|---|---|---|---|---|---|---|
| 892 | Balanced | Tindall Investment Trust | Institutional | Olivia Sinclair | 12 | 133,208,598.49 | 41,453.88 | 29 |
| 2402 | Growth | Stonebridge Endowment | Institutional | Beatrice Merrick | 12 | 119,389,355.81 | 38,993.21 | 40 |
| 2377 | Income | Quillon Insurance Group | Institutional | William Vaughan | 9 | 116,662,315.59 | 37,899.94 | 30 |
| 2439 | Growth | Ravenswood Endowment | Institutional | Edward Merrick | 10 | 116,313,025.97 | 56,675.44 | 30 |
| 2026 | Balanced | Ravenswood Endowment | Institutional | William Vaughan | 12 | 92,022,957.40 | 30,716.16 | 31 |

## Totals that must reconcile (the four singular tests)

| summary_aum | advisor_book_aum | segment_aum | region_aum | position_trades | daily_trades | instrument_trades |
|---|---|---|---|---|---|---|
| 6,721,818,148.99 | 6,721,818,148.99 | 6,721,818,148.99 | 6,721,818,148.99 | 9880 | 9880 | 9880 |

## Instrument activity, top 5 by value traded

| ticker | asset_class | sector | qty_traded | value_traded | trades |
|---|---|---|---|---|---|
| JP8BJZVTNF85 | Bond | Government | 6880336 | 712,706,756.60 | 564 |
| HKC3770LK5N7 | Bond | Corporate | 7951573 | 703,106,665.08 | 480 |
| GBVPHF2MR9P4 | Bond | Corporate | 5555993 | 523,914,074.60 | 481 |
| 1730.HK | ETF | Broad | 4115442 | 521,185,213.86 | 612 |
| XZB | Equity | Industrials | 15175130 | 520,482,089.13 | 472 |

## Daily market, first 5 days

| trade_date | traded_value | fees | trades |
|---|---|---|---|
| 2024-06-03 | 3,288,376.48 | 2,410.15 | 11 |
| 2024-06-04 | 21,914,793.76 | 11,435.29 | 16 |
| 2024-06-05 | 11,305,809.08 | 6,394.09 | 14 |
| 2024-06-06 | 14,771,454.64 | 9,511.63 | 15 |
| 2024-06-07 | 8,659,413.97 | 4,294.40 | 10 |

## Fund NAV, top 5

| fund_id | name | style | holdings | nav_per_100_units |
|---|---|---|---|---|
| 4 | Orion Core Bond Fund | FixedIncome | 24 | 101.54 |
| 14 | Vantage Core Bond Fund | FixedIncome | 50 | 100.12 |
| 40 | Beacon Core Bond Fund | FixedIncome | 31 | 99.99 |
| 13 | Vantage Core Bond Fund | FixedIncome | 38 | 99.72 |
| 60 | Orion Core Bond Fund | FixedIncome | 27 | 98.10 |

## Latest price lookup, sample

| instrument_id | last_price | last_ts |
|---|---|---|
| 1 | 53.80 | 1780068649 |
| 2 | 109.95 | 1780049110 |
| 3 | 132.02 | 1780071034 |
| 4 | 41.10 | 1780049026 |
| 5 | 5.71 | 1780053433 |
