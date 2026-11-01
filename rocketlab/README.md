# RocketLab
# Distributed rocket simulation & experiment platform
#
# Backend: FastAPI + SQLAlchemy + PostgreSQL
# Frontend: React + TypeScript + Vite + Tailwind + Three.js + Recharts
# Worker: Python (runs on local machines)
#
# Quick start (Oracle server):
#   cd rocketlab/deployment
#   cp ../.env.example .env   # edit as needed
#   docker compose up -d
#
# Then SSH tunnel:
#   ssh -N -L 8080:127.0.0.1:8080 ubuntu@152.70.40.141
#   open http://localhost:8080
#
# Worker (Windows laptop, PowerShell):
#   cd rocketlab/worker
#   python -m venv .venv
#   .venv\Scripts\Activate.ps1
#   pip install -r requirements.txt
#   $env:WORKER_TOKEN="worker-change-me"
#   python -m rocketlab_worker register --name "my-laptop" --token $env:WORKER_TOKEN --api-url http://localhost:8080
#   python -m rocketlab_worker run --token $env:WORKER_TOKEN --api-url http://localhost:8080
