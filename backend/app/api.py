"""API endpoints.

FastAPI APIs used:
- query parameters (optional ?controller= filter):
  https://fastapi.tiangolo.com/tutorial/query-params/
- HTTPException for 404 on a missing run:
  https://fastapi.tiangolo.com/tutorial/handling-errors/
- response_model with Pydantic models (docs above).
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.database import connect
from app.models import Band, Health, Run, RunDetail, SummaryRow

router = APIRouter()


@router.get("/health", response_model=Health)
def health():
    return Health(status="ok")


@router.get("/runs", response_model=list[Run])
def list_runs(controller: Optional[str] = Query(default=None)):
    conn = connect()
    try:
        if controller is not None:
            rows = conn.execute(
                "SELECT * FROM runs WHERE controller = ? ORDER BY id", (controller,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM runs ORDER BY id").fetchall()
    finally:
        conn.close()
    return [Run.model_validate(dict(r)) for r in rows]


@router.get("/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: int):
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="run not found")
        bands = conn.execute(
            "SELECT alt_min, alt_max, games, landings "
            "FROM altitude_bands WHERE run_id = ? ORDER BY alt_min",
            (run_id,),
        ).fetchall()
    finally:
        conn.close()
    data = dict(row)
    data["bands"] = [Band.model_validate(dict(b)) for b in bands]
    return RunDetail.model_validate(data)


@router.get("/summary", response_model=list[SummaryRow])
def summary():
    # One row per (controller, obs_mode).  PPO basic and PPO extended are
    # never merged: obs_mode is part of the GROUP BY key.  NULL obs_mode
    # (hand_rule / random) forms its own group per controller.
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT controller, obs_mode, COUNT(*) AS n_runs,
                   AVG(landings * 100.0 / games) AS avg_landing_rate,
                   MIN(landings * 100.0 / games) AS min_landing_rate,
                   MAX(landings * 100.0 / games) AS max_landing_rate
            FROM runs
            GROUP BY controller, obs_mode
            ORDER BY controller, obs_mode
            """
        ).fetchall()
    finally:
        conn.close()
    return [SummaryRow.model_validate(dict(r)) for r in rows]
