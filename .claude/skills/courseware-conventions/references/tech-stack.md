# Default tech stack: LLM calls, keys, serving

Decoded-wide defaults. A programme profile may override any of them; when it does, the profile wins. **CG Core overrides the LLM client (OpenAI-compatible SDK + Pydantic, no LangChain), the key file (`.env`, not `secrets.txt`), key guarantees (keys are NOT guaranteed at CG; offline fixtures required) and serving (local Docker ports first). Read `programme-profile/references/stack.md` before anything here.**

## Keys and secrets

`secrets.txt` is a plain visible file at the session root (dotfiles are hidden in the virtual labs), `KEY="value"` lines, never committed with real values and never printed. Load it sequentially — no candidate loops:

```python
# Load the API key — python-dotenv reads secrets.txt into environment variables
import os
from dotenv import load_dotenv

load_dotenv("secrets.txt")                        # this folder…
load_dotenv("../secrets.txt")                     # …or the session folder — a missing file is skipped
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
assert OPENAI_API_KEY, "No OPENAI_API_KEY in secrets.txt — tell the instructor before going on"
print("✅ API key found")
MODEL_NAME = "gpt-5-nano"
```

In `.py` apps anchor the path with `HERE = Path(__file__).parent` and `load_dotenv(HERE / "…")`.

**Keys are guaranteed in the learner environment**, so there are no `HAS_KEY` branches, no keyless fallbacks, and no local open-source models standing in for an API call. A missing key is an error at setup, not a degraded session. Where a programme ships a `secrets.example.txt` for learners to fill in, the profile says so.

**API-embeddings truthfulness**: with hosted embeddings, chunk text leaves the machine at indexing and the probe needs the key too — never claim "embeddings run locally" or "retrieval never left this machine". The honest privacy story: files are never uploaded as files; text goes out at two points (chunks at indexing, retrieved passages at generation); locked-down environments swap both for self-hosted models.

## LLM calls

LangChain only (`from langchain_openai import ChatOpenAI`), model from `MODEL_NAME`, `timeout=20` or more (reasoning latency), `max_retries`, no `temperature` (gpt-5 models reject non-default values). One `ask_llm()`-style helper per notebook:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model=MODEL_NAME, api_key=OPENAI_API_KEY, timeout=30, max_retries=2)

def ask_llm(prompt):
    """One place for the LLM call, so every cell below reads the same way."""
    return llm.invoke(prompt).content          # .invoke sends the prompt, .content is the reply text
```

Never a direct provider SDK import (`from openai import …`). Rough answers from a small model are teaching material — do not upgrade the model to make outputs prettier.

## Setup cells

Minimal: package check (green ticks via `importlib.metadata`), key load, file checks, `MODEL_NAME`. Plumbing lives where it belongs — library-quieting env vars beside the import they quiet, `import pandas as pd` at first use, reset guards in the cell whose narrative they serve. A learner reading the setup cell should understand every line of it. Servers and apps do not start in setup — each starts in its own clearly-headed cell inside the section that uses it.

## Lab serving (Decoded labs — https://guide.labs.decoded.com/)

- URL pattern is **subdomain-per-port**: `https://<port>-lab<NNNN>.labs.decoded.com/` for any port **2000–9000**. Named shortcuts exist (`app`→5000, `app1`–`app5`→5001–5005, `svc`→8100, `svc1`–`svc5`→8101–8105) but the number form is what content uses.
- **Reserved ports — never use**: 80, 22, 8001 (VS Code), 8002 (Jupyter), 8003 (GUI), 8005.
- Three universal requirements: bind `0.0.0.0` (never localhost/127.0.0.1), port in 2000–9000, trust the gateway's proxy headers (it terminates HTTPS).
- FastAPI: `uvicorn api:app --host 0.0.0.0 --port <port> --proxy-headers --forwarded-allow-ips="*"` — no `root_path`.
- Streamlit: `streamlit run app.py --server.address 0.0.0.0 --server.port <port> --server.headless true --server.enableCORS false --server.enableXsrfProtection false` — no `--server.baseUrlPath`.
- Gradio: `demo.launch(server_name="0.0.0.0", server_port=<port>, prevent_thread_lock=True, quiet=True)` — no `root_path`.
- These URLs are **public — no login in front of them**. So (a) code can call them — curl/requests/notebooks reach `https://<port>-lab<N>...` directly, no browser-vs-code split; (b) READMEs for served apps carry a one-line note that the URL is open to anyone who has it — synthetic data only, change demo passwords.
- Never use the legacy `/proxy/<port>` path-proxy URLs.
- Notebooks derive the learner's URLs from the VM hostname, defaulting to the public URL with localhost as a switchable option:

```python
import socket
LAB_HOST = socket.gethostname()                       # e.g. lab1234.labs.decoded.com
BASE_URL = f"https://5005-{LAB_HOST}"                 # public URL — works in the browser AND from code
# BASE_URL = "http://localhost:5005"                  # local alternative — same app, VM-only
```

(`socket.gethostname()` only works on the VM itself, not inside a container.)

- Troubleshooting pointer for learners: https://guide.labs.decoded.com/ (its diagnostic: `ss -tlnp | grep :<port>` — `0.0.0.0:<port>` good, `127.0.0.1:<port>` is the classic failure).
- **Ports are registered per programme** in the profile. Check it before choosing one; extend it when you add an app.
- The lesson plan's instructor guide carries the session's full port map (port · what runs there · started from) plus diagnostics — first fix `stop_server(<port>)`, then `lsof -i :<port>` / `kill` from a terminal.

## Server lifecycle helper (uvicorn-served apps)

Notebooks that start background servers define one canonical `start_server(app, port, folder=".")` / `stop_server(port)` cell — headed `# Run once, use all day`, comments not docstrings. `start_server` is re-run-safe (checks `/docs` before launching, waits up to 20s, prints ✅/❌ with the URL); `stop_server` terminates the tracked process or `pkill -f "uvicorn.*{port}"` for orphans from earlier kernels, and doubles as the port-jam fix. The helper cell is copied per notebook (never imported — notebooks stand alone) and byte-identical across them. Notebook-started servers are the in-session pattern; the terminal is the deliberate step-up in a resource or stretch ("a product is programs running, not notebook cells").

Long-running servers start via `subprocess.Popen` in a dedicated, clearly-headed cell inside the section that uses them (not in setup); Gradio demos use `prevent_thread_lock=True` and close after.

## Container and cloud sessions

Where a programme uses a cloud lab (an emulator or a real account), the profile names the interface, its guide URL and its glossary. Every first mention of a service in a markdown cell links to its guide page; the learner-facing name is the one the profile gives (never the internal one). Every container command carries a comment above it explaining each flag. Never have learners pull each other's images.
