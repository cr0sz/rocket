"""RocketLab distributed worker.
Runs on the user's local machine (Windows/Linux), connects to the RocketLab API,
claims queued simulation jobs, runs them locally, and streams results back.

Usage:
    python -m rocketlab_worker register --name "my-laptop" --token <token> --api-url http://localhost:8080
    python -m rocketlab_worker run --token <token> --api-url http://localhost:8080
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from rocketlab_worker.adapter_registry import get_adapter, DemoSimulationAdapter, AeroRocketAdapter, SimulationAdapter


class WorkerClient:
    def __init__(self, api_url: str, token: str, name: str, hostname: str, cpu_info: str):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.name = name
        self.hostname = hostname
        self.cpu_info = cpu_info
        self.worker_id: Optional[str] = None

    def register(self) -> str:
        payload = {
            "name": self.name,
            "hostname": self.hostname,
            "cpu_info": self.cpu_info,
            "token": self.token,
        }
        r = requests.post(f"{self.api_url}/api/v1/workers/register", json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        self.worker_id = data["id"]
        print(f"[worker] registered as {self.name} (id={self.worker_id})")
        return self.worker_id

    def heartbeat(self, status: str = "online", current_job_id: Optional[str] = None):
        if not self.worker_id:
            return
        try:
            requests.post(
                f"{self.api_url}/api/v1/workers/heartbeat",
                json={"token": self.token, "status": status, "current_job_id": current_job_id},
                timeout=10,
            )
        except Exception as e:
            print(f"[worker] heartbeat failed: {e}")

    def claim(self) -> Optional[Dict[str, Any]]:
        try:
            r = requests.post(
                f"{self.api_url}/api/v1/workers/claim",
                json={"token": self.token},
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                return data.get("job")
        except Exception as e:
            print(f"[worker] claim failed: {e}")
        return None

    def report_progress(self, run_id: str, progress: float, log: Optional[str] = None):
        try:
            requests.post(
                f"{self.api_url}/api/v1/runs/{run_id}/progress",
                json={"token": self.token, "run_id": run_id, "progress": progress, "log": log},
                timeout=10,
            )
        except Exception as e:
            print(f"[worker] progress report failed: {e}")

    def report_result(self, run_id: str, status: str, metrics: Optional[Dict] = None,
                      error_message: Optional[str] = None, duration_seconds: Optional[float] = None):
        try:
            requests.post(
                f"{self.api_url}/api/v1/runs/{run_id}/result",
                json={
                    "token": self.token,
                    "run_id": run_id,
                    "status": status,
                    "metrics": metrics,
                    "error_message": error_message,
                    "duration_seconds": duration_seconds,
                },
                timeout=30,
            )
        except Exception as e:
            print(f"[worker] result report failed: {e}")

    def upload_telemetry(self, run_id: str, points: List[Dict[str, Any]]):
        if not points:
            return
        try:
            requests.post(
                f"{self.api_url}/api/v1/runs/{run_id}/telemetry",
                json={"token": self.token, "run_id": run_id, "points": points},
                timeout=30,
            )
        except Exception as e:
            print(f"[worker] telemetry upload failed: {e}")

    def upload_training(self, run_id: str, metrics: List[Dict[str, Any]]):
        if not metrics:
            return
        try:
            requests.post(
                f"{self.api_url}/api/v1/runs/{run_id}/training",
                json={"token": self.token, "run_id": run_id, "metrics": metrics},
                timeout=30,
            )
        except Exception as e:
            print(f"[worker] training upload failed: {e}")

    def run_loop(self, poll_interval: float = 3.0):
        print(f"[worker] {self.name} polling for jobs every {poll_interval}s…")
        while True:
            self.heartbeat("online", None)
            job = self.claim()
            if job:
                self.handle_job(job)
            else:
                print("[worker] no jobs available, waiting…")
            time.sleep(poll_interval)

    def handle_job(self, job: Dict[str, Any]):
        run_id = job["run_id"]
        algorithm = job["algorithm"]
        obs_mode = job.get("obs_mode")
        seed = job.get("seed")
        config = job.get("config") or {}

        print(f"[worker] claimed job {run_id}: {algorithm} seed={seed}")
        self.heartbeat("busy", run_id)
        self.report_progress(run_id, 0.0, f"Starting {algorithm} simulation (seed={seed})")

        start = time.time()
        try:
            adapter = get_adapter(algorithm, model_dir=os.environ.get("MODEL_DIR", "."))
            result = adapter.run(
                algorithm=algorithm,
                seed=seed or 0,
                obs_mode=obs_mode,
                config=config,
                progress_callback=lambda p, log: self.report_progress(run_id, p, log),
            )

            duration = time.time() - start
            self.upload_telemetry(run_id, result.get("trajectory", []))
            self.upload_training(run_id, result.get("training", []))
            self.report_result(
                run_id,
                "completed",
                metrics=result.get("metrics", {}),
                duration_seconds=duration,
            )
            print(f"[worker] job {run_id} completed in {duration:.1f}s")
        except Exception as e:
            duration = time.time() - start
            print(f"[worker] job {run_id} failed: {e}")
            self.report_result(run_id, "failed", error_message=str(e), duration_seconds=duration)
        finally:
            self.heartbeat("online", None)


def main():
    parser = argparse.ArgumentParser(prog="rocketlab_worker")
    sub = parser.add_subparsers(dest="command", required=True)

    p_reg = sub.add_parser("register", help="Register this worker with the API")
    p_reg.add_argument("--name", required=True)
    p_reg.add_argument("--hostname", default=platform.node())
    p_reg.add_argument("--cpu-info", default=platform.processor() or "unknown")
    p_reg.add_argument("--token", required=True)
    p_reg.add_argument("--api-url", required=True)

    p_run = sub.add_parser("run", help="Start the worker job loop")
    p_run.add_argument("--token", required=True)
    p_run.add_argument("--api-url", required=True)
    p_run.add_argument("--name", default=platform.node())
    p_run.add_argument("--hostname", default=platform.node())
    p_run.add_argument("--cpu-info", default=platform.processor() or "unknown")

    args = parser.parse_args()

    if args.command == "register":
        client = WorkerClient(args.api_url, args.token, args.name, args.hostname, args.cpu_info)
        client.register()
    elif args.command == "run":
        client = WorkerClient(args.api_url, args.token, args.name, args.hostname, args.cpu_info)
        if not client.worker_id:
            client.register()
        client.run_loop()


if __name__ == "__main__":
    main()
