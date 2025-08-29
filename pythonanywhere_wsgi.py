# This file contains the WSGI configuration required to serve your
# FastAPI application on PythonAnywhere.
# It works by wrapping the FastAPI ASGI application in a WSGI application.

import os
import sys

# IMPORTANT:
# 1. Replace 'your-username' with your actual PythonAnywhere username.
# 2. Replace 'BI_automate' with the name of your project's root directory.
project_home = '/home/praykar/biautomate'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the ASGI-to-WSGI wrapper and your FastAPI app
from a2wsgi import ASGIMiddleware

from main import app as fastapi_app

# Wrap the FastAPI app for the WSGI server
application = ASGIMiddleware(fastapi_app)
