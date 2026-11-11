# Activity 9b — Second look at yesterday's AI-generated dbt

*Day 3 · Pairs · 15 minutes*

Yesterday Copilot and Catalyst generated a dbt project from your contract, before you knew dbt. This morning you wrote down two things in it you could not judge. Reopen that project with a partner (if yours did not finish, use your partner's) and review it in graph order: the sources, then staging, then the joins, then the tests, then anything nobody asked for. For each of your two notes, decide whether you can judge it now.

**Produce**

- Your two morning notes, each marked: can judge now, or still cannot
- One thing you catch now that you could not have caught yesterday, with the file it is in
- One thing you still cannot judge, for the questions table

**Debrief questions**

- What did you catch today that you would have approved yesterday?
- Which file did you open first, and why that one?
- Did the AI write anything nobody asked for? What would you delete?

**What to look for, in order**

| Where | Ask |
|---|---|
| `sources.yml` | Is every raw table declared, or are there hard-coded table names in the SQL? |
| Staging models | One row per what? Are names, types and codes cleaned here, and are duplicates handled? |
| Joins | Are the keys unique on the right-hand side? What happens to a row with no match: dropped, null, or a silent default? |
| Tests | Does each promise in your contract (keys, not null, accepted values, a reconciliation) have a test? Would any test fail if the data were wrong? |
| `dbt_project.yml`, `config()` | Which models are views and which are tables, and is that what consumers need? |
| Everything else | Which files, models or macros did nobody ask for? |

Open one model's file under `target/compiled/` if you are unsure what the warehouse receives.
