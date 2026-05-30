from __future__ import annotations

import json

from src.auth.auth_client import AuthClient, AuthClientError
from src.auth.session import SessionManager
from src.chat.chat_client import ChatClient, ChatClientError
from src.chat.chat_view import render_rooms_table, run_chat_session
from src.dna_core.dna_client import DNAClient, DNAClientError
from src.events.events_client import EventsClient, EventsClientError
from src.events.events_view import render_attendees_table, render_events_table
from src.matches.matches_client import MatchesClient, MatchesClientError
from src.matches.matches_view import render_matches_table, render_radar_table
from src.swipe.compatibility_client import CompatibilityServiceError
from src.swipe.swipe_client import SwipeClient, SwipeClientError, SwipeType
from src.swipe.swipe_service import SwipeService
from src.swipe.swipe_view import (
    render_compatibility_preview,
    render_song_card,
    render_swipe_progress,
)
from src.ui.display import (
    show_error,
    show_info,
    show_panel,
    show_success,
    show_table,
    show_title,
)
from src.ui.prompts import ask_password, ask_select, ask_text

MAIN_MENU_OPTIONS = [
    "Login",
    "Registro",
    "Ver mi DNA Core",
    "Sound Swipe",
    "Matches",
    "Chat",
    "Events",
    "Logout",
    "Salir",
]


def run_main_menu() -> None:
    session = SessionManager()
    auth_client = AuthClient(session_manager=session)
    dna_client = DNAClient(session_manager=session)

    show_title("Encorely")

    while True:
        choice = ask_select("Selecciona una opcion", MAIN_MENU_OPTIONS)
        if choice is None:
            show_info("Menu cerrado.")
            break

        if choice == "Login":
            _handle_login(auth_client)
        elif choice == "Registro":
            _handle_register(auth_client)
        elif choice == "Ver mi DNA Core":
            _handle_dna_core(dna_client, session)
        elif choice == "Sound Swipe":
            _handle_swipe(session)
        elif choice == "Matches":
            _handle_matches(session)
        elif choice == "Chat":
            _handle_chat(session)
        elif choice == "Events":
            _handle_events(session)
        elif choice == "Logout":
            _handle_logout(auth_client, session)
        elif choice == "Salir":
            show_info("Saliendo del cliente Encorely.")
            break


def _require_session(session: SessionManager, accion: str) -> bool:
    if not session.has_active_session():
        show_error(f"Debes iniciar sesion para {accion}.")
        return False
    return True


def _handle_login(auth_client: AuthClient) -> None:
    username = ask_text("Usuario")
    password = ask_password("Contraseña")

    if not username or not password:
        show_error("Usuario y contraseña son obligatorios.")
        return

    try:
        auth_client.login(username, password)
        show_success("Sesion iniciada correctamente.")
    except AuthClientError as exc:
        show_error(str(exc))


def _handle_register(auth_client: AuthClient) -> None:
    username = ask_text("Usuario")
    email = ask_text("Correo electronico (opcional)")
    password = ask_password("Contraseña")

    if not username or not password:
        show_error("Usuario y contraseña son obligatorios.")
        return

    try:
        response = auth_client.register(username=username, password=password, email=email or None)
        show_success("Registro completado correctamente.")
        show_panel("Respuesta del registro", json.dumps(response, indent=2, ensure_ascii=False))
    except AuthClientError as exc:
        show_error(str(exc))


def _handle_dna_core(dna_client: DNAClient, session: SessionManager) -> None:
    if not _require_session(session, "consultar tu DNA Core"):
        return

    try:
        data = dna_client.get_music_vector()
        user = data.get("user", {})
        vector = data.get("music_vector", [])

        show_panel(
            "DNA Core",
            json.dumps(
                {
                    "usuario": user,
                    "source": data.get("source"),
                },
                indent=2,
                ensure_ascii=False,
            ),
        )

        rows = [(str(index + 1), str(value)) for index, value in enumerate(vector)]
        show_table("Vector musical", ["#", "Valor"], rows)
    except DNAClientError as exc:
        show_error(str(exc))


