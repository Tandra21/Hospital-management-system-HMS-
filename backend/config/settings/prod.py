"""
MedFind — Production Settings
All secrets come from environment variables. Never hardcode here.
"""
from .base import *
import os

# ── Core ─────────────────────────────────────────────────────────────────────
DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]           # MUST be set in production env
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]

# ── Database — PostgreSQL ─────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     os.environ["DB_NAME"],
        "USER":     os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST":     os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT":     os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS":  {"sslmode": os.environ.get("DB_SSLMODE", "prefer")},
    }
}

# ── Security Headers ──────────────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER          = True
SECURE_CONTENT_TYPE_NOSNIFF        = True
SECURE_HSTS_SECONDS                = 31536000      # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS     = True
SECURE_HSTS_PRELOAD                = True
SECURE_SSL_REDIRECT                = True
X_FRAME_OPTIONS                    = "DENY"
SESSION_COOKIE_SECURE              = True
SESSION_COOKIE_HTTPONLY            = True
SESSION_COOKIE_SAMESITE            = "Lax"
CSRF_COOKIE_SECURE                 = True
CSRF_COOKIE_HTTPONLY               = True
CSRF_TRUSTED_ORIGINS               = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

# ── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS  = False
CORS_ALLOWED_ORIGINS    = [o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS  = True

# ── Static & Media — WhiteNoise + S3 ─────────────────────────────────────────
STATICFILES_STORAGE     = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

AWS_ACCESS_KEY_ID        = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY    = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME  = os.environ.get("AWS_STORAGE_BUCKET_NAME", "medfind-files")
AWS_S3_REGION_NAME       = os.environ.get("AWS_S3_REGION_NAME", "ap-southeast-1")
AWS_S3_FILE_OVERWRITE    = False
AWS_DEFAULT_ACL          = "private"              # Medical files — NEVER public
AWS_S3_ENCRYPTION        = "aws:kms"
if AWS_ACCESS_KEY_ID:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# ── Payment — SSLCommerz ──────────────────────────────────────────────────────
SSLCOMMERZ_STORE_ID     = os.environ.get("SSLCOMMERZ_STORE_ID", "")
SSLCOMMERZ_STORE_PASSWD = os.environ.get("SSLCOMMERZ_STORE_PASS", "")
SSLCOMMERZ_IS_LIVE      = True                    # Live mode in production
SUPER_ADMIN_COMMISSION_PCT = 5
SUPER_ADMIN_BKASH       = os.environ.get("SUPER_ADMIN_BKASH", "")
SUPER_ADMIN_NAGAD        = os.environ.get("SUPER_ADMIN_NAGAD", "")

# ── WebRTC — TURN Server ──────────────────────────────────────────────────────
TURN_SERVER_URL         = os.environ.get("TURN_SERVER_URL", "")
TURN_SERVER_USER        = os.environ.get("TURN_SERVER_USER", "")
TURN_SERVER_PASS        = os.environ.get("TURN_SERVER_PASS", "")

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "prod": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style":  "{",
        }
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "prod"},
        "file":    {
            "class":     "logging.handlers.RotatingFileHandler",
            "filename":  BASE_DIR / "logs" / "medfind.log",
            "maxBytes":  10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "prod",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "WARNING"},
    "loggers": {
        "django":     {"handlers": ["console", "file"], "level": "WARNING", "propagate": False},
        "apps":       {"handlers": ["console", "file"], "level": "INFO",    "propagate": False},
        "ai":         {"handlers": ["console", "file"], "level": "INFO",    "propagate": False},
    },
}

# ── Session ───────────────────────────────────────────────────────────────────
SESSION_ENGINE       = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS  = "default"
CACHES = {
    "default": {
        "BACKEND":  "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}

# ── Anthropic AI ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
ANTHROPIC_MODEL   = "claude-sonnet-4-20250514"
AI_MAX_TOKENS     = 1200
AI_MAX_HISTORY    = 14
