from __future__ import annotations

import json

from src.auth.auth_client import AuthClient, AuthClientError
from src.auth.session import SessionManager
from src.dna_core.dna_client import DNAClient, DNAClientError
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
			_show_placeholder("Sound Swipe")
		elif choice == "Matches":
			_show_placeholder("Matches")
		elif choice == "Chat":
			_show_placeholder("Chat")
		elif choice == "Events":
			_show_placeholder("Events")
		elif choice == "Logout":
			_handle_logout(auth_client, session)
		elif choice == "Salir":
			show_info("Saliendo del cliente Encorely.")
			break


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
	if not session.has_active_session():
		show_error("Debes iniciar sesion para consultar tu DNA Core.")
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


def _handle_logout(auth_client: AuthClient, session: SessionManager) -> None:
	if not session.has_active_session():
		show_info("No hay una sesion activa.")
		return

	auth_client.logout()
	show_success("Sesion cerrada correctamente.")


def _show_placeholder(module_name: str) -> None:
	show_info(f"{module_name}: modulo en integracion.")


if __name__ == "__main__":
	run_main_menu()