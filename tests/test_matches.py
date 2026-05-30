from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClientError
from src.matches.matches_client import MatchesClient, MatchesClientError

from helpers import make_response


@pytest.fixture
def matches_client(http_client: MagicMock, session: SessionManager) -> MatchesClient:
    return MatchesClient(http_client=http_client, session_manager=session)


def test_get_matches_returns_list(matches_client: MatchesClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response([
        {"id": 1, "status": "pending", "compatibility_score": 0.85},
    ])
    result = matches_client.get_matches()
    http_client.get.assert_called_once_with("/matches/")
    http_client.set_bearer_token.assert_called_with("test-access-token")
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_get_radar_returns_suggestions(matches_client: MatchesClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response({
        "count": 1,
        "suggestions": [{"user_id": 2, "compatibility_score": 0.91}],
        "your_swipe_count": 25,
    })
    result = matches_client.get_radar()
    http_client.get.assert_called_once_with("/matches/radar/")
    assert result["count"] == 1


def test_send_match_request_payload(matches_client: MatchesClient, http_client: MagicMock) -> None:
    http_client.post.return_value = make_response({"id": 5, "status": "pending"})
    result = matches_client.send_match_request(2)
    http_client.post.assert_called_once_with("/matches/", json={"other_user_id": 2})
    assert result["id"] == 5


def test_respond_match_accept(matches_client: MatchesClient, http_client: MagicMock) -> None:
    http_client.patch.return_value = make_response({"id": 5, "status": "accepted"})
    result = matches_client.respond_match(5, accept=True)
    http_client.patch.assert_called_once_with("/matches/5/", json={"status": "accepted"})
    assert result["status"] == "accepted"


def test_respond_match_reject(matches_client: MatchesClient, http_client: MagicMock) -> None:
    http_client.patch.return_value = make_response({"id": 5, "status": "blocked"})
    matches_client.respond_match(5, accept=False)
    http_client.patch.assert_called_once_with("/matches/5/", json={"status": "blocked"})


def test_get_matches_without_token_raises() -> None:
    client = MatchesClient(http_client=MagicMock(), session_manager=SessionManager())
    with pytest.raises(MatchesClientError, match="sesión activa"):
        client.get_matches()


def test_get_radar_http_error(matches_client: MatchesClient, http_client: MagicMock) -> None:
    http_client.get.side_effect = EncorelyHTTPClientError("403 forbidden")
    with pytest.raises(MatchesClientError, match="radar"):
        matches_client.get_radar()
