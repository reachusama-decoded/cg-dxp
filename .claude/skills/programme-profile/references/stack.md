# CG Core stack

Overrides and additions to the Decoded defaults in `courseware-conventions/references/tech-stack.md`. Where this file speaks, it wins.

## Configuration and keys

`.env` at the root of the session's `learner/moduleNN-<slug>/` folder (or `instructor/moduleNN-<slug>/` for the demo) (or the repo root during development), loaded with `python-dotenv`. `.env.example` ships with placeholder values and a one-line comment per key; `.env` is gitignored and never shipped. Never print a key; never paste one into a cell.

```
OPENAI_API_KEY=replace-me
OPENAI_BASE_URL=https://<decoded-proxy>/v1       # Decoded reverse proxy in front of OpenRouter; URL per cohort
LLM_MODEL=<openrouter-model-id>                 # e.g. openai/gpt-5-mini; working default to confirm
```

Keys are issued by Decoded for the reverse proxy (OpenRouter behind it; MJB shares the OpenRouter details on request) and are **not** guaranteed on every laptop on the day. Every LLM-calling demo and challenge therefore has: (a) a setup check that fails with a clear message naming the missing variable, and (b) offline fixtures (recorded responses or deterministic stubs) so the engineering parts run without a key. Live-model evidence is a separate, labelled step. This is the Deloitte capstone's "offline fixtures, live route preserved" pattern.

## LLM calls

The one raw call S03 M3 shows first, so the vendor call is not a black box; every later call goes through LangChain (below).

```python
# One client for the module, configured from .env — swap vendor by changing the two URLs/model lines, not the code
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI(
    base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"]
)
MODEL = os.environ.get("LLM_MODEL", "gpt-5-mini")


class FundSummary(BaseModel):  # the shape we require back — validated, not hoped for
    fund_id: str
    one_line: str
    risks: list[str]


response = client.beta.chat.completions.parse(  # structured output: the model must return a FundSummary
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    response_format=FundSummary,
)
summary = response.choices[0].message.parsed
```

Rules (user, 2026-10-15, replacing "no LangChain"): after that one raw call, LangChain's `langchain-openai` chat model pointed at `OPENAI_BASE_URL` with `LLM_MODEL` as a setting, reusing the AI Accelerator flows; Pydantic for every structured output and tool schema; `timeout` set; retries bounded; a deterministic check on every field the application relies on; rough answers from a small model are teaching material.

## Engineering tools

