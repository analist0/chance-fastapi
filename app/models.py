from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DrawRecord(Base):
    __tablename__ = "chance_draws"
    __table_args__ = (UniqueConstraint("draw_id", name="uq_chance_draw_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    draw_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    draw_date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    draw_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    game_type: Mapped[str] = mapped_column(String(32), nullable=False, default="Chance")
    cards_json: Mapped[str] = mapped_column(Text, nullable=False)
    raw_response: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Card(BaseModel):
    suit: str
    suit_he: str
    rank: str


class ChanceDraw(BaseModel):
    draw_id: int
    date: str
    time: str | None = None
    cards: list[Card] = Field(min_length=4, max_length=4)
    game_type: str = "Chance"
    raw_response: str
    source: str
    fetched_at: datetime


class DrawResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    draw_id: int
    date: str
    time: str | None
    cards: list[Card]
    game_type: str
    source: str
    fetched_at: datetime


class RefreshResponse(BaseModel):
    success: bool
    inserted: int
    updated: int
    duplicate_count: int
    latest: DrawResponse | None
    validation: dict[str, Any]


class StatsResponse(BaseModel):
    total_draws: int
    latest_draw_id: int | None
    oldest_draw_id: int | None
    last_fetch_at: datetime | None
    draw_changed: bool | None
