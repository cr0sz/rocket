"""Pydantic response models for the AeroRL Bench API.

Docs used: https://docs.pydantic.dev/latest/concepts/models/ (BaseModel)
"""
from typing import Optional

from pydantic import BaseModel


class Band(BaseModel):
    alt_min: int
    alt_max: int
    games: int
    landings: int


class Run(BaseModel):
    id: int
    controller: str
    obs_mode: Optional[str] = None
    seed: Optional[int] = None
    eval_seed: int
    games: int
    landings: int


class RunDetail(Run):
    bands: list[Band] = []


class SummaryRow(BaseModel):
    controller: str
    obs_mode: Optional[str] = None
    n_runs: int
    avg_landing_rate: float
    min_landing_rate: float
    max_landing_rate: float


class Health(BaseModel):
    status: str