| Need | Use | Notes |
|---|---|---|
| Python | 3.13 (user, 2026-10-15) | Matches CG's dev container (pins 3.13.0) and Catalyst RFD 0008 PY-VERSION-001 (3.12 or later). `uv` preferred (`uv venv --python 3.13`, `uv pip install -r requirements.txt`); plain `pip` shown as the fallback. Docker examples use `python:3.13-slim` |
| Editor and AI | VS Code + Copilot; Catalyst AI skills | Demonstrate CG's workflow in the task, never as a separate AI lesson |
| Tests, lint | `pytest`, `ruff` | |
| Version control | Git, pull requests on the team's Git server | Branches and pull requests on the local Harness Open Source server (`common/services/harness/`, S02 decision D2; accounts `jordan` and `reviewer`); GitHub stays CG context (outcome 3 reads "on the team's Git server"; individual corporate GitHub accounts, MJB 2026-10-13, are CG's). `git init -q`; never let a home path into shipped output |
| Containers | Docker, Compose | Learners have Docker on their laptops; CG systems run Podman. Every container command carries a comment per flag |
| CI | Harness, CG's CI/CD platform; Harness Open Source run as a container for teaching (Drone-style pipeline YAML, steps run in Docker) | Runs as a local service under `courseware/common/services/`, like every container the course uses (profile rule 3); `services/harness/` (S02), port 3000, pipelines in `.harness/*.yaml`. S02 settled the Docker socket: the Harness container mounts it so pipeline steps run in containers; the challenge pipeline runs the tests only, with no image build, and the handbook names the socket's root-level risk. CG is not using GitHub Actions |
| API | FastAPI + uvicorn (confirmed by MJB 2026-10-13) | JSON only; `/health` plus the real endpoints; Pydantic response models |
| Local SQL | DuckDB | Parquet/CSV in, SQL out; the local stand-in for the lakehouse |
| Retrieval (RAG) | A LangChain retriever over `courseware/common/data/demo/documents/` (demos) and `courseware/common/data/challenge/documents/` (challenges); DuckDB full-text search as the portable baseline, a small shipped embedding model only if it earns its place | No hosted vector database; embeddings via the Decoded proxy to confirm (S04 M4) |
| Transformations | dbt-duckdb in the dev container | CG's own container also carries dbt-databricks (a client fact; content doesn't depend on it) |
| Orchestration | Airflow in Docker Compose, a local service under `courseware/common/services/` | CG's own container has Airflow pre-installed (a client fact; content doesn't depend on it) |
| Data science | pandas, numpy, scipy, statsmodels, scikit-learn, matplotlib/plotly | CPU only |
| Local models | PyTorch, Hugging Face transformers | No Hugging Face Hub access at CG: model files shipped under `courseware/common/data/models/`; run in the dev container (small, CPU-safe models), otherwise through the model API; `USE_TF=0` |
| Platforms (CG) | Databricks, Catalyst | CG context in content (Catalyst boxes, Databricks as CG's lakehouse); never a CG-access note (profile rule 3) |
| Dev environment | The dev container the course folder opens in, `courseware/.devcontainer/`, running locally on the learner's laptop; tested by `scripts/test-dev-container.sh` | Every demo and challenge runs in it and the local services in `courseware/common/services/` (profile rule 3); Decoded hosts only the model-API reverse proxy. Per-learner Labs VMs not assumed |

## Served apps

Local only (profile rule 3): `uvicorn app:app --host 0.0.0.0 --port <port>` inside a container, `http://localhost:<port>` from the laptop. Every served app has a `/health` route and the README says how to stop it.

## Port registry

Extend, do not clash. Check here and the neighbouring sessions before choosing a port, and register a service's ports before it's built.

| Port | What runs there | Module |
|---|---|---|
| 8000 | FastAPI demo API | S03 M2 |
| 8010 | FastAPI challenge API | S03 M2 |
| 8080 | Airflow webserver (Compose default) | S08 M5 |
| 8100 | Capstone API | S09 |
| 8888 | Jupyter (dev container) | all |
| 3000 | Harness Open Source: repositories, pull requests and pipelines (`common/services/harness/`) | S02 M5, M6 |
| 8020 | The fund report API in its container, demo | S02 M6 |
| 8021 | The fund report API in its container, challenge | S02 M6 |
| 2222 | SSH into the remote container | S01 M2 |

## Given analysis package (U2)

`courseware/common/code/harbourline_analysis/` is a small, tested Python package (returns, drawdown, benchmark comparison, summary statistics) that returns plain dicts from the synthetic pack. The AI engineering pair wraps it, grounds generated text in it and serves it; learners do not need to understand its internals until U3 opens them up. Built once in S03 M2's stage 2 and never duplicated into module folders. Its functions are the capstone's analysis baseline.

## Copilot at CG

Copilot in VS Code is the paid version and is enabled for learners (MJB, 2026-10-13); ask Will for the same for development. Which models, modes and settings CG enables is an "at CG" question for Catalyst first, then Michael, tracked in Asana outside the content. Content describes standard VS Code Copilot (the Ask, Plan and Agent modes; the model picker; context attachments; `/compact`-style context management) with no caveat about CG's settings (profile rule 3).

## Dev container (working)

The course runs in **the dev container** the course folder opens in, running locally on the learner's laptop (profile rule 3; user, 2026-10-16). Content calls it "the dev container", never "the CG dev container". **Built (2026-10-16): `courseware/.devcontainer/`**, kept as simple as possible, with no Dockerfile: `devcontainer.json` takes the prebuilt `mcr.microsoft.com/devcontainers/python:3.13-trixie` (Debian, Python 3.13, git, `ssh` and `scp`), the `docker-outside-of-docker` feature (`moby: false`, Docker's own CLI and Compose, talking to the laptop's Docker), `--add-host=host.docker.internal:host-gateway`, `remoteEnv` giving `HARBOURLINE_DATA` and `HARBOURLINE_KEYS` the laptop's paths through `${localWorkspaceFolder}` (so `bash service.sh start` works inside), a `postCreateCommand` that pip-installs `.devcontainer/requirements.txt`, and the Python, Jupyter, Copilot and Copilot Chat extensions; `devcontainer-lock.json` pins the feature. `requirements.txt` holds S01's pins (numpy 2.5.4, pandas 2.3.3, pyarrow 26.0.0, the same as `scripts/requirements.txt` and the remote's; ipykernel 7.4.0); a later session adds its own pins there when it is built (uv, DuckDB, dbt-duckdb, pytest, ruff, LangChain, the openai SDK, Pydantic, FastAPI, the data-science set), and adds a Dockerfile only if something truly can't be done without one. Learners work in VS Code's terminal inside it for everything, the services included (user, 2026-10-16). `scripts/test-dev-container.sh` brings it up with the dev containers CLI (`npx @devcontainers/cli@0.89.0`) and checks it end to end: 15 checks (2026-10-16), the last one that a fresh venv installs the pins from pip's download cache (`postCreateCommand` keeps it, decision D4). The build copies it to `release/latest/.devcontainer/`, at the top of the course folder as in `courseware/` (user, 2026-10-27). Every demo and solution is verified in it. CG has its own dev container with Python, dbt and the Databricks adapter, Airflow and the data/ML libraries pre-installed (MJB, 2026-10-13); keeping the two aligned (CG's container definition, adding `langchain` and `langchain-openai` through MJB, carefully) is tracked in Asana and never written into the content.

