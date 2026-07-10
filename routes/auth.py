"""
Rutas de autenticación: registro e inicio de sesión.
Endpoint base: /api
"""

import bcrypt
import jwt
import datetime

from flask import Blueprint, request, jsonify
from database import get_db
from config import SECRET_KEY

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.post("/register")
def register():
    """Registra un nuevo usuario con la contraseña hasheada."""
    data     = request.get_json(silent=True) or {}
    nombre   = data.get("nombre", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not nombre or not email or not password:
        return jsonify({"error": "nombre, email y password son requeridos"}), 400

    hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO usuario (nombre, email, contrasena_hash) VALUES (?, ?, ?)",
            (nombre, email, hash_pw),
        )
        conn.commit()
    except Exception:
        return jsonify({"error": "El email ya está registrado"}), 409
    finally:
        conn.close()

    return jsonify({"mensaje": "Usuario registrado correctamente"}), 201


@auth_bp.post("/login")
def login():
    """Autentica al usuario y devuelve un JWT válido por 7 días."""
    data     = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "email y password son requeridos"}), 400

    conn = get_db()
    row  = conn.execute(
        "SELECT id, nombre, contrasena_hash FROM usuario WHERE email = ?", (email,)
    ).fetchone()
    conn.close()

    if row is None or not bcrypt.checkpw(password.encode(), row["contrasena_hash"].encode()):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    token = jwt.encode(
        {
            "usuario_id": row["id"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        },
        SECRET_KEY,
        algorithm="HS256",
    )

    return jsonify({"token": token, "nombre": row["nombre"]}), 200
