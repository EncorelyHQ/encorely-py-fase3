from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SessionManager:
    access_token: str | None = None
    refresh_token: str | None = None

    def set_access_token(self, token: str | None) -> None:
        self.access_token = token

    def set_refresh_token(self, token: str | None) -> None:
        self.refresh_token = token

    def get_access_token(self) -> str | None:
        return self.access_token

    def get_refresh_token(self) -> str | None:
        return self.refresh_token

    def clear_session(self) -> None:
        self.access_token = None
        self.refresh_token = None

    def has_active_session(self) -> bool:
        return bool(self.access_token and self.refresh_token)
