#!/usr/bin/env python3
"""What the Spark engine is, in two minutes on a laptop: a driver plans a query, executors run
it over partitions of data, and you write SQL. Databricks runs this for you on many machines.
Run:  python demo.py            python demo.py --hold 90   (keeps the Spark UI at :4040 open)"""
from __future__ import annotations
import os, pathlib, sys, time
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
from pyspark.sql import SparkSession

HERE = pathlib.Path(__file__).resolve().parent
PRICES = HERE.parent / "contract-to-code" / "eod_prices" / "seeds" / "vendor_prices_raw.csv"
hold = int(sys.argv[sys.argv.index("--hold") + 1]) if "--hold" in sys.argv else 0

def step(n, title): print(f"\n\033[1;34m== {n}. {title} ==\033[0m")

step(1, "A Spark session: one driver, several executors (here: 4 local cores)")
spark = SparkSession.builder.master("local[4]").appName("data-creators-spark").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
print(f"   Spark {spark.version}; Spark UI: {spark.sparkContext.uiWebUrl}")

step(2, "Data is read in partitions; each executor works on its own slice")
prices = spark.read.option("header", True).option("inferSchema", True).csv(str(PRICES))
big = prices.crossJoin(spark.range(0, 2000).withColumnRenamed("id", "copy"))   # make it big enough to see work
print(f"   rows: {big.count():,}  partitions: {big.rdd.getNumPartitions()}")

step(3, "You write SQL; the driver plans it; the plan shows the stages (look for Exchange = a shuffle)")
big.createOrReplaceTempView("vendor_prices")
q = spark.sql("select px_date, px_ccy, count(*) as prices, round(avg(px_close), 4) as avg_close from vendor_prices group by 1, 2 order by 1, 2")
q.explain()

step(4, "Run it: tasks on executors, results combined")
t0 = time.time(); rows = q.collect(); print(f"   {len(rows)} result rows in {time.time() - t0:.1f}s")
for r in rows[:6]:
    print("  ", r.px_date, r.px_ccy, r.prices, r.avg_close)

step(5, "On Databricks: the same SQL (from dbt) on a cluster of machines, reading Delta tables in S3")
print("   dbt compiles your model to SQL -> Databricks plans it with Spark -> executors read Parquet files under the Delta log -> a new Delta version is written.")
if hold:
    print(f"\n   Holding {hold}s so you can open the Spark UI: {spark.sparkContext.uiWebUrl}  (Jobs, Stages, SQL tabs)")
    time.sleep(hold)
spark.stop()
