"""Refresh the committed market_pulse.db (used by the weekly GitHub Action).

Reuses the app's own incremental loader: only series whose release calendar
says new data can exist hit the network; everything upserts into the DB.
Run locally any time too:  python refresh_db.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Load app.py's loader without launching Streamlit.
_src = open(os.path.join(HERE, "app.py")).read().replace("\nmain()\n", "\n")
_ns: dict = {}
exec(compile(_src, "app.py", "exec"), _ns)


def main():
    import db_store
    db = db_store.open_db()
    assert db is not None, "could not open DB"
    db.close()

    F = _ns["_load_group"]("FRED", _ns["FRED_IDS"], _ns["_fred_one"], 6,
                           "economic")
    M = _ns["_load_group"]("MULTPL", _ns["MULTPL_SLUGS"], _ns["_multpl_one"], 4,
                           "valuation")
    px = _ns["_load_yahoo"]()

    print(f"FRED:   {sum(1 for s in F.values() if len(s))}/{len(F)} series ok")
    print(f"multpl: {sum(1 for s in M.values() if len(s))}/{len(M)} series ok")
    print(f"Yahoo:  {px.shape[1]} tickers x {px.shape[0]} days")
    print(f"DB -> {db_store.DB_PATH} "
          f"({os.path.getsize(db_store.DB_PATH) // 1024} KB)")


if __name__ == "__main__":
    main()
