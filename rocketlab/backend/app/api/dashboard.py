"""Dashboard summary API routes."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Experiment, Run, Worker
from app.schemas import DashboardSummary, RunOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    total_experiments = db.query(func.count(Experiment.id)).scalar() or 0
    total_runs = db.query(func.count(Run.id)).scalar() or 0

    # Landing success rate from metrics
    completed = db.query(Run).filter(Run.status == "completed").all()
    successes = sum(1 for r in completed if r.metrics and r.metrics.get("landing_success"))
    success_rate = (successes / len(completed) * 100) if completed else 0.0

    # Best touchdown velocity
    best_vel = None
    best_err = None
    for r in completed:
        if r.metrics:
            v = r.metrics.get("touchdown_velocity_mps")
            if v is not None and (best_vel is None or v < best_vel):
                best_vel = v
            e = r.metrics.get("horizontal_error_m")
            if e is not None and (best_err is None or e < best_err):
                best_err = e

    active_workers = (
        db.query(func.count(Worker.id))
        .filter(Worker.status == "online")
        .scalar()
        or 0
    )

    recent = (
        db.query(Run)
        .order_by(Run.created_at.desc())
        .limit(10)
        .all()
    )

    return DashboardSummary(
        total_experiments=total_experiments,
        total_runs=total_runs,
        landing_success_rate=round(success_rate, 2),
        best_touchdown_velocity=best_vel,
        best_horizontal_error=best_err,
        active_workers=active_workers,
        recent_runs=recent,
    )
