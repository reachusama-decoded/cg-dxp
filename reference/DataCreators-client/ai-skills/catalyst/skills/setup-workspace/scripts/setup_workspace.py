#!/usr/bin/env python3
"""setup_workspace.py — detect, verify, and (where safe) configure the local
toolchain AI Catalyst needs.

Two subcommands:

  check      Read-only.  Reports OS, Python, pip -> cgrepo, dependencies, and
             the git/gh tools.  Exit 0 means ready; a non-zero code is the
             top-priority blocker (see EXIT CODES).
  configure  Requires Python 3.10+ already present (provision it first with
             bootstrap.sh, which needs no Python).  Points pip at cgrepo and
             installs the core Catalyst dependencies through cgrepo
             (tested-against extras are best-effort).  Never runs sudo.

Optional:

  tool git|gh  Installs one extra tool through an existing package manager, or
               guides when none is present.

Python provisioning (install/upgrade, or guide to self-service) is handled by
bootstrap.sh, which needs no Python.  This script assumes Python already exists
and focuses on the Python-dependent steps.

EXIT CODES (check):
  0  ready
  2  Python missing or older than 3.10 (run bootstrap.sh to provision it)
  4  dependencies missing
  5  pip not pointed at cgrepo

The safe, read-only helpers at the top are unit-tested by
tests/skills/test_setup_workspace.py.  install.md is the source of truth for the
versions and URLs referenced here.
"""
from __future__ import annotations

import argparse
import configparser
import difflib
import json
import os
import platform
import re
import shutil
import socket
import ssl
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# --- Facts from docs/install.md (the source of truth) ------------------------
MIN_VERSION = (3, 10)
RECOMMENDED = (3, 13)
CGREPO_INDEX = "https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/"
CGREPO_HOST = "cgrepo-aws.capgroup.com"
REQUIREMENTS = Path(__file__).resolve().parents[2] / "requirements.txt"

# Representative import probe (package -> import name).
CORE_DEPS = {
    "pydantic": "pydantic",
    "pyyaml": "yaml",
    "requests": "requests",
    "databricks-sdk": "databricks.sdk",
}

# Package managers per OS, used to detect the environment and to install the
# optional git/gh tools.  Python provisioning lives in bootstrap.sh, not here.
MANAGERS_BY_OS = {
    "darwin": ["brew", "uv"],
    "windows": ["winget", "choco", "uv"],
    "linux": ["apt-get", "dnf"],
}

# Install commands for the optional git/gh step, keyed by package manager.
# Deliberately narrower than MANAGERS_BY_OS: `uv` manages Python, not arbitrary
# tools, and the Linux managers need sudo, which this skill never invokes. A
# manager absent here is reported honestly by `tool` rather than advertised by
# `check` and then refused -- see cmd_tool and cmd_check.
TOOL_INSTALL_COMMANDS = {
    "brew": lambda name: ["brew", "install", name],
    "winget": lambda name: [
        "winget", "install", "-e", "--accept-source-agreements",
        "--accept-package-agreements", "--id",
        "GitHub.cli" if name == "gh" else "Git.Git",
    ],
    "choco": lambda name: ["choco", "install", name, "-y"],
}


def can_install_tools(os_name: str | None = None) -> bool:
    """Whether the detected manager can install the optional git/gh tools."""
    return detect_package_manager(os_name) in TOOL_INSTALL_COMMANDS


# --- Read-only helpers (pure enough to unit-test) ----------------------------
def detect_os() -> str:
    """Return 'darwin', 'windows', 'linux', or the lowered platform name."""
    return {"Darwin": "darwin", "Windows": "windows", "Linux": "linux"}.get(
        platform.system(), platform.system().lower()
    )


def detect_package_manager(os_name: str | None = None) -> str | None:
    """Return the first package manager found on PATH for this OS, else None."""
    os_name = os_name or detect_os()
    for mgr in MANAGERS_BY_OS.get(os_name, []):
        if shutil.which(mgr):
            return mgr
    return None


def parse_python_version(text: str) -> tuple[int, int] | None:
    """Parse '(major, minor)' out of a 'Python 3.13.1' style string."""
    m = re.search(r"(\d+)\.(\d+)", text or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def meets_floor(version: tuple[int, int] | None) -> bool:
    return version is not None and version >= MIN_VERSION


def is_too_new(version: tuple[int, int] | None) -> bool:
    return version is not None and version > RECOMMENDED


# --- Environment probes (call out to the real toolchain) ---------------------
# Quick probes use the short default; installs (pip, package managers) can take
# several minutes, so they pass INSTALL_TIMEOUT.
INSTALL_TIMEOUT = 900


def _run(cmd: list[str], timeout: int = 30) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)


def find_python() -> tuple[str | None, tuple[int, int] | None]:
    """Find the interpreter skills would use: python3, then python."""
    for exe in ("python3", "python"):
        path = shutil.which(exe)
        if not path:
            continue
        rc, out = _run([path, "--version"])
        if rc == 0:
            return path, parse_python_version(out)
    return None, None


def pip_index_is_cgrepo(python_exe: str) -> bool:
    rc, out = _run([python_exe, "-m", "pip", "config", "list"])
    return rc == 0 and "cgrepo" in out and "index-url" in out


def deps_present(python_exe: str) -> bool:
    probe = "import " + ", ".join(sorted(set(CORE_DEPS.values())))
    rc, _ = _run([python_exe, "-c", probe])
    return rc == 0


def gh_authenticated() -> bool:
    if not shutil.which("gh"):
        return False
    rc, _ = _run(["gh", "auth", "status"])
    return rc == 0


# --- State + reporting -------------------------------------------------------
def gather_state() -> dict:
    os_name = detect_os()
    mgr = detect_package_manager(os_name)
    py_exe, py_ver = find_python()
    py_ok = meets_floor(py_ver)
    state = {
        "os": os_name,
        "package_manager": mgr,
        "can_install_tools": mgr in TOOL_INSTALL_COMMANDS,
        "python_exe": py_exe,
        "python_version": py_ver,
        "python_ok": py_ok,
        "python_too_new": is_too_new(py_ver),
        "pip_cgrepo": pip_index_is_cgrepo(py_exe) if py_exe else False,
        "deps": deps_present(py_exe) if py_exe else False,
        "git": bool(shutil.which("git")),
        "gh": bool(shutil.which("gh")),
        "gh_authed": gh_authenticated(),
    }
    return state


