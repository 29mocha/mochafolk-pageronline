# mochafolk_backend/settings.py
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- MEMBACA KONFIGURASI DARI ENVIRONMENT VARIABLES ---
# SECRET_KEY akan dibaca dari environment, dengan nilai default jika tidak ditemukan
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-w(#ua&&ua0o-7w*6e_vkj74spsyvu$*=4my%g-@7j@#j@kmw6#'
)

# DEBUG akan False di produksi, kecuali diatur sebaliknya
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() in ('true', '1', 't')

# ALLOWED_HOSTS akan membaca dari environment, dipisahkan oleh spasi
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost 127.0.0.1').split()


# Application definition
INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'shops.apps.ShopsConfig',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Pastikan whitenoise ada di sini
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mochafolk_backend.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mochafolk_backend.wsgi.application'
ASGI_APPLICATION = 'mochafolk_backend.asgi.application'

# --- KONFIGURASI DATABASE DARI ENVIRONMENT ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'mochafolk_db'),
        'USER': os.getenv('DB_USER', 'mochafolk_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'your_super_secret_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'), # Gunakan 'db' untuk Docker
        'PORT': os.getenv('DB_PORT', '5432'),
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
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

# Static and Media files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- KONFIGURASI REDIS DARI ENVIRONMENT ---
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv('REDIS_HOST', 'localhost'), 6379)],
        },
    },
}

# CORS and CSRF
CORS_ALLOWED_ORIGINS = os.getenv(
    'DJANGO_CORS_ALLOWED_ORIGINS',
    'http://localhost:3000 http://127.0.0.1:3000'
).split()

CSRF_TRUSTED_ORIGINS = os.getenv(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'http://localhost:8000 http://127.0.0.1:8000'
).split()


# --- VAPID & MIDTRANS KEYS (HARUS DISET DI ENVIRONMENT SAAT DEPLOY) ---
VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', 'default_public_key')
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', 'default_private_key')
WEBPUSH_CLAIMS = {"sub": f"mailto:{os.getenv('WEBPUSH_EMAIL', 'test@example.com')}"}

MIDTRANS_SERVER_KEY = os.getenv('MIDTRANS_SERVER_KEY', 'default_midtrans_key')
MIDTRANS_IS_PRODUCTION = os.getenv('MIDTRANS_IS_PRODUCTION', 'False').lower() in ('true', '1', 't')
XENDIT_CALLBACK_TOKEN = os.getenv('XENDIT_CALLBACK_TOKEN', 'default_xendit_token')

FRONTEND_URL = os.getenv('FRONTEND_URL', "http://localhost:3000")
