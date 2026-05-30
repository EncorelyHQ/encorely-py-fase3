from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    django_api_base_url: str
    django_username: str
    django_password: str
    request_timeout: int


settings = Settings(
    django_api_base_url=os.getenv("DJANGO_API_BASE_URL", "http://localhost:8000/api").rstrip("/") + "/",
    django_username=os.getenv("DJANGO_USERNAME", "demo"),
    django_password=os.getenv("DJANGO_PASSWORD", "changeme"),
    request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
)
