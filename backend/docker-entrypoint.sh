#!/bin/sh
set -e

# Seed (re-seed is idempotent) from the bundled results.json into the volume DB.
python seed_db.py results.json "${AERORL_DB_PATH:-/data/aerorl.db}"

exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
