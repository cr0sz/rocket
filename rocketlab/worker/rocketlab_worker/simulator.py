"""Demo simulation adapter - produces deterministic illustrative rocket flight data."""
from __future__ import annotations

import random
import time
from typing import Any, Callable, Dict, List, Optional


class SimulationAdapter:
    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True

    def run(self, algorithm: str, seed: int, obs_mode: Optional[str] = None,
            config: Optional[Dict[str, Any]] = None,
            progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        raise NotImplementedError


def _log(message: str, callback: Optional[Callable[[float, str], None]], progress: float):
    if callback:
        callback(progress, message)
    print(f"[sim] {message}")


class DemoSimulationAdapter(SimulationAdapter):
    """Deterministic demo rocket landing simulator (no GPU, no ML)."""

    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True

    def run(self, algorithm: str, seed: int, obs_mode: Optional[str] = None,
            config: Optional[Dict[str, Any]] = None,
            progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        rng = random.Random(seed)
        start_alt = rng.uniform(400, 600)
        gravity = 9.8
        thrust = 20.0
        fuel_per_burn = 5.0
        max_safe_speed = 10.0
        fuel = 100.0
        altitude = start_alt
        speed = 0.0
        t = 0.0
        dt = 1.0
        points: List[Dict[str, Any]] = []
        landed = False
        crash_speed = 0.0

        _log("Simulation start", progress_callback, 0)

        while altitude > 0 and t < 300:
            burn = False
            if algorithm == "random":
                burn = rng.random() < 0.5
            elif algorithm == "hand_rule":
                burn = altitude < 5.0 * speed - 20.0
            elif algorithm in ("ppo_extended", "ppo_basic"):
                burn = (speed > 15 or altitude < 100) or (rng.random() < 0.05)
            else:
                burn = rng.random() < 0.5

            if burn and fuel > 0:
                speed -= thrust
                fuel = max(0, fuel - fuel_per_burn * dt)
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

            if int(t) % 10 == 0:
                _log(f"t={t:.0f}s alt={max(0,altitude):.0f}m speed={abs(speed):.1f}m/s",
                     progress_callback, min(95, t / 300 * 100))

            if altitude <= 0:
                landed = abs(speed) <= max_safe_speed
                crash_speed = abs(speed)
                break

    # Handle case where loop exits without landing (timeout)
        if not landed and altitude > 0:
            landed = False
            crash_speed = abs(speed)

        metrics = {
            "landing_success": landed,
            "touchdown_velocity_mps": round(crash_speed, 2),
            "horizontal_error_m": round(rng.uniform(0.5, 50.0), 2),
            "fuel_used_kg": round(100.0 - fuel, 2),
            "max_altitude_m": round(start_alt, 2),
            "duration_s": round(t, 2),
            "start_altitude_m": round(start_alt, 2),
            "fuel_remaining_kg": round(fuel, 2),
        }

        training: List[Dict[str, Any]] = []
        if algorithm.startswith("ppo"):
            ep_reward = -50.0 if not landed else 50.0
            for ep in range(1, 51):
                ep_reward += rng.uniform(-5, 15)
                training.append({
                    "episode": ep,
                    "reward": round(ep_reward, 2),
                    "avg_reward": round(ep_reward + rng.uniform(-2, 2), 2),
                    "policy_loss": round(rng.uniform(0.01, 0.5), 4),
                    "value_loss": round(rng.uniform(0.01, 0.5), 4),
                    "episode_length": round(t, 1),
                    "success_rate": round(min(1.0, ep / 50.0), 3),
                    "t_s": round(ep * t / 50.0, 3),
                })

        _log("Simulation complete", progress_callback, 100)
        return {
            "metrics": metrics,
            "trajectory": points,
            "training": training,
            "logs": [],
            "duration": round(t, 2),
        }
