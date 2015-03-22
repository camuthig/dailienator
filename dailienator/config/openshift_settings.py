"""
Django settings for dailienator project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os

def env_var(key, default=None):
    """Retrieves env vars and makes Python boolean replacements"""
    val = os.environ.get(key, default)
    if val == 'True':
        val = True
    elif val == 'False':
        val = False
    return val

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_var('DEBUG', False)

TEMPLATE_DEBUG = env_var('DEBUG', False)

ALLOWED_HOSTS = ['dailienator-kringle.rhcloud.com']

# Keys used by AESFields
AES_KEYS= {
	'catertrax_key': os.path.join(os.environ.get('OPENSHIFT_DATA_DIR'), 'catertrax.key'),
}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': os.environ.get('OPENSHIFT_MYSQL_DB_USERNAME'),
        'PASSWORD': os.environ.get('OPENSHIFT_MYSQL_DB_PASSWORD'),
        'NAME': 'dailienator',
        'HOST': os.environ.get('OPENSHIFT_MYSQL_DB_HOST'),
        'PORT': os.environ.get('OPENSHIFT_MYSQL_DB_PORT'),
    }
}

STATIC_ROOT = os.path.join(os.environ.get('OPENSHIFT_REPO_DIR'), 'wsgi', 'static')

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
            'filename': os.path.join(os.environ.get('OPENSHIFT_LOG_DIR'), 'dailienator.log'),
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