def exit_code_for(state: dict) -> int:
    """Top-priority blocker per the documented precedence.

    Python provisioning is bootstrap.sh's job (it needs no Python), so a Python
    gap here simply means "run bootstrap.sh first".
    """
    if not state["python_ok"]:
        return 2
    if not state["pip_cgrepo"]:
        return 5
    if not state["deps"]:
        return 4
    return 0


def _mark(ok: bool) -> str:
    return "ok" if ok else "MISSING"


def cmd_check() -> int:
    s = gather_state()
    code = exit_code_for(s)
    ver = ".".join(map(str, s["python_version"])) if s["python_version"] else "none"
    print("AI Catalyst workspace check")
    print(f"  OS:               {s['os']}")
    # Say plainly whether the detected manager can install the optional tools, so
    # `check` cannot advertise one that `tool` will then refuse to use.
    if s["package_manager"]:
        suffix = "" if s["can_install_tools"] else " (cannot install git/gh here)"
        print(f"  Package manager:  {s['package_manager']}{suffix}")
    else:
        print("  Package manager:  none detected")
    print(f"  Python:           {ver} ({_mark(s['python_ok'])}, need >= 3.10)")
    if s["python_too_new"]:
        print("    warning: newer than the recommended 3.13; dependency wheels "
              "may lag. Prefer 3.13 if a dependency install fails.")
    print(f"  pip -> cgrepo:    {_mark(s['pip_cgrepo'])}")
    print(f"  Dependencies:     {_mark(s['deps'])}")
    print(f"  git:              {'present' if s['git'] else 'absent'} (optional tool)")
    print(f"  gh:               "
          f"{'authenticated' if s['gh_authed'] else ('present, not authenticated' if s['gh'] else 'absent')} "
          f"(optional tool)")
    print(f"  Verdict:          {'READY' if code == 0 else 'NOT READY (exit ' + str(code) + ')'}")
    return code


# --- Configure (side-effecting; never sudo, never installs a manager) --------
def verify_cgrepo_tls(host: str = CGREPO_HOST, port: int = 443) -> tuple[bool, str]:
    """Confirm cgrepo's certificate validates against the system trust store.

    The honest alternative to `trusted-host`. When a corporate TLS-interception
    proxy re-signs the connection, the fix is to point pip at the corporate CA
    bundle (`cert = <path>`), which keeps the connection *verified*. Disabling
    verification for the one host every corporate install flows through would
    harden the supply chain at the registry and open it at the transport.
    """
    ctx = ssl.create_default_context()  # CERT_REQUIRED + check_hostname
    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                return True, "verified against the system trust store"
    except ssl.SSLCertVerificationError as exc:
        return False, (
            f"certificate verification failed ({exc.verify_message}). This is "
            "corporate TLS interception. Point pip at the corporate CA bundle "
            "with `cert = <path>` in pip.conf -- do not set trusted-host, which "
            "disables verification entirely."
        )
    except OSError as exc:
        return False, f"could not reach {host}: {exc}"


def _documented_pip_conf() -> Path:
    """The per-user config path docs/install.md documents."""
    if detect_os() == "windows":
        return Path(os.environ.get("APPDATA", str(Path.home()))) / "pip" / "pip.ini"
    return Path.home() / ".pip" / "pip.conf"


def _pip_conf_candidates() -> list[Path]:
    """Every per-user config pip reads, in pip's own precedence order."""
    if detect_os() == "windows":
        return [_documented_pip_conf()]
    # pip prefers the XDG location when both exist; install.md documents the legacy one.
    return [Path.home() / ".config" / "pip" / "pip.conf", _documented_pip_conf()]


def _pip_conf_path() -> Path:
    """Where to write.

    Merge into a config the user already has rather than creating a second,
    competing file whose precedence they would have to reason about. Only when
    nothing exists do we create the path install.md documents.
    """
    for path in _pip_conf_candidates():
        if path.exists():
            return path
    return _documented_pip_conf()


def ensure_pip_cgrepo(python_exe: str) -> bool:
    """Point pip at cgrepo, preserving every other setting already configured.

    Sets `index-url` and nothing else. A read-modify-write rather than an
    overwrite: clobbering `cert` on a machine behind TLS interception would break
    pip for everything else the user does, and `proxy` / `extra-index-url` /
    `timeout` are equally load-bearing.
    """
    if pip_index_is_cgrepo(python_exe):
        print("pip already points at cgrepo; nothing to do.")
        return True

    ok, detail = verify_cgrepo_tls()
    print(f"cgrepo TLS: {detail}")

    path = _pip_conf_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    parser = configparser.ConfigParser()
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak." + datetime.now().strftime("%Y%m%d%H%M%S"))
        shutil.copy2(path, backup)
        print(f"Backed up existing pip config to {backup}")
        try:
            parser.read(path)
        except configparser.Error as exc:
            # Do not guess at a malformed config -- the backup is the recovery path.
            print(f"Existing pip config at {path} is malformed ({exc}); "
                  f"leaving it alone. Restore from {backup} if needed.")
            return False

    if not parser.has_section("global"):
        parser.add_section("global")
    parser.set("global", "index-url", CGREPO_INDEX)

    with path.open("w", encoding="utf-8") as fh:
        parser.write(fh)

    preserved = sum(len(parser.options(s)) for s in parser.sections()) - 1
    print(f"Set index-url to cgrepo in {path}"
          + (f" ({preserved} existing setting(s) preserved)" if preserved > 0 else ""))
    if not ok:
        print("Note: pip may still fail TLS verification. Add "
              "`cert = <corporate CA bundle>` to the [global] section above.")
    return True


