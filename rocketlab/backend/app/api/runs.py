"""Run API routes - CRUD, telemetry, training, logs."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models import Experiment, Run, TelemetryPoint, TrainingMetric, RunLog
from app.schemas import (
    JobProgress,
    JobResult,
    JobTelemetry,
    JobTraining,
    RunCreate,
    RunOut,
    RunUpdate,
    TelemetryPointOut,
    TrainingMetricOut,
    TrajectoryOut,
)

router = APIRouter(prefix="/runs", tags=["runs"])


def _get_run_or_404(db: Session, run_id: UUID) -> Run:
    run = db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("", response_model=RunOut, status_code=status.HTTP_201_CREATED)
def create_run(payload: RunCreate, db: Session = Depends(get_db)):
    exp = db.get(Experiment, payload.experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    run = Run(
        experiment_id=payload.experiment_id,
        algorithm=payload.algorithm,
        obs_mode=payload.obs_mode,
        seed=payload.seed,
        config=payload.config,
        status="queued",
        progress=0.0,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@router.get("", response_model=List[RunOut])
def list_runs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    algorithm: Optional[str] = Query(None),
    experiment_id: Optional[UUID] = Query(None),
):
    q = db.query(Run).options(joinedload(Run.experiment))
    if status_filter:
        q = q.filter(Run.status == status_filter)
    if algorithm:
        q = q.filter(Run.algorithm == algorithm)
    if experiment_id:
        q = q.filter(Run.experiment_id == experiment_id)
    return q.order_by(Run.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{run_id}", response_model=RunOut)
def get_run(run_id: UUID, db: Session = Depends(get_db)):
    return _get_run_or_404(db, run_id)


@router.patch("/{run_id}", response_model=RunOut)
def update_run(run_id: UUID, payload: RunUpdate, db: Session = Depends(get_db)):
    run = _get_run_or_404(db, run_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(run, field, value)
    db.commit()
    db.refresh(run)
    return run


@router.post("/{run_id}/cancel", response_model=RunOut)
def cancel_run(run_id: UUID, db: Session = Depends(get_db)):
    run = _get_run_or_404(db, run_id)
    if run.status in ("completed", "cancelled"):
        raise HTTPException(status_code=400, detail="Run cannot be cancelled")
    run.status = "cancelled"
    db.commit()
    db.refresh(run)
    return run


@router.post("/{run_id}/retry", response_model=RunOut)
def retry_run(run_id: UUID, db: Session = Depends(get_db)):
    run = _get_run_or_404(db, run_id)
    if run.status not in ("failed", "cancelled"):
        raise HTTPException(status_code=400, detail="Only failed or cancelled runs can be retried")
    run.status = "queued"
    run.progress = 0.0
    run.error_message = None
    run.completed_at = None
    run.duration_seconds = None
    run.worker_id = None
    db.commit()
    db.refresh(run)
    return run


# --- Telemetry ---

@router.get("/{run_id}/telemetry", response_model=List[TelemetryPointOut])
def get_telemetry(
    run_id: UUID,
    db: Session = Depends(get_db),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    _get_run_or_404(db, run_id)
    return (
        db.query(TelemetryPoint)
        .filter(TelemetryPoint.run_id == run_id)
        .order_by(TelemetryPoint.t_s)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{run_id}/trajectory", response_model=TrajectoryOut)
def get_trajectory(run_id: UUID, db: Session = Depends(get_db)):
    _get_run_or_404(db, run_id)
    points = (
        db.query(TelemetryPoint)
        .filter(TelemetryPoint.run_id == run_id)
        .order_by(TelemetryPoint.t_s)
        .all()
    )
    return {"run_id": run_id, "points": points}


@router.post("/{run_id}/telemetry", status_code=status.HTTP_204_NO_CONTENT)
def upload_telemetry(run_id: UUID, payload: JobTelemetry, db: Session = Depends(get_db)):
    _get_run_or_404(db, run_id)
    # Validate worker token
    from app.api.workers import _verify_worker
    _verify_worker(payload.token)
    for p in payload.points:
        db.add(TelemetryPoint(run_id=run_id, **p.model_dump()))
    db.commit()
    return None


# --- Training metrics ---

@router.get("/{run_id}/training", response_model=List[TrainingMetricOut])
def get_training(
    run_id: UUID,
    db: Session = Depends(get_db),
    limit: int = Query(1000, ge=1, le=10000),
):
    _get_run_or_404(db, run_id)
    return (
        db.query(TrainingMetric)
        .filter(TrainingMetric.run_id == run_id)
        .order_by(TrainingMetric.episode)
        .limit(limit)
        .all()
    )


@router.post("/{run_id}/training", status_code=status.HTTP_204_NO_CONTENT)
def upload_training(run_id: UUID, payload: JobTraining, db: Session = Depends(get_db)):
    _get_run_or_404(db, run_id)
    from app.api.workers import _verify_worker
    _verify_worker(payload.token)
    for m in payload.metrics:
        db.add(TrainingMetric(run_id=run_id, **m.model_dump()))
    db.commit()
    return None


# --- Logs ---

@router.get("/{run_id}/logs")
def get_logs(
    run_id: UUID,
    db: Session = Depends(get_db),
    limit: int = Query(500, ge=1, le=5000),
):
    _get_run_or_404(db, run_id)
    return (
        db.query(RunLog)
        .filter(RunLog.run_id == run_id)
        .order_by(RunLog.t_s.desc())
        .limit(limit)
        .all()
    )


@router.post("/{run_id}/logs", status_code=status.HTTP_204_NO_CONTENT)
def add_log(run_id: UUID, level: str, message: str, db: Session = Depends(get_db)):
    _get_run_or_404(db, run_id)
    db.add(RunLog(run_id=run_id, level=level, message=message))
    db.commit()
    return None


# --- Worker job endpoints ---

@router.post("/{run_id}/progress", status_code=status.HTTP_204_NO_CONTENT)
def job_progress(run_id: UUID, payload: JobProgress, db: Session = Depends(get_db)):
    from app.api.workers import _verify_worker
    _verify_worker(payload.token)
    run = _get_run_or_404(db, run_id)
    run.progress = payload.progress
    if payload.log:
        db.add(RunLog(run_id=run_id, level="info", message=payload.log))
    db.commit()
    return None


@router.post("/{run_id}/result", status_code=status.HTTP_204_NO_CONTENT)
def job_result(run_id: UUID, payload: JobResult, db: Session = Depends(get_db)):
    from app.api.workers import _verify_worker
    _verify_worker(payload.token)
    run = _get_run_or_404(db, run_id)
    run.status = payload.status
    run.metrics = payload.metrics
    run.error_message = payload.error_message
    run.duration_seconds = payload.duration_seconds
    if payload.status == "completed":
        from sqlalchemy import func
        run.completed_at = func.now()
    db.commit()
    return None
