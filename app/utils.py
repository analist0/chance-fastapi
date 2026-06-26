from __future__ import annotations

import re
from datetime import date, datetime, timezone


HEBREW_SUIT_MAP = {
    "תלתן": "clubs",
    "יהלום": "diamonds",
    "לב": "hearts",
    "עלה": "spades",
}

SUIT_HEBREW = {
    "clubs": "תלתן",
    "diamonds": "יהלום",
    "hearts": "לב",
    "spades": "עלה",
}

IMAGE_SUIT_MAP = {
    "clubs": "clubs",
    "diamond": "diamonds",
    "diamonds": "diamonds",
    "hearth": "hearts",
    "heart": "hearts",
    "hearts": "hearts",
    "peak": "spades",
    "spade": "spades",
    "spades": "spades",
}

SUIT_ORDER = ["clubs", "diamonds", "hearts", "spades"]
VALID_RANKS = {"7", "8", "9", "10", "J", "Q", "K", "A"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_rank(value: str | int | None) -> str:
    rank = clean_text(str(value or "")).upper()
    aliases = {"ACE": "A", "KING": "K", "QUEEN": "Q", "JACK": "J"}
    return aliases.get(rank, rank)


def normalize_date(value: str | None) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d.%m.%Y", "%d.%m.%y", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(text, fmt).date()
            return parsed.isoformat()
        except ValueError:
            continue
    return None


def normalize_time(value: str | None) -> str | None:
    text = clean_text(value)
    match = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text)
    if not match:
        return None
    return f"{int(match.group(1)):02d}:{match.group(2)}"


def card_dict(suit: str, rank: str) -> dict[str, str]:
    normalized_suit = IMAGE_SUIT_MAP.get(suit, suit)
    normalized_rank = normalize_rank(rank)
    return {
        "suit": normalized_suit,
        "suit_he": SUIT_HEBREW.get(normalized_suit, normalized_suit),
        "rank": normalized_rank,
    }


def infer_draw_time(draw_date: str, draw_id: int) -> str | None:
    try:
        parsed = date.fromisoformat(draw_date)
    except ValueError:
        return None
    weekday = parsed.weekday()
    if weekday == 5:
        return None
    if weekday == 4:
        slots = ["11:00", "13:00", "15:00", "17:00", "19:00", "21:00"]
    else:
        slots = ["09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"]
    return slots[(draw_id - 1) % len(slots)]
