from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient


@pytest.fixture
def session() -> SessionManager:
    mgr = SessionManager()
    mgr.set_access_token("test-access-token")
    mgr.set_refresh_token("test-refresh-token")
    return mgr


@pytest.fixture
def http_client() -> MagicMock:
    return MagicMock(spec=EncorelyHTTPClient)


def make_response(payload: dict | list, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response
