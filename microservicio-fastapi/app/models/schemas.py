from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Clasificaciones posibles que devuelve el cálculo de compatibilidad.
Classification = Literal["COMPATIBLE", "NOT_COMPATIBLE"]


class VibeVectorInput(BaseModel):
    """Vector musical (audio features) de un usuario o canción."""

    vector: list[float] = Field(
        ...,
        min_length=1,
        description="Componentes del vibe vector (p. ej. danceability, energy, valence).",
        examples=[[0.8, 0.6, 0.7, 0.5]],
    )

    @field_validator("vector")
    @classmethod
    def _reject_non_finite(cls, value: list[float]) -> list[float]:
        if any(component != component or component in (float("inf"), float("-inf")) for component in value):
            raise ValueError("El vector no admite valores NaN ni infinitos")
        return value


class CompatibilityRequest(BaseModel):
    """Par de vectores a comparar para obtener su compatibilidad."""

    vector_a: VibeVectorInput
    vector_b: VibeVectorInput


class CompatibilityResponse(BaseModel):
    """Resultado del cálculo de compatibilidad entre dos vectores."""

    score: float = Field(..., description="Similitud del coseno en el rango [0, 1].")
    score_percentage: float = Field(..., description="Score expresado como porcentaje [0, 100].")
    classification: Classification = Field(
        ...,
        description="COMPATIBLE si el score supera el umbral configurado, NOT_COMPATIBLE en caso contrario.",
    )
    threshold: float = Field(..., description="Umbral aplicado para la clasificación.")
