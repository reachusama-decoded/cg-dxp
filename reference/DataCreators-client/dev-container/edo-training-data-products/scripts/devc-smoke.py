#!/usr/bin/env python3
"""Read-only pre-class capability check. No installs, jobs, resets or repair."""
import argparse,json,sys
from pathlib import Path
from instructor_demos.contracts import doctor,load_story
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--route',choices=['duckdb','docker','astro-ui'],required=True);a=ap.parse_args()
    requirements={'duckdb':['dbt','duckdb-python'],'docker':['docker-client','docker-server'],'astro-ui':['docker-client','docker-server','astro','env:DEMO_AIRFLOW_RUN_URL','env:DEMO_AIRFLOW_LOG_URL']}[a.route]
    result=doctor(ROOT,requirements)
    manifest=json.loads((ROOT/'challenges/v2/manifest.json').read_text())
    missing=[p for p in manifest['readme_order'] if not (ROOT/'challenges/v2'/p).is_file()]
    report={'route':a.route,'capabilities':result,'missing_learner_readmes':missing,'boundary':'Tool/process readiness only. Identity, assigned resources, worker mounts and route execution require the live audit; this smoke check never silently repairs or runs the course.'}
    print(json.dumps(report,indent=2));return 77 if missing or any(r['status']=='blocked' for r in result.values()) else 0
if __name__=='__main__':sys.exit(main())
