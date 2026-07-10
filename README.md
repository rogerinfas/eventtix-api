# EventTix API 🎟️

Backend Flask mínimo para la app móvil **EventTix-Flutter**.  
Base de datos: **SQLite** (archivo `eventtix.db` generado automáticamente).

---

## Instalación rápida

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Correr el servidor
python app.py
```

El servidor queda en: **http://localhost:5000**

---

## Endpoints

### Públicos

| Método | Ruta            | Descripción                  |
|--------|-----------------|------------------------------|
| POST   | `/api/register` | Registra un nuevo usuario    |
| POST   | `/api/login`    | Devuelve un token JWT        |
| GET    | `/api/eventos`  | Lista todos los eventos      |

### Protegidos (requieren `Authorization: Bearer <token>`)

| Método | Ruta                      | Descripción                         |
|--------|---------------------------|-------------------------------------|
| GET    | `/api/perfil`             | Datos del usuario autenticado       |
| GET    | `/api/billetera`          | Boletos del usuario autenticado     |
| POST   | `/api/billetera/comprar`  | Compra un boleto para un evento     |

---

## Ejemplos de uso (curl)

```bash
# Registrar
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Roger Infa","email":"rinfas@ulasalle.edu.pe","password":"1234"}'

# Login → guarda el token
TOKEN=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"rinfas@ulasalle.edu.pe","password":"1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Ver perfil
curl http://localhost:5000/api/perfil -H "Authorization: Bearer $TOKEN"

# Ver eventos
curl http://localhost:5000/api/eventos

# Comprar boleto
curl -X POST http://localhost:5000/api/billetera/comprar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"evento_id":1,"asiento":"Fila A - 12"}'

# Ver billetera
curl http://localhost:5000/api/billetera -H "Authorization: Bearer $TOKEN"
```

---

## Estructura del proyecto

```
eventtix-api/
├── app.py           ← Toda la lógica (Flask + SQLite + JWT)
├── requirements.txt ← Dependencias Python
├── README.md        ← Este archivo
└── eventtix.db      ← Generado automáticamente al correr app.py
```
