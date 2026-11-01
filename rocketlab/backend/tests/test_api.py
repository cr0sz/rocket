"""Backend API tests for RocketLab.

Run from rocketlab/backend/:
    python -m pytest
"""
import os
import sys
import uuid

# Force SQLite for tests (no PostgreSQL needed)
os.environ["DATABASE_URL"] = "sqlite:///./test_rocketlab.db"
os.environ["SEED_DEMO_DATA"] = "false"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.core.database import SessionLocal, engine, Base  # noqa: E402
from app.models import Experiment, Run  # noqa: E402


def setup_module(module):
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("./test_rocketlab.db")
    except OSError:
        pass


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_experiment():
    r = client.post("/api/v1/experiments", json={
        "name": "Test Exp",
        "algorithm": "ppo_basic",
        "obs_mode": "basic",
        "seed": 0,
        "is_demo": False,
    })
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Test Exp"
    assert data["algorithm"] == "ppo_basic"
    assert "id" in data


def test_list_experiments():
    r = client.get("/api/v1/experiments")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_experiment_not_found():
    r = client.get(f"/api/v1/experiments/{uuid.uuid4()}")
    assert r.status_code == 404


def test_create_run():
    # Create experiment first
    er = client.post("/api/v1/experiments", json={
        "name": "Exp for run",
        "algorithm": "random",
        "obs_mode": None,
        "seed": 1,
        "is_demo": True,
    })
    exp_id = er.json()["id"]

    r = client.post("/api/v1/runs", json={
        "experiment_id": exp_id,
        "algorithm": "random",
        "obs_mode": None,
        "seed": 1,
    })
    assert r.status_code == 201, r.text
    run = r.json()
    assert run["status"] == "queued"
    assert run["progress"] == 0.0
    return run["id"]


def test_list_runs():
    r = client.get("/api/v1/runs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_run_crud_flow():
    # Create experiment
    er = client.post("/api/v1/experiments", json={
        "name": "CRUD Exp",
        "algorithm": "hand_rule",
        "obs_mode": None,
        "seed": 0,
        "is_demo": True,
    })
    exp_id = er.json()["id"]

    # Create run
    rr = client.post("/api/v1/runs", json={
        "experiment_id": exp_id,
        "algorithm": "hand_rule",
        "obs_mode": None,
        "seed": 0,
    })
    run_id = rr.json()["id"]

    # Get run
    gr = client.get(f"/api/v1/runs/{run_id}")
    assert gr.status_code == 200
    assert gr.json()["id"] == run_id

    # Update progress
    pr = client.post(f"/api/v1/runs/{run_id}/progress", json={
        "token": "worker-change-me",
        "run_id": run_id,
        "progress": 50.0,
        "log": "halfway",
    })
    assert pr.status_code == 204

    # Complete run
    cr = client.post(f"/api/v1/runs/{run_id}/result", json={
        "token": "worker-change-me",
        "run_id": run_id,
        "status": "completed",
        "metrics": {"landing_success": True, "touchdown_velocity_mps": 5.0},
        "duration_seconds": 10.0,
    })
    assert cr.status_code == 204

    # Verify completed
    gr2 = client.get(f"/api/v1/runs/{run_id}")
    assert gr2.json()["status"] == "completed"
    assert gr2.json()["metrics"]["landing_success"] is True


def test_cancel_run():
    er = client.post("/api/v1/experiments", json={
        "name": "Cancel Exp",
        "algorithm": "random",
        "obs_mode": None,
        "seed": 0,
        "is_demo": True,
    })
    exp_id = er.json()["id"]
    rr = client.post("/api/v1/runs", json={
        "experiment_id": exp_id,
        "algorithm": "random",
        "obs_mode": None,
        "seed": 0,
    })
    run_id = rr.json()["id"]

    cr = client.post(f"/api/v1/runs/{run_id}/cancel")
    assert cr.status_code == 200
    assert cr.json()["status"] == "cancelled"


def test_retry_failed_run():
    er = client.post("/api/v1/experiments", json={
        "name": "Retry Exp",
        "algorithm": "random",
        "obs_mode": None,
        "seed": 0,
        "is_demo": True,
    })
    exp_id = er.json()["id"]
    rr = client.post("/api/v1/runs", json={
        "experiment_id": exp_id,
        "algorithm": "random",
        "obs_mode": None,
        "seed": 0,
    })
    run_id = rr.json()["id"]

    # Mark as failed
    client.post(f"/api/v1/runs/{run_id}/result", json={
        "token": "worker-change-me",
        "run_id": run_id,
        "status": "failed",
        "error_message": "sim crashed",
    })

    # Retry
    rr2 = client.post(f"/api/v1/runs/{run_id}/retry")
    assert rr2.status_code == 200
    assert rr2.json()["status"] == "queued"
    assert rr2.json()["progress"] == 0.0


def test_worker_register_and_claim():
    # Register worker
    wr = client.post("/api/v1/workers/register", json={
        "name": "test-worker",
        "hostname": "test-host",
        "cpu_info": "x86_64",
        "token": "worker-change-me",
    })
    assert wr.status_code == 201, wr.text

    # Create a queued run
    er = client.post("/api/v1/experiments", json={
        "name": "Claim Exp",
        "algorithm": "random",
        "obs_mode": None,
        "seed": 0,
        "is_demo": True,
    })
    exp_id = er.json()["id"]
    client.post("/api/v1/runs", json={
        "experiment_id": exp_id,
        "algorithm": "random",
        "obs_mode": None,
        "seed": 0,
    })

    # Claim job
    cr = client.post("/api/v1/workers/claim", json={"token": "worker-change-me"})
    assert cr.status_code == 200
    job = cr.json()
    assert "job" in job
    assert job["job"] is not None
    assert "run_id" in job["job"]

    # List workers
    wl = client.get("/api/v1/workers")
    assert wl.status_code == 200
    assert len(wl.json()) >= 1


def test_dashboard_summary():
    r = client.get("/api/v1/dashboard/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_experiments" in data
    assert "total_runs" in data
    assert "landing_success_rate" in data
    assert "active_workers" in data


def test_delete_experiment():
    er = client.post("/api/v1/experiments", json={
        "name": "Delete Exp",
        "algorithm": "random",
        "obs_mode": None,
        "seed": 0,
        "is_demo": True,
    })
    exp_id = er.json()["id"]

    dr = client.delete(f"/api/v1/experiments/{exp_id}")
    assert dr.status_code == 204

    gr = client.get(f"/api/v1/experiments/{exp_id}")
    assert gr.status_code == 404
