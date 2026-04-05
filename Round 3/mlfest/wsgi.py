"""WSGI config for ML Fest Round 3."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlfest.settings')

application = get_wsgi_application()
