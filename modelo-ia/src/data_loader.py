from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException

from src.config import settings


class DataLoaderError(Exception):
    """Error al cargar datos desde la API Django."""


class DjangoAPIClient:
    """Cliente HTTP mínimo para el módulo de análisis."""

    def __init__(self) -> None:
        self.base_url = settings.django_api_base_url
        self.timeout = settings.request_timeout
        self._token: str | None = None

    def login(self) -> None:
        url = urljoin(self.base_url, "auth/login/")
        try:
            response = requests.post(
                url,
                json={"username": settings.django_username, "password": settings.django_password},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except RequestException as exc:
            raise DataLoaderError(f"No se pudo autenticar: {exc}") from exc

        data = response.json()
        token = data.get("access") or data.get("access_token")
        if not isinstance(token, str):
            raise DataLoaderError("Respuesta de login inválida: falta access token")
        self._token = token

    def _headers(self) -> dict[str, str]:
        if not self._token:
            raise DataLoaderError("Debe autenticarse antes de consumir datos")
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        try:
            response = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except RequestException as exc:
            raise DataLoaderError(f"GET {endpoint} falló: {exc}") from exc


def _as_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload["results"]
    if isinstance(payload, list):
        return payload
    return []


def load_matches(client: DjangoAPIClient) -> list[dict[str, Any]]:
    return _as_records(client.get("matches/"))


def load_users(client: DjangoAPIClient) -> list[dict[str, Any]]:
    return _as_records(client.get("auth/management/"))


def load_swipes(client: DjangoAPIClient) -> list[dict[str, Any]]:
    return _as_records(client.get("swipes/my/"))


def load_all_dataframes():
    """Autentica y retorna DataFrames de matches, usuarios y swipes."""
    import pandas as pd

    client = DjangoAPIClient()
    client.login()

    matches_df = pd.json_normalize(load_matches(client))
    users_df = pd.json_normalize(load_users(client))
    swipes_df = pd.json_normalize(load_swipes(client))

    return {
        "matches": matches_df,
        "users": users_df,
        "swipes": swipes_df,
    }
