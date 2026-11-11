# Activity 9b — Second look at yesterday's AI-generated dbt

*Day 3 · Pairs · 15 minutes*

Yesterday Copilot and Catalyst generated a dbt project from your contract, before you knew dbt. First, write down two things in that project you could not judge yesterday. Then reopen it with a partner (if yours did not finish, use your partner's) and assess it in graph order: the sources, then staging, then the joins, then the tests, then anything nobody asked for. Finally, pick one thing you caught and prompt Copilot again to fix it: name the file, say what is wrong and say how you will check the fix. Read what it changed and run the check.

**Produce**

- Two things you could not judge yesterday, each marked: can judge now, or still cannot
- One thing you catch now that you would have approved yesterday, with the file it is in
- The prompt you wrote to fix it, and whether the fix passed your check
- One thing you still cannot judge, for the questions table

**Debrief questions**

- What did you catch today that you would have approved yesterday?
- How is today's prompt different from yesterday's?
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
