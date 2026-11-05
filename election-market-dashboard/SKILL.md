---
name: election-market-dashboard
description: >
  Builds a single-file HTML election market analysis dashboard from viaNexus data,
  showing how equity markets perform around U.S. elections. Embeds live SPY/index
  data, historical post-election return patterns, government composition effects,
  technical stats, and a news feed. Use whenever someone wants an election market
  view, midterm analysis, post-election performance tracker, political market
  impact dashboard, or a "what happens to stocks after elections" visualization.
compatibility:
  tools:
    - viaNexus:fetch
    - viaNexus:search
    - viaNexus:current_date
---

# Election Market Dashboard

Generate a **single HTML file** the user opens in any browser: a comprehensive
election-market analysis page that combines live viaNexus data with historical
post-election performance patterns.

Division of labor:

- **You (Claude) use the MCP at build time**: pull the current SPY price
  history, technical stats, and news snapshot. Embed these alongside the
  historical election data (which is static reference data you carry in this
  skill).
- **The generated page uses the REST API at run time**: optionally polls
  viaNexus for live quote updates. The historical election data is always
  embedded (it does not change).

Read [references/datasets.md](references/datasets.md) for the datasets and
their URL shapes. Read [references/historical-data.md](references/historical-data.md)
for the pre-compiled election return data you embed directly.

---

## Step 1 — Determine scope

Ask for (or extract from the conversation):

- **Which election cycle?** Default to the most recent or upcoming. The
  historical data covers every midterm and presidential election since 1950.
- **Which index?** Default to SPY (S&P 500 ETF). The user may want QQQ, DIA,
  IWM, or a custom watchlist.
- **Live or snapshot?** Live pages poll for updated quotes; snapshots embed
  everything and make zero network requests after load. Default to live.

## Step 2 — Pull current market data

Three calls, all symbols comma-separated where applicable:

1. **Price history** (YTD or trailing 12 months):
   ```
   viaNexus:fetch dataset="historical_prices" product="EDGE" key="SPY"
   ```
   Use `last=250` for roughly one year of trading days.

2. **Technical stats** (RSI, moving averages, beta, P/E):
   ```
   viaNexus:fetch dataset="stock_stats_us" product="CORE" key="SPY"
   ```

3. **Recent news** (election and market headlines):
   ```
   viaNexus:fetch dataset="mt_newswires_north_america" product="EDGE" key="SPY" last=10
   ```

Verify every symbol resolves. Missing symbols get flagged, not dropped.

## Step 3 — Build the page

One HTML file, **zero external dependencies** except Chart.js 4.4.1 from
cdnjs (needed for the charts; inline it if the user wants fully offline).
Required sections in this order:

### 3a. Hero metrics (4 cards)

Four stat cards across the top:

| Card | Source |
|------|--------|
| **S&P 500 YTD** | Computed from HISTORICAL_PRICES (first vs last close) |
| **Post-Election Avg** | From historical data: +16.9% (midterm) or +9.1% (presidential) |
| **Current RSI-14** | From STOCK_STATS_US |
| **Historical Win Rate** | 19/19 midterms positive since 1950 (or equivalent for presidential) |

Each card: large number, label, small delta or context line. Color-code the
YTD change (green positive, red negative).

### 3b. Price chart

Full-width line chart of the index YTD (or trailing 12 months), built from
HISTORICAL_PRICES data. Mark the election date with a vertical dashed line
and annotation. If a pre-election pullback is visible, annotate that too.

Use Chart.js with these settings:
- Responsive, 16:9 aspect ratio
- Grid lines subtle (opacity 0.1)
- Tooltip showing date and price
- Fill under the line with gradient opacity

### 3c. Historical post-election returns

Bar chart showing 12-month S&P 500 returns after each election in the
relevant cycle (midterm or presidential) since 1950. Data is in
[references/historical-data.md](references/historical-data.md).

Color-code bars by magnitude:
- Above 20%: dark blue
- 10-20%: medium blue
- Under 10%: light blue
- Negative: red

Draw a dashed average line across the chart.

### 3d. Return buildup chart

