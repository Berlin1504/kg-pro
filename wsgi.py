import os
import sys

# Add the project root to the path so we can import the backend
sys.path.insert(0, os.path.dirname(__file__))

from backend.main import app
from a2wsgi import ASGIMiddleware

# PythonAnywhere WSGI expects an application callable
application = ASGIMiddleware(app)
