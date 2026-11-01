"""Database models for RocketLab."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    algorithm = Column(String(100), nullable=False, index=True)  # ppo, hand_rule, random, demo
    obs_mode = Column(String(50), nullable=True)  # basic, extended, null
    seed = Column(Integer, nullable=True)
    config = Column(JSONB, nullable=True)  # versioned experiment configuration
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id", ondelete="SET NULL"), nullable=True, index=True)

    status = Column(Enum("queued", "running", "completed", "failed", "cancelled", name="run_status"), nullable=False, default="queued", index=True)
    progress = Column(Float, default=0.0, nullable=False)

    # Simulation parameters
    algorithm = Column(String(100), nullable=False)
    obs_mode = Column(String(50), nullable=True)
    seed = Column(Integer, nullable=True)
    config = Column(JSONB, nullable=True)

    # Results (populated on completion)
    metrics = Column(JSONB, nullable=True)  # landing_success, touchdown_velocity, etc.
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    experiment = relationship("Experiment", back_populates="runs")
    worker = relationship("Worker", back_populates="runs", foreign_keys=[worker_id])
    telemetry = relationship("TelemetryPoint", back_populates="run", cascade="all, delete-orphan")
    training_metrics = relationship("TrainingMetric", back_populates="run", cascade="all, delete-orphan")
    logs = relationship("RunLog", back_populates="run", cascade="all, delete-orphan")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    hostname = Column(String(255), nullable=False)
    cpu_info = Column(String(255), nullable=True)
    token = Column(String(255), nullable=False)
    status = Column(Enum("online", "offline", "busy", name="worker_status"), nullable=False, default="offline", index=True)
    current_job_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="SET NULL"), nullable=True)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    runs = relationship("Run", back_populates="worker", foreign_keys="Run.worker_id")
    current_job = relationship("Run", foreign_keys=[current_job_id])


class TelemetryPoint(Base):
    __tablename__ = "telemetry_points"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True)
    t_s = Column(Float, nullable=False)
    x_m = Column(Float, nullable=False)
    y_m = Column(Float, nullable=False)
    z_m = Column(Float, nullable=False)
    vx_mps = Column(Float, nullable=False)
    vy_mps = Column(Float, nullable=False)
    vz_mps = Column(Float, nullable=False)
    altitude_m = Column(Float, nullable=False)
    speed_mps = Column(Float, nullable=False)
    fuel_kg = Column(Float, nullable=False)
    throttle = Column(Float, nullable=False)
    tilt_deg = Column(Float, nullable=False)

    run = relationship("Run", back_populates="telemetry")

    __table_args__ = (
        # Index for efficient trajectory queries
        {"postgresql_partition_by": None},
    )


class TrainingMetric(Base):
    __tablename__ = "training_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True)
    episode = Column(Integer, nullable=False)
    reward = Column(Float, nullable=False)
    avg_reward = Column(Float, nullable=True)
    policy_loss = Column(Float, nullable=True)
    value_loss = Column(Float, nullable=True)
    episode_length = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)
    t_s = Column(Float, nullable=False)

    run = relationship("Run", back_populates="training_metrics")


class RunLog(Base):
    __tablename__ = "run_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(String(20), nullable=False, default="info")
    message = Column(Text, nullable=False)
    t_s = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    run = relationship("Run", back_populates="logs")
