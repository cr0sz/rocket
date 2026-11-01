"""Seed deterministic demo data into RocketLab.

Creates demo experiments with simulated rocket landing runs, telemetry,
training metrics, and logs so the dashboard is immediately useful.
All data is clearly labelled DEMO.
"""
import json
import math
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, "/app")

from app.core.database import SessionLocal, engine, Base
from app.core.config import settings
from app.models import Experiment, Run, TelemetryPoint, TrainingMetric, RunLog, Worker


def simulate_rocket_flight(algorithm: str, seed: int, obs_mode: str = None) -> dict:
    """Deterministic demo rocket flight simulation."""
    rng = random.Random(seed)
    start_alt = rng.uniform(400, 600)
    gravity = 9.8
    thrust = 20.0
    fuel_per_burn = 5
    max_safe_speed = 10.0
    fuel = 100.0  # kg
    altitude = start_alt
    speed = 0.0
    t = 0.0
    dt = 1.0
    points = []
    events = []

    # Algorithm-specific behavior
    if algorithm == "random":
        burn_threshold = 0.5
    elif algorithm == "hand_rule":
        c, d = 5.0, -20.0
        burn_threshold = None
    elif algorithm == "ppo_extended":
        burn_threshold = None  # smart controller
    elif algorithm == "ppo_basic":
        burn_threshold = None
    else:
        burn_threshold = 0.5

    landed = False
    crash_speed = 0.0

    while altitude > 0 and t < 300:
        # Decide burn
        burn = False
        if algorithm == "random":
            burn = rng.random() < 0.5
        elif algorithm == "hand_rule":
            burn = altitude < c * speed + d
        elif algorithm in ("ppo_extended", "ppo_basic"):
            # Smart-ish: burn when speed is high or altitude is low
            # Plus some noise for realism
            needed_burn = speed > 15 or altitude < 100
            burn = needed_burn or (rng.random() < 0.05)

        if burn and fuel > 0:
            speed -= thrust
            fuel -= fuel_per_burn * dt
            fuel = max(0, fuel)
        speed += gravity * dt
        altitude -= speed * dt
        t += dt

        points.append({
            "t_s": round(t, 3),
            "x_m": round(rng.uniform(-50, 50), 3),
            "y_m": round(rng.uniform(-50, 50), 3),
            "z_m": round(max(0, altitude), 3),
            "vx_mps": round(rng.uniform(-5, 5), 3),
            "vy_mps": round(rng.uniform(-5, 5), 3),
            "vz_mps": round(speed, 3),
            "altitude_m": round(max(0, altitude), 3),
            "speed_mps": round(abs(speed), 3),
            "fuel_kg": round(fuel, 3),
            "throttle": round(1.0 if burn else 0.0, 3),
            "tilt_deg": round(rng.uniform(-10, 10), 3),
        })

        if altitude <= 0:
            landed = speed <= max_safe_speed
            crash_speed = abs(speed)
            break

    # Metrics
    horizontal_error = round(rng.uniform(0.5, 50.0), 2)
    touchdown_velocity = round(crash_speed, 2)
    fuel_used = round(100.0 - fuel, 2)
    max_altitude = round(start_alt, 2)
    duration = round(t, 2)

    metrics = {
        "landing_success": landed,
        "touchdown_velocity_mps": touchdown_velocity,
        "horizontal_error_m": horizontal_error,
        "fuel_used_kg": fuel_used,
        "max_altitude_m": max_altitude,
        "duration_s": duration,
        "start_altitude_m": round(start_alt, 2),
        "fuel_remaining_kg": round(fuel, 2),
    }

    # Training metrics (only for PPO algorithms)
    training = []
    if algorithm.startswith("ppo"):
        ep_reward = -50.0 if not landed else 50.0
        for ep in range(1, 51):
            ep_reward += rng.uniform(-5, 15)
            avg = ep_reward + rng.uniform(-2, 2)
            training.append({
                "episode": ep,
                "reward": round(ep_reward, 2),
                "avg_reward": round(avg, 2),
                "policy_loss": round(rng.uniform(0.01, 0.5), 4),
                "value_loss": round(rng.uniform(0.01, 0.5), 4),
                "episode_length": round(t, 1),
                "success_rate": round(min(1.0, ep / 50.0), 3),
                "t_s": round(ep * t / 50.0, 3),
            })

    # Logs
    logs = [
        {"level": "info", "message": f"Simulation started: {algorithm} (seed={seed})"},
        {"level": "info", "message": f"Start altitude: {start_alt:.1f} m"},
    ]
    if landed:
        logs.append({"level": "info", "message": f"Landed safely at {touchdown_velocity:.1f} m/s"})
    else:
        logs.append({"level": "error", "message": f"Crashed at {touchdown_velocity:.1f} m/s"})

    return {
        "metrics": metrics,
        "trajectory": points,
        "training": training,
        "logs": logs,
        "duration": duration,
    }


