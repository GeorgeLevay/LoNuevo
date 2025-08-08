FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 WEB_CONCURRENCY=2 GUNICORN_THREADS=8
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn
COPY . .
CMD ["sh","-c","gunicorn -w  -k gthread --threads  -b 0.0.0.0: app:app"]
