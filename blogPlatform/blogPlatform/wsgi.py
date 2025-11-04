import os
import sys

# Add the base directory to the Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogPlatform.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()