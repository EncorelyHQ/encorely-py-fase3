from __future__ import annotations

from typing import Any

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient


class AuthenticatedClient:
    """Base para clientes que consumen endpoints autenticados de la API Django.

    Centraliza la construcción del cliente HTTP, la sincronización del bearer
    token desde la sesión y la normalización de respuestas JSON. Cada cliente
    concreto define `error_class` con su excepción de dominio.
    """

    error_class: type[Exception] = RuntimeError

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
            raise self.error_class("No existe una sesión activa con access token")
        self.http_client.set_bearer_token(token)

    def _response_json(self, response: Any) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise self.error_class("La respuesta del servidor no es JSON válido") from exc

    def _as_list(self, payload: Any) -> list[dict[str, Any]]:
        """Normaliza respuestas paginadas (`{"results": [...]}`) o listas planas."""
        if isinstance(payload, dict) and isinstance(payload.get("results"), list):
            return payload["results"]
        if isinstance(payload, list):
            return payload
        raise self.error_class("Formato inesperado: se esperaba una lista de elementos")
