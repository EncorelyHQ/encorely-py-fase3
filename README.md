# Encorely Fase 3

Este repositorio contiene el cliente Python de Encorely para la Fase 3, organizado como un subproyecto en `cliente-python/`.

## Requisitos previos

- Python 3.11 o superior.
- `pip` disponible en el entorno local.
- Git para clonar y actualizar el repositorio.

## Estructura principal

- `cliente-python/main.py`: punto de entrada de la aplicación CLI.
- `cliente-python/src/core/`: configuración centralizada y cliente HTTP compartido.
- `cliente-python/src/auth/`: sesión en memoria y cliente de autenticación.
- `cliente-python/src/dna_core/`: consulta del vector musical del usuario autenticado.
- `cliente-python/src/ui/`: utilidades de pantalla, prompts y menú principal.
- `cliente-python/src/swipe/`, `cliente-python/src/matches/`, `cliente-python/src/chat/`, `cliente-python/src/events/`: módulos reservados para futuras integraciones.

## Crear el entorno virtual

Desde la raíz del repositorio:

```bash
python -m venv .venv
```

Activar el entorno virtual:

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

En Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

## Instalar dependencias

Con el entorno virtual activado, instala las dependencias del cliente:

```bash
pip install -r cliente-python/requirements.txt
```

## Configurar variables de entorno

Dentro de `cliente-python/` existe el archivo `.env.example`. Úsalo como base para crear tu archivo real `.env`.

Variables disponibles:

```env
ENCORELY_ENV=development
DJANGO_API_BASE_URL=http://localhost:8000
FASTAPI_BASE_URL=http://localhost:8001
REQUEST_TIMEOUT=10
```

Copia el ejemplo y ajusta los valores según tu entorno:

```bash
copy cliente-python\.env.example cliente-python\.env
```

En PowerShell también puedes usar:

```powershell
Copy-Item cliente-python\.env.example cliente-python\.env
```

## Ejecutar el cliente

Ejecuta la aplicación desde la carpeta `cliente-python/`:

```bash
cd cliente-python
python main.py
```

La aplicación mostrará una bienvenida inicial y abrirá el menú principal interactivo.

## Módulos disponibles

- `core`: agrupa la configuración y la capa HTTP reutilizable.
- `auth`: maneja login, registro, refresh y sesión en memoria.
- `dna_core`: consulta el vector musical del usuario autenticado.
- `ui`: concentra la experiencia CLI con pantalla, prompts y navegación principal.

Los módulos de `swipe`, `matches`, `chat` y `events` están preparados como base de integración y aún no contienen lógica funcional completa.

## Validación básica

Si quieres comprobar que el proyecto está bien formado, puedes usar:

```bash
python -m compileall cliente-python
```

## Notas

- El cliente CLI está pensado para consumir la API Django existente.
- Los endpoints y el comportamiento pueden evolucionar a medida que los módulos del equipo se integren.
