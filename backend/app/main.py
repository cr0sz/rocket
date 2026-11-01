"""AeroRL Bench API application."""
from fastapi import FastAPI

from app.api import router
from app.dashboard import router as dashboard_router

app = FastAPI(title="AeroRL Bench", version="0.1.0")
app.include_router(router)
app.include_router(dashboard_router)
