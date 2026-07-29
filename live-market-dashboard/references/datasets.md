# Dataset reference — live-market-dashboard

Three datasets cover the whole dashboard. All are reachable two ways:

- **MCP (build time)**: `viaNexus:fetch` with `dataset_name`, `product`, `symbols`, `last`, `filter`
- **REST (run time, from the generated page)**:
  `https://api.blueskyapi.com/v1/data/{PRODUCT}/{DATASET}/{symbols}?token={pk_token}&...`
  (dataset name uppercase in the path; CORS is open — `Access-Control-Allow-Origin: *`)

`filter=` is **field selection**, not content filtering: a comma-delimited,
case-sensitive list of field names to keep. Always use it — it cuts payloads by
~10x. Misspelled field names silently match nothing and return `{}` objects.

---

## 1. quote — live prices (CORE)

The page's polling target. Batch **all** symbols into one request:

```
GET /v1/data/CORE/QUOTE/AAPL,MSFT,SPY?token=pk_...&filter=symbol,companyName,latestPrice,change,changePercent,latestVolume,avgTotalVolume,week52High,week52Low,latestSource,latestUpdate,marketCap,peRatio,isUSMarketOpen
```

Returns one object per resolved symbol. Symbols that don't resolve are simply
absent — compare response symbols against the request list to detect them.

| Field | Notes |
|---|---|
| `latestPrice` | The price to display. Best available source. |
| `change`, `changePercent` | vs `previousClose`. **`changePercent` is a decimal** — 0.0094 means +0.94%. |
| `latestSource` | Observed values: `"synthetic real-time price"`, `"15 minute delayed price"`, `"Close"`, `"Prior close"`, `"official"`, `"Unofficial"` (VNX price from extended hours — no disclaimer needed). Only "delayed" ⇒ mandatory disclaimer. |
| `latestUpdate` | ms epoch; can be `0` when source is a prior close — don't render `1970` timestamps. |
| `latestVolume`, `avgTotalVolume` | Ratio flags unusual activity, but only meaningful mid-session (`isUSMarketOpen: true`); `latestVolume` can be a tiny float off-hours. |
| `week52High`, `week52Low` | Draw the range bar clamped: `latestPrice` can legitimately sit outside the bracket (fresh 52-week high/low) and occasionally the bracket itself is bad — tag "range suspect" only beyond ~10% tolerance. Real example: SPY has been observed with `week52Low: 69.01` against a ~740 price. |
| `isUSMarketOpen` | Gate for volume ratio + "market open/closed" header chip. |

Mutual funds (FZROX-style tickers) are not in this dataset. ETFs are.

## 2. historical_prices — daily bars (EDGE)

For sparklines / session traces. Fetch lazily per selected symbol:

```
GET /v1/data/EDGE/HISTORICAL_PRICES/AAPL?token=pk_...&last=40&filter=priceDate,fclose,fvolume
```

Rows come **newest first** — reverse before plotting. Use the fully-adjusted
`f*` fields (`fclose`, `fopen`, `fhigh`, `flow`, `fvolume`) so splits and
dividends don't produce fake cliffs. `priceDate` is `YYYY-MM-DD`.

## 3. news — headlines (CORE)

Per-symbol headlines, lazy-fetched on selection:

```
GET /v1/data/CORE/NEWS/AAPL?token=pk_...&last=10&filter=headline,datetime,provider,qmUrl,uuid,summary
```

| Field | Notes |
|---|---|
| `uuid` | Dedupe key — multi-symbol stories repeat. |
| `datetime` | ms epoch. |
| `qmUrl` | Direct link to the source article — use this for links. |
| `url` / `image` | viaNexus-proxied, require appending a token — avoid in generated pages. |
| `symbol` | `MARKET` = market-wide news, available as a pseudo-symbol. |

Aggregated multi-provider US feed (CityFalcon and others). Accounts with EDGE
MT Newswires access can substitute `mt_newswires_north_america`
(product EDGE, fields `headline`, `body`, `releaseTime`, `isPrimary`, key/subkey
instead of symbol/uuid) for wire-grade content — check availability with
`viaNexus:search` before wiring it in.

---

## Handy extras (verify with `viaNexus:search` before use)

- `intraday_prices` (CORE) — minute bars for today; richer than a 40-day
  sparkline if the user wants an intraday trace. `last=1&limit=390`-style
  pagination quirks apply; test before committing.
- `earnings_calendar`, `advanced_dividends`, `advanced_splits` (EDGE) —
  upcoming-catalyst rails.
- Full catalog: [console.blueskyapi.com/catalog](https://console.blueskyapi.com/catalog)
