from __future__ import annotations

from typing import Any

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient, EncorelyHTTPClientError


class MatchesClientError(Exception):
    """Error del cliente de matches para fallos HTTP o respuestas inválidas."""


class MatchStatus:
    ACCEPTED = "accepted"
    BLOCKED = "blocked"


class MatchesClient:
    """Cliente del módulo Matches y Radar de compatibilidad."""

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
            raise MatchesClientError("No existe una sesión activa con access token")
        self.http_client.set_bearer_token(token)

    def _response_json(self, response: Any) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise MatchesClientError("La respuesta del servidor no es JSON válido") from exc

    def _as_list(self, payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            return payload["results"]
        if isinstance(payload, list):
            return payload
        raise MatchesClientError("Formato inesperado: se esperaba una lista de elementos")

    def get_matches(self) -> list[dict[str, Any]]:
        """Lista las friendships del usuario autenticado."""
        self._authorize()
        try:
            response = self.http_client.get("/matches/")
        except EncorelyHTTPClientError as exc:
            raise MatchesClientError(f"No se pudieron obtener los matches: {exc}") from exc
        return self._as_list(self._response_json(response))

    def get_radar(self) -> dict[str, Any]:
        """Usuarios compatibles con score > 70%; requiere 25+ swipes."""
        self._authorize()
        try:
            response = self.http_client.get("/matches/radar/")
        except EncorelyHTTPClientError as exc:
            raise MatchesClientError(f"No se pudo obtener el radar: {exc}") from exc
        data = self._response_json(response)
        if not isinstance(data, dict):
            raise MatchesClientError("Formato inesperado en respuesta del radar")
        return data

    def send_match_request(self, user_id: int | str) -> dict[str, Any]:
        """Envía solicitud de match a otro usuario."""
        self._authorize()
        payload = {"other_user_id": user_id}
        try:
            response = self.http_client.post("/matches/", json=payload)
        except EncorelyHTTPClientError as exc:
            raise MatchesClientError(f"No se pudo enviar la solicitud de match: {exc}") from exc
        data = self._response_json(response)
        if not isinstance(data, dict):
            raise MatchesClientError("Formato inesperado al crear match")
        return data

    def respond_match(self, match_id: int | str, accept: bool) -> dict[str, Any]:
        """Acepta o rechaza una solicitud de match pendiente."""
        self._authorize()
        status = MatchStatus.ACCEPTED if accept else MatchStatus.BLOCKED
        try:
            response = self.http_client.patch(f"/matches/{match_id}/", json={"status": status})
        except EncorelyHTTPClientError as exc:
            raise MatchesClientError(f"No se pudo responder al match: {exc}") from exc
        data = self._response_json(response)
        if not isinstance(data, dict):
            raise MatchesClientError("Formato inesperado al actualizar match")
        return data

    def get_compatibility(self, other_user_id: int | str) -> dict[str, Any]:
        """Consulta compatibilidad en tiempo real con otro usuario."""
        self._authorize()
        try:
            response = self.http_client.get(f"/matches/compatibility/{other_user_id}/")
        except EncorelyHTTPClientError as exc:
            raise MatchesClientError(f"No se pudo calcular compatibilidad: {exc}") from exc
        data = self._response_json(response)
        if not isinstance(data, dict):
            raise MatchesClientError("Formato inesperado en compatibilidad")
        return data
