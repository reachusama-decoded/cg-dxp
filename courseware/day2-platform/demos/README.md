# Day 2 demos

| Folder | What it shows | Run |
|---|---|---|
| `docker/portfolio-summary/` | The challenge's six-holding app: run an image, look inside, build, run, mount, tag (the same steps as challenge 01) | `bash demo.sh` |
| `delta-under-the-hood/` | A Delta table on disk: Parquet files plus a transaction log; append, MERGE, history, time travel, OPTIMIZE; read back from DuckDB | `python demo.py` |
| `spark-engine/` | A local Spark: driver, executors, partitions, a SQL plan with its shuffle, the Spark UI | `python demo.py --hold 90`, then open http://localhost:4040 |
| `contract-to-code/eod_prices/` | The running example's contract implemented as a dbt project on DuckDB: seeds, sources with freshness, staging, intermediate, mart, tests | `bash run.sh` |

All four need `source ../../common/env/activate.sh` in the terminal first (dbt, duckdb, pyspark and docker on PATH). Spark needs a Java 17 runtime; `activate.sh` sets `JAVA_HOME` to the Homebrew OpenJDK 17 on this laptop.
