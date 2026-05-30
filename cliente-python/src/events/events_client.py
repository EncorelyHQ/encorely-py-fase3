from __future__ import annotations

from typing import Any

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient


class EventsClientError(Exception):
    """Error del cliente de eventos para fallos HTTP o respuestas inválidas."""


class EventsClient:
    """Cliente del módulo Events: listado, asistencia y asistentes."""

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
            raise EventsClientError("No existe una sesión activa con access token")
        self.http_client.set_bearer_token(token)

    def _response_json(self, response: Any) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise EventsClientError("La respuesta del servidor no es JSON válido") from exc

    def _as_list(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            return payload["results"]
        if isinstance(payload, list):
            return payload
        raise EventsClientError("Formato inesperado: se esperaba una lista de elementos")

    def get_events(
        self,
        city: str | None = None,
        artist: str | None = None,
        date_from: str | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get_event(self, event_id: int | str) -> dict[str, Any]:
        raise NotImplementedError

    def attend_event(self, event_id: int | str, has_ticket: bool = False) -> dict[str, Any]:
        raise NotImplementedError

    def get_attendees(self, event_id: int | str) -> list[dict[str, Any]]:
        raise NotImplementedError
