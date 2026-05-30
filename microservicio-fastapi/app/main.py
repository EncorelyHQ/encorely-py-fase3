from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import compatibility

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

# CORS abierto en desarrollo: el cliente Python y la API Django consumen este servicio
# desde orígenes distintos. En producción debe restringirse a hosts conocidos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(compatibility.router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "service": "encorely-compatibility",
        "version": app.version,
        "environment": APP_ENV,
    }
