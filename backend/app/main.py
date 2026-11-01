"""AeroRL Bench API application."""
from fastapi import FastAPI

from app.api import router

app = FastAPI(title="AeroRL Bench", version="0.1.0")
app.include_router(router)
