---
name: rsi-screener
description: >
  Builds a single-file HTML momentum board that ranks a watchlist by RSI-14 and
  shows where every name sits on the oscillator, powered by viaNexus
  CORE/STOCK_STATS_US. One batched API call at build time, no polling, no
  backend, no client-side math. Use whenever the user wants an RSI screen,
  momentum screener, overbought/oversold view, relative strength ranking, or a
  "which of my stocks are stretched" answer — even if they don't say RSI (e.g.
  "which names are oversold", "screen my watchlist for momentum", "what's
  overbought right now", "rank these by relative strength").
compatibility:
  tools:
    - viaNexus:fetch
    - viaNexus:search
    - viaNexus:current_date
---

# RSI Screener

Generate a **single HTML file** the user opens in any browser: a momentum board
that ranks a watchlist by RSI-14 and plots the whole universe on one 0–100
oscillator axis.

This skill differs from `live-market-dashboard` in one important way: the page
is a **snapshot, not a poller**. You make one API call at build time and embed
the result. The finished page makes zero network requests, contains no token,
and can therefore be shipped as a hosted artifact, emailed, or committed — none
of which are safe for a polling dashboard.

The other core idea: **RSI-14 is a stored field, not something the page
computes.** `rsi14` ships on the same `STOCK_STATS_US` record as the 50-day and
200-day moving averages. Never pull price history and never implement Wilder's
smoothing in the generated page. If you find yourself writing an RSI function,
you have taken the wrong path.

Read [references/dataset.md](references/dataset.md) before writing any fetch
code. The finished reference implementation is
[assets/example-screener.html](assets/example-screener.html) — this is the
layout to reproduce, not merely a source of ideas.

---

## Step 1 — Get the watchlist

Ask for (or extract from the conversation) the tickers. If the user has no list
and just wants to see the thing work, use the default universe in
[references/dataset.md](references/dataset.md) (60 US large caps) and say that
is what you used.

Only exchange-listed US equities and ETFs are in this dataset. Mutual funds
(5-letter tickers ending in X, e.g. FZROX) return nothing — name them to the
user and offer ETF analogs rather than dropping them silently.

## Step 2 — One call, then verify

A single request with **all** symbols comma-separated and `filter=` applied:

```
GET /v1/data/CORE/STOCK_STATS_US/{sym1,sym2,...}?token={pk_}&filter=symbol,issuerName,date,rsi14,day50MovingAverage,day200MovingAverage
```

Do not loop per symbol. Sixty symbols in one request is ~28 KB and about a
second; that measurement is the story the page tells, so keep it true.

Then check three things before you build:

- **Missing symbols.** Any ticker absent from the response did not resolve.
  Report those to the user by name.
- **Null `rsi14`.** Legitimate for names with fewer than 15 trading days of
  history. Keep the row, render it as "insufficient history", and never
  substitute a number.
- **One `date` value.** All rows should carry the same `date`. If they don't,
  say so in the page footer rather than implying a single as-of moment.

Record the payload size and elapsed time of that one call. They go in the
masthead.

## Step 3 — Build the page

One HTML file, no external dependencies. Inline all CSS and JS, no CDN scripts,
no webfonts, no frameworks. Sections in this order, because the board is
scanned, not read:

1. **Masthead** — dataset identity (`viaNexus · CORE / STOCK_STATS_US`), the
   headline, and a right-aligned provenance block: as-of date, symbol count,
   payload size, elapsed time.
2. **Four tiles** — universe size, oversold count, neutral count, overbought
   count. Each tile is a button that filters the rest of the page.
3. **The oscillator** — the hero. All symbols as dots on one 0–100 axis (see
   Step 4). This is the view that makes the point in a screenshot.
4. **The table** — every symbol, sorted weakest to strongest by default, with
   an inline RSI bar, both moving averages, and a trend chip. Sortable columns.
   This doubles as the accessible view of the chart.
5. **Provenance** — the exact curl that produced the page, and one unedited
   record. Users trust a screen they can reproduce.
6. **Footer** — how RSI is calculated, what nulls mean, and the not-advice line.

## Step 4 — The oscillator, exactly

The hero is a **dot plot stacked upward from the baseline**, not a bar chart and
not a gauge. Position on the x-axis carries the RSI value; the stack height
where dots collide reveals the distribution for free.

Bands are fixed at the conventional thresholds. Do not invent your own:

| Band | Range | Meaning |
|---|---|---|
| Oversold | RSI < 30 | selling pressure exhausted |
| Neutral | 30 – 70 | no momentum signal |
| Overbought | RSI > 70 | extended after a run |

