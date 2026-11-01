FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATABASE_URL=postgresql+psycopg://rocketlab:rocketlab@db:5432/rocketlab \
    SEED_DEMO_DATA=true

RUN groupadd -r rocketlab && useradd -r -g rocketlab --create-home --shell /usr/sbin/nologin rocketlab

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY seed.py .

RUN mkdir -p /var/lib/rocketlab && chown -R rocketlab:rocketlab /app /var/lib/rocketlab

USER rocketlab

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')" || exit 1

ENTRYPOINT ["sh", "-c", "python seed.py && exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8080"]
