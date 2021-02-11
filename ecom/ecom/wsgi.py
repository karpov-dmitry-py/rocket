"""
WSGI config for ecom project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys
from importlib import reload

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
os.environ['LC_ALL'] = "en_US.UTF-8"
os.environ['LC_LANG'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"
os.environ['LC_CTYPE'] = "en_US.UTF-8"

# noinspection PyBroadException
try:
    # noinspection PyTypeChecker
    reload(sys)
    # noinspection PyUnresolvedReferences
    sys.setdefaultencoding("utf-8")
except Exception:
    pass

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
