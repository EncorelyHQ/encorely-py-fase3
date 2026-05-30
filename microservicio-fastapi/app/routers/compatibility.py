from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import CompatibilityRequest, CompatibilityResponse
from app.services.vibe_calculator import VibeCalculator, VibeCalculatorError

router = APIRouter(prefix="/compatibility", tags=["compatibility"])


@router.post("/calculate", response_model=CompatibilityResponse)
def calculate_compatibility(payload: CompatibilityRequest) -> CompatibilityResponse:
    """Calcula la compatibilidad entre dos vibe vectors y la clasifica."""
    try:
        score = VibeCalculator.calculate(
            payload.vector_a.vector,
            payload.vector_b.vector,
        )
    except VibeCalculatorError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    threshold = VibeCalculator.COMPATIBILITY_THRESHOLD
    return CompatibilityResponse(
        score=round(score, 4),
        score_percentage=round(score * 100, 2),
        classification=VibeCalculator.classify(score, threshold),
        threshold=threshold,
    )
