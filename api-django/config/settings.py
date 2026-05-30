"""
Encorely — Django Settings
==========================
Configuración principal del proyecto Encorely.
Plataforma social de matchmaking musical basada en gustos de conciertos.

Patrones aplicados:
- Configuración centralizada mediante variables de entorno (.env)
- Separación de concerns: apps modulares bajo apps/
"""

import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv

# ============================================
# BASE DIRECTORY & ENV
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# ============================================
# INSTALLED APPS
# ============================================
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',                    # Django REST Framework
    'rest_framework_simplejwt',          # JWT Authentication
    'corsheaders',                       # CORS Headers
    'drf_spectacular',                   # OpenAPI / Swagger
    'django_extensions',                 # Dev utilities

    # Encorely apps
    'apps.users',                        # Usuarios y perfiles (Camilo + Emmanuel)
    'apps.music',                        # Canciones y swipes (Camilo)
    'apps.matches',                      # Compatibilidad y conexiones (Juan Diego)
    'apps.chat',                         # Mensajería (Juan Diego)
    'apps.events',                       # Eventos y conciertos (Juan Diego)
]


# ============================================
# MIDDLEWARE
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',       # CORS — debe ir antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================
# URL CONFIGURATION
# ============================================
ROOT_URLCONF = 'config.urls'


# ============================================
# TEMPLATES
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'frontend' / 'templates',   # Templates del frontend de Emmanuel
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ============================================
# WSGI
# ============================================
WSGI_APPLICATION = 'config.wsgi.application'


# ============================================
# DATABASE — SQLite para desarrollo
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================================
# CUSTOM USER MODEL & AUTHENTICATION
# ============================================
AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'apps.users.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]


# ============================================
# PASSWORD VALIDATION
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================
# INTERNATIONALIZATION
# ============================================
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# ============================================
# STATIC FILES (CSS, JavaScript, Images)
# ============================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'frontend' / 'static',    # Archivos estáticos del frontend
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ============================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================
# DJANGO REST FRAMEWORK
# ============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}


# ============================================
# JWT CONFIGURATION (Simple JWT)
# ============================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '60'))
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}


# ============================================
# CORS CONFIGURATION
# ============================================
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:8000,http://127.0.0.1:8000'
).split(',')
CORS_ALLOW_CREDENTIALS = True


# ============================================
# DRF-SPECTACULAR (Swagger / OpenAPI)
# ============================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Encorely API',
    'DESCRIPTION': (
        'API REST para Encorely — plataforma social de matchmaking musical. '
        'Conecta personas según sus gustos de conciertos usando análisis '
        'de similitud del coseno sobre vectores de audio features.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Auth', 'description': 'Registro, login y refresh de tokens JWT'},
        {'name': 'Users', 'description': 'Gestión de perfiles y vectores DNA musical'},
        {'name': 'Music', 'description': 'Canciones y sistema de swipes'},
        {'name': 'Matches', 'description': 'Compatibilidad y radar de conexiones'},
        {'name': 'Chat', 'description': 'Mensajería entre usuarios conectados'},
        {'name': 'Events', 'description': 'Conciertos y asistencia'},
    ],
}
