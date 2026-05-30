from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from helpers import make_response

from src.auth.session import SessionManager
from src.dna_core.dna_client import DNAClient, DNAClientError


def _client(http: MagicMock, with_token: bool = True) -> DNAClient:
    session = SessionManager()
    if with_token:
        session.set_access_token("A")
    return DNAClient(http_client=http, session_manager=session)


def test_uses_embedded_vector_from_me() -> None:
    http = MagicMock()
    http.get.return_value = make_response(
        {"id": 1, "username": "u", "music_vector": [0.1, 0.2, 0.3]}
    )
    data = _client(http).get_music_vector()

    http.get.assert_called_once_with("/auth/me/", headers={"Authorization": "Bearer A"})
    assert data["music_vector"] == [0.1, 0.2, 0.3]
    assert data["source"] == "/auth/me/"


def test_falls_back_to_vibe_endpoint() -> None:
    http = MagicMock()
    http.get.side_effect = [
        make_response({"id": 5, "username": "u"}),
        make_response({"vibe_vector": [0.5, 0.6]}),
    ]
    data = _client(http).get_music_vector()

    assert http.get.call_count == 2
    http.get.assert_any_call("/users/5/vibe/", headers={"Authorization": "Bearer A"})
    assert data["music_vector"] == [0.5, 0.6]
    assert data["source"] == "/users/5/vibe/"


def test_without_session_raises() -> None:
    with pytest.raises(DNAClientError, match="sesion activa"):
        _client(MagicMock(), with_token=False).get_music_vector()


def test_vibe_without_vector_raises() -> None:
    http = MagicMock()
    http.get.side_effect = [
        make_response({"id": 5, "username": "u"}),
        make_response({"foo": "bar"}),
    ]
    with pytest.raises(DNAClientError, match="vector musical"):
        _client(http).get_music_vector()
