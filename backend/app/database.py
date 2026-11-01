"""SQLite connection helpers.

The database path comes from the ``AERORL_DB_PATH`` environment variable
(default ``aerorl.db``).  It is read on every connection so tests can point
the app at an isolated temp database without re-importing the module.
"""
import os
import sqlite3

DB_PATH_ENV = "AERORL_DB_PATH"
DEFAULT_DB_PATH = "aerorl.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    controller TEXT NOT NULL,
    obs_mode TEXT,
    seed INTEGER,
    eval_seed INTEGER NOT NULL,
    games INTEGER NOT NULL,
    landings INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS altitude_bands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    alt_min INTEGER NOT NULL,
    alt_max INTEGER NOT NULL,
    games INTEGER NOT NULL,
    landings INTEGER NOT NULL
);
"""


def get_db_path() -> str:
    return os.environ.get(DB_PATH_ENV, DEFAULT_DB_PATH)


def connect(db_path: str | None = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
