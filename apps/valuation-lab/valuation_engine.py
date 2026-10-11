"""Valuation Lab engine — importable, no Streamlit dependency.

Same functions the Streamlit app uses; the app imports from here so the
interactive tool and any headless/scheduled use always share one engine.
"""
import json
import numpy as np
import pandas as pd
import time
import yfinance as yf


HORIZON = 5  # projection years


def _yahoo_session():
    """Browser-impersonating session so Yahoo is less likely to flag requests
    as bot traffic (HTTP 429 crumb rate-limits / 401 'Invalid Crumb')."""
    try:
        from curl_cffi import requests as _creq
        return _creq.Session(impersonate="chrome")
    except Exception:
        return None


def _fallback_price(ticker: str):
    """Last-resort price fallback: Nasdaq's public quote API (no key)."""
    try:
        import urllib.request
        import json
        url = f"https://api.nasdaq.com/api/quote/{ticker}/info?assetclass=stocks"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        px = (data.get("data") or {}).get("primaryData", {}).get("lastSalePrice") or ""
        px = float(px.replace("$", "").replace(",", ""))
        return px if px > 0 else None
    except Exception:
        return None


_UA_SEC = {"User-Agent": "ValuationLab research@example.com", "Accept-Encoding": "gzip"}
_EDGAR_REV_TAGS = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
                   "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"]
_EDGAR_NI_TAGS = ["NetIncomeLoss"]
_EDGAR_SH_TAGS = ["WeightedAverageNumberOfDilutedSharesOutstanding"]
_edgar_cik_cache = None


def _edgar_cik(ticker: str):
    """Ticker -> SEC CIK via the SEC's own ticker list (cached in memory)."""
    global _edgar_cik_cache
    if _edgar_cik_cache is None:
        try:
            import urllib.request
            import gzip
            req = urllib.request.Request("https://www.sec.gov/files/company_tickers.json",
                                         headers=_UA_SEC)
            raw = urllib.request.urlopen(req, timeout=20).read()
            try:
                raw = gzip.decompress(raw)
            except Exception:
                pass
            _edgar_cik_cache = {v["ticker"].upper(): v["cik_str"]
                                for v in json.loads(raw).values()}
        except Exception:
            return None
    return (_edgar_cik_cache or {}).get(ticker.upper())


def _edgar_qseries(facts: dict, tags, unit="USD"):
    """Quarterly (10-Q/10-K) series for a tag, sorted by period end."""
    for tag in tags:
        try:
            units = facts["facts"]["us-gaap"][tag]["units"][unit]
        except KeyError:
            continue
        pts = {}
        for u in units:
            if u.get("form") not in ("10-Q", "10-K"):
                continue
            if u.get("fp") not in ("Q1", "Q2", "Q3", "Q4"):
                continue
            try:
                pts[u["end"]] = float(u["val"])
            except (KeyError, TypeError, ValueError):
                pass
        if len(pts) >= 8:
            return sorted(pts.items())
    return []


