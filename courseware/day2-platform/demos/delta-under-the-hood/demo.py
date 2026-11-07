#!/usr/bin/env python3
"""Delta under the hood, on a laptop: what a Delta table is made of, what a transaction log
gives you (versions, time travel, merge), and how an engine (DuckDB here, Spark on Databricks)
reads it. Run:  python demo.py            Prints each step; writes to ./warehouse/prices_delta."""
from __future__ import annotations
import json, pathlib, shutil, sys
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
from deltalake import DeltaTable, write_deltalake

HERE = pathlib.Path(__file__).resolve().parent
TABLE = HERE / "warehouse" / "prices_delta"
SEED = HERE.parent / "contract-to-code" / "eod_prices" / "seeds" / "vendor_prices_raw.csv"
STR = pacsv.ConvertOptions(column_types={"px_date": pa.string(), "vendor_ts": pa.string(), "_received_at": pa.string()})

def read_day(day: str):
    """One day's vendor file, deduplicated to the latest delivery per ISIN (STTM rule R1)."""
    import duckdb
    t = pacsv.read_csv(SEED, convert_options=STR)
    return duckdb.sql(f"select * from t where px_date = '{day}' qualify row_number() over (partition by isin order by vendor_ts desc) = 1").arrow()

def step(n, title):
    print(f"\n\033[1;34m== {n}. {title} ==\033[0m")

def tree():
    for p in sorted(TABLE.rglob("*")):
        if p.is_file():
            print(f"   {p.relative_to(TABLE)}  ({p.stat().st_size:,} bytes)")

shutil.rmtree(TABLE, ignore_errors=True)
TABLE.parent.mkdir(parents=True, exist_ok=True)

step(1, "A Delta table is Parquet files plus a transaction log")
day1 = read_day("2026-11-03")
write_deltalake(TABLE, day1, mode="overwrite")
tree()
print("   -> _delta_log/00000000000000000000.json is commit 0: which Parquet files make up version 0")

step(2, "Append the next day's file: a new commit, old files untouched")
day2 = read_day("2026-11-04")
write_deltalake(TABLE, day2, mode="append")
tree()
dt = DeltaTable(TABLE)
print(f"   version {dt.version()}, {dt.to_pyarrow_table().num_rows} rows")

step(3, "The log is readable JSON: each commit records what it added or removed")
commit = TABLE / "_delta_log" / "00000000000000000001.json"
for line in commit.read_text().splitlines()[:3]:
    rec = json.loads(line)
    key = next(iter(rec)); print(f"   {key}: {json.dumps(rec[key])[:110]}...")

step(4, "MERGE: a vendor correction becomes an upsert, not a rewrite by hand")
correction = pa.table({"isin": ["US0378331005"], "px_date": ["2026-11-04"], "px_close": [231.5], "px_ccy": ["USD"],
                       "vendor_ts": ["2026-11-04 23:30:00"], "_received_at": ["2026-11-04 23:35:00"]})
(dt.merge(source=correction, predicate="t.isin = s.isin and t.px_date = s.px_date", source_alias="s", target_alias="t")
   .when_matched_update_all().when_not_matched_insert_all().execute())
dt = DeltaTable(TABLE)
print(f"   version {dt.version()} after merge")

step(5, "History and time travel: every write is a version you can read back")
for h in dt.history():
    print(f"   v{h['version']}  {h['operation']:<9} {h.get('operationParameters', {}).get('mode', '')}")
v0 = DeltaTable(TABLE, version=0).to_pyarrow_table()
now = dt.to_pyarrow_table()
print(f"   VERSION AS OF 0: {v0.num_rows} rows   |   current: {now.num_rows} rows")
aapl_now = now.filter(pc.equal(now["isin"], "US0378331005")).to_pylist()
print("   AAPL rows now:", [(r["px_date"], r["px_close"]) for r in aapl_now])

step(6, "OPTIMIZE: compact small files; VACUUM: remove files no version needs")
print("  ", dt.optimize.compact())
tree()

step(7, "Any engine that speaks Delta can read it: DuckDB here, Spark on Databricks")
import duckdb
con = duckdb.connect()
try:
    con.execute("INSTALL delta; LOAD delta;")
    print(con.sql(f"select px_date, count(*) as prices, round(avg(px_close), 2) as avg_close from delta_scan('{TABLE}') group by 1 order by 1"))
except Exception as e:
    print("   (DuckDB delta extension unavailable offline:", str(e).splitlines()[0][:80], ")")
    print("   Fallback: read the Parquet files directly:")
    print(con.sql(f"select count(*) as rows_in_parquet_files from read_parquet('{TABLE}/*.parquet')"))
print("\nDone. On Databricks the same table lives in S3, Unity Catalog names it catalog.schema.table, and Spark runs the queries.")
