"""Kelly Position Sizer — size stock positions with the Kelly criterion.

Run:  pip install -r requirements.txt && streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Kelly Position Sizer", page_icon="🎯", layout="wide")

st.title("🎯 Kelly Position Sizer")
st.markdown(
    "Size stock positions with the **Kelly criterion** — `f* = p − (1−p) / b` — "
    "bet in proportion to your edge. Edit the table, tune the assumptions, "
    "and get a growth-optimal portfolio."
)

# ---------------------------------------------------------------- presets
# (ticker, win prob %, price $, target $, downside %, beta) — Sept 26, 2026 research
PRESETS = [
    ("ADBE", 60, 235.47, 465.00, 36.3, 1.40),
    ("GRAB", 55, 3.13, 6.00, 36.2, 0.81),
    ("FI", 55, 46.73, 85.00, 38.0, 1.00),
    ("DKNG", 55, 22.02, 36.00, 44.6, 1.69),
    ("MCD", 65, 236.50, 300.00, 24.2, 0.45),
    ("BKNG", 60, 163.95, 222.00, 34.3, 1.16),
    ("NFLX", 65, 71.15, 90.00, 32.3, 1.61),
    ("ZTS", 55, 71.05, 108.00, 35.2, 0.70),
    ("SOFI", 55, 16.58, 23.50, 50.3, 2.30),
    ("FIS", 55, 35.41, 49.50, 37.0, 0.89),
    ("CELH", 55, 27.99, 38.00, 42.8, 1.50),
    ("NKE", 55, 35.75, 46.00, 38.6, 1.06),
    ("PYPL", 55, 55.04, 70.00, 41.4, 1.36),
    ("META", 60, 751.66, 780.00, 35.1, 1.26),
]

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Assumptions")
    kelly_frac = st.slider(
        "Kelly fraction", 0.10, 1.00, 0.50, 0.05,
        help="Full Kelly maximizes long-run growth but demands brutal drawdowns. "
             "0.50 (half-Kelly) is the professional standard.")
    p_adj = st.slider(
        "Shift all win probabilities by (pp)", -10, 10, 0, 1,
        help="Sensitivity test: what if you're more/less confident than your base case?")
    cash_pct = st.slider("Cash reserve (%)", 0, 50, 10)
    max_pos = st.slider("Max single position (%)", 5, 100, 100,
                        help="Cap any one stock. 100 = no cap (pure Kelly).")
    dust = st.slider("Drop positions below (%)", 0.0, 5.0, 1.0,
                     help="Positions smaller than this are dropped as not worth the complexity.")
    st.divider()
    st.subheader("Covariance model")
    sig_m = st.slider("Market volatility (annual)", 0.05, 0.40, 0.20, 0.01)
    sig_e = st.slider("Idiosyncratic vol (annual)", 0.10, 0.60, 0.30, 0.01)
    st.caption("Single-index model: Σ = σₘ²·ββᵀ + σₑ²·I")
    st.divider()
    portfolio_value = st.number_input("Portfolio value ($)", min_value=1000,
                                      value=100000, step=5000)

# ---------------------------------------------------------------- inputs
st.subheader("Your bets — edit any cell, add or delete rows")
base_df = pd.DataFrame(PRESETS, columns=["Ticker", "Win prob %", "Price $",
                                        "Target $", "Downside %", "Beta"])
edited = st.data_editor(
    base_df, num_rows="dynamic", width="stretch", hide_index=True,
    column_config={
        "Ticker": st.column_config.TextColumn("Ticker", width="small"),
        "Win prob %": st.column_config.NumberColumn(
            "Win prob %", format="%.0f%%", min_value=1, max_value=99, step=1,
            help="Probability your thesis plays out over ~12 months."),
        "Price $": st.column_config.NumberColumn("Price $", format="$%.2f", min_value=0.01),
        "Target $": st.column_config.NumberColumn("Target $", format="$%.2f", min_value=0.01),
        "Downside %": st.column_config.NumberColumn(
            "Downside %", format="%.1f%%", min_value=1, max_value=99,
            help="How far the stock falls if your thesis is wrong."),
        "Beta": st.column_config.NumberColumn("Beta", format="%.2f", min_value=0.0, max_value=5.0),
    },
)
st.caption("Incomplete rows are ignored. Upside is computed as Target ÷ Price − 1.")

df = edited.dropna(subset=["Ticker"]).copy()
df = df.dropna(subset=["Win prob %", "Price $", "Target $", "Downside %", "Beta"])
df = df[(df["Price $"] > 0) & (df["Target $"] > 0) & (df["Downside %"] > 0)]
if df.empty:
    st.warning("Add at least one complete stock row to compute position sizes.")
    st.stop()

tickers = df["Ticker"].astype(str).str.strip().tolist()
n = len(tickers)
p = np.clip(df["Win prob %"].to_numpy(dtype=float) / 100 + p_adj / 100, 0.01, 0.99)
price = df["Price $"].to_numpy(dtype=float)
target = df["Target $"].to_numpy(dtype=float)
down = np.abs(df["Downside %"].to_numpy(dtype=float)) / 100
beta = df["Beta"].to_numpy(dtype=float)

# ---------------------------------------------------------------- Kelly math
upside = target / price - 1.0
odds = upside / np.maximum(down, 1e-6)
k_disc = p - (1.0 - p) / np.maximum(odds, 1e-9)   # discrete Kelly per bet
mu = p * upside - (1.0 - p) * down                 # expected 12-mo return

Sigma = sig_m ** 2 * np.outer(beta, beta) + np.diag(np.full(n, sig_e ** 2)) + np.eye(n) * 1e-8

# Long-only growth-optimal portfolio: w = Sigma^-1 mu, dropping negative weights
w_full = np.zeros(n)
if np.any(mu > 0):
    keep = np.ones(n, dtype=bool)
    for _ in range(50):
        idx = np.where(keep)[0]
        if len(idx) == 0:
            break
        w = np.linalg.solve(Sigma[np.ix_(idx, idx)], mu[idx])
        neg = idx[w < 1e-9]
        if len(neg) == 0:
            break
        keep[neg] = False
    idx = np.where(keep)[0]
    if len(idx):
        w = np.maximum(np.linalg.solve(Sigma[np.ix_(idx, idx)], mu[idx]), 0.0)
        w_full[idx] = w

w_frac = kelly_frac * w_full

# ---------------------------------------------------------------- edge table
# Display columns are in percent units (Streamlit's % format does NOT x100).
st.subheader("Edge check — who earns a bet?")
edge = pd.DataFrame({
    "Ticker": tickers,
    "Win prob": p * 100,
    "Upside": upside * 100,
    "Downside": down * 100,
    "Odds": odds,
    "Kelly f*": k_disc * 100,
    "E[return]": mu * 100,
})
edge["Verdict"] = np.where(k_disc > 0.005, "✅ BET",
                   np.where(k_disc > -0.005, "➖ MARGINAL", "⛔ NO BET"))
edge = edge.sort_values("Kelly f*", ascending=False).reset_index(drop=True)
st.dataframe(
    edge, width="stretch", hide_index=True,
    column_config={
        "Win prob": st.column_config.NumberColumn(format="%.0f%%"),
        "Upside": st.column_config.NumberColumn(format="%.1f%%"),
        "Downside": st.column_config.NumberColumn(format="%.1f%%"),
        "Odds": st.column_config.NumberColumn(format="%.2f"),
        "Kelly f*": st.column_config.NumberColumn(format="%.1f%%"),
        "E[return]": st.column_config.NumberColumn(format="%.1f%%"),
    },
)

# ---------------------------------------------------------------- portfolio
st.subheader("Optimal portfolio")
mode = st.radio(
    "Sizing mode",
    ("🎯 Growth-optimal (pure Kelly)", "🛡️ Conviction-weighted (diversified)"),
    horizontal=True,
    help="Pure Kelly is the mathematically optimal portfolio — concentrated by design. "
         "Conviction-weighted uses per-stock fractional Kelly as conviction scores "
         "with your caps — diversified by design.",
)

def finalize(w):
    """Cap -> normalize to invested -> dust filter -> renormalize."""
    w = np.array(w, dtype=float).copy()
    cap = max_pos / 100.0
    for _ in range(30):  # iterative water-fill for the max-position cap
        over = w > cap
        if not over.any():
            break
        excess = float((w[over] - cap).sum())
        w[over] = cap
        under = ~over & (w > 0)
        if under.any() and w[under].sum() > 0:
            w[under] += excess * w[under] / w[under].sum()
    invested = 1.0 - cash_pct / 100.0
    tot = w.sum()
    w = w / tot * invested if tot > 0 else w
    w[w < dust / 100.0] = 0.0
    tot = w.sum()
    return w / tot * invested if tot > 0 else w

w_growth = finalize(w_frac)                                # multivariate, fraction applied
w_conv = finalize(kelly_frac * np.maximum(k_disc, 0.0))    # discrete conviction scores

if mode.startswith("🎯"):
    w_final = w_growth
    lev = float(w_full.sum())
    st.caption("Multivariate Kelly **w = Σ⁻¹μ**, solved long-only. It concentrates on the "
               "highest edge-per-unit-risk bets — diversifiers earn zero weight by design.")
else:
    w_final = w_conv
    lev = float(np.maximum(k_disc, 0.0).sum())
    st.caption("Per-stock fractional Kelly as conviction scores, then your caps, dust filter, "
               "and cash reserve. Diversified by design — matches the guardrailed portfolio.")

res = pd.DataFrame({
    "Ticker": tickers,
    "Weight": w_final * 100,   # percent units for display
    "$ amount": w_final * portfolio_value,
    "Full-Kelly w": w_full,
})
res = res[res["Weight"] > 0].sort_values("Weight", ascending=False).reset_index(drop=True)

if res.empty:
    st.warning("No positive-edge names at these inputs — Kelly says hold cash. "
               "Raise win probabilities or targets, or lower downsides.")
else:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.bar_chart(res.set_index("Ticker")["Weight"], horizontal=True,
                     x_label="Portfolio weight (%)", y_label="")
    with c2:
        st.dataframe(
            res[["Ticker", "Weight", "$ amount"]], width="stretch", hide_index=True,
            column_config={
                "Weight": st.column_config.NumberColumn(format="%.1f%%"),
                "$ amount": st.column_config.NumberColumn(format="$%.0f"),
            },
        )

    er = float(w_final @ mu)
    vol = float(np.sqrt(w_final @ Sigma @ w_final))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Expected 12-mo return", f"{er:.1%}")
    m2.metric("Portfolio volatility", f"{vol:.1%}")
    m3.metric("Names held", f"{len(res)} of {n}")
    m4.metric("Full Kelly demanded", f"{lev:.0%}",
              help="Total leverage raw Kelly wanted before your fraction/caps. "
                   "Over 100% = it wanted margin.")

    excluded = edge[~edge["Ticker"].isin(res["Ticker"])]["Ticker"].tolist()
    if excluded:
        st.info("Excluded: **" + "**, **".join(excluded) +
                "** — zero/negative edge or below the dust threshold at these inputs.")

# ---------------------------------------------------------------- explainer
with st.expander("How this works — the math, plainly"):
    st.markdown(
        """
