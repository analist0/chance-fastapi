from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.database import get_history, get_latest_draw, get_stats
from app.models import DrawResponse, RefreshResponse, StatsResponse
from app.scheduler import chance_scheduler


router = APIRouter()


@router.get("/")
async def root() -> dict[str, object]:
    return {
        "service": "chance-fastapi",
        "status": "ok",
        "source": "Official Mifal Hapais Chance CSV with AJAX/HTML fallback",
        "endpoints": ["/health", "/latest", "/history", "/refresh", "/stats"],
    }


@router.get("/health")
async def health() -> dict[str, object]:
    latest = get_latest_draw()
    return {"status": "ok", "has_latest": latest is not None}


@router.get("/latest", response_model=DrawResponse)
async def latest() -> DrawResponse:
    draw = get_latest_draw()
    if draw is None:
        raise HTTPException(status_code=404, detail="No draw available. Run POST /refresh first.")
    return draw


@router.get("/history", response_model=list[DrawResponse])
async def history(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[DrawResponse]:
    return get_history(limit=limit, offset=offset)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh() -> RefreshResponse:
    try:
        return await chance_scheduler.refresh()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/stats", response_model=StatsResponse)
async def stats() -> StatsResponse:
    return get_stats(draw_changed=chance_scheduler.last_draw_changed)
