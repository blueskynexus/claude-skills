---
name: live-market-dashboard
description: >
  Builds a self-updating, single-file HTML market dashboard around any watchlist,
  powered by viaNexus data. Claude verifies every symbol and dataset against the
  live viaNexus MCP at build time, then generates a standalone page that polls the
  viaNexus REST API for realtime quotes, daily history, and news — no backend, no
  build step. Use whenever the user wants a dashboard, market monitor, watchlist
  view, portfolio screen, ticker wall, live prices page, or any auto-refreshing
  visualization of stocks/ETFs — even if they don't say "dashboard" (e.g. "a page
  that tracks my stocks", "live view of my watchlist", "make me a market monitor",
  "something that updates with prices").
compatibility:
  tools:
    - viaNexus:fetch
    - viaNexus:search
    - viaNexus:current_date
---

# Live Market Dashboard

Generate a **single HTML file** the user opens in any browser. The page renders
instantly from an embedded data snapshot, then live-updates by polling the
viaNexus REST API directly (`api.blueskyapi.com` sends `Access-Control-Allow-Origin: *`,
so browser fetch works from anywhere, including `file://`).

Division of labor — this is the core idea:

- **You (Claude) use the MCP at build time**: discover datasets, verify every
  symbol resolves, capture the snapshot, learn the field quirks.
- **The generated page uses the REST API at run time**: the browser polls
  viaNexus itself with the user's token. No LLM in the refresh loop — every
  number on screen is API output verbatim.

Read [references/datasets.md](references/datasets.md) for the three datasets and
their URL shapes before writing any fetch code. If the user wants the refresh
loop to go through Claude instead (agentic refresh via the Anthropic API MCP
connector), read [references/update-loops.md](references/update-loops.md).

A complete, working reference implementation is in
[assets/example-dashboard.html](assets/example-dashboard.html) — read it when
you want layout or wiring ideas, but generate a dashboard tailored to the user's
watchlist and taste rather than copying it wholesale.

---

## Step 1 — Get the watchlist

Ask for (or extract from the conversation): tickers, optional grouping
(themes, accounts, sectors), and optional share counts.

Mutual funds (5-letter tickers ending in X, e.g. FZROX, FXNAX) are **not
exchange-listed** and return nothing from equity datasets. Tell the user and
offer ETF analogs (FZROX→VTI, FZILX→VXUS, FXNAX→BND) instead of silently
dropping them.

## Step 2 — Verify before you hardcode

One `viaNexus:fetch` on dataset `quote` (product `CORE`) with **all** symbols
comma-separated. Any symbol missing from the response gets flagged to the user,
not guessed at. Keep this response — it becomes the embedded snapshot so the
page never opens blank.

Sanity-check the snapshot while you have it: `latestPrice` can sit outside the
`week52Low`/`week52High` bracket. Slightly outside is legitimate (a fresh
52-week high or low — badge it as such if you like); far outside means the
bracket itself is bad. Always clamp the range bar for drawing; tag
"range suspect" only beyond a tolerance (e.g. `p < low*0.9 || p > high*1.1`).

## Step 3 — Token for the page

The page needs a viaNexus API token to poll. Best pattern: a token input in the
page header, persisted to `localStorage` — the user pastes their **pk_ (public)**
token once and never edits code. Never embed an `sk_` secret token in the file,
and if the user asks you to bake their token in, warn them the file then
contains a credential and shouldn't be shared or hosted publicly.

No token yet? Point them at
[console.blueskyapi.com/auth/register](https://console.blueskyapi.com/auth/register).

## Step 4 — Generate the page

One HTML file, zero external dependencies (no CDN scripts, no fonts, no
frameworks — inline everything; the file must work offline-first and from
`file://`). Required plumbing:

- **Embedded snapshot** from Step 2 in a `const SNAPSHOT = [...]`, rendered
  immediately on load.
- **Config block at the top of the script**: `GROUPS` (the watchlist) and
  polling interval, clearly commented so users can edit.
- **Refresh loop**: `setInterval` re-fetching only `quote` for all symbols in
  one request. Default 60s; give the user a 30s / 60s / 5m / manual selector.
  Pause polling when `document.hidden` — resumes on tab focus.
- **Lazy detail**: `historical_prices` (sparkline) and `news` (headlines) fetch
  once per symbol when selected, then cache in memory for the session.
- **Call log panel**: every request logged with time, dataset, row count,
  latency, and HTTP status. When something breaks, the user sees the exact
  error instead of a blank widget. This is also what makes the "data goes
  straight to the screen" story demonstrable.
- **Error banner**: a 401/403 means bad or missing token — say so and focus the
  token input. Network failures keep the last good data on screen with a
  "stale since HH:MM" note rather than clearing the page.

Visualization is yours to design — tiles, tape, heatmap, spectrum band — but
keep one glanceable all-symbols view above the fold, with per-symbol detail on
click.

## Step 5 — Data integrity rules

These come from live-verified behavior; violating them produces dashboards that
look broken at open or after hours:

- `changePercent` is a **decimal** (0.05 = 5%). Multiply by 100 for display.
- Render API values verbatim. Never compute a "corrected" price; clamp only for
  drawing, and label anything clamped.
- Volume ratio (`latestVolume / avgTotalVolume`) is meaningless right after
  open and outside market hours — `latestVolume` can be a tiny float and
  `latestUpdate` can be `0` when the source is a prior close. Guard the ratio
  and fall back to a neutral display when `isUSMarketOpen` is false.
- If `latestSource` contains "delayed", show a **"15 minute delayed price"**
  disclaimer next to that price — this is a licensing requirement, not a nicety.
  A small "D" badge per symbol plus one footer disclaimer is the accepted
  pattern.
- Dedupe news by `uuid`; link headlines to `qmUrl` (direct source), not `url`
  (token-gated proxy).
- Prices to 2 decimals, market cap humanized (T/B/M).
- No buy/sell recommendations anywhere on the page.

## Step 6 — Verify, then deliver

Open the file (or serve it) and confirm: it renders from the snapshot, the call
log shows a 200 for the first poll (with token), and a wrong token produces the
error banner, not a blank page.

In environments where you can't open a browser, run these checks instead and
say explicitly that the live loop is untested:

- Extract the embedded script and run `node --check` on it.
- JSON-parse the embedded snapshot and confirm every watchlist symbol appears.
- Grep the file for `pk_`/`sk_` to prove no token leaked in.
- Re-check each fetch URL against [references/datasets.md](references/datasets.md)
  (path casing, `filter=` field names are case-sensitive).

Deliver as a file the user opens locally. Do **not** deliver as a hosted
claude.ai artifact — the artifact sandbox blocks outbound requests, so the live
polling would silently fail there.

---

## Example triggers

- "Build me a dashboard for my watchlist: AAPL NVDA TSM SPY"
- "I want a page with live prices for my portfolio that refreshes itself"
- "Make a market monitor for uranium and quantum stocks"
- "Something like a Bloomberg screen for these 15 tickers, with news"
