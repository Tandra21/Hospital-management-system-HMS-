# medfind/medfind_project/settings.py
# NOTE: This file is used by the simple 'donate' + 'ai' standalone apps only.
# The main production backend uses config/settings/prod.py via manage.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-before-running')
DEBUG      = os.getenv('DEBUG', 'False') == 'True'   # Default FALSE
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'donate',
    'ai',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'medfind_project.urls'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'frontend'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'medfind_project.wsgi.application'

# ── MongoDB via Djongo ──────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME':   os.getenv('MONGO_DB', 'medfind_db'),
        'CLIENT': {
            'host': os.getenv('MONGO_URI', 'mongodb://localhost:27017'),
        }
    }
}

# ── Anthropic AI ────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
ANTHROPIC_MODEL   = 'claude-sonnet-4-20250514'
AI_MAX_TOKENS     = 1200
AI_MAX_HISTORY    = 14

# ── Static & Media ──────────────────────────────────
STATIC_URL   = '/static/'
STATIC_ROOT  = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'frontend' / 'static'] if (BASE_DIR / 'frontend' / 'static').exists() else []
MEDIA_URL    = '/media/'
MEDIA_ROOT   = BASE_DIR / 'media'

# ── CORS ────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ── Session ─────────────────────────────────────────
SESSION_ENGINE         = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE     = 86400 * 7
SESSION_COOKIE_SECURE  = not DEBUG

# ── Security (production) ───────────────────────────
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER    = True
    SECURE_CONTENT_TYPE_NOSNIFF  = True
    X_FRAME_OPTIONS              = 'DENY'
    SECURE_SSL_REDIRECT          = True
    SESSION_COOKIE_SECURE        = True
    CSRF_COOKIE_SECURE           = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Dhaka'
USE_I18N      = True
USE_TZ        = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root':     {'handlers': ['console'], 'level': 'WARNING'},
    'loggers':  {'ai': {'handlers': ['console'], 'level': 'INFO', 'propagate': False}},
}
