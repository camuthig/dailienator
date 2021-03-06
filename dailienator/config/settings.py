"""
Django settings for dailienator project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os

if os.environ.get('OPENSHIFT_LOG_DIR'):
    from openshift_settings import *
if os.environ.get('DAILIENATOR_ENV'):
    if os.environ.get('DAILIENATOR_ENV') == 'dev':
        from dev_settings import *

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


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DAILIENATOR_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_var('DAILIENATOR_DEBUG', False)

TEMPLATE_DEBUG = env_var('DAILIENATOR_DEBUG', False)
TEMPLATE_DIRS = (
				os.path.join(BASE_DIR, 'templates'),
				)

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

#Override the authentication user with my customer model
AUTH_USER_MODEL = 'sodexoaccounts.AccountUser'

# ADMIN Information
ADMINS = (
    ('Chris Muthig', 'dailienator.py@gmail.com'),
)

SUPPORTERS = [
    'help.dailienator@gmail.com',
]

# Email credentails
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'help.dailienator@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('DAILIENATOR_EMAIL_PASS')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = ''
SERVER_EMAIL = 'support@dailienator.com'

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
    'bootstrap3_datetime',
    'password_reset',
)

INTERNAL_APPS = (
    'dailienator.sodexoaccounts',
    'dailienator.daily',
    'dailienator.common.aesfield',
    'dailienator.support',
    'dailienator'
)

try:
  INSTALLED_APPS
except NameError:
  INSTALLED_APPS = CORE_APPS + THIRD_PARTY_APPS + INTERNAL_APPS
else:
  INSTALLED_APPS += CORE_APPS + THIRD_PARTY_APPS + INTERNAL_APPS


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

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Sessions
SESSION_COOKIE_AGE = 86400

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Common Celery configurations
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static'),
)
