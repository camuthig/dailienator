"""
Django settings for dailienator project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DAILIENATOR_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DAILIENATOR_DEBUG')

TEMPLATE_DEBUG = os.environ.get('DAILIENATOR_DEBUG')
TEMPLATE_DIRS = (
				os.path.join(BASE_DIR, 'templates'),
				)

ALLOWED_HOSTS = []

#Override the authentication user with my customer model
AUTH_USER_MODEL = 'sodexoaccounts.AccountUser'

# Keys used by AESFields
AES_KEYS= {
	'catertrax_key': os.path.join(BASE_DIR, 'config', 'catertrax.key'),
}

# Application definition

CORE_APPS = (
	'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
	'south',
	'Crypto',
)

INTERNAL_APPS = (
	'dailienator.sodexoaccounts',
    'dailienator.daily',
	'dailienator.common.aesfield',
)

INSTALLED_APPS = CORE_APPS + THIRD_PARTY_APPS + INTERNAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'dailienator.urls'

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = 'users/'
LOGOUT_REDIRECT_URL = '/'

WSGI_APPLICATION = 'dailienator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = '/var/www/static/dailienator'

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
