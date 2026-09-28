# Market Pulse — Metric Intuition Guide

A plain-English companion to every number on the dashboard. For each metric:
**what it is**, **how this dashboard computes it**, **what counts as normal /
high / low**, and **what it actually read during the four big episodes** —
the dot-com bust (2000–02), the Global Financial Crisis (2008–09), the COVID
crash (2020), and the inflation shock (2022). All values are approximate;
check the dashboard for today's reading.

> This is research context, not investment advice.

---

## The regime strip (top of the dashboard)

Six pills, each summarizing one dimension of market weather.

### 1. Valuation (CAPE)
- **What:** Are stocks priced richly relative to a decade of earnings?
- **How:** Percentile of the Shiller CAPE within its own history. Extreme =
  above the 90th percentile, Expensive = above the 75th.
- **Normal / high / low:** "Fair" (25th–75th percentile) is normal. Extreme
  has historically preceded decade-long stretches of poor returns, not
  necessarily an imminent crash.
- **History:** Sat at Extreme through 1998–2001 and again 2017–2026 with
  brief breaks. Was merely "Fair" in 2009–2012 — the best buying zone of
  the modern era.

### 2. Yield curve 2s10s
- **What:** The bond market's recession forecast. Banks borrow short and lend
  long, so an inverted curve (short rates above long rates) squeezes lending
  and has preceded every US recession since the 1970s.
- **How:** 10-year Treasury yield minus 2-year Treasury yield, in percentage
  points. Inverted < 0, Flat < 1, Normal ≥ 1.
- **Normal / high / low:** +1.0 to +1.5 pp is a healthy normal. Negative =
  warning; the deeper and longer, the louder.
- **History:** Inverted in 2000 (recession 2001), mid-2006–2007 (recession
  Dec 2007), 2019 briefly (recession 2020), and Jul 2022–Sep 2024 — the
  deepest (−1.05 pp) and longest inversion on record. Un-inverted in
  Sep 2024; as of 2026 no NBER recession has followed that episode, a
  reminder that the signal is about odds, not certainty — recessions
  historically *begin* after the curve un-inverts.

### 3. Credit stress
- **What:** Are lenders scared? When credit markets stress, the extra yield
  investors demand to hold junk bonds blows out — usually before stocks
  bottom.
- **How:** Percentile of the high-yield option-adjusted spread in its own
  history. Stressed > 80th percentile, Complacent < 20th.
- **Normal / high / low:** "Normal" (20th–80th) most of the time. "Complacent"
  means spreads are pricing almost no defaults — great until it isn't.
- **History:** Stressed through 2008 (spreads hit ~22%), flashed in late
  2015–early 2016 (energy defaults), Mar 2020 (~11%), and briefly in 2022.
  Read Complacent through 2024–2026 with spreads near ~3%.

### 4. Fear (VIX)
- **What:** The market's 30-day expected turbulence, priced from S&P 500
  options. Spikes when investors pay up for protection.
- **How:** Latest VIX close. Panic > 30, Elevated > 20, Calm ≤ 20.
- **Normal / high / low:** 12–20 is normal; below 12 is deep complacency
  (options are cheap — often right before a shock); above 30 is genuine
  panic and has historically been a *contrarian buy* zone for stocks.
- **History:** 2008: 89.5 (Oct 2008, all-time high). 2020: 82.7 (Mar 16,
  2020). 2022: ~36 at the October low. Aug 2024: 65 intraday during the
  yen-carry-unwind scare, then collapsed within days — a textbook
  spike-and-fade.

### 5. Labor (Sahm)
- **What:** A real-time recession tripwire from unemployment data, designed
  by economist Claudia Sahm. It fires faster than the official NBER
  recession calls, which come ~a year late.
- **How:** 3-month average unemployment minus its 12-month low. ≥ 0.5 =
  recession signal; 0.3–0.5 = softening.
- **Normal / high / low:** Near 0 is a solid labor market. 0.5 has never
  fired outside a recession — until August 2024, when it tripped (0.53)
  with no recession following, denting its perfect record.
- **History:** Fired mid-2008 (months before Lehman), April 2020
  (unemployment went 3.5% → 14.7% in two months), and the false-ish
  positive of Aug 2024.

