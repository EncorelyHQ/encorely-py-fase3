# Encorely — Documento Técnico

Plataforma social de **matchmaking musical**: conecta personas según la afinidad de
su "ADN musical" (vibe vector) y su *Concert Mood*. Este documento describe la
arquitectura, los modelos de datos, los endpoints, el algoritmo de IA, la seguridad,
las pruebas y las decisiones técnicas del proyecto.

---

## 1. Arquitectura

El sistema es un **monorepo con cuatro componentes desplegables de forma independiente**:

```
                       ┌──────────────────────────┐
                       │      api-django (8000)    │
                       │  Django + DRF + JWT        │
                       │  Web (login/swipe/radar)   │
                       │  /admin/ · /api/docs/      │
                       └───────┬───────────┬────────┘
                               │ REST/JWT  │ REST (login + datos)
            ┌──────────────────┘           └──────────────────┐
            ▼                                                  ▼
   ┌──────────────────┐                            ┌────────────────────┐
   │  cliente-python  │  REST (sin auth)           │     modelo-ia      │
   │  (CLI, Rich)     │ ─────────────────┐         │  (pandas, análisis)│
   └──────────────────┘                  ▼         └────────────────────┘
                               ┌────────────────────────┐
                               │ microservicio-fastapi  │
                               │ (8001) compatibilidad  │
                               └────────────────────────┘
```

| Componente | Rol | Stack |
|---|---|---|
| `api-django/` | Backend REST + frontend web + admin | Django 5.1, DRF, SimpleJWT, drf-spectacular |
| `cliente-python/` | Cliente CLI que consume la API y el microservicio | requests, rich, questionary |
| `microservicio-fastapi/` | Servicio de cálculo de compatibilidad | FastAPI, numpy, pydantic |
| `modelo-ia/` | Análisis de datos (estadísticas de matches/swipes) | pandas, numpy |

---

## 2. Modelos de datos (Django)

| App | Modelo | Campos clave |
|---|---|---|
| `users` | `User` (extiende `AbstractUser`) | `display_name`, `bio`, `city`, `concert_mood` (enum), `swipe_count`, `is_premium` |
| `users` | `MusicVibeVector` (1:1 con User) | `energy`, `danceability`, `valence`, `tempo`, `top_genres` |
| `music` | `Song` (mixin `AudioFeaturesMixin`) | `title`, `artist_name`, `energy`, `danceability`, `valence`, `tempo` |
| `music` | `Swipe` | `user`, `song`, `type` (RIGHT/LEFT), único por (user, song) |
| `matches` | `Friendship` | par ordenado `user_source`/`user_target`, `compatibility_score`, `status` |
| `chat` | `ChatRoom` | directa (`friendship`) o grupo (`is_group`, `name`, `participants` M2M) |
| `chat` | `Message` | `room`, `sender`, `content`, `sent_at`, `is_read` |
| `events` | `Event`, `EventAttendance` | conciertos y asistencia con flag de compatibilidad |

**Patrones aplicados:** Herencia (`User`/`AbstractUser`, `AudioFeaturesMixin`),
Composición (`MusicVibeVector`), Enum (`ConcertMood`, `SwipeType`, `FriendshipStatus`),
Observer (signals), Service Layer (`MatchService`, `UserService`), Strategy (`VibeCalculator`).

---

