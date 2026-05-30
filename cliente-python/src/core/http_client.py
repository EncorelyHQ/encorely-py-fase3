from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import urljoin

import requests
from requests import Response
from requests.exceptions import RequestException

from src.core.config import settings


class EncorelyHTTPClientError(Exception):
    """Error base para problemas de red o respuestas HTTP no exitosas."""


class EncorelyHTTPClient:
    """Facade HTTP para centralizar llamadas hacia la API Django."""

    def __init__(self, base_url: str | None = None, timeout: int | None = None) -> None:
        self.base_url = (base_url or settings.django_api_base_url).rstrip("/") + "/"
        self.timeout = timeout if timeout is not None else settings.request_timeout
        self._bearer_token: str | None = None
        self._on_unauthorized: Callable[[], bool] | None = None
        self._refreshing = False

    def set_bearer_token(self, token: str | None) -> None:
        """Inyecta el Bearer token usado en las cabeceras Authorization."""
        self._bearer_token = token

    def set_unauthorized_handler(self, handler: Callable[[], bool] | None) -> None:
        """Registra un callback que intenta refrescar el token ante un 401.

        Debe devolver True si logró renovar el token (en cuyo caso la petición
        original se reintenta una vez) y False si no fue posible.
        """
        self._on_unauthorized = handler

    def _build_url(self, endpoint: str) -> str:
        return urljoin(self.base_url, endpoint.lstrip("/"))

    def _build_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        base_headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._bearer_token:
            base_headers["Authorization"] = f"Bearer {self._bearer_token}"
        if headers:
            base_headers.update(headers)
        return base_headers

    def _run_refresh(self) -> bool:
        """Ejecuta el handler de refresh protegido contra recursión."""
        self._refreshing = True
        try:
            return bool(self._on_unauthorized()) if self._on_unauthorized else False
        except Exception:
            return False
        finally:
            self._refreshing = False

    def _request(
        self, method: str, endpoint: str, *, _allow_refresh: bool = True, **kwargs: Any
    ) -> Response:
        url = self._build_url(endpoint)
        request_kwargs = dict(kwargs)
        request_kwargs["headers"] = self._build_headers(kwargs.get("headers"))
        request_kwargs.setdefault("timeout", self.timeout)

        try:
            response = requests.request(method=method, url=url, **request_kwargs)
            response.raise_for_status()
            return response
        except RequestException as exc:
            response_obj = getattr(exc, "response", None)
            status_code = getattr(response_obj, "status_code", None)

            # Token expirado: intenta refrescar una sola vez y reintenta la petición.
            if (
                status_code == 401
                and _allow_refresh
                and self._on_unauthorized is not None
                and not self._refreshing
                and self._run_refresh()
            ):
                return self._request(method, endpoint, _allow_refresh=False, **kwargs)

            response_body = response_obj.text if response_obj is not None else ""
            raise EncorelyHTTPClientError(
                f"HTTP {method.upper()} {url} fallo"
                f" (status={status_code}, detail={response_body})"
            ) from exc

    def get(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Response:
        return self._request("get", endpoint, headers=headers, params=params)

    def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._request("post", endpoint, data=data, json=json, headers=headers)

    def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._request("put", endpoint, data=data, json=json, headers=headers)

    def patch(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response:
        return self._request("patch", endpoint, data=data, json=json, headers=headers)

    def delete(self, endpoint: str, headers: dict[str, str] | None = None) -> Response:
        return self._request("delete", endpoint, headers=headers)