# requirements.txt splits itself at this comment: everything above is the core
# runtime; everything below is the "tested-against" block that the file itself
# says is NOT imported by Catalyst (dbt, the legacy databricks-cli).
# Anchored to the line start, not a bare substring: a future comment that merely
# mentions the phrase would otherwise move the core/extras boundary silently.
# --- Copilot Chat usage reporting (OTEL) -------------------------------------
#
# Why this is a textual edit and not a parse-and-rewrite: settings.json is JSONC.
# Round-tripping it through json.dumps would silently delete every comment and
# reflow the whole file -- the same class of damage as overwriting pip.conf,
# which is why this inserts and patches lines in place instead.
#
# captureContent is the one key with a compliance consequence: true sends
# conversation text and requires a Governance, Risk and Compliance review. This
# module writes `false` and only `false`. There is deliberately no parameter to
# request otherwise.

# Named collectors, mirroring CLAUDE_OTEL_COLLECTORS below and the set
# dplc-preflight accepts. Deliberately names only, no free-form URL: the checker
# reports anything that is not one of these two as a problem, so letting this
# write one would have the writer produce a state the checker rejects.
#
# Unlike claude-otel, this one defaults rather than requiring a choice -- prd is
# routable from the laptops Copilot Chat runs on, so there is a right answer to
# default to. dev is for someone who has asked for it.
OTEL_COLLECTORS = {
    "dev": "https://catalyst-otel.datalakefoundation.aws-dev.capgroup.com",
    "prd": "https://catalyst-otel.datalake.aws.capgroup.com",
}
OTEL_DEFAULT_COLLECTOR = "prd"

OTEL_KEYS: dict[str, str] = {
    "github.copilot.chat.otel.enabled": "true",
    "github.copilot.chat.otel.exporterType": '"otlp-http"',
    # Derived, never a literal. `plan_otel_settings` does `wanted = dict(OTEL_KEYS)`
    # and then unconditionally overwrites this key from OTEL_COLLECTORS, so a literal
    # here would be dead -- and a dead copy of a URL is one a future edit can leave
    # behind while the copy that is actually read moves on. This leaves exactly one
    # source for the URL, which is the point.
    "github.copilot.chat.otel.otlpEndpoint":
        '"%s"' % OTEL_COLLECTORS[OTEL_DEFAULT_COLLECTOR],
    "github.copilot.chat.otel.captureContent": "false",
}
OTEL_CAPTURE_KEY = "github.copilot.chat.otel.captureContent"
OTEL_ENDPOINT_KEY = "github.copilot.chat.otel.otlpEndpoint"

# The fifth setting, and the one whose absence is invisible. Copilot Chat 0.63.0
# does not emit `user.id` itself -- verified against 693 production payloads, none
# of which carried it (PR #434). Without it the data arrives and can never be
# attributed to a person, which is a silent failure rather than an error.
#
# The settings key, not OTEL_RESOURCE_ATTRIBUTES: the env var outranks it but
# never reaches a VS Code launched from the Dock.
OTEL_RESOURCE_ATTRS_KEY = "github.copilot.chat.otel.resourceAttributes"


def _mask_comments(text: str) -> str:
    """A same-length copy with comment bytes blanked out.

    Presence checks and property patterns run against this instead of the raw
    JSONC. Otherwise a commented-out line such as

        // "github.copilot.chat.otel.enabled": false

    reads as a live setting: the patch edits inside the comment, skips inserting
    the real key, and still reports a successful update. Offsets are preserved so
    a match found here can be applied to the original text.
    """
    out = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if text.startswith("//", i):
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if text.startswith("/*", i):
            while i < n and not text.startswith("*/", i):
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            out.append("  ")
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _existing_user_id(masked: str) -> str | None:
    """The `user.id` inside an existing resourceAttributes block, if any."""
    block = re.search(re.escape(OTEL_RESOURCE_ATTRS_KEY) + r'"\s*:\s*\{([^}]*)\}', masked)
    if not block:
        return None
    found = re.search(r'"user\.id"\s*:\s*"([^"]*)"', block.group(1))
    return found.group(1) if found else None


def _looks_like_initials(value: str) -> bool:
    """The one shape a corporate id may take here: 2-8 letters, nothing else.

    Deliberately strict. Everything that reaches settings.json goes through this,
    so anything it lets past is something a dashboard will attribute usage to.
    """
    return bool(value) and value.isalpha() and 2 <= len(value) <= 8


def detect_user_id() -> tuple[str | None, str]:
    """Best-effort corporate ID, with the source, so the caller can show its work.

    Never guesses: an unrecognisable value returns None so the caller can ask
    rather than writing an identity that attributes someone else's usage.
    """
    override = os.environ.get("CATALYST_OTEL_USER_ID")
    if override:
        candidate = override.strip().upper()
        # Held to the same bar as the git-email path below. Unvalidated, this
        # value is interpolated straight into settings.json, so a stray quote
        # corrupts the file and an arbitrary label silently misattributes usage
        # to something that is not a person.
        if _looks_like_initials(candidate):
            return candidate, "CATALYST_OTEL_USER_ID"
        return None, (f"CATALYST_OTEL_USER_ID={override!r} is not initials "
                      "(2-8 letters); ignoring it rather than writing an "
                      "identity nobody can be held to")

    # Accepts an initials-shaped local part (2-8 letters), which is what the EMU
    # login convention `<INITIALS>_capgroup` implies. `first.last@capgroup.com`
    # deliberately does NOT match -- initials cannot be derived from it without
    # guessing -- so that user falls through to the gh login below and, failing
    # that, is asked for CATALYST_OTEL_USER_ID by name. (An earlier version of this
    # comment cited docs/install.md for an `initials@capgroup.com` convention; no
    # such statement exists there.)
    code, out = _run(["git", "config", "--get", "user.email"])
    if code == 0 and "@" in out:
        local = out.strip().split("@", 1)[0]
        if _looks_like_initials(local):
            return local.upper(), "git config user.email"

    # GitHub EMU logins are INITIALS_capgroup.
    code, out = _run(["gh", "api", "user", "--jq", ".login"])
    if code == 0 and out.strip().lower().endswith("_capgroup"):
        initials = out.strip().rsplit("_", 1)[0]
        if initials.isalpha():
            return initials.upper(), "gh api user"

    return None, "could not determine"


