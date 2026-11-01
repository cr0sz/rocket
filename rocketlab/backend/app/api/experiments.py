"""Experiment API routes."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models import Experiment, Run
from app.schemas import (
    ExperimentCreate,
    ExperimentOut,
    ExperimentUpdate,
    RunOut,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.post("", response_model=ExperimentOut, status_code=status.HTTP_201_CREATED)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)):
    exp = Experiment(
        name=payload.name,
        description=payload.description,
        algorithm=payload.algorithm,
        obs_mode=payload.obs_mode,
        seed=payload.seed,
        config=payload.config,
        is_demo=payload.is_demo,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.get("", response_model=List[ExperimentOut])
def list_experiments(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    algorithm: Optional[str] = Query(None),
    is_demo: Optional[bool] = Query(None),
):
    q = db.query(Experiment)
    if algorithm:
        q = q.filter(Experiment.algorithm == algorithm)
    if is_demo is not None:
        q = q.filter(Experiment.is_demo == is_demo)
    return q.offset(skip).limit(limit).all()


@router.get("/{experiment_id}", response_model=ExperimentOut)
def get_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    exp = db.get(Experiment, experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.patch("/{experiment_id}", response_model=ExperimentOut)
def update_experiment(
    experiment_id: UUID, payload: ExperimentUpdate, db: Session = Depends(get_db)
):
    exp = db.get(Experiment, experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(exp, field, value)
    db.commit()
    db.refresh(exp)
    return exp


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment(experiment_id: UUID, db: Session = Depends(get_db)):
    exp = db.get(Experiment, experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    db.delete(exp)
    db.commit()
    return None


@router.get("/{experiment_id}/runs", response_model=List[RunOut])
def list_experiment_runs(experiment_id: UUID, db: Session = Depends(get_db)):
    exp = db.get(Experiment, experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return (
        db.query(Run)
        .filter(Run.experiment_id == experiment_id)
        .order_by(Run.created_at.desc())
        .all()
    )
