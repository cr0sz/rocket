# RocketLab

Distributed rocket simulation & experiment platform — mission control dashboard for rocket landing simulations and ML experiments.

## What it is

A lightweight experiment tracker + simulation job manager + flight telemetry viewer. Backend serves a dark-theme React dashboard with Three.js 3D trajectory visualization and Recharts telemetry charts. Workers run simulations locally on your machines and stream results back to the Oracle server.

## Stack

- **Backend**: FastAPI + SQLAlchemy 2 + PostgreSQL (ARM64, python:3.12-slim)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS + Three.js + Recharts
- **Worker**: Python (Windows/Linux), `requests` only
- **Infra**: Docker Compose (postgres + backend + frontend), Caddy reverse proxy on the host

## What works

- Dashboard at `https://crossrocket.duckdns.org/` (demo data seeded)
- API: `/api/v1/experiments`, `/api/v1/runs`, `/api/v1/runs/{id}`, `/api/v1/dashboard/summary`, `/api/v1/workers`
- Run detail: 3D trajectory, altitude/velocity/fuel charts, training curves, worker logs
- Experiment comparison (up to 3 runs)
- Worker register/claim/progress/results lifecycle
- Demo experiments: PPO Extended, PPO Basic, Hand Rule, Random (14 runs, telemetry + training)

## Quick start (Oracle server)

```bash
cd rocketlab/deployment
cp ../.env.example .env   # edit SECRET_KEY, ADMIN_TOKEN, WORKER_TOKEN
docker compose up -d
```

Dashboard is served via Caddy on `crossrocket.duckdns.org` (HTTPS, Let's Encrypt). No SSH tunnel needed.

## Worker (Windows laptop, PowerShell)

```powershell
cd rocketlab/worker
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:WORKER_TOKEN="worker-change-me"
python -m rocketlab_worker register --name "my-laptop" --token $env:WORKER_TOKEN --api-url https://crossrocket.duckdns.org
python -m rocketlab_worker run --token $env:WORKER_TOKEN --api-url https://crossrocket.duckdns.org
```

## Project structure

```
rocketlab/
├── backend/          # FastAPI app, SQLAlchemy models, seed script, Dockerfile
├── frontend/         # React + Vite + Tailwind + Three.js + Recharts
├── worker/           # Python worker (rocketlab_worker package)
├── deployment/       # docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Limitations / honest status

- Frontend is a functional MVP, not polished UI. Charts work, 3D viewer works, but styling is rough.
- Demo data is deterministic synthetic (labelled DEMO), not real flight data.
- No AeroRocket PPO model integration yet — uses `DemoSimulationAdapter`. Actual `rocket_env.py`/`stable_baselines3` integration is a future adapter.
- No auth beyond shared worker/admin tokens. Change them in `.env`.
- PostgreSQL is the only DB. No Redis, no Kafka, no K8s (by design).

## What's NOT in this repo

- `node_modules/`, `dist/`, `*.db`, `.env`, `__pycache__/` — all gitignored.
- Model `.zip` files (AeroRocket's) — stay in the parent repo, not here.
