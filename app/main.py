from __future__ import annotations

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request
from loguru import logger

import app.logger  # noqa: F401
from app.api import router
from app.config import settings
from app.database import init_db
from app.scheduler import chance_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await chance_scheduler.start()
    if not os.getenv("PYTEST_CURRENT_TEST") and os.getenv("SKIP_INITIAL_FETCH") != "1":
        try:
            await chance_scheduler.refresh()
        except Exception as exc:
            logger.warning("Initial Chance fetch failed: {}", repr(exc))
    yield
    await chance_scheduler.shutdown()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("{} {}", request.method, request.url.path)
    response = await call_next(request)
    logger.info("{} {} -> {}", request.method, request.url.path, response.status_code)
    return response


app.include_router(router)