## 3. Endpoints principales (prefijo `/api/`)

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/auth/register/` | Registro (throttling `auth`) |
| POST | `/api/auth/login/` | Login JWT (throttling `auth`) |
| POST | `/api/auth/token/refresh/` | Renovar access token |
| GET/PATCH | `/api/auth/me/` | Perfil + ADN musical |
| GET/POST | `/api/songs/` · `/api/swipes/` | Catálogo y registro de swipes |
| GET | `/api/matches/radar/` | Sugerencias por IA (score > 0.70, requiere 25 swipes) |
| GET | `/api/matches/compatibility/{id}/` | Score en tiempo real con otro usuario |
| GET/POST | `/api/chat/rooms/` | Listar salas / crear grupo |
| GET/POST | `/api/chat/rooms/{id}/messages/` | Mensajes de una sala |
| GET/POST | `/api/events/` · `/api/events/{id}/attend/` | Eventos y asistencia |

Documentación interactiva: **`/api/docs/`** (Swagger / OpenAPI 3).

---

## 4. El algoritmo de IA (compatibilidad)

La afinidad entre dos usuarios se calcula con **similitud del coseno** sobre las 4
dimensiones del ADN musical (`energy`, `danceability`, `valence`, `tempo`):

```
similitud(A, B) = (A · B) / (‖A‖ · ‖B‖)   ∈ [0, 1]
```

- El ADN de cada usuario (`MusicVibeVector`) se **recalcula automáticamente** (signal
  `post_save` de `Swipe`) como el promedio de los audio features de sus swipes RIGHT.
  Es decir: **mientras más deslizas, más se afina tu perfil**.
- Umbral de match: `0.70`. El Radar se desbloquea a los **25 swipes**.

---

## 5. Seguridad

- **Autenticación:** JWT (SimpleJWT) con rotación de refresh tokens y blacklist tras
  rotación. Access 60 min, refresh 7 días.
- **Throttling:** `auth` 10/min en login/registro (anti fuerza bruta), `anon` 60/min,
  `user` 1000/min.
- **Permisos:** `IsAuthenticated` por defecto; `IsChatParticipant` valida pertenencia a
  la sala (directa o grupo) por la relación `participants`.
- **CORS:** restringido a orígenes conocidos (configurable por env) tanto en Django como
  en el microservicio.
- **Refresh transparente:** el frontend web (`api.js`) y el cliente CLI renuevan el token
  automáticamente ante un 401 y reintentan la petición.

---

## 6. Pruebas y CI

- **api-django:** `pytest` + `pytest-django` (algoritmo, modelos, API de usuarios,
  servicios de matches, chat grupal y permisos).
- **cliente-python:** `pytest` (auth, dna, swipe, http client con refresh).
- **microservicio-fastapi:** `pytest` (VibeCalculator y endpoint de compatibilidad).
- **CI** (`.github/workflows/ci.yml`): ruff + las suites de los cuatro componentes en
  cada push y pull request.

---

## 7. Decisiones técnicas

**¿Por qué la fórmula de compatibilidad está duplicada (Django y microservicio)?**
Es intencional. Django y el microservicio son **servicios desplegables independientes**;
acoplarlos con un paquete compartido anularía el propósito de tener un microservicio.
Django usa su copia (`apps/music/algorithms.py`) para el Radar interno, mientras el
microservicio (`vibe_calculator.py`) expone el cálculo como **servicio autónomo para
clientes externos** (lo consume el cliente CLI antes de un swipe). Se evitó deliberadamente
que Django delegue vía HTTP en el microservicio, porque agregaría latencia y un punto de
fallo nuevo al camino crítico del Radar.

**¿Por qué `/api/songs/` no pagina?** El mazo de Sound-Swipe necesita el lote disponible
de una vez; el `queryset` ya excluye las canciones que el usuario evaluó, acotando el tamaño.

**Chat en "tiempo real".** Implementado con **polling** (cada 3 s) en lugar de WebSockets,
suficiente para el alcance del proyecto y sin infraestructura adicional (Channels/Redis).

---

## 8. Trabajo futuro

- Configuración de producción (whitenoise para estáticos, `SECRET_KEY` obligatoria,
  base de datos PostgreSQL).
- Chat por WebSockets (Django Channels) en lugar de polling.
- Refactor del frontend: extraer estilos inline a clases en `encorely.css`.
- Cobertura de pruebas en CI y linting del código Django.

---

## 9. Cómo ejecutar y credenciales de demo

Ver [README.md](../README.md) para la puesta en marcha. Usuarios sembrados por
`python manage.py seed_demo` (contraseña `Encorely2026!`): `admin` (administrador),
`camilo`, `juandiego`, `emmanuel`.
