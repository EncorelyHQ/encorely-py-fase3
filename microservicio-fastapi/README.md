# Encorely · Microservicio de Compatibilidad (FastAPI)

Microservicio independiente que expone el cálculo de compatibilidad musical
(VibeCalculator) como servicio autónomo. Recibe dos *vibe vectors* y devuelve un
score de afinidad con su clasificación.

## Requisitos

- Python 3.10+
- Dependencias en [`requirements.txt`](requirements.txt)

## Instalación y ejecución local

```bash
cd microservicio-fastapi
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# copia y ajusta variables de entorno
cp .env.example .env

# arranca el servidor
uvicorn app.main:app --reload --port 8001
```

- Swagger UI: <http://localhost:8001/docs>
- ReDoc: <http://localhost:8001/redoc>

## Variables de entorno

| Variable  | Default       | Descripción                          |
|-----------|---------------|--------------------------------------|
| `APP_ENV` | `development` | Entorno de ejecución (informativo).  |
| `PORT`    | `8001`        | Puerto sugerido para uvicorn.        |

## Endpoints

### `GET /health`

Healthcheck liviano.

```json
{ "status": "ok" }
```

### `POST /compatibility/calculate`

Calcula la compatibilidad entre dos vibe vectors mediante similitud del coseno
(reescalada a `[0, 1]`).

**Request**

```json
{
  "vector_a": { "vector": [0.8, 0.6, 0.7] },
  "vector_b": { "vector": [0.7, 0.5, 0.6] }
}
```

**Response `200`**

```json
{
  "score": 0.9999,
  "score_percentage": 99.99,
  "classification": "COMPATIBLE",
  "threshold": 0.7
}
```

- `score`: similitud del coseno normalizada en `[0, 1]`.
- `classification`: `COMPATIBLE` si `score >= threshold`, si no `NOT_COMPATIBLE`.
- El umbral por defecto es `0.7` (`VibeCalculator.COMPATIBILITY_THRESHOLD`).

**Errores**

- `422`: vectores vacíos, de distinta dimensión, con norma cero, o payload inválido.

## Contrato con el cliente Python

El módulo Sound-Swipe del cliente (`cliente-python/src/swipe/`) consume este
servicio mediante `CompatibilityServiceClient`, que apunta a `FASTAPI_BASE_URL`.
Antes de confirmar un swipe RIGHT, `SwipeService` arma el vector del usuario
(desde `DNAClient`) y el de la canción (desde sus *audio features*, en el orden
de `AUDIO_FEATURE_KEYS`) y solicita el preview de score a este endpoint.

> Ambos vectores deben compartir el mismo esquema de features para que la
> comparación sea válida (misma dimensión y orden de componentes).

## Pruebas

```bash
cd microservicio-fastapi
pytest
```

Cubre el `VibeCalculator` (casos válidos, edge cases y errores) y los endpoints
vía `TestClient`.
