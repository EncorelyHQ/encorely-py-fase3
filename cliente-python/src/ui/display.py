from __future__ import annotations

from collections.abc import Iterable, Sequence

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def show_title(text: str) -> None:
    title = Text(text, style="bold cyan", justify="center")
    console.print(Panel(title, border_style="cyan", expand=False))


def show_success(message: str) -> None:
    console.print(f"[bold green]OK:[/bold green] {message}")


def show_error(message: str) -> None:
    console.print(f"[bold red]ERROR:[/bold red] {message}")


def show_info(message: str) -> None:
    console.print(f"[bold blue]INFO:[/bold blue] {message}")


def show_table(title: str, columns: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    table = Table(title=title, header_style="bold magenta", show_lines=False)

    for column in columns:
        table.add_column(column)

    for row in rows:
        table.add_row(*(str(value) for value in row))

    console.print(table)


def show_panel(title: str, content: str) -> None:
    panel = Panel(content, title=title, border_style="blue")
    console.print(panel)
