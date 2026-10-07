# astralmanac/store.py
"""The local store: a single SQLite database.

Every fetcher writes rows into one ``items`` table, tagged by ``source``. A row
is one thing — a launch, a close approach, a natural event — identified by a
``(source, external_id)`` pair so a re-fetch updates in place instead of
duplicating. The full upstream record is kept verbatim as JSON in ``payload``;
a few common fields are promoted to columns so the web layer can sort and
filter without parsing every blob.

SQLite is deliberate: the whole point of Astralmanac is that it is boring to
run. One file, no daemon, trivially backed up by copying it.
"""
import json
import sqlite3
import threading
from contextlib import contextmanager

from . import config

_local = threading.local()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    source       TEXT NOT NULL,
    external_id  TEXT NOT NULL,
    title        TEXT,
    event_time   TEXT,          -- ISO 8601, the moment the item is "about"
    url          TEXT,
    payload      TEXT NOT NULL, -- the full upstream record, as JSON
    fetched_at   TEXT NOT NULL, -- ISO 8601, when we last stored it
    PRIMARY KEY (source, external_id)
);
CREATE INDEX IF NOT EXISTS idx_items_source ON items(source);
CREATE INDEX IF NOT EXISTS idx_items_event_time ON items(event_time);

CREATE TABLE IF NOT EXISTS fetch_runs (
    source      TEXT PRIMARY KEY,
    last_run    TEXT,
    last_ok     TEXT,
    last_error  TEXT,
    item_count  INTEGER
);
"""


@contextmanager
def connect():
    """A thread-local SQLite connection with sane defaults."""
    conn = getattr(_local, "conn", None)
    if conn is None:
        import os
        os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
        conn = sqlite3.connect(config.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        _local.conn = conn
    yield conn


def init_db():
    with connect() as conn:
        conn.executescript(_SCHEMA)
        conn.commit()


def upsert_items(source, items):
    """Insert or update a batch of items for one source. ``items`` is an
    iterable of dicts with keys: external_id, title, event_time, url, payload,
    fetched_at. Returns the number of rows written."""
    rows = [
        (source, it["external_id"], it.get("title"), it.get("event_time"),
         it.get("url"), json.dumps(it["payload"], ensure_ascii=False), it["fetched_at"])
        for it in items
    ]
    with connect() as conn:
        conn.executemany(
            "INSERT INTO items (source, external_id, title, event_time, url, payload, fetched_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(source, external_id) DO UPDATE SET "
            "title=excluded.title, event_time=excluded.event_time, url=excluded.url, "
            "payload=excluded.payload, fetched_at=excluded.fetched_at",
            rows,
        )
        conn.commit()
    return len(rows)


def record_run(source, *, ok, error=None, item_count=None):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        existing = conn.execute("SELECT last_ok FROM fetch_runs WHERE source=?", (source,)).fetchone()
        last_ok = now if ok else (existing["last_ok"] if existing else None)
        conn.execute(
            "INSERT INTO fetch_runs (source, last_run, last_ok, last_error, item_count) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(source) DO UPDATE SET last_run=excluded.last_run, "
            "last_ok=excluded.last_ok, last_error=excluded.last_error, item_count=excluded.item_count",
            (source, now, last_ok, error, item_count),
        )
        conn.commit()


def query_items(source=None, limit=100, order="event_time", descending=True):
    allowed = {"event_time", "fetched_at", "title"}
    order = order if order in allowed else "event_time"
    direction = "DESC" if descending else "ASC"
    sql = "SELECT * FROM items"
    params = []
    if source:
        sql += " WHERE source = ?"
        params.append(source)
    sql += f" ORDER BY {order} {direction} NULLS LAST LIMIT ?"
    params.append(limit)
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def status():
    with connect() as conn:
        runs = [dict(r) for r in conn.execute("SELECT * FROM fetch_runs ORDER BY source").fetchall()]
        counts = {r["source"]: r["n"] for r in conn.execute(
            "SELECT source, count(*) AS n FROM items GROUP BY source").fetchall()}
    for r in runs:
        r["stored_items"] = counts.get(r["source"], 0)
    return runs