**The formula.** For a bet with win probability *p*, loss probability *q = 1−p*,
and net odds *b* (profit per $1 staked): **f\\* = p − q/b**. Bet in proportion
to your edge; it maximizes long-run compound growth.

**From bets to stocks.** Each stock is treated as a binary-ish bet:
- *Upside* = Target ÷ Price − 1, *Downside* = your loss estimate if wrong
- *Odds b* = Upside ÷ Downside
- *Expected return μ* = p·Upside − (1−p)·Downside

**From stocks to a portfolio.** For correlated bets, Kelly generalizes to the
*growth-optimal portfolio*: **w = Σ⁻¹μ** (inverse covariance × expected returns),
solved long-only by iteratively dropping negative weights. Covariance comes from
a single-index model: Σ = σₘ²ββᵀ + σₑ²I, with your sidebar volatilities.

**Why fractional Kelly.** Full Kelly assumes your *p* and payoffs are *true*.
They're judgments. Halving (or quartering) the fraction is the professional
response to estimation error — overbetting destroys wealth faster than
underbetting builds it.

**Caveats.** This optimizes median wealth over many repeated bets, not one
12-month horizon; it assumes no fat tails and no leverage limits beyond your caps.
Expected returns inherit whatever optimism lives in your targets. Treat it as a
sizing discipline, not a prediction.
        """)
