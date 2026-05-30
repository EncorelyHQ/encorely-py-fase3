from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from helpers import make_response

from src.auth.session import SessionManager
from src.events.events_client import EventsClient, EventsClientError


@pytest.fixture
def events_client(http_client: MagicMock, session: SessionManager) -> EventsClient:
    return EventsClient(http_client=http_client, session_manager=session)


def test_get_events_with_city_filter(events_client: EventsClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response([
        {"id": 1, "title": "Concierto", "city": "Medellín"},
    ])
    events = events_client.get_events(city="Medellín")
    http_client.get.assert_called_once_with("/events/", params={"city": "Medellín"})
    assert events[0]["city"] == "Medellín"


def test_get_event_detail(events_client: EventsClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response({"id": 3, "title": "Festival"})
    result = events_client.get_event(3)
    http_client.get.assert_called_once_with("/events/3/")
    assert result["title"] == "Festival"


def test_attend_event(events_client: EventsClient, http_client: MagicMock) -> None:
    http_client.post.return_value = make_response({"id": 1, "has_ticket": True})
    result = events_client.attend_event(1, has_ticket=True)
    http_client.post.assert_called_once_with("/events/1/attend/", json={"has_ticket": True})
    assert result["has_ticket"] is True


def test_get_attendees(events_client: EventsClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response({
        "count": 1,
        "results": [{"user": {"id": 2, "username": "bob"}, "is_compatible": True}],
    })
    attendees = events_client.get_attendees(1)
    http_client.get.assert_called_once_with("/events/1/attendees/")
    assert attendees[0]["is_compatible"] is True


def test_get_events_without_token_raises() -> None:
    client = EventsClient(http_client=MagicMock(), session_manager=SessionManager())
    with pytest.raises(EventsClientError, match="sesión activa"):
        client.get_events()
