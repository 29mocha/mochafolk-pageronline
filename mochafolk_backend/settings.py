# mochafolk_backend/settings.py
from datetime import timedelta
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-w(#ua&&ua0o-7w*6e_vkj74spsyvu$*=4my%g-@7j@#j@kmw6#'
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '96d07e328c5c.ngrok-free.app', # Ganti dengan URL ngrok Anda jika berbeda
]

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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mochafolk_backend.urls'
TEMPLATES = [ { 'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': { 'context_processors': [ 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages', ], }, }, ]
WSGI_APPLICATION = 'mochafolk_backend.wsgi.application'
ASGI_APPLICATION = 'mochafolk_backend.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mochafolk_db',
        'USER': 'mochafolk_user',
        'PASSWORD': 'Lighthouse1717',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [ { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', }, { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', }, { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', }, { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', }, ]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": { "hosts": [("127.0.0.1", 6379)], },
    },
}

CORS_ALLOWED_ORIGINS = [ "http://localhost:3000", ]
CSRF_TRUSTED_ORIGINS = [ 'http://localhost:8000', 'http://127.0.0.1:8000', ]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- KUNCI VAPID YANG SUDAH DIBERSIHKAN ---
VAPID_PUBLIC_KEY = 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAESmIVpjr+FFUTajXcjN0SwCqI+CWBtFswrgVla8s/9TGMNPOjA74cErqDW/tRGqEIlZUHPkOI1qNt3pebSlXB4w=='
VAPID_PRIVATE_KEY = 'MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgJ7g598CguExS8oP9pR80Jx8Umc3AYNJTK//1l2kllo2hRANCAARKYhWmOv4UVRNqNdyM3RLAKoj4JYG0WzCuBWVryz/1MYw086MDvhwSuoNb+1EaoQiVlQc+Q4jWo23el5tKVcHj'
WEBPUSH_CLAIMS = { "sub": "mailto:mochafolk@gmail.com" }

# Midtrans API Keys
MIDTRANS_SERVER_KEY = 'MASUKKAN_SERVER_KEY_ANDA_DI_SINI'
MIDTRANS_IS_PRODUCTION = False
MIDTRANS_CALLBACK_KEY = 'INI_ADALAH_TOKEN_RAHASIA_SAYA_UNTUK_MIDTRANS'

FRONTEND_URL = "http://localhost:3000"
