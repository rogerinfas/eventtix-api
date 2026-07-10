"""
Script de pruebas para la EventTix API.
Ejecutar con el servidor corriendo en http://localhost:9988
"""

import urllib.request
import urllib.error
import json

BASE  = "http://localhost:9988"
S     = "─" * 60
OK    = "✅ "
KO    = "🔴 "
TOKEN = None   # se llena después del login


def req(method, path, body=None, token=None):
    data    = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        f"{BASE}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def titulo(n, icono, descripcion):
    print(f"\n{S}\n{icono} {n}. {descripcion}")


# ── 1. Registro exitoso ──────────────────────────────────────────────────────
titulo(1, OK, "POST /api/register")
code, resp = req("POST", "/api/register", {
    "nombre": "Roger Infa Sanchez",
    "email":  "rinfas@ulasalle.edu.pe",
    "password": "1234"
})
print(f"   HTTP {code} → {resp}")

# ── 2. Login exitoso ─────────────────────────────────────────────────────────
titulo(2, OK, "POST /api/login")
code, resp = req("POST", "/api/login", {
    "email": "rinfas@ulasalle.edu.pe",
    "password": "1234"
})
TOKEN = resp.get("token")
print(f"   HTTP {code} → nombre: '{resp.get('nombre')}'")
print(f"   token: {TOKEN[:50]}…")

# ── 3. Login con contraseña incorrecta ──────────────────────────────────────
titulo(3, KO, "POST /api/login  (contraseña incorrecta → espera 401)")
code, resp = req("POST", "/api/login", {
    "email": "rinfas@ulasalle.edu.pe",
    "password": "wrongpass"
})
print(f"   HTTP {code} → {resp}")

# ── 4. Eventos (público) ─────────────────────────────────────────────────────
titulo(4, OK, "GET /api/eventos")
code, resp = req("GET", "/api/eventos")
print(f"   HTTP {code} → {len(resp)} eventos recibidos:")
for e in resp:
    print(f"      [{e['id']}] {e['nombre']:<32} {e['fecha']}  {e['precio']}")

# ── 5. Perfil con JWT ────────────────────────────────────────────────────────
titulo(5, OK, "GET /api/perfil  (con JWT)")
code, resp = req("GET", "/api/perfil", token=TOKEN)
print(f"   HTTP {code} → {resp}")

# ── 6. Perfil sin token ──────────────────────────────────────────────────────
titulo(6, KO, "GET /api/perfil  (sin token → espera 401)")
code, resp = req("GET", "/api/perfil")
print(f"   HTTP {code} → {resp}")

# ── 7. Comprar boleto #1 ─────────────────────────────────────────────────────
titulo(7, OK, "POST /api/billetera/comprar  (Rock Clásico — Fila A-12)")
code, resp = req("POST", "/api/billetera/comprar", {
    "evento_id": 1, "asiento": "Fila A - 12"
}, TOKEN)
print(f"   HTTP {code} → {resp}")

# ── 8. Comprar boleto #2 ─────────────────────────────────────────────────────
titulo(8, OK, "POST /api/billetera/comprar  (Hamlet — VIP 5)")
code, resp = req("POST", "/api/billetera/comprar", {
    "evento_id": 3, "asiento": "VIP 5"
}, TOKEN)
print(f"   HTTP {code} → {resp}")

# ── 9. Comprar boleto con evento inexistente ─────────────────────────────────
titulo(9, KO, "POST /api/billetera/comprar  (evento_id=999 → espera 404)")
code, resp = req("POST", "/api/billetera/comprar", {
    "evento_id": 999, "asiento": "X1"
}, TOKEN)
print(f"   HTTP {code} → {resp}")

# ── 10. Ver billetera ────────────────────────────────────────────────────────
titulo(10, OK, "GET /api/billetera  (con JWT)")
code, resp = req("GET", "/api/billetera", token=TOKEN)
print(f"   HTTP {code} → {len(resp)} boleto(s):")
for b in resp:
    print(f"      [{b['id']}] {b['evento_nombre']:<32} Asiento: {b['asiento']:<15} Estado: {b['estado']}")
    print(f"           QR → {b['qr_data']}")

# ── 11. Email duplicado ──────────────────────────────────────────────────────
titulo(11, KO, "POST /api/register  (email duplicado → espera 409)")
code, resp = req("POST", "/api/register", {
    "nombre": "Duplicado", "email": "rinfas@ulasalle.edu.pe", "password": "abc"
})
print(f"   HTTP {code} → {resp}")

# ── 12. Campos faltantes ─────────────────────────────────────────────────────
titulo(12, KO, "POST /api/register  (sin password → espera 400)")
code, resp = req("POST", "/api/register", {"nombre": "X", "email": "x@x.com"})
print(f"   HTTP {code} → {resp}")

print(f"\n{S}\n🎉  12/12 pruebas completadas.\n")