def vscode_settings_candidates() -> list[Path]:
    """User-scope settings.json only, most-likely first.

    Workspace and folder settings do not enable the exporter, so writing one
    would look like success while doing nothing outside that folder.
    """
    home = Path.home()
    if sys.platform == "darwin":
        roots = [home / "Library" / "Application Support"]
    elif os.name == "nt":
        appdata = os.environ.get("APPDATA")
        roots = [Path(appdata)] if appdata else [home / "AppData" / "Roaming"]
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        roots = [Path(xdg)] if xdg else [home / ".config"]
    return [root / product / "User" / "settings.json"
            for root in roots
            for product in ("Code", "Code - Insiders", "VSCodium")]


def _otel_settings_path() -> Path | None:
    for path in vscode_settings_candidates():
        if path.exists():
            return path
    return None


def plan_otel_settings(path: Path | None = None, endpoint: str = OTEL_DEFAULT_COLLECTOR) -> dict:
    """Work out the edit without making it. Returns a plan the caller can show.

    Keys are patched in place when present and inserted after the opening brace
    when absent, so comments and formatting survive.
    """
    path = path or _otel_settings_path()
    if path is None:
        return {"ok": False, "reason": "no VS Code User settings.json found -- open VS Code "
                                       "once so it creates one, then re-run",
                "path": None, "diff": "", "new_text": None, "changes": []}

    try:
        original = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "reason": f"could not read {path}: {exc}",
                "path": str(path), "diff": "", "new_text": None, "changes": []}

    if not original.strip():
        original = "{\n}\n"

    # Every structural decision below is taken against a comment-masked copy, so a
    # commented-out setting is never read as live. Offsets are preserved, so an
    # offset found here applies to the original text.
    masked = _mask_comments(original)

    # The root brace is located in the masked copy, not by `original.strip()`.
    # A normal settings.json often *opens* with a comment -- VS Code writes one --
    # so requiring the file to start with `{` rejected perfectly valid files. And
    # a brace inside that leading comment would otherwise be picked as the
    # insertion point, putting our keys inside the comment where they do nothing.
    root = masked.find("{")
    if root < 0 or masked[:root].strip():
        return {"ok": False,
                "reason": f"{path} has no top-level '{{' outside a comment -- refusing "
                          "to guess at its structure",
                "path": str(path), "diff": "", "new_text": None, "changes": []}

    user_id, id_source = detect_user_id()
    # Whether an identity already exists, not merely whether the key appears. A
    # live block of `{ "team": "edo" }`, or the key sitting inside a `//` comment,
    # satisfied a presence check -- and then the key dropped out of `wanted`, so
    # none of the block validation below ran and four keys were written with no
    # identity at all. That is precisely what this refusal exists to prevent.
    if user_id is None and _existing_user_id(masked) is None:
        return {"ok": False,
                "reason": "could not determine your corporate ID, and writing the settings "
                          "without it would make every report anonymous. Re-run with "
                          "CATALYST_OTEL_USER_ID=<your initials>",
                "path": str(path), "diff": "", "new_text": None, "changes": []}

    wanted = dict(OTEL_KEYS)
    wanted[OTEL_ENDPOINT_KEY] = '"%s"' % OTEL_COLLECTORS[endpoint]
    if user_id is not None:
        wanted[OTEL_RESOURCE_ATTRS_KEY] = '{ "user.id": "%s" }' % user_id

    text = original
    changes: list[str] = []
    missing: list[str] = []

    for key, value in wanted.items():
        if key == OTEL_RESOURCE_ATTRS_KEY:
            # Its value is a JSON object, so the scalar pattern below cannot match
            # it, and an existing block may carry attributes beyond user.id that
            # are not ours to drop. But "a block exists" is not the same as "the
            # block identifies someone": one without user.id reports anonymously,
            # and one with a stale id -- settings copied from a colleague --
            # reports as them. Neither may be waved through as already correct.
            if key not in masked:
                missing.append(key)
                continue
            present = _existing_user_id(masked)
            if present is None:
                return {"ok": False,
                        "reason": f"{path} already has {OTEL_RESOURCE_ATTRS_KEY} but it "
                                  "carries no user.id, so reporting would stay anonymous. "
                                  "Add \"user.id\": \"<your initials>\" to that block by "
                                  "hand -- it holds attributes this skill will not rewrite.",
                        "path": str(path), "diff": "", "new_text": None, "changes": []}
            if user_id is not None and present.upper() != user_id.upper():
                return {"ok": False,
                        "reason": f"{path} reports as {present!r} but this machine looks like "
                                  f"{user_id!r} (from {id_source}). Copied settings attribute "
                                  "your usage to someone else. Fix the user.id in that block, "
                                  "or set CATALYST_OTEL_USER_ID if the existing value is right.",
                        "path": str(path), "diff": "", "new_text": None, "changes": []}
            continue
        # Match `"key": <value>`, stopping *before* any trailing same-line comment.
        # A greedy `[^,\n}]*` ran through the masked comment to end of line and
        # deleted it when the value was patched, so the group is lazy with a
        # lookahead at the real terminator instead.
        pattern = re.compile(r'("' + re.escape(key) + r'"\s*:\s*)([^,\n}]*?)(?=\s*(?:[,\n}]|$))')
        # Re-masked from the CURRENT text, not once from the original. `text` is
        # mutated after every replacement, so a mask built up front yields stale
        # offsets for every later key: a first patch that changes length shifted
        # the next one mid-token, producing `capfalseContent` (valid JSON, and
        # invisible to the captureContent guardrail because the key name changed)
        # or `tfalse}` (does not parse). Both while reporting success.
        match = pattern.search(_mask_comments(text))
        if match:
            current = match.group(2).strip()
            if current == value:
                continue
            if key == OTEL_CAPTURE_KEY and current == "true":
                changes.append(f"{key}: true -> false  (was sending conversation text)")
            else:
                changes.append(f"{key}: {current} -> {value}")
            text = text[:match.start(2)] + value + text[match.end(2):]
        else:
            missing.append(key)

    # Inserted as one block, in declaration order, so the result reads the way
    # the getting-started guide shows it rather than reversed.
    if missing:
        insert_at = root + 1
        # A trailing comma is fine before an existing property and illegal before
        # the closing brace. On `{}` the old unconditional comma produced output
        # that VS Code and `_strip_jsonc` tolerate but strict `json.loads` rejects
        # -- and this PR states that a stray comma breaking the file is a failure
        # mode it fixes, so it should not introduce one.
        rest = _mask_comments(text)[insert_at:].lstrip()
        has_following_property = bool(rest) and not rest.startswith("}")
        block = "".join(f'\n  "{k}": {wanted[k]},' for k in missing)
        if not has_following_property:
            block = block.rstrip(",")
        text = text[:insert_at] + block + text[insert_at:]
        changes.extend(f"{k}: (not set) -> {wanted[k]}" for k in missing)

    if not changes:
        return {"ok": True, "reason": "already configured correctly; nothing to change",
                "path": str(path), "diff": "", "new_text": None, "changes": []}

    diff = "".join(difflib.unified_diff(
        original.splitlines(keepends=True), text.splitlines(keepends=True),
        fromfile=str(path), tofile=f"{path} (proposed)"))
    return {"ok": True, "reason": "ready to apply", "path": str(path),
            "diff": diff, "new_text": text, "changes": changes,
            "user_id": user_id, "user_id_source": id_source}


