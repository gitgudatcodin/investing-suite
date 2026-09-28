# Market Pulse — trader dashboard

Real-time economic indicators and market-valuation gauges for traders and
investors. No API keys required — data from FRED, multpl.com, and Yahoo
Finance. (An optional free FRED key makes economic data bulletproof;
see below.)

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What's inside

- **Regime strip** — six at-a-glance pills: valuation (CAPE percentile),
  yield-curve shape, credit stress, VIX fear, labor (Sahm rule), inflation
  vs the Fed's 2% target.
- **💰 Valuation tab** — Shiller CAPE (live history + percentile), Buffett
  indicator (official annual series + live estimate with disclosed method),
  excess CAPE yield, trailing P/E, price/sales, dividend yield.
- **🏭 Economy tab** — GDP, industrial production, retail sales; unemployment,
  payrolls, jobless claims, JOLTS, wage growth; CPI headline/core, core PCE,
  5-yr breakevens; 2-yr/10-yr yields, 2s10s curve, real yields; Michigan
  sentiment, Case-Shiller, housing starts, mortgage rates.
- **📈 Markets tab** — S&P 500, VIX, 10-yr yield, equal-vs-cap-weight breadth
  (RSP/SPY), HY/IG credit spreads, dollar, gold, copper, oil, bitcoin.

## Notes

- **Local database** (`data/market_pulse.db`, SQLite): all series are
  bulk-downloaded once, then updated incrementally — each series is only
  refetched when its release calendar says new data can exist (daily series
  after the last weekday, monthly after the prior month, etc.). A normal
  launch does zero network requests and renders instantly.
- FRED's public CSV endpoint throttles aggressively (many cloud IPs are
  blocked outright), so every FRED series fails over fast (6s) to the
  DBnomics FRED mirror (no key). The DB ships pre-seeded with multpl +
  Yahoo history; FRED series fill on first run. `python seed_db.py`
  re-seeds from scratch.

## Free FRED API key — recommended (2 minutes, no credit card)

This is the reliable path for economic data: FRED's website throttles cloud
hosts, and third-party mirrors can break. The official API works everywhere.

1. Sign up at https://fred.stlouisfed.org/docs/api/api_key.html
   (free account, instant key, no credit card).
2. Add it next to your Turso secrets in Streamlit Cloud → Settings →
   Secrets (or as an env var locally):

```toml
FRED_API_KEY = "..."
```

That's it — the app tries the official API first, then the CSV endpoint,
then DBnomics. With the key set, the whole Economy tab and all FRED-backed
cards (Buffett indicator, excess CAPE yield, credit spreads) backfill
automatically on the next run.

## Shared cloud database (Turso) — recommended for Streamlit Cloud

The local `data/market_pulse.db` works, but Streamlit Cloud wipes the
container filesystem on every sleep/reboot, so runtime updates don't survive.
Point the app at a free [Turso](https://turso.tech) database (hosted SQLite,
generous free tier, no credit card) and all viewers share one live,
persistent DB:

```bash
# one-time setup (~5 min)
curl -sSfL https://get.tur.so/install.sh | bash
turso auth login
turso db create market-pulse
turso db show market-pulse --url            # -> TURSO_DATABASE_URL
turso db tokens create market-pulse         # -> TURSO_AUTH_TOKEN

# seed it from your machine (FRED series fill on first app run)
export TURSO_DATABASE_URL="libsql://..." TURSO_AUTH_TOKEN="..."
python seed_db.py
```

Then in Streamlit Cloud: app → Settings → Secrets, add

```toml
TURSO_DATABASE_URL = "libsql://your-db.turso.io"
TURSO_AUTH_TOKEN = "..."
```

and reboot the app. Without these variables the app quietly uses the local
SQLite file instead — zero-config, just not shared across reboots.
