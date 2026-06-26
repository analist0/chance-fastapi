from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup
from loguru import logger

from app.models import ChanceDraw
from app.utils import (
    HEBREW_SUIT_MAP,
    IMAGE_SUIT_MAP,
    SUIT_ORDER,
    VALID_RANKS,
    card_dict,
    clean_text,
    infer_draw_time,
    normalize_date,
    normalize_rank,
    normalize_time,
)


DRAW_RE = re.compile(r"(?:הגרל[הת]|draw|number|מס(?:פר)?)[^\d]{0,20}(\d{4,8})", re.I)
LOOSE_DRAW_RE = re.compile(r"\b(\d{4,8})\b")
DATE_RE = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b")
TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b")


class ParseError(RuntimeError):
    pass


def parse_csv_response(text: str, fetched_at: datetime) -> list[ChanceDraw]:
    decoded = _repair_csv_encoding(text)
    rows = list(csv.reader(io.StringIO(decoded)))
    draws: list[ChanceDraw] = []
    for row in rows:
        if len(row) < 6:
            continue
        draw_date = normalize_date(row[0])
        if not draw_date or not clean_text(row[1]).isdigit():
            continue
        draw_id = int(clean_text(row[1]))
        ranks = [normalize_rank(value) for value in row[2:6]]
        if any(rank not in VALID_RANKS for rank in ranks):
            continue
        cards = [card_dict(suit, rank) for suit, rank in zip(SUIT_ORDER, ranks, strict=True)]
        draws.append(
            ChanceDraw(
                draw_id=draw_id,
                date=draw_date,
                time=None,
                cards=cards,
                raw_response=",".join(row),
                source="official_csv",
                fetched_at=fetched_at,
            )
        )
    logger.info("Parsed {} Chance draws from CSV", len(draws))
    return sorted(draws, key=lambda item: item.draw_id, reverse=True)


def parse_json_response(text: str, fetched_at: datetime) -> list[ChanceDraw]:
    data = json.loads(text)
    items = data if isinstance(data, list) else [data]
    draws: list[ChanceDraw] = []
    for item in items:
        if isinstance(item, dict):
            parsed = _draw_from_mapping(item, fetched_at)
            if parsed:
                draws.append(parsed)
    logger.info("Parsed {} Chance draws from JSON", len(draws))
    return sorted(draws, key=lambda item: item.draw_id, reverse=True)


def parse_html_response(html: str, fetched_at: datetime, source: str = "official_html") -> list[ChanceDraw]:
    soup = BeautifulSoup(html, "lxml")
    draws = _parse_archive_items(soup, html, fetched_at, source)
    if draws:
        logger.info("Parsed {} Chance draws from archive-style HTML", len(draws))
        return sorted(draws, key=lambda item: item.draw_id, reverse=True)

    for script in soup.find_all("script"):
        for blob in _extract_json_blobs(script.string or ""):
            try:
                draws.extend(parse_json_response(blob, fetched_at))
            except (json.JSONDecodeError, ParseError, ValueError):
                continue
    if draws:
        return sorted(_dedupe(draws), key=lambda item: item.draw_id, reverse=True)

    text_candidates = _candidate_text_blocks(soup)
    for text in text_candidates:
        parsed = _draw_from_text(text, fetched_at, html, source)
        if parsed:
            draws.append(parsed)
    logger.info("Parsed {} Chance draws from generic HTML", len(draws))
    return sorted(_dedupe(draws), key=lambda item: item.draw_id, reverse=True)


def merge_draw_lists(primary: list[ChanceDraw], enrichment: list[ChanceDraw]) -> list[ChanceDraw]:
    by_id = {draw.draw_id: draw for draw in primary}
    for extra in enrichment:
        current = by_id.get(extra.draw_id)
        if current is None:
            by_id[extra.draw_id] = extra
            continue
        if extra.time and current.time != extra.time:
            current.time = extra.time
        if extra.raw_response and len(extra.raw_response) > len(current.raw_response):
            current.raw_response = extra.raw_response
            current.source = f"{current.source}+{extra.source}"
    return sorted(by_id.values(), key=lambda item: item.draw_id, reverse=True)


def validate_draw(draw: ChanceDraw) -> None:
    if len(draw.cards) != 4:
        raise ParseError(f"draw {draw.draw_id} has {len(draw.cards)} cards")
    ranks = [card.rank for card in draw.cards]
    if any(rank not in VALID_RANKS for rank in ranks):
        raise ParseError(f"draw {draw.draw_id} has invalid ranks: {ranks}")
    suits = [card.suit for card in draw.cards]
    if suits != SUIT_ORDER:
        raise ParseError(f"draw {draw.draw_id} has invalid suit order: {suits}")


def _repair_csv_encoding(text: str) -> str:
    if "����" not in text:
        return text
    try:
        return text.encode("latin-1", errors="ignore").decode("cp1255", errors="ignore")
    except UnicodeError:
        return text


