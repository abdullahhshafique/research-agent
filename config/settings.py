"""
Django settings for AI Research Agent project - Fly.io Ready.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env", override=True)

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Add Fly.io domain
FLY_APP_NAME = os.environ.get('FLY_APP_NAME', '')
if FLY_APP_NAME:
    ALLOWED_HOSTS.append(f'{FLY_APP_NAME}.fly.dev')
    ALLOWED_HOSTS.append('*')  # For Fly.io internal health checks

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.research',
    'apps.reports',
    'apps.history',
    'apps.collaboration',
    'apps.templates_app',
    'apps.dashboard',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.utils.middleware.ContentSecurityPolicyMiddleware',
    'apps.utils.middleware.QuotaMiddleware',
    'apps.utils.middleware.RequestTimingMiddleware',
    'apps.utils.rate_limit.RateLimitMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database - SQLite with persistent volume on Fly.io
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',  # Persistent volume path
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache' / 'django_cache',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Authentication URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@airesearchagent.com')

# API Keys
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

# Research settings
MAX_RESULTS = int(os.getenv('MAX_RESULTS', '5'))
SEARCH_DEPTH = os.getenv('SEARCH_DEPTH', 'advanced')
QUOTA_FREE = int(os.getenv('QUOTA_FREE', '10'))
QUOTA_PREMIUM = int(os.getenv('QUOTA_PREMIUM', '100'))
PDF_RETENTION_DAYS = int(os.getenv('PDF_RETENTION_DAYS', '30'))
MAX_QUERY_LENGTH = int(os.getenv('MAX_QUERY_LENGTH', '500'))

# CSP Settings
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FONT_SRC = ["'self'"]
CSP_CONNECT_SRC = ["'self'"]
CSP_FRAME_ANCESTORS = ["'none'"]

# Rate Limiting Settings
RATE_LIMIT_ANONYMOUS = int(os.getenv('RATE_LIMIT_ANONYMOUS', '60'))
RATE_LIMIT_AUTHENTICATED = int(os.getenv('RATE_LIMIT_AUTHENTICATED', '300'))

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],  # Console only on Fly.io
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
