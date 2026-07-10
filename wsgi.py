"""
Punto de entrada WSGI para gunicorn (producción).
Gunicorn llama a este archivo: gunicorn wsgi:app
"""

from database import init_db
from app import create_app

init_db()
app = create_app()