Shade 0–30 and 70–100, draw hairline rules at 30, 50 and 70, and label the 30
and 70 rules in the plot.

Layout algorithm — lanes, so dots never overlap:

```js
const dot = 11, gapY = 2, minGapX = dot + 2;
const sorted = [...DATA].sort((a, b) => a.rsi14 - b.rsi14);
const lanes = [];                    // lanes[i] = rightmost x used in that lane
sorted.forEach(d => {
  const x = (d.rsi14 / 100) * plotWidth;
  let lane = 0;
  while (lanes[lane] != null && x - lanes[lane] < minGapX) lane++;
  lanes[lane] = x;
  d._x = x; d._lane = lane;          // bottom = 4 + lane * (dot + gapY)
});
```

Direct-label only the two extremes (lowest and highest RSI) with value and
ticker. Everything else gets a hover tooltip carrying symbol, company, RSI, and
both moving averages. Never print a number on every dot.

## Step 5 — Color, fixed

These hexes are validated (lightness band, chroma floor, colorblind separation,
normal-vision separation, and contrast against their own surface, in both
modes). **Use them as given.** If the user asks for their own brand colors,
re-validate rather than swapping by eye.

| Role | Light | Dark |
|---|---|---|
| Oversold pole | `#0d7fc4` | `#2b96d6` |
| Overbought pole | `#a35f00` | `#c07d18` |
| Neutral midpoint | `#6f7885` | `#7d8794` |
| Page / surface | `#eceff3` / `#f7f9fb` | `#080d10` / `#0c1317` |
| Primary / secondary ink | `#0e1620` / `#4b5a6c` | `#f2f6f8` / `#a8b4c0` |
| Chrome accent (never on a data mark) | `#0b7f70` | `#12b39c` |

The scale is diverging: a cool pole, a warm pole, and a neutral gray at the
middle. Rules that follow from that:

- **Never red/green.** It reads as good/bad, and oversold is not "bad".
- **The two pole hues encode the RSI band and nothing else.** Trend chips,
  status, and links use ink and glyphs (▲ / ▼), never the pole colors, or blue
  starts meaning two different things on one page.
- **Color never carries meaning alone.** Every dot's value is also its x
  position; every row prints its number; every band is named in the legend.
- Define these as CSS custom properties and redefine them under both
  `@media (prefers-color-scheme: dark)` and `:root[data-theme="dark"]` so a
  viewer's explicit toggle wins over the OS setting.

## Step 6 — Integrity rules

- **Render API values verbatim.** No rounding beyond display, no interpolation,
  no filling a null.
- **RSI is one reading on one day.** The page states this. It never says buy,
  sell, cheap, expensive, or "due for a bounce".
- **No signals.** Crossing 30 is not a recommendation, and neither is a golden
  cross. Report the level and the trend relationship; stop there.
- **Same-record claim must stay true.** The page's whole argument is that
  momentum and trend arrive together. If you end up making a second call for
  anything on the board, either drop that element or correct the masthead.
- **No token in the file.** The page makes no requests, so it needs none. Grep
  the output for `pk_` and `sk_` before delivering.

## Step 7 — Verify, then launch it

Do not end by handing over a file path. Open it:

1. **Browser pane / preview tool** (Claude Code desktop, Cowork). Note that
   preview panes may render files outside the project folder as static
   snapshots with scripts disabled — if the tiles and dots come up empty, that
   is why; write the file inside the project folder and reopen.
2. **Desktop shell**: `open` (macOS), `xdg-open` (Linux), `start` (Windows).
3. **No visible browser**: present the file for download, and say which rung
   you used.

Then confirm, in the rendered page:

- tile counts sum to the symbol count;
- the dot count equals the number of symbols with a non-null `rsi14`;
- the lowest and highest RSI names are the ones direct-labeled;
- both themes render (toggle the OS/preview color scheme, don't assume);
- no horizontal scroll on the page body at 1200px wide.

For a LinkedIn or deck screenshot, a 1200×660 viewport in dark mode crops the
masthead, tiles, and oscillator into one image.

Unlike `live-market-dashboard`, this page is safe to deliver as a hosted
artifact — it is a static snapshot with no outbound calls and no credential.

---

## Example triggers

- "Which of my holdings are overbought? AAPL MSFT NVDA TSLA"
- "Build me an RSI screen for the S&P mega caps"
- "Show me what's oversold right now"
- "Rank these tickers by relative strength"
- "Momentum board for my watchlist"
