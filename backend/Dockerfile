FROM python:3.12-slim

WORKDIR /app

ENV AERORL_DB_PATH=/data/aerorl.db \
    PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Non-root user; the server never trains, so no torch / stable-baselines3.
RUN groupadd -r aerorl && useradd -r -g aerorl --create-home --shell /usr/sbin/nologin aerorl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY seed_db.py .
COPY results.json .

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && mkdir -p /data \
    && chown -R aerorl:aerorl /app /data

VOLUME /data

USER aerorl

# SQLite database lives on the /data volume so it survives container recreation.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
