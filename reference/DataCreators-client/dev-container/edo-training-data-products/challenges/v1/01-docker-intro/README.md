# Docker, hands-on — wrap a script in a container


Docker is a way to package code together with everything it needs to run — its
libraries **and** the operating-system libraries underneath them — into one
runnable image that behaves consistently on compatible Docker hosts. That is why
this firm runs Airflow and dbt in containers: the same image can move from your
laptop to a teammate's machine, a build server, or the cloud without reinstalling
its application dependencies.

In this mini-lab you take a tiny Python script that summarises a portfolio CSV
and wrap it in a container yourself. The script is deliberately trivial — six
holdings, one total — so Docker is the thing you are learning, not the app. By
the end you can explain the difference between an image and a container, write a
Dockerfile, build an image from it, and run it.

You author the **Dockerfile** — the recipe. The app under `starter/app/`
(`summarize.py` + `holdings.csv`) is already complete, so you do not touch it.
The finished reference lives under `solution/`; compare against it after making
your own attempt. Work the sections in order.

## What You'll Build

A container image called `portfolio-summary` that, when you run it, prints:

```text
Portfolio summary
6 holdings, total market value 12,011,626.50
```

It prints that on a compatible machine with Docker — yours, a colleague's, a
server — because the image carries the app, Python, and its user-space OS
libraries with it.

## Every Section Has The Same Shape

1. **Concept** — what the idea is and why it exists.
2. **Challenge (authoring)** — the exact thing you do or write.
3. **Hint** — where to look, and the shape of the answer.
4. **How to check** — a command to run, and the observable result.
5. **Try a variation** — an optional small twist to make the step your own.

The first two challenges have nothing to author — you run a command and read the
output. That is the right shape for learning what an image and a container are.
The Dockerfile you write is the deliverable from Challenge 3 on. In the starter,
the `Dockerfile` is a stub with a `# TODO` per line; the solution has it
complete.

## Start Here

From the repository root, move into the learner workspace:

```bash
cd challenges/v1/01-docker-intro/starter
```

Run the remaining Docker commands from this folder. This matters because `.` is
the build context, and the Dockerfile copies `app/` from that context. You can
run the final gate from anywhere in the repository with:

```bash
mise run challenge:verify 01
```

## Time Budget

| # | Section | Approx. time |
|---|---------|--------------|
| 1 | Run an image | `<5min` |
| 2 | Look inside (isolation) | `~5min` |
| 3 | Write the Dockerfile | `~10min` |
| 4 | Build the image | `~5min` |
| 5 | Run your image (portability) | `~5min` |
| 6 | Try it yourself (optional) | `~5min` |
| | **Total** | **~35min** |

## Prereqs

You need the `docker` command available. Either:

- **Docker Desktop** on your laptop (macOS / Windows / Linux), with the engine
  running; or
- the **repository devcontainer**, which already has Docker.

Confirm it is there before you start:

```bash
docker --version
```

You should see a version line (for example `Docker version 27.x`). If the
command is not found, install Docker Desktop or open the repository
devcontainer. The app is standard-library-only Python, so it needs no
`pip install`; Docker may still need network access to pull the base image the
first time.

\newpage

## 1. Run an image

**Concept.** An **image** is a frozen template — a read-only package of a
filesystem plus configuration such as a default command. A **container** is one
running instance of an image: Docker prepares the image's filesystem, runs its
command, and the container lives only as long as that command runs. `docker run`
pulls the image if you do not have it, starts a container from it, runs the
command, and exits. `--rm` deletes the finished container so it does not pile
up. The Dockerfile is the recipe, the image is the packaged result, and many
containers can be started from one image.

Docs: docker run: https://docs.docker.com/reference/cli/docker/container/run/

**Challenge (authoring).** Nothing to write here — run one command and read what
happens. Run the official Python image and ask it for its version:

```bash
docker run --rm python:3.11-slim python --version
```

