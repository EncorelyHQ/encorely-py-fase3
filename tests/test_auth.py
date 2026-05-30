from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from helpers import make_response

from src.auth.auth_client import AuthClient, AuthClientError
from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClientError


def _client(http: MagicMock, session: SessionManager | None = None) -> AuthClient:
    return AuthClient(http_client=http, session_manager=session or SessionManager())


def test_login_stores_tokens_and_registers_refresh_handler() -> None:
    http = MagicMock()
    http.post.return_value = make_response({"access": "AAA", "refresh": "RRR"})
    session = SessionManager()
    client = _client(http, session)

    data = client.login("user", "pass")

    http.post.assert_called_once_with(
        "/auth/login/", json={"username": "user", "password": "pass"}
    )
    assert session.get_access_token() == "AAA"
    assert session.get_refresh_token() == "RRR"
    http.set_bearer_token.assert_called_with("AAA")
    http.set_unauthorized_handler.assert_called_once()
    assert data["access"] == "AAA"


def test_login_accepts_alternative_token_keys() -> None:
    http = MagicMock()
    http.post.return_value = make_response({"access_token": "A", "refresh_token": "R"})
    session = SessionManager()
    _client(http, session).login("u", "p")
    assert session.get_access_token() == "A"
    assert session.get_refresh_token() == "R"


def test_login_without_tokens_raises() -> None:
    http = MagicMock()
    http.post.return_value = make_response({"detail": "bad credentials"})
    with pytest.raises(AuthClientError, match="tokens"):
        _client(http).login("u", "p")


def test_login_http_error_wrapped() -> None:
    http = MagicMock()
    http.post.side_effect = EncorelyHTTPClientError("401")
    with pytest.raises(AuthClientError, match="iniciar sesion"):
        _client(http).login("u", "p")


def test_refresh_token_updates_access() -> None:
    http = MagicMock()
    http.post.return_value = make_response({"access": "NEW"})
    session = SessionManager()
    session.set_refresh_token("RRR")
    _client(http, session).refresh_token()

    http.post.assert_called_once_with("/auth/token/refresh/", json={"refresh": "RRR"})
    assert session.get_access_token() == "NEW"
    http.set_bearer_token.assert_called_with("NEW")


def test_refresh_without_refresh_token_raises() -> None:
    with pytest.raises(AuthClientError, match="refresh token"):
        _client(MagicMock()).refresh_token()


def test_register_builds_payload_with_email() -> None:
    http = MagicMock()
    http.post.return_value = make_response({"id": 1, "username": "u"})
    result = _client(http).register(username="u", password="p", email="e@x.com")

    http.post.assert_called_once_with(
        "/auth/register/", json={"username": "u", "password": "p", "email": "e@x.com"}
    )
    assert result["id"] == 1


def test_logout_clears_session_and_handler() -> None:
    http = MagicMock()
    session = SessionManager()
    session.set_access_token("A")
    session.set_refresh_token("R")
    _client(http, session).logout()

    assert session.get_access_token() is None
    http.set_bearer_token.assert_called_with(None)
    http.set_unauthorized_handler.assert_called_with(None)


def test_get_current_user() -> None:
    http = MagicMock()
    http.get.return_value = make_response({"id": 7, "username": "u"})
    session = SessionManager()
    session.set_access_token("A")
    user = _client(http, session).get_current_user()

    http.get.assert_called_once_with("/auth/me/")
    assert user["id"] == 7
