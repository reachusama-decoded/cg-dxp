"""A small HTTP API in front of the price sheet: three routes, the standard library's server, psycopg for Postgres.

The point is the network, not the code. This process reaches Postgres as "db", the service name in docker-compose.yml,
which Docker's DNS resolves to the database container's address on the project's private network. No address is
written anywhere in the project.
"""
import json
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import psycopg

# Connection details arrive as environment variables from the Compose file, never from a file baked into the image.
DB = dict(host=os.environ["DB_HOST"], user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"], dbname=os.environ["DB_NAME"])


def query(sql, params=()):
    """Run one query and return the rows as dictionaries. A fresh connection per request: simple, and enough for a demo."""
    with psycopg.connect(**DB, connect_timeout=3) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [c.name for c in cur.description]
        return [dict(zip(cols, (str(v) for v in row))) for row in cur.fetchall()]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        try:
            if url.path == "/health":
                body = {"api": "ok",
                        "db_host": DB["host"],                               # the name the API was given
                        "db_addr": socket.gethostbyname(DB["host"]),         # what Docker's DNS makes of it, right now
                        "db": "ok" if query("select 1") else "down"}
            elif url.path == "/prices" and "instrument_id" in q:
                body = query("select price_date, ticker, price_usd from eod_prices where instrument_id = %s order by price_date",
                             (q["instrument_id"][0],))
            elif url.path == "/prices":
                body = query("select price_date, count(*) as instruments from eod_prices group by price_date order by price_date")
            else:
                body = {"routes": ["/health", "/prices", "/prices?instrument_id=US0378331005"]}
            status = 200
        except Exception as e:                                               # a database error becomes a 503 with the reason, not a crash
            status, body = 503, {"error": str(e)}
        data = json.dumps(body, indent=1).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):                                       # one line per request in `docker compose logs api`
        print(f"{self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    print(f"api listening on 0.0.0.0:8000, database at {DB['host']}", flush=True)
    # 0.0.0.0 means every interface inside the container; the `ports:` line in the Compose file decides who outside can reach it.
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
