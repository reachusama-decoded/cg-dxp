# Compute Optimization Report

```yaml
Skill:          optimize-compute
Target:         {{ target.kind }}  # "job" or "warehouse"
Target Name:    {{ target.name or "n/a" }}
Target ID:      {{ target.id }}
Workspace:      {{ target.workspace_host or "n/a" }}
Generated:      {{ generated_at }}  # ISO-8601 UTC
```

## Scope

| Field               | Value                                       |
|---------------------|---------------------------------------------|
| Run history window  | {{ window.start }} to {{ window.end }}      |
| Total runs analyzed | {{ window.runs_analyzed }}                  |

{% if insufficient_data %}
> **Note:** {{ insufficient_data.reason }}
> The following rules were skipped for insufficient data: {% for s in insufficient_data.skipped_rules %}{{ s.rule_id if s is mapping else s }}{% if s is mapping and s.reason %} ({{ s.reason }}){% endif %}{% if not loop.last %}, {% endif %}{% endfor %}.
{% endif %}

## Executive Summary

| Severity  | Count                  |
|-----------|------------------------|
| error     | {{ counts.error }}     |
| warning   | {{ counts.warning }}   |
| info      | {{ counts.info }}      |
| **Total** | **{{ counts.total }}** |

### Top findings by impact

Ranked by severity (error > warning > info), ties broken by confidence (high > medium > low).

| Rank | Rule ID         | Title              | Severity              | Confidence              | Est. impact              |
|------|-----------------|--------------------|-----------------------|-------------------------|--------------------------|
{% for f in top_findings %}
| {{ loop.index }} | `{{ f.rule_id }}` | {{ f.title }} | {{ f.severity }} | {{ f.confidence }} | {{ f.estimated_impact or "n/a" }} |
{% endfor %}

---

## Findings

{% for f in findings %}
### `{{ f.rule_id }}` — {{ f.title }}

- **Severity:** {{ f.severity }}
- **Confidence:** {{ f.confidence }}
- **Apply mode:** {{ "supported" if f.apply_mode_supported else "manual review only" }}

**Evidence**

| Field   | Value         |
|---------|---------------|
{% for k, v in f.evidence.items() %}
| {{ k }} | {{ v }}       |
{% endfor %}

**Remediation**

{{ f.remediation.summary }}

Affected files: {{ f.remediation.affected_files | join(", ") or "n/a" }}

```diff
{% for key, delta in f.remediation.config_delta.items() %}
{% if delta.delete %}
- {{ key }}: {{ delta.current }}
# DELETE {{ key }}
{% elif delta.add %}
# ADD {{ key }}
+ {{ key }}: {{ delta.proposed }}
{% else %}
- {{ key }}: {{ delta.current }}
+ {{ key }}: {{ delta.proposed }}
{% endif %}
{% endfor %}
```

{% if f.apply_mode_supported %}
Apply this with: `apply {{ f.rule_id }}`
{% endif %}

---
{% endfor %}

## Next steps

1. Review each finding above and confirm the recommended config delta.
2. Apply the change manually in the affected file(s) listed for each finding. Apply mode is not shipped in this release; when it lands (Phase 2), supported findings will surface an `apply <RULE_ID>` hint inline.
3. Re-run `optimize-compute` after applying changes to confirm the finding clears (some rules require a fresh 30-day run window to re-evaluate).
4. For unresolved findings, see `references/findings-catalog.md` for the full rationale and links to Databricks docs.
