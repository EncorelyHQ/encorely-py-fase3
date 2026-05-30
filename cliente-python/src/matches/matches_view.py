from __future__ import annotations

from typing import Any

from rich.panel import Panel

from src.ui.display import console, show_error, show_info, show_table, show_title

RADAR_MIN_SCORE = 0.70


def _format_user(user: dict[str, Any] | None) -> str:
    if not user:
        return "—"
    name = user.get("display_name") or user.get("username") or "?"
    return str(name)


def render_radar_table(radar: dict[str, Any]) -> None:
    """Muestra sugerencias del radar con score >= 70%."""
    suggestions = radar.get("suggestions") or []
    filtered = [
        s for s in suggestions
        if float(s.get("compatibility_score", 0)) >= RADAR_MIN_SCORE
    ]
    show_info(
        f"Swipes: {radar.get('your_swipe_count', '?')} / "
        f"{radar.get('minimum_swipes_required', 25)} | "
        f"Sugerencias compatibles: {len(filtered)}"
    )
    rows = [
        (
            s.get("user_id", ""),
            s.get("username", ""),
            s.get("display_name", ""),
            s.get("city", ""),
            f"{float(s.get('compatibility_score', 0)) * 100:.1f}%",
        )
        for s in filtered
    ]
    show_table(
        "Radar de compatibilidad (≥ 70%)",
        ["ID", "Username", "Nombre", "Ciudad", "Score"],
        rows,
    )


def render_matches_table(matches: list[dict[str, Any]]) -> None:
    """Lista friendships del usuario."""
    rows = [
        (
            m.get("id", ""),
            _format_user(m.get("user_source")),
            _format_user(m.get("user_target")),
            m.get("status", ""),
            f"{float(m.get('compatibility_score', 0)) * 100:.1f}%",
        )
        for m in matches
    ]
    show_table(
        "Mis matches",
        ["ID", "Origen", "Destino", "Estado", "Score"],
        rows,
    )


def render_compatibility_panel(result: dict[str, Any]) -> None:
    """Panel de compatibilidad en tiempo real."""
    score = result.get("compatibility_score") or result.get("score") or 0
    pct = float(score) * 100 if float(score) <= 1 else float(score)
    color = "green" if pct >= 70 else "yellow"
    console.print(
        Panel(
            f"[bold]{pct:.1f}%[/bold] de afinidad musical",
            title="Compatibilidad",
            border_style=color,
            expand=False,
        )
    )


def _demo() -> None:
    import getpass

    from src.auth.auth_client import AuthClient, AuthClientError
    from src.core.http_client import EncorelyHTTPClient
    from src.matches.matches_client import MatchesClient, MatchesClientError

    show_title("Encorely — Matches & Radar")
    username = input("Usuario: ").strip()
    password = getpass.getpass("Contraseña: ")

    http = EncorelyHTTPClient()
    auth = AuthClient(http_client=http)
    try:
        auth.login(username, password)
    except AuthClientError as exc:
        show_error(str(exc))
        return

    client = MatchesClient(http_client=http, session_manager=auth.session)
    try:
        show_info("Cargando radar...")
        radar = client.get_radar()
        render_radar_table(radar)
        show_info("Cargando matches...")
        render_matches_table(client.get_matches())
    except MatchesClientError as exc:
        show_error(str(exc))


if __name__ == "__main__":
    _demo()
