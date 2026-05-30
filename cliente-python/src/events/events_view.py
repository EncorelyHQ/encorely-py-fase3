from __future__ import annotations

from typing import Any

from src.ui.display import show_error, show_info, show_success, show_table, show_title


def render_events_table(events: list[dict[str, Any]]) -> None:
    """Lista eventos con datos principales."""
    rows = [
        (
            e.get("id", ""),
            e.get("title", ""),
            e.get("artist_name", ""),
            e.get("venue_name", ""),
            e.get("city", ""),
            e.get("event_date", ""),
        )
        for e in events
    ]
    show_table(
        "Eventos",
        ["ID", "Título", "Artista", "Venue", "Ciudad", "Fecha"],
        rows,
    )


def render_attendees_table(attendees: list[dict[str, Any]]) -> None:
    """Lista asistentes con flag de compatibilidad."""
    rows = []
    for att in attendees:
        user = att.get("user") or {}
        compatible = att.get("is_compatible", False)
        rows.append((
            user.get("id", ""),
            user.get("username", ""),
            user.get("display_name", ""),
            user.get("city", ""),
            "Sí" if att.get("has_ticket") else "No",
            "Sí" if compatible else "No",
        ))
    show_table(
        "Asistentes",
        ["ID", "Username", "Nombre", "Ciudad", "Ticket", "Compatible"],
        rows,
    )


def _demo() -> None:
    import getpass

    from src.auth.auth_client import AuthClient, AuthClientError
    from src.core.http_client import EncorelyHTTPClient
    from src.events.events_client import EventsClient, EventsClientError

    show_title("Encorely — Eventos")
    username = input("Usuario: ").strip()
    password = getpass.getpass("Contraseña: ")

    http = EncorelyHTTPClient()
    auth = AuthClient(http_client=http)
    try:
        auth.login(username, password)
    except AuthClientError as exc:
        show_error(str(exc))
        return

    client = EventsClient(http_client=http, session_manager=auth.session)
    city = input("Filtrar por ciudad (Enter = todas): ").strip() or None

    try:
        events = client.get_events(city=city)
        render_events_table(events)
        if not events:
            return
        event_id = input("ID de evento para asistir (Enter = omitir): ").strip()
        if event_id:
            result = client.attend_event(event_id)
            show_success(f"Asistencia registrada (ticket: {result.get('has_ticket', False)})")
            attendees = client.get_attendees(event_id)
            render_attendees_table(attendees)
    except EventsClientError as exc:
        show_error(str(exc))


if __name__ == "__main__":
    _demo()
