from __future__ import annotations

from collections.abc import Sequence

import numpy as np


class VibeCalculatorError(ValueError):
    """Error de dominio cuando los vectores de entrada son inválidos."""


class VibeCalculator:
    """Cálculo de compatibilidad musical mediante similitud del coseno.

    Portado desde la Fase 2. La similitud del coseno mide el ángulo entre dos
    vectores de audio features; valores cercanos a 1 implican gustos afines.
    """

    # Umbral por defecto sobre el score normalizado [0, 1] para clasificar como COMPATIBLE.
    COMPATIBILITY_THRESHOLD: float = 0.7

    @staticmethod
    def calculate(vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
        """Devuelve la similitud del coseno normalizada al rango [0, 1].

        El coseno vive en [-1, 1]; se reescala a [0, 1] para usarlo como score
        de compatibilidad legible (0 = opuestos, 1 = idénticos en dirección).
        """
        a = np.asarray(vector_a, dtype=float)
        b = np.asarray(vector_b, dtype=float)

        if a.ndim != 1 or b.ndim != 1:
            raise VibeCalculatorError("Los vectores deben ser unidimensionales")
        if a.size == 0 or b.size == 0:
            raise VibeCalculatorError("Los vectores no pueden estar vacíos")
        if a.size != b.size:
            raise VibeCalculatorError(
                f"Los vectores deben tener la misma dimensión (a={a.size}, b={b.size})"
            )

        norm_a = float(np.linalg.norm(a))
        norm_b = float(np.linalg.norm(b))
        if norm_a == 0.0 or norm_b == 0.0:
            raise VibeCalculatorError("Un vector con norma cero no admite similitud del coseno")

        cosine = float(np.dot(a, b) / (norm_a * norm_b))
        # Reescala [-1, 1] -> [0, 1] y recorta por errores de punto flotante.
        normalized = (cosine + 1.0) / 2.0
        return float(np.clip(normalized, 0.0, 1.0))

    @classmethod
    def classify(cls, score: float, threshold: float | None = None) -> str:
        applied_threshold = cls.COMPATIBILITY_THRESHOLD if threshold is None else threshold
        return "COMPATIBLE" if score >= applied_threshold else "NOT_COMPATIBLE"
