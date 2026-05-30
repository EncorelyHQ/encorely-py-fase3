from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from helpers import make_response

from src.auth.session import SessionManager
from src.chat.chat_client import ChatClient, ChatClientError


@pytest.fixture
def chat_client(http_client: MagicMock, session: SessionManager) -> ChatClient:
    return ChatClient(http_client=http_client, session_manager=session)


def test_get_rooms(chat_client: ChatClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response([{"id": 1, "other_user": {"username": "alice"}}])
    rooms = chat_client.get_rooms()
    http_client.get.assert_called_once_with("/chat/rooms/")
    assert rooms[0]["id"] == 1


def test_get_messages(chat_client: ChatClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response([{"id": 10, "content": "hola"}])
    messages = chat_client.get_messages(1)
    http_client.get.assert_called_once_with("/chat/rooms/1/messages/")
    assert messages[0]["content"] == "hola"


def test_send_message(chat_client: ChatClient, http_client: MagicMock) -> None:
    http_client.post.return_value = make_response({"id": 11, "content": "test"})
    result = chat_client.send_message(1, "test")
    http_client.post.assert_called_once_with("/chat/rooms/1/messages/", json={"content": "test"})
    assert result["id"] == 11


def test_send_empty_message_raises(chat_client: ChatClient) -> None:
    with pytest.raises(ChatClientError, match="vacío"):
        chat_client.send_message(1, "   ")


def test_mark_read(chat_client: ChatClient, http_client: MagicMock) -> None:
    http_client.patch.return_value = make_response({"id": 10, "is_read": True})
    result = chat_client.mark_read(10)
    http_client.patch.assert_called_once_with("/chat/messages/10/read/", json={"is_read": True})
    assert result["is_read"] is True


def test_poll_messages_invokes_callback(chat_client: ChatClient, http_client: MagicMock) -> None:
    http_client.get.side_effect = [
        make_response([{"id": 1, "content": "a"}]),
        make_response([{"id": 1, "content": "a"}, {"id": 2, "content": "b"}]),
    ]
    seen: list[list] = []
    stop_after = {"count": 0}

    def stop() -> bool:
        stop_after["count"] += 1
        return stop_after["count"] > 2

    with patch("src.chat.chat_client.time.sleep"):
        chat_client.poll_messages(1, interval=3, stop_event=stop, on_update=seen.append)

    assert len(seen) == 2
    assert len(seen[1]) == 2