Then answer, from what you saw: did Docker download anything the first time? What
command ran inside the container? Where did the container go after it printed?

**Hint.** The first run pulls the `python:3.11-slim` image (you see layer
download lines); later runs reuse the cached image and start instantly. The
container started, ran `python --version`, printed one line, exited, and `--rm`
removed it — a container is not a long-lived thing unless its command is.

**How to check.**

```bash
docker run --rm python:3.11-slim python --version
```

You should see a single line like `Python 3.11.x`. That line came from Python
running **inside a container** built from the image — not from any Python on your
host. The shell prompt returns immediately because the container has already
exited.

**Try a variation (optional).** Run `docker run --rm python:3.11-slim python -c "print(2 + 2)"`
and watch a different command run in a fresh container from the same image. Same
image, different container, different command.

\newpage

## 2. Look inside (isolation)

**Concept.** A container is an **isolated process environment**: it has its own
filesystem, OS user-space libraries, and view of processes and networking. It
shares the host's Linux kernel rather than carrying a second kernel. That
isolation is the point of the "wrap it twice" idea from the module — the
container packages the user-space libraries with the code. Step inside one and
you see a Linux filesystem separate from your host's: its own `/` and
`/etc/os-release`. When this `--rm` container exits, its writable layer is
removed.

Docs: docker run -it: https://docs.docker.com/reference/cli/docker/container/run/

**Challenge (authoring).** Nothing to write — open an interactive shell inside a
container and look around. Start a container with a terminal attached:

```bash
docker run --rm -it python:3.11-slim bash
```

Now you are *inside* the container. Run `ls /` to see its root filesystem, then
`cat /etc/os-release` to see which Linux it is, then `exit` to leave.

**Hint.** `-it` attaches an interactive terminal so you get a shell prompt
*inside* the container. `ls /` shows a normal Linux root (`bin`, `etc`, `usr`,
`tmp`, …) — but it is the container's, not your host's. `/etc/os-release` reports
Debian (the base of `python:3.11-slim`), even if your laptop is macOS or a
different Linux. `exit` ends the shell, which ends the container.

**How to check.**

```bash
docker run --rm -it python:3.11-slim bash -c "ls / && cat /etc/os-release"
```

You should see a Linux root listing and an `os-release` naming **Debian** —
proof you are looking at the container's own OS libraries, not your host's.
This is the second wrapping from the module made concrete: the image carries its
own user-space filesystem and libraries while Docker provides the isolated
runtime.

**Try a variation (optional).** Inside the interactive shell
(`docker run --rm -it python:3.11-slim bash`), run `touch /tmp/proof.txt`, then
`exit`, then start a fresh container and `ls /tmp` — the file is gone. Each
container starts clean from the image; changes do not persist unless you build
them in or mount them.

\newpage

## 3. Write the Dockerfile

**Concept.** A **Dockerfile** is the recipe for an image: a short text file of
instructions Docker uses to assemble the image. Filesystem-changing build steps
produce cached layers, while instructions such as `CMD` add image configuration.
This lets a rebuild reuse work whose inputs did not change. The four instructions
you need here are the common core: `FROM` picks a base image, `WORKDIR` sets the
directory work happens in, `COPY` brings your files in, and `CMD` sets the
default command the container runs.

Docs: Dockerfile reference: https://docs.docker.com/reference/dockerfile/

**Challenge (authoring).** Open `Dockerfile` in the `starter/` folder and
complete the stub. The
`FROM python:3.11-slim` line is given; fill in the three `# TODO` lines so the
recipe:

1. sets the working directory to `/app` (`WORKDIR /app`);
2. copies the `app/` folder (`summarize.py` + `holdings.csv`) into the working
   directory (`COPY app/ ./`);
3. sets the default command to run the script
   (`CMD ["python", "summarize.py"]`).

