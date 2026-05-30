from __future__ import annotations

from typing import Any

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient, EncorelyHTTPClientError


class AuthClientError(Exception):
    """Error de autenticacion para respuestas invalidas o fallos HTTP."""


class AuthClient:
    def __init__(
        self,
        http_client: EncorelyHTTPClient | None = None,
        session_manager: SessionManager | None = None,
    ) -> None:
        self.http_client = http_client or EncorelyHTTPClient()
        self.session = session_manager or SessionManager()

    def register(
        self,
        username: str,
        password: str,
        email: str | None = None,
        **extra_fields: Any,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "username": username,
            "password": password,
        }
        if email:
            payload["email"] = email
        if extra_fields:
            payload.update(extra_fields)

        try:
            response = self.http_client.post("/auth/register/", json=payload)
            return self._response_json(response)
        except EncorelyHTTPClientError as exc:
            raise AuthClientError(f"No se pudo registrar usuario: {exc}") from exc

    def login(self, username: str, password: str) -> dict[str, Any]:
        payload = {
            "username": username,
            "password": password,
        }

        try:
            response = self.http_client.post("/auth/login/", json=payload)
            data = self._response_json(response)
        except EncorelyHTTPClientError as exc:
            raise AuthClientError(f"No se pudo iniciar sesion: {exc}") from exc

        access_token = data.get("access") or data.get("access_token")
        refresh_token = data.get("refresh") or data.get("refresh_token")

        if not isinstance(access_token, str) or not isinstance(refresh_token, str):
            raise AuthClientError("Respuesta de login invalida: faltan tokens access/refresh")

        self.session.set_access_token(access_token)
        self.session.set_refresh_token(refresh_token)
        self.http_client.set_bearer_token(access_token)
        return data

    def refresh_token(self) -> dict[str, Any]:
        refresh_token = self.session.get_refresh_token()
        if not refresh_token:
            raise AuthClientError("No existe refresh token en la sesion actual")

        try:
            response = self.http_client.post(
                "/auth/token/refresh/",
                json={"refresh": refresh_token},
            )
            data = self._response_json(response)
        except EncorelyHTTPClientError as exc:
            raise AuthClientError(f"No se pudo refrescar el token: {exc}") from exc

        new_access_token = data.get("access") or data.get("access_token")
        if not isinstance(new_access_token, str):
            raise AuthClientError("Respuesta de refresh invalida: falta access token")

        self.session.set_access_token(new_access_token)
        self.http_client.set_bearer_token(new_access_token)
        return data

    def logout(self) -> None:
        self.session.clear_session()
        self.http_client.set_bearer_token(None)

    def get_current_user(self) -> dict[str, Any]:
        access_token = self.session.get_access_token()
        if access_token:
            self.http_client.set_bearer_token(access_token)

        try:
            response = self.http_client.get("/auth/me/")
            return self._response_json(response)
        except EncorelyHTTPClientError as exc:
            raise AuthClientError(f"No se pudo obtener el usuario actual: {exc}") from exc

    def _response_json(self, response: Any) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise AuthClientError("La respuesta del servidor no es JSON valido") from exc

        if not isinstance(payload, dict):
            raise AuthClientError("Formato de respuesta no soportado: se esperaba objeto JSON")

        return payload
