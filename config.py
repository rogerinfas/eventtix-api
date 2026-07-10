"""
Configuración global de la aplicación.
Los valores se leen desde el archivo .env (copia .env.example → .env para empezar).
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de .env al entorno

SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto_insegura")
DB_PATH    = os.getenv("DB_PATH", "data/eventtix.db")
PORT       = int(os.getenv("PORT", 9988))
