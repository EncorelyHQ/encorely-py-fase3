from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import questionary


def ask_text(message: str) -> str:
    answer = questionary.text(message).ask()
    return "" if answer is None else str(answer)


def ask_password(message: str) -> str:
    answer = questionary.password(message).ask()
    return "" if answer is None else str(answer)


def ask_select(message: str, choices: Sequence[Any]) -> Any:
    return questionary.select(message, choices=choices).ask()


def ask_confirm(message: str) -> bool:
    answer = questionary.confirm(message).ask()
    return bool(answer)
