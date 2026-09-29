"""Valuation Lab engine — importable, no Streamlit dependency.

Same functions the Streamlit app uses; the app imports from here so the
interactive tool and any headless/scheduled use always share one engine.
"""
import numpy as np
import pandas as pd
import yfinance as yf


HORIZON = 5  # projection years


def fetch_company(ticker: str) -> dict:
    """Pull live fundamentals + history. Never raises — returns {'error': msg}
    on failure so the UI can fall back to manual entry."""
    t = yf.Ticker(ticker)
    try:
        info = t.info or {}
    except Exception:
        info = {}
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    if not price:
        try:
            price = float(t.fast_info.get("last_price"))
        except Exception:
            price = None
    if not price:
        return {"error": f"Could not fetch data for '{ticker}'. Check the ticker or enter data manually."}

    out = {
        "ticker": ticker.upper(),
        "name": info.get("longName") or info.get("shortName") or ticker.upper(),
        "price": float(price),
        "market_cap": info.get("marketCap"),
        "shares": info.get("sharesOutstanding"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "peg": info.get("pegRatio"),
        "ttm_margin": (info.get("profitMargins") or 0) * 100,
        "dividend_yield": info.get("dividendYield"),
        "currency": info.get("currency"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }

    # --- annual history: revenue, net income, FCF, margins -----------------
    try:
        fin = t.financials
        rev = fin.loc["Total Revenue"].sort_index() if "Total Revenue" in fin.index else None
        ni = None
        for key in ("Net Income", "Net Income Common Stockholders"):
            if key in fin.index:
                ni = fin.loc[key].sort_index()
                break
    except Exception:
        rev, ni = None, None
    try:
        cf = t.cashflow
        ocf = cf.loc["Operating Cash Flow"].sort_index() if "Operating Cash Flow" in cf.index else None
        capex = cf.loc["Capital Expenditure"].sort_index() if "Capital Expenditure" in cf.index else None
        fcf = (ocf + capex) if (ocf is not None and capex is not None) else None  # capex is negative
    except Exception:
        fcf = None

    hist = {}
    if rev is not None and len(rev) >= 2:
        rev = rev.dropna()
        yrs = len(rev) - 1
        hist["rev_cagr_5y"] = (rev.iloc[-1] / rev.iloc[0]) ** (1 / yrs) - 1 if yrs and rev.iloc[0] else None
        hist["rev_cagr_3y"] = (rev.iloc[-1] / rev.iloc[-3]) ** (1 / 2) - 1 if len(rev) >= 3 and rev.iloc[-3] else None
        hist["revenue_ttm"] = float(rev.iloc[-1])
    if ni is not None and rev is not None:
        common = pd.DataFrame({"rev": rev, "ni": ni}).dropna()
        if len(common):
            margins = (common["ni"] / common["rev"] * 100)
            hist["margin_min_5y"] = float(margins.min())
            hist["margin_max_5y"] = float(margins.max())
            hist["margin_avg_5y"] = float(margins.mean())
            hist["ni_ttm"] = float(common["ni"].iloc[-1])
    if fcf is not None and rev is not None:
        common = pd.DataFrame({"rev": rev, "fcf": fcf}).dropna()
        if len(common):
            fm = common["fcf"] / common["rev"] * 100
            hist["fcf_margin_avg"] = float(fm.mean())
            hist["fcf_ttm"] = float(common["fcf"].iloc[-1])
    out["hist"] = hist
    return out


def project(sc: dict, base: dict, years: int = HORIZON) -> pd.DataFrame:
    """Scenario projection. The applied P/E fades linearly from today's
    multiple to the exit range over the horizon — multiples compress as
    growth matures, so year-1 targets shouldn't already use the year-5
    multiple. Target prices are masked when EPS is non-positive."""
    rows = []
    rev = base["revenue_ttm"]
    shares = base["shares"]
    r = sc["discount"] / 100.0
    cur_pe = base.get("current_pe")
    fade = bool(cur_pe and cur_pe > 0)
    for t in range(1, years + 1):
        rev *= 1 + sc["rev_growth"] / 100.0
        margin = sc["margin_start"] + (sc["margin_end"] - sc["margin_start"]) * t / years
        ni = rev * margin / 100.0
        shares *= 1 + sc["share_change"] / 100.0
        eps = ni / shares if shares else np.nan
        fcf = rev * sc["fcf_margin"] / 100.0
        fcf_ps = fcf / shares if shares else np.nan
        w = t / years
        pe_lo_t = cur_pe + (sc["pe_lo"] - cur_pe) * w if fade else sc["pe_lo"]
        pe_hi_t = cur_pe + (sc["pe_hi"] - cur_pe) * w if fade else sc["pe_hi"]
        if isinstance(eps, float) and np.isfinite(eps) and eps > 0:
            p_lo, p_hi = eps * pe_lo_t, eps * pe_hi_t
        else:
            p_lo = p_hi = np.nan
        disc = (1 + r) ** t

        def _cagr(p):
            return ((p / base["price"]) ** (1 / t) - 1) * 100 if np.isfinite(p) and p > 0 else np.nan

        rows.append({
            "Year": t,
            "Revenue": rev,
            "Net income": ni,
            "Net margin %": margin,
            "EPS": eps,
            "FCF/share": fcf_ps,
            "PE lo": pe_lo_t,
            "PE hi": pe_hi_t,
            "Price lo": p_lo,
            "Price hi": p_hi,
            "PV lo": p_lo / disc,
            "PV hi": p_hi / disc,
            "CAGR lo %": _cagr(p_lo),
            "CAGR hi %": _cagr(p_hi),
        })
    return pd.DataFrame(rows)


def implied_growth(mktcap: float, fcf0: float, r: float = 0.10,
                   n: int = HORIZON, gt: float = 0.025):
    """Reverse DCF: what constant FCF growth rate g over n years justifies the
    current market cap? Returns None if FCF is non-positive (nothing sane to
    solve for) or the market cap is absurd."""
    if not fcf0 or fcf0 <= 0 or r <= gt:
        return None

    def pv(g):
        v, f = 0.0, fcf0
        for t in range(1, n + 1):
            f *= 1 + g
            v += f / (1 + r) ** t
        v += (f * (1 + gt) / (r - gt)) / (1 + r) ** n
        return v

    lo, hi = -0.30, 0.60
    if pv(lo) > mktcap:
        return lo  # priced for shrinkage — deep value or broken model
    if pv(hi) < mktcap:
        return hi  # priced for >60% growth — mania or model miss
    for _ in range(60):
        mid = (lo + hi) / 2
        if pv(mid) < mktcap:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


