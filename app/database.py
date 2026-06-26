from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Base, ChanceDraw, DrawRecord, DrawResponse, StatsResponse
from app.utils import utcnow


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def save_draws(draws: list[ChanceDraw]) -> tuple[int, int, int]:
    inserted = 0
    updated = 0
    duplicate_count = 0
    now = utcnow()
    with SessionLocal() as session:
        for draw in draws:
            existing = session.scalar(select(DrawRecord).where(DrawRecord.draw_id == draw.draw_id))
            cards_json = json.dumps([card.model_dump() for card in draw.cards], ensure_ascii=False)
            if existing is None:
                session.add(
                    DrawRecord(
                        draw_id=draw.draw_id,
                        draw_date=draw.date,
                        draw_time=draw.time,
                        cards_json=cards_json,
                        raw_response=draw.raw_response,
                        source=draw.source,
                        fetched_at=draw.fetched_at,
                        created_at=now,
                        updated_at=now,
                    )
                )
                inserted += 1
                continue
            duplicate_count += 1
            changed = (
                existing.draw_date != draw.date
                or existing.draw_time != draw.time
                or existing.cards_json != cards_json
                or existing.source != draw.source
            )
            if changed:
                existing.draw_date = draw.date
                existing.draw_time = draw.time
                existing.cards_json = cards_json
                existing.raw_response = draw.raw_response
                existing.source = draw.source
                existing.fetched_at = draw.fetched_at
                existing.updated_at = now
                updated += 1
        session.commit()
    return inserted, updated, duplicate_count


def get_latest_draw() -> DrawResponse | None:
    with SessionLocal() as session:
        record = session.scalar(select(DrawRecord).order_by(DrawRecord.draw_id.desc()).limit(1))
        return _to_response(record) if record else None


def get_history(limit: int = 50, offset: int = 0) -> list[DrawResponse]:
    limit = max(1, min(limit, 500))
    offset = max(0, offset)
    with SessionLocal() as session:
        records = session.scalars(
            select(DrawRecord).order_by(DrawRecord.draw_id.desc()).offset(offset).limit(limit)
        ).all()
        return [_to_response(record) for record in records]


def get_stats(draw_changed: bool | None = None) -> StatsResponse:
    with SessionLocal() as session:
        total = session.scalar(select(func.count()).select_from(DrawRecord)) or 0
        latest_id = session.scalar(select(func.max(DrawRecord.draw_id)))
        oldest_id = session.scalar(select(func.min(DrawRecord.draw_id)))
        last_fetch = session.scalar(select(func.max(DrawRecord.fetched_at)))
    return StatsResponse(
        total_draws=total,
        latest_draw_id=latest_id,
        oldest_draw_id=oldest_id,
        last_fetch_at=last_fetch,
        draw_changed=draw_changed,
    )


def _to_response(record: DrawRecord) -> DrawResponse:
    return DrawResponse(
        draw_id=record.draw_id,
        date=record.draw_date,
        time=record.draw_time,
        cards=json.loads(record.cards_json),
        game_type=record.game_type,
        source=record.source,
        fetched_at=_ensure_datetime(record.fetched_at),
    )


def _ensure_datetime(value: datetime) -> datetime:
    return value
