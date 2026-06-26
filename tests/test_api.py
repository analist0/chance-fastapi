from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient

from app.database import init_db, save_draws
from app.main import app
from app.models import ChanceDraw, Card


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_latest_endpoint_returns_saved_draw() -> None:
    init_db()
    draw = ChanceDraw(
        draw_id=999001,
        date="2026-06-25",
        time="21:00",
        cards=[
            Card(suit="clubs", suit_he="תלתן", rank="A"),
            Card(suit="diamonds", suit_he="יהלום", rank="J"),
            Card(suit="hearts", suit_he="לב", rank="K"),
            Card(suit="spades", suit_he="עלה", rank="A"),
        ],
        raw_response="test",
        source="test",
        fetched_at=datetime(2026, 6, 26, 8, 0, 0),
    )
    save_draws([draw])
    with TestClient(app) as client:
        response = client.get("/latest")
    assert response.status_code == 200
    body = response.json()
    assert body["draw_id"] == 999001
    assert len(body["cards"]) == 4