def apply_otel_settings(plan: dict) -> bool:
    """Write the planned edit, after a timestamped backup.

    Refuses to write anything whose captureContent is true -- a last-line check
    against a future caller assembling the text itself.
    """
    if not plan.get("ok") or plan.get("new_text") is None:
        print(plan.get("reason", "nothing to do"))
        return plan.get("ok", False)

    new_text = plan["new_text"]
    # Masked, for the same reason the planner masks: a commented-out
    # `// "...captureContent": true` is inert, but matched raw it made this guard
    # refuse to write and exit 4, leaving the user no way forward except deleting
    # their own comment. The guard must see what Copilot Chat sees.
    if re.search(r'"' + re.escape(OTEL_CAPTURE_KEY) + r'"\s*:\s*true',
                 _mask_comments(new_text)):
        print("REFUSING to write: captureContent would be true. That sends conversation "
              "text and requires a Governance, Risk and Compliance review.")
        return False

    path = Path(plan["path"])
    backup = path.with_suffix(path.suffix + ".bak." + datetime.now().strftime("%Y%m%d%H%M%S"))
    try:
        shutil.copy2(path, backup)
    except OSError as exc:
        print(f"Could not back up {path} ({exc}); not writing.")
        return False
    print(f"Backed up existing settings to {backup}")

    try:
        path.write_text(new_text, encoding="utf-8")
    except OSError as exc:
        print(f"Could not write {path} ({exc}). Original is intact at {backup}.")
        return False

    for change in plan["changes"]:
        print(f"  {change}")
    print(f"Updated {path}")
    print("")
    # A window reload is sufficient -- verified by hand, and the same conclusion
    # RBLW reached from the extension manifest on #434. Earlier revisions of this
    # branch asserted a full quit was required; that was wrong, and it told users
    # to do more work than the exporter actually needs.
    print("NOW RELOAD THE WINDOW: Ctrl+Shift+P / Cmd+Shift+P -> Developer: Reload Window.")
    print("  That is enough to start reporting. Quitting and reopening also works.")
    return True


# --- Claude Code usage reporting (AICAT-337) ---------------------------------
#
# The asymmetry this closes: `otel` above can turn Copilot Chat reporting on for a
# user, and nothing could do the same for Claude Code. A developer who wanted it was
# handed `export` lines that die with the shell, or told to wait for a fleet rollout
# of docs/telemetry/managed-settings-otel.json.
#
# Why a user-scope file works at all: managed settings outrank user settings, and the
# DevNext managed policy sets CLAUDE_CODE_ENABLE_TELEMETRY, a logs exporter and the
# content switches -- but *none* of the four keys below. So there is nothing to
# outrank, and ~/.claude/settings.json takes effect.

CLAUDE_SETTINGS = Path.home() / ".claude" / "settings.json"

# Named collectors, because the choice is not cosmetic: production is not routable
# from an oz-dev Coder workspace (TCP 443 opens, TLS resets), so configuring it there
# silently drops every batch while every local check still reports ON.
CLAUDE_OTEL_COLLECTORS = {
    "dev": "https://catalyst-otel.datalakefoundation.aws-dev.capgroup.com",
    "prd": "https://catalyst-otel.datalake.aws.capgroup.com",
}
# Required on a per-signal endpoint. OTEL_EXPORTER_OTLP_ENDPOINT is a base URL and
# the exporter appends this itself; OTEL_EXPORTER_OTLP_METRICS_ENDPOINT is used
# AS-IS. A host-only value therefore POSTs to `/`, which the collector answers 404
# -- measured, not assumed -- so every batch is rejected while the configuration
# still reads as correct.
CLAUDE_METRICS_PATH = "/v1/metrics"

# Never written, by design rather than by omission. Content is only ever a LOG
# record, so a configuration that sets no logs destination is *structurally*
# incapable of sending prompt text to Catalyst -- a guarantee that survives someone
# later enabling a content switch, which a policy of four zeroes does not. The
# switches are also the enterprise's call, not this script's.
CLAUDE_FORBIDDEN_KEYS = (
    "OTEL_LOGS_EXPORTER",
    "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
    "OTEL_EXPORTER_OTLP_ENDPOINT",      # the generic fallback: logs would follow it
    "OTEL_LOG_USER_PROMPTS",
    "OTEL_LOG_ASSISTANT_RESPONSES",
    "OTEL_LOG_TOOL_CONTENT",
    "OTEL_LOG_RAW_API_BODIES",
    "OTEL_LOG_TOOL_DETAILS",
)


class EndpointError(ValueError):
    """An --endpoint value that is neither a known collector nor a URL."""


def normalise_metrics_endpoint(value: str) -> str:
    """A collector name or URL -> a full per-signal metrics endpoint.

    Rejects anything else rather than passing it through. `prod` -- the obvious typo
    for `prd` -- was previously written verbatim as `prod/v1/metrics` with a success
    message, and the lookup was case-sensitive so `DEV` did the same. That is exactly
    the silent black hole the named-collector design exists to prevent, so the
    validation belongs here rather than in the caller.
    """
    name = (value or "").strip()
    url = CLAUDE_OTEL_COLLECTORS.get(name.lower(), name)
    if url is name and not name.lower().startswith(("http://", "https://")):
        raise EndpointError(
            f"{value!r} is neither a known collector "
            f"({', '.join(sorted(CLAUDE_OTEL_COLLECTORS))}) nor an http(s) URL")
    url = url.rstrip("/")
    if not url.endswith(CLAUDE_METRICS_PATH):
        url += CLAUDE_METRICS_PATH
    return url


