from __future__ import annotations

from typing import Any

from src.core.authenticated_client import AuthenticatedClient
from src.core.http_client import EncorelyHTTPClientError


class EventsClientError(Exception):
    """Error del cliente de eventos para fallos HTTP o respuestas inválidas."""


class EventsClient(AuthenticatedClient):
    """Cliente del módulo Events: listado, asistencia y asistentes."""

    error_class = EventsClientError

    def get_events(
        self,
        city: str | None = None,
        artist: str | None = None,
        date_from: str | None = None,
    ) -> list[dict[str, Any]]:
        """Lista eventos con filtros opcionales por ciudad, artista o fecha."""
        self._authorize()
        params: dict[str, str] = {}
        if city:
            params["city"] = city
        if artist:
            params["artist"] = artist
        if date_from:
            params["date_from"] = date_from
        try:
            response = self.http_client.get("/events/", params=params or None)
        except EncorelyHTTPClientError as exc:
            raise EventsClientError(f"No se pudieron obtener los eventos: {exc}") from exc
        return self._as_list(self._response_json(response))

    def get_event(self, event_id: int | str) -> dict[str, Any]:
        """Obtiene el detalle de un evento."""
        self._authorize()
        try:
            response = self.http_client.get(f"/events/{event_id}/")
        except EncorelyHTTPClientError as exc:
            raise EventsClientError(f"No se pudo obtener el evento: {exc}") from exc
        data = self._response_json(response)
        if not isinstance(data, dict):
            raise EventsClientError("Formato inesperado al obtener evento")
        return data

    def attend_event(self, event_id: int | str, has_ticket: bool = False) -> dict[str, Any]:
        """Registra intención de asistencia a un evento."""
        self._authorize()
        try:
            response = self.http_client.post(
                f"/events/{event_id}/attend/",
                json={"has_ticket": has_ticket},
            )
        except EncorelyHTTPClientError as exc:
            raise EventsClientError(f"No se pudo registrar asistencia: {exc}") from exc
        data = self._response_json(response)
        if not isinstance(data, dict):
            raise EventsClientError("Formato inesperado al registrar asistencia")
        return data

    def get_attendees(self, event_id: int | str) -> list[dict[str, Any]]:
        """Lista asistentes de un evento con flag de compatibilidad."""
        self._authorize()
        try:
            response = self.http_client.get(f"/events/{event_id}/attendees/")
        except EncorelyHTTPClientError as exc:
            raise EventsClientError(f"No se pudieron obtener los asistentes: {exc}") from exc
        data = self._response_json(response)
        if isinstance(data, dict) and isinstance(data.get("results"), list):
            return data["results"]
        return self._as_list(data)
