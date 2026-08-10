# CORE/EARNINGS_CALENDAR

```
GET https://api.blueskyapi.com/v1/data/CORE/EARNINGS_CALENDAR/{symbol}?token={token}
```

Returns an array. Fields used by this skill:

| Field | Notes |
| --- | --- |
| `earningsDate` | `YYYY-MM-DD`. This is also the time-series date — see below. |
| `status` | `predicted` or `confirmed`. |
| `marketSession` | `pre`, `post`, or absent. |
| `confidence` | 0 to 1, for predicted records. |
| `predictionSources` | Filing URLs the prediction was derived from. |

Three things will produce a wrong page if you don't know them.

## 1. A bare GET returns the highest-dated point, not the newest-written

`earningsDate` *is* the time-series date, so each distinct date is its own
point. A GET with no parameters returns the single highest-dated one.

For a forward-looking calendar that is the correct and intended behaviour: you
get the next expected report. It has one consequence worth internalising —
**a bare GET is almost always `status: predicted`**, because a forward
prediction outranks the confirmed record sitting behind it. Confirmed records
are still there; they are just older, and therefore lower-dated.

Do not "fix" this by collapsing to one row per symbol. That would destroy the
forward-looking design.

To see history instead, pass `last`:

```
GET /v1/data/CORE/EARNINGS_CALENDAR/AAPL?token=...&last=50
```

`start` and `end` are not accepted and will 400.

## 2. Roughly half of all records have no `marketSession`

The session is derived from the SEC `acceptanceDateTime` of a real filing,
converted to America/New_York: before 09:30 is `pre`, 16:00 or later is `post`.

A *predicted* date has no filing behind it, so it carries a session only if one
was inherited from a prior confirmed report. Across a full S&P 500 build, about
55% of records come back with no session at all.

**Anything that renders a pre/post badge needs an empty state.** Treat "no
session" as the largest category, not an edge case.

Two traps if you ever recompute this yourself:

- `acceptanceDateTime` is **UTC** despite how it is formatted. Handle DST, or
  half the year shifts an hour and every borderline case flips.
- Do not derive it from an events/calendar feed. Those carry the earnings
  *call*, not the *release*; a company routinely releases at 07:00 and holds the
  call at 10:00. Measured over a large event sample, roughly a third land during
  market hours and would be classified wrongly.

## 3. Predictions can outlive their evidence

A prediction is extrapolated from the cadence of past filings in
`predictionSources`. Nothing in the response tells you how old that evidence is,
and a low `confidence` does not reliably fall to zero when it goes stale.

Sanity checks worth applying before you trust a date, in rough order of value:

1. **Age the evidence.** Parse the accession numbers in `predictionSources` —
   the two digits after the 10-digit prefix are the filing year. If the newest
   source is more than a year old, the cadence behind that date is not current.
2. **Check `confidence`.** Very low values cluster around symbols whose filing
   history is thin or irregular.
3. **Watch for a date that has already passed.** A prediction whose date lapsed
   without a confirming filing means the roll-forward has not caught up yet.

## Symbols

Index membership changes faster than any checked-in list. Spins, renames, and
reconstitutions mean a list can carry symbols that are no longer current, miss
ones that are, or occasionally hold the same company under two tickers where
only one is actively maintained.

Worth knowing when a symbol looks wrong:

- **Unfamiliar is not the same as invalid.** Recent spinoffs legitimately trade
  under tickers you will not recognise. Resolve against SEC's
  `company_tickers.json` before assuming a bug.
- **The current SEC ticker may not be the one people say.** Long-established
  companies sometimes trade under a symbol that differs from the one in common
  use. Ask for both.
- **Two symbols resolving to the same CIK** means one of them is likely the
  stale side of a rename. Compare their newest `earningsDate` to see which is
  being maintained.

Pass `--symbols` to build against a curated list instead of the shipped one.
