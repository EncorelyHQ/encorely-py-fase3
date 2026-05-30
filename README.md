# Encorely · Proyecto Final Integrador

Encorely es una plataforma social de **matchmaking musical**: conecta personas según
la afinidad de su "ADN musical" (vibe vector) y su *Concert Mood*. Este repositorio
reúne **las cuatro piezas del proyecto** (Fase 2 + Fase 3) en un solo monorepo.

## Mapeo con las fases

| Fase | Entregable | Carpeta |
|---|---|---|
| **Fase 2** — API con Django | Proyecto Django, modelos + migraciones, BD, endpoints REST (GET/POST/PUT/DELETE), Postman | [`api-django/`](api-django/) |
| **Fase 3** — Integrador | Cliente Python que consume la API | [`cliente-python/`](cliente-python/) |
| | Módulo de análisis de datos / IA | [`modelo-ia/`](modelo-ia/) |
| | Microservicio FastAPI | [`microservicio-fastapi/`](microservicio-fastapi/) |
| | CI con GitHub Actions | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |

## Estructura del repositorio

```
encorely-py-fase3/
├── api-django/              # FASE 2 — Backend REST (Django + DRF + JWT)
│   ├── apps/
│   │   ├── users/           # ← MODELOS (User, MusicVibeVector), auth JWT, admin
│   │   ├── music/           # Canciones, Swipes, algorithms.py (similitud coseno)
│   │   ├── matches/         # Radar de compatibilidad + services.py
│   │   ├── chat/            # Salas y mensajería
│   │   └── events/          # Conciertos y asistencia
│   │        ├── models.py        # ← los MODELOS de cada dominio
│   │        ├── views.py         # ← las VIEWS REST (ViewSets / APIViews)
│   │        ├── serializers.py   # validación y forma del JSON
│   │        ├── urls.py          # rutas /api/...
│   │        └── admin.py         # registro en el panel de admin
│   ├── config/              # settings.py, urls.py raíz
│   ├── frontend/            # ← FRONTEND WEB (login, swipe, radar, chat) HTML+CSS+JS
│   ├── fixtures/ · postman/ # datos de ejemplo y colecciones Postman
│   └── manage.py
│
├── cliente-python/          # Cliente CLI (Rich) que consume la API Django + microservicio
│   └── src/{core,auth,dna_core,swipe,matches,chat,events,ui}/
│
├── microservicio-fastapi/   # Microservicio de compatibilidad (VibeCalculator, coseno)
│   └── app/{routers,services,models}/
│
├── modelo-ia/               # Análisis de datos (pandas): estadísticas y reporte CSV
│   └── src/{data_loader,analyzer,report}.py
│
├── tests/                   # Suite del cliente CLI (pytest)
├── docs/                    # Documentación y colecciones
├── pyproject.toml           # ruff / black
└── .github/workflows/ci.yml # CI: ruff + tests de los 4 componentes
```

### ¿Dónde está cada cosa?

- **Modelos / base de datos** → `api-django/apps/<app>/models.py` (p. ej. `User` y
  `MusicVibeVector` en [users/models.py](api-django/apps/users/models.py)).
- **Views (endpoints REST)** → `api-django/apps/<app>/views.py`.
- **Frontend web (la "ventana" de login, swipe, radar…)** → `api-django/frontend/templates/` y `frontend/static/`.
- **Panel de administración** → Django Admin en `/admin/` (registros en cada `admin.py`).
- **La IA / algoritmo de afinidad** → vive en dos lugares complementarios:
  - [api-django/apps/music/algorithms.py](api-django/apps/music/algorithms.py) — similitud del coseno dentro del backend.
  - [microservicio-fastapi/app/services/vibe_calculator.py](microservicio-fastapi/app/services/vibe_calculator.py) — el mismo cálculo expuesto como servicio independiente.
- **Análisis de datos** → [modelo-ia/src/analyzer.py](modelo-ia/src/analyzer.py) (estadísticas sobre matches/swipes).

## Puesta en marcha (orden recomendado)

Requisitos: Python 3.11+. La API usa **SQLite** (sin Docker).

### 1. API Django (Fase 2) — puerto 8000

```bash
cd api-django
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # ajusta SECRET_KEY si quieres
python manage.py migrate
python manage.py seed_demo           # crea admin + 3 usuarios + canciones + swipes
python manage.py runserver           # http://localhost:8000
```

### 2. Microservicio FastAPI — puerto 8001

```bash
cd microservicio-fastapi
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

### 3. Cliente CLI

```bash
cd cliente-python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # DJANGO_API_BASE_URL=http://localhost:8000/api
python main.py
```

## Paso a paso visual (para la sustentación)

Con la API Django corriendo en `http://localhost:8000`:

1. **Login web** → abre `http://localhost:8000/` (o `/login/`). Entra con un usuario demo.
2. **Discover / Sound-Swipe** (`/swipe/`) → califica canciones (✅/❌); la barra de ADN avanza.
3. **Radar** (`/radar/`) → al superar 25 swipes se desbloquea; muestra usuarios compatibles.
4. **Matches & Chat** (`/chat/`) → conecta con un match y conversa (polling).
5. **Eventos** (`/events/`) → conciertos y asistencia.
6. **Panel de administración** → `http://localhost:8000/admin/` (entra con `admin`).
7. **Documentación interactiva de la API** → `http://localhost:8000/api/docs/` (Swagger).
8. **Cliente CLI** → en otra terminal, `python main.py` consume la misma API desde consola.

### Usuarios de demostración (`seed_demo`)

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Encorely2026!` | Administrador (acceso a `/admin/`) |
| `camilo` | `Encorely2026!` | Usuario (26 swipes, radar desbloqueado) |
| `juandiego` | `Encorely2026!` | Usuario (26 swipes) |
| `emmanuel` | `Encorely2026!` | Usuario (26 swipes) |

## Endpoints principales de la API

Todos bajo el prefijo `/api/` (detalle completo en `/api/docs/`):

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register/` · `/api/auth/login/` · `/api/auth/token/refresh/` | Registro y JWT |
| GET | `/api/auth/me/` | Perfil + ADN musical del usuario |
| GET/POST | `/api/songs/` · `/api/swipes/` | Canciones y swipes |
| GET | `/api/matches/radar/` · `/api/matches/compatibility/{id}/` | Radar y compatibilidad |
| GET/POST | `/api/chat/rooms/` · `/api/events/` | Chat y eventos |

## Tests y calidad

```bash
# Cliente CLI            → pytest (desde la raíz)
# API Django             → cd api-django && pytest
# Microservicio FastAPI  → cd microservicio-fastapi && pytest
ruff check .             # lint + orden de imports
```

El CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) ejecuta ruff y la suite de
los cuatro componentes en cada push y pull request.
