from __future__ import annotations

from typing import Any

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient

# Umbral de swipes requeridos por el flujo Sound-Swipe de la Fase 3.
SWIPE_GOAL = 25


class SwipeType:
    """Tipos de swipe soportados por la API."""

    RIGHT = "RIGHT"
    LEFT = "LEFT"


class SwipeClientError(Exception):
    """Error del cliente de Sound-Swipe para fallos HTTP o respuestas inválidas."""


class SwipeClient:
    """Cliente del módulo Sound-Swipe.

    Consume los endpoints de canciones y swipes de la API Django reutilizando
    el EncorelyHTTPClient compartido y la sesión JWT activa.
    """

    def __init__(
        self,
        http_client: EncorelyHTTPClient | None = None,
        session_manager: SessionManager | None = None,
    ) -> None:
        self.http_client = http_client or EncorelyHTTPClient()
        self.session = session_manager or SessionManager()

    def _authorize(self) -> None:
        """Sincroniza el bearer token de la sesión hacia el cliente HTTP."""
        token = self.session.get_access_token()
        if not token:
            raise SwipeClientError("No existe una sesión activa con access token")
        self.http_client.set_bearer_token(token)

    def _response_json(self, response: Any) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise SwipeClientError("La respuesta del servidor no es JSON válido") from exc
