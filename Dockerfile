FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

# Copiar el resto del código
COPY . .

# Cloud Run expone el puerto a través de la variable PORT
ENV PORT=8080

# Ejecutar con Gunicorn (threads para mejor concurrencia en I/O)
CMD ["gunicorn", "-w", "2", "-k", "gthread", "--threads", "8", "-b", "0.0.0.0:${PORT}", "app:app"]


