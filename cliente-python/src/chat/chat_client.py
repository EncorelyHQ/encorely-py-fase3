from __future__ import annotations

from typing import Any, Callable

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient


class ChatClientError(Exception):
    """Error del cliente de chat para fallos HTTP o respuestas inválidas."""


class ChatClient:
    """Cliente del módulo Chat con soporte de polling."""

    def __init__(
        self,
        http_client: EncorelyHTTPClient | None = None,
        session_manager: SessionManager | None = None,
    ) -> None:
        self.http_client = http_client or EncorelyHTTPClient()
        self.session = session_manager or SessionManager()

    def _authorize(self) -> None:
        token = self.session.get_access_token()
        if not token:
            raise ChatClientError("No existe una sesión activa con access token")
        self.http_client.set_bearer_token(token)

    def _response_json(self, response: Any) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise ChatClientError("La respuesta del servidor no es JSON válido") from exc

    def _as_list(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            return payload["results"]
        if isinstance(payload, list):
            return payload
        raise ChatClientError("Formato inesperado: se esperaba una lista de elementos")

    def get_rooms(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get_messages(self, room_id: int | str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def send_message(self, room_id: int | str, content: str) -> dict[str, Any]:
        raise NotImplementedError

    def mark_read(self, message_id: int | str) -> dict[str, Any]:
        raise NotImplementedError

    def poll_messages(
        self,
        room_id: int | str,
        interval: float = 3,
        stop_event: Callable[[], bool] | None = None,
        on_update: Callable[[list[dict[str, Any]]], None] | None = None,
    ) -> None:
        raise NotImplementedError
