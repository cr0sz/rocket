"""Pydantic schemas for RocketLab API."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# --- Experiment schemas ---

class ExperimentBase(BaseModel):
    name: str
    description: Optional[str] = None
    algorithm: str
    obs_mode: Optional[str] = None
    seed: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    is_demo: bool = False


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    algorithm: Optional[str] = None
    obs_mode: Optional[str] = None
    seed: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    is_demo: Optional[bool] = None


class ExperimentOut(ExperimentBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- Run schemas ---

class RunBase(BaseModel):
    experiment_id: UUID
    algorithm: str
    obs_mode: Optional[str] = None
    seed: Optional[int] = None
    config: Optional[Dict[str, Any]] = None


class RunCreate(RunBase):
    pass


class RunUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None


class RunOut(RunBase):
    id: UUID
    worker_id: Optional[UUID] = None
    status: str
    progress: float
    metrics: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Telemetry schemas ---

class TelemetryPointBase(BaseModel):
    t_s: float
    x_m: float
    y_m: float
    z_m: float
    vx_mps: float
    vy_mps: float
    vz_mps: float
    altitude_m: float
    speed_mps: float
    fuel_kg: float
    throttle: float
    tilt_deg: float


class TelemetryPointOut(TelemetryPointBase):
    id: int
    run_id: UUID

    model_config = ConfigDict(from_attributes=True)


class TrajectoryOut(BaseModel):
    run_id: UUID
    points: List[TelemetryPointOut]


# --- Training schemas ---

class TrainingMetricBase(BaseModel):
    episode: int
    reward: float
    avg_reward: Optional[float] = None
    policy_loss: Optional[float] = None
    value_loss: Optional[float] = None
    episode_length: Optional[float] = None
    success_rate: Optional[float] = None
    t_s: float


class TrainingMetricOut(TrainingMetricBase):
    id: int
    run_id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- Log schemas ---

class RunLogBase(BaseModel):
    level: str = "info"
    message: str


class RunLogOut(RunLogBase):
    id: int
    run_id: UUID
    t_s: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Worker schemas ---

class WorkerBase(BaseModel):
    name: str
    hostname: str
    cpu_info: Optional[str] = None
    token: str


class WorkerRegister(WorkerBase):
    pass


class WorkerOut(WorkerBase):
    id: UUID
    status: str
    current_job_id: Optional[UUID] = None
    last_heartbeat: Optional[datetime] = None
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkerHeartbeat(BaseModel):
    token: str
    status: str = "online"
    current_job_id: Optional[UUID] = None


# --- Worker job claim / results ---

class JobClaim(BaseModel):
    token: str
    run_id: Optional[UUID] = None
    algorithm: Optional[str] = None
    obs_mode: Optional[str] = None
    seed: Optional[int] = None
    config: Optional[Dict[str, Any]] = None


class JobProgress(BaseModel):
    token: str
    run_id: UUID
    progress: float
    log: Optional[str] = None


class JobResult(BaseModel):
    token: str
    run_id: UUID
    status: str  # completed or failed
    metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None


class JobTelemetry(BaseModel):
    token: str
    run_id: UUID
    points: List[TelemetryPointBase]


class JobTraining(BaseModel):
    token: str
    run_id: UUID
    metrics: List[TrainingMetricBase]


# --- Dashboard summary ---

class DashboardSummary(BaseModel):
    total_experiments: int
    total_runs: int
    landing_success_rate: float
    best_touchdown_velocity: Optional[float] = None
    best_horizontal_error: Optional[float] = None
    active_workers: int
    recent_runs: List[RunOut]


# --- Comparison ---

class ComparisonRun(BaseModel):
    id: UUID
    experiment_name: str
    algorithm: str
    seed: Optional[int]
    status: str
    metrics: Optional[Dict[str, Any]] = None
    trajectory: Optional[List[TelemetryPointOut]] = None

    model_config = ConfigDict(from_attributes=True)
