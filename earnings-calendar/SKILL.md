---
name: earnings-calendar
description: >
  Builds a single-file HTML earnings calendar from viaNexus CORE/EARNINGS_CALENDAR,
  laid out as a real month grid and colour-coded by market session (pre-market vs
  post-market). Produces either a static snapshot page or a live page that fetches
  with the user's own token. Use whenever someone wants to see upcoming earnings —
  an earnings calendar, reporting schedule, "who reports this week", "when does
  NVDA report", an earnings season view, or a pre/post-market release breakdown.
compatibility:
  tools:
    - viaNexus:fetch
    - viaNexus:search
    - viaNexus:current_date
---

# Earnings Calendar

Generate a **single HTML file** the user opens in any browser. No backend, no
build step at view time, no external requests.

Read [references/dataset.md](references/dataset.md) before writing any code that
touches this dataset. It documents three things that will otherwise produce a
wrong page: every record is `predicted`, roughly half carry no session, and the
serving semantics are not what a normal table lookup would suggest.

## Two shapes, one template

`assets/template.html` renders a build-time snapshot if it has one, and shows a
token bar if it doesn't. Same file either way.

```bash
export VIANEXUS_TOKEN=sk_...
python3 scripts/build.py                    # snapshot -> calendar.html
python3 scripts/build.py --no-data          # live page, nothing embedded
```

| Shape | When to use |
| --- | --- |
| **Snapshot** | Handing a finished page to someone. Renders instantly and offline; no token needed to view it. Contains real data, so treat it as you would any data export. |
| **Live** (`--no-data`) | Publishing anywhere others can reach. Ships no data at all — the viewer pastes their own token and the page fetches for them. |

`assets/example-calendar.html` is a prebuilt live page. Open it, paste a token,
press Load.

The token is used only at build time and never written into either output.
`build.py` refuses to write a file containing anything shaped like a key or a
proxystream ticket.

## How the live page fetches

`api.blueskyapi.com` sends `Access-Control-Allow-Origin: *`, so browser `fetch`
works from anywhere including `file://`. The page runs a pool of 10 concurrent
requests, one per symbol, and reports progress as it goes. About 500 symbols
takes roughly a minute.

No LLM sits in the fetch loop. Every date on screen is API output verbatim.

## Changing what it looks like

Styles live in `assets/_shared.css` and are inlined at build time. The colour
system is deliberate and worth preserving:

- **Chrome stays neutral** so the only colour on the page is the data.
- **Pre-market is teal, post-market is amber** — first light and the close.
  Semantic, not decorative. Don't repurpose these two hues for anything else.
- **No session is grey**, and it is the largest group. Design for that, don't
  treat it as an edge case.

Weekends are omitted from the grid entirely. Earnings are not released on a
Saturday, and rendering two permanently empty columns misstates how dense a
week is. Leading and trailing empty weeks are trimmed for the same reason.

## Adjusting the symbol list

`assets/symbols.txt`, one per line. It ships as an S&P 500 list. There is no API
route that returns universe membership for an unscoped token, so it is a file
rather than a lookup — which also means it needs occasional review. See
[references/dataset.md](references/dataset.md) for the drift currently in it.

To build for a different set, pass `--symbols my-list.txt`, or paste symbols
directly into the live page's textarea.
