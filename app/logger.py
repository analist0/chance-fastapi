from __future__ import annotations

import sys

from loguru import logger

from app.config import settings


def configure_logging() -> None:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )
    logger.add(
        settings.log_dir / "chance-fastapi.log",
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )


configure_logging()
