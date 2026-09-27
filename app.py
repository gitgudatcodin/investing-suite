"""Investing Suite — one home for every research tool.

Run:  pip install -r requirements.txt && streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Investing Suite", page_icon="🏛️", layout="wide")

st.title("🏛️ Investing Suite")
st.markdown(
    "Every stock/investment research app in one place. Pick a tool below "
    "or from the sidebar — each opens as its own page, no API keys needed anywhere."
)
st.warning(
    "**Research tooling, not investment advice.** Screeners produce candidates, "
    "backtests are not predictions, and valuation gauges estimate long-horizon "
    "returns — they don't time markets."
)

tools = [
    ("pages/01_Market_Pulse.py", "📊 Market Pulse",
     "Real-time trader dashboard: regime strip (valuation, curve, credit, VIX, labor, inflation), "
     "live Shiller CAPE & Buffett indicator, ~20 FRED economy series, market prices."),
    ("pages/02_Stock_Screeners.py", "🔬 Stock Screeners",
     "Six S&P 500 / S&P 1500 strategies — Undiscovered Growth, Fallen Quality, Gross Profitability, "
     "Momentum, Profitable Value, Composite — with watchlists, run-fresh screens, and honest backtests vs SPY."),
    ("pages/03_Portfolio_Analytics.py", "💼 Portfolio Analytics",
     "Institutional-style portfolio diagnostics: CAGR, Sharpe/Sortino, drawdowns, VaR/CVaR, "
     "factor exposures, rolling risk, correlation — from Yahoo prices, no keys."),
    ("pages/04_Kelly_Sizer.py", "🎯 Kelly Position Sizer",
     "Size positions with the Kelly criterion: editable bet table, edge check, "
     "growth-optimal (multivariate Kelly) and conviction-weighted diversified modes."),
    ("pages/05_Quant_Lab.py", "🧪 Quant Lab",
     "Five strategy workbenches — pairs trading, ML signals, RL agent, sentiment signals, "
     "sentiment strategy — each backtested point-in-time with costs, benchmarked vs SPY."),
]

for path, label, desc in tools:
    c1, c2 = st.columns([1, 4])
    with c1:
        st.page_link(path, label=f"Open {label}")
    with c2:
        st.subheader(label)
        st.markdown(desc)
    st.divider()

st.caption("Data: FRED · multpl.com · Yahoo Finance · SEC EDGAR · Stooq. "
           "Cached where noted on each tool's page.")
