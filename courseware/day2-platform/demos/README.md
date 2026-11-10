# Day 2 demos

| Folder | What it shows | Run |
|---|---|---|
| `docker/portfolio-summary/` | The challenge's six-holding app: run an image, look inside, build, run, mount, tag (the same steps as challenge 01) | `bash demo.sh` |
| `docker/compose/` | Three containers on one private network: Postgres seeded with the running example's price sheet, an HTTP API that queries it by service name, a one-shot report; the network and its members, name resolution, the one published port, isolation three ways, `down -v` | `bash demo.sh` |
| `delta-under-the-hood/` | A Delta table on disk: Parquet files plus a transaction log; append, MERGE, history, time travel, OPTIMIZE; read back from DuckDB | `python demo.py` |
| `spark-engine/` | A local Spark: driver, executors, partitions, a SQL plan with its shuffle, the Spark UI | `python demo.py --hold 90`, then open http://localhost:4040 |
| `git/` | The Git section's six steps on a throwaway repository: a first commit, status and diff, a branch, the merge, `.gitignore`, restore and revert | `bash demo.sh` |
| `contract-to-code/eod_prices/` | The running example's contract implemented as a dbt project on DuckDB: seeds, sources with freshness, staging, intermediate, mart, tests | `bash run.sh` |

The Git demo needs only `git`. The other five need `source ../../common/env/activate.sh` in the terminal first (dbt, duckdb, pyspark and docker on PATH). Spark needs a Java 17 runtime; `activate.sh` sets `JAVA_HOME` to the Homebrew OpenJDK 17 on this laptop.
