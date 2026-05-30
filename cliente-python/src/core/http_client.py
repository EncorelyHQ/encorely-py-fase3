from __future__ import annotations

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

    def set_bearer_token(self, token: str | None) -> None:
        """Punto de extension para inyectar Bearer token sin manejar refresh."""
        self._bearer_token = token

    def _build_url(self, endpoint: str) -> str:
        return urljoin(self.base_url, endpoint.lstrip("/"))

    def _build_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        base_headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._bearer_token:
            base_headers["Authorization"] = f"Bearer {self._bearer_token}"
        if headers:
            base_headers.update(headers)
        return base_headers

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Response:
        url = self._build_url(endpoint)
        kwargs["headers"] = self._build_headers(kwargs.get("headers"))
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = requests.request(method=method, url=url, **kwargs)
            response.raise_for_status()
            return response
        except RequestException as exc:
            status_code = None
            response_body = ""
            if getattr(exc, "response", None) is not None:
                status_code = exc.response.status_code
                response_body = exc.response.text
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

    def delete(self, endpoint: str, headers: dict[str, str] | None = None) -> Response:
        return self._request("delete", endpoint, headers=headers)
