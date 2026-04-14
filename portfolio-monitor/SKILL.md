---
name: portfolio-monitor
description: >
  Monitors a user-supplied portfolio of holdings: pulls live quotes, flags
  price/volume alerts, surfaces the day's news impact per position, and produces
  a daily brief combining market data with news. Use whenever the user asks about
  their holdings, a watchlist, portfolio performance, or a daily market brief for
  specific tickers — e.g. "check my portfolio", "morning brief on AAPL MSFT NVDA",
  "anything moving on my positions today", "alert me if TSLA drops below 240",
  "end-of-day summary for this watchlist", or "which of my holdings had news
  today". User provides holdings; this skill does NOT persist them.
compatibility:
  tools:
    - viaNexus:fetch
    - viaNexus:current_date
---

# Portfolio Monitor

Combines viaNexus quotes, corporate actions, and MT Newswires news into a single
portfolio briefing. The user always supplies the holdings (tickers + optional
share counts + optional price alerts); this skill does not store state.

---

## Step 1 — Parse Holdings

Extract from the user's message:
- **Tickers** — required
- **Share counts** — optional, for dollar-weighted PnL
- **Alert thresholds** — optional, per-ticker price or % move triggers

If no shares given, show per-share change only.
If no alerts given, flag any ticker with > ±3% day move as "notable".

## Step 2 — Get Today's Date

Call `viaNexus:current_date`.

## Step 3 — Fetch Quotes

Call `viaNexus:fetch`:

- `dataset_name`: `quote`
- `product`: `core`
- `endpoint`: `data`
- `symbols`: comma-separated tickers

Key fields: `symbol`, `latestPrice`, `change`, `changePercent`, `previousClose`,
`latestVolume`, `avgTotalVolume`, `week52High`, `week52Low`, `peRatio`, `marketCap`,
`isUSMarketOpen`.

## Step 4 — Compute Positions

For each holding:
- `day_change = latestPrice - previousClose`
- `day_change_pct = changePercent` (already decimal)
- `volume_spike = latestVolume / avgTotalVolume` — flag if > 2x
- If shares provided: `position_value = latestPrice × shares`,
  `position_pnl_today = day_change × shares`

Aggregate portfolio total value and day PnL if shares provided.

## Step 5 — Check Alerts

For each user-supplied alert:
- Price alert: fire if `latestPrice` crosses threshold
- % move alert: fire if `abs(changePercent) >= threshold`
- Default: flag any ticker moving > ±3% or with volume_spike > 2x

## Step 6 — Pull News for Movers

For any ticker flagged in Step 5 (or the top 3 movers if no alerts),
call `viaNexus:fetch`:

- `dataset_name`: `mt_newswires_north_america`
- `product`: `edge`
- `endpoint`: `data`
- `symbols`: mover tickers (comma-separated)
- `last`: `5`
- `on_date`: today's date from Step 2

Deduplicate by `subkey`, prioritize `isPrimary: true`.

## Step 7 — Check Corporate Actions (Optional)

If any ticker has dividend or split activity that could explain a move,
call `viaNexus:fetch` with `advanced_dividends` or `advanced_splits`
(product `edge`).

## Step 8 — Synthesize

Output format:

```
## Portfolio Brief — [Today]
Market status: [OPEN | CLOSED]

### 💼 Holdings
| Ticker | Last | Day % | Day $ | Volume vs Avg | Position Value |
|--------|------|-------|-------|---------------|----------------|
| AAPL   | 259.10 | -0.04% | -0.10 | 0.6x | $25,910 (100 sh) |
| ...    |        |        |       |      |                  |

**Portfolio total:** $X,XXX,XXX | **Day PnL:** $X,XXX (+X.X%)

### 🚨 Alerts Fired
- **[TICKER]** crossed $XXX threshold (currently $YYY)
- **[TICKER]** volume 3.2x avg — unusual activity

### 📰 News on Movers
- **[TICKER]** (+4.2%): "[Headline]" — [1-line summary, MT Newswires, HH:MM]
- **[TICKER]** (-2.8%): "[Headline]" — [...]

### 🗓️ Upcoming Catalysts
Any earnings / dividend / split dates in the next 7 days for holdings.
```

**Rules:**
- Never invent prices or PnL — only report what the API returns.
- If `isUSMarketOpen: false`, label the brief as an after-hours / pre-market view.
- Flag when quotes are 15-min delayed (`calculationPrice: "delayed"`) so the user
  knows this isn't real-time.
- Round prices to 2 decimals, percentages to 2 decimals, position values to the
  dollar.
- Do not give buy/sell recommendations.

---

## Example Triggers

- "Check my portfolio: AAPL MSFT NVDA GOOGL"
- "Morning brief on XOM CVX COP"
- "Anything moving on my watchlist today?"
- "Alert me if TSLA drops below 240"
- "End-of-day summary for AAPL 100 shares MSFT 50 shares"
- "Which of my holdings had news today?"
