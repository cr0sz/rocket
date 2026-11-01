"""API router package."""
from fastapi import APIRouter

from app.api import experiments, runs, workers, dashboard

api_router = APIRouter()
api_router.include_router(experiments.router)
api_router.include_router(runs.router)
api_router.include_router(workers.router)
api_router.include_router(dashboard.router)
