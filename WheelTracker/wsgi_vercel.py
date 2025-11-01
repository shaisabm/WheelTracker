"""
WSGI config for WheelTracker project on Vercel.
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WheelTracker.settings')

try:
    application = get_wsgi_application()
    app = application
except Exception as e:
    print(f"Error initializing Django application: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    raise
