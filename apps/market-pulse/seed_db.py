"""Seed market_pulse.db with live data.

Run once before packaging: fills multpl + Yahoo series (reachable without
API keys). FRED series fill automatically on the app's first run.
Usage: python seed_db.py
"""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pandas as pd  # noqa: E402

import db_store  # noqa: E402

# Load app.py's fetch helpers without launching the Streamlit app.
_src = open(os.path.join(HERE, "app.py")).read().replace("\nmain()\n", "\n")
_ns: dict = {}
exec(compile(_src, "app.py", "exec"), _ns)
_multpl_one = _ns["_multpl_one"]
_yf_download = _ns["_yf_download"]

MULTPL_SLUGS = ("shiller-pe", "s-p-500-pe-ratio", "s-p-500-price-to-sales",
                "s-p-500-dividend-yield")
YF_TICKERS = ["^GSPC", "^VIX", "^TNX", "DX-Y.NYB", "GC=F", "HG=F", "CL=F",
              "BTC-USD", "RSP", "SPY"]


def main():
    if os.path.exists(db_store.DB_PATH):
        os.remove(db_store.DB_PATH)
    db = db_store.open_db()
    assert db is not None, "could not create DB"

    total = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for slug, s in zip(MULTPL_SLUGS, ex.map(_multpl_one, MULTPL_SLUGS)):
            n = db_store.upsert_series(db, db_store.key("MULTPL", slug),
                                       "monthly", s)
            total += n
            print(f"MULTPL {slug}: {n} rows, through "
                  f"{s.index[-1].date() if len(s) else 'n/a'}", flush=True)

    frame = _yf_download(YF_TICKERS, "5y")
    for t in YF_TICKERS:
        s = frame[t].dropna() if t in frame.columns else pd.Series(dtype=float)
        n = db_store.upsert_series(db, db_store.key("YF", t), "daily", s)
        total += n
        print(f"YF {t}: {n} rows, through "
              f"{s.index[-1].date() if len(s) else 'n/a'}", flush=True)

    db.close()
    sz = os.path.getsize(db_store.DB_PATH) / 1024
    print(f"done: {total} rows, {sz:.0f} KB -> {db_store.DB_PATH}")


if __name__ == "__main__":
    main()
