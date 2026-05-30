from __future__ import annotations

from src.ui.display import show_error, show_info, show_title
from src.ui.menu import run_main_menu


def main() -> None:
    show_title("Bienvenido a Encorely")
    show_info("Iniciando cliente CLI...")

    try:
        run_main_menu()
    except KeyboardInterrupt:
        show_info("Ejecucion interrumpida por el usuario.")
    except Exception:
        show_error("Ocurrio un error inesperado. Intenta nuevamente.")


if __name__ == "__main__":
    main()
