# Docker: the commands, and how to use them securely

One line per command. The flags listed are the ones that matter in practice; `docker <command> --help` has the rest. Everything here runs in the dev container's terminal or on a laptop with Docker Desktop; `astro dev start` runs several of these for you.

# Part 1 — The commands, by what you are trying to do

## Check the engine

| Command | What it does |
|---|---|
| `docker version` | Prints the client and engine versions; the engine line is missing when Docker Desktop is not running. |
| `docker info` | Prints the engine's state: containers, images, storage driver, resources. The first check when anything fails. |
| `docker context ls` | Lists the engines the client can talk to (Docker Desktop, a remote host) and which is active. |

## Get and manage images

| Command | What it does |
|---|---|
| `docker pull IMAGE[:TAG]` | Downloads an image from a registry (Docker Hub by default, or CG's internal registry when the name says so). |
| `docker images` (or `docker image ls`) | Lists the images on this machine with their tags, IDs and sizes. |
| `docker build -t NAME[:TAG] PATH` | Builds an image from the Dockerfile in PATH; PATH is also the build context that `COPY` reads from. |
| `docker build --no-cache …` | Builds without reusing cached layers, when a `RUN` fetched something stale. |
| `docker build -f FILE …` | Builds from a Dockerfile that is not called `Dockerfile` or lives elsewhere. |
| `docker tag SOURCE TARGET` | Gives an image another name, usually a registry prefix and a version: two names, one ID. |
| `docker push NAME[:TAG]` | Uploads an image to the registry its name points at. |
| `docker history IMAGE` | Shows the layers an image is made of and which instruction created each. |
| `docker image inspect IMAGE` | Prints the image's metadata as JSON: entrypoint, environment, exposed ports, layers. |
| `docker rmi IMAGE` (or `docker image rm`) | Deletes an image; fails while a container still uses it. |
| `docker image prune` | Deletes dangling images (untagged layers left by rebuilds); `-a` deletes every unused image. |
| `docker save IMAGE -o FILE.tar` / `docker load -i FILE.tar` | Exports an image to a file and imports it again, for machines without registry access. |
| `docker search TERM` | Searches Docker Hub for images by name. |

## Run containers

| Command | What it does |
|---|---|
| `docker run IMAGE [COMMAND]` | Creates and starts a container from an image, running its default command or the one given. |
| `docker run --rm …` | Deletes the container when it exits; use it for one-off commands. |
| `docker run -it …` | Interactive with a terminal: `docker run -it python:3.11-slim bash` gives a shell inside. |
| `docker run -d …` | Detached: runs in the background and prints the container ID. |
| `docker run --name NAME …` | Names the container so later commands can refer to it instead of an ID. |
| `docker run -p HOST:CONTAINER …` | Publishes a port: `-p 8080:8080` makes the container's 8080 reachable as the laptop's 8080. |
| `docker run -v HOST_PATH:CONTAINER_PATH[:ro] …` | Mounts a laptop folder or file into the container; `:ro` makes it read-only. |
| `docker run -e KEY=VALUE …` / `--env-file FILE` | Sets environment variables inside the container. |
| `docker run -w DIR …` | Sets the working directory for the command. |
| `docker run --entrypoint CMD …` | Overrides the image's entrypoint, for example to get a shell in an image that runs an app. |
| `docker run --memory 2g --cpus 1.5 …` | Caps the container's memory and CPU so a runaway process cannot take the host down. |
| `docker run --network NAME …` | Attaches the container to a network so it can reach other containers by name. |
| `docker run --restart unless-stopped …` | Restarts the container automatically after a crash or a reboot. |
| `docker create …` | Creates a container without starting it; `docker start` runs it later. |
| `docker start NAME` / `docker stop NAME` | Starts a stopped container; stops a running one gracefully (then kills it after a timeout). |
| `docker restart NAME` | Stops and starts a container. |
| `docker kill NAME` | Stops a container immediately, without the graceful signal. |
| `docker pause NAME` / `docker unpause NAME` | Freezes and resumes every process in a container. |
| `docker wait NAME` | Blocks until the container exits and prints its exit code. |
| `docker attach NAME` | Connects your terminal to a running container's main process. |
| `docker rm NAME` | Deletes a stopped container; `-f` deletes a running one. |

## Look inside and diagnose

| Command | What it does |
|---|---|
| `docker ps` | Lists running containers; `-a` includes stopped ones; `-q` prints only IDs. |
| `docker logs NAME` | Prints a container's output; `-f` follows it live; `--tail 100` shows the last lines. |
| `docker exec -it NAME bash` | Runs a command inside a running container; with `-it bash` you get a shell. |
| `docker inspect NAME` | Prints everything about a container as JSON: mounts, ports, environment, IP, state. |
| `docker top NAME` | Lists the processes running inside a container. |
| `docker stats` | Shows live CPU, memory and network use per container. |
| `docker port NAME` | Shows which laptop ports map to which container ports. |
| `docker diff NAME` | Lists files the container has changed since it started from its image. |
| `docker cp NAME:PATH LOCAL` / `docker cp LOCAL NAME:PATH` | Copies files out of or into a container. |
| `docker events` | Streams engine events (starts, stops, pulls) as they happen. |

## Keep data: volumes and mounts

| Command | What it does |
|---|---|
| `docker volume create NAME` | Creates a named volume, storage that outlives any container. |
| `docker volume ls` / `docker volume inspect NAME` | Lists volumes; shows where a volume lives and which containers use it. |
| `docker volume rm NAME` / `docker volume prune` | Deletes a volume; deletes every volume no container uses (data is gone). |
| `-v NAME:/path` (on `run`) | Mounts a named volume at a path; the data stays when the container is removed. |
| `-v /laptop/path:/path` (on `run`) | A bind mount: the container reads and writes the laptop's folder directly. |
| `--mount type=bind,src=…,dst=…` | The explicit form of the same mounts, with clearer options. |

## Connect containers: networks

| Command | What it does |
|---|---|
| `docker network ls` | Lists networks; every container joins `bridge` unless told otherwise. |
| `docker network create NAME` | Creates a network; containers on it reach each other by container name. |
| `docker network inspect NAME` | Shows the network's containers and addresses. |
| `docker network connect NAME CONTAINER` / `disconnect` | Attaches or detaches a running container. |
| `docker network rm NAME` / `docker network prune` | Deletes a network; deletes unused ones. |

## Run several containers together: Compose

| Command | What it does |
|---|---|
| `docker compose up` | Creates and starts every service in `docker-compose.yml`; `-d` detached; `--build` rebuilds images first. |
| `docker compose down` | Stops and removes the services and their network; `-v` also deletes their volumes. |
| `docker compose ps` | Lists the project's containers and their state. |
| `docker compose logs SERVICE` | Shows a service's output; `-f` follows. |
| `docker compose exec SERVICE CMD` | Runs a command inside a running service (`… scheduler bash`). |
| `docker compose build` / `pull` | Builds the project's images; pulls them. |
| `docker compose stop` / `start` / `restart` | Stops, starts or restarts the services without removing them. |
| `docker compose config` | Prints the fully resolved configuration, with overrides and variables applied. |
| `docker compose run --rm SERVICE CMD` | Starts one service for a single command and removes it afterwards. |

`astro dev start`, `stop`, `restart` and `astro dev run …` wrap Compose: the Astro CLI writes the Compose file for the scheduler, DAG processor, API server, triggerer and Postgres and runs it. `docker ps` shows those containers.

A runnable two-service example of all of this, with the network commands above, is `day2-platform/demos/docker/compose/`: Postgres with no published port, an API that reaches it by service name, and every line of the Compose file commented.

## Registries and sign-in

| Command | What it does |
|---|---|
| `docker login REGISTRY` / `docker logout` | Signs in to a registry (Docker Hub, or CG's internal registry) so push and pull work. |
| `docker pull REGISTRY/PATH/IMAGE:TAG` | Pulls from a specific registry; the host name in the image name is the registry. |

## Clean up

| Command | What it does |
|---|---|
| `docker system df` | Shows disk used by images, containers, volumes and the build cache. |
| `docker system prune` | Deletes stopped containers, unused networks, dangling images and build cache; `-a` adds unused images; `--volumes` adds volumes. |
| `docker container prune` | Deletes every stopped container. |
| `docker builder prune` | Deletes the build cache; the next build pulls and runs everything again. |

## The Dockerfile instructions, for reference

Instructions, not commands: the recipe `docker build` follows.

| Instruction | What it does |
|---|---|
| `FROM image[:tag]` | Starts from a base image; almost every Dockerfile begins here. `FROM … AS name` names a stage in a multi-stage build. |
| `WORKDIR /path` | Sets the directory the following instructions and the container's command run in. |
| `COPY src dest` | Copies files from the build context into the image; `COPY --from=stage` copies from an earlier stage. |
| `ADD src dest` | Like `COPY`, but also unpacks archives and fetches URLs; prefer `COPY`. |
| `RUN command` | Runs a command at build time and keeps the result as a layer (install packages, create folders). |
| `ENV KEY=value` | Sets an environment variable in the image and in every container started from it. |
| `ARG name[=default]` | A build-time variable passed with `--build-arg`; not present at run time. |
| `EXPOSE port` | Documents the port the app listens on; `-p` on `run` publishes it. |
| `USER name` | Switches the user the following instructions and the command run as. |
| `VOLUME /path` | Marks a path as data that should live in a volume. |
| `CMD ["prog", "arg"]` | The default command when the container starts; replaced by a command given to `docker run`. |
| `ENTRYPOINT ["prog"]` | The fixed program the container runs; a `docker run` command becomes its arguments. |
| `HEALTHCHECK CMD …` | A command Docker runs periodically to report the container healthy or not. |
| `LABEL key=value` | Metadata on the image (owner, version). |
| `.dockerignore` | A file beside the Dockerfile listing what to leave out of the build context (data, `.git`, caches). |

Two habits that keep images small and builds fast: order instructions from least to most frequently changed (base image, system packages, dependencies, then your code) so the cache survives a code change; and use a multi-stage build to compile or install in one stage and copy only the result into a slim final image.

# Part 2 — Build images and run containers securely

The habits, in the order they bite. Most of them are one line in the Dockerfile or one flag on `docker run`; CG's base images and cluster policies already enforce several, which is one reason the paved path starts from them.

## Building the image

| Habit | How |
|---|---|
| Start from a trusted, minimal base | `FROM` an image from CG's internal registry or an official image; prefer the `slim` or `alpine` variant so there is less to attack and patch. |
| Pin what you depend on | A base image tag with a version (`python:3.11-slim`, not `python:latest`), or a digest (`image@sha256:…`) when the build must be reproducible; pinned package versions in `requirements.txt`. |
| Do not run as root | Create a user and switch to it before `CMD`: `RUN useradd -m app` then `USER app`. A process that escapes a root container is root on the host's kernel. |
| Keep secrets out of the image | Never `COPY` a `.env`, a key or a token, and never `ENV TOKEN=…` or `ARG` a secret: every layer is readable with `docker history` and stays in the registry forever. Pass secrets at run time (`-e` from a secrets manager, a mounted file) or use `docker build --secret` for build-time needs. |
| Keep the build context small | A `.dockerignore` that excludes `.git`, data, caches, virtualenvs and anything secret, so they cannot be copied in by accident. |
| Ship only what runs | A multi-stage build: compile or install in one stage, `COPY --from=` only the result into a slim final image; no compilers, package managers or test data in production. |
| Update and rebuild | Rebuild regularly from the updated base image so operating-system patches arrive; `docker build --pull` fetches the newest base tag. |
| Scan before you push | `docker scout cves IMAGE` (Docker Desktop) or Trivy (`trivy image IMAGE`) lists known vulnerabilities; fix or justify the critical ones before the image leaves the laptop. |
| Declare what the app needs | `EXPOSE` only the port the app listens on; a `HEALTHCHECK` so the platform can tell a wedged container from a healthy one. |
| Label and track | `LABEL` the owner and version; keep the Dockerfile in Git so every image is traceable to a commit and a pull request. |

## Running the container

| Habit | How |
|---|---|
| Least privilege | Never `--privileged`; drop capabilities you do not need: `--cap-drop ALL --cap-add NET_BIND_SERVICE`; `--security-opt no-new-privileges`. |
| Read-only where possible | `--read-only` with a `--tmpfs /tmp` for scratch space, so a compromised process cannot modify the image's files. |
| Cap resources | `--memory` and `--cpus` so one container cannot starve the host or its neighbours (the production point from Day 2). |
| Publish ports narrowly | `-p 127.0.0.1:8080:8080` binds to the laptop only; `-p 8080:8080` listens on every interface, including the office network. |
| Mount deliberately | Mount the one folder needed, read-only when the app only reads (`-v …:/data:ro`); never mount the Docker socket (`/var/run/docker.sock`) into a container, which hands it control of the engine. |
| Secrets at run time only | `--env-file` from a file outside Git, or a mounted secret file, or the platform's secrets manager; `docker inspect` shows environment variables to anyone with engine access, so prefer files for anything long-lived. |
| Isolate the network | A dedicated `docker network` for the services that must talk; containers that do not need the internet get `--network none`. |
| One process, one job | One application per container; sidecars for logging or proxies rather than a second service inside. |
| Clean up | `--rm` for one-off runs; `docker system prune` for the rest, so stale containers with old secrets or data do not accumulate. |

## A secure Dockerfile, for the six-holding app

```dockerfile
# Start from a pinned, minimal, official image: a known Python, a small Debian, nothing extra to patch.
FROM python:3.11-slim

# Every later instruction, and the running app, works in /app (created if missing).
WORKDIR /app

# Create an ordinary user for the app to run as. --create-home gives it a home folder (some tools need one);
# --shell /usr/sbin/nologin means nobody can log in as it, even inside the container. The user exists only in the image.
RUN useradd --create-home --shell /usr/sbin/nologin app

# Copy only the two files the app needs, from the build context into /app. Nothing else from the folder gets in,
# and .dockerignore stops .git, data dumps and secrets from being part of the context at all.
COPY app/summarize.py app/holdings.csv ./

# From here on, instructions and the container's process run as "app", not root. If the app is compromised,
# the attacker holds an unprivileged account inside a container, not root on a shared kernel.
USER app

# A command Docker runs periodically to decide whether the container is healthy; here, can the module import.
HEALTHCHECK CMD ["python", "-c", "import summarize"]

# What runs when the container starts; `docker run IMAGE other-command` replaces it.
CMD ["python", "summarize.py"]
```

Run it as `docker run --rm --read-only --memory 256m --cpus 0.5 --cap-drop ALL portfolio-summary`. A fuller, runnable example with a backend service, a database and Compose is in `docker-secure-example/` beside this file. On the paved path the equivalent choices are already made: the dev container and the Airflow images start from EDO's base images, Harness builds them from Git, secrets live in the secrets manager and arrive at run time, and the cluster policy blocks operators that would give a task an arbitrary shell.
