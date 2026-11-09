# Docker commands, by what you are trying to do

One line per command. The flags listed are the ones that matter in practice; `docker <command> --help` has the rest. Everything here runs in the dev container's terminal or on a laptop with Docker Desktop; `astro dev start` runs several of these for you.

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

## The Dockerfile, for reference

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
