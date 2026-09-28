"""Market Pulse — real-time trader/investor dashboard.

Live data: FRED (economy & rates), multpl.com (valuation ratios),
Yahoo Finance (market prices). No API keys required (optional free FRED key
for bulletproof economic data). Cached 6h (FRED/multpl), 1h (prices).

Run:  pip install -r requirements.txt && streamlit run app.py
"""

import re
import os
import time
import hashlib
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, wait

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Test hook: MARKETPULSE_STUB=1 -> deterministic synthetic FRED data (UI tests
# without network); =fail -> every FRED series empty (degradation tests).
_STUB_MODE = os.environ.get("MARKETPULSE_STUB", "")


def _stub_series(sid):
    """Deterministic synthetic series for UI testing (never used in production)."""
    seed = int(hashlib.md5(sid.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    specs = {
        "GDP": ("QE", "2000-01-01", "2026-06-30", 10000, 0.012, 0.008),
        "INDPRO": ("ME", "2000-01-01", "2026-08-31", 100, 0.001, 0.010),
        "RSXFS": ("ME", "2000-01-01", "2026-08-31", 400000, 0.003, 0.008),
        "PAYEMS": ("ME", "2000-01-01", "2026-08-31", 140000, 0.001, 0.002),
        "UNRATE": ("ME", "2000-01-01", "2026-08-31", 5.5, 0.0, 0.030),
        "ICSA": ("W", "2000-01-01", "2026-09-20", 220, 0.0, 0.050),
        "JTSJOL": ("ME", "2001-01-01", "2026-07-31", 8000, 0.002, 0.030),
        "AHETPI": ("ME", "2007-01-01", "2026-08-31", 28, 0.0025, 0.002),
        "CPIAUCSL": ("ME", "2000-01-01", "2026-08-31", 220, 0.002, 0.002),
        "CPILFESL": ("ME", "2000-01-01", "2026-08-31", 210, 0.002, 0.0015),
        "PCEPILFE": ("ME", "2000-01-01", "2026-07-31", 100, 0.0016, 0.001),
        "T5YIE": ("D", "2003-01-01", "2026-09-25", 2.3, 0.0, 0.020),
        "DFII10": ("D", "2003-01-01", "2026-09-25", 1.8, 0.0, 0.030),
        "DGS2": ("D", "2000-01-01", "2026-09-25", 3.5, 0.0, 0.020),
        "DGS10": ("D", "2000-01-01", "2026-09-25", 4.2, 0.0, 0.015),
        "DGS3MO": ("D", "2000-01-01", "2026-09-25", 3.8, 0.0, 0.020),
        "BAMLH0A0HYM2": ("D", "2000-01-01", "2026-09-24", 4.5, 0.0, 0.030),
        "BAMLC0A0CM": ("D", "2000-01-01", "2026-09-24", 1.4, 0.0, 0.030),
        "UMCSENT": ("ME", "2000-01-01", "2026-08-31", 80, 0.0, 0.030),
        "CSUSHPISA": ("ME", "2000-01-01", "2026-07-31", 180, 0.004, 0.005),
        "HOUST": ("ME", "2000-01-01", "2026-08-31", 1400, 0.0, 0.050),
        "MORTGAGE30US": ("W", "2000-01-01", "2026-09-24", 6.0, 0.0, 0.020),
        "WILL5000PR": ("D", "2000-01-01", "2026-09-25", 12000, 0.0003, 0.012),
        "DDDM01USA156NWDB": ("YE", "2000-12-31", "2020-12-31", 140, 0.020, 0.050),
    }
    freq, start, end, base, drift, vol = specs.get(
        sid, ("ME", "2000-01-01", "2026-08-31", 100, 0.001, 0.01))
    idx = pd.date_range(start, end, freq=freq)
    rets = rng.normal(drift, vol, len(idx))
    return pd.Series(base * np.exp(np.cumsum(rets)), index=idx)

FRED_IDS = ("GDP", "INDPRO", "RSXFS", "PAYEMS", "UNRATE", "ICSA", "JTSJOL", "AHETPI",
            "CPIAUCSL", "CPILFESL", "PCEPILFE", "T5YIE", "DFII10",
            "DGS2", "DGS10", "DGS3MO", "BAMLH0A0HYM2", "BAMLC0A0CM",
            "UMCSENT", "CSUSHPISA", "HOUST", "MORTGAGE30US",
            "WILL5000PR", "DDDM01USA156NWDB")
MULTPL_SLUGS = ("shiller-pe", "s-p-500-pe-ratio", "s-p-500-price-to-sales",
                "s-p-500-dividend-yield")
YF_TICKERS = ["^GSPC", "^VIX", "^TNX", "DX-Y.NYB", "GC=F", "HG=F", "CL=F",
              "BTC-USD", "RSP", "SPY"]


# ============================================================ data layer
def _dbnomics_fred(sid, timeout=25):
    """Fallback: DBnomics mirrors the full FRED database (no key, generous
    rate limits). Handles both documented response shapes."""
    import json as _json
    url = f"https://api.db.nomics.world/v22/series/FRED/series/{sid}?observations=1"
    try:
        req = urllib.request.Request(url, headers=UA)
        payload = _json.loads(
            urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8"))
        series = payload.get("series", {})
        if isinstance(series, list):
            series = series[0] if series else {}
        periods, values = None, None
        if isinstance(series.get("period"), list) and isinstance(series.get("value"), list):
            periods, values = series["period"], series["value"]
        elif isinstance(series.get("observations"), list):
            obs = series["observations"]
            periods = [o.get("period") for o in obs]
            values = [o.get("value") for o in obs]
        if not periods:
            return pd.Series(dtype=float)
        idx = pd.to_datetime(periods)
        vals = pd.to_numeric(
            pd.Series(list(values)).replace("NA", np.nan), errors="coerce")
        s = pd.Series(vals.to_numpy(), index=idx).dropna().sort_index()
        return s[~s.index.duplicated(keep="last")]
    except Exception:
        return pd.Series(dtype=float)


def _fred_api_key():
    """Free FRED API key from env or Streamlit secrets (optional)."""
    k = os.environ.get("FRED_API_KEY")
    if not k:
        try:
            k = st.secrets.get("FRED_API_KEY")
        except Exception:
            k = None
    return k


def _fred_api(sid, key, timeout=25):
    """FRED official API (api.stlouisfed.org) — reliable even where the FRED
    website/CSV endpoint throttles cloud IPs. Free key, no card."""
    import json as _json
    url = ("https://api.stlouisfed.org/fred/series/observations?series_id="
           + urllib.parse.quote(sid) + "&api_key=" + urllib.parse.quote(key)
           + "&file_type=json")
    try:
        req = urllib.request.Request(url, headers=UA)
        payload = _json.loads(
            urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8"))
        obs = payload.get("observations", [])
        rows = [(o.get("date"), o.get("value")) for o in obs
                if o.get("value") not in (None, "", ".")]
        if not rows:
            return pd.Series(dtype=float)
        idx = pd.to_datetime([r[0] for r in rows])
        vals = pd.to_numeric([r[1] for r in rows], errors="coerce")
        s = pd.Series(vals, index=idx).dropna().sort_index()
        return s[~s.index.duplicated(keep="last")]
    except Exception:
        return pd.Series(dtype=float)


def _fred_one(sid):
    if _STUB_MODE == "fail":
        return pd.Series(dtype=float)
    if _STUB_MODE:
        return _stub_series(sid)
    # 0) FRED official API when a free key is configured — the reliable path.
    key = _fred_api_key()
    if key:
        s = _fred_api(sid, key)
        if len(s):
            return s
    # 1) FRED direct CSV — single fast attempt so a blocked FRED fails over
    #    quickly instead of burning 2 x 25s timeouts per series.
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
    try:
        req = urllib.request.Request(url, headers=UA)
        df = pd.read_csv(urllib.request.urlopen(req, timeout=6))
        df.columns = [c.strip().upper() for c in df.columns]
        df["DATE"] = pd.to_datetime(df["DATE"])
        df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")
        s = df.dropna(subset=["VALUE"]).set_index("DATE")["VALUE"].sort_index()
        if len(s):
            return s
    except Exception:
        pass
    # 2) DBnomics FRED mirror (independent host, no key)
    return _dbnomics_fred(sid)


def _multpl_one(slug, tries=2):
    url = f"https://www.multpl.com/{slug}/table/by-month"
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
            rows = re.findall(
                r"<td>\s*([A-Z][a-z]{2} \d{1,2}, \d{4})\s*</td>\s*<td[^>]*>\s*&#x2002;\s*([\d.]+)",
                html,
            )
            df = pd.DataFrame(rows, columns=["date", "value"])
            df["date"] = pd.to_datetime(df["date"])
            df["value"] = pd.to_numeric(df["value"])
            return df.set_index("date")["value"].sort_index()
        except Exception:
            time.sleep(3 * (a + 1))
    return pd.Series(dtype=float)


def _db():
    """DB connection, or None in stub mode / when SQLite is unavailable."""
    if _STUB_MODE:
        return None
    import db_store
    return db_store.open_db()


def _load_group(source, sids, fetch_one, workers=6, label="series",
                progress=None, deadline=None):
    """DB-backed group load: fresh series come from SQLite, stale ones are
    fetched in parallel and upserted. A failed fetch falls back to whatever
    the DB already holds (even if stale) instead of 'data unavailable'.

    progress(sid) is called as each series resolves (fresh or fetched) so
    the UI can show where the load is. Series still unfetched when
    time.time() passes deadline are skipped and served from the DB.
    """
    import db_store
    db = _db()
    out, stale = {}, []
    if db is not None:
        for sid in sids:
            k = db_store.key(source, sid)
            if db_store.is_fresh(db, k, db_store.freq_of(source, sid)):
                out[sid] = db_store.get_series(db, k)
                if progress is not None:
                    progress(sid)
            else:
                stale.append(sid)
    else:
        stale = list(sids)

    if stale:
        def one(sid):
            if deadline is not None and time.time() > deadline:
                return sid, pd.Series(dtype=float)  # too slow: serve DB rows
            time.sleep(0.3)
            s = fetch_one(sid)
            if progress is not None:
                progress(sid)
            return sid, s

        with ThreadPoolExecutor(max_workers=workers) as ex:
            fetched = dict(ex.map(one, stale))
        for sid, s in fetched.items():
            k = db_store.key(source, sid)
            if db is not None:
                db_store.upsert_series(db, k, db_store.freq_of(source, sid), s)
                if not len(s):  # fetch failed: serve stale DB rows if any
                    s = db_store.get_series(db, k)
            out[sid] = s
    if db is not None:
        db.close()
    return out


def _yf_download(tickers, period):
    try:
        d = yf.download(" ".join(tickers), period=period, interval="1d",
                        auto_adjust=True, progress=False, threads=True)
        c = d["Close"]
        if isinstance(c, pd.Series):
            c = c.to_frame(tickers[0])
        return c
    except Exception:
        return pd.DataFrame()


def _load_yahoo(progress=None, deadline=None):
    """DB-backed Yahoo closes: 5y seed on first run, 1-month tail refreshes.

    progress(t) is called per resolved ticker; tickers still unfetched when
    time.time() passes deadline are skipped and served from the DB.
    """
    import db_store
    db = _db()
    tickers = list(YF_TICKERS)
    need_full, need_tail, series = [], [], {}
    if db is None:
        need_full = tickers
    else:
        for t in tickers:
            k = db_store.key("YF", t)
            if db_store.is_fresh(db, k, "daily"):
                series[t] = db_store.get_series(db, k)
                if progress is not None:
                    progress(t)
            elif db_store.has_rows(db, k):
                need_tail.append(t)
            else:
                need_full.append(t)

    for tks, period in ((need_full, "5y"), (need_tail, "1mo")):
        if not tks:
            continue
        if deadline is not None and time.time() > deadline:
            frame = pd.DataFrame()
        else:
            frame = _yf_download(tks, period)
        for t in tks:
            s = pd.Series(dtype=float)
            if len(frame) and t in frame.columns:
                s = frame[t].dropna()
            k = db_store.key("YF", t)
            if db is not None:
                db_store.upsert_series(db, k, "daily", s)
                if not len(s):
                    s = db_store.get_series(db, k)
            series[t] = s
            if progress is not None:
                progress(t)
    if db is not None:
        db.close()
    px = pd.DataFrame(series).sort_index().ffill()
    return px


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def load_all():
    """Single cached entry point — import stays side-effect free.

    Fresh series are served from the local SQLite store; only series whose
    release calendar says new data can exist hit the network (in parallel).
    """
    status = st.status("Loading market data…", expanded=False)
    # Per-group progress counters, bumped from worker threads (the label
    # itself is only ever updated here, in the script thread).
    counts = {"economic": [0, len(FRED_IDS)],
              "valuation": [0, len(MULTPL_SLUGS)],
              "prices": [0, len(YF_TICKERS)]}

    def _prog(group):
        def cb(_sid):
            counts[group][0] += 1
        return cb

    def _label():
        parts = [f"{g} {c[0]}/{c[1]}" for g, c in counts.items()]
        return "Loading market data… (" + ", ".join(parts) + ")"

    start = time.time()
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {
            ex.submit(_load_group, "FRED", FRED_IDS, _fred_one, 6, "economic",
                      _prog("economic"), start + 300): "FRED",
            ex.submit(_load_group, "MULTPL", MULTPL_SLUGS, _multpl_one, 4,
                      "valuation", _prog("valuation"), start + 120): "MULTPL",
            ex.submit(_load_yahoo, _prog("prices"), start + 150): "YF",
        }
        pending = set(futs)
        results = {}
        # Poll so the status label shows live per-group progress instead of
        # a spinner that looks stuck; each group also has a hard deadline
        # after which it serves whatever the DB holds.
        while pending:
            done, pending = wait(pending, timeout=2)
            for f in done:
                try:
                    results[futs[f]] = f.result()
                except Exception:
                    results[futs[f]] = {} if futs[f] != "YF" else pd.DataFrame()
            status.update(label=_label())
        F, M, px = results["FRED"], results["MULTPL"], results["YF"]
        status.write("Economic series ready")
        status.write("Valuation multiples ready")
        status.write("Market prices ready")
    status.update(label="Market data ready", state="complete", expanded=False)
    return F, M, px


# ============================================================ helpers
def pct_rank(s):
    s = s.dropna()
    return float((s <= s.iloc[-1]).mean() * 100) if len(s) else float("nan")


def asof(s):
    return s.index[-1].strftime("%b %d, %Y") if len(s) else "n/a"


def kpi(title, s, fmt="{:.2f}", unit="", years=6, transform=None, note="",
        higher_is="neutral"):
    """Metric + history chart card. transform: 'yoy12' | 'yoy4' | None."""
    if s is None or len(s) < 5:
        st.warning(f"{title}: data unavailable")
        return
    s = s.dropna()
    if transform == "yoy12":
        s, unit = s.pct_change(12) * 100, "% YoY"
    elif transform == "yoy4":
        s, unit = s.pct_change(4) * 100, "% YoY"
    s = s.dropna()
    if len(s) < 5:
        st.warning(f"{title}: data unavailable")
        return
    cur, prev = s.iloc[-1], s.iloc[-2]
    chg = cur - prev
    pr = pct_rank(s)
    c1, c2 = st.columns([1, 2.4])
    with c1:
        st.metric(title, f"{fmt.format(cur)}{unit}", f"{chg:+.2f} vs prev",
                  delta_color="normal" if higher_is == "neutral"
                  else ("normal" if (chg > 0) == (higher_is == "good") else "inverse"))
        st.caption(f"{pr:.0f}th pctile of history · as of {asof(s)}")
        if note:
            st.caption(note)
    with c2:
        cutoff = s.index.max() - pd.DateOffset(years=years)
        st.line_chart(s[s.index >= cutoff])


def pill(label, status, color):
    st.markdown(f"**{label}**<br>:{color}[**{status}**]", unsafe_allow_html=True)


# ============================================================ app
def main():
    st.set_page_config(page_title="Market Pulse", page_icon="📊", layout="wide")
    st.title("📊 Market Pulse — trader dashboard")
    st.caption("Live: FRED · multpl.com · Yahoo Finance · cached 6h/1h · research tooling, not advice")

    F, M, px = load_all()

    def G(sid):
        return F.get(sid, pd.Series(dtype=float))

    cape, pe_trail = M.get("shiller-pe", pd.Series(dtype=float)), M.get("s-p-500-pe-ratio", pd.Series(dtype=float))
    ps, divy = M.get("s-p-500-price-to-sales", pd.Series(dtype=float)), M.get("s-p-500-dividend-yield", pd.Series(dtype=float))

    # derived series
    curve_2s10s = (G("DGS10") - G("DGS2")).dropna()
    curve_3m10s = (G("DGS10") - G("DGS3MO")).dropna()
    unrate = G("UNRATE")
    sahm = (unrate.rolling(3).mean() - unrate.rolling(12).min()).dropna() if len(unrate) else pd.Series(dtype=float)
    core_pce = (G("PCEPILFE").pct_change(12) * 100).dropna()
    tnx = (px["^TNX"] / 10).dropna() if "^TNX" in px else pd.Series(dtype=float)
    vx = px["^VIX"].dropna() if "^VIX" in px else pd.Series(dtype=float)
    rsp_spy = (px["RSP"] / px["SPY"]).dropna() if {"RSP", "SPY"} <= set(px.columns) else pd.Series(dtype=float)

    # Buffett indicator: official annual series + live estimate
    buffett_est, buffett_note = float("nan"), ""
    wb, will, gdp = G("DDDM01USA156NWDB"), G("WILL5000PR"), G("GDP")
    if len(wb) and len(will) and len(gdp):
        try:
            buffett_est = float(wb.iloc[-1] * (will.iloc[-1] / will["2020"].mean())
                                / (gdp.iloc[-1] / gdp["2020"].mean()) * 100)
            buffett_note = (f"Live estimate: {wb.iloc[-1]:.0f}% (2020 annual) × Wilshire-5000 move "
                            f"÷ GDP move since 2020 · as of {asof(will)} / {asof(gdp)}")
        except Exception:
            pass
    dfii10 = G("DFII10")
    excess_cape_yield = float(100 / cape.iloc[-1] - dfii10.iloc[-1]) if len(cape) and len(dfii10) else float("nan")

    # ---------------- regime strip ----------------
    st.subheader("Regime at a glance")
    r = st.columns(6)
    with r[0]:
        p = pct_rank(cape)
        pill("Valuation (CAPE)", "Extreme" if p > 90 else "Expensive" if p > 75 else "Fair" if p == p else "n/a",
             "red" if p > 90 else "orange" if p > 75 else "green")
        st.caption(f"CAPE {cape.iloc[-1]:.1f}" if len(cape) else "n/a")
    with r[1]:
        v = curve_2s10s.iloc[-1] if len(curve_2s10s) else float("nan")
        pill("Yield curve 2s10s", "Inverted" if v < 0 else "Flat" if v < 1 else "Normal" if v == v else "n/a",
             "red" if v < 0 else "orange" if v < 1 else "green")
        st.caption(f"{v * 100:.0f} bp" if v == v else "n/a")
    with r[2]:
        h = G("BAMLH0A0HYM2")
        hp = pct_rank(h)
        pill("Credit stress", "Stressed" if hp > 80 else "Complacent" if hp < 20 else "Normal" if hp == hp else "n/a",
             "red" if hp > 80 else "orange" if hp < 20 else "green")
        st.caption(f"HY OAS {h.iloc[-1]:.2f}%" if len(h) else "n/a")
    with r[3]:
        vv = vx.iloc[-1] if len(vx) else float("nan")
        pill("Fear (VIX)", "Panic" if vv > 30 else "Elevated" if vv > 20 else "Calm" if vv == vv else "n/a",
             "red" if vv > 30 else "orange" if vv > 20 else "green")
        st.caption(f"{vv:.1f}" if vv == vv else "n/a")
    with r[4]:
        sv = sahm.iloc[-1] if len(sahm) else float("nan")
        pill("Labor (Sahm)", "Recession signal" if sv >= 0.5 else "Softening" if sv >= 0.3 else "Solid" if sv == sv else "n/a",
             "red" if sv >= 0.5 else "orange" if sv >= 0.3 else "green")
        st.caption(f"unemployment {unrate.iloc[-1]:.1f}%" if len(unrate) else "n/a")
    with r[5]:
        pv = core_pce.iloc[-1] if len(core_pce) else float("nan")
        pill("Inflation (core PCE)", "Hot" if pv > 3 else "Above target" if pv > 2 else "At target" if pv == pv else "n/a",
             "red" if pv > 3 else "orange" if pv > 2 else "green")
        st.caption(f"{pv:.1f}% YoY" if pv == pv else "n/a")

    # ---------------- tabs ----------------
    t1, t2, t3 = st.tabs(["💰 Valuation", "🏭 Economy", "📈 Markets"])

    with t1:
        st.subheader("How expensive is the market?")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Shiller CAPE", f"{cape.iloc[-1]:.1f}" if len(cape) else "n/a",
                      f"{pct_rank(cape):.0f}th pctile of history" if len(cape) else "")
            st.caption(f"As of {asof(cape)} · avg since 1881 ≈ 17 · record 44.2 (Dec 1999)")
        with m2:
            st.metric("Buffett indicator (est.)", f"{buffett_est:.0f}%" if buffett_est == buffett_est else "n/a",
                      "all-time-high zone" if buffett_est == buffett_est and buffett_est > 200 else "")
            st.caption(buffett_note or "n/a")
        with m3:
            ecy = excess_cape_yield
            st.metric("Excess CAPE yield", f"{ecy:+.1f}%" if ecy == ecy else "n/a",
                      "thin vs history" if ecy == ecy and ecy < 2 else "")
            st.caption("Earnings yield (1/CAPE) − 10-yr real yield · as of " + asof(dfii10))
        if len(cape):
            st.line_chart(cape[cape.index >= "1985"])
            st.caption("Shiller CAPE since 1985 — peaks: 1929 (~33), 1999 (44.2), 2021 (~39), now (~41). "
                       "Predicts 10-yr forward returns, not timing.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**S&P 500 trailing P/E**")
            if len(pe_trail):
                st.metric("P/E", f"{pe_trail.iloc[-1]:.1f}×", f"{pct_rank(pe_trail):.0f}th pctile")
                st.line_chart(pe_trail[pe_trail.index >= "2000"])
            else:
                st.warning("data unavailable")
        with c2:
            st.markdown("**S&P 500 price / sales**")
            if len(ps):
                st.metric("P/S", f"{ps.iloc[-1]:.2f}×", f"{pct_rank(ps):.0f}th pctile")
                st.line_chart(ps[ps.index >= "2000"])
                st.caption("Hist. norm ~1.5×")
            else:
                st.warning("data unavailable")
        with c3:
            st.markdown("**S&P 500 dividend yield**")
            if len(divy):
                st.metric("Div yield", f"{divy.iloc[-1]:.2f}%", f"{pct_rank(divy):.0f}th pctile")
                st.line_chart(divy[divy.index >= "2000"])
                st.caption("Low yield = expensive")
            else:
                st.warning("data unavailable")
        if len(wb):
            st.markdown("**Buffett indicator — official annual series (lagged)**")
            st.line_chart(wb)
            st.caption("FRED/WDI annual market-cap-to-GDP; live estimate above.")

    with t2:
        st.subheader("Growth")
        kpi("Real GDP", G("GDP"), fmt="{:.0f}", unit=" $B", transform="yoy4", years=10,
            note="Quarterly", higher_is="good")
        kpi("Industrial production", G("INDPRO"), transform="yoy12", years=6, higher_is="good")
        kpi("Retail sales", G("RSXFS"), fmt="{:.0f}", unit=" $M", transform="yoy12", years=6,
            higher_is="good", note="Advance retail sales")
        st.subheader("Labor")
        kpi("Unemployment rate", unrate, fmt="{:.1f}", unit="%", years=10, higher_is="bad",
            note=f"Sahm: {sahm.iloc[-1]:.2f} (≥0.50 = recession signal)" if len(sahm) else "")
        kpi("Nonfarm payrolls", G("PAYEMS"), fmt="{:.0f}", unit="k", years=4, higher_is="good",
            note="Level (thousands) — watch the slope")
        kpi("Jobless claims (initial)", G("ICSA"), fmt="{:.0f}", unit="k", years=4,
            higher_is="bad", note="Weekly — fastest real-time labor signal")
        kpi("JOLTS job openings", G("JTSJOL"), fmt="{:.0f}", unit="k", years=6)
        kpi("Wage growth (avg hourly earnings)", G("AHETPI"), transform="yoy12", years=6,
            note="Wage-inflation feed-through")
        st.subheader("Inflation")
        kpi("CPI headline", G("CPIAUCSL"), transform="yoy12", years=6, higher_is="bad")
        kpi("CPI core", G("CPILFESL"), transform="yoy12", years=6, higher_is="bad")
        kpi("Core PCE (Fed's target)", G("PCEPILFE"), transform="yoy12", years=6, higher_is="bad",
            note="Target = 2.0%")
        kpi("5-yr inflation expectations", G("T5YIE"), fmt="{:.2f}", unit="%", years=6,
            note="TIPS breakeven")
        st.subheader("Rates & curve")
        kpi("10-yr Treasury", G("DGS10"), fmt="{:.2f}", unit="%", years=6)
        kpi("2-yr Treasury", G("DGS2"), fmt="{:.2f}", unit="%", years=6,
            note="Market's Fed-policy proxy")
        kpi("2s10s spread", curve_2s10s, fmt="{:.2f}", unit=" pp", years=10,
            note="Negative = inverted = classic recession flag")
        kpi("10-yr real yield (TIPS)", dfii10, fmt="{:.2f}", unit="%", years=6,
            note="The discount rate for everything")
        st.subheader("Consumer & housing")
        kpi("Michigan sentiment", G("UMCSENT"), fmt="{:.1f}", years=10, higher_is="good")
        kpi("Case-Shiller home prices", G("CSUSHPISA"), transform="yoy12", years=10)
        kpi("Housing starts", G("HOUST"), fmt="{:.0f}", unit="k", years=10, higher_is="good")
        kpi("30-yr mortgage rate", G("MORTGAGE30US"), fmt="{:.2f}", unit="%", years=10,
            higher_is="bad")

    with t3:
        st.subheader("Price action & risk")
        if len(px):
            c1, c2 = st.columns(2)
            with c1:
                sp = px["^GSPC"].dropna()
                if len(sp):
                    st.metric("S&P 500", f"{sp.iloc[-1]:,.0f}",
                              f"{(sp.iloc[-1] / sp.iloc[-21] - 1) * 100:+.1f}% 1-mo" if len(sp) > 21 else "")
                    st.line_chart(sp[sp.index >= sp.index.max() - pd.DateOffset(years=1)])
            with c2:
                if len(vx):
                    st.metric("VIX", f"{vx.iloc[-1]:.1f}", "fear" if vx.iloc[-1] > 25 else "calm")
                    st.line_chart(vx[vx.index >= vx.index.max() - pd.DateOffset(years=1)])
        kpi("10-yr yield (market)", tnx, fmt="{:.2f}", unit="%", years=2)
        if len(rsp_spy):
            st.markdown("**Breadth: equal-weight ÷ cap-weight (RSP/SPY)**")
            c1, c2 = st.columns([1, 2.4])
            with c1:
                st.metric("RSP/SPY", f"{rsp_spy.iloc[-1]:.3f}", f"{pct_rank(rsp_spy):.0f}th pctile")
                st.caption("Low = narrow mega-cap leadership")
            with c2:
                st.line_chart(rsp_spy)
        st.subheader("Credit — the fear gauge that matters")
        kpi("HY option-adjusted spread", G("BAMLH0A0HYM2"), fmt="{:.2f}", unit="%",
            years=6, higher_is="bad", note="Blow-outs precede equity pain")
        kpi("IG option-adjusted spread", G("BAMLC0A0CM"), fmt="{:.2f}", unit="%",
            years=6, higher_is="bad")
        st.subheader("Dollar, commodities, crypto")
        cols = st.columns(5)
        for col, (tk, lbl, fm) in zip(cols, [
                ("DX-Y.NYB", "Dollar (DXY)", "{:.1f}"),
                ("GC=F", "Gold", "{:,.0f}"),
                ("HG=F", "Copper", "{:.2f}"),
                ("CL=F", "WTI crude", "{:.1f}"),
                ("BTC-USD", "Bitcoin", "{:,.0f}")]):
            with col:
                if tk in px and px[tk].dropna().size > 5:
                    s = px[tk].dropna()
                    r1m = (s.iloc[-1] / s.iloc[-21] - 1) * 100 if len(s) > 21 else float("nan")
                    st.metric(lbl, fm.format(s.iloc[-1]),
                              f"{r1m:+.1f}% 1-mo" if r1m == r1m else "")
                    st.caption(f"as of {asof(s)}")
                else:
                    st.warning(f"{lbl}: n/a")

    with st.expander("Methodology & limitations"):
        st.markdown(
            "- **Valuation**: CAPE / P/E / P/S / div yield from multpl.com (monthly). "
            "Buffett indicator: official FRED/WDI annual series (lags several years) + a live estimate "
            "scaling the last annual ratio by Wilshire-5000 and nominal GDP moves since — an approximation, labeled as such.\n"
            "- **Economy**: FRED series as published (subject to revision). YoY transforms labeled. FRED loads via the official API when a free FRED_API_KEY is set (recommended), else direct CSV, with the DBnomics FRED mirror as automatic fallback.\n"
            "- **Markets**: Yahoo Finance adjusted closes; weekend/holiday gaps forward-filled.\n"
            "- Percentiles rank the current value against each series' full history.\n"
            "- Valuation gauges predict long-horizon returns, not timing. Regime pills are "
            "transparent rules of thumb, not signals."
        )


main()
