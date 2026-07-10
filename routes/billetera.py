"""
Rutas de la billetera (boletos del usuario).
Endpoint base: /api
"""

from flask import Blueprint, request, jsonify
from database import get_db
from middleware import requiere_token

billetera_bp = Blueprint("billetera", __name__, url_prefix="/api")


@billetera_bp.get("/billetera")
@requiere_token
def get_billetera():
    """Devuelve todos los boletos del usuario autenticado."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT b.id, b.asiento, b.estado, b.qr_data,
               e.nombre AS evento_nombre, e.fecha, e.lugar,
               e.categoria, e.color_hex
        FROM   boleto b
        JOIN   evento e ON e.id = b.evento_id
        WHERE  b.usuario_id = ?
        ORDER  BY b.id DESC
        """,
        (request.usuario_id,),
    ).fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows]), 200


@billetera_bp.post("/billetera/comprar")
@requiere_token
def comprar_boleto():
    """Registra la compra de un boleto para el evento indicado."""
    data      = request.get_json(silent=True) or {}
    evento_id = data.get("evento_id")
    asiento   = data.get("asiento", "General")

    if not evento_id:
        return jsonify({"error": "evento_id es requerido"}), 400

    qr_data = f"EVENTTIX-U{request.usuario_id}-E{evento_id}-{asiento}"

    conn   = get_db()
    evento = conn.execute("SELECT id FROM evento WHERE id = ?", (evento_id,)).fetchone()
    if evento is None:
        conn.close()
        return jsonify({"error": "Evento no encontrado"}), 404

    cur = conn.execute(
        "INSERT INTO boleto (usuario_id, evento_id, asiento, estado, qr_data) VALUES (?,?,?,?,?)",
        (request.usuario_id, evento_id, asiento, "activo", qr_data),
    )
    conn.commit()
    boleto_id = cur.lastrowid
    conn.close()

    return jsonify({
        "mensaje"  : "Boleto comprado exitosamente",
        "boleto_id": boleto_id,
        "qr_data"  : qr_data,
    }), 201
