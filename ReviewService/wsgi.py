"""
WSGI config for ReviewService project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReviewService.settings')

application = get_wsgi_application()

try:
    from labora_shared.env_config import validate_mysql_connection_readable
except ImportError:
    pass
else:
    validate_mysql_connection_readable()
