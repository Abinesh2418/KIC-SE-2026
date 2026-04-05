"""ASGI config for ML Fest Round 3."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mlfest.settings')

application = get_asgi_application()