## Pins (user, 2026-10-26)

`courseware/.devcontainer/requirements.txt` is the one list of versions. Every project `requirements.txt`, pipeline install step, Dockerfile base image and version quoted in a handbook matches it (`scripts/check_pins.py` fails on a mismatch). A session's new pins are resolved with every transitive dependency pinned and nothing newer than about two weeks old (S02: resolved for Python 3.13 with nothing newer than 2026-10-12; left unpinned, pip pulled python-dateutil 3.0.0 and starlette 1.10.0), and `pip check` is clean. Each project folder keeps its own `requirements.txt` when the thread teaches a pinned project (S02: pytest pinned beside the report's packages, one file). No warning appears in learner-visible output: change a pin or the code rather than hide it (S02: httpx2, httpcore2 and truststore replaced httpx, httpcore and certifi because starlette's TestClient warned). After any pin change, re-run every affected output and `scripts/test-dev-container.sh`. Quoted outputs come from the dev container image only; `.venv/bin/python` is for tooling and quick checks.

Images are pinned to an exact version tag, never `latest` or a bare minor (user, 2026-10-27). Security fixes override the two-week rule. Harness: `harness/harness:3.3.0` is the newest Harness Open Source release (checked 2026-10-27; the only published advisory, CVE-2025-58158, is fixed in 3.3.0; the CVEs scanners list for the image are in its bundled Alpine packages and Go libraries and need a new upstream build). Before moving to a newer release, check that the screens and API the M5 and M6 demos use are unchanged; the `unstable` builds are not releases. Harness's clone image, `drone/git:latest`, is hardcoded and has no version tag, so `service.sh start` pulls it by digest and tags it with that name (`CLONE_IMAGE` in `common/services/harness/service.sh`). Notes and sources: `reference/cg-core-research/security/notes-2026-10-27.md`.

## SSH remote (S01 M2)

There is no CG remote target. **Decided (user, 2026-10-15): a second Docker container on the learner's laptop.** It lives once in `courseware/common/services/remote-machine/` (`service.sh`, `compose.yaml`, `Dockerfile`, `README.md`), shared by every session that needs a remote (moved there from S01's `demo/remote/`, user, 2026-10-15): Python 3.13 with the pinned data libraries, OpenSSH with key-only login as the non-root user `jordan`, host keys made per container, the two datasets read-only at `/data`, logs writable at `/var/log/harbourline`, published on `127.0.0.1:2222` only. Each learner's own public key goes in `keys/` (the key pair is the teaching moment). `scripts/test-remote-machine.sh` builds it, runs every move M2 teaches, checks `service.sh` and tears it down: 28 checks (2026-10-16), the newest that a venv on the remote installs the course pins (it needs the network), including from another container by Docker network name and through `host.docker.internal:2222`, the route a dev container uses, and `service.sh connect` from inside a container. Learners start the remote and do S01's SSH work in VS Code's terminal, inside the dev container, where the key is made (user, 2026-10-16; supersedes the laptop's-own-terminal route): Docker would read the bind-mount paths as the laptop's, so `service.sh start` refuses inside a container unless `HARBOURLINE_DATA` and `HARBOURLINE_KEYS` give the laptop's paths, which the dev container sets, and `connect` uses `host.docker.internal` (`HARBOURLINE_HOST` overrides it). The laptop's own terminal, with `localhost`, is the README's one fallback line. `scripts/test-dev-container.sh` checks the start and an SSH login from inside the dev container.

The remote runs locally like every service, so content needs nothing from CG. Anything about CG's laptops (its registries, an SSH client in CG's own container) is tracked in Asana, never written into the README or the session files (profile rule 3). Per-learner Decoded Labs VMs and a Decoded-hosted SSH VM are not needed.
