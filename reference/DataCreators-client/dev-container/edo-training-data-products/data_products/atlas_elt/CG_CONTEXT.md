# Atlas business and measure context

Atlas is a fictional advisory client-account reporting case, not a Capital Group organisation chart or internal investment schema. Its `portfolio_id` denotes a synthetic client investment container; `advisor_id` denotes a client-relationship role, not a CG portfolio manager or sleeve assignment. The current assessed route is the separately prepared v2 capstone; the native product remains a historical platform shell.

The supplied seven CSVs describe clients, advisors, accounts, instruments, executions, funds and fund/instrument reference weights. Account `client_id` and `advisor_id` are separate dimension relationships. Trades connect an account to an instrument. The fund weights have no account key, dated quantity or ownership bridge: shared instruments do not prove that an account owns a fund. Target versus actual weight semantics are not established. The finite account-report core does not require that branch.

Current v2 eligibility keeps positive raw quantity and price and side B/S: 10,000 raw executions yield 9,880 valid executions, 3,717 account/instrument activity groups and 1,028 active account summaries out of 2,500 conformed accounts. The 1,472 inactive accounts are expected exclusions under this contract. These counts describe the supplied fixture, not CG business populations.

The supplied execution history spans 3 June 2024 to 29 May 2026 UTC. Position quantities are net signed quantities from qualifying trades; opening balances, cash, corporate actions and other changes are absent. Do not infer zero opening holdings or authorised shorting. Latest-price selection uses the newest qualifying execution per instrument across supplied accounts, with timestamp/trade-ID tie-breaking. No independent valuation feed or separate reporting cutoff is applied. Currency conversion is absent, so nominal sums and ranks cannot identify the largest comparable real managed book.

| Compatible identifier | Display meaning |
|---|---|
| `net_qty` | Net trade-derived quantity, not established complete holdings |
| `market_value`, `aum` | Estimated trade-derived position value using the execution-price proxy |
| `book_aum` | Advisor aggregate of that restricted nominal value |
| `positions` | Instrument groups with qualifying activity, including zero-net groups |
| `fees_paid`, `fees_generated` | Transaction charges paid, not management fees or advisor revenue |
| `net_flow` | Purchase value less sale value, not external cash flow or cash balance |
| `rpt_portfolio_performance` | Account trading activity and transaction costs, not investment return |

Prices convert cents to currency units; fees use positive execution quantity × execution price × basis points / 10,000. Fee calculations must not substitute a later valuation proxy. Cost basis, realised/unrealised gains, official NAV and investment returns require separately designed inputs and rules. Retain compatible identifiers, fixture arithmetic and independent reconciliation while publishing their scoped meaning.

A source-owning team supplies data through CSV artifacts; a product creator builds the contracted output; a business owner agrees meaning; a consumer uses it. These are illustrative responsibilities rather than verified CG department assignments. Require actual keys for each generated diagram edge and keep unresolved assumptions visible. Upstream trade checks do not replace downstream join-multiplicity, membership, aggregate or consumer-label checks.
