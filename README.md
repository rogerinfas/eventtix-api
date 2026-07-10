# EventTix API 🎟️

Backend REST en **Flask + SQLite** para la app móvil **EventTix-Flutter**.  
Listo para correr en local o desplegado en un VPS con Docker.

---

## Stack

| Tecnología | Uso |
|---|---|
| Python 3.11 | Lenguaje |
| Flask 3 | Framework web |
| SQLite | Base de datos |
| bcrypt | Hash de contraseñas |
| PyJWT | Tokens de autenticación |
| gunicorn | Servidor WSGI de producción |
| Docker + Compose | Contenedor y orquestación |

---

## Estructura del proyecto

```
eventtix-api/
├── app.py              ← Crea la app y registra blueprints (factory pattern)
├── wsgi.py             ← Punto de entrada para gunicorn (producción)
├── config.py           ← Lee variables desde .env
├── database.py         ← Conexión SQLite + esquema + seed de eventos
├── middleware.py       ← Decorador @requiere_token (validación JWT)
├── test_api.py         ← 12 pruebas de endpoints
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example        ← Plantilla de variables de entorno
├── data/               ← Volumen persistente de la BD (ignorado por git)
└── routes/
    ├── auth.py         → POST /api/register  |  POST /api/login
    ├── eventos.py      → GET  /api/eventos
    ├── perfil.py       → GET  /api/perfil
    └── billetera.py    → GET  /api/billetera  |  POST /api/billetera/comprar
```

---

## Instalación local

```bash
# 1. Clonar y entrar al proyecto
git clone https://github.com/rogerinfas/eventtix-api.git
cd eventtix-api

# 2. Crear entorno virtual e instalar dependencias
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# editar .env con tu SECRET_KEY

# 4. Correr en modo desarrollo
python app.py
```

Servidor disponible en: **http://localhost:9988**

---

## Deploy en VPS con Docker

### Requisitos en el servidor
- Docker y Docker Compose instalados
- Puerto **9988** abierto en el firewall

### Paso a paso

```bash
# 1. Instalar Docker (si no está)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker

# 2. Clonar el repo
git clone https://github.com/rogerinfas/eventtix-api.git
cd eventtix-api

# 3. Crear el archivo de entorno
cp .env.example .env
nano .env   # ← editar SECRET_KEY

# 4. Abrir el puerto en UFW
sudo ufw allow 9988/tcp

# 5. Construir y levantar el contenedor
docker compose up -d --build
```

### Verificar que está corriendo

```bash
# Estado del contenedor
docker compose ps

# Logs en vivo
docker compose logs -f

# Prueba rápida desde el propio servidor
curl http://localhost:9988/api/eventos

# Prueba desde cualquier máquina externa
curl http://<IP_DEL_VPS>:9988/api/eventos
```

### Comandos útiles

```bash
# Reiniciar el servicio
docker compose restart

# Detener sin borrar datos
docker compose down

# Actualizar después de un git pull
git pull && docker compose up -d --build

# Ver logs de los últimos 50 mensajes
docker compose logs --tail=50
```

> **Persistencia de datos**: la base de datos SQLite se guarda en `./data/eventtix.db`
> (montada como volumen Docker). Los datos **sobreviven** a reinicios y rebuilds del contenedor.

---

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `SECRET_KEY` | Clave para firmar los JWT | *(obligatorio cambiarlo)* |
| `DB_PATH` | Ruta del archivo SQLite | `data/eventtix.db` |
| `PORT` | Puerto del servidor | `9988` |

---

## Usuario de prueba (seed)

Al arrancar por primera vez se crea automáticamente un usuario con billetera precargada:

| Campo | Valor |
|---|---|
| **Email** | `admin@eventtix.com` |
| **Password** | `admin123` |
| **Nombre** | Roger Infa Sanchez |

**Billetera inicial:**

| Evento | Asiento | Estado |
|---|---|---|
| Noche de Rock Clásico | Fila A - 12 | activo |
| Obra: Hamlet | VIP 5 | activo |
| Exposición Arte Moderno | General | usado |

---

## Endpoints

### Públicos

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/register` | Registra un nuevo usuario |
| `POST` | `/api/login` | Devuelve un token JWT |
| `GET` | `/api/eventos` | Lista todos los eventos disponibles |

### Protegidos — requieren `Authorization: Bearer <token>`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/perfil` | Datos del usuario autenticado |
| `GET` | `/api/billetera` | Boletos comprados por el usuario |
| `POST` | `/api/billetera/comprar` | Compra un boleto para un evento |

---

## Ejemplos de uso

### Registrar usuario
```bash
curl -X POST http://localhost:9988/api/register \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Roger Infa","email":"rinfas@ulasalle.edu.pe","password":"1234"}'
```

### Login → obtener token
```bash
TOKEN=$(curl -s -X POST http://localhost:9988/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"rinfas@ulasalle.edu.pe","password":"1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

### Ver eventos
```bash
curl http://localhost:9988/api/eventos
```

### Ver perfil
```bash
curl http://localhost:9988/api/perfil \
  -H "Authorization: Bearer $TOKEN"
```

### Comprar boleto
```bash
curl -X POST http://localhost:9988/api/billetera/comprar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"evento_id": 1, "asiento": "Fila A - 12"}'
```

### Ver billetera
```bash
curl http://localhost:9988/api/billetera \
  -H "Authorization: Bearer $TOKEN"
```

---

## Correr las pruebas

Con el servidor corriendo en `localhost:9988`:

```bash
source venv/bin/activate
python3 test_api.py
```

Cubre 12 escenarios: registro, login, JWT válido/inválido, compra de boletos, errores 400/401/404/409.

---

## Conectar desde Flutter

```dart
// Emulador Android
const baseUrl = 'http://10.0.2.2:9988';

// Dispositivo físico en red local
const baseUrl = 'http://192.168.X.X:9988';

// VPS (producción)
const baseUrl = 'http://<IP_DEL_VPS>:9988';
```