def seed_demo(db: Session):
    # Clear existing demo data
    db.query(TelemetryPoint).delete()
    db.query(TrainingMetric).delete()
    db.query(RunLog).delete()
    db.query(Run).delete()
    db.query(Experiment).filter(Experiment.is_demo == True).delete()  # noqa: E712
    db.commit()

    # Demo worker
    worker = Worker(
        name="demo-worker",
        hostname="demo-machine",
        cpu_info="ARM64 demo",
        token=settings.WORKER_TOKEN,
        status="online",
        last_heartbeat=datetime.now(timezone.utc),
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)

    configs = [
        {"name": "PPO Extended - Seed Sweep", "algorithm": "ppo_extended", "obs_mode": "extended", "seeds": [0, 1, 2, 3, 4]},
        {"name": "PPO Basic - Seed Sweep", "algorithm": "ppo_basic", "obs_mode": "basic", "seeds": [0, 1, 2, 3, 4]},
        {"name": "Hand Rule Autopilot", "algorithm": "hand_rule", "obs_mode": None, "seeds": [0]},
        {"name": "Random Baseline", "algorithm": "random", "obs_mode": None, "seeds": [0, 1, 2]},
    ]

    for cfg in configs:
        exp = Experiment(
            name=cfg["name"],
            description=f"Demo experiment: {cfg['algorithm']} ({cfg['obs_mode'] or 'n/a'} obs)",
            algorithm=cfg["algorithm"],
            obs_mode=cfg["obs_mode"],
            seed=None,
            config={"demo": True, "description": cfg["description"]},
            is_demo=True,
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)

        for seed in cfg["seeds"]:
            result = simulate_rocket_flight(cfg["algorithm"], seed, cfg["obs_mode"])
            run = Run(
                experiment_id=exp.id,
                worker_id=worker.id,
                algorithm=cfg["algorithm"],
                obs_mode=cfg["obs_mode"],
                seed=seed,
                config=cfg["config"],
                status="completed",
                progress=100.0,
                metrics=result["metrics"],
                started_at=datetime.now(timezone.utc) - timedelta(seconds=result["duration"]),
                completed_at=datetime.now(timezone.utc),
                error_message=None,
                duration_seconds=result["duration"],
            )
            db.add(run)
            db.commit()
            db.refresh(run)

            # Telemetry
            for pt in result["trajectory"]:
                db.add(TelemetryPoint(run_id=run.id, **pt))
            # Training
            for tm in result["training"]:
                db.add(TrainingMetric(run_id=run.id, **tm))
            # Logs
            for lg in result["logs"]:
                db.add(RunLog(run_id=run.id, level=lg["level"], message=lg["message"]))
            db.commit()

    print(f"Seeded demo data: {len(configs)} experiments, {worker.id} worker")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if settings.SEED_DEMO_DATA.lower() == "true":
            seed_demo(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
