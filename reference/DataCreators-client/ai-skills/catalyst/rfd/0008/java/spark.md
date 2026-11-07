# JV-SPARK: Spark

Spark-on-JVM patterns: DataFrame chains, UDFs, serialization, encoders.

## JV-SPARK-001 — Chain DataFrame transformations one per line

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Each transformation in a DataFrame chain on its own line.
Extract complex chains into named methods.

**Examples.**
```java
// ✓
Dataset<Row> result = spark.read()
    .format("delta")
    .load(inputPath)
    .filter(col("status").equalTo("active"))
    .withColumn("processed_at", current_timestamp())
    .select("id", "name", "processed_at");
```

## JV-SPARK-002 — Extract complex transformations into named methods

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `Dataset.transform(this::method)` to compose named
transformation steps.

**Examples.**
```java
Dataset<Row> result = loadInput(spark, inputPath)
    .transform(this::filterActive)
    .transform(this::addAuditColumns)
    .transform(this::selectOutputColumns);

private Dataset<Row> filterActive(Dataset<Row> df) {
    return df.filter(col("status").equalTo("active"));
}
```

## JV-SPARK-003 — Avoid UDFs when built-in functions work

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `org.apache.spark.sql.functions.*` whenever possible.
UDFs are opaque to Catalyst, prevent predicate pushdown, and incur
serialization overhead.

**Examples.**
```java
// ✓
import static org.apache.spark.sql.functions.*;

Dataset<Row> result = df
    .withColumn("name_upper", upper(col("name")))
    .withColumn("year", year(col("created_at")));
```

## JV-SPARK-004 — UDFs handle nulls explicitly; never throw

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** When a UDF is unavoidable, handle `null` inputs explicitly
and never throw exceptions — they kill the entire stage.

**Examples.**
```java
UDF1<String, String> normalizePhone = (phone) -> {
    if (phone == null) return null;
    return phone.replaceAll("[^0-9]", "");
};
spark.udf().register("normalize_phone", normalizePhone, DataTypes.StringType);
```

## JV-SPARK-005 — Closures must be serializable; extract values from `this`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Spark closures cannot capture non-serializable outer
classes. Extract the needed value into a local variable before the
closure.

**Examples.**
```java
// ✗ captures non-serializable enclosing class
public class Pipeline {
    private final DataSource dataSource;  // not Serializable
    public void run(Dataset<Row> df) {
        df.map(row -> dataSource.lookup(row.getString(0)), encoder);
        // NotSerializableException at runtime
    }
}

// ✓ extract serializable value first
public void run(Dataset<Row> df) {
    String lookupUrl = dataSource.getUrl();  // String is Serializable
    df.map(row -> RemoteLookup.lookup(lookupUrl, row.getString(0)), encoder);
}
```

## JV-SPARK-006 — Use `Broadcast` for read-only data larger than a few KB

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Lookup tables larger than a few KB go through a
`Broadcast` variable instead of being captured by closures.

**Examples.**
```java
Broadcast<Map<String, String>> lookupBroadcast =
    spark.sparkContext().broadcast(lookupMap, classTag(Map.class));

df.map(row -> {
    Map<String, String> lookup = lookupBroadcast.value();
    return lookup.getOrDefault(row.getString(0), "unknown");
}, Encoders.STRING());
```

## JV-SPARK-007 — Always specify explicit `Encoder`s with `Dataset.map()`

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Don't rely on implicit encoder resolution. Pass the encoder
explicitly.
