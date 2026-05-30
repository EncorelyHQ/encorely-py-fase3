from __future__ import annotations

from typing import Any

from src.dna_core.dna_client import DNAClient
from src.swipe.compatibility_client import CompatibilityServiceClient
from src.swipe.swipe_client import SwipeClient, SwipeClientError, SwipeType
from src.swipe.swipe_view import AUDIO_FEATURE_KEYS


def song_to_vector(song: dict[str, Any]) -> list[float]:
    """Construye el vibe vector de una canción a partir de sus audio features.

    Usa el orden fijo de AUDIO_FEATURE_KEYS para que el vector sea comparable
    con el vector musical del usuario (mismo esquema de features).
    """
    nested = song.get("audio_features")
    source = nested if isinstance(nested, dict) else song
    vector = [float(source[key]) for key in AUDIO_FEATURE_KEYS if key in source]
    if not vector:
        raise SwipeClientError("La canción no expone audio features numéricas")
    return vector


class SwipeService:
    """Orquesta el flujo de Sound-Swipe con preview de compatibilidad.

    Antes de confirmar un swipe RIGHT consulta el microservicio FastAPI para
    mostrar el score de afinidad entre el usuario y la canción.
    """

    def __init__(
        self,
        swipe_client: SwipeClient | None = None,
        compatibility_client: CompatibilityServiceClient | None = None,
        dna_client: DNAClient | None = None,
    ) -> None:
        self.swipe_client = swipe_client or SwipeClient()
        self.compatibility_client = compatibility_client or CompatibilityServiceClient()
        self.dna_client = dna_client or DNAClient()
        self._cached_user_vector: list[float] | None = None

    def _user_vector(self) -> list[float]:
        if self._cached_user_vector is None:
            data = self.dna_client.get_music_vector()
            vector = data.get("music_vector")
            if not isinstance(vector, list) or not vector:
                raise SwipeClientError("No se pudo obtener el vector musical del usuario")
            self._cached_user_vector = [float(value) for value in vector]
        return self._cached_user_vector

    def preview_compatibility(self, song: dict[str, Any]) -> dict[str, Any]:
        """Calcula el preview de compatibilidad usuario ↔ canción."""
        return self.compatibility_client.calculate(
            self._user_vector(),
            song_to_vector(song),
        )

    def swipe_right(self, song: dict[str, Any]) -> dict[str, Any]:
        """Obtiene el preview de score y registra el swipe RIGHT."""
        preview = self.preview_compatibility(song)
        song_id = song.get("id")
        if song_id is None:
            raise SwipeClientError("La canción no tiene id para registrar el swipe")
        result = self.swipe_client.register_swipe(song_id, SwipeType.RIGHT)
        return {"preview": preview, "swipe": result}
