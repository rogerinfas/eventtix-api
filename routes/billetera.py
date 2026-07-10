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


@billetera_bp.patch("/billetera/<int:boleto_id>/cancelar")
@requiere_token
def cancelar_boleto(boleto_id):
    """
    Cancela un boleto activo del usuario autenticado.
    Solo se puede cancelar si el estado es 'activo'.
    """
    conn   = get_db()
    boleto = conn.execute(
        "SELECT id, estado, usuario_id FROM boleto WHERE id = ?", (boleto_id,)
    ).fetchone()

    if boleto is None:
        conn.close()
        return jsonify({"error": "Boleto no encontrado"}), 404

    if boleto["usuario_id"] != request.usuario_id:
        conn.close()
        return jsonify({"error": "No tienes permiso para cancelar este boleto"}), 403

    if boleto["estado"] != "activo":
        conn.close()
        return jsonify({"error": f"El boleto no se puede cancelar (estado actual: {boleto['estado']})"}), 400

    conn.execute(
        "UPDATE boleto SET estado = 'cancelado' WHERE id = ?", (boleto_id,)
    )
    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Boleto cancelado exitosamente", "boleto_id": boleto_id}), 200


@billetera_bp.post("/billetera/transferir")
@requiere_token
def transferir_boleto():
    """
    Transfiere un boleto activo a otro usuario por email.
    Regenera el qr_data para el nuevo dueño.
    """
    data               = request.get_json(silent=True) or {}
    boleto_id          = data.get("boleto_id")
    destinatario_email = data.get("destinatario_email", "").strip().lower()

    if not boleto_id or not destinatario_email:
        return jsonify({"error": "boleto_id y destinatario_email son requeridos"}), 400

    conn = get_db()

    # Verificar que el boleto existe y pertenece al usuario
    boleto = conn.execute(
        "SELECT id, estado, usuario_id, evento_id, asiento FROM boleto WHERE id = ?",
        (boleto_id,),
    ).fetchone()

    if boleto is None:
        conn.close()
        return jsonify({"error": "Boleto no encontrado"}), 404

    if boleto["usuario_id"] != request.usuario_id:
        conn.close()
        return jsonify({"error": "No tienes permiso para transferir este boleto"}), 403

    if boleto["estado"] != "activo":
        conn.close()
        return jsonify({"error": f"Solo se pueden transferir boletos activos (estado actual: {boleto['estado']})"}), 400

    # Verificar que el destinatario existe
    destinatario = conn.execute(
        "SELECT id, nombre FROM usuario WHERE email = ?", (destinatario_email,)
    ).fetchone()

    if destinatario is None:
        conn.close()
        return jsonify({"error": f"No existe ningún usuario con el email '{destinatario_email}'"}), 404

    if destinatario["id"] == request.usuario_id:
        conn.close()
        return jsonify({"error": "No puedes transferirte un boleto a ti mismo"}), 400

    # Regenerar QR para el nuevo dueño y transferir
    nuevo_qr = f"EVENTTIX-U{destinatario['id']}-E{boleto['evento_id']}-{boleto['asiento']}-TRF"
    conn.execute(
        "UPDATE boleto SET usuario_id = ?, qr_data = ? WHERE id = ?",
        (destinatario["id"], nuevo_qr, boleto_id),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "mensaje"          : "Boleto transferido exitosamente",
        "boleto_id"        : boleto_id,
        "destinatario"     : destinatario["nombre"],
        "destinatario_email": destinatario_email,
        "nuevo_qr"         : nuevo_qr,
    }), 200
