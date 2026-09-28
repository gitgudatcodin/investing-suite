# Investing Suite

One Streamlit app combining all six stock/investment research tools.
No API keys needed anywhere.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tools

| Page | Tool | What it does |
|------|------|--------------|
| 📊 Market Pulse | Regime dashboard | Live valuation (Shiller CAPE, Buffett indicator), ~20 FRED economy series, market prices, credit spreads |
| 🔬 Stock Screeners | 6 strategies | Undiscovered Growth, Fallen Quality, Gross Profitability, Momentum, Profitable Value, Composite — S&P 500/1500, with backtests |
| 💼 Portfolio Analytics | Diagnostics | CAGR, Sharpe/Sortino, drawdowns, VaR/CVaR, beta/alpha, rolling risk, correlations |
| 🎯 Kelly Sizer | Position sizing | Kelly-criterion sizing: growth-optimal (multivariate) + conviction-weighted diversified modes |
| 🧪 Quant Lab | 5 workbenches | Pairs trading, ML signals, RL agent, sentiment signals, sentiment strategy — honest backtests vs SPY |
| 🔬 Valuation Lab | Scenario valuator | Bull/base/bear multi-year projections (growth, margins, buybacks, exit P/E), present values, reverse-DCF check, probability-weighted fair value |

## Structure

- `app.py` — suite home page with navigation cards
- `pages/` — thin launchers, one per tool (each original app runs unmodified)
- `apps/` — the original apps: `market-pulse`, `kelly-sizer`, `portfolio-app`,
  `stock-screeners` (with its JSON datasets), `quant-lab` (engine + pages), `valuation-lab`

## Notes

- Research tooling, not investment advice.
- Screeners produce research candidates, not buy lists; several saved lists are
  unreviewed — status is labeled in the app.
- First load of Market Pulse fetches live data (~30–60s); everything is cached after that.
