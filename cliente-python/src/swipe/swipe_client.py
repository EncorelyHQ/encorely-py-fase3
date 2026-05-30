from __future__ import annotations

from typing import Any

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient, EncorelyHTTPClientError

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

    def _as_list(self, payload: Any) -> list[dict[str, Any]]:
        """Normaliza respuestas paginadas (`{"results": [...]}`) o listas planas."""
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            return payload["results"]
        if isinstance(payload, list):
            return payload
        raise SwipeClientError("Formato inesperado: se esperaba una lista de elementos")

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
