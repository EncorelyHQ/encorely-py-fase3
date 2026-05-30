# 🎵 Encorely Django Backend & MVP Frontend

![Encorely Banner](https://images.unsplash.com/photo-1459749411175-04bf5292ceea?auto=format&fit=crop&w=1200&q=80)

Encorely es una plataforma social de **matchmaking musical** diseñada para conectar personas a través de su afinidad en gustos musicales y estilos de asistencia a conciertos (*Concert Mood*). Este repositorio alberga el backend (API REST) construido en Django y el Módulo Frontend (MVP visual) para demostrar el flujo completo.

---

## 🚀 Características Principales

### 1. Backend API (Django REST Framework)
- **Autenticación Segura**: Implementación de JSON Web Tokens (JWT) con rotación de refresh tokens (`SimpleJWT`).
- **Arquitectura Modular**: Dividido funcionalmente en 5 aplicaciones independientes (`users`, `music`, `matches`, `chat`, `events`).
- **DNA Musical Reactivo**: Sistema de actualización en tiempo real que recalcula el perfil musical del usuario tras cada interacción (*swipe* RIGHT).
- **ADN Musical (MusicVibeVector)**: Un modelo de composición orientado a objetos que almacena métricas acústicas (`energy`, `danceability`, `valence`, `tempo`) para calcular afinidad algorítmica.
- **Documentación Dinámica**: OpenAPI 3 y Swagger UI completamente funcionales en la ruta `/api/docs/`.
- **Panel Administrativo Premium**: Secciones personalizadas para gestionar perfiles y estadísticas directamente desde el Django Admin.

### 2. Frontend MVP (HTML, CSS Neón, Vanilla JS)
- **Tema Oscuro Dinámico**: Estética premium basada en el Manual de Marca usando colores Neón (*Purple, Blue, Pink, Green*).
- **Patrón Facade (`api.js`)**: Cliente HTTP centralizado que maneja automáticamente las peticiones `fetch()` y la inyección transparente del token de sesión JWT.
- **Sound-Swipe**: Interfaz estilo Tinder con animaciones CSS avanzadas en 3D para calificar canciones y llenar tu barra de progreso musical.
- **Radar & Matches**: Cuadrícula de afinidad basada en porcentaje con sistema de conexión simulado y bloqueo lógico (si no has definido tu música).
- **Chat en Tiempo Real Simulado**: Interfaz de mensajería bidireccional que integra auto-scroll y *polling* de datos.

---

## 🛠️ Stack Tecnológico

**Backend:**
- Python 3.10+
- Django 5.1
- Django REST Framework (DRF)
- djangorestframework-simplejwt (Autenticación)
- drf-spectacular (Swagger Docs)
- django-cors-headers

**Frontend:**
- HTML5
- CSS3 Nativo (Variables de entorno, UI responsiva)
- Vanilla JavaScript (ES6+ async/await, DOM Manipulation)
- Google Fonts (Outfit, Inter)

---

## 📂 Estructura del Proyecto

```text
EncorelyDjango/
├── apps/
│   ├── users/        # Modelos (User, MusicVibeVector), Serializers y JWT Views
│   ├── music/        # Algoritmos, Canciones y Swipes (Próxima etapa)
│   ├── matches/      # Sistema de compatibilidad Radar (Próxima etapa)
│   ├── chat/         # Salas de chat y mensajería (Próxima etapa)
│   └── events/       # Conciertos y festivales (Próxima etapa)
├── config/           # Configuraciones base de Django y urls.py principal
├── frontend/
│   ├── static/       # Estilos CSS y utilidades JS (api.js, auth.js, swipe.js)
│   └── templates/    # Layout base y pantallas renderizadas vía TemplateView
├── requirements.txt  # Listado estricto de dependencias de Python
└── manage.py
```

---

## 💻 Instalación y Uso Local

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/EncorelyHQ/EncorelyDjango.git
   cd EncorelyDjango
   ```

2. **Crear y activar el entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   venv\Scripts\activate     # En Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno**
   - Crea un archivo `.env` en la raíz basándote en el modelo de `.env.example`.

5. **Aplicar migraciones de Base de Datos**
   ```bash
   python manage.py migrate
   ```

6. **Ejecutar el Servidor de Desarrollo**
   ```bash
   python manage.py runserver
   ```
   
> **Rutas disponibles:**
> - **Aplicación Web (MVP):** `http://localhost:8000/`
> - **Documentación API:** `http://localhost:8000/api/docs/`
> - **Django Admin:** `http://localhost:8000/admin/`
102: 
103: ---
104: 
105: ## 🧪 Pruebas Automatizadas (Pytest)
106: 
107: El proyecto incluye una suite de pruebas profesional para garantizar la integridad de los algoritmos y la lógica de negocio:
108: 
109: ```bash
110: # Ejecutar todos los tests
111: python3 -m pytest
112: 
113: # Ejecutar con reporte detallado
114: python3 -m pytest -v
115: ```
116: 
117: **Áreas cubiertas:**
118: - `music.algorithms`: Validación matemática de la Similitud del Coseno.
119: - `music.models`: Ciclo de vida de Swipes y señales de actualización de ADN.
120: - `users.api`: Flujos de registro y autenticación JWT.
121: - `matches.services`: Lógica de sugerencias y cálculo de compatibilidad.

---

## 🛣️ Prueba del Flujo de Usuario (End-to-End)

Para probar la navegación implementada en el Módulo Frontend:
1. Accede a **`http://localhost:8000/register/`** y crea una nueva cuenta.
2. Serás redirigido a **Discover (`/swipe/`)**. Califica la música (✅ o ❌) y observa cómo avanza la barra de ADN musical.
3. Al alcanzar 25 swipes, se habilitará tu **Radar**. Haz clic en el enlace.
4. En el Radar (`/radar/`), haz match con algún perfil que tenga alta compatibilidad y presiona **Conectar**.
5. Serás redirigido de forma automática a interactuar en la ventana de **Mensajes (`/chat/`)**.

---
_Proyecto colaborativo diseñado con la mejor estética y arquitectura para potenciar conexiones reales a través de la música._
