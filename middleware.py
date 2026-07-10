"""
Decorador de autenticación JWT.
Úsalo en cualquier ruta protegida con @requiere_token.
"""

import jwt
from functools import wraps
from flask import request, jsonify
from config import SECRET_KEY


def requiere_token(f):
    """Valida el JWT del header Authorization y expone request.usuario_id."""
    @wraps(f)
    def decorador(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token no proporcionado"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        request.usuario_id = payload["usuario_id"]
        return f(*args, **kwargs)

    return decorador
