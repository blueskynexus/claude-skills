# Datasets

Three viaNexus datasets power the live sections of this dashboard. All use
the same base URL and authentication.

## Base URL

```
https://api.blueskyapi.com/v1/data
```

Authentication: `?token=pk_...` query parameter or `x-api-key: pk_...` header.
CORS is `*`, so browser fetch works from `file://` and any origin.

---

## EDGE / HISTORICAL_PRICES

Daily OHLCV, split-adjusted. Global coverage since 2005.

```
GET /v1/data/EDGE/HISTORICAL_PRICES/{symbol}?token={tk}&last=250
```

Key fields: `date`, `open`, `high`, `low`, `close`, `volume`, `fclose`
(split-adjusted close).

For the election dashboard, pull SPY with `last=250` for roughly one trading
year, or use `from=` and `to=` for a specific date range:

```
GET /v1/data/EDGE/HISTORICAL_PRICES/SPY?token={tk}&from=2026-01-02&to=2026-11-04
```

Docs: [console.blueskyapi.com/docs/all/historical-prices/HISTORICAL_PRICES](https://console.blueskyapi.com/docs/all/historical-prices/HISTORICAL_PRICES)

---

## CORE / STOCK_STATS_US

Daily precomputed technical indicators. One row per symbol per day.

```
GET /v1/data/CORE/STOCK_STATS_US/{symbol}?token={tk}&last=1
```

Key fields for the dashboard stats grid:
- `rsi14` — RSI-14 (0-100 oscillator)
- `beta` — trailing beta vs market
- `day50MovingAverage`, `day200MovingAverage`
- `week52High`, `week52Low`, `week52HighDate`, `week52LowDate`
- `trailingPE`, `ttmEPS`
- `ytdChangePercent` — decimal (0.10 = 10%)
- `avg30Volume`
- `sharesOutstanding`

Docs: [console.blueskyapi.com/docs/all/fundamentals/STOCK_STATS_US](https://console.blueskyapi.com/docs/all/fundamentals/STOCK_STATS_US)

---

## EDGE / MT_NEWSWIRES_North_America

Real-time U.S. and Canadian market news from MT Newswires.

```
GET /v1/data/EDGE/MT_NEWSWIRES_North_America/{symbol}?token={tk}&last=10
```

Key fields:
- `headline` — the headline text
- `datetime` — publication timestamp
- `qmUrl` — direct link to the story (use this, not `url`)
- `isPrimary` — boolean, true if the symbol is the main subject
- `storyType` — e.g. "Breaking", "Update", "Analysis"

Filter to `isPrimary=true` for the news panel to avoid tangential mentions.

Docs: [console.blueskyapi.com/docs/all/news/MT_NEWSWIRES_North_America](https://console.blueskyapi.com/docs/all/news/MT_NEWSWIRES_North_America)
