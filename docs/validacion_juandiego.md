# Validación funcional — Juan Diego Calle

Checklist reproducible para los módulos Matches, Chat, Events y modelo-ia.

## Prerrequisitos

1. EncorelyDjango corriendo en `http://localhost:8000`
2. Variables en `cliente-python/.env`:
   ```env
   DJANGO_API_BASE_URL=http://localhost:8000/api
   ```
3. Variables en `modelo-ia/.env`:
   ```env
   DJANGO_API_BASE_URL=http://localhost:8000/api
   DJANGO_USERNAME=demo
   DJANGO_PASSWORD=<tu_password>
   ```

## Flujo de validación

### 1. Autenticación

```bash
# Postman: Auth → Login
POST http://localhost:8000/api/auth/login/
Body: {"username": "demo", "password": "..."}
```

Copiar `access` a la variable de colección.

### 2. Matches y Radar

- [ ] `GET /api/matches/radar/` muestra sugerencias con `compatibility_score >= 0.70` (requiere 25+ swipes)
- [ ] `POST /api/matches/` con `{"other_user_id": N}` crea solicitud
- [ ] `PATCH /api/matches/{id}/` con `{"status": "accepted"}` acepta match

**Cliente CLI:**

```bash
cd cliente-python
PYTHONPATH=. python -m src.matches.matches_view
```

### 3. Chat con polling

- [ ] `GET /api/chat/rooms/` lista salas tras match aceptado
- [ ] `POST /api/chat/rooms/{room_id}/messages/` envía mensaje
- [ ] Polling cada 3s muestra mensajes nuevos sin reiniciar

**Cliente CLI:**

```bash
cd cliente-python
PYTHONPATH=. python -m src.chat.chat_view
```

### 4. Eventos por ciudad

- [ ] `GET /api/events/?city=Medellín` filtra eventos
- [ ] `POST /api/events/{id}/attend/` registra asistencia
- [ ] `GET /api/events/{id}/attendees/` muestra compatibilidad

**Cliente CLI:**

```bash
cd cliente-python
PYTHONPATH=. python -m src.events.events_view
```

### 5. Reporte IA

```bash
cd modelo-ia
python src/report.py
```

- [ ] Imprime resumen en consola con Rich
- [ ] Genera `docs/reporte_compatibilidad.csv`

### 6. Tests automatizados

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r cliente-python/requirements.txt -r tests/requirements.txt
pytest tests/ -v
```

- [ ] 18 tests pasan sin errores

## Colección Postman

Importar [`postman_collection.json`](postman_collection.json) en Postman o usar el MCP de Postman.
