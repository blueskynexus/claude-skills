---
name: financial-research
description: >
  Analyzes a public company's fundamentals, earnings, and peer positioning using
  viaNexus financial data. Use this skill whenever the user asks about a company's
  financials, valuation, earnings history, estimates, or wants a peer comparison —
  for example "how's Apple's balance sheet", "compare NVDA and AMD fundamentals",
  "what's Microsoft's P/E", "next earnings date for Tesla", "is Meta overvalued",
  "show me Amazon's revenue trend", or "pull fundamentals on XOM, CVX, COP". Also
  trigger on generic phrases like "give me a research report on [ticker]" or
  "run the financials on [company]".
compatibility:
  tools:
    - viaNexus:fetch
    - viaNexus:current_date
---

# Financial Research

Produces a concise equity research briefing: headline valuation, recent fundamentals,
forward estimates, peer context, and upcoming catalysts. Powered by viaNexus.

---

## Step 1 — Resolve Tickers

From the user's message, identify one primary ticker (the company being researched)
and optionally a peer set. If the user names a company, map to its symbol (e.g.
"Apple" → AAPL, "NVIDIA" → NVDA). If the user asks for a peer comparison without
specifying peers, pick 3–5 obvious industry peers (e.g. AAPL peers: MSFT, GOOGL, META).

## Step 2 — Get Today's Date

Call `viaNexus:current_date` so "recent" and "upcoming" are anchored correctly.

## Step 3 — Pull Fundamentals

For the primary ticker AND each peer, call `viaNexus:fetch`:

- `dataset_name`: `summary_normalized_financials`
- `product`: `core`
- `endpoint`: `data`
- `symbols`: comma-separated tickers
- `last`: `4` (gets last few fiscal periods so you can see trend)

Key fields returned per period: `revenue`, `ebit`, `ebitda`, `incomeNet`, `basicEPS`,
`PERatio`, `enterpriseValueToEBITDA`, `marketCap`, `pricePerRevenue`, `fiscalQuarter`,
`fiscalYear`, `reportType` (quarterly / ttm / annual), `periodEndDate`.

Use `reportType: ttm` rows for the headline valuation snapshot and the `quarterly`
rows to show YoY revenue/EPS growth.

## Step 4 — Pull Forward Estimates

For the primary ticker, call `viaNexus:fetch`:

- `dataset_name`: `truebeats_eps_revenue_forecasts`
- `product`: `edge`
- `endpoint`: `data`
- `symbols`: primary ticker
- `last`: `4`

Key fields: `fiscalPeriod`, `truebeatEps` (ExtractAlpha EPS surprise score,
positive = beat expected), `truebeatSales`, `numberOfAnalystsEps`.

## Step 5 — Pull Upcoming Earnings Date

Call `viaNexus:fetch`:

- `dataset_name`: `earnings_calendar`
- `product`: `core`
- `endpoint`: `data`
- `symbols`: primary ticker
- `last`: `1`

## Step 6 — (Optional) Pull Company Description

If the user hasn't indicated they already know the business, call:

- `dataset_name`: `company_descriptions`
- `product`: `core`
- `endpoint`: `data`
- `symbols`: primary ticker

## Step 7 — Synthesize

Structure the output:

```
## [Company] ([TICKER]) — Research Briefing — [Today]

### 📌 Snapshot
- Market cap: $X.XB | P/E (TTM): XX.X | EV/EBITDA: XX.X | Price / Revenue: X.X
- TTM revenue: $X.XB | TTM net income: $X.XB | TTM EPS: $X.XX

### 📈 Fundamentals Trend
| Period | Revenue | Net Income | EPS | P/E |
|--------|---------|-----------|-----|-----|
| FY26 Q1 | ... | ... | ... | ... |

Highlight YoY growth or decline in 1–2 sentences.

### 🔮 Forward Estimates (ExtractAlpha TrueBeats)
- Next FY EPS beat score: +X.X% (N analysts)
- Next FY revenue beat score: +X.X%
Briefly interpret: positive score = consensus likely to be beaten.

### 🏁 Peers
| Ticker | Market Cap | P/E TTM | EV/EBITDA | Rev Growth YoY |
|--------|-----------|---------|-----------|----------------|
| AAPL   | $X.XT     | XX.X    | XX.X      | +X.X%          |
| ...    |           |         |           |                |

One-line takeaway on where the primary ticker sits vs peers.

### 🗓️ Next Catalyst
Earnings expected: YYYY-MM-DD (confidence: high/medium/low).
```

**Rules:**
- Never fabricate numbers — only report what the API returned.
- If a dataset returns empty, say so explicitly and skip that section.
- Keep the report scannable — use tables for peer and trend data.
- Round large numbers sensibly: $3,995,778,162,360 → $4.0T.
- Don't give investment advice. State facts; let the user decide.

---

## Example Triggers

- "Research report on AAPL"
- "Compare NVDA and AMD fundamentals"
- "What's Microsoft's P/E and EV/EBITDA?"
- "Is Tesla expensive vs its peers?"
- "When does Apple report next?"
- "Pull financials on XOM, CVX, COP"
