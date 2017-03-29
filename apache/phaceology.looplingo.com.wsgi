# -*-python-*-
"""
WSGI config for phaceology project.
"""
import sys
from os import path
import os

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "looplingo.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phaceology.settings")

THIS_DIR = path.dirname(path.abspath(__file__))
APP_DIR = path.dirname(THIS_DIR)
VENV_DIR= path.join(APP_DIR, 'env')
LOG_DIR= path.join(APP_DIR, 'logs')

os.environ['PHACEOLOGY_SERVER_CONFIG_DIR'] = path.join(APP_DIR, 'local_settings', 'phaceology.looplingo.com')

# Set up the virtualenv
activate_this = path.join(VENV_DIR, 'bin/activate_this.py')
# Code from http://stackoverflow.com/a/33637378/109044
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

sys.path = [APP_DIR] + sys.path

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
