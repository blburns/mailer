#!/usr/bin/env python3
import os
import sys

APP_NAME='mailer'

# Adjust this path to where the project is deployed (e.g., /opt/dreamlikelabs)
APP_HOME = os.environ.get('APP_HOME', '/opt/dreamlikelabs/' + APP_NAME)
if APP_HOME not in sys.path:
    sys.path.insert(0, APP_HOME)

# Ensure the app runs in production mode by default
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

# Import WSGI application
from app import app as application  # app is created in app/__init__.py


