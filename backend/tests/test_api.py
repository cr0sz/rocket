"""Tests for the AeroRL Bench API.

Run from the backend/ folder:
    python -m pytest
Uses FastAPI's TestClient against an isolated temp SQLite database seeded
from results.json.  /summary assertions are computed independently from the
JSON (never copied from the API's own output).
"""
import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parent.parent
RESULTS_JSON = BACKEND_ROOT / "results.json"

# Import the app and the seeder with the backend root on sys.path.
import sys  # noqa: E402
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402
from seed_db import load as seed_load  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("AERORL_DB_PATH", db_path)
    n = seed_load(str(RESULTS_JSON), db_path)
    assert n == 12, f"expected 12 records, got {n}"
    return TestClient(app)


def load_records():
    with open(RESULTS_JSON) as f:
        return json.load(f)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_runs_shape_and_count(client):
    resp = client.get("/runs")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 12
    for r in body:
        assert set(r.keys()) == {"id", "controller", "obs_mode", "seed", "eval_seed", "games", "landings"}
        assert "bands" not in r  # list endpoint omits band data
        assert r["eval_seed"] == 123
        assert r["games"] == 2000


def test_list_runs_controller_filter(client):
    resp = client.get("/runs?controller=ppo")
    assert resp.status_code == 200
    ppo = resp.json()
    assert len(ppo) == 10
    assert all(r["controller"] == "ppo" for r in ppo)

    resp = client.get("/runs?controller=random")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_run_includes_bands(client):
    resp = client.get("/runs/1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 1
    assert body["controller"] == "ppo"
    assert body["obs_mode"] == "extended"
    assert len(body["bands"]) == 10
    for b in body["bands"]:
        assert set(b.keys()) == {"alt_min", "alt_max", "games", "landings"}
        assert b["games"] > 0
    # band sums equal the run totals
    assert sum(b["games"] for b in body["bands"]) == body["games"] == 2000
    assert sum(b["landings"] for b in body["bands"]) == body["landings"]


def test_get_run_unknown_id_404(client):
    resp = client.get("/runs/99999")
    assert resp.status_code == 404


def test_summary_matches_json(client):
    # Expected values computed independently from results.json.
    records = load_records()
    expected = {}
    for r in records:
        rate = r["landings"] / r["games"] * 100.0
        key = (r["controller"], r["obs_mode"])
        expected.setdefault(key, []).append(rate)

    resp = client.get("/summary")
    assert resp.status_code == 200
    got = {(s["controller"], s["obs_mode"]): s for s in resp.json()}

    # ppo basic and ppo extended are separate groups (never merged).
    assert ("ppo", "basic") in got
    assert ("ppo", "extended") in got
    assert ("hand_rule", None) in got
    assert ("random", None) in got

    for key, rates in expected.items():
        assert key in got, f"missing summary group {key}"
        s = got[key]
        assert s["n_runs"] == len(rates)
        assert abs(s["avg_landing_rate"] - (sum(rates) / len(rates))) < 1e-9
        assert abs(s["min_landing_rate"] - min(rates)) < 1e-9
        assert abs(s["max_landing_rate"] - max(rates)) < 1e-9
