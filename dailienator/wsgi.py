"""
WSGI config for dailienator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailienator.config.settings")


if os.environ.has_key('OPENSHIFT_REPO_DIR'):
    # Set up the virtualenv stuff on OpenShift
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    try:
        execfile(virtualenv, dict(__file__=virtualenv))
    except IOError:
        pass

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
