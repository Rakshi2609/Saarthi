#!/usr/bin/env bash
# Saarthi — one-command local start.
# Creates venv if missing, installs deps, starts FastAPI on :8000 and the
# static frontend on :5173 in the background. Logs go to logs/.
# Idempotent: if both are already running, it just prints the URLs.

set -euo pipefail
cd "$(dirname "$0")"

PY="${PY:-python3}"
VENV=".venv"
PIP="$VENV/bin/pip"
PYBIN="$VENV/bin/python"
API_PID_FILE="/tmp/saarthi_api.pid"
WEB_PID_FILE="/tmp/saarthi_web.pid"
API_LOG="logs/api.log"
WEB_LOG="logs/web.log"

mkdir -p logs

# ---------- venv ----------
if [ ! -x "$PYBIN" ]; then
  echo "[start.sh] creating venv at $VENV ..."
  $PY -m venv "$VENV"
fi

# ---------- deps ----------
echo "[start.sh] ensuring dependencies ..."
"$PIP" install --quiet --upgrade pip
"$PIP" install --quiet -r requirements.txt

# ---------- API ----------
if [ -f "$API_PID_FILE" ] && kill -0 "$(cat "$API_PID_FILE")" 2>/dev/null; then
  echo "[start.sh] API already running (pid $(cat "$API_PID_FILE"))"
else
  echo "[start.sh] starting FastAPI on :8000 ..."
  nohup "$PYBIN" -m uvicorn api.main:app --host 0.0.0.0 --port 8000 \
    > "$API_LOG" 2>&1 &
  echo $! > "$API_PID_FILE"
fi

# ---------- frontend ----------
if [ -f "$WEB_PID_FILE" ] && kill -0 "$(cat "$WEB_PID_FILE")" 2>/dev/null; then
  echo "[start.sh] frontend already running (pid $(cat "$WEB_PID_FILE"))"
else
  echo "[start.sh] starting frontend on :5173 ..."
  nohup "$PYBIN" -m http.server 5173 --directory frontend \
    > "$WEB_LOG" 2>&1 &
  echo $! > "$WEB_PID_FILE"
fi

# ---------- ready ----------
sleep 2
echo ""
echo "================================================================"
echo "  Saarthi demo is up"
echo "  Frontend  ->  http://localhost:5173"
echo "  API       ->  http://localhost:8000"
echo "  Swagger   ->  http://localhost:8000/docs"
echo "  Logs:"
echo "    API       : $API_LOG"
echo "    Frontend  : $WEB_LOG"
echo "  Stop with:  $0 stop"
echo "================================================================"
