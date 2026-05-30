from __future__ import annotations

from unittest.mock import MagicMock


def make_response(payload: dict | list, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response
