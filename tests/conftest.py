from __future__ import annotations

import os
from pathlib import Path


TEST_DB = Path(__file__).resolve().parent.parent / ".pytest_chance.db"

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["SKIP_INITIAL_FETCH"] = "1"
