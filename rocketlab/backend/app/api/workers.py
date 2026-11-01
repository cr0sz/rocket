"""Worker API routes - registration, heartbeat, job claim."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Run, Worker
from app.schemas import (
    JobClaim,
    JobProgress,
    JobResult,
    WorkerOut,
    WorkerRegister,
    WorkerHeartbeat,
)

router = APIRouter(prefix="/workers", tags=["workers"])


def _verify_worker(token: str):
    from app.core.config import settings
    if token != settings.WORKER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid worker token")


@router.post("/register", response_model=WorkerOut, status_code=status.HTTP_201_CREATED)
def register_worker(payload: WorkerRegister, db: Session = Depends(get_db)):
    from app.core.config import settings
    if payload.token != settings.WORKER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid worker token")
    worker = Worker(
        name=payload.name,
        hostname=payload.hostname,
        cpu_info=payload.cpu_info,
        token=payload.token,
        status="online",
        last_heartbeat=func.now(),
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.get("", response_model=List[WorkerOut])
def list_workers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return db.query(Worker).order_by(Worker.registered_at.desc()).offset(skip).limit(limit).all()


@router.get("/{worker_id}", response_model=WorkerOut)
def get_worker(worker_id: UUID, db: Session = Depends(get_db)):
    w = db.get(Worker, worker_id)
    if not w:
        raise HTTPException(status_code=404, detail="Worker not found")
    return w


@router.post("/heartbeat", status_code=status.HTTP_204_NO_CONTENT)
def heartbeat(payload: WorkerHeartbeat, db: Session = Depends(get_db)):
    _verify_worker(payload.token)
    # Find worker by token - in production we'd look up by token
    # For simplicity, find the most recent worker with this token
    w = (
        db.query(Worker)
        .filter(Worker.token == payload.token)
        .order_by(Worker.registered_at.desc())
        .first()
    )
    if not w:
        raise HTTPException(status_code=404, detail="Worker not registered")
    w.status = payload.status
    w.last_heartbeat = func.now()
    if payload.current_job_id:
        w.current_job_id = payload.current_job_id
    db.commit()
    return None


@router.post("/claim", status_code=status.HTTP_200_OK)
def claim_job(payload: JobClaim, db: Session = Depends(get_db)):
    _verify_worker(payload.token)
    # Atomically claim a queued run
    run = (
        db.query(Run)
        .filter(Run.status == "queued")
        .order_by(Run.created_at.asc())
        .with_for_update(skip_locked=True)
        .first()
    )
    if not run:
        return {"job": None}
    # Verify worker is registered
    w = (
        db.query(Worker)
        .filter(Worker.token == payload.token)
        .order_by(Worker.registered_at.desc())
        .first()
    )
    if not w:
        raise HTTPException(status_code=404, detail="Worker not registered")
    run.status = "running"
    run.progress = 0.0
    run.worker_id = w.id
    from sqlalchemy import func as sql_func
    run.started_at = sql_func.now()
    w.status = "busy"
    w.current_job_id = run.id
    db.commit()
    db.refresh(run)
    return {
        "job": {
            "run_id": str(run.id),
            "experiment_id": str(run.experiment_id),
            "algorithm": run.algorithm,
            "obs_mode": run.obs_mode,
            "seed": run.seed,
            "config": run.config,
        }
    }


@router.post("/{worker_id}/progress", status_code=status.HTTP_204_NO_CONTENT)
def worker_progress(worker_id: UUID, payload: JobProgress, db: Session = Depends(get_db)):
    _verify_worker(payload.token)
    run = db.get(Run, payload.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run.progress = payload.progress
    if payload.log:
        from app.models import RunLog
        db.add(RunLog(run_id=run.id, level="info", message=payload.log))
    db.commit()
    return None


@router.post("/{worker_id}/results", status_code=status.HTTP_204_NO_CONTENT)
def worker_results(worker_id: UUID, payload: JobResult, db: Session = Depends(get_db)):
    _verify_worker(payload.token)
    run = db.get(Run, payload.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run.status = payload.status
    run.metrics = payload.metrics
    run.error_message = payload.error_message
    run.duration_seconds = payload.duration_seconds
    if payload.status == "completed":
        run.completed_at = func.now()
    # Free the worker
    w = db.get(Worker, worker_id)
    if w:
        w.status = "online"
        w.current_job_id = None
        w.last_heartbeat = func.now()
    db.commit()
    return None


@router.post("/{worker_id}/fail", status_code=status.HTTP_204_NO_CONTENT)
def worker_fail(worker_id: UUID, payload: JobResult, db: Session = Depends(get_db)):
    _verify_worker(payload.token)
    run = db.get(Run, payload.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run.status = "failed"
    run.error_message = payload.error_message or "Worker reported failure"
    run.completed_at = func.now()
    w = db.get(Worker, worker_id)
    if w:
        w.status = "online"
        w.current_job_id = None
        w.last_heartbeat = func.now()
    db.commit()
    return None
