"""ASGI config for GymPro."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gympro.settings")

application = get_asgi_application()
