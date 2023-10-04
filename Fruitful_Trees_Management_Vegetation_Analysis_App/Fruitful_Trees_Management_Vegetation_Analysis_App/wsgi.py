"""
WSGI config for treesSite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import ee
from pathlib import Path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treesSite.settings')

application = get_wsgi_application()


# GEE key path
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# you must add key file to "keys" folder and name it "geeKey.json"
GEE_KEY_DIR = file_path = os.path.join(BASE_DIR, "keys/geeKey.json")


# Earth Engine Authentication
service_account = "Put Your Service Account Here"

# uncomment these lines to enable ee authentication
credentials = ee.ServiceAccountCredentials(service_account, GEE_KEY_DIR)

# initialize earth engine
print('\033[32m' + 'initializing Earth Engine......' + '\033[0m')
ee.Initialize(credentials)
print('\033[32m' + 'Earth Engine initialization completed' + '\033[0m')
