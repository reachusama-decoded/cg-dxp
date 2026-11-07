Validate Challenge set 04 (Atlas capstone) end to end as a beginner trainee.

This is a maintainer validation run. Use the repository's `challenge-trainee-runs` skill and
follow `.github/skills/challenge-trainee-runs/SKILL.md` exactly. Use
`docs/challenge-run-brief.md` as the canonical trainee brief; do not improvise a shorter
brief or relax any of its audit rules.

Isolation is mandatory:

1. Create a clean, detached, isolated git worktree or clone at the commit being validated.
2. Prove the isolated path is accessible from the running devcontainer before proceeding.
3. Never run `mise run challenge:reset 04` in the maintainer's source checkout. Run reset only
   inside the isolated checkout.
4. Record the source commit, isolated path, host OS/architecture, devcontainer architecture,
   and initial `git status --porcelain`.
5. Run one challenge at a time. Stop any unrelated Astro stack first and check Docker
   headroom as required by the skill.

Role-play a beginner and follow `challenges/v1/04-atlas-capstone/README.md` literally, in order.
Run every printed command exactly as written. Do not work around a failure, add undocumented
flags, silently correct a command, or edit repository plumbing. If a documented command
fails, capture the relevant output and continue only when the guide permits it. A workaround
is a failed validation, even if it eventually produces green output.

Complete the entire learning path, not only the required MVP:

- Before-you-begin readiness checks.
- Phase 1 Sections 1-8, including the rendered Airflow UI inspection.
- The Phase 1 command using `ATLAS_VERIFY_SCOPE=mvp`; require `MVP LIVE PASS`.
- Every Phase 2 challenge in dependency order, using the dependency map in the guide.
- The required AI Catalyst checkpoint. Confirm that the AI Catalyst plugin is enabled and
  that the dbt best-practices skill actually runs. Do not count an ordinary unscoped chat
  response as a Catalyst pass.
- The `Use the product` queries and briefing. Check every reported value against query output
  and reject invented claims.
- The offline verifier and the full live completion verifier; require `LIVE PASS` for the
  latter.

Airflow validation must include both machine evidence and a real UI check:

- `astro dev run dags list-import-errors` returns no import errors.
- The DAG list includes the documented `atlas_elt_*` DAGs.
- Open the URL printed by `astro dev start`, navigate to `atlas_elt_advisors`, and inspect its
  Graph view.
- Confirm the schedule and visible task chain agree with
  `datasets/advisors/airflow/advisors.dag.yml`.
- Capture a screenshot when browser tooling is available. If visual interaction is not
  available, mark the UI check UNVERIFIED rather than PASS.

Audit the run independently before accepting the trainee report:

- Compare `git status --porcelain` with the allowed edit path from
  `docs/challenge-run-brief.md`.
- Inspect timestamp-bounded dbt invocation records in `data_products/atlas_elt/logs/dbt.log`
  and flag undocumented flags or repeated commands.
- Compare model and test results with dbt artifacts (`manifest.json` and
  `run_results.json`), not only terminal summaries.
- Confirm Phase 1 selected only its documented MVP scope and the full run selected the
  complete solution scope.
- Confirm Astro is stopped after the run.
- Independently reproduce every failure that would lead to a repository change. Treat an
  agent's proposed root cause as a hypothesis until reproduced.

Return a report containing:

1. Source commit, host OS/architecture, devcontainer architecture, and isolated path.
2. A PASS/FAIL/UNVERIFIED table for every README section and challenge.
3. Every command run, with repeats identified and explained.
4. For each failure: exact command, 10-30 relevant output lines, expected result, observed
   result, and whether it reproduced independently.
5. Phase 1 MVP verifier output and full live verifier output verbatim.
6. Airflow DAG/import/UI evidence and Catalyst invocation evidence.
7. Scope audit and dbt-artifact audit results.
8. Documentation mismatches, including successful commands whose output differs from the
   guide.
9. A final verdict: READY, READY WITH DOCUMENTATION FIXES, or NOT READY.

After auditing, append the required row to `docs/challenge-runs.md` from the maintainer
checkout, following the `challenge-trainee-runs` skill. Write an RCA only for a reproduced
root cause that was fixed. Do not copy trainee-authored challenge files back into the source
checkout. Remove the isolated worktree/clone only after all report evidence has been saved.
