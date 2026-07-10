"""
Rutas del catálogo de eventos (pública).
Endpoint base: /api
"""

from flask import Blueprint, jsonify
from database import get_db

eventos_bp = Blueprint("eventos", __name__, url_prefix="/api")


@eventos_bp.get("/eventos")
def get_eventos():
    """Devuelve todos los eventos disponibles ordenados por fecha."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM evento ORDER BY fecha ASC").fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows]), 200
