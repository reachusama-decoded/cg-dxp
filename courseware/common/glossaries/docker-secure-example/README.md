# A secure container, end to end

A small backend service (FastAPI) with a database (Postgres), built and run the way the glossary's Part 2 recommends. Every file is commented line by line; read them in this order: `.dockerignore`, `Dockerfile`, `app/main.py`, `docker-compose.yml`, `.env.example`.

| File | What it shows |
|---|---|
| `Dockerfile` | A multi-stage build (dependencies in stage 1, only the result in stage 2), pinned base, a non-root user with a fixed UID, `--chown` copies so a read-only filesystem works, a standard-library `HEALTHCHECK`, `ENTRYPOINT` plus `CMD`, labels. |
| `.dockerignore` | Keeps `.git`, caches, the data and the secrets file out of the build context, so they cannot be copied in. |
| `app/main.py` | Configuration from the environment at run time; data from a read-only mount; a database check that never prints the connection string. |
| `app/requirements.txt` | Pinned versions. |
| `docker-compose.yml` | The run-time side: secrets from an env file, a read-only root filesystem with a tmpfs, all capabilities dropped, no new privileges, memory and CPU limits, a port bound to the laptop only, a private network, a database with no published port, health checks and start ordering. |
| `.env.example` | The shape of the secrets file; copy to `.env` and fill it in. `.env` is ignored by Git and by the build. |

## Run it

```bash
cd courseware/common/glossaries/docker-secure-example
cp .env.example .env                      # then edit the password

# Just the API, with the data mounted read-only and the secret passed at run time
docker build -t portfolio-api:local .
docker run --rm -p 127.0.0.1:8000:8000 -v "$PWD/data:/data:ro" --env-file .env \
  --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges --memory 256m portfolio-api:local
curl -s localhost:8000/health && curl -s localhost:8000/summary

# The API and the database together
docker compose up -d --build
curl -s localhost:8000/db                 # the service reached Postgres over the private network
docker compose ps                         # both healthy
docker compose down -v                    # stop, and delete the database volume
```

## What to point at in the room

- `docker history portfolio-api:local` shows no `pip install` of a compiler, no requirements file, no secrets: stage 1 never reached the final image.
- `docker inspect portfolio-api-api-1 --format '{{.Config.User}}'` prints `app`; `docker exec portfolio-api-api-1 touch /app/x` fails because the filesystem is read-only.
- `docker port portfolio-api-api-1` shows `127.0.0.1:8000`; the database has no entry because nothing is published.
- The same choices on the paved path: EDO's base images, Harness building from Git, secrets from the secrets manager at run time, the cluster policy that blocks arbitrary-shell operators.
