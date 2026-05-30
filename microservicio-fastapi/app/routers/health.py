from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Endpoint liviano para verificar la disponibilidad del servicio."""
    return {"status": "ok"}
