# ── Etapa única: imagen ligera de Python ────────────────────────────────────
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias primero (aprovecha caché de capas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Puerto expuesto
EXPOSE 9988

# Arranque con gunicorn (servidor WSGI de producción)
CMD ["gunicorn", "--bind", "0.0.0.0:9988", "--workers", "2", "wsgi:app"]
