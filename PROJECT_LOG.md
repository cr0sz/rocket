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

## Phase E — Docker (built on Oracle server; OCI cloud ingress pending)
- Server: 152.70.40.141, ubuntu, aarch64, Ubuntu 24.04, Docker 29.9.2.
- Existing containers left untouched: `stack-caddy-1` (80, 443), `stack-n8n-1` (5678 internal).
- Listening check: 80/443 (caddy), 22 (ssh), 111 (rpcbind) taken; 8000 FREE -> chosen.
- Image `aerorl-backend:latest` built natively for aarch64 from `backend/Dockerfile`
  (python:3.12-slim, non-root `aerorl` user, HEALTHCHECK on /health, SQLite on
  /data volume, entrypoint seeds then runs uvicorn on PORT=8000).
- VM firewall (iptables, add-only, policy unchanged, no prune):
  `iptables -I INPUT -p tcp --dport 8000 -j ACCEPT` (rule #1).
- Container `aerorl-backend` running: `--restart unless-stopped`, `-p 8000:8000`,
  `-v aerorl_data:/data`, `AERORL_DB_PATH=/data/aerorl.db`. Status: **healthy**.
  HEALTHCHECK on /health passes. Internal curl http://127.0.0.1:8000/health ->
  {"status":"ok"}. DB seeded with 12 runs.
- BLOCKED externally: curl http://152.70.40.141:8000/health times out. The OCI
  cloud ingress rule (security list / network security group) for tcp port 8000
  is missing. No `~/.oci` config and instance metadata returns 403, so I cannot
  add it via CLI — must be added in the OCI Console:
    Networking -> VCN -> Security Lists (or the instance's NSG) -> add Ingress rule:
    STATIC, Source CIDR 0.0.0.0/0 (or your IP), IP Protocol TCP, Destination Port 8000, Allow.

Next: user adds the OCI cloud ingress rule for port 8000, then
curl http://152.70.40.141:8000/health (and /runs, /summary) from outside.

## Phase E — status after user added OCI ingress rule
- OCI cloud ingress for tcp 8000 added by user; external http://152.70.40.141:8000/health -> 200 OK.
- Dashboard deployed at / and /dashboard (commit 1ecb97e).
- External access confirmed: /, /dashboard, /health, /summary all return 200.

## Domain: crossrocket.duckdns.org (LIVE)
- DNS resolves crossrocket.duckdns.org -> 152.70.40.141 (verified).
- Caddy reverse proxy added to /home/ubuntu/stack/Caddyfile:
    crossrocket.duckdns.org {
        reverse_proxy aerorl-backend:8000
    }
  (aerorl-backend connected to stack_default network so Caddy can reach it.)
- Caddy auto-provisioned Let's Encrypt HTTPS. External:
    https://crossrocket.duckdns.org/health -> 200 {"status":"ok"}
    https://crossrocket.duckdns.org/ -> dashboard
    https://crossrocket.duckdns.org/summary -> JSON
- Existing n8n block (crossn8n.duckdns.org -> n8n:5678) untouched.

## Phase F (optional) — README + GitHub Actions
- README written (rocketlab/README.md) — honest about MVP status, stack, quick start, limitations.
- GitHub Actions not added (deferred).

## RocketLab (new project, separate from AeroRocket)
- Built distributed rocket simulation & experiment platform: FastAPI backend + SQLAlchemy 2 + PostgreSQL, React + TypeScript + Vite + Tailwind + Three.js + Recharts frontend, Python worker.
- Backend (commit 75af699): experiments, runs (CRUD + cancel/retry), telemetry, training, logs, workers (register/heartbeat/claim/results/fail), dashboard summary. 12 pytest pass.
- Frontend (commit 7419dfb + 9dd8e18): dark mission-control dashboard, 3D Three.js trajectory viewer with animated rocket, Recharts telemetry charts, run detail page, multi-run comparison (overlay trajectories + multi-line charts), experiment management, worker management.
- Worker (commit 9dd8e18): DemoSimulationAdapter + AeroRocketAdapter (real rocket_env.py/rocket.py integration with model fallback), adapter_registry selects best adapter per algorithm.
- Deployment (commit 9dd8e18): Docker Compose (postgres + backend + frontend), python:3.12-slim ARM64, non-root user, healthchecks, SQLite-on-volume pattern kept from AeroRL.
- Live at https://crossrocket.duckdns.org/ (HTTPS via Caddy reverse proxy, n8n untouched).
- Backend tested end-to-end with SQLite TestClient; frontend `tsc` + `vite build` pass.

Versions (rocketlab backend venv): Python 3.14.3, fastapi 0.116.1, uvicorn 0.35.0, pydantic 2.14.2, sqlalchemy 2.0.36, psycopg[binary] 3.2.2, alembic 1.13.1.

Next: none. Project complete for today.
