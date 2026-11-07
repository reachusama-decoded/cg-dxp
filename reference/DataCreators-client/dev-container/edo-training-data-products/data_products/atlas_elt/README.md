# Atlas ELT

This native product is the retained v1 platform shell. Assigned v2 Atlas work starts from [challenges/v2/capstone](../../challenges/v2/capstone/README.md), which prepares independent attempts using the supplied Atlas CSVs.

Read [Atlas business and measure context](CG_CONTEXT.md) before interpreting account relationships, prices or compatibility labels such as `aum` and `performance`.

## Layer mapping

| Model pattern | Layer |
|---|---|
| `src_*` | `staging` |
| `dom_*` | `integration` |
| published marts | `prepared` |
| `rpt_portfolio_summary`, `rpt_advisor_book`, `rpt_advisor_leaderboard` | `integration` |

For this historical shell, see [v1 Atlas](../../challenges/v1/04-atlas-capstone/README.md).
