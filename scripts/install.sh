#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

python -m venv .venv
. .venv/bin/activate

if command -v pkg >/dev/null 2>&1; then
  pkg install -y libxml2 libxslt clang
fi

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

pytest -q

python - <<'PY'
import asyncio
from app.database import init_db, get_latest_draw
from app.scheduler import chance_scheduler

async def main() -> None:
    init_db()
    result = await chance_scheduler.refresh()
    latest = get_latest_draw()
    if not result.success or latest is None:
        raise SystemExit("FAILURE: first fetch did not store a latest draw")
    print("SUCCESS")
    print(latest.model_dump_json(indent=2))

asyncio.run(main())
PY

exec uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
