# Encorely · Fase 3

Encorely es una app de afinidad musical: empareja personas según la similitud de sus
gustos (su *vibe vector*). Este repositorio agrupa las piezas Python de la **Fase 3**
que consumen y complementan la API Django del proyecto, organizadas en tres
subproyectos independientes:

| Subproyecto | Rol | Stack |
|---|---|---|
| [`cliente-python/`](cliente-python/) | Aplicación CLI interactiva que consume la API Django (auth, DNA Core, Sound-Swipe, Matches, Chat, Events) | requests · rich · questionary |
| [`microservicio-fastapi/`](microservicio-fastapi/) | Microservicio autónomo que expone el cálculo de compatibilidad (`VibeCalculator`) | FastAPI · numpy · pydantic |
| [`modelo-ia/`](modelo-ia/) | Scripts de análisis que extraen datos de Django y generan estadísticas/reporte de compatibilidad | pandas · numpy |

## Arquitectura

```
                 ┌────────────────────┐
                 │   API Django (ext.) │
                 └─────────┬──────────┘
                           │ JWT
        ┌──────────────────┼───────────────────┐
        │                  │                    │
 ┌──────▼──────┐   ┌───────▼───────┐    ┌───────▼────────┐
 │ cliente-py  │   │  modelo-ia    │    │ microservicio  │
 │  (CLI)      │──▶│  (análisis)   │    │  FastAPI       │
 └──────┬──────┘   └───────────────┘    └───────▲────────┘
        │            preview de compatibilidad   │
        └────────────────────────────────────────┘
```

El cliente CLI consulta la API Django para autenticarse y operar, y llama al
microservicio FastAPI para previsualizar el score de compatibilidad antes de un swipe.

## Requisitos

- Python 3.11 o superior.
- `pip` y `venv` disponibles.

## Puesta en marcha rápida

Cada subproyecto se ejecuta de forma independiente. El orden habitual para una demo
completa es: **microservicio FastAPI → cliente CLI**.

### 1. Microservicio de compatibilidad

```bash
cd microservicio-fastapi
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

Detalle de endpoints y contrato JSON en [microservicio-fastapi/README.md](microservicio-fastapi/README.md).

### 2. Cliente CLI

```bash
cd cliente-python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ajusta DJANGO_API_BASE_URL y FASTAPI_BASE_URL
python main.py
```

El menú principal expone: Login, Registro, DNA Core, **Sound Swipe**, **Matches**,
**Chat** y **Events** (todos integrados contra la API Django).

### 3. Módulo de análisis (opcional)

```bash
cd modelo-ia
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # define DJANGO_USERNAME y DJANGO_PASSWORD
```

## Variables de entorno

`cliente-python/.env`:

```env
ENCORELY_ENV=development
DJANGO_API_BASE_URL=http://localhost:8000
FASTAPI_BASE_URL=http://localhost:8001
REQUEST_TIMEOUT=10
```

Cada subproyecto trae su propio `.env.example` como referencia. Los `.env` reales
están en `.gitignore` y nunca se versionan.

## Tests

```bash
# Cliente CLI (desde la raíz; usa pytest.ini)
pip install -r cliente-python/requirements.txt -r tests/requirements.txt
pytest

# Microservicio FastAPI
cd microservicio-fastapi && pytest
```

## Calidad de código

Linter y formateador configurados en [`pyproject.toml`](pyproject.toml):

```bash
ruff check .     # lint + orden de imports
ruff format .    # formateo (compatible con black)
```

El workflow de CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) corre ruff,
los tests del cliente y del microservicio, y compila el módulo de análisis en cada
push y pull request.
