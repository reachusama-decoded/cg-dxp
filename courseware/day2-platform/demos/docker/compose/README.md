# Day 2 Compose demo

Three containers that run together on one private network, from one commented file: `db`, Postgres seeded at first start with the running example's price sheet (`common/running-example/data/rpt_eod_prices_us.csv`); `api`, a small HTTP service that answers `/health` and `/prices` by querying `db` by name; `report`, a one-shot `psql` that runs one query and exits. The anchor's cells and this script show the same eight steps: up, the report's output, the network and its members, name resolution inside a container, the laptop reaching the API through the one published port, three isolation checks, down.

```bash
bash demo.sh                      # the eight steps, then everything removed
docker compose up -d --build      # or by hand, from this folder
curl localhost:8000/prices
docker compose down -v
```

Docker Desktop must be running. The first run pulls `postgres:16-alpine` and builds the API image, about a minute; later runs take seconds. Port 8000 on the laptop must be free. The password in the file is a demo value: the secure example in `common/glossaries/docker-secure-example/` shows the same stack loading it from an uncommitted `.env`.
