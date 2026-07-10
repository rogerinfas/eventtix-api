"""
Punto de entrada de la aplicación EventTix API.
Registra los blueprints y arranca el servidor.
"""

from flask import Flask
from flask_cors import CORS

from config import SECRET_KEY         # noqa: F401 — importado para que esté en scope
from database import init_db
from routes.auth import auth_bp
from routes.eventos import eventos_bp
from routes.perfil import perfil_bp
from routes.billetera import billetera_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(eventos_bp)
    app.register_blueprint(perfil_bp)
    app.register_blueprint(billetera_bp)

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    print("✅  EventTix API corriendo en http://localhost:9988")
    app.run(debug=True, host="0.0.0.0", port=9988)
