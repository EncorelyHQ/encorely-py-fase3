from __future__ import annotations

from typing import Any

from src.core.authenticated_client import AuthenticatedClient
from src.core.http_client import EncorelyHTTPClientError

# Umbral de swipes requeridos por el flujo Sound-Swipe de la Fase 3.
SWIPE_GOAL = 25


class SwipeType:
    """Tipos de swipe soportados por la API."""

    RIGHT = "RIGHT"
    LEFT = "LEFT"


class SwipeClientError(Exception):
    """Error del cliente de Sound-Swipe para fallos HTTP o respuestas inválidas."""


class SwipeClient(AuthenticatedClient):
    """Cliente del módulo Sound-Swipe.

    Consume los endpoints de canciones y swipes de la API Django reutilizando
    el EncorelyHTTPClient compartido y la sesión JWT activa.
    """

    error_class = SwipeClientError

    def get_songs(self) -> list[dict[str, Any]]:
        """Obtiene el catálogo de canciones disponibles para hacer swipe."""
        self._authorize()
        try:
            response = self.http_client.get("/songs/")
        except EncorelyHTTPClientError as exc:
            raise SwipeClientError(f"No se pudieron obtener las canciones: {exc}") from exc
        return self._as_list(self._response_json(response))

    def register_swipe(self, song_id: int | str, swipe_type: str) -> dict[str, Any]:
        """Registra un swipe (RIGHT/LEFT) sobre una canción."""
        if swipe_type not in (SwipeType.RIGHT, SwipeType.LEFT):
            raise SwipeClientError(f"Tipo de swipe inválido: {swipe_type!r}")

        self._authorize()
        payload = {"song": song_id, "type": swipe_type}
        try:
            response = self.http_client.post("/swipes/", json=payload)
        except EncorelyHTTPClientError as exc:
            raise SwipeClientError(f"No se pudo registrar el swipe: {exc}") from exc

        data = self._response_json(response)
        if not isinstance(data, dict):
            raise SwipeClientError("Respuesta de swipe inválida: se esperaba un objeto JSON")
        return data

    def get_my_swipes(self) -> list[dict[str, Any]]:
        """Devuelve los swipes registrados por el usuario autenticado."""
        self._authorize()
        try:
            response = self.http_client.get("/swipes/my/")
        except EncorelyHTTPClientError as exc:
            raise SwipeClientError(f"No se pudieron obtener tus swipes: {exc}") from exc
        return self._as_list(self._response_json(response))

    def count_my_swipes(self) -> int:
        """Cuenta los swipes realizados, útil para medir avance hacia SWIPE_GOAL."""
        return len(self.get_my_swipes())