def detect_workspace_kind() -> str:
    """`coder-eks`, `coder`, or `local`. Separates the populations in the data.

    `KUBERNETES_SERVICE_HOST` is deliberately *not* consulted. It is visible in a pod
    but not in a host shell that shares the same `~/.claude`, so keying on it made the
    value flip between `coder-eks` and `coder` depending on where the command ran --
    and since the value is written to a file, every alternate run reported a change,
    rewrote it, and dropped another `settings.json.bak.<timestamp>`.

    A label that changes with the shell it was computed in is not a label. Coder
    workspaces at Capital Group are containerised, so `coder` and `coder-eks` were
    never distinguishing much anyway; the stable signal is Coder or not.
    """
    if os.environ.get("CODER_WORKSPACE_NAME") or os.environ.get("CODER_AGENT_TOKEN"):
        return "coder"
    return "local"


def claude_otel_env(endpoint: str, workspace_kind: str | None = None) -> dict:
    """The keys this writes, and only these.

    `CLAUDE_CODE_ENABLE_TELEMETRY` is included, which an earlier revision left out on
    the grounds that the managed policy supplies it. That was wrong for the audience:
    this command exists for the person who has *not* had a fleet rollout, and on that
    machine nothing exports at all while the tool still says to start a new session.
    Setting it is harmless where managed already does -- identical value, and managed
    wins regardless.
    """
    kind = workspace_kind or detect_workspace_kind()
    return {
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
        "OTEL_METRICS_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": normalise_metrics_endpoint(endpoint),
        "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL": "http/protobuf",
        # Strict format: no spaces, comma-separated. `telemetry.producer` is what
        # distinguishes this from VS Code Copilot Chat downstream -- the /s/<source>
        # S3 partition that would do it at the prefix level is not deployed.
        "OTEL_RESOURCE_ATTRIBUTES":
            f"workspace.kind={kind},department=edo,telemetry.producer=claude-code",
    }


def merge_resource_attributes(existing: str | None, wanted: str) -> str:
    """Ours merged into theirs, by attribute key, preserving their order.

    The value is itself a comma-separated list, so replacing it wholesale dropped an
    existing `service.name=foo,team=bar` silently -- the opposite of what the `env`
    block one level up does, and on the same reasoning: it is shared with whatever
    else the user has set.
    """
    def parse(raw):
        out = {}
        for pair in (raw or "").split(","):
            pair = pair.strip()
            if not pair or "=" not in pair:
                continue
            k, v = pair.split("=", 1)
            out[k.strip()] = v.strip()
        return out

    merged = parse(existing)
    merged.update(parse(wanted))
    return ",".join(f"{k}={v}" for k, v in merged.items())


def _has_jsonc_comments(text: str) -> bool:
    """Whether the file carries comments a parse-and-rewrite would destroy.

    String-aware on purpose: the `//` in `https://` is not a comment, and treating
    it as one would make this refuse to write any settings file containing a URL.
    """
    in_string = escaped = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == "/" and i + 1 < len(text) and text[i + 1] in "/*":
            return True
        i += 1
    return False


def plan_claude_otel(endpoint: str, path: Path | None = None,
                     workspace_kind: str | None = None) -> dict:
    """What would change in ~/.claude/settings.json, without touching it.

    Merges into any existing `env` block rather than replacing it: that block is
    shared with whatever else the user has set there.
    """
    path = path or CLAUDE_SETTINGS
    wanted = claude_otel_env(endpoint, workspace_kind)
    plan = {"ok": False, "path": str(path), "changes": [], "diff": "",
            "new_text": None, "reason": ""}

    if path.exists():
        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            # Distinguished from a plain OSError because the fix is different: a
            # non-UTF-8 settings file is not a permissions problem.
            plan["reason"] = (f"{path} is not valid UTF-8 ({exc}); not touching it. "
                              "Claude Code settings must be UTF-8 JSON.")
            return plan
        except OSError as exc:
            # A permissions problem, a home directory that is not mounted, a dangling
            # symlink. The VS Code path at plan_otel_settings already returns a reason
            # for these; this one raised and aborted the command with a traceback, in a
            # tool whose whole contract is "a missing precondition is a finding to
            # report, never a stack trace".
            plan["reason"] = f"Could not read {path} ({exc}); not touching it."
            return plan
        if _has_jsonc_comments(raw):
            # Refusing rather than eating them. A rewrite would drop every comment
            # silently, and this file holds the user's own preferences.
            plan["reason"] = (f"{path} contains comments, which a rewrite would delete. "
                              "Add the env block by hand, or remove the comments first.")
            return plan
        try:
            current = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            plan["reason"] = f"{path} will not parse ({exc}); not touching it."
            return plan
        if not isinstance(current, dict):
            plan["reason"] = f"{path} is not a JSON object; not touching it."
            return plan
    else:
        raw, current = "", {}
        plan["changes"].append(f"create {path}")

    env = current.get("env")
    if env is not None and not isinstance(env, dict):
        plan["reason"] = f'"env" in {path} is not an object; not touching it.'
        return plan
    env = dict(env or {})
    before = dict(env)          # for the +/~ markers; env is mutated below

    # Refuse at PLAN time, not only at apply. Checking the merged `env` at apply meant
    # a user who already had OTEL_EXPORTER_OTLP_ENDPOINT set -- someone who followed
    # the old `export` advice, which is precisely this command's audience -- got a
    # clean dry run inviting them to --apply, and then a refusal exiting 4 that named
    # a key this tool never wrote. Say it once, up front, about their key.
    theirs = [k for k in CLAUDE_FORBIDDEN_KEYS if k in env]
    if theirs:
        plan["reason"] = (
            f"{path} already sets {', '.join(theirs)}, which routes the LOGS signal --"
            " the one that can carry prompt text. This command configures the metrics"
            " signal only and will not write alongside those. Remove them (they are"
            " yours, not ours) and re-run, or leave telemetry to the managed policy.")
        return plan

    for key, value in wanted.items():
        if key == "OTEL_RESOURCE_ATTRIBUTES":
            value = merge_resource_attributes(env.get(key), value)
        if env.get(key) == value:
            continue
        plan["changes"].append(
            f"{key}: {env[key]!r} -> {value!r}" if key in env else f"{key} = {value!r}")
        env[key] = value

    plan["ok"] = True
    if not plan["changes"]:
        plan["reason"] = "already configured"
        return plan

    updated = dict(current)
    updated["env"] = env
    # ensure_ascii=False so a non-ASCII value the user set stays readable instead of
    # becoming \uXXXX escapes in their own config.
    new_text = json.dumps(updated, indent=2, ensure_ascii=False) + "\n"
    plan["new_text"] = new_text
    plan["reason"] = "changes needed"
    # Scoped to the keys being written, NOT a whole-file diff.
    #
    # A unified diff of the file put the hunk inside `env` with three lines of
    # context, which pulls in neighbouring entries -- ANTHROPIC_AUTH_TOKEN, AWS
    # credentials -- and SKILL.md tells the agent to run this and show the output, so
    # it lands in a transcript and in scrollback. The consent step needs to show what
    # is being written, and nothing else does it any good.
    plan["diff"] = render_env_diff(env, wanted, path, before)
    return plan


