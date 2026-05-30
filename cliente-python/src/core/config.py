from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Carga variables de .env ubicado en la raiz del subproyecto cliente-python.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    django_api_base_url: str
    fastapi_base_url: str
    request_timeout: int


settings = Settings(
    django_api_base_url=os.getenv("DJANGO_API_BASE_URL", "http://localhost:8000"),
    fastapi_base_url=os.getenv("FASTAPI_BASE_URL", "http://localhost:8001"),
    request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
)
