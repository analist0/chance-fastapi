from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    app_name: str = os.getenv("APP_NAME", "chance-fastapi")
    environment: str = os.getenv("ENVIRONMENT", "production")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'chance.db'}",
    )
    log_dir: Path = Path(os.getenv("LOG_DIR", str(BASE_DIR / "logs")))
    fetch_interval_seconds: int = int(os.getenv("FETCH_INTERVAL_SECONDS", "30"))
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    request_retries: int = int(os.getenv("REQUEST_RETRIES", "3"))
    pais_base_url: str = os.getenv("PAIS_BASE_URL", "https://www.pais.co.il")
    chance_page_url: str = os.getenv("CHANCE_PAGE_URL", f"{pais_base_url}/chance/")
    chance_csv_url: str = os.getenv(
        "CHANCE_CSV_URL",
        f"{pais_base_url}/chance/chance_resultsDownload.aspx",
    )
    chance_ajax_url: str = os.getenv(
        "CHANCE_AJAX_URL",
        f"{pais_base_url}/chance/showMoreResults.aspx",
    )
    user_agent: str = os.getenv(
        "USER_AGENT",
        (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        ),
    )


settings = Settings()
