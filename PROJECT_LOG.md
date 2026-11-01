# Project Log — AeroRL Bench backend

Versions (venv): Python 3.12.10, gymnasium 1.4.0, numpy 2.5.4, stable-baselines3 2.9.0, torch 2.14.1+cpu

## Phase A — make the data
Commit: `feat: evaluate all controllers and write results.json`

- Rewrote `evaluate.py`: evaluates `ppo` (basic & extended, seeds 0-4), `hand_rule` (`make_autopilot(5, -20)`), `random` (seeded coin flip), all on the same 2000 start altitudes (`env.reset(seed=123)` once, then replayed). Writes `results.json` with counts + 10 altitude bands (20 m each, 400-600 m). Asserts band game/landing sums equal the totals.
- PPO extended landings (MEASURED): 1291, 1335, 1335, 1325, 1335 — matches the brief exactly.
- PPO basic landings (MEASURED): 1106, 1114, 1114, 1053, 1114 (55.30 / 55.70 / 55.70 / 52.65 / 55.70 %).
- `hand_rule`: 875/2000 (43.75 %), `random`: 1/2000 (0.05 %). Both seeded & reproducible; supersede the unverified 44.18 % / 0.1 % that came from the non-reproducible unseeded `win_rate()`.
- Removed the swear comment from `rocket.py` line 1.
- `plots.py` now reads `results.json` instead of hand-typed numbers (ceiling/best_by_band remain theoretical constants from ceiling.py).

## Phase B — API skeleton
Commit: `6c356c8 feat: add FastAPI backend, SQLite seed, tests, and Dockerfile` (includes C, D, E's Dockerfile)

- New `backend/` folder with its own venv (`backend/.venv`, gitignored) and pinned `requirements.txt`:
  fastapi 0.116.1, uvicorn 0.35.0, pydantic 2.14.2, httpx 0.28.1, pytest 8.4.1.
  No torch / stable-baselines3 (server never trains).
- Pydantic response models (docs: https://docs.pydantic.dev/latest/concepts/models/):
  Band, Run, RunDetail (bands included), SummaryRow, Health.
- Endpoints (docs: query params https://fastapi.tiangolo.com/tutorial/query-params/;
  HTTPException 404 https://fastapi.tiangolo.com/tutorial/handling-errors/):
  GET /health -> {"status":"ok"}
  GET /runs[?controller=X] -> list of runs (no bands), optional controller filter
  GET /runs/{id} -> 404 if missing; includes band data (JOIN altitude_bands)
  GET /summary -> GROUP BY controller, obs_mode; PPO basic and PPO extended
  never merged; n_runs, avg/min/max per-seed landing rate
- DB path from env var AERORL_DB_PATH (default aerorl.db). read per connection.

## Phase C — SQLite
- seed_db.py loads results.json using the built-in sqlite3 module.
- Tables: runs (id, controller, obs_mode, seed, eval_seed, games, landings) and
  altitude_bands (id, run_id, alt_min, alt_max, games, landings).
- Idempotent (DELETE + reload). Seeded 12 runs from results.json.

## Phase D — Tests
- pytest + FastAPI TestClient on an isolated temp DB (monkeypatch AERORL_DB_PATH).
- 6 tests pass: /health, /runs shape & count (12), ?controller= filter (ppo=10,
  random=1), /runs/{id} includes 10 bands with band-sum assertions, 404 on
  unknown id, /summary matches numbers recomputed independently from results.json
  (never copied from API output).

## Phase E — Docker (written, not deployed)
- backend/Dockerfile: python:3.12-slim, non-root `aerorl` user, HEALTHCHECK on
  /health, SQLite DB on /data volume, docker-entrypoint.sh seeds then runs uvicorn.
- NOT deployed yet: Docker is not installed on this Windows machine; the image
  must be built on the Oracle Linux server. Blocked on Oracle server SSH
  details (host, user, port/key) needed to:
    * run uname -m and build for that architecture,
    * check what's listening before choosing a port,
    * add OCI cloud ingress + VM firewall rules for the port (add only, no
      policy changes, no prune),
    * ensure the existing Dockerized n8n bot is not disturbed.

Next: get Oracle server SSH access, then build, run, and verify the container.
