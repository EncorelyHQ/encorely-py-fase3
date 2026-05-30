from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError

from src.core.http_client import EncorelyHTTPClient, EncorelyHTTPClientError


def _http_error(status: int) -> HTTPError:
    response = MagicMock()
    response.status_code = status
    response.text = "error"
    error = HTTPError("boom")
    error.response = response
    return error


def _ok_response() -> MagicMock:
    response = MagicMock()
    response.raise_for_status.return_value = None
    return response


def _failing_response(status: int) -> MagicMock:
    response = MagicMock()
    response.raise_for_status.side_effect = _http_error(status)
    return response


def test_retries_once_after_successful_refresh() -> None:
    client = EncorelyHTTPClient(base_url="http://api")
    calls = {"refresh": 0}

    def handler() -> bool:
        calls["refresh"] += 1
        client.set_bearer_token("new-token")
        return True

    client.set_unauthorized_handler(handler)
    ok = _ok_response()

    with patch(
        "src.core.http_client.requests.request",
        side_effect=[_failing_response(401), ok],
    ) as request:
        result = client.get("/songs/")

    assert result is ok
    assert calls["refresh"] == 1
    assert request.call_count == 2


def test_does_not_retry_when_refresh_fails() -> None:
    client = EncorelyHTTPClient(base_url="http://api")
    client.set_unauthorized_handler(lambda: False)

    with patch(
        "src.core.http_client.requests.request",
        side_effect=[_failing_response(401)],
    ) as request:
        with pytest.raises(EncorelyHTTPClientError):
            client.get("/songs/")

    assert request.call_count == 1


def test_refresh_not_triggered_on_non_401() -> None:
    client = EncorelyHTTPClient(base_url="http://api")
    handler = MagicMock(return_value=True)
    client.set_unauthorized_handler(handler)

    with patch(
        "src.core.http_client.requests.request",
        side_effect=[_failing_response(500)],
    ):
        with pytest.raises(EncorelyHTTPClientError):
            client.get("/songs/")

    handler.assert_not_called()
