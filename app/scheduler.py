from __future__ import annotations

from datetime import timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from app.config import settings
from app.database import get_latest_draw, save_draws
from app.models import RefreshResponse
from app.scraper import get_latest_draws


class ChanceScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone=timezone.utc)
        self.last_draw_changed: bool | None = None

    async def refresh(self) -> RefreshResponse:
        before = get_latest_draw()
        draws = await get_latest_draws()
        if not draws:
            raise RuntimeError("No Chance draws parsed from official sources")
        inserted, updated, duplicates = save_draws(draws)
        latest = get_latest_draw()
        self.last_draw_changed = (
            before is None
            or latest is not None
            and latest.draw_id != before.draw_id
        )
        validation = {
            "cards_count_valid": all(len(draw.cards) == 4 for draw in draws),
            "no_duplicate_draw_ids_in_fetch": len({draw.draw_id for draw in draws}) == len(draws),
            "draw_changed": self.last_draw_changed,
            "parsed_count": len(draws),
        }
        logger.info(
            "Refresh complete inserted={} updated={} duplicates={} latest={}",
            inserted,
            updated,
            duplicates,
            latest.draw_id if latest else None,
        )
        return RefreshResponse(
            success=True,
            inserted=inserted,
            updated=updated,
            duplicate_count=duplicates,
            latest=latest,
            validation=validation,
        )

    async def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.add_job(
                self.refresh,
                "interval",
                seconds=settings.fetch_interval_seconds,
                id="chance-refresh",
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
            self.scheduler.start()
            logger.info("Scheduler started interval={}s", settings.fetch_interval_seconds)

    async def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")


chance_scheduler = ChanceScheduler()
