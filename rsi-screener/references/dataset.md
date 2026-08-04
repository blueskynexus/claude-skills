# Dataset reference — rsi-screener

One dataset covers the whole board: **`stock_stats_us`** (product `CORE`).
Reachable two ways:

- **MCP (build time)**: `viaNexus:fetch` with `dataset_name: "stock_stats_us"`,
  `product: "CORE"`, `symbols`, `filter`
- **REST**:
  `https://api.blueskyapi.com/v1/data/CORE/STOCK_STATS_US/{symbols}?token={pk_token}&filter=...`
  (dataset name uppercase in the path; CORS is open —
  `access-control-allow-origin: *`, verified)

`filter=` is **field selection**, not content filtering: a comma-delimited,
case-sensitive list of field names to keep. Always use it. Misspelled names
silently match nothing.

A `pk_` (public) token is sufficient for this dataset. Never put an `sk_` in a
generated page — and for this skill, never put any token in it, since the page
makes no runtime requests.

---

## The call

```
GET /v1/data/CORE/STOCK_STATS_US/aapl,msft,nvda,...?token=pk_...&filter=symbol,issuerName,date,rsi14,day50MovingAverage,day200MovingAverage
```

Symbols are case-insensitive. Dotted tickers work as-is (`brk.b`). Returns one
object per resolved symbol; unresolved symbols are simply absent, so compare
the response against your request list.

Measured on a 60-symbol request: **27.8 KB, ~1.3 s** unfiltered. With `filter=`
applied it is a fraction of that.

## Fields

| Field | Notes |
|---|---|
| `rsi14` | Wilder's RSI over 14 trading days on split-adjusted closes, computed server-side and refreshed each session. **Nullable** — null means fewer than 15 trading days of history, or a perfectly flat series. Never substitute a number. |
| `day50MovingAverage`, `day200MovingAverage` | Same record. Their relationship is the trend chip; `rsi14` is the momentum reading. This is why the board needs only one call. |
| `symbol`, `issuerName` | Ticker and company name. `issuerName` is the display name. |
| `date` | Trading date the stats refer to, `YYYY-MM-DD`. Should be identical across rows in one response. |
| `52weekHigh`, `52weekLow`, `52weekHighDate`, `52weekLowDate` | Range context if you want a range rail. |
| `52weekChange`, `ytdChange` | Decimals, not percents. |
| `beta`, `epsTtm`, `peRatioTtm`, `sharesOutstanding`, `avg30DayVolume`, `mic` | Available on the same record; pull them only if the user asks, and keep the payload honest. |

Stale rows exist for delisted symbols that have left the universe: a very old
`date` on a row is the tell. Check `date` rather than assuming every row is
current.

## Coverage

US exchange-listed equities and ETFs. `SPY`, `QQQ`, and other ETFs return a
populated `rsi14`. Mutual funds are not in this dataset.

## Default universe

When the user has no watchlist, use these 60 US large caps so the distribution
has enough shape to be worth plotting:

```
aapl,msft,nvda,amzn,googl,meta,tsla,avgo,jpm,v,
ma,unh,xom,jnj,wmt,pg,hd,cost,orcl,crm,
amd,nflx,dis,bac,ko,pep,csco,intc,qcom,adbe,
pfe,mrk,cvx,t,vz,nke,sbux,ba,ge,gm,
f,pypl,uber,abnb,coin,pltr,mu,shop,spot,gs,
lly,tsm,now,ibm,cat,de,mcd,lmt,rtx,gme
```

## Related datasets

Verify with `viaNexus:search` before wiring anything in:

- `quote` (CORE) — live price. Only add it if the user asks for price on the
  board, and remember it breaks the one-call claim in the masthead.
- `historical_prices` (EDGE) — daily bars. **Not needed for RSI.** If you are
  reaching for this, re-read the skill.
- Full catalog: [console.blueskyapi.com/catalog](https://console.blueskyapi.com/catalog)
