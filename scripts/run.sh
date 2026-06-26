#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

if [ -d ".venv" ]; then
  . .venv/bin/activate
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

exec uvicorn app.main:app --host "$HOST" --port "$PORT"
