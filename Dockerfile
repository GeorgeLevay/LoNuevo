FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn
COPY . .
# 2 workers, 8 threads, bind al puerto que da Render
CMD ["sh","-c","gunicorn -w 2 -k gthread --threads 8 -b 0.0.0.0: app:app"]
