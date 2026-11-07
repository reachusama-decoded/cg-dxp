# dbt Pre-Deploy Validation — {{DATA_PRODUCT}} / {{SELECTOR}}

- **Target:** {{TARGET}} (maps to the profiles.yml / bundle target entry)
- **Mode:** {{MODE}}  ·  **Run mode:** {{INLINE_OR_ONDISK}}
- **Timestamp:** {{TIMESTAMP}}

VERDICT: {{DEPLOY_READY|BLOCKED}} — {{N}} blocker, {{N}} advisory, {{N}} ok, {{N}} n-a

> `DEPLOY_READY` iff zero blockers. CI (and the planned /deploy-dab partner) read this line.

---

## Summary

| Gate | blocker | advisory | ok | n-a |
|---|---|---|---|---|
| 1 · Compile check | {{N}} | {{N}} | {{N}} | {{N}} |
| 2 · Schema diff vs target | {{N}} | {{N}} | {{N}} | {{N}} |
| 3 · Test resolution | {{N}} | {{N}} | {{N}} | {{N}} |

---

## Gate 1 — Compile check

<!-- One row per finding. Omit the table if the gate is fully ok. -->

| Severity | Rule | Location | Finding | Remediation |
|---|---|---|---|---|
| {{blocker\|advisory\|ok\|n-a}} | {{SQL-DBSQL-NNN or —}} | {{model / file:line}} | {{one line}} | {{one line — points at /troubleshoot-dbt-on-databricks or an authoring skill}} |

## Gate 2 — Schema diff against target

| Severity | Change | Relation | Column | Remediation |
|---|---|---|---|---|
| {{blocker\|advisory\|ok\|n-a}} | {{additive\|breaking}} | {{catalog.schema.relation}} | {{column (type→type)}} | {{one line}} |

## Gate 3 — Test resolution

| Severity | Rule | Test / PK | Finding | Remediation |
|---|---|---|---|---|
| {{blocker\|advisory\|ok\|n-a}} | {{SQL-DBSQL-006 or —}} | {{test name / pk column}} | {{one line}} | {{one line}} |

---

## Next steps

<!-- Ordered list, blockers first. Each step names the skill to consult.
     If DEPLOY_READY, the final step notes the change is deploy-ready and to
     proceed with the bundle deploy (the /deploy-dab partner is planned, G-01). -->

1. {{blocker fix — /troubleshoot-dbt-on-databricks or authoring skill}}
2. {{advisory — review before merging}}
3. {{if DEPLOY_READY: change is deploy-ready — proceed with your bundle deploy; the paired /deploy-dab gate is planned (G-01), not yet built}}
