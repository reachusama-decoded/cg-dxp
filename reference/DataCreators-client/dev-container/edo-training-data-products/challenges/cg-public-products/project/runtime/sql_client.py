#!/usr/bin/env python3
"""Execute supplied owned SQL statements in the dbt venv, which has the connector.

Request arrives as JSON on stdin; credentials remain in the approved environment.
Emits result JSON or a generic error category, never connection strings/tokens.
"""
import json
import os
import sys


def main():
    from databricks import sql
    statements=json.load(sys.stdin)
    values=[]
    with sql.connect(server_hostname=os.environ['DATABRICKS_HOST'].replace('https://',''),
                     http_path=os.environ['DATABRICKS_HTTP_PATH'],
                     access_token=os.environ['DBT_ACCESS_TOKEN']) as connection:
        with connection.cursor() as cursor:
            for item in statements:
                cursor.execute(item['sql'])
                values.append([list(r) for r in cursor.fetchall()] if item.get('fetch') else [])
    print(json.dumps(values,default=str))


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print('SQL client failed: '+type(exc).__name__,file=sys.stderr)
        raise SystemExit(2)
