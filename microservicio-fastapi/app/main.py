from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import compatibility, health

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Encorely · Microservicio de Compatibilidad",
    version="1.0.0",
    description=(
        "Microservicio independiente que expone el cálculo de compatibilidad "
        "musical (VibeCalculator) como servicio autónomo para el ecosistema Encorely."
    ),
)

# CORS restringido a orígenes conocidos (configurable por env). Evita el anti-patrón
# de allow_origins=["*"] junto a allow_credentials=True, que los navegadores rechazan.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router)
app.include_router(compatibility.router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "service": "encorely-compatibility",
        "version": app.version,
        "environment": APP_ENV,
    }
