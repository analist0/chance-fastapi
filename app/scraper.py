from __future__ import annotations

import asyncio
import json

import httpx
from loguru import logger

from app.config import settings
from app.models import ChanceDraw
from app.parser import (
    ParseError,
    merge_draw_lists,
    parse_csv_response,
    parse_html_response,
    parse_json_response,
    validate_draw,
)
from app.utils import utcnow


class ScraperBlockedError(RuntimeError):
    pass


class ChanceScraper:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml,text/csv,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": settings.chance_page_url,
        }

    async def fetch_latest(self) -> list[ChanceDraw]:
        fetched_at = utcnow()
        csv_text = await self._get_text(settings.chance_csv_url)
        primary = self._parse_response(csv_text, fetched_at, "csv")
        ajax_draws: list[ChanceDraw] = []
        try:
            ajax_url = f"{settings.chance_ajax_url}?fromIndex=0&amount=12"
            ajax_text = await self._get_text(ajax_url)
            ajax_draws = parse_html_response(ajax_text, fetched_at, source="official_ajax_html")
        except Exception as exc:
            logger.warning("AJAX enrichment failed: {}", repr(exc))
        draws = merge_draw_lists(primary, ajax_draws)
        if not draws:
            logger.warning("CSV/AJAX parsing yielded no draws, trying Chance page fallback")
            page_text = await self._get_text(settings.chance_page_url)
            draws = parse_html_response(page_text, fetched_at, source="official_page_html")
        for draw in draws:
            validate_draw(draw)
        return draws

    async def _get_text(self, url: str) -> str:
        last_error: Exception | None = None
        for attempt in range(1, settings.request_retries + 1):
            try:
                async with httpx.AsyncClient(
                    headers=self.headers,
                    timeout=settings.request_timeout_seconds,
                    follow_redirects=True,
                ) as client:
                    logger.info("HTTP GET {} attempt {}", url, attempt)
                    response = await client.get(url)
                    logger.info(
                        "HTTP {} {} bytes={} content_type={}",
                        response.status_code,
                        url,
                        len(response.content),
                        response.headers.get("content-type"),
                    )
                    self._detect_blocking(response)
                    response.raise_for_status()
                    return response.text
            except (httpx.HTTPError, ScraperBlockedError) as exc:
                last_error = exc
                logger.warning("Request failed: {} attempt={} error={}", url, attempt, repr(exc))
                if attempt < settings.request_retries:
                    await asyncio.sleep(min(2**attempt, 8))
        raise RuntimeError(f"failed to fetch {url}: {last_error!r}")

    def _detect_blocking(self, response: httpx.Response) -> None:
        body_prefix = response.text[:1000].lower()
        block_markers = ("captcha", "access denied", "forbidden", "cloudflare", "blocked")
        if response.status_code in {401, 403, 429} or any(marker in body_prefix for marker in block_markers):
            raise ScraperBlockedError(f"possible blocking status={response.status_code}")

    def _parse_response(self, text: str, fetched_at, preferred: str) -> list[ChanceDraw]:
        if preferred == "csv":
            draws = parse_csv_response(text, fetched_at)
            if draws:
                return draws
        stripped = text.lstrip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                return parse_json_response(text, fetched_at)
            except (json.JSONDecodeError, ParseError, ValueError) as exc:
                logger.warning("JSON parser failed: {}", repr(exc))
        return parse_html_response(text, fetched_at)


async def get_latest_draws() -> list[ChanceDraw]:
    return await ChanceScraper().fetch_latest()
