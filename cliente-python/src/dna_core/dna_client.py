from __future__ import annotations

from typing import Any

from src.auth.session import SessionManager
from src.core.http_client import EncorelyHTTPClient, EncorelyHTTPClientError

# Orden canónico de las dimensiones del ADN musical (coincide con MusicVibeVector
# y los audio features de las canciones en la API Django).
DNA_FEATURE_KEYS = ("energy", "danceability", "valence", "tempo")


class DNAClientError(Exception):
    """Error del cliente DNA para flujos autenticados."""


class DNAClient:
    def __init__(
        self,
        http_client: EncorelyHTTPClient | None = None,
        session_manager: SessionManager | None = None,
    ) -> None:
        self.http_client = http_client or EncorelyHTTPClient()
        self.session = session_manager or SessionManager()

    def get_music_vector(self) -> dict[str, Any]:
        """Obtiene el vector musical del usuario autenticado en formato amigable para UI."""
        token = self.session.get_access_token()
        if not token:
            raise DNAClientError("No existe una sesion activa con access token")

        headers = {"Authorization": f"Bearer {token}"}

        try:
            me_response = self.http_client.get("/auth/me/", headers=headers)
            me_data = self._response_json(me_response)
        except EncorelyHTTPClientError as exc:
            raise DNAClientError(f"No se pudo obtener el usuario autenticado: {exc}") from exc

        user_id = me_data.get("id")

        # Si /auth/me/ ya incluye la informacion de DNA/vibe, se reutiliza sin otra llamada.
        embedded_vector = self._extract_vector(me_data)
        if embedded_vector is not None:
            return {
                "user": {
                    "id": user_id,
                    "username": me_data.get("username"),
                },
                "music_vector": embedded_vector,
                "source": "/auth/me/",
            }

        if user_id is None:
            raise DNAClientError("No fue posible resolver user_id desde /auth/me/")

        try:
            vibe_response = self.http_client.get(f"/users/{user_id}/vibe/", headers=headers)
            vibe_data = self._response_json(vibe_response)
        except EncorelyHTTPClientError as exc:
            raise DNAClientError(f"No se pudo obtener el vector musical: {exc}") from exc

        extracted_vector = self._extract_vector(vibe_data)
        if extracted_vector is None:
            raise DNAClientError("La respuesta de /users/{id}/vibe/ no contiene vector musical")

        return {
            "user": {
                "id": user_id,
                "username": me_data.get("username"),
            },
            "music_vector": extracted_vector,
            "source": f"/users/{user_id}/vibe/",
        }

    def _extract_vector(self, payload: dict[str, Any]) -> list[float] | None:
        for key in ("music_vector", "vibe_vector", "vector", "dna_vector"):
            raw_vector = payload.get(key)
            if isinstance(raw_vector, list):
                try:
                    return [float(value) for value in raw_vector]
                except (TypeError, ValueError):
                    return None
            # La API Django expone el ADN como objeto {energy, danceability, ...};
            # se ordena según DNA_FEATURE_KEYS para obtener un vector comparable.
            if isinstance(raw_vector, dict):
                ordered = [raw_vector[k] for k in DNA_FEATURE_KEYS if k in raw_vector]
                if ordered:
                    try:
                        return [float(value) for value in ordered]
                    except (TypeError, ValueError):
                        return None
        return None

    def _response_json(self, response: Any) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise DNAClientError("La respuesta del servidor no es JSON valido") from exc

        if not isinstance(payload, dict):
            raise DNAClientError("Formato de respuesta no soportado: se esperaba objeto JSON")

        return payload