### 6. Inflation (core PCE)
- **What:** The Fed's preferred inflation gauge — the one its 2% target is
  defined against.
- **How:** Year-over-year change in the core PCE price index (excludes food
  and energy). Hot > 3%, Above target 2–3%, At target ≈ 2%.
- **Normal / high / low:** ~2% is the target. Sustained >3% forces the Fed
  to keep rates high; <1.5% lets it cut.
- **History:** Ran 2.5–4% through the 2000s scares, collapsed toward 1% in
  2009 and 2015 (deflation worry), spiked to 5.6% in Feb 2022 — the
  hottest since the 1980s — then ground back toward ~2.5% by 2024–2026.

---

## Valuation tab

### Shiller CAPE
- **What:** The S&P 500's price divided by average inflation-adjusted
  earnings of the last 10 years. Smoothing earnings over a decade stops one
  weird year from distorting the picture. The single best long-horizon
  valuation metric ever found (Campbell-Shiller, Nobel-adjacent work).
- **How:** Live from multpl.com's Shiller P/E series (data back to 1871).
- **Normal / high / low:** Historical median ≈ 16–17. 10–20 is normal;
  below 10 is generationally cheap (seen 1920, 1932, 1982, briefly 2009);
  above 30 is expensive; above 35 has occurred only in 1929 (~33), 2000
  (~44), 2021 (~39), and 2024–2026 (~40).
- **History:** 2000 peak 44.2 → the 2000s delivered ~zero real returns for
  a decade. 2009 low 13.3 → the 2010s bull market began. High CAPE doesn't
  time crashes — it was "expensive" for most of 1992–2008 while stocks
  still rose — it forecasts *10-year* returns, which is why the dashboard
  pairs it with the percentile pill.

### Buffett indicator (est.)
- **What:** Warren Buffett's favorite valuation yardstick: total US stock
  market value ÷ GDP. "When it gets to 200%, play with caution" (Fortune,
  2001). It answers: how big is the stock market relative to the economy
  that must support it?
- **How:** The official FRED/WDI annual series (ends 2020, ~195%) scaled
  by the Wilshire-5000 price move divided by the nominal-GDP move since
  2020 — a live estimate, labeled as such.
- **Normal / high / low:** Buffett's old bands: <75% cheap, 75–90% fair,
  >120% expensive. The modern era runs hotter (median ~100% since 1990):
  treat >150% as rich, >200% as historic.
- **History:** ~183% in 2000 (then halved by 2002), ~55% in 2009 (the
  buying opportunity of a lifetime), ~211% in late 2021, ~300% in 2026 —
  the highest on record, driven by mega-cap tech outgrowing GDP.

### Excess CAPE yield
- **What:** The equity risk premium in one number: what stocks yield
  (1/CAPE) minus what inflation-proof bonds yield (real 10-yr). Positive =
  stocks compensate you for their risk; negative = bonds pay you more
  than stocks' earnings yield — a rare, extreme valuation signal.
- **How:** 100/CAPE − 10-year TIPS yield (FRED DFII10).
- **Normal / high / low:** ~3–4% is historically normal; >5% is screaming
  cheap stocks (2009, 2020); near 0% or negative means equities offer no
  compensation over safe bonds (1999–2000, 2024–2026).
- **History:** Deeply negative in 2000 (stocks doomed vs bonds — correct).
  +6–7% in early 2009 (back up the truck — correct). Hovered near 0% or
  negative through 2024–2026: the market is priced for perfection, and
  bonds are a genuine competitor for the first time in 15 years.

### Trailing P/E
- **What:** Price ÷ last 12 months' earnings. The valuation multiple you
  see quoted in headlines.
- **How:** Live from multpl.com's S&P 500 P/E ratio.
- **Normal / high / low:** Median ≈ 15–16. <12 cheap, 15–20 normal, >25
  expensive.
- **History:** ~30 in 2000 (earnings were also cyclically *high* — a
  double warning CAPE caught better). Spiked to ~40 in 2020 — but that
  was collapsed earnings (E fell), not euphoria; a lesson in why P/E
  needs CAPE beside it. ~29 in 2026: expensive on both.

