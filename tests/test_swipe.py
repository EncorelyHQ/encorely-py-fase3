from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from helpers import make_response

from src.auth.session import SessionManager
from src.swipe.swipe_client import SwipeClient, SwipeClientError, SwipeType
from src.swipe.swipe_service import SwipeService, song_to_vector


@pytest.fixture
def swipe_client(http_client: MagicMock, session: SessionManager) -> SwipeClient:
    return SwipeClient(http_client=http_client, session_manager=session)


def test_song_to_vector_flat_keeps_feature_order() -> None:
    # Orden canónico: energy, danceability, valence, tempo.
    song = {"danceability": 0.8, "energy": 0.6, "valence": 0.7, "extra": 1}
    assert song_to_vector(song) == [0.6, 0.8, 0.7]


def test_song_to_vector_supports_nested_features() -> None:
    song = {"audio_features": {"danceability": 0.5, "tempo": 120.0}}
    assert song_to_vector(song) == [0.5, 120.0]


def test_song_to_vector_without_features_raises() -> None:
    with pytest.raises(SwipeClientError):
        song_to_vector({"title": "x"})


def test_preview_compatibility_uses_user_vector_and_caches() -> None:
    dna = MagicMock()
    dna.get_music_vector.return_value = {"music_vector": [1.0, 0.0, 0.0]}
    compat = MagicMock()
    compat.calculate.return_value = {"score": 0.9, "classification": "COMPATIBLE"}
    service = SwipeService(swipe_client=MagicMock(), compatibility_client=compat, dna_client=dna)

    song = {"danceability": 0.5, "energy": 0.4, "valence": 0.3}
    result = service.preview_compatibility(song)

    compat.calculate.assert_called_once_with([1.0, 0.0, 0.0], [0.4, 0.5, 0.3])
    assert result["classification"] == "COMPATIBLE"

    service.preview_compatibility(song)
    dna.get_music_vector.assert_called_once()


def test_swipe_right_previews_then_registers() -> None:
    dna = MagicMock()
    dna.get_music_vector.return_value = {"music_vector": [1.0]}
    compat = MagicMock()
    compat.calculate.return_value = {"score": 0.8}
    swipe = MagicMock()
    swipe.register_swipe.return_value = {"id": 99}
    service = SwipeService(swipe_client=swipe, compatibility_client=compat, dna_client=dna)

    out = service.swipe_right({"id": 7, "danceability": 0.5})

    swipe.register_swipe.assert_called_once_with(7, SwipeType.RIGHT)
    assert out["swipe"]["id"] == 99
    assert out["preview"]["score"] == 0.8


def test_swipe_right_without_id_raises() -> None:
    dna = MagicMock()
    dna.get_music_vector.return_value = {"music_vector": [1.0]}
    compat = MagicMock()
    compat.calculate.return_value = {"score": 0.8}
    service = SwipeService(swipe_client=MagicMock(), compatibility_client=compat, dna_client=dna)

    with pytest.raises(SwipeClientError, match="id"):
        service.swipe_right({"danceability": 0.5})


def test_get_songs_normalizes_paginated(swipe_client: SwipeClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response({"results": [{"id": 1}]})
    songs = swipe_client.get_songs()
    http_client.get.assert_called_once_with("/songs/")
    assert songs[0]["id"] == 1


def test_register_swipe_rejects_invalid_type(swipe_client: SwipeClient) -> None:
    with pytest.raises(SwipeClientError, match="inválido"):
        swipe_client.register_swipe(1, "UP")


def test_register_swipe_payload(swipe_client: SwipeClient, http_client: MagicMock) -> None:
    http_client.post.return_value = make_response({"id": 3})
    swipe_client.register_swipe(5, SwipeType.RIGHT)
    http_client.post.assert_called_once_with("/swipes/", json={"song": 5, "type": "RIGHT"})


def test_count_my_swipes(swipe_client: SwipeClient, http_client: MagicMock) -> None:
    http_client.get.return_value = make_response([{"id": 1}, {"id": 2}])
    assert swipe_client.count_my_swipes() == 2
