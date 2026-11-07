# Profiling Checklist

Use this checklist when executing the `profile-columns` capability skill.

## 1) Metadata

```sql
DESCRIBE TABLE <catalog>.<schema>.<table>;
```

Capture:
- column list + types
- partition columns (often includes `year__`, `month__`, `day__`, `time__`)

## 2) Row counts

```sql
SELECT COUNT(*) AS row_count
FROM <catalog>.<schema>.<table>;
```

Optional filtered slice (example):

```sql
SELECT COUNT(*) AS row_count
FROM <catalog>.<schema>.<table>
WHERE <date_col> >= DATEADD(MONTH, -24, CURRENT_DATE());
```

## 3) Grain validation

Given grain `(k1, k2, ..., kn)`:

```sql
SELECT COUNT(*) AS duplicate_key_groups
FROM (
  SELECT k1, k2, /* ... */, kn, COUNT(*) AS c
  FROM <catalog>.<schema>.<table>
  GROUP BY k1, k2, /* ... */, kn
  HAVING COUNT(*) > 1
) d;
```

## 4) Null checks for critical columns

```sql
SELECT
  SUM(CASE WHEN k1 IS NULL THEN 1 ELSE 0 END) AS null_k1,
  SUM(CASE WHEN k2 IS NULL THEN 1 ELSE 0 END) AS null_k2
FROM <catalog>.<schema>.<table>;
```

## 5) Batch column profiling template

For columns `[c1, c2, c3, c4, c5]`:

```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(*) - COUNT(`c1`) AS c1_null_count,
  APPROX_COUNT_DISTINCT(`c1`) AS c1_distinct_count,
  CAST(MIN(`c1`) AS STRING) AS c1_min,
  CAST(MAX(`c1`) AS STRING) AS c1_max,
  COUNT(*) - COUNT(`c2`) AS c2_null_count,
  APPROX_COUNT_DISTINCT(`c2`) AS c2_distinct_count,
  CAST(MIN(`c2`) AS STRING) AS c2_min,
  CAST(MAX(`c2`) AS STRING) AS c2_max
  -- repeat per column
FROM <catalog>.<schema>.<table>;
```

## 6) Metric distribution sanity checks

```sql
SELECT
  MIN(metric) AS min_metric,
  APPROX_PERCENTILE(metric, 0.01) AS p01,
  APPROX_PERCENTILE(metric, 0.50) AS p50,
  APPROX_PERCENTILE(metric, 0.99) AS p99,
  MAX(metric) AS max_metric
FROM <catalog>.<schema>.<table>;
```

## 7) Write-back gate

Before moving on to model generation, update the model spec:

- `grain` (confirm or revise)
- `columns` types + `not_null`
- `business_logic` notes about deduping/versioning
- suggested tests (in spec notes or dbt schema.yml)
