from __future__ import annotations

from typing import Any

from src.ui.display import show_error, show_info, show_table, show_title


def _sender_name(message: dict[str, Any]) -> str:
    sender = message.get("sender") or {}
    return str(sender.get("display_name") or sender.get("username") or "?")


def render_rooms_table(rooms: list[dict[str, Any]]) -> None:
    """Lista salas de chat disponibles."""
    rows = [
        (
            r.get("id", ""),
            _other_user_name(r),
            r.get("friendship_status", ""),
            r.get("created_at", ""),
        )
        for r in rooms
    ]
    show_table("Salas de chat", ["ID", "Otro usuario", "Estado match", "Creada"], rows)


def _other_user_name(room: dict[str, Any]) -> str:
    other = room.get("other_user") or {}
    return str(other.get("display_name") or other.get("username") or "?")


def render_messages_table(messages: list[dict[str, Any]]) -> None:
    """Muestra historial de mensajes de una sala."""
    rows = [
        (
            m.get("id", ""),
            _sender_name(m),
            m.get("content", ""),
            "Sí" if m.get("is_read") else "No",
            m.get("sent_at", ""),
        )
        for m in messages
    ]
    show_table("Mensajes", ["ID", "Remitente", "Contenido", "Leído", "Enviado"], rows)


def run_chat_session(room_id: int | str, client: Any) -> None:
    """Loop interactivo con polling cada 3 segundos."""
    stop = {"value": False}

    def on_update(messages: list[dict[str, Any]]) -> None:
        render_messages_table(messages)

    show_info(f"Sala {room_id} — escribe mensajes o 'salir' para terminar. Polling cada 3s.")

    import threading

    poller = threading.Thread(
        target=client.poll_messages,
        kwargs={"room_id": room_id, "interval": 3, "stop_event": lambda: stop["value"], "on_update": on_update},
        daemon=True,
    )
    poller.start()

    try:
        while not stop["value"]:
            text = input("> ").strip()
            if text.lower() in ("salir", "exit", "quit"):
                stop["value"] = True
                break
            if text:
                client.send_message(room_id, text)
    except (KeyboardInterrupt, EOFError):
        stop["value"] = True

    poller.join(timeout=4)


def _demo() -> None:
    import getpass

    from src.auth.auth_client import AuthClient, AuthClientError
    from src.chat.chat_client import ChatClient, ChatClientError
    from src.core.http_client import EncorelyHTTPClient

    show_title("Encorely — Chat")
    username = input("Usuario: ").strip()
    password = getpass.getpass("Contraseña: ")

    http = EncorelyHTTPClient()
    auth = AuthClient(http_client=http)
    try:
        auth.login(username, password)
    except AuthClientError as exc:
        show_error(str(exc))
        return

    client = ChatClient(http_client=http, session_manager=auth.session)
    try:
        rooms = client.get_rooms()
        render_rooms_table(rooms)
        if not rooms:
            show_info("No hay salas disponibles. Acepta un match primero.")
            return
        room_id = input("ID de sala para chatear: ").strip()
        if room_id:
            run_chat_session(room_id, client)
    except ChatClientError as exc:
        show_error(str(exc))


if __name__ == "__main__":
    _demo()
