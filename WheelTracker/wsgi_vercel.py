"""
WSGI config for WheelTracker project on Vercel.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WheelTracker.settings')

application = get_wsgi_application()
app = application
