from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn
from rich.table import Table

from src.swipe.swipe_client import SWIPE_GOAL
from src.ui.display import console

# Claves de audio features conocidas que Spotify/Encorely expone por canción.
AUDIO_FEATURE_KEYS = (
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "tempo",
)


def _extract_features(song: dict[str, Any]) -> dict[str, Any]:
    """Soporta features anidadas en `audio_features` o planas en la canción."""
    nested = song.get("audio_features")
    source = nested if isinstance(nested, dict) else song
    return {key: source[key] for key in AUDIO_FEATURE_KEYS if key in source}


def render_song_card(song: dict[str, Any]) -> None:
    """Muestra la tarjeta de una canción con sus audio features."""
    title = song.get("title") or song.get("name") or "Canción sin título"
    artist = song.get("artist") or song.get("artist_name") or "Artista desconocido"

    features = _extract_features(song)
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column(style="bold cyan")
    table.add_column()
    if features:
        for key, value in features.items():
            table.add_row(key, str(value))
    else:
        table.add_row("audio features", "no disponibles")

    console.print(
        Panel(
            table,
            title=f"🎵 {title} — {artist}",
            border_style="magenta",
            expand=False,
        )
    )


def render_swipe_progress(current: int, goal: int = SWIPE_GOAL) -> None:
    """Renderiza una barra de progreso del avance hacia el umbral de swipes."""
    bounded = min(current, goal)
    with Progress(
        TextColumn("[bold blue]Swipes[/bold blue]"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TextColumn("hacia el objetivo"),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("swipes", total=goal)
        progress.update(task, completed=bounded)

    if current >= goal:
        console.print("[bold green]¡Objetivo de swipes alcanzado![/bold green]")


def render_compatibility_preview(result: dict[str, Any]) -> None:
    """Muestra el preview de compatibilidad devuelto por el microservicio."""
    classification = result.get("classification", "DESCONOCIDO")
    percentage = result.get("score_percentage", 0)
    color = "green" if classification == "COMPATIBLE" else "yellow"
    console.print(
        Panel(
            f"[bold]{percentage}%[/bold] de afinidad — [bold {color}]{classification}[/bold {color}]",
            title="Preview de compatibilidad",
            border_style=color,
            expand=False,
        )
    )
