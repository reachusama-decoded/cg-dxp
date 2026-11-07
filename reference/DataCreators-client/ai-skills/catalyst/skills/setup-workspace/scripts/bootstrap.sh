#!/bin/sh
# bootstrap.sh — ensure Python 3.10+ is available for AI Catalyst, using no
# Python itself.  This is the piece that must work on a machine that has no
# Python yet, so it is plain POSIX shell.  It detects the interpreter and
# version, installs Python 3.13 via Homebrew or uv when one is present, or guides
# the user to the Capital Group self-service app / app store.  It never installs
# a package manager and never runs sudo.
#
# Once this exits 0, run scripts/setup_workspace.py for the pip and dependency
# steps (those genuinely need Python).
#
# Exit codes:
#   0  Python 3.10+ is present and ready
#   3  Python missing/old and could not be provisioned here (no installer, or the
#      install did not produce a usable Python); guidance printed

MIN_MAJOR=3
MIN_MINOR=10
RECOMMENDED=3.13

# Print "MAJOR MINOR" for the first usable interpreter, or nothing.
find_python() {
  for exe in python3 python; do
    if command -v "$exe" >/dev/null 2>&1; then
      "$exe" -c 'import sys; print("%d %d" % sys.version_info[:2])' 2>/dev/null && return 0
    fi
  done
  return 1
}

version_ok() {  # args: MAJOR MINOR
  [ "$1" -gt "$MIN_MAJOR" ] && return 0
  [ "$1" -eq "$MIN_MAJOR" ] && [ "$2" -ge "$MIN_MINOR" ] && return 0
  return 1
}

detect_os() {
  case "$(uname -s 2>/dev/null)" in
    Darwin) echo darwin ;;
    Linux)  echo linux ;;
    *)      echo other ;;
  esac
}

# Returns 0 and prints a message if Python 3.10+ is present.
report_python() {
  ver=$(find_python)
  if [ -n "$ver" ]; then
    maj=${ver% *}
    min=${ver#* }
    if version_ok "$maj" "$min"; then
      echo "Python ${maj}.${min} is present (>= ${MIN_MAJOR}.${MIN_MINOR})."
      return 0
    fi
    echo "Python ${maj}.${min} is present but older than ${MIN_MAJOR}.${MIN_MINOR}."
    return 1
  fi
  echo "Python is not installed."
  return 1
}

guide_and_exit() {
  os=$(detect_os)
  echo ""
  echo "Cannot install Python here without a package manager or elevated rights."
  case "$os" in
    darwin)
      echo "Open the Capital Group self-service app and install Homebrew (or Python ${RECOMMENDED} directly), then re-run this script." ;;
    *)
      echo "Install Python ${RECOMMENDED} through your Capital Group sanctioned channel (IT self-service or software portal), then re-run this script." ;;
  esac
  exit 3
}

# 1) Already good?
if report_python; then
  exit 0
fi

# 2) Try the non-sudo installers, best-effort: Homebrew, then uv.  Any failure
# (missing installer, a download blocked on the corporate network, or a Python
# that does not land on PATH) falls through to the guidance step below.
if command -v brew >/dev/null 2>&1; then
  echo "Installing Python ${RECOMMENDED} via Homebrew..."
  brew install "python@${RECOMMENDED}"
  if report_python; then exit 0; fi
  echo "Homebrew did not yield a usable Python; trying other options."
fi
if command -v uv >/dev/null 2>&1; then
  echo "Installing Python ${RECOMMENDED} via uv..."
  uv python install --default "${RECOMMENDED}"
  if report_python; then exit 0; fi
  echo "uv did not yield a usable Python on PATH; falling back to guidance."
fi

# 3) Nothing produced a usable Python -> guide.  (apt/dnf need sudo; Windows
# uses bootstrap.ps1, not this script.)
guide_and_exit
