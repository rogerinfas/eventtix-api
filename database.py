"""
Gestión de la base de datos SQLite.
Proporciona get_db() para obtener una conexión e init_db() para crear las tablas.
"""

import sqlite3
from config import DB_PATH


def get_db() -> sqlite3.Connection:
    """Abre y retorna una conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn


def init_db() -> None:
    """Crea las tablas si no existen y siembra eventos de ejemplo."""
    conn = get_db()
    cur  = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS usuario (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre          TEXT    NOT NULL,
            email           TEXT    NOT NULL UNIQUE,
            contrasena_hash TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS evento (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre     TEXT NOT NULL,
            categoria  TEXT NOT NULL,
            fecha      TEXT NOT NULL,
            lugar      TEXT NOT NULL,
            precio     TEXT NOT NULL,
            color_hex  TEXT NOT NULL DEFAULT '#6C63FF'
        );

        CREATE TABLE IF NOT EXISTS boleto (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER NOT NULL REFERENCES usuario(id),
            evento_id   INTEGER NOT NULL REFERENCES evento(id),
            asiento     TEXT    NOT NULL,
            estado      TEXT    NOT NULL DEFAULT 'activo',
            qr_data     TEXT    NOT NULL
        );
    """)

    # Siembra eventos solo si la tabla está vacía
    cur.execute("SELECT COUNT(*) FROM evento")
    if cur.fetchone()[0] == 0:
        eventos_seed = [
            ("Noche de Rock Clásico",   "Música",     "2024-08-15", "Estadio Nacional, Lima",      "S/. 120.00", "#E91E63"),
            ("Festival de Jazz",        "Música",     "2024-09-01", "Parque de la Exposición",     "S/. 80.00",  "#9C27B0"),
            ("Obra: Hamlet",            "Teatro",     "2024-08-22", "Teatro Municipal, Arequipa",  "S/. 45.00",  "#3F51B5"),
            ("Stand-Up Comedy Night",   "Comedia",    "2024-08-30", "Centro Cultural Miraflores",  "S/. 60.00",  "#FF9800"),
            ("Concierto de Cumbia",     "Música",     "2024-09-10", "Campo de Marte, Lima",        "S/. 35.00",  "#4CAF50"),
            ("Exposición Arte Moderno", "Arte",       "2024-09-05", "MALI, Lima",                  "S/. 20.00",  "#00BCD4"),
            ("Maratón Ciudad 5K",       "Deportes",   "2024-09-15", "Av. Arequipa, Lima",          "S/. 25.00",  "#FF5722"),
            ("Tech Summit Perú 2024",   "Tecnología", "2024-09-20", "Centro de Convenciones Lima", "S/. 200.00", "#607D8B"),
        ]
        cur.executemany(
            "INSERT INTO evento (nombre, categoria, fecha, lugar, precio, color_hex) VALUES (?,?,?,?,?,?)",
            eventos_seed,
        )

    conn.commit()
    conn.close()