**Hint.** Order matters and is the whole shape: base, then where, then what, then
how-to-run. `COPY app/ ./` copies the *contents* of `app/` into the current
`WORKDIR` (`/app`), so `summarize.py` lands at `/app/summarize.py` — which is why
the script can open `holdings.csv` by its bare name. The `CMD` uses the JSON-array
("exec") form so the process runs directly without a shell. There is a
`.dockerignore` next to the Dockerfile that keeps Python cache files out of the
build context.

**How to check.** A Dockerfile has no output on its own — you check it by
building (next section). For now, confirm it has all four instructions present
and in order:

```bash
grep -E '^(FROM|WORKDIR|COPY|CMD)' Dockerfile
```

You should see exactly four lines back, one each for `FROM`, `WORKDIR`, `COPY`,
and `CMD`, in that order. If `WORKDIR`, `COPY`, or `CMD` is missing, a `# TODO`
is still unfilled.

**Try a variation (optional).** Read the `.dockerignore` file. It excludes
Python bytecode and `__pycache__/` folders if you happen to run the app locally
before building. Leave it as is — a small, intentional build context is a habit
worth keeping.

::: solution
**Solution.** Four instructions, in order: pick the base image, set the working directory, copy the app in, set the default command. Docker can cache and reuse unchanged build results.

```dockerfile
# Start from a small official Python base image (Python 3.11 on slim Debian).
FROM python:3.11-slim

# Everything below runs relative to /app inside the image.
WORKDIR /app

# Copy the app (summarize.py + holdings.csv) into the working directory.
# No pip install: the script is stdlib-only, so there is nothing to add.
COPY app/ ./

# The default command when the container starts: run the summary script.
CMD ["python", "summarize.py"]
```

`COPY app/ ./` puts `summarize.py` and `holdings.csv` side by side in `/app`, so the script opens the CSV by its bare name. The `CMD` exec-form array runs Python directly, with no shell wrapper.

Reference: `solution/Dockerfile`.
:::

\newpage

## 4. Build the image

**Concept.** `docker build` reads the Dockerfile and **bakes** the recipe plus
your app into an image. It processes each instruction and caches reusable build
results; the `-t` flag tags the image with a name you can run later. The `.` at
the end is the **build context** — the folder Docker sends to the builder, from
which `COPY` reads. Build a second time without changing anything and most steps
say `CACHED` because Docker reuses results whose inputs did not change.

Docs: docker build: https://docs.docker.com/reference/cli/docker/buildx/build/

**Challenge (authoring).** Nothing new to write — build the image from the
Dockerfile you completed. From the folder that holds the `Dockerfile`:

```bash
docker build -t portfolio-summary .
```

Watch the steps go by. Then run the **exact same command again** and notice how
much of it is `CACHED` the second time.

**Hint.** `-t portfolio-summary` names the image; `.` is the build context (this
folder). The first build pulls the `python:3.11-slim` base and runs every step;
the second build, with nothing changed, reuses cached layers and finishes almost
instantly. If `COPY` re-runs on the second build, something under `app/` changed.

**How to check.** Confirm the image now exists in your local image store:

```bash
docker images | grep portfolio-summary
```

You should see a `portfolio-summary` row with a tag of `latest`, an image ID, and
a size (around 130 MB — almost all of it the shared Python base layer, not your
tiny app). That row is the frozen template you will run next.

**Try a variation (optional).** Change one number in `app/holdings.csv`, rebuild,
and watch *only* the `COPY` layer and everything after it re-run — the `FROM` and
`WORKDIR` layers stay `CACHED`. Put the number back. That is layer caching: only
what changed, and what depends on it, is rebuilt.

\newpage

## 5. Run your image (portability)

**Concept.** `docker run portfolio-summary` starts a container from the image you
built and runs its `CMD` — your `summarize.py`. The payoff is **portability**:
this image prints the same summary on any machine with Docker, because the app,
Python, and the OS libraries all travel inside it. It does not borrow the host's
Python or system libraries and break when they differ. That is the module's
single yes/no made real: instead of forever asking "is everything configured
right on this machine?", you ask one question, answered once at build time —
**did the container run?** A compatible Docker host can run the same image
without separately installing the app's Python dependencies.