### P/S (price-to-sales)
- **What:** Price ÷ revenue per share. Harder to manipulate than earnings,
  useful when earnings are depressed or negative.
- **How:** Live from multpl.com's S&P 500 price-to-sales.
- **Normal / high / low:** ~1.0–1.5 historically normal; >2 expensive;
  >3 has only happened in 2021 and 2024–2026.
- **History:** ~2.9 in 2000 (revenue multiples also bubbly), ~0.8 in 2009
  (cheap on every metric), ~3.0 in 2021, ~3.2+ in 2026 — the market is
  paying over $3 for every $1 of sales, a record.

### Dividend yield
- **What:** Annual dividends ÷ price. The "get paid to wait" component of
  returns; high yield = cheap prices and/or generous payouts.
- **How:** Live from multpl.com's S&P 500 dividend yield.
- **Normal / high / low:** ~4% was normal pre-1990; ~2% is normal since
  (buybacks replaced dividends). <1.5% = euphoric; >3% = fearful.
- **History:** 1.1% in 2000 (the ultimate "nobody wants dividends in a
  bubble" print), 3.6% in Mar 2009 (get paid 3.6% to buy the bottom),
  ~1.2% in 2026 — near record lows, consistent with extreme valuation on
  every other metric.

---

## Economy tab

### Real GDP (year-over-year)
- **What:** The economy's speedometer — inflation-adjusted output growth.
- **How:** Quarterly FRED GDP, shown as % change vs the same quarter a
  year earlier.
- **Normal / high / low:** 2–3% is healthy cruising speed; >4% is a boom
  (inflation risk); <0% is a recession.
- **History:** −4% in 2009; −9% YoY (−31% annualized) in Q2 2020, then the
  fastest snapback on record; 2–2.5% through 2024–2026 — remarkably
  steady, which is why the "soft landing" narrative survived.

### Industrial production (YoY)
- **What:** Factory, mining, and utility output. Manufacturing-heavy, so
  it swings harder than GDP — an early cyclical tell.
- **How:** FRED INDPRO, YoY %.
- **Normal / high / low:** +2–4% normal; negative for several months =
  industrial recession.
- **History:** −15% in 2009 (factories idled), −16% in Apr 2020, soft
  −1–2% readings through 2023–2024 (the "manufacturing recession" that
  services offset).

### Retail sales (YoY)
- **What:** Consumer spending at stores — the consumer is ~70% of the US
  economy, so this is demand in real time.
- **How:** FRED RSXFS (ex-food-services), YoY %, nominal dollars.
- **Normal / high / low:** +3–5% nominal is normal; negative prints are
  rare and recessionary.
- **History:** −11% in 2009; −19% in Apr 2020 (then +30% stimulus-fueled
  rebound — the weirdest whiplash in the data); steady +3–4% in
  2024–2026.

### Unemployment rate
- **What:** Share of the labor force without a job but looking. The most
  human of the macro numbers.
- **How:** FRED UNRATE, monthly %.
- **Normal / high / low:** 4–5.5% is normal; <4% is a hot labor market
  (wage/inflation pressure); >7% is a jobs crisis.
- **History:** 3.8% in 2000 (then doubled by 2003), 10.0% in Oct 2010
  (the GFC's long tail), 14.7% in Apr 2020 (then the fastest recovery
  ever), drifted 3.4% → ~4.4% in 2024–2026 — the "normalization" the Fed
  engineered.

### Nonfarm payrolls
- **What:** Jobs added/lost per month. The labor market's pulse.
- **How:** FRED PAYEMS, monthly change in thousands.
- **Normal / high / low:** +150–250k/month is healthy; negative prints =
  layoffs exceeding hiring; −500k+ = crisis.
- **History:** −700–800k/month in late 2008–early 2009; −20.5 *million*
  in Apr 2020 (a vertical line off the chart); +100–200k/month through
  2024–2026 — cooling but not collapsing.

### Jobless claims (initial)
- **What:** New unemployment filings per week. The fastest labor-market
  signal — it moves weeks before the unemployment rate.
- **How:** FRED ICSA, weekly, thousands.
- **Normal / high / low:** 200–250k is healthy; sustained >350k =
  layoff wave building.
- **History:** 665k in Mar 2009; 6.87 *million* in Mar 2020 (the single
  most shocking print of the COVID crash — 30× normal); 210–240k
  through 2024–2026 — eerily calm, which is why the Sahm scare of 2024
  faded.

### JOLTS job openings
- **What:** Unfilled jobs — labor *demand*. Openings > unemployed people
  = workers hold the cards.
- **How:** FRED JTSJOL, monthly, thousands.
- **Normal / high / low:** 5–7M was normal pre-2020; the pandemic broke
  the scale.
- **History:** 12.0M in Mar 2022 (1.9 openings per unemployed person —
  the craziest labor shortage on record, fueling the wage spike);
  normalized to ~7–8M by 2024–2026.

### Wage growth (avg hourly earnings, YoY)
- **What:** Paycheck growth. The Fed watches it as an inflation input —
  wages are costs for businesses and spending power for households.
- **How:** FRED AHETPI, YoY %.
- **Normal / high / low:** 2.5–3.5% is the Goldilocks zone; >5% feeds
  inflation; <2% means workers are losing ground.
- **History:** 2–3% through the 2010s; spiked to 5.9% in Mar 2022
  (workers finally had leverage — and it showed up in prices); cooled
  to ~3.5–4% by 2024–2026, roughly matching inflation again.

### CPI headline (YoY)
- **What:** The inflation number on the news — the cost of living.
- **How:** FRED CPIAUCSL, YoY %.
- **Normal / high / low:** ~2–3% is normal; >5% is a crisis for the Fed;
  negative = deflation (worse — debts get heavier).
- **History:** −2.1% in late 2008 (deflation scare amid the crash); 9.1%
  in Jun 2022 (40-year high — gas, food, everything); ~2.5–3% in
  2024–2026 — conquered but not quite at target.

### CPI core (YoY)
- **What:** CPI minus food and energy — the "underlying" trend, less
  noisy than headline.
- **How:** FRED CPILFESL, YoY %.
- **Normal / high / low:** ~2–2.5% normal; >4% = entrenched.
- **History:** Peaked 6.6% in Sep 2022 (shelter and services kept it
  sticky long after gas fell); ~3% in 2024–2026 — the "last mile" of
  disinflation that took years.

### Core PCE (the Fed's target, YoY)
- **What:** The inflation measure the Fed actually targets at 2%. Broader
  and smoother than CPI (it captures substitution — when beef gets
  pricey, people buy chicken).
- **How:** FRED PCEPILFE, YoY %.
- **Normal / high / low:** 2% is the target, period. 2–2.5% tolerable;
  >3% forces high rates.
- **History:** 5.6% in Feb 2022 (hottest since the 1980s); the entire
  2022–2023 rate-hike campaign was about dragging this back; ~2.5–2.9%
  in 2024–2026 — close, never quite 2.

### 5-yr inflation expectations (breakeven)
- **What:** What the bond market expects inflation to average over 5
  years — the crowd's forecast, with money behind it.
- **How:** FRED T5YIE: 5-yr Treasury yield minus 5-yr TIPS yield.
- **Normal / high / low:** 2–2.5% = anchored (the Fed is credible);
  >3% = the market doubts the Fed; <1.5% = deflation fear.
- **History:** Crashed to ~0.5% in late 2008 (markets priced *deflation*);
  spiked to 3.6% in Mar 2022 (inflation panic); ~2.5% since 2023 — the
  single most reassuring chart of the whole episode: expectations never
  de-anchored, which is why the Fed could stop hiking.

### 10-yr Treasury yield
- **What:** The world's most important interest rate — the discount rate
  for everything from mortgages to stock valuations.
- **How:** FRED DGS10, daily %.
- **Normal / high / low:** 4–5% was normal pre-2008; 2–3% was the 2010s
  normal; >5% tightens financial conditions hard.
- **History:** 6.8% in 2000, 15.8% in 1981 (the all-time high); 0.5% in
  Aug 2020 (free money era); 5.0% in Oct 2023 (the "higher for longer"
  shock that broke regional banks' bond portfolios); ~4–4.5% in
  2024–2026.

### 2-yr Treasury yield
- **What:** Where the market thinks the Fed is going — it hugs the
  expected path of short rates.
- **How:** FRED DGS2, daily %.
- **Normal / high / low:** Usually a bit below the 10-yr; when it spikes
  above, the curve inverts (see regime strip).
- **History:** 6.5%+ in 2000 and 2006–07; 0.1% in 2020; 5.2% in 2023
  (pricing "higher for longer"); ~3.5–4% in 2024–2026 as cuts were
  priced in, then partially out.

### 2s10s spread
- **What:** 10-yr minus 2-yr — the curve shape in one number. (Same as
  regime pill #2, with history.)
- **How:** FRED DGS10 − FRED DGS2, percentage points.
- **Normal / high / low:** +1.0–1.5 pp healthy; <0 inverted = recession
  warning.
- **History:** See regime strip: inverted before 2001, 2008, 2020; the
  Jul 2022–Sep 2024 inversion (−1.05 pp) was the deepest and longest
  ever, then un-inverted with (so far) no recession — the most debated
  chart in macro.

### 10-yr real yield (TIPS)
- **What:** The 10-yr yield *after* inflation — the true risk-free return.
  Negative = you're guaranteed to lose purchasing power holding safe
  bonds (which is why money flooded into stocks/crypto/housing).
- **How:** FRED DFII10, daily %.
- **Normal / high / low:** 1.5–2.5% is normal; negative is emergency
  policy; >2.5% is genuinely tight.
- **History:** −1% through 2020–2021 (financial repression — savers
  punished, asset prices levitated); +2.5% in Oct 2023 (the fastest
  real-rate spike in decades — broke SVB and UK gilts); ~2% in
  2024–2026 — normal-ish at last.

### Michigan consumer sentiment
- **What:** How households *feel* about the economy — and feelings drive
  spending. It also has a famous political/partisan skew.
- **How:** FRED UMCSENT, monthly index.
- **Normal / high / low:** 85–100 normal; >100 euphoric; <60 miserable.
- **History:** ~110 in 2000 (peak optimism, right before the bust); 55.3
  in Nov 2008; **50.0 in Jun 2022 — the all-time record low**, as
  inflation crushed real incomes (a weirder, angrier print than 2008
  because unemployment was 3.6%!); recovered only to ~55–65 by
  2024–2026 — the "vibecession": decent data, glum people.

### Case-Shiller home prices (YoY)
- **What:** US house-price inflation, the bedrock of household wealth.
- **How:** FRED CSUSHPISA, YoY %.
- **Normal / high / low:** 3–6% is healthy; >10% is a boom (affordability
  crisis); negative = housing bust.
- **History:** +14% in 2005 (bubble), then −27% peak-to-trough 2006–2012
  (the wound that caused the GFC); +19% in 2021 (remote-work +
  2.65% mortgages); ~3–4% in 2024–2026 — frozen market: prices high,
  volumes dead, nobody with a 3% mortgage will sell.

### Housing starts
- **What:** New homes breaking ground — the most interest-rate-sensitive
  sector in the economy, so it moves *first*.
- **How:** FRED HOUST, monthly annualized, thousands.
- **Normal / high / low:** 1.2–1.6M is normal; >2M is a building boom;
  <800k is a bust.
- **History:** 2.27M in Jan 2006 (the top — "they're not making more
  land" was the mantra), 478k in Apr 2009 (ghost subdivisions);
  ~1.3–1.4M in 2024–2026 — builders can't build enough *affordable*
  homes at 6.5–7% mortgage rates.

### 30-yr mortgage rate
- **What:** What a homebuyer actually pays. The transmission belt from
  Fed policy to the housing market.
- **How:** FRED MORTGAGE30US, weekly %.
- **Normal / high / low:** 6–8% is the long-run normal; <4% is stimulus;
  >8% kills demand.
- **History:** 18.6% in 1981 (yes, really); 2.65% in Jan 2021 (free
  money — fueled the housing boom); 7.79% in Oct 2023 (payment shock:
  the same house cost ~2× per month vs 2021); ~6.5% in 2024–2026.

### HY option-adjusted spread
- **What:** The extra yield junk bonds pay over Treasuries — the market's
  fear-of-default meter. (Same series as regime pill #3.)
- **How:** FRED BAMLH0A0HYM2, % (shown in percentage points on the card).
- **Normal / high / low:** 3–5% normal; >8% distressed; >15% crisis.
- **History:** ~22% in Dec 2008 (default Armageddon priced in — the
  actual bottom for risk assets); ~11% in Mar 2020; ~9% in Feb 2016
  (energy bust); ~3% in 2024–2026 — priced for perfection.

### IG option-adjusted spread
- **What:** Same idea for investment-grade corporate bonds — a subtler,
  earlier stress signal.
- **How:** FRED BAMLC0A0CM, %.
- **Normal / high / low:** ~1–1.5% normal; >3% stressed.
- **History:** ~6% in 2008 (even blue chips couldn't borrow); ~3.7% in
  Mar 2020; ~0.8–0.9% in 2024–2026 — historically tight.

---

## Markets tab

### S&P 500
- **What:** 500 large US stocks — the default scoreboard of American
  business wealth.
- **How:** Yahoo ^GSPC, daily close.
- **Normal / high / low:** No "normal" level — it's the *drawdowns* that
  matter: −10% = correction, −20% = bear market, −30%+ = crash.
- **History:** −49% (2000–02), −57% (2007–09), −34% in 33 days then
  +114% to the 2021 peak (2020 — the fastest round-trip ever), −25%
  (2022). Every −20%+ drawdown since 1950 eventually made new highs —
  the base rate behind "buy the dip," and also behind every bag-holder.

### VIX
- **What:** Same series as regime pill #4, shown here with price context.
  Read it as the market's pulse: low VIX + falling stocks = complacency
  breaking; high VIX + stabilizing stocks = fear exhausting itself.
- **History:** See regime strip. The tradable insight: VIX >40 has marked
  within days of every major bottom (2002, 2009, 2011, 2018, 2020).

### 10-yr yield (market)
- **What:** Same as the Economy tab's 10-yr, via Yahoo ^TNX (×10) — shown
  here because it's the discount rate competing with stocks *today*.
- **How to read it:** Rising yield + rising stocks = growth optimism.
  Rising yield + falling stocks = valuation compression (2022). Falling
  yield + falling stocks = flight to safety (2008, 2020).

### RSP/SPY (breadth)
- **What:** Equal-weight S&P (RSP) ÷ cap-weight S&P (SPY). When mega-caps
  carry the market, SPY outruns RSP and the ratio falls — narrow
  leadership, a late-cycle signature.
- **How:** Yahoo closes ratio; the card shows its history percentile.
- **Normal / high / low:** ~1.0 is neutral; persistently falling =
  concentration risk (a handful of stocks *are* the market).
- **History:** Fell through 1998–2000 (dot-com narrowness), 2020–2021,
  and 2023–2024 (the "Magnificent 7" era — at one point 7 stocks were
  ~35% of the S&P). Breadth thrusts (ratio rising) marked the healthy
  mid-cycle rallies of 2003–2006 and 2009–2010.

### Dollar (DXY)
- **What:** The dollar vs a basket of major currencies. A strong dollar
  tightens global financial conditions (emerging markets borrow in
  dollars) and hurts US multinationals' earnings.
- **How:** Yahoo DX-Y.NYB.
- **Normal / high / low:** 90–100 is the modern normal band; >110 is
  wrecking-ball strong; <80 is weak.
- **History:** ~120 in 2002, ~70 in 2008 (then spiked as the world
  scrambled for dollars — the dollar *rallies* in panics); ~114 in Sep
  2022 (20-year high — crushed the pound, yen, and emerging markets);
  ~95–100 in 2024–2026.

### Gold
- **What:** The 5,000-year-old fear asset: no yield, no earnings — pure
  monetary distrust insurance. Rises on real-rate collapse, central-bank
  buying, and geopolitical fear.
- **How:** Yahoo GC=F, $/oz.
- **Normal / high / low:** No fundamental anchor — read it as sentiment:
  breaking to highs = the world is buying insurance.
- **History:** ~$280 in 2000 → ~$1,900 in 2011 (GFC aftermath + QE
  distrust); ~$1,050 in 2015; ~$2,070 in 2020; then the 2024–2026
  moonshot past $3,500 on central-bank buying (de-dollarization) and
  negative real-rate memories — gold at records *alongside* stocks at
  records is the market saying "we like risk, but we don't trust
  money."

### Copper ("Dr. Copper")
- **What:** The PhD in economics — copper goes into everything built, so
  its price is a real-time read on global industrial demand, especially
  China.
- **How:** Yahoo HG=F, $/lb.
- **Normal / high / low:** ~$3–4/lb has been the recent normal; >$4.50
  = strong demand (or supply panic); <$2.50 = global slowdown.
- **History:** $1.25 → $4.50 → $1.40 around 2008 (the perfect cycle
  trace); crashed then ripped to $4.70+ in 2021 (green-energy demand
  narrative); ~$4.50–5 in 2025–26 on electrification/AI-datacenter
  demand — notably strong *despite* a wobbly China, which bulls read
  as structural deficit and bears read as speculation.

### WTI crude
- **What:** The price of energy — an input to everything and, via gas
  prices, the inflation number voters actually feel.
- **How:** Yahoo CL=F, $/barrel.
- **Normal / high / low:** $60–80 has been the recent normal; >$100 =
  inflation shock / geopolitical premium; <$40 = demand collapse.
- **History:** $147 in Jul 2008 → $32 by December (demand vaporized);
  **−$37 in Apr 2020** (futures went *negative* — sellers paid buyers
  to take oil with storage full); $120+ after Russia invaded Ukraine in
  2022; ~$60–70 in 2024–2026 — the dog that didn't bark: wars and
  tariffs, yet oil stayed tame, a big reason inflation normalized.

### Bitcoin
- **What:** Digital scarcity — "gold with a network." Trades as
  high-beta tech sentiment: liquidity up = Bitcoin up, violently.
- **How:** Yahoo BTC-USD.
- **Normal / high / low:** No valuation anchor — 4-year halving cycles
  and drawdowns of −80% are the historical rhythm. Position-size it
  like the volatility it is.
- **History:** $20k (2017) → $3k (2018); $69k (2021) → $15.5k (2022,
  FTX); $100k+ in Dec 2024 (ETF launches + pro-crypto US policy);
  ~$110–125k in 2025–26. Every cycle: ~−80% drawdown, then a new high
  — so far. Note the maturation: 2024–2026 drawdowns have been
  shallower (~−25–30%), behaving more like a high-beta tech stock
  than the wild asset of 2017.

---

## How to read the dashboard as a whole

1. **Start with the strip.** If 4+ pills are red, respect risk; if most
   are green/calm while valuation is Extreme, the market is priced for
   perfection — returns from here are historically poor even without a
   crash.
2. **Valuation tells you the next 10 years; the economy tells you the
   next 10 months; markets tell you the next 10 minutes.** Don't use one
   for another's job.
3. **Watch the internals, not just the index:** credit spreads and the
   curve (regime strip) deteriorated *before* stocks in 2000, 2008, and
   2020. When HY spreads blow out while the S&P is flat, believe the
   bonds.
4. **Every metric lies sometimes:** P/E spiked in 2020 on collapsed
   earnings (stocks were actually cheap-ish); the Sahm rule fired in
   2024 with no recession; the curve inverted for two years with no
   recession (yet). Use clusters of signals, never one.
5. **The four episodes rhyme:** 2000 = valuation bust (CAPE 44, Buffett
   183%, div yield 1.1% — then a slow 3-year bleed). 2008 = credit bust
   (spreads 22%, VIX 89, claims 665k — fast, then a V). 2020 = exogenous
   shock (everything to extremes in weeks, then the fastest recovery
   ever on stimulus). 2022 = valuation + inflation bust (stocks *and*
   bonds fell together — the 60/40 portfolio's worst year ever).
   Today's dashboard — extreme valuation, calm credit, normalizing
   labor, sticky-ish inflation — looks most like **late 2021 wearing a
   1999 valuation mask**. Which is not a forecast; it's just what the
   instruments say.