def _handle_swipe(session: SessionManager) -> None:
    if not _require_session(session, "usar Sound Swipe"):
        return

    swipe_client = SwipeClient(session_manager=session)
    service = SwipeService(
        swipe_client=swipe_client,
        dna_client=DNAClient(session_manager=session),
    )

    try:
        songs = swipe_client.get_songs()
    except SwipeClientError as exc:
        show_error(str(exc))
        return

    if not songs:
        show_info("No hay canciones disponibles para hacer swipe.")
        return

    for song in songs:
        render_song_card(song)
        choice = ask_select(
            "¿Qué haces con esta canción?",
            ["Like (RIGHT)", "Pass (LEFT)", "Terminar"],
        )
        if choice is None or choice == "Terminar":
            break

        song_id = song.get("id")
        if song_id is None:
            show_error("La canción no tiene id; se omite.")
            continue

        try:
            if choice.startswith("Like"):
                try:
                    render_compatibility_preview(service.preview_compatibility(song))
                except CompatibilityServiceError:
                    show_info("Preview de compatibilidad no disponible (microservicio offline).")
                swipe_client.register_swipe(song_id, SwipeType.RIGHT)
            else:
                swipe_client.register_swipe(song_id, SwipeType.LEFT)
        except SwipeClientError as exc:
            show_error(str(exc))
            continue

    try:
        render_swipe_progress(swipe_client.count_my_swipes())
    except SwipeClientError as exc:
        show_error(str(exc))


def _handle_matches(session: SessionManager) -> None:
    if not _require_session(session, "ver tus matches"):
        return

    client = MatchesClient(session_manager=session)
    action = ask_select(
        "Matches",
        ["Ver radar de compatibilidad", "Ver mis matches", "Enviar solicitud", "Volver"],
    )
    if action is None or action == "Volver":
        return

    try:
        if action == "Ver radar de compatibilidad":
            render_radar_table(client.get_radar())
        elif action == "Ver mis matches":
            render_matches_table(client.get_matches())
        elif action == "Enviar solicitud":
            user_id = ask_text("ID del usuario al que enviar la solicitud")
            if user_id:
                client.send_match_request(user_id)
                show_success("Solicitud de match enviada.")
    except MatchesClientError as exc:
        show_error(str(exc))


def _handle_chat(session: SessionManager) -> None:
    if not _require_session(session, "usar el chat"):
        return

    client = ChatClient(session_manager=session)
    try:
        rooms = client.get_rooms()
    except ChatClientError as exc:
        show_error(str(exc))
        return

    render_rooms_table(rooms)
    if not rooms:
        show_info("No hay salas disponibles. Acepta un match primero.")
        return

    room_id = ask_text("ID de sala para chatear (Enter = volver)")
    if room_id:
        run_chat_session(room_id, client)


def _handle_events(session: SessionManager) -> None:
    if not _require_session(session, "ver eventos"):
        return

    client = EventsClient(session_manager=session)
    city = ask_text("Filtrar por ciudad (Enter = todas)") or None

    try:
        events = client.get_events(city=city)
        render_events_table(events)
        if not events:
            show_info("No hay eventos para los filtros indicados.")
            return

        event_id = ask_text("ID de evento para asistir (Enter = omitir)")
        if event_id:
            result = client.attend_event(event_id)
            show_success(f"Asistencia registrada (ticket: {result.get('has_ticket', False)}).")
            render_attendees_table(client.get_attendees(event_id))
    except EventsClientError as exc:
        show_error(str(exc))


def _handle_logout(auth_client: AuthClient, session: SessionManager) -> None:
    if not session.has_active_session():
        show_info("No hay una sesion activa.")
        return

    auth_client.logout()
    show_success("Sesion cerrada correctamente.")


if __name__ == "__main__":
    run_main_menu()
