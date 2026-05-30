from __future__ import annotations

from typing import Any

import pandas as pd


def compatibility_score_distribution(matches_df: pd.DataFrame) -> dict[str, Any]:
    """Resumen estadístico de scores de compatibilidad en friendships."""
    if matches_df.empty or "compatibility_score" not in matches_df.columns:
        return {"count": 0, "mean": None, "min": None, "max": None, "bins": {}}

    scores = pd.to_numeric(matches_df["compatibility_score"], errors="coerce").dropna()
    if scores.empty:
        return {"count": 0, "mean": None, "min": None, "max": None, "bins": {}}

    bins = pd.cut(scores, bins=[0, 0.5, 0.7, 0.85, 1.0], include_lowest=True)
    bin_counts = bins.value_counts().sort_index()
    return {
        "count": int(scores.count()),
        "mean": round(float(scores.mean()), 4),
        "min": round(float(scores.min()), 4),
        "max": round(float(scores.max()), 4),
        "bins": {str(k): int(v) for k, v in bin_counts.items()},
    }


def top_genres_in_accepted_matches(
    matches_df: pd.DataFrame,
    users_df: pd.DataFrame,
    top_n: int = 10,
) -> list[dict[str, Any]]:
    """Géneros más frecuentes entre usuarios con matches aceptados."""
    if matches_df.empty or users_df.empty:
        return []

    accepted = matches_df[matches_df.get("status", pd.Series(dtype=str)) == "accepted"]
    if accepted.empty:
        return []

    user_genres: dict[Any, list[str]] = {}
    for _, row in users_df.iterrows():
        uid = row.get("id")
        vibe = row.get("vibe_vector")
        if isinstance(vibe, dict):
            genres = vibe.get("top_genres") or []
        else:
            genres = row.get("vibe_vector.top_genres") or []
        if uid is not None and isinstance(genres, list):
            user_genres[uid] = [str(g) for g in genres]

    genre_counts: dict[str, int] = {}
    for _, match in accepted.iterrows():
        for col in ("user_source.id", "user_target.id", "user_source", "user_target"):
            if col not in match:
                continue
            val = match[col]
            user_id = val.get("id") if isinstance(val, dict) else val
            for genre in user_genres.get(user_id, []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

    ranked = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"genre": g, "count": c} for g, c in ranked]


def top_users_by_swipes(users_df: pd.DataFrame, top_n: int = 10) -> list[dict[str, Any]]:
    """Usuarios con mayor actividad de swipes."""
    if users_df.empty or "swipe_count" not in users_df.columns:
        return []

    ranked = (
        users_df.sort_values("swipe_count", ascending=False)
        .head(top_n)[["id", "username", "swipe_count"]]
        .fillna("")
    )
    return ranked.to_dict(orient="records")


def run_full_analysis(data: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Ejecuta todas las métricas y retorna resultados estructurados."""
    matches_df = data.get("matches", pd.DataFrame())
    users_df = data.get("users", pd.DataFrame())
    swipes_df = data.get("swipes", pd.DataFrame())

    return {
        "compatibility_distribution": compatibility_score_distribution(matches_df),
        "top_genres_accepted": top_genres_in_accepted_matches(matches_df, users_df),
        "top_users_by_swipes": top_users_by_swipes(users_df),
        "total_swipes_recorded": len(swipes_df),
        "total_matches": len(matches_df),
        "total_users": len(users_df),
    }
