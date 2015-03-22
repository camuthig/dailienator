import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Keys used by AESFields
AES_KEYS= {
    'catertrax_key': os.path.join(BASE_DIR, 'config', 'catertrax.key'),
}


# Dev Only Installed Apps
INSTALLED_APPS = (
    'kombu.transport.django',
)

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': '',
        'NAME': 'dailienator'
    }
}

# Celery
BROKER_URL = 'django://'

# Static Files
STATIC_ROOT = '/var/www/static/dailienator'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logging/dailienator.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'dailienator': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}