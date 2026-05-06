#!/usr/bin/env bash
# Idempotent venv bootstrap for founder-portfolio.
# Creates ~/.claude/skills/founder-portfolio/.venv with pinned dependencies
# from requirements.txt. Cross-platform Chrome detection (macOS / Linux).
# Safe to run repeatedly — exits early if venv is healthy AND Python version
# matches the venv's recorded version (prevents subtle 3.12→3.13 breakage).

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$SKILL_DIR/.venv"
REQUIREMENTS="$SKILL_DIR/scripts/requirements.txt"
PYTHON="${PYTHON_BIN:-python3}"

# ─── Chrome detection (cross-platform) ───────────────────────────────
find_chrome() {
  local candidates=(
    "${CHROME_BIN:-}"
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
    "$(command -v google-chrome 2>/dev/null || true)"
    "$(command -v google-chrome-stable 2>/dev/null || true)"
    "$(command -v chromium 2>/dev/null || true)"
    "$(command -v chromium-browser 2>/dev/null || true)"
  )
  for c in "${candidates[@]}"; do
    if [[ -n "$c" && -x "$c" ]]; then
      echo "$c"; return 0
    fi
  done
  return 1
}

if ! CHROME=$(find_chrome); then
  echo "[bootstrap] ERROR: Chrome/Chromium not found." >&2
  echo "[bootstrap] Install Google Chrome (https://www.google.com/chrome/)" >&2
  echo "[bootstrap] or set \$CHROME_BIN, or 'apt install chromium-browser'." >&2
  exit 1
fi
echo "[bootstrap] Chrome: $CHROME"

# ─── venv idempotency with Python-version compatibility check ────────
# A venv created under Python 3.12 can SILENTLY break after a system
# upgrade to 3.13 (C extensions are ABI-incompatible). We compare the
# venv's recorded version against the system python before reusing.
# Additionally, requirements.txt SHA is tracked so dep changes (e.g.,
# adding `openai`) trigger an in-place pip upgrade without full rebuild.
SYS_VER="$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
REQ_SHA="$(shasum -a 256 "$REQUIREMENTS" 2>/dev/null | awk '{print $1}' | head -c 16)"
SHA_FILE="$VENV/.requirements.sha"
IMPORT_PROBE='import jinja2, yaml, PIL, bleach, openai'

if [[ -x "$VENV/bin/python" ]]; then
  VENV_VER="$("$VENV/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "?")"
  STORED_SHA="$([[ -f "$SHA_FILE" ]] && cat "$SHA_FILE" || echo "")"
  if [[ "$VENV_VER" == "$SYS_VER" ]] && \
     [[ "$STORED_SHA" == "$REQ_SHA" ]] && \
     "$VENV/bin/python" -c "$IMPORT_PROBE" 2>/dev/null; then
    echo "[bootstrap] venv ready: $VENV (python $VENV_VER, deps SHA $REQ_SHA)"
    exit 0
  fi
  if [[ "$VENV_VER" == "$SYS_VER" && "$STORED_SHA" != "$REQ_SHA" ]]; then
    echo "[bootstrap] requirements.txt changed (was '$STORED_SHA', now '$REQ_SHA'); in-place upgrade"
    "$VENV/bin/pip" install --quiet -r "$REQUIREMENTS" || true
    echo "$REQ_SHA" > "$SHA_FILE"
    if "$VENV/bin/python" -c "$IMPORT_PROBE" 2>/dev/null; then
      echo "[bootstrap] upgrade done"
      exit 0
    fi
    echo "[bootstrap] upgrade did not satisfy import probe; recreating"
  else
    echo "[bootstrap] venv exists but stale (venv=$VENV_VER, system=$SYS_VER, or missing deps); recreating"
  fi
  rm -rf "$VENV"
fi

if [[ ! -f "$REQUIREMENTS" ]]; then
  echo "[bootstrap] ERROR: requirements.txt not found at $REQUIREMENTS" >&2
  exit 1
fi

echo "[bootstrap] creating venv at $VENV (python $SYS_VER)"
"$PYTHON" -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip --quiet
"$VENV/bin/pip" install --quiet -r "$REQUIREMENTS"
echo "$REQ_SHA" > "$SHA_FILE"
echo "[bootstrap] done — installed: $(grep -v '^#' "$REQUIREMENTS" | grep -v '^$' | tr '\n' ' ')"
