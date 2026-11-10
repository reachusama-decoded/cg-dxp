#!/usr/bin/env bash
# Day 2 Compose demo: three containers on one private network, in the order of the anchor's cells. Docker Desktop
# must be running. The first run pulls postgres:16-alpine and builds the API image (about a minute); later runs are seconds.
set -euo pipefail
cd "$(dirname "$0")"
step() { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }
step "0. A clean slate: remove any earlier run of this project, its network and its volume"
docker compose down -v --remove-orphans 2>/dev/null || true
step "1. The file: three services, one network, one volume"
docker compose config --services
step "2. Up: build the API image, pull Postgres, create the network and the volume, start in dependency order"
docker compose up -d --build
docker compose ps -a --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}'
step "3. The one-shot report ran one query against db, by name, and exited"
docker compose logs --no-log-prefix report
step "4. The network Compose created, and who is on it"
docker network ls --filter name=eod_
docker network inspect eod_backend --format '{{range .Containers}}{{println .Name .IPv4Address}}{{end}}'
step "5. Inside the API container: the service name is a hostname, answered by Docker's DNS"
docker compose exec api python -c "import socket; print('db resolves to', socket.gethostbyname('db'))"
docker compose exec api grep nameserver /etc/resolv.conf   # 127.0.0.11: the embedded DNS Docker runs for every user-defined network
step "6. From the laptop, through the one published port: the API answers by querying db over the network"
curl -s localhost:8000/health
curl -s 'localhost:8000/prices?instrument_id=US0378331005'
step "7. Isolation three ways: no laptop port leads to Postgres; a container off the network cannot resolve its name; one on it can"
echo "api:" && docker port eod-api-1 && echo "db:" && docker port eod-db-1 && echo "(nothing: db publishes no port, so no laptop address leads to it)"
docker run --rm postgres:16-alpine pg_isready -h db -t 2 || echo "^ a container on the default network: no such host"
docker run --rm --network eod_backend postgres:16-alpine pg_isready -h db -t 2
step "8. Down: the containers, the network and (with -v) the volume are gone; the images stay, cached"
docker compose down -v
docker network ls --filter name=eod_
