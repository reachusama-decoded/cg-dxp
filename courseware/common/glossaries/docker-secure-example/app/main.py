"""A small backend service, written to show the run-time side of a secure container.

Three endpoints: /health (is the process up), /summary (reads a CSV from a read-only mount),
/db (reaches the database using a connection string that arrives as an environment variable).
Nothing here is secret: configuration comes from the environment at run time, never from the image.
"""
import csv
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException

app = FastAPI(title="portfolio-api")

# Configuration from the environment, with safe defaults for local runs. The data path points at a mount,
# so the image carries no data; the database URL carries the password, so it is never written down in code.
DATA_FILE = Path(os.environ.get("DATA_FILE", "/data/holdings.csv"))
DATABASE_URL = os.environ.get("DATABASE_URL")


@app.get("/health")
def health() -> dict:
    """Cheap and dependency-free: Docker's HEALTHCHECK and the platform's probes call this."""
    return {"status": "ok"}


@app.get("/summary")
def summary() -> dict:
    """Total market value of the holdings in the mounted CSV. The mount is read-only; the app never writes."""
    if not DATA_FILE.exists():
        raise HTTPException(status_code=503, detail=f"data file not mounted at {DATA_FILE}")
    with DATA_FILE.open(newline="") as f:
        rows = list(csv.DictReader(f))
    total = sum(float(r["market_value"]) for r in rows)
    return {"holdings": len(rows), "total_market_value": round(total, 2)}


@app.get("/db")
def db() -> dict:
    """Open a connection, run a trivial query, close it: proves the secret arrived and the network allows the hop."""
    if not DATABASE_URL:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not set")
    import psycopg  # imported here so the service still starts when the database is not part of the run

    try:
        with psycopg.connect(DATABASE_URL, connect_timeout=3) as conn:
            version = conn.execute("select version()").fetchone()[0]
    except Exception as exc:  # the message names the failure class, never the connection string
        raise HTTPException(status_code=503, detail=f"database unreachable: {type(exc).__name__}") from exc
    return {"database": version.split(" on ")[0]}