def _parse_archive_items(
    soup: BeautifulSoup,
    raw_response: str,
    fetched_at: datetime,
    source: str,
) -> list[ChanceDraw]:
    draws: list[ChanceDraw] = []
    for item in soup.find_all(["li", "div"]):
        classes = set(item.get("class") or [])
        if "archive_list_item" not in classes and not item.find(class_=re.compile("chance_number")):
            continue
        text = clean_text(item.get_text(" "))
        draw_id = _extract_draw_id(text)
        draw_date = _first_match(DATE_RE, text)
        cards = []
        card_container = item.find(class_=re.compile(r"\bcard\b"))
        if card_container:
            for card_tag in card_container.find_all(class_=re.compile(r"cat_data_info")):
                image = card_tag.find("img")
                suit = _suit_from_image(image.get("src", "") if image else "")
                if not suit and image:
                    suit = HEBREW_SUIT_MAP.get(clean_text(image.get("alt")))
                rank = normalize_rank(card_tag.find_all("div")[-1].get_text(" ") if card_tag.find_all("div") else "")
                if suit and rank in VALID_RANKS:
                    cards.append(card_dict(suit, rank))
        if draw_id and draw_date and len(cards) == 4:
            normalized_date = normalize_date(draw_date)
            if normalized_date:
                draw = ChanceDraw(
                    draw_id=draw_id,
                    date=normalized_date,
                    time=normalize_time(text),
                    cards=cards,
                    raw_response=str(item)[:20000] or raw_response[:20000],
                    source=source,
                    fetched_at=fetched_at,
                )
                validate_draw(draw)
                draws.append(draw)
    return _dedupe(draws)


def _draw_from_mapping(item: dict[str, Any], fetched_at: datetime) -> ChanceDraw | None:
    lower = {str(key).lower(): value for key, value in item.items()}
    draw_id_value = (
        lower.get("draw_id")
        or lower.get("drawid")
        or lower.get("id")
        or lower.get("num")
        or lower.get("number")
        or lower.get("lotteryid")
    )
    date_value = lower.get("date") or lower.get("drawdate") or lower.get("lotterydate")
    if draw_id_value is None or date_value is None:
        return None
    draw_date = normalize_date(str(date_value))
    if not draw_date:
        return None
    cards = _cards_from_mapping(lower)
    if len(cards) != 4:
        return None
    draw = ChanceDraw(
        draw_id=int(draw_id_value),
        date=draw_date,
        time=normalize_time(str(lower.get("time") or lower.get("drawtime") or "")),
        cards=cards,
        raw_response=json.dumps(item, ensure_ascii=False),
        source="official_json",
        fetched_at=fetched_at,
    )
    validate_draw(draw)
    return draw


def _cards_from_mapping(item: dict[str, Any]) -> list[dict[str, str]]:
    for key in ("cards", "winningcards", "results", "numbers"):
        value = item.get(key)
        if isinstance(value, list) and len(value) >= 4:
            cards = []
            for index, raw_card in enumerate(value[:4]):
                suit = SUIT_ORDER[index]
                rank = ""
                if isinstance(raw_card, dict):
                    suit = str(raw_card.get("suit") or raw_card.get("location") or suit)
                    rank = str(raw_card.get("rank") or raw_card.get("number") or raw_card.get("value") or "")
                else:
                    rank = str(raw_card)
                cards.append(card_dict(suit, normalize_rank(rank)))
            return cards
    ranks = []
    for key in ("clubs", "diamond", "diamonds", "heart", "hearts", "spade", "spades", "peak"):
        if key in item:
            ranks.append((IMAGE_SUIT_MAP.get(key, key), normalize_rank(str(item[key]))))
    if len(ranks) >= 4:
        by_suit = {suit: rank for suit, rank in ranks}
        return [card_dict(suit, by_suit[suit]) for suit in SUIT_ORDER if suit in by_suit]
    return []


def _draw_from_text(text: str, fetched_at: datetime, raw_response: str, source: str) -> ChanceDraw | None:
    draw_id = _extract_draw_id(text)
    draw_date = _first_match(DATE_RE, text)
    if not draw_id or not draw_date:
        return None
    normalized_date = normalize_date(draw_date)
    if not normalized_date:
        return None
    cards = []
    for suit in SUIT_ORDER:
        suit_he = next(key for key, value in HEBREW_SUIT_MAP.items() if value == suit)
        pattern = re.compile(rf"(?:{suit}|{suit_he})\D{{0,20}}(A|K|Q|J|10|[7-9])", re.I)
        match = pattern.search(text)
        if match:
            cards.append(card_dict(suit, match.group(1)))
    if len(cards) != 4:
        ranks = re.findall(r"\b(?:A|K|Q|J|10|[7-9])\b", text, flags=re.I)
        cards = [card_dict(suit, rank) for suit, rank in zip(SUIT_ORDER, ranks[:4])]
    if len(cards) != 4:
        return None
    draw = ChanceDraw(
        draw_id=draw_id,
        date=normalized_date,
        time=normalize_time(text) or infer_draw_time(normalized_date, draw_id),
        cards=cards,
        raw_response=raw_response[:20000],
        source=source,
        fetched_at=fetched_at,
    )
    validate_draw(draw)
    return draw


def _candidate_text_blocks(soup: BeautifulSoup) -> list[str]:
    candidates = []
    for tag in soup.find_all(["table", "tr", "li", "section", "article", "div"]):
        text = clean_text(tag.get_text(" "))
        if 20 <= len(text) <= 2000 and (
            "צ'אנס" in text or "Chance" in text or DATE_RE.search(text)
        ):
            candidates.append(text)
    return candidates


def _extract_json_blobs(text: str) -> list[str]:
    return [match.group(0) for match in re.finditer(r"(\{.*?\}|\[.*?\])", text, flags=re.S)]


def _extract_draw_id(text: str) -> int | None:
    match = DRAW_RE.search(text) or LOOSE_DRAW_RE.search(text)
    return int(match.group(1)) if match else None


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(0) if match else None


def _suit_from_image(src: str) -> str | None:
    src = src.lower()
    for key, suit in IMAGE_SUIT_MAP.items():
        if key in src:
            return suit
    return None


def _dedupe(draws: list[ChanceDraw]) -> list[ChanceDraw]:
    by_id: dict[int, ChanceDraw] = {}
    for draw in draws:
        by_id[draw.draw_id] = draw
    return list(by_id.values())