Grouped bar chart showing how returns accumulate after elections:

| Period | Midterm avg | Presidential avg |
|--------|-------------|------------------|
| 1 month | +1.7% | +0.8% |
| 3 months | +5.7% | +3.2% |
| 6 months | +12.4% | +6.1% |
| 12 months | +16.9% | +9.1% |

Source these from [references/historical-data.md](references/historical-data.md).

### 3e. Government composition panel

Two-column layout:
- **Left**: horizontal bar chart comparing divided vs unified government
  12-month returns (+15.0% vs +11.5%)
- **Right**: text summary of Janus Henderson's finding (8.73% vs 9.24%
  annualized, divided vs unified)

### 3f. Technical stats grid

A 2x4 or 4x2 grid of the key statistics from STOCK_STATS_US:
- RSI-14
- Beta
- 50-day MA
- 200-day MA
- 52-week high/low
- Trailing P/E
- YTD change
- Avg 30-day volume

### 3g. News feed

Recent market headlines from MT_NEWSWIRES, rendered as a compact list with
timestamp and headline. Link to `qmUrl` (direct source), not `url`.

### 3h. Source citations

**Every historical claim must be cited.** Include a sources section at the
bottom with these references:

- CNBC: S&P 500 performance after midterm elections history
- yCarts: Historical midterm election market response analysis
- Capital Group: Midterm elections and markets (5 charts)
- Janus Henderson: Government composition and market returns
- Edward Jones / CBS News: Post-election return windows
- Schwab: Post-midterm return analysis
- viaNexus: All current market data (HISTORICAL_PRICES, STOCK_STATS_US,
  MT_NEWSWIRES_North_America)

### 3i. Footer

- Data provenance: "Current data from viaNexus. Historical election returns
  compiled from CNBC, yCarts, Capital Group, and Janus Henderson research."
- Disclaimer: "Past performance does not guarantee future results. This is
  not investment advice."
- viaNexus CTA: link to free trial and data catalog

## Step 4 — Styling

Dark theme by default with light mode support. The election dashboard has a
financial terminal aesthetic:

- Background: `#0a0f1a` (dark) / `#f5f7fa` (light)
- Cards: `#111827` with subtle border / `#ffffff`
- Accent blue: `#3b82f6`
- Positive green: `#10b981`
- Negative red: `#ef4444`
- Text: `#e5e7eb` / `#1f2937`

Define as CSS custom properties. Support both `prefers-color-scheme` and a
manual toggle button in the header.

The header includes the viaNexus logo/name and a "Powered by viaNexus" badge.

## Step 5 — Token handling

Same pattern as `live-market-dashboard`: token input in the header, persisted
to `localStorage`. The historical data sections work without a token (they
are embedded). The live price, stats, and news sections need a token to
refresh.

No token on first load? The page renders everything from the embedded
snapshot. The token input says "Add your viaNexus API key for live updates"
with a link to the free trial signup.

## Step 6 — Data integrity rules

- `changePercent` is a decimal. Multiply by 100 for display.
- Render API values verbatim. No "corrected" prices.
- Historical election data is static and cited. Do not present it as
  viaNexus data — it comes from the research sources listed.
- Current market data IS viaNexus data. Label it as such.
- No buy/sell recommendations. No "the market will rally."
- The 19-for-19 streak is historical fact, not a prediction.

## Step 7 — Verify, then launch

Open the file in the browser pane or desktop shell. Confirm:

- All four hero cards render with real numbers
- The price chart shows the full date range
- Historical bars match the data in references/historical-data.md
- News headlines are present (or gracefully absent if no token)
- Both themes work
- No horizontal scroll at 1200px
- Citations section is present and complete
- No token leaked in the file (grep for pk_/sk_)

For a screenshot, 1440x900 in dark mode captures the full above-the-fold
dashboard in one image.

---

## Example triggers

- "Build me an election market dashboard"
- "Show me how stocks perform after midterm elections"
- "I want a dashboard tracking the post-election rally"
- "What happens to the S&P 500 after elections? Build me something I can see"
- "Make a midterm election market analysis page"
- "Political market impact dashboard"
