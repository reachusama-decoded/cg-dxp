#!/usr/bin/env python3
"""Print the bitemporal table four ways. Usage: python show.py [as_was_timestamp]"""
import os, sys, duckdb
con = duckdb.connect(os.environ.get("BT_DUCKDB_PATH", "warehouse/bitemporal.duckdb"), read_only=True)
T = "training_demo.dim_associate"
def show(title, sql):
    print(f"\n-- {title}\n{sql.strip()}\n"); print(con.sql(sql))
show("Full history for associate 1001 in system order: the audit trail (nothing is overwritten)",
     f"select job_title, tenure_months, dl_business_start_dt, dl_business_end_dt, dl_system_start_ts, dl_system_end_ts, dl_current_ind "
     f"from {T} where associate_id = 1001 order by dl_system_start_ts, dl_business_start_dt")
show("AS IS: current in both clocks",
     f"select associate_id, name, job_title, tenure_months, dl_business_start_dt from {T} where dl_current_ind order by 1")
show("AS OF business date 2026-11-02, with today's knowledge (system clock open)",
     f"select associate_id, job_title, tenure_months, dl_business_start_dt, dl_business_end_dt from {T} "
     f"where dl_business_start_dt <= date '2026-11-02' and coalesce(dl_business_end_dt, date '9999-12-31') >= date '2026-11-02' "
     f"and dl_system_end_ts is null order by 1")
if len(sys.argv) > 1:
    t = sys.argv[1]
    show(f"AS WAS at system time {t}: what the warehouse believed then, before the correction arrived",
         f"select associate_id, job_title, tenure_months, dl_business_start_dt from {T} "
         f"where dl_system_start_ts <= timestamp '{t}' and coalesce(dl_system_end_ts, timestamp '9999-12-31') > timestamp '{t}' "
         f"and dl_business_end_dt is null order by 1")
