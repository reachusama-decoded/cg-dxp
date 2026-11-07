# Activity 8 — Generate and investigate

*Day 2 · Pairs · 50 minutes*

Give Catalyst your reviewed PRD, contract, mapping and a few sample records; resolve any conflicts between them first. Ask for a dbt project. If you have no source data, ask for simulated data that matches the contract. Add explanatory comments and get instructions for running it and finding the output. Then ask for Airflow orchestration matching the contract's cadence or trigger, and for an explanation of the code and how to run it. Run what you can; inspect the results; prepare one discovery and one correction for the debrief.

**Produce**

- A dbt project generated from the contract, with comments
- An Airflow DAG matching the contract's schedule
- Where the output landed (the schema in Databricks), or why it did not
- One discovery and one correction

**Finished early?** Choose one: how is a missing input handled? can a lookup duplicate rows? what happens when the same input is processed twice? Propose the expected result and a check; report it in the debrief. Experienced: investigate the bitemporal macro, or logging from Airflow to Datadog.

**Debrief questions**

- Which design choice did the generator make for you, and would you keep it?
- Which edge case did the contract not mention?
- What did you correct: the specification, or the implementation?

**Prompts.** `/ai-catalyst setup-dbt-project` with the contract and mapping attached · `/ai-catalyst write-dbt-model` for each layer · "Add a comment above every CTE saying which STTM rule it implements" · "How do I run this, and where will the tables appear?" · `/ai-catalyst generate-dag` "Schedule for the contract's delivery commitment; check source freshness first."

**Running.** From the project folder: `dbt debug`, `dbt seed`, `dbt build`, `dbt show --select <model> --limit 5`. Tables land in `training_dev.training_<username>` in the Databricks catalog.
