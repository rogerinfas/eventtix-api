"""
Rutas del perfil del usuario autenticado.
Endpoint base: /api
"""

from flask import Blueprint, request, jsonify
from database import get_db
from middleware import requiere_token

perfil_bp = Blueprint("perfil", __name__, url_prefix="/api")


@perfil_bp.get("/perfil")
@requiere_token
def get_perfil():
    """Devuelve nombre y email del usuario autenticado."""
    conn = get_db()
    row  = conn.execute(
        "SELECT nombre, email FROM usuario WHERE id = ?", (request.usuario_id,)
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"nombre": row["nombre"], "email": row["email"]}), 200
