import configparser
import os
import socket
import warnings

from django.core.cache import CacheKeyWarning
from django.template.base import TemplateSyntaxError


DEFAULT_CONFIG = {
    'django': {
        'debug': True,
        'secret': 'not-a-secret',
        'static_url': '/static/',
        'debug_use_cache': False,
    },
    'logging': {
        'scifiweb_log_level': 'INFO',
        'django_log_level': 'INFO',
    },
}

config = configparser.RawConfigParser()
config_path = os.environ.get('SCIFIWEB_CONFIG')
config.read_dict(DEFAULT_CONFIG)
if config_path:
    config.read(config_path)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = config.getboolean('django', 'debug')
SECRET_KEY = config.get('django', 'secret')

ALLOWED_HOSTS = ['projectscifi.org']
if DEBUG:
    ALLOWED_HOSTS += [
        socket.getfqdn(),
        socket.gethostname(),
        'localhost',
        '0.0.0.0',
        '127.0.0.1',
        '::1',
    ]

ROOT_URLCONF = 'scifiweb.urls'
WSGI_APPLICATION = 'scifiweb.wsgi.application'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'scifiweb',
    'scifiweb.info',
    'scifiweb.news',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


class InvalidReferenceInTemplate(str):
    """Raise exceptions on invalid references in templates.

    By default Django just replaces references to undefined variables with
    empty strings. This is a horrible idea, so we instead hack it to raise an
    exception.
    """

    def __mod__(self, ref):
        raise TemplateSyntaxError('Invalid reference in template: {}'.format(ref))


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'string_if_invalid': InvalidReferenceInTemplate('%s'),
        },
    },
]


# Log exceptions to stderr (you can find this code on StackOverflow)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'scifiweb': {
            'handlers': ['console'],
            'level': config.get('logging', 'scifiweb_log_level'),
        },
        'django': {
            'handlers': ['console'],
            'level': config.get('logging', 'django_log_level'),
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


DATABASES = {}


DEBUG_USE_CACHE = config.getboolean('django', 'debug_use_cache')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config.get('django', 'redis_uri'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    } if not DEBUG or DEBUG_USE_CACHE else {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# We don't use memcached, so these warnings are not helpful
warnings.simplefilter('ignore', CacheKeyWarning)


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = False
USE_L10N = False
USE_TZ = True

X_FRAME_OPTIONS = 'DENY'


STATIC_URL = config.get('django', 'static_url')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'scifiweb/static'),
]


if not DEBUG:
    EMAIL_HOST = config.get('email', 'host')
    EMAIL_HOST_USER = config.get('email', 'user')
    EMAIL_HOST_PASSWORD = config.get('email', 'password')
    EMAIL_USE_TLS = config.get('email', 'use_tls')

    ADMINS = [('Webmaster', 'webmaster@projectscifi.org')]
    SERVER_EMAIL = EMAIL_HOST_USER

    # We don't use cookies yet but these might be forgotten later on
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
