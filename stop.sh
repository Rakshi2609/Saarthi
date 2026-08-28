#!/usr/bin/env bash
# Saarthi — one-command local stop.
set -euo pipefail
cd "$(dirname "$0")"

API_PID_FILE="/tmp/saarthi_api.pid"
WEB_PID_FILE="/tmp/saarthi_web.pid"

stop_pid() {
  local f="$1"
  local name="$2"
  if [ -f "$f" ] && kill -0 "$(cat "$f")" 2>/dev/null; then
    kill "$(cat "$f")" && echo "[stop.sh] stopped $name (pid $(cat "$f"))"
    rm -f "$f"
  else
    echo "[stop.sh] $name not running"
    rm -f "$f"
  fi
}

stop_pid "$API_PID_FILE" "API"
stop_pid "$WEB_PID_FILE" "frontend"