Docs: docker run: https://docs.docker.com/reference/cli/docker/container/run/

**Challenge (authoring).** Nothing new to write — run your image and read the
summary. From the folder with the `Dockerfile`:

```bash
docker run --rm portfolio-summary
```

**Hint.** No `python --version` this time — the image's own `CMD` runs, which is
`python summarize.py` inside `/app`. The script opens `holdings.csv` (copied in
beside it), sums the `market_value` column over six rows, and prints the total.
`--rm` cleans up the finished container.

**How to check.**

```bash
docker run --rm portfolio-summary
```

You should see exactly:

```text
Portfolio summary
6 holdings, total market value 12,011,626.50
```

That is your app running inside a container you built — and it would print the
identical two lines on any machine with Docker, with no setup beyond `docker run`.
For the one-command gate, run `mise run challenge:verify 01` from anywhere in
the repository (or `bash ../verify.sh` from `starter/`). It builds the starter
image, runs it, checks the exact two-line output, and prints `PASS`.

**Try a variation (optional).** Same image, different data. Mount a different CSV
over the one baked in and re-run — the image is unchanged, but the output
follows the new file:

```bash
docker run --rm -v "$PWD/app/holdings.csv:/app/holdings.csv" portfolio-summary
```

(Here it mounts the same file, so the output matches; point `-v` at any CSV with
the same columns and you get a different summary from the **same** image. That is
the separation of image from data.)

\newpage

## 6. Try it yourself (optional)

**Concept.** An image is a thing you **ship**. You tag it with a version so a
specific build can be named, pushed to a registry, and pulled elsewhere — exactly
how this firm moves its Airflow and dbt images from a laptop to the cloud. Tagging
does not rebuild anything; it adds a second name pointing at the same image.

**Challenge (authoring).** Give your image an explicit version tag, then list
your tags:

```bash
docker tag portfolio-summary portfolio-summary:v1
docker images | grep portfolio-summary
```

**Hint.** `docker tag <source> <target>` adds a name; the underlying image ID is
the same for `portfolio-summary:latest` and `portfolio-summary:v1`. In a real
workflow the next step is `docker push` to a registry, which is how a teammate or
a cloud runner gets the *exact* image you built — same bytes, same behaviour.

**How to check.**

```bash
docker images | grep portfolio-summary
```

You should now see two rows — `latest` and `v1` — sharing one image ID. Two
names, one image: that is how a build gets a version label without being rebuilt.

**Try a variation (optional).** Run the tagged version explicitly with
`docker run --rm portfolio-summary:v1` and confirm it prints the same summary —
`:v1` is the same image you already built and ran.

\newpage

## That is the lab

You ran a container from an image and watched it exit; you stepped inside one and
saw its isolated filesystem and user-space tools; you wrote a Dockerfile, built
it into an image, and ran your own container that printed the portfolio summary
— the same output on a compatible machine with Docker. That is the whole loop
the module describes: code and user-space libraries wrapped together so machine
differences matter less, and "is it configured right?" collapses to "did the
container run?"

## Troubleshooting

- **`Cannot connect to the Docker daemon`** — the engine is not running. Start
  Docker Desktop or confirm Docker is up in the repository devcontainer, then re-run.
  `docker info` should print engine details, not an error.
- **`permission denied while trying to connect to the Docker daemon socket`** —
  on Linux your user is not in the `docker` group. Use the repository devcontainer,
  or add your user to the group and re-log (`sudo usermod -aG docker $USER`),
  then start a new shell.
- **`exec format error` or the script not found** — usually CRLF line endings in
  the Dockerfile or `summarize.py` after editing on Windows. Save the files with
  LF (Unix) line endings and rebuild.
- **The first `docker run` or `docker build` is slow** — it is pulling the
  `python:3.11-slim` base image over the network the first time. That is a
  one-off; later builds and runs reuse the cached layers and are fast.