def render_env_diff(env: dict, wanted: dict, path: Path,
                    before: dict | None = None) -> str:
    """The proposed `env` entries for our keys only, in JSON shape.

    Deliberately not a file diff: neighbouring `env` entries are frequently secrets,
    and this output is designed to be pasted into a chat.

    `before` is the env as it was *prior* to merging, which is what makes the markers
    mean anything -- comparing against the already-updated dict marked every key as an
    addition, including ones that were being changed.
    """
    before = {} if before is None else before
    lines = [f"  {path} -- proposed \"env\" entries (this command writes only these):", "  {"]
    for key in wanted:
        if key not in before:
            marker = "+"
        elif before[key] != env[key]:
            marker = "~"
        else:
            marker = " "          # already correct; shown for completeness
        lines.append(f"  {marker}   {json.dumps(key)}: {json.dumps(env[key], ensure_ascii=False)}")
    lines.append("  }")
    others = [k for k in env if k not in wanted]
    if others:
        lines.append(f"  ({len(others)} other env entr{'y' if len(others) == 1 else 'ies'} "
                     "left untouched and not shown -- they are frequently credentials)")
    return "\n".join(lines) + "\n"


def apply_claude_otel(plan: dict) -> bool:
    """Write the planned settings, after a timestamped backup.

    The forbidden-key check is a last line of defence against a future caller
    assembling the env block itself: it is what keeps the metrics-only guarantee
    structural rather than merely intended.
    """
    if not plan.get("ok") or plan.get("new_text") is None:
        print(plan.get("reason", "nothing to do"))
        return plan.get("ok", False)

    written = json.loads(plan["new_text"]).get("env", {})
    offenders = [k for k in CLAUDE_FORBIDDEN_KEYS if k in written]
    if offenders:
        print("REFUSING to write: " + ", ".join(offenders) + ". Catalyst configures the "
              "METRICS signal only -- content is only ever a log record, and routing logs "
              "here is what would make prompt text reachable.")
        return False

    path = Path(plan["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_suffix(path.suffix + ".bak." + datetime.now().strftime("%Y%m%d%H%M%S"))
        try:
            shutil.copy2(path, backup)
        except OSError as exc:
            print(f"Could not back up {path} ({exc}); not writing.")
            return False
        print(f"Backed up existing settings to {backup}")

    # Written to a sibling temp file and renamed, not truncated in place. This file
    # belongs to a live Claude Code session -- the skill runs from inside one -- and
    # Claude Code settings are strict JSON, so a crash or a full disk mid-write would
    # leave the session with a file it cannot parse. os.replace is atomic within a
    # filesystem, so the file is either the old one or the new one, never half of each.
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(plan["new_text"], encoding="utf-8")
        os.replace(tmp, path)
    except OSError as exc:
        tmp.unlink(missing_ok=True)
        print(f"Could not write {path} ({exc}). The original is unchanged.")
        return False

    for change in plan["changes"]:
        print(f"  {change}")
    print(f"Updated {path}")
    print("")
    # Unlike the VS Code path, a reload is not a thing here: the OTel SDK reads its
    # environment once at process start, so an existing session keeps exporting
    # nowhere no matter what this file now says.
    print("NOW START A NEW CLAUDE CODE SESSION. The exporter reads its configuration")
    print("  at startup, so this session will not begin reporting on its own.")
    print("  Then confirm with: /dplc-preflight otel --probe-endpoint")
    return True


def cmd_claude_otel(endpoint: str, apply: bool = False) -> int:
    """Show, and on --apply write, Claude Code usage reporting settings."""
    try:
        resolved = normalise_metrics_endpoint(endpoint)
    except EndpointError as exc:
        print(f"Bad --endpoint: {exc}")
        print("  Nothing was written. A typo here configures a destination that")
        print("  accepts nothing and reports no error, so it is refused rather than passed on.")
        return 2
    plan = plan_claude_otel(endpoint)
    print("Claude Code usage reporting")
    print("")
    print(f"  Settings file: {plan['path']}")
    print(f"  Endpoint:      {resolved}")
    print(f"  Status:        {plan['reason']}")

    if not plan["ok"]:
        return 3
    if not plan["changes"]:
        print("")
        print("Nothing to do. If reporting still is not arriving, the likely cause is that")
        print("this session started before the settings existed -- start a new one.")
        return 0

    print("")
    print("  Proposed changes:")
    for change in plan["changes"]:
        print(f"    {change}")
    print("")
    print("  Deliberately NOT set: any logs exporter, any logs endpoint, the generic")
    print("  OTEL_EXPORTER_OTLP_ENDPOINT, or any content switch. Prompt text is only ever")
    print("  a log record, so this configuration cannot send it to Catalyst.")
    print("")
    print(plan["diff"])

    if not apply:
        print("Dry run. Re-run with --apply to write it.")
        return 0
    return 0 if apply_claude_otel(plan) else 4


TESTED_AGAINST_MARKER = "# Tested-against"


def parse_requirements() -> tuple[list[str], list[str]]:
    """Return (core_specs, extra_specs) parsed from requirements.txt."""
    core: list[str] = []
    extras: list[str] = []
    in_extras = False
    for raw in REQUIREMENTS.read_text().splitlines():
        line = raw.strip()
        if line.startswith(TESTED_AGAINST_MARKER):
            in_extras = True
            continue
        if not line or line.startswith("#") or line.startswith("--"):
            continue
        (extras if in_extras else core).append(line)
    return core, extras


def install_deps(python_exe: str) -> bool:
    """Install core deps (gating) and the tested-against extras (best-effort).

    Core deps gate readiness.  A stale pin in the tested-against block (for
    example databricks-cli>=0.218.0, which cannot resolve) must not block a
    working install, so the extras are attempted separately and never fail the
    core setup.
    """
    if not REQUIREMENTS.exists():
        print(f"Cannot find {REQUIREMENTS}")
        return False
    core, extras = parse_requirements()
    base = [python_exe, "-m", "pip", "install", "--index-url", CGREPO_INDEX]

    print(f"Installing {len(core)} core dependencies through cgrepo...")
    rc, out = _run(base + core, timeout=INSTALL_TIMEOUT)
    if rc != 0:
        print(out.strip())
        print("Core dependency install failed.")
        return False
    print("Core dependencies installed.")

    if extras:
        print(f"Installing {len(extras)} tested-against extras (best-effort)...")
        rc2, _ = _run(base + extras, timeout=INSTALL_TIMEOUT)
        if rc2 != 0:
            print("Note: some tested-against extras could not be installed "
                  "(for example a stale databricks-cli pin). They are not "
                  "imported by Catalyst, so core functionality is unaffected.")
        else:
            print("Tested-against extras installed.")
    return True


def cmd_configure() -> int:
    s = gather_state()

    if not s["python_ok"]:
        print("Python 3.10+ is required first, and it is provisioned by "
              "bootstrap.sh (which needs no Python).  Run scripts/bootstrap.sh, "
              "then re-run configure.")
        return 2

    ensure_pip_cgrepo(s["python_exe"])
    if not deps_present(s["python_exe"]):
        install_deps(s["python_exe"])

    return cmd_check()


def cmd_tool(name: str) -> int:
    if name not in ("git", "gh"):
        print(f"Unknown tool '{name}'. Only git and gh are supported.")
        return 1
    if shutil.which(name):
        print(f"{name} is already installed.")
        if name == "gh" and not gh_authenticated():
            print("gh is not authenticated. Run: gh auth login --web")
        return 0
    mgr = detect_package_manager()
    install = TOOL_INSTALL_COMMANDS.get(mgr, lambda _n: None)(name) if mgr else None
    if not install:
        detail = (f"{mgr} is present but this skill has no vetted install command "
                  f"for {name} through it") if mgr else "no package manager detected"
        print(f"Cannot install {name} here ({detail}). Install it through your "
              "Capital Group self-service app or app store.")
        return 3
    print(f"Installing {name} via {mgr}: {' '.join(install)}")
    rc, out = _run(install, timeout=INSTALL_TIMEOUT)
    print(out.strip())
    if name == "gh" and rc == 0:
        print("Next: authenticate with `gh auth login --web`.")
    return rc


def cmd_otel(apply: bool = False, endpoint: str = OTEL_DEFAULT_COLLECTOR) -> int:
    """Show, and on --apply write, the usage-reporting settings.

    Dry-run by default. The diff is the consent step: a user should see exactly
    what is going into their settings file before it goes there.
    """
    plan = plan_otel_settings(endpoint=endpoint)
    print("Copilot Chat usage reporting")
    print("")
    print(f"  Settings file: {plan['path'] or 'not found'}")
    print(f"  Collector:     {endpoint} ({OTEL_COLLECTORS[endpoint]})")
    print(f"  Status:        {plan['reason']}")

    if not plan["ok"]:
        return 3
    if not plan["changes"]:
        print("")
        print("Nothing to do. If reporting still is not arriving, the likely cause is that")
        print("VS Code has not been reloaded since the settings were added.")
        return 0

    print("")
    print("  Proposed changes:")
    for change in plan["changes"]:
        print(f"    {change}")
    print("")
    print(plan["diff"])

    if not apply:
        print("Dry run. Re-run with --apply to write it.")
        return 0
    return 0 if apply_otel_settings(plan) else 4


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Catalyst workspace setup.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Read-only readiness report.")
    sub.add_parser("configure", help="Install Python, pip->cgrepo, and deps on real gaps.")
    t = sub.add_parser("tool", help="Install an optional tool (git or gh).")
    t.add_argument("name", choices=["git", "gh"])
    o = sub.add_parser("otel", help="Turn on Copilot Chat usage reporting (User settings).")
    o.add_argument("--endpoint", choices=sorted(OTEL_COLLECTORS),
                   default=OTEL_DEFAULT_COLLECTOR,
                   help="Which Catalyst collector to report to. Defaults to prd.")
    o.add_argument("--apply", action="store_true",
                   help="Write the change. Without this, only the diff is shown.")
    c = sub.add_parser("claude-otel",
                       help="Turn on Claude Code usage reporting (~/.claude/settings.json).")
    # Required, with no default, on purpose. Production is not routable from an
    # oz-dev Coder workspace, so defaulting to it would configure something that
    # silently drops every batch; defaulting to dev would be wrong on a laptop.
    # The one choice a script cannot make for you is the one it must not guess.
    c.add_argument("--endpoint", required=True,
                   help="'dev', 'prd', or a full URL. /v1/metrics is appended if missing.")
    c.add_argument("--apply", action="store_true",
                   help="Write the change. Without this, only the diff is shown.")
    args = parser.parse_args(argv)

    if args.command == "check":
        return cmd_check()
    if args.command == "configure":
        return cmd_configure()
    if args.command == "tool":
        return cmd_tool(args.name)
    if args.command == "otel":
        return cmd_otel(apply=args.apply, endpoint=args.endpoint)
    if args.command == "claude-otel":
        return cmd_claude_otel(args.endpoint, apply=args.apply)
    return 1


if __name__ == "__main__":
    sys.exit(main())
