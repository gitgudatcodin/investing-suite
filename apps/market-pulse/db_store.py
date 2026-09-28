"""SQLite store for Market Pulse (local file, or Turso when configured).

Bulk-download once, then incremental forever: each series is refetched only
when its release calendar says new data can exist. Every DB failure degrades
to plain network fetching — the store never crashes the app.
"""
from __future__ import annotations

import datetime as dt
import os
import sqlite3

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "market_pulse.db")

# Update frequency per FRED series id.
FREQ = {
    "GDP": "quarterly",
    "INDPRO": "monthly", "RSXFS": "monthly", "PAYEMS": "monthly",
    "UNRATE": "monthly", "JTSJOL": "monthly", "AHETPI": "monthly",
    "CPIAUCSL": "monthly", "CPILFESL": "monthly", "PCEPILFE": "monthly",
    "UMCSENT": "monthly", "HOUST": "monthly", "MORTGAGE30US": "monthly",
    "ICSA": "weekly",
    "T5YIE": "daily", "DFII10": "daily", "DGS2": "daily", "DGS10": "daily",
    "DGS3MO": "daily", "BAMLH0A0HYM2": "daily", "BAMLC0A0CM": "daily",
    "WILL5000PR": "daily",
    "CSUSHPISA": "annual", "DDDM01USA156NWDB": "annual",
}

# Don't re-check a series more often than this after a fetch that found
# nothing new (some releases lag the calendar).
MIN_INTERVAL = {
    "daily": dt.timedelta(hours=12),
    "weekly": dt.timedelta(days=2),
    "monthly": dt.timedelta(days=5),
    "quarterly": dt.timedelta(days=20),
    "annual": dt.timedelta(days=60),
}

_SCHEMA_STMTS = [
    """CREATE TABLE IF NOT EXISTS series (
        sid TEXT NOT NULL,
        d   TEXT NOT NULL,
        v   REAL NOT NULL,
        PRIMARY KEY (sid, d))""",
    """CREATE TABLE IF NOT EXISTS meta (
        sid        TEXT PRIMARY KEY,
        freq       TEXT NOT NULL,
        last_fetch TEXT)""",
]


def key(source: str, sid: str) -> str:
    return f"{source}:{sid}"


def freq_of(source: str, sid: str) -> str:
    if source == "FRED":
        return FREQ.get(sid, "monthly")
    if source == "MULTPL":
        return "monthly"
    return "daily"  # YF


def _turso_creds():
    """(url, token) from env or Streamlit secrets; (None, None) if unset."""
    url = os.environ.get("TURSO_DATABASE_URL")
    token = os.environ.get("TURSO_AUTH_TOKEN")
    if not url:
        try:
            import streamlit as st
            url = st.secrets.get("TURSO_DATABASE_URL")
            token = st.secrets.get("TURSO_AUTH_TOKEN")
        except Exception:
            pass
    return url, token


def _open_turso(url: str, token: str):
    try:
        try:
            import libsql
        except ImportError:
            import libsql_experimental as libsql
        con = libsql.connect(database=url, auth_token=token)
        for stmt in _SCHEMA_STMTS:
            con.execute(stmt)
        con.commit()
        return con
    except Exception as e:
        print(f"[db_store] Turso connect failed ({e}); using local SQLite")
        return None


def open_db(path: str = DB_PATH):
    """Return a connection, or None if the DB can't be used.

    Uses Turso (shared, persistent) when TURSO_DATABASE_URL/TURSO_AUTH_TOKEN
    are set via env or Streamlit secrets; otherwise the local SQLite file.
    """
    url, token = _turso_creds()
    if url and token:
        con = _open_turso(url, token)
        if con is not None:
            return con
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        con = sqlite3.connect(path, timeout=30)
        con.execute("PRAGMA journal_mode=WAL")
        for stmt in _SCHEMA_STMTS:
            con.execute(stmt)
        return con
    except Exception:
        return None


def _expected_min(freq: str, today: dt.date) -> dt.date:
    """Earliest date we must already have for the series to be fresh."""
    if freq == "daily":
        d = today
        while d.weekday() >= 5:  # last weekday
            d -= dt.timedelta(days=1)
        return d
    if freq == "weekly":
        return today - dt.timedelta(days=7)
    if freq == "monthly":
        return (today.replace(day=1) - dt.timedelta(days=1)).replace(day=1)
    if freq == "quarterly":
        qstart = 3 * ((today.month - 1) // 3) + 1
        prev = today.replace(month=qstart, day=1) - dt.timedelta(days=1)
        return prev.replace(month=3 * ((prev.month - 1) // 3) + 1, day=1)
    return dt.date(today.year - 1, 1, 1)  # annual


def is_fresh(con, sid: str, freq: str, now: dt.datetime | None = None) -> bool:
    """True if no new data can exist yet, or we checked recently."""
    now = now or dt.datetime.now(dt.timezone.utc)
    try:
        row = con.execute(
            "SELECT d FROM series WHERE sid=? ORDER BY d DESC LIMIT 1",
            (sid,)).fetchone()
        if not row:
            return False
        if dt.date.fromisoformat(row[0]) >= _expected_min(freq, now.date()):
            return True
        m = con.execute(
            "SELECT last_fetch FROM meta WHERE sid=?", (sid,)).fetchone()
        if m and m[0] and now - dt.datetime.fromisoformat(m[0]) < MIN_INTERVAL[freq]:
            return True
        return False
    except Exception:
        return False


def has_rows(con, sid: str) -> bool:
    try:
        return con.execute(
            "SELECT 1 FROM series WHERE sid=? LIMIT 1", (sid,)).fetchone() is not None
    except Exception:
        return False


def get_series(con, sid: str):
    """Full history as a pandas Series with DatetimeIndex (may be empty)."""
    import pandas as pd
    try:
        rows = con.execute(
            "SELECT d, v FROM series WHERE sid=? ORDER BY d", (sid,)).fetchall()
    except Exception:
        rows = []
    if not rows:
        return pd.Series(dtype=float)
    idx = pd.to_datetime([r[0] for r in rows])
    return pd.Series([r[1] for r in rows], index=idx).sort_index()


def upsert_series(con, sid: str, freq: str, series, now: dt.datetime | None = None) -> int:
    """Insert/replace rows; always refresh last_fetch. Returns rows written."""
    now = now or dt.datetime.now(dt.timezone.utc)
    n = 0
    try:
        if series is not None and len(series):
            s = series.dropna()
            rows = [(sid, d.strftime("%Y-%m-%d"), float(v))
                    for d, v in zip(s.index, s.values)]
            con.executemany(
                "INSERT OR REPLACE INTO series (sid, d, v) VALUES (?, ?, ?)", rows)
            n = len(rows)
        con.execute(
            "INSERT INTO meta (sid, freq, last_fetch) VALUES (?, ?, ?)"
            " ON CONFLICT(sid) DO UPDATE SET freq=excluded.freq,"
            " last_fetch=excluded.last_fetch",
            (sid, freq, now.isoformat()))
        con.commit()
    except Exception:
        try:
            con.rollback()
        except Exception:
            pass
    return n
