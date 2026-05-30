from __future__ import annotations

import time
from typing import Any, Callable

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient, EncorelyHTTPClientError


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
        """Lista las salas de chat del usuario autenticado."""
        self._authorize()
        try:
            response = self.http_client.get("/chat/rooms/")
        except EncorelyHTTPClientError as exc:
            raise ChatClientError(f"No se pudieron obtener las salas: {exc}") from exc
        return self._as_list(self._response_json(response))

    def get_messages(self, room_id: int | str) -> list[dict[str, Any]]:
        """Obtiene el historial de mensajes de una sala."""
        self._authorize()
        try:
            response = self.http_client.get(f"/chat/rooms/{room_id}/messages/")
        except EncorelyHTTPClientError as exc:
            raise ChatClientError(f"No se pudieron obtener los mensajes: {exc}") from exc
        return self._as_list(self._response_json(response))

    def send_message(self, room_id: int | str, content: str) -> dict[str, Any]:
        """Envía un mensaje a una sala de chat."""
        if not content.strip():
            raise ChatClientError("El contenido del mensaje no puede estar vacío")
        self._authorize()
        try:
            response = self.http_client.post(
                f"/chat/rooms/{room_id}/messages/",
                json={"content": content},
            )
        except EncorelyHTTPClientError as exc:
            raise ChatClientError(f"No se pudo enviar el mensaje: {exc}") from exc
        data = self._response_json(response)
        if not isinstance(data, dict):
            raise ChatClientError("Formato inesperado al enviar mensaje")
        return data

    def mark_read(self, message_id: int | str) -> dict[str, Any]:
        """Marca un mensaje como leído."""
        self._authorize()
        try:
            response = self.http_client.patch(
                f"/chat/messages/{message_id}/read/",
                json={"is_read": True},
            )
        except EncorelyHTTPClientError as exc:
            raise ChatClientError(f"No se pudo marcar el mensaje como leído: {exc}") from exc
        data = self._response_json(response)
        if not isinstance(data, dict):
            raise ChatClientError("Formato inesperado al marcar mensaje")
        return data

    def poll_messages(
        self,
        room_id: int | str,
        interval: float = 3,
        stop_event: Callable[[], bool] | None = None,
        on_update: Callable[[list[dict[str, Any]]], None] | None = None,
    ) -> None:
        """Polling de mensajes cada `interval` segundos hasta interrupción o stop_event."""
        seen_ids: set[Any] = set()
        try:
            while True:
                if stop_event and stop_event():
                    break
                messages = self.get_messages(room_id)
                current_ids = {msg.get("id") for msg in messages}
                if current_ids != seen_ids:
                    seen_ids = current_ids
                    if on_update:
                        on_update(messages)
                time.sleep(interval)
        except KeyboardInterrupt:
            return
