from __future__ import annotations

from typing import Any

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient


class MatchesClientError(Exception):
    """Error del cliente de matches para fallos HTTP o respuestas inválidas."""


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
        raise NotImplementedError

    def get_radar(self) -> dict[str, Any]:
        raise NotImplementedError

    def send_match_request(self, user_id: int | str) -> dict[str, Any]:
        raise NotImplementedError

    def respond_match(self, match_id: int | str, accept: bool) -> dict[str, Any]:
        raise NotImplementedError

    def get_compatibility(self, other_user_id: int | str) -> dict[str, Any]:
        raise NotImplementedError