def _edgar_fundamentals(ticker: str, price: float) -> dict:
    """SEC EDGAR fallback when Yahoo fundamentals are blocked. Returns
    {name, market_cap, shares, trailing_pe, ttm_margin, hist} or {}."""
    cik = _edgar_cik(ticker)
    if not cik:
        return {}
    try:
        import urllib.request
        import gzip
        req = urllib.request.Request(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json",
            headers=_UA_SEC)
        raw = urllib.request.urlopen(req, timeout=30).read()
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
        facts = json.loads(raw)
    except Exception:
        return {}

    rev = _edgar_qseries(facts, _EDGAR_REV_TAGS)
    ni = _edgar_qseries(facts, _EDGAR_NI_TAGS)
    sh = _edgar_qseries(facts, _EDGAR_SH_TAGS, unit="shares")
    if len(rev) < 8 or len(ni) < 8:
        return {}

    rev_d, ni_d = dict(rev), dict(ni)
    ends = sorted(set(rev_d) & set(ni_d))
    if len(ends) < 8:
        return {}
    n_years = min(6, len(ends) // 4)
    ann_rev = [sum(rev_d[e] for e in ends[-(4 * (i + 1)): len(ends) - 4 * i])
               for i in range(n_years)]
    ann_ni = [sum(ni_d[e] for e in ends[-(4 * (i + 1)): len(ends) - 4 * i])
              for i in range(n_years)]
    margins = [n / r * 100 for n, r in zip(ann_ni, ann_rev) if r]
    if not ann_rev[0]:
        return {}

    ttm_rev, ttm_ni = ann_rev[0], ann_ni[0]
    ttm_sh = sum(v for _, v in sh[-4:]) / 4 if len(sh) >= 4 else None

    shares_out = None
    try:
        units = facts["facts"]["us-gaap"]["CommonStockSharesOutstanding"]["units"]["shares"]
        pts = sorted(((u["end"], float(u["val"])) for u in units if "val" in u))
        if pts:
            shares_out = pts[-1][1]
    except KeyError:
        pass
    if not shares_out and sh:
        shares_out = sh[-1][1]

    ttm_eps = ttm_ni / ttm_sh if ttm_sh else None
    hist = {
        "revenue_ttm": float(ttm_rev),
        "ni_ttm": float(ttm_ni),
        "rev_cagr_5y": ((ann_rev[0] / ann_rev[-1]) ** (1 / (n_years - 1)) - 1
                        if n_years > 1 and ann_rev[-1] else None),
        "rev_cagr_3y": ((ann_rev[0] / ann_rev[2]) ** (1 / 2) - 1
                        if n_years >= 3 and ann_rev[2] else None),
        "margin_avg_5y": float(sum(margins) / len(margins)) if margins else None,
        "margin_min_5y": float(min(margins)) if margins else None,
        "margin_max_5y": float(max(margins)) if margins else None,
    }
    out = {"hist": hist, "fund_source": "edgar"}
    try:
        if facts.get("entityName"):
            out["name"] = facts["entityName"]
    except Exception:
        pass
    if shares_out:
        out["shares"] = float(shares_out)
        out["market_cap"] = float(price * shares_out)
    if ttm_eps and ttm_eps > 0:
        out["trailing_pe"] = float(price / ttm_eps)
    out["ttm_margin"] = float(ttm_ni / ttm_rev * 100)
    return out


def fetch_company(ticker: str) -> dict:
    """Pull live fundamentals + history. Never raises — returns {'error': msg}
    on failure so the UI can fall back to manual entry."""
    info, t = {}, None
    for attempt in range(3):
        try:
            sess = _yahoo_session()
            t = yf.Ticker(ticker, session=sess) if sess is not None else yf.Ticker(ticker)
            info = t.info or {}
            if info.get("currentPrice") or info.get("regularMarketPrice"):
                break
        except Exception:
            info = {}
        if attempt < 2:
            time.sleep(1.5 * (attempt + 1))
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    if not price and t is not None:
        try:
            price = float(t.fast_info.get("last_price"))
        except Exception:
            price = None
    degraded = False
    if not price:
        # Yahoo blocked us entirely — at least get a price from Nasdaq so the
        # app loads; fundamentals fall back to manual entry.
        price = _fallback_price(ticker)
        degraded = price is not None
    if not price:
        return {"error": f"Could not fetch data for '{ticker}'. Check the ticker or enter data manually."}

    out = {
        "ticker": ticker.upper(),
        "name": info.get("longName") or info.get("shortName") or ticker.upper(),
        "price": float(price),
        "degraded": degraded,
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
    # --- EDGAR fallback: fill whatever Yahoo missed (free, no key) ------------
    if (not out.get("market_cap") or not out.get("trailing_pe")
            or not hist.get("rev_cagr_5y")):
        ed = _edgar_fundamentals(ticker, float(price))
        if ed:
            for k in ("name", "market_cap", "shares", "trailing_pe", "ttm_margin"):
                if not out.get(k) and ed.get(k) is not None:
                    out[k] = ed[k]
            if ed.get("name") and out.get("name") == ticker.upper():
                out["name"] = ed["name"]  # prefer "Apple Inc." over bare "AAPL"
            for k, v in ed.get("hist", {}).items():
                if hist.get(k) is None and v is not None:
                    hist[k] = v
            if any(out.get(k) for k in ("market_cap", "trailing_pe")):
                out["fund_source"] = "edgar"
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




def multiples_value(fwd_eps: float, pe_bear: float, pe_base: float,
                    pe_bull: float, price: float,
                    w_bear: float = 0.25, w_base: float = 0.50,
                    w_bull: float = 0.25) -> dict:
    """Simple multiples valuation: fair value = forward EPS x target P/E.

    No projection machinery, no discounting — the P/E scenarios carry all
    the growth/multiple judgment explicitly. Pure function, no Streamlit.
    Returns scenario target prices, the probability-weighted fair value,
    upside vs the current price, and the P/E implied by the fair value.
    """
    scenarios = {
        "bear": fwd_eps * pe_bear,
        "base": fwd_eps * pe_base,
        "bull": fwd_eps * pe_bull,
    }
    w_sum = w_bear + w_base + w_bull
    fv = (w_bear * scenarios["bear"] + w_base * scenarios["base"]
          + w_bull * scenarios["bull"]) / w_sum if w_sum else float("nan")
    return {
        "scenarios": scenarios,
        "fair_value": fv,
        "weights": {"bear": w_bear, "base": w_base, "bull": w_bull},
        "fwd_eps": fwd_eps,
        "pe": {"bear": pe_bear, "base": pe_base, "bull": pe_bull},
        "upside": (fv / price - 1) if price else None,
        "implied_pe": (fv / fwd_eps) if fwd_eps else None,
    }
