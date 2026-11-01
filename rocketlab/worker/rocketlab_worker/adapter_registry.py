"""Simulation adapter registry for the worker.

Picks the best available adapter for each algorithm:
  - ppo_basic / ppo_extended -> AeroRocketAdapter (real PPO models) if model
    files exist, else DemoSimulationAdapter
  - hand_rule / random -> AeroRocketAdapter (real physics) if importable,
    else DemoSimulationAdapter
"""
from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional

from app.adapters import (
    DemoSimulationAdapter,
    AeroRocketAdapter,
    SimulationAdapter,
)


def get_adapter(algorithm: str, model_dir: Optional[str] = None) -> SimulationAdapter:
    """Return the best adapter for the given algorithm."""
    # Try AeroRocket first if model dir has the needed files
    if model_dir is None:
        model_dir = os.environ.get("MODEL_DIR", ".")

    if algorithm in ("ppo_basic", "ppo_extended"):
        import os as _os
        ext = algorithm == "ppo_extended"
        name = "ppo_rocket_ext_seed" if ext else "ppo_rocket_seed"
        # Check if any seed model exists
        any_exists = any(
            _os.path.exists(_os.path.join(model_dir, f"{name}{s}.zip"))
            for s in range(5)
        )
        if any_exists:
            try:
                return AeroRocketAdapter(model_dir=model_dir)
            except Exception:
                pass
        return DemoSimulationAdapter()

    if algorithm in ("hand_rule", "random"):
        # Try real AeroRocket physics for hand_rule/random
        try:
            return AeroRocketAdapter(model_dir=model_dir)
        except Exception:
            return DemoSimulationAdapter()

    return DemoSimulationAdapter()


__all__ = ["get_adapter", "DemoSimulationAdapter", "AeroRocketAdapter", "SimulationAdapter"]
