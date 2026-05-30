from __future__ import annotations

import csv
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
DOCS_DIR = REPO_ROOT / "docs"
CSV_PATH = DOCS_DIR / "reporte_compatibilidad.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analyzer import run_full_analysis  # noqa: E402
from src.data_loader import DataLoaderError, load_all_dataframes  # noqa: E402

console = Console()


def _print_summary(results: dict) -> None:
    dist = results["compatibility_distribution"]
    console.print(Panel(
        f"Matches: {results['total_matches']} | Usuarios: {results['total_users']} | "
        f"Swipes registrados: {results['total_swipes_recorded']}",
        title="Encorely — Reporte de compatibilidad",
        border_style="cyan",
    ))

    score_table = Table(title="Distribución de scores", header_style="bold magenta")
    score_table.add_column("Métrica")
    score_table.add_column("Valor")
    score_table.add_row("Cantidad", str(dist.get("count", 0)))
    score_table.add_row("Media", str(dist.get("mean", "N/A")))
    score_table.add_row("Mínimo", str(dist.get("min", "N/A")))
    score_table.add_row("Máximo", str(dist.get("max", "N/A")))
    console.print(score_table)

    genres_table = Table(title="Géneros en matches aceptados", header_style="bold magenta")
    genres_table.add_column("Género")
    genres_table.add_column("Frecuencia")
    for item in results.get("top_genres_accepted", []):
        genres_table.add_row(str(item.get("genre", "")), str(item.get("count", 0)))
    if not results.get("top_genres_accepted"):
        genres_table.add_row("(sin datos)", "0")
    console.print(genres_table)

    users_table = Table(title="Top usuarios por swipes", header_style="bold magenta")
    users_table.add_column("ID")
    users_table.add_column("Username")
    users_table.add_column("Swipes")
    for item in results.get("top_users_by_swipes", []):
        users_table.add_row(
            str(item.get("id", "")),
            str(item.get("username", "")),
            str(item.get("swipe_count", 0)),
        )
    if not results.get("top_users_by_swipes"):
        users_table.add_row("(sin datos)", "", "0")
    console.print(users_table)


def _export_csv(results: dict) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []

    dist = results["compatibility_distribution"]
    rows.append({"seccion": "compatibilidad", "metrica": "count", "valor": str(dist.get("count", 0))})
    rows.append({"seccion": "compatibilidad", "metrica": "mean", "valor": str(dist.get("mean", ""))})
    rows.append({"seccion": "compatibilidad", "metrica": "min", "valor": str(dist.get("min", ""))})
    rows.append({"seccion": "compatibilidad", "metrica": "max", "valor": str(dist.get("max", ""))})

    for item in results.get("top_genres_accepted", []):
        rows.append({
            "seccion": "genero",
            "metrica": str(item.get("genre", "")),
            "valor": str(item.get("count", 0)),
        })

    for item in results.get("top_users_by_swipes", []):
        rows.append({
            "seccion": "usuario_swipes",
            "metrica": str(item.get("username", "")),
            "valor": str(item.get("swipe_count", 0)),
        })

    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["seccion", "metrica", "valor"])
        writer.writeheader()
        writer.writerows(rows)

    return CSV_PATH


def main() -> None:
    try:
        data = load_all_dataframes()
        results = run_full_analysis(data)
    except DataLoaderError as exc:
        console.print(f"[bold red]ERROR:[/bold red] {exc}")
        sys.exit(1)

    _print_summary(results)
    csv_path = _export_csv(results)
    console.print(f"[bold green]OK:[/bold green] Reporte exportado a {csv_path}")


if __name__ == "__main__":
    main()
