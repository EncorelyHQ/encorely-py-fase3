from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import requests
from requests.exceptions import RequestException

from src.core.config import settings


class CompatibilityServiceError(Exception):
    """Error al consumir el microservicio FastAPI de compatibilidad."""


class CompatibilityServiceClient:
    """Cliente HTTP hacia el microservicio FastAPI de compatibilidad.

    Vive separado del EncorelyHTTPClient porque apunta a otra base URL
    (FASTAPI_BASE_URL) y no requiere autenticación JWT.
    """

    def __init__(self, base_url: str | None = None, timeout: int | None = None) -> None:
        self.base_url = (base_url or settings.fastapi_base_url).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.request_timeout

    def calculate(
        self,
        vector_a: Sequence[float],
        vector_b: Sequence[float],
    ) -> dict[str, Any]:
        """Solicita el score de compatibilidad entre dos vibe vectors."""
        url = f"{self.base_url}/compatibility/calculate"
        payload = {
            "vector_a": {"vector": list(vector_a)},
            "vector_b": {"vector": list(vector_b)},
        }
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            raise CompatibilityServiceError(
                f"No se pudo calcular la compatibilidad en {url}: {exc}"
            ) from exc

    def is_healthy(self) -> bool:
        """Verifica disponibilidad del microservicio vía GET /health."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("status") == "ok"
        except RequestException:
            return False
