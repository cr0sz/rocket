"""Seed the SQLite database from results.json (built-in sqlite3 only).

Usage:
    python seed_db.py                       # AERORL_RESULTS_JSON / AERORL_DB_PATH env vars
    python seed_db.py results.json aerorl.db

Idempotent: re-running clears and reloads both tables.
"""
import json
import os
import sys

from app.database import connect, init_db

DEFAULT_RESULTS = "results.json"
DEFAULT_DB = "aerorl.db"


def load(results_path: str, db_path: str) -> int:
    with open(results_path) as f:
        records = json.load(f)

    conn = connect(db_path)
    try:
        init_db(conn)
        conn.execute("DELETE FROM altitude_bands")
        conn.execute("DELETE FROM runs")
        for r in records:
            cur = conn.execute(
                "INSERT INTO runs "
                "(controller, obs_mode, seed, eval_seed, games, landings) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (r["controller"], r["obs_mode"], r["seed"], r["eval_seed"],
                 r["games"], r["landings"]),
            )
            run_id = cur.lastrowid
            for b in r["bands"]:
                conn.execute(
                    "INSERT INTO altitude_bands "
                    "(run_id, alt_min, alt_max, games, landings) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (run_id, b["alt_min"], b["alt_max"], b["games"], b["landings"]),
                )
        conn.commit()
    finally:
        conn.close()
    return len(records)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    results_path = argv[0] if len(argv) > 0 else os.environ.get(
        "AERORL_RESULTS_JSON", DEFAULT_RESULTS)
    db_path = argv[1] if len(argv) > 1 else os.environ.get(
        "AERORL_DB_PATH", DEFAULT_DB)
    n = load(results_path, db_path)
    print(f"seeded {n} runs into {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
