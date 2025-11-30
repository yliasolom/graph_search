#!/usr/bin/env bash
set -euo pipefail

# Kill any FastAPI/Uvicorn processes bound to the given port (default 8000).
# Usage:
#   ./scripts/kill_fastapi.sh           # kills whatever listens on 8000
#   PORT=8010 ./scripts/kill_fastapi.sh # kills whatever listens on 8010

PORT="${PORT:-8000}"

if ! command -v lsof >/dev/null 2>&1; then
  echo "lsof is required but not installed."
  exit 1
fi

PIDS="$(lsof -ti tcp:$PORT || true)"

if [[ -z "${PIDS}" ]]; then
  echo "No processes found on port ${PORT}."
  exit 0
fi

echo "Killing processes on port ${PORT}: ${PIDS}"
kill ${PIDS} 2>/dev/null || true
sleep 1

LEFTOVER="$(lsof -ti tcp:$PORT || true)"
if [[ -n "${LEFTOVER}" ]]; then
  echo "Force killing remaining processes: ${LEFTOVER}"
  kill -9 ${LEFTOVER} 2>/dev/null || true
else
  echo "Port ${PORT} is now free."
fi









